#!/usr/bin/env python3
"""Check authored language without audience, filename, or Markdown-quote exemptions.

Read-only. Findings do not authorize changing captured evidence or code syntax.
"""
import argparse
import ast
import csv
import io
import json
import re
from pathlib import Path
import sys
import tokenize
import zipfile
from html.parser import HTMLParser
import xml.etree.ElementTree as ET

from prose_check import check, load_config
from authored_code import javascript_parts


class Block:
    def __init__(self, text, citation=False):
        self.text, self.citation = text, citation


def structured_parts(value, path=()):
    if isinstance(value, str):
        yield Block(value)
    elif isinstance(value, list):
        for item in value:
            yield from structured_parts(item, path)
    elif isinstance(value, dict):
        for key, item in value.items():
            citation = (path[-1:] == ('emotionLabels',) and key == 'source' and value.get('basis') in ('observed', 'reported')) or path[-2:] == ('metadata', 'sourceLabels')
            if citation and isinstance(item, str):
                yield Block(item, citation=True)
            else:
                yield from structured_parts(item, (*path, key))


class AuthoredText(str):
    def __new__(cls, parts):
        blocks, repetition, all_text, body = [], [], [], []
        citations = set()

        def flush():
            if body:
                blocks.append('\n'.join(body))
                body.clear()

        for part in parts:
            items = structured_parts(part) if isinstance(part, (dict, list)) else [part]
            for item in items:
                if isinstance(item, Block):
                    flush()
                    text = item.text
                    blocks.append(text)
                    if not item.citation or text not in citations:
                        repetition.append(text)
                    if item.citation:
                        citations.add(text)
                else:
                    text = item
                    body.append(text)
                    repetition.append(text)
                all_text.append(text)
        flush()
        result = super().__new__(cls, '\n'.join(all_text))
        result.fragment_blocks = blocks
        result.repetition_text = '\n'.join(repetition)
        return result


def css_words(data):
    # CSS comments and string values can contain authored language. Selectors,
    # property names and repeated declarations are executable syntax.
    return '\n'.join(match.group(0)[2:-2] if match.group(0).startswith('/*')
                     else match.group(0)[1:-1]
                     for match in re.finditer(r"/\*.*?\*/|\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", data, re.S))


class HTMLWords(HTMLParser):
    def __init__(self, depth=0):
        if depth > 16:
            raise ValueError('Nested HTML strings exceed extraction limit')
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.in_style = False
        self.script_type = None
        self.depth = depth

    def handle_data(self, data):
        if self.script_type is not None:
            if self.script_type in ('application/json', 'application/ld+json'):
                self.parts.append(json.loads(data))
            elif self.script_type in ('', 'module', 'text/javascript', 'application/javascript'):
                for item in javascript_parts(data):
                    if isinstance(item, str):
                        if re.search(r'</?[A-Za-z][^>]*>', item):
                            nested = HTMLWords(self.depth + 1)
                            nested.feed(item)
                            self.parts.extend(Block(block) for block in AuthoredText(nested.parts).fragment_blocks)
                        else:
                            self.parts.append(Block(item))
                    else:
                        self.parts.append(item)
            else:
                if self.script_type in ('text/template', 'text/html'):
                    nested = HTMLWords(self.depth + 1)
                    nested.feed(data)
                    self.parts.extend(Block(block) for block in AuthoredText(nested.parts).fragment_blocks)
                else:
                    self.parts.append(data)
        else:
            self.parts.append(css_words(data) if self.in_style else data)

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == 'script':
            self.script_type = None

    def handle_comment(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == "style":
            self.in_style = True
        if tag == 'script':
            self.script_type = (dict(attrs).get('type') or '').lower()
        for name, value in attrs:
            if value and name == 'style':
                self.parts.append(css_words(value))
            if value and name in {'alt', 'title', 'aria-label', 'placeholder', 'content', 'value'}:
                self.parts.append(Block(value))
            if value and name.startswith('on'):
                self.parts.extend(Block(item) if isinstance(item, str) else item for item in javascript_parts(value))


def string_values(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from string_values(item)


def authored_text(path):
    suffix = path.suffix.lower()
    if suffix in {'.docx', '.pptx', '.xlsx'}:
        parts = []
        with zipfile.ZipFile(path) as archive:
            for name in sorted(archive.namelist()):
                if name.endswith('.xml'):
                    tree = ET.fromstring(archive.read(name))
                    parts.extend(node.text for node in tree.iter()
                                 if node.tag.rsplit('}', 1)[-1] in {'t', 'v'} and node.text)
        return '\n'.join(parts)
    raw = path.read_text(encoding='utf-8')
    if '\x00' in raw:
        raise ValueError('Binary content is not supported; extract the text and review it explicitly.')
    if suffix == '.css':
        return css_words(raw)
    if suffix in {'.json', '.jsonl', '.ndjson'}:
        values = [json.loads(line) for line in raw.splitlines() if line.strip()] if suffix != '.json' else [json.loads(raw)]
        return AuthoredText(values)
    if suffix in {'.js', '.mjs', '.cjs'}:
        return AuthoredText(Block(item) if isinstance(item, str) else item for item in javascript_parts(raw))
    if suffix in {'.csv', '.tsv'}:
        return '\n'.join(cell for row in csv.reader(io.StringIO(raw), delimiter='\t' if suffix == '.tsv' else ',') for cell in row)
    if suffix == '.py':
        tree = ast.parse(raw)
        parts = [node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)]
        parts.extend(token.string.lstrip('#').strip() for token in tokenize.generate_tokens(io.StringIO(raw).readline)
                     if token.type == tokenize.COMMENT)
        return '\n'.join(parts)
    if suffix in {'.html', '.htm'}:
        parser = HTMLWords()
        parser.feed(raw)
        return AuthoredText(parser.parts)
    # Markdown quoting, fences and audience labels do not exempt authored words.
    # Other UTF-8 source formats remain visible rather than silently disappearing.
    return raw


def strict_config(path):
    baseline_path = Path(__file__).resolve().parent.parent / 'house.json'
    baseline = load_config(baseline_path)
    if path.resolve() == baseline_path.resolve():
        return baseline
    supplied = json.loads(path.read_text())
    if not isinstance(supplied, dict):
        raise ValueError('Writing configuration must be an object')
    # Validate names through the engine before applying additive restrictions.
    load_config(path)
    result = dict(baseline)
    for key, value in supplied.items():
        if key.startswith('_'):
            continue
        if key in {'banned_terms', 'banned_chars', 'hedge_openers'}:
            if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                raise ValueError(key + ' must contain strings')
            result[key] = list(dict.fromkeys([*baseline[key], *value]))
        elif key in {'triad_enabled', 'flag_justification_tails'}:
            if value is not True:
                raise ValueError('Cannot disable writing rule: ' + key)
        elif key == 'allowed_repeated_phrases':
            if value != baseline[key]:
                raise ValueError('Cannot add repetition exemptions through --config')
        elif key in {'em_dash_budget', 'balanced_clause_per_words', 'triad_per_words'}:
            if type(value) is not int or value != baseline[key]:
                raise ValueError('Cannot change writing budgets through --config: ' + key)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    parser.add_argument('--config', type=Path, default=Path(__file__).resolve().parent.parent / 'house.json')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    report = {}
    worst = 0
    try:
        config = strict_config(args.config)
        for path in args.files:
            findings, words = check(authored_text(path), config)
            report[str(path)] = {'wordcount': words, 'findings': [item.as_dict() for item in findings],
                                 'scope': 'authored language; no audience-category exemption'}
            if findings:
                worst = 1
    except (OSError, ValueError, SyntaxError, RecursionError, ET.ParseError, zipfile.BadZipFile, tokenize.TokenError) as exc:
        print('Writing check could not finish: ' + str(exc), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for path, entry in report.items():
            print(f"{path}: {len(entry['findings'])} findings")
            for finding in entry['findings']:
                print(f"  {finding['rule']}: {finding['message']}")
    return worst


if __name__ == '__main__':
    raise SystemExit(main())
