#!/usr/bin/env python3
"""A small HTML tree and CSS-selector engine on the Python standard library.

`parity_audit.py` used BeautifulSoup for four things: build a tree, walk it,
read text with hidden subtrees excluded, and resolve a selector. Only a narrow
slice of each was ever exercised, and the dependency made the parity gate the
one release control that could not run on a bare interpreter. A cloud mount with
no `pip install` reached `beautifulsoup4 is required` and the gate was skipped,
which is the failure mode a release control exists to prevent.

Scope is deliberate. The selector grammar is tag, `#id`, `.class`, a compound of
those, and a comma-separated list of compounds. Descendant and child combinators,
attribute selectors, and pseudo-classes raise `SelectorError` rather than
returning no match, because a silent miss reads downstream as a missing element
in the artifact rather than as an unsupported query.

Known limit: optional end tags are not inferred. `<p>a<p>b` nests where a browser
would not. Every artifact this gate reads is machine-rendered with explicit end
tags, so inference would add a guessing layer with no caller.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, Dict, Iterator, List, Optional

# Elements that never take an end tag, per the HTML spec's void-element list.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}

# Attributes HTML defines as a space-separated token list. Callers read these as
# lists, so a caller asking for `rel` never receives a bare string it would then
# iterate one character at a time.
MULTI_VALUED = {"rel", "class", "rev", "accesskey", "headers", "sandbox"}

TEXT = "#text"

_COMPOUND = re.compile(r"^(?:([A-Za-z][\w-]*)|\*)?((?:[#.][\w-]+)*)$")
_SIMPLE = re.compile(r"([#.])([\w-]+)")


class SelectorError(ValueError):
    """A selector outside the supported grammar."""


class Node:
    """One element or text node. The document root is a Node with tag ''."""

    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag: str, attrs: Optional[Dict[str, Any]] = None,
                 text: str = "") -> None:
        self.tag = tag
        self.attrs: Dict[str, Any] = attrs or {}
        self.children: List["Node"] = []
        self.parent: Optional["Node"] = None
        self.text = text

    # -- shape ---------------------------------------------------------------
    @property
    def name(self) -> str:
        """The tag name. Callers that format `<{name}>` into a finding read this."""
        return self.tag

    @property
    def is_element(self) -> bool:
        return self.tag not in ("", TEXT)

    def get(self, name: str, default: Any = None) -> Any:
        return self.attrs.get(name, default)

    def has_attr(self, name: str) -> bool:
        return name in self.attrs

    def attr_list(self, name: str) -> List[str]:
        """A space-separated attribute as its tokens. Empty when absent."""
        value = self.attrs.get(name)
        if value is None:
            return []
        if isinstance(value, list):
            return list(value)
        return str(value).split()

    # -- traversal -----------------------------------------------------------
    def ancestors(self) -> Iterator["Node"]:
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def descendants(self) -> Iterator["Node"]:
        for child in list(self.children):
            yield child
            for deeper in child.descendants():
                yield deeper

    def elements(self) -> Iterator["Node"]:
        """Every descendant element, in document order."""
        for node in self.descendants():
            if node.is_element:
                yield node

    def find_all(self, tag: Optional[str] = None) -> List["Node"]:
        return [n for n in self.elements() if tag is None or n.tag == tag]

    def find_tag(self, tag: str) -> Optional["Node"]:
        for node in self.elements():
            if node.tag == tag:
                return node
        return None

    def find_by_id(self, value: str) -> Optional["Node"]:
        for node in self.elements():
            if node.get("id") == value:
                return node
        return None

    def remove(self) -> None:
        if self.parent is not None:
            self.parent.children.remove(self)
            self.parent = None

    # -- text ----------------------------------------------------------------
    def get_text(self, separator: str = " ", strip: bool = True) -> str:
        parts = [n.text for n in self.descendants() if n.tag == TEXT]
        if strip:
            parts = [p.strip() for p in parts]
            parts = [p for p in parts if p]
        return separator.join(parts)

    # -- selectors -----------------------------------------------------------
    def select(self, selector: str) -> List["Node"]:
        compounds = _parse_selector(selector)
        return [n for n in self.elements()
                if any(_matches(n, c) for c in compounds)]

    def select_one(self, selector: str) -> Optional["Node"]:
        compounds = _parse_selector(selector)
        # Document order across the whole selector list, which is what a browser
        # returns. Matching each compound to exhaustion in turn would return the
        # first match of the first compound instead.
        for node in self.elements():
            if any(_matches(node, c) for c in compounds):
                return node
        return None

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "<Node {}>".format(self.tag or "document")


def _parse_selector(selector: str) -> List[tuple]:
    if not isinstance(selector, str) or not selector.strip():
        raise SelectorError("selector must be a nonempty string")
    compounds = []
    for part in selector.split(","):
        piece = part.strip()
        if not piece:
            raise SelectorError("empty compound in selector {!r}".format(selector))
        match = _COMPOUND.match(piece)
        if not match:
            raise SelectorError(
                "unsupported selector {!r}; this gate reads tag, #id, .class, "
                "a compound of those, and a comma-separated list".format(piece))
        tag = match.group(1)
        ids, classes = [], []
        for kind, name in _SIMPLE.findall(match.group(2) or ""):
            (ids if kind == "#" else classes).append(name)
        compounds.append((tag.lower() if tag else None, tuple(ids), tuple(classes)))
    return compounds


def _matches(node: "Node", compound: tuple) -> bool:
    tag, ids, classes = compound
    if tag is not None and node.tag != tag:
        return False
    node_id = node.get("id")
    if any(node_id != want for want in ids):
        return False
    if classes:
        have = set(node.attr_list("class"))
        if not set(classes).issubset(have):
            return False
    return True


class _Builder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("")
        self._stack = [self.root]

    def _append(self, node: Node) -> None:
        parent = self._stack[-1]
        node.parent = parent
        parent.children.append(node)

    def _attrs(self, attrs) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key, value in attrs:
            key = key.lower()
            if value is None:
                value = ""
            out[key] = value.split() if key in MULTI_VALUED else value
        return out

    def handle_starttag(self, tag, attrs):
        node = Node(tag.lower(), self._attrs(attrs))
        self._append(node)
        if tag.lower() not in VOID:
            self._stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self._append(Node(tag.lower(), self._attrs(attrs)))

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        # Pop to the nearest open element of this name. A stray end tag with no
        # open counterpart is discarded rather than unwinding the document.
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].tag == tag:
                del self._stack[index:]
                return

    def handle_data(self, data):
        if data:
            self._append(Node(TEXT, text=data))


def parse_html(html: str) -> Node:
    """Parse a document and return its root Node."""
    builder = _Builder()
    builder.feed(html)
    builder.close()
    return builder.root
