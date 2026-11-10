#!/usr/bin/env python3
"""Extract reader-facing text from rendered or generated files for line-by-line review.

Rendered files are too large to review in raw form. Inline CSS, SVG paths and
base64 images can push a page with 300 lines of text past 38,000 tokens, which
forces partial reads and pushes review toward scanner output. This script writes
only the words a reader sees or a screen reader announces, as numbered Markdown
lines tagged with their source location, in parts small enough for one read.

Commands:

  extract SOURCE... --out DIR [--root DIR] [--generator SOURCE=GENERATOR]
          [--max-chars N] [--max-lines N]
      Write one Markdown file (or numbered parts) per source and DIR/manifest.json.
      Supports .html .htm .svg .js .mjs .xlsx .docx .pptx .md .txt.

  init-log DIR
      Write DIR/review-log.json with one entry per part, ready for the reviewer.

  diff BEFORE_DIR AFTER_DIR
      Compare two extractions by text and print every changed line with its
      locator on both sides. Exit 0 when nothing changed, 1 when lines changed.

  receipt BEFORE_DIR AFTER_DIR [--log FILE] [--out FILE]
      Write a coverage receipt: files, source and extracted line counts, parts
      read, lines read, findings, lines changed and any gaps. Exit 0 only when
      every part has a valid read token, every finding has a disposition, and
      the after-extraction matches the current source files.

Each part ends with a read token. The reviewer copies it into the review log
after reading to the end of that part. The receipt checks the token, which shows
the end of the part was opened; it does not prove attention to every line.
Standard library only.
"""
import argparse
import difflib
import hashlib
import html
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

VERSION = 1
MAX_CHARS = 60000      # characters per part; one Read call holds it comfortably
MAX_LINES = 1500       # lines per part; Read returns 2,000 lines by default
MAX_LINE = 1800        # characters per output line; Read truncates longer lines
LONG_LINE = 400        # source lines longer than this get a column in the locator
TEXT_SUFFIXES = {'.html', '.htm', '.svg', '.js', '.mjs', '.cjs', '.xlsx', '.docx', '.pptx', '.md', '.txt'}
GENERATOR_SUFFIXES = {'.py', '.js', '.mjs', '.cjs', '.ts', '.sh', '.rb', '.jsx', '.tsx'}
SKIP_DIRS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'dist', 'build', '.next', 'archive'}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE64_RUN = re.compile(r'[A-Za-z0-9+/=]{120,}')
WORDY = re.compile(r'[A-Za-z]{2,}')


def clean(text):
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()


def has_words(text, minimum=1):
    return len(WORDY.findall(text)) >= minimum


def looks_like_code(text):
    """True for strings that are identifiers, selectors, paths, URLs or encoded data.

    The filter is deliberately narrow: a stray class name costs the reviewer one
    line, and a dropped sentence costs a missed failure.
    """
    t = text.strip()
    if not t or not re.search(r'[A-Za-z]', t):
        return True
    if BASE64_RUN.search(t) or t.startswith(('data:', 'http://', 'https://', 'mailto:', './', '../')):
        return True
    toks = t.split()
    if len(toks) == 1:
        if re.search(r'[_/#=(){}\[\]<>;$@\\|]', t) or re.search(r'\.\w', t):
            return True                      # paths, calls, selectors, file names
        if re.fullmatch(r'[a-z][a-z0-9]*(?:[-:][a-z0-9]+)*', t):
            return True                      # lowercase keys, class names, event names
        if re.fullmatch(r'[a-z]+[A-Z][A-Za-z0-9]*', t):
            return True                      # camelCase identifiers
        return False
    if re.match(r'[.#\[]', t):
        return True                          # CSS selectors
    if all(re.fullmatch(r'[.#]?[a-z][\w-]*|[>+~*]', x) for x in toks) and any(re.search(r'[-_.#]', x) for x in toks):
        return True                          # class lists such as "btn btn-primary"
    return False


class Line:
    __slots__ = ('loc', 'text', 'section')

    def __init__(self, loc, text, section='Page text'):
        self.loc, self.text, self.section = loc, text, section


# ---------------------------------------------------------------------------
# JavaScript lexer: string and template literals with their source offsets
# ---------------------------------------------------------------------------

REGEX_PREFIX = set('(,=:[!&|?{};+-*%~^<>') | {''}
REGEX_KEYWORDS = {'return', 'typeof', 'case', 'do', 'else', 'in', 'of', 'new', 'delete', 'void', 'throw', 'yield', 'await'}


def js_strings(src):
    """Yield (offset, value) for every string literal and template text run.

    Template literals yield their static text with ${...} replaced by '…'; the
    expressions inside are lexed too, so nested strings are found. Comments and
    regular-expression literals are skipped. Never executes the code.
    """
    out = []
    n = len(src)
    i = 0
    last = ''          # last significant character, for regex detection
    last_word = ''

    def read_quoted(i, q):
        start = i
        i += 1
        buf = []
        while i < n:
            c = src[i]
            if c == '\\' and i + 1 < n:
                nxt = src[i + 1]
                buf.append({'n': ' ', 't': ' ', 'r': ''}.get(nxt, nxt))
                i += 2
                continue
            if c == q:
                return i + 1, ''.join(buf)
            if c == '\n':
                break
            buf.append(c)
            i += 1
        return i, ''.join(buf)

    def read_template(i):
        nonlocal out
        start = i
        i += 1
        buf = []
        while i < n:
            c = src[i]
            if c == '\\' and i + 1 < n:
                buf.append(src[i + 1] if src[i + 1] not in 'nt' else ' ')
                i += 2
                continue
            if c == '`':
                out.append((start, ''.join(buf)))
                return i + 1
            if c == '$' and i + 1 < n and src[i + 1] == '{':
                buf.append('\x00')
                i = lex(i + 2, until_brace=True)
                continue
            buf.append(c)
            i += 1
        out.append((start, ''.join(buf)))
        return i

    def lex(i, until_brace=False):
        nonlocal last, last_word
        depth = 0
        while i < n:
            c = src[i]
            if c.isspace():
                i += 1
                continue
            if src.startswith('//', i):
                j = src.find('\n', i)
                i = n if j < 0 else j
                continue
            if src.startswith('/*', i):
                j = src.find('*/', i + 2)
                i = n if j < 0 else j + 2
                continue
            if c in '"\'':
                start = i
                i, val = read_quoted(i, c)
                out.append((start, val))
                last, last_word = '"', ''
                continue
            if c == '`':
                i = read_template(i)
                last, last_word = '`', ''
                continue
            if c == '/' and (last in REGEX_PREFIX or last_word in REGEX_KEYWORDS):
                # regular-expression literal
                i += 1
                in_class = False
                while i < n and src[i] != '\n':
                    if src[i] == '\\':
                        i += 2
                        continue
                    if src[i] == '[':
                        in_class = True
                    elif src[i] == ']':
                        in_class = False
                    elif src[i] == '/' and not in_class:
                        i += 1
                        break
                    i += 1
                while i < n and src[i].isalpha():
                    i += 1
                last, last_word = 'r', ''
                continue
            if until_brace:
                if c == '{':
                    depth += 1
                elif c == '}':
                    if depth == 0:
                        return i + 1
                    depth -= 1
            m = re.match(r'[A-Za-z_$][\w$]*', src[i:i + 64])
            if m:
                last_word = m.group(0)
                last = 'a'
                i += len(last_word)
                continue
            last, last_word = c, ''
            i += 1
        return i

    lex(0)
    return out


class _FragmentText(HTMLParser):
    """Text and reader-facing attributes from an HTML fragment inside a JS string."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.skip += 1
        for k, v in attrs:
            if k in READER_ATTRS and v and not v.startswith('data:'):
                self.parts.append(f'\n[{k}] {v}\n')
        if re.fullmatch(r'h[1-6]', tag):
            self.parts.append('\n' + '#' * int(tag[1]) + ' ')
        elif tag == 'li':
            self.parts.append('\n- ')
        else:
            self.parts.append('\n' if tag in BLOCK else ' ')

    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.skip = max(0, self.skip - 1)
        self.parts.append('\n' if tag in BLOCK else ' ')

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def js_text_lines(src, base_line=1, section='Script text'):
    """Reader-facing strings from JavaScript source, one Line per text run."""
    lines = []
    line_starts = [0]
    for m in re.finditer('\n', src):
        line_starts.append(m.end())

    def line_of(offset):
        lo, hi = 0, len(line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if line_starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        loc = f'L{base_line + lo}'
        end = line_starts[lo + 1] if lo + 1 < len(line_starts) else len(src)
        if end - line_starts[lo] > LONG_LINE and (lo > 0 or base_line == 1):
            loc += f':c{offset - line_starts[lo] + 1}'   # column, for data packed on one long line
        return loc

    for offset, raw in js_strings(src):
        if '<' in raw and re.search(r'</?[a-zA-Z][^>]*>', raw.replace('\x00', '…')):
            frag = _FragmentText()
            try:
                frag.feed(raw.replace('\x00', '…'))
                frag.close()
                pieces = ''.join(frag.parts).split('\n')
            except Exception:
                pieces = [re.sub(r'<[^>]+>', ' ', raw)]
        else:
            pieces = [raw.replace('\x00', '…')]
        for piece in pieces:
            text = clean(piece)
            text = re.sub(r'(\s*…\s*)+', ' … ', text).strip() if text.replace('…', '').strip() else ''
            body = re.sub(r'^(?:\[[\w-]+\] |#{1,6} |- )', '', text)
            if body in ('use strict', 'use client', 'use server'):
                continue
            if not body or not has_words(body) or looks_like_code(body):
                continue
            lines.append(Line(line_of(offset), text, section))
    return lines


# ---------------------------------------------------------------------------
# HTML and SVG
# ---------------------------------------------------------------------------

BLOCK = {'p', 'div', 'section', 'article', 'header', 'footer', 'main', 'nav', 'aside', 'li', 'tr',
         'dt', 'dd', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'td', 'th', 'caption', 'figcaption',
         'label', 'button', 'option', 'summary', 'details', 'blockquote', 'pre', 'br', 'hr', 'title',
         'legend', 'dialog', 'form', 'table', 'ul', 'ol', 'dl', 'figure', 'text', 'tspan', 'desc',
         'select', 'textarea', 'a'}
READER_ATTRS = ('title', 'alt', 'aria-label', 'aria-description', 'aria-placeholder',
                'aria-roledescription', 'aria-valuetext', 'placeholder', 'label', 'data-tooltip')
SVG_TEXT = {'text', 'tspan', 'title', 'desc', 'textpath'}


class HTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = []
        self.scripts = []         # (start_line, type, text)
        self.styles = []          # (start_line, text)
        self.buf, self.buf_line, self.prefix = [], None, ''
        self.mode = None          # 'script' or 'style'
        self.mode_type, self.mode_line, self.mode_buf = '', 0, []
        self.svg, self.svg_text = 0, 0
        self.section = 'Page text'

    def flush(self):
        text = clean(''.join(self.buf))
        if text and not (' ' not in text and BASE64_RUN.fullmatch(text)):
            self.lines.append(Line(f'L{self.buf_line}', self.prefix + text, self.section))
        self.buf, self.buf_line, self.prefix = [], None, ''

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        a = {k: (v or '') for k, v in attrs}
        if self.mode:
            return
        if tag in ('script', 'style'):
            self.flush()
            self.mode, self.mode_line, self.mode_buf = tag, line, []
            self.mode_type = a.get('type', '').lower()
            return
        if tag == 'svg':
            self.svg += 1
        if self.svg and tag in SVG_TEXT:
            self.svg_text += 1
        if tag in BLOCK or tag in ('img', 'input', 'meta'):
            self.flush()
            if re.fullmatch(r'h[1-6]', tag):
                self.prefix = '#' * int(tag[1]) + ' '
            elif tag == 'li':
                self.prefix = '- '
            elif tag in ('td', 'th'):
                self.prefix = '| '
            elif tag == 'title' and not self.svg:
                self.prefix = '[page title] '
        for k in READER_ATTRS:
            v = a.get(k, '').strip()
            if v and not v.startswith('data:') and has_words(v):
                self.lines.append(Line(f'L{line}', f'[{k}] {clean(v)}', self.section))
        if tag == 'input' and a.get('type', '').lower() in ('button', 'submit', 'reset') and a.get('value'):
            self.lines.append(Line(f'L{line}', f'[button] {clean(a["value"])}', self.section))
        if tag == 'meta':
            key = (a.get('name') or a.get('property') or '').lower()
            if key in ('description', 'og:title', 'og:description', 'twitter:title', 'twitter:description') and a.get('content'):
                self.lines.append(Line(f'L{line}', f'[meta {key}] {clean(a["content"])}', self.section))
        if tag == 'template':
            self.section = 'Template text'

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in ('script', 'style'):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.mode:
            if tag == self.mode:
                body = ''.join(self.mode_buf)
                (self.scripts if tag == 'script' else self.styles).append(
                    (self.mode_line, self.mode_type, body) if tag == 'script' else (self.mode_line, body))
                self.mode = None
            return
        if self.svg and tag in SVG_TEXT:
            self.svg_text = max(0, self.svg_text - 1)
        if tag == 'svg':
            self.svg = max(0, self.svg - 1)
        if tag == 'template':
            self.flush()
            self.section = 'Page text'
        if tag in BLOCK:
            self.flush()

    def handle_data(self, data):
        if self.mode:
            self.mode_buf.append(data)
            return
        if self.svg and not self.svg_text:
            return
        if data.strip():
            if self.buf_line is None:
                lead = len(data) - len(data.lstrip())
                self.buf_line = self.getpos()[0] + data[:lead].count('\n')
            self.buf.append(data)
        elif self.buf:
            self.buf.append(' ')


def json_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from json_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from json_strings(v)


def json_text_lines(body, base_line, section):
    """Strings from a JSON script, tagged with the source line where each appears."""
    lines = []
    try:
        data = json.loads(body)
    except ValueError:
        return js_text_lines(body, base_line, section)
    seen = {}
    for s in json_strings(data):
        text = clean(re.sub(r'<[^>]+>', ' ', s))
        if not text or not has_words(text) or looks_like_code(text):
            continue
        needle = json.dumps(s)[1:-1][:60]
        pos = body.find(needle, seen.get(needle, 0))
        if pos >= 0:
            seen[needle] = pos + 1
        line = base_line + (body.count('\n', 0, pos) if pos >= 0 else 0)
        lines.append(Line(f'L{line}', text, section))
    return lines


CSS_CONTENT = re.compile(r'content\s*:\s*(["\'])((?:\\.|(?!\1).)*)\1')


def html_lines(raw):
    p = HTMLText()
    p.feed(raw)
    p.close()
    p.flush()
    lines = list(p.lines)
    for start, kind, body in p.scripts:
        if kind in ('application/json', 'application/ld+json', 'importmap'):
            if kind != 'importmap':
                lines += json_text_lines(body, start, 'Script text (JSON data)')
        elif 'template' in kind or kind == 'text/html':
            sub = html_lines(body)
            for ln in sub:
                ln.loc = f'L{start + int(ln.loc[1:]) - 1}'
                ln.section = 'Template text'
            lines += sub
        else:
            lines += js_text_lines(body, start, 'Script text')
    for start, body in p.styles:
        for m in CSS_CONTENT.finditer(body):
            text = clean(m.group(2))
            if has_words(text) and not looks_like_code(text):
                lines.append(Line(f'L{start + body.count(chr(10), 0, m.start())}', f'[css content] {text}', 'Style text'))
    return lines


# ---------------------------------------------------------------------------
# Office Open XML
# ---------------------------------------------------------------------------

NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    's': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
}


def _q(prefix, tag):
    return f'{{{NS[prefix]}}}{tag}'


def _natural(name):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', name)]


def docx_lines(z):
    lines = []
    parts = ['word/document.xml'] + sorted(
        (n for n in z.namelist() if re.fullmatch(r'word/(header|footer)\d*\.xml', n)), key=_natural) + [
        n for n in ('word/footnotes.xml', 'word/endnotes.xml', 'word/comments.xml') if n in z.namelist()]
    for part in parts:
        if part not in z.namelist():
            continue
        root = ET.fromstring(z.read(part))
        label = Path(part).stem
        section = 'Document text' if label == 'document' else f'{label.capitalize()} text'
        for i, para in enumerate(root.iter(_q('w', 'p')), 1):
            text = clean(''.join(
                (t.text or '') if t.tag == _q('w', 't') else ' ' for t in para.iter()
                if t.tag in (_q('w', 't'), _q('w', 'tab'), _q('w', 'br'))))
            if not text:
                continue
            style = para.find(f'{_q("w", "pPr")}/{_q("w", "pStyle")}')
            sv = style.get(_q('w', 'val'), '') if style is not None else ''
            m = re.match(r'(?i)heading\s*(\d)', sv) or re.match(r'(?i)title$', sv)
            prefix = ''
            if m:
                prefix = '#' * (int(m.group(1)) if m.groups() else 1) + ' '
            elif para.find(f'{_q("w", "pPr")}/{_q("w", "numPr")}') is not None:
                prefix = '- '
            lines.append(Line(f'{label}:p{i}', prefix + text, section))
    return lines


def pptx_lines(z):
    lines = []
    slides = sorted((n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)), key=_natural)
    for path in slides:
        num = re.search(r'(\d+)', Path(path).name).group(1)
        root = ET.fromstring(z.read(path))
        for i, para in enumerate(root.iter(_q('a', 'p')), 1):
            text = clean(''.join(t.text or '' for t in para.iter(_q('a', 't'))))
            if text:
                lines.append(Line(f'slide{num}:p{i}', text, 'Slide text'))
        for el in root.iter():
            if el.tag == _q('p', 'cNvPr') and el.get('descr'):
                lines.append(Line(f'slide{num}', f'[alt] {clean(el.get("descr"))}', 'Slide text'))
        notes = f'ppt/notesSlides/notesSlide{num}.xml'
        if notes in z.namelist():
            nroot = ET.fromstring(z.read(notes))
            for i, para in enumerate(nroot.iter(_q('a', 'p')), 1):
                text = clean(''.join(t.text or '' for t in para.iter(_q('a', 't'))))
                if text and not re.fullmatch(r'\d+', text):
                    lines.append(Line(f'notes{num}:p{i}', text, 'Speaker notes'))
    return lines


def _col(ref):
    return re.match(r'[A-Z]+', ref).group(0) if ref else ''


def xlsx_lines(z):
    names = z.namelist()
    shared = []
    if 'xl/sharedStrings.xml' in names:
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall(_q('s', 'si')):
            shared.append(''.join(t.text or '' for t in si.iter(_q('s', 't'))))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {}
    if 'xl/_rels/workbook.xml.rels' in names:
        for rel in ET.fromstring(z.read('xl/_rels/workbook.xml.rels')):
            rels[rel.get('Id')] = rel.get('Target')
    sheets = []
    for sh in wb.iter(_q('s', 'sheet')):
        target = rels.get(sh.get(_q('r', 'id')), '')
        target = target.lstrip('/')
        path = target if target.startswith('xl/') else 'xl/' + target
        sheets.append((sh.get('name'), path))
    uses = {}          # shared index -> [cell refs]
    inline = []        # (ref, text)
    for name, path in sheets:
        if path not in names:
            continue
        root = ET.fromstring(z.read(path))
        for c in root.iter(_q('s', 'c')):
            ref = f"{name}!{c.get('r')}"
            t = c.get('t')
            if t == 's':
                v = c.find(_q('s', 'v'))
                if v is not None and v.text and v.text.isdigit():
                    uses.setdefault(int(v.text), []).append(ref)
            elif t == 'inlineStr':
                inline.append((ref, ''.join(x.text or '' for x in c.iter(_q('s', 't')))))
            elif t == 'str':
                v = c.find(_q('s', 'v'))
                if v is not None and v.text and has_words(v.text, 2):
                    inline.append((ref, v.text))
    lines = [Line('workbook', f'[sheet] {name}', 'Sheet names') for name, _ in sheets]
    for idx, text in enumerate(shared):
        text = clean(text)
        if not text or not has_words(text):
            continue
        cells = uses.get(idx, [])
        where = cells[0] + (f' +{len(cells) - 1}' if len(cells) > 1 else '') if cells else 'unused'
        lines.append(Line(f's{idx} {where}', text, 'Cell text (shared strings)'))
    for ref, text in inline:
        text = clean(text)
        if text and has_words(text):
            lines.append(Line(ref, text, 'Cell text (inline and formula results)'))
    for n in sorted((n for n in names if re.fullmatch(r'xl/comments\d*\.xml', n)), key=_natural):
        root = ET.fromstring(z.read(n))
        for cm in root.iter(_q('s', 'comment')):
            text = clean(''.join(t.text or '' for t in cm.iter(_q('s', 't'))))
            if text:
                lines.append(Line(f'comment {cm.get("ref")}', text, 'Cell comments'))
    return lines


# ---------------------------------------------------------------------------
# Dispatch, generators and output
# ---------------------------------------------------------------------------

def extract_lines(path):
    suffix = path.suffix.lower()
    if suffix in ('.docx', '.pptx', '.xlsx'):
        with zipfile.ZipFile(path) as z:
            return {'.docx': docx_lines, '.pptx': pptx_lines, '.xlsx': xlsx_lines}[suffix](z), None
    raw = path.read_text(encoding='utf-8', errors='replace')
    count = raw.count('\n') + (0 if raw.endswith('\n') else 1)
    if suffix in ('.html', '.htm', '.svg'):
        return html_lines(raw), count
    if suffix in ('.js', '.mjs', '.cjs'):
        return js_text_lines(raw, 1, 'Script text'), count
    return [Line(f'L{i}', t, 'Text') for i, t in enumerate(raw.splitlines(), 1) if t.strip()], count


def find_generators(path, root):
    """Files under root that name this output file: likely generators or copy steps."""
    if root is None:
        return []
    name = path.name
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for f in filenames:
            p = Path(dirpath, f)
            if p.suffix.lower() not in GENERATOR_SUFFIXES or p.resolve() == path.resolve():
                continue
            try:
                if p.stat().st_size > 2_000_000:
                    continue
                text = p.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue
            if name in text:
                hits.append(str(p.relative_to(root)))
        if len(hits) >= 20:
            break
    return sorted(hits)


def slug(rel):
    s = re.sub(r'[^a-z0-9]+', '-', rel.lower()).strip('-')
    return s or 'source'


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def wrap(text, width=MAX_LINE):
    if len(text) <= width:
        return [text]
    out, rest = [], text
    while len(rest) > width:
        cut = rest.rfind(' ', 0, width)
        cut = width if cut < width // 2 else cut
        out.append(rest[:cut])
        rest = rest[cut:].lstrip()
    out.append(rest)
    return out


def render(lines):
    """Numbered output lines grouped by section, each carrying its locator."""
    body, records = [], []
    current = None
    for i, ln in enumerate(lines, 1):
        if ln.section != current:
            current = ln.section
            if body:
                body.append('')
            body.append(f'## {current}')
            body.append('')
        rid = f'{i:04d}'
        records.append({'id': rid, 'loc': ln.loc, 'section': ln.section, 'text': ln.text})
        for k, chunk in enumerate(wrap(ln.text)):
            tag = f'[{rid}] {ln.loc}' + (f' (cont. {k + 1})' if k else '')
            body.append(f'{tag}: {chunk}')
    return body, records


def split(body, max_chars, max_lines):
    parts, cur, size = [], [], 0
    for line in body:
        if cur and (size + len(line) + 1 > max_chars or len(cur) >= max_lines):
            parts.append(cur)
            cur, size = [], 0
        cur.append(line)
        size += len(line) + 1
    parts.append(cur)
    return parts


def cmd_extract(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    root = Path(args.root).resolve() if args.root else Path.cwd().resolve()
    gen_map = {}
    for item in args.generator or []:
        if '=' not in item:
            sys.exit(f'--generator needs SOURCE=GENERATOR, got {item!r}')
        s, g = item.split('=', 1)
        gen_map[str(Path(s).resolve())] = g
    manifest_path = out / 'manifest.json'
    manifest = {'version': VERSION, 'tool': 'extract_review_text.py', 'root': str(root),
                'created': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'files': []}
    sources = []
    for s in args.sources:
        p = Path(s)
        if p.is_dir():
            sources += sorted(q for q in p.rglob('*') if q.suffix.lower() in TEXT_SUFFIXES and q.is_file()
                              and not any(part in SKIP_DIRS for part in q.parts))
        elif p.is_file():
            sources.append(p)
        else:
            sys.exit(f'No such file: {s}')
    status = 0
    for p in sources:
        absp = p.resolve()
        try:
            rel = str(absp.relative_to(root))
        except ValueError:
            rel = str(absp)
        try:
            lines, src_lines = extract_lines(absp)
        except (zipfile.BadZipFile, ET.ParseError, KeyError, UnicodeDecodeError) as exc:
            print(f'{rel}: cannot extract ({exc})', file=sys.stderr)
            status = 2
            continue
        stem = slug(rel)
        body, records = render(lines)
        explicit = gen_map.get(str(absp))
        candidates = [] if explicit else find_generators(absp, root if args.find_generators else None)
        head = [f'# Text of {rel}', '',
                f'Source: `{rel}`. Each line is `[ID] LOCATOR: text`. LOCATOR is the source line (`L87`), '
                'workbook cell, document paragraph or slide where the text lives.']
        if explicit:
            head.append(f'Generated by `{explicit}`. Edit the generator or its data, then rebuild and re-extract; '
                        'an edit to the output alone is overwritten on the next build.')
        elif candidates:
            head.append('Files that name this output (possible generators or copy steps): '
                        + ', '.join(f'`{c}`' for c in candidates)
                        + '. If one builds it, fix the text there, not in this output.')
        head.append('')
        for old in out.glob(f'{stem}*.md'):
            if re.fullmatch(re.escape(stem) + r'(-part-\d{2})?\.md', old.name):
                old.unlink()
        chunks = split(body, args.max_chars - 2000, args.max_lines - 20)
        parts = []
        for i, chunk in enumerate(chunks, 1):
            name = f'{stem}.md' if len(chunks) == 1 else f'{stem}-part-{i:02d}.md'
            ids = [l.split(']', 1)[0][1:] for l in chunk if l.startswith('[')]
            text = '\n'.join(head + ([f'Part {i} of {len(chunks)}.', ''] if len(chunks) > 1 else []) + chunk)
            token = hashlib.sha256((rel + name + text).encode()).hexdigest()[:12]
            text += f'\n\nEnd of {name}. Read token: {token}\n'
            (out / name).write_text(text, encoding='utf-8')
            parts.append({'file': name, 'first': ids[0] if ids else None, 'last': ids[-1] if ids else None,
                          'lines': len({x for x in ids}), 'chars': len(text),
                          'token_sha256': hashlib.sha256(token.encode()).hexdigest()})
        manifest['files'].append({
            'source': rel, 'path': str(absp), 'sha256': sha256_file(absp), 'bytes': absp.stat().st_size,
            'source_lines': src_lines, 'extracted_lines': len(records), 'generator': explicit,
            'generator_candidates': candidates, 'parts': parts, 'records': records})
        print(f'{rel}: {src_lines if src_lines is not None else "-"} source lines, {len(records)} text lines '
              f'-> {", ".join(x["file"] for x in parts)}')
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'manifest: {manifest_path}')
    return status


def load_manifest(d):
    p = Path(d) / 'manifest.json'
    if not p.is_file():
        sys.exit(f'No manifest.json in {d}; run extract first.')
    return json.loads(p.read_text(encoding='utf-8'))


def cmd_init_log(args):
    m = load_manifest(args.dir)
    path = Path(args.dir) / 'review-log.json'
    if path.exists() and not args.force:
        sys.exit(f'{path} exists; pass --force to replace it.')
    log = {'reviewer': '', 'rules': 'writing-integrity (review-writing)',
           'parts': {p['file']: '' for f in m['files'] for p in f['parts']},
           'findings': [],
           'example_finding': {'file': 'outputs-page.md', 'id': '0042', 'loc': 'L87',
                               'issue': 'Heading promises a plural; the page has one job.',
                               'action': 'fixed | kept | deferred', 'fix_at': 'src/build_page.py:120',
                               'note': 'Why it was kept or deferred, when it was not fixed.'}}
    path.write_text(json.dumps(log, indent=1) + '\n', encoding='utf-8')
    print(path)
    return 0


def diff_files(before, after):
    """Per source: list of (tag, before_record, after_record) for changed lines."""
    bf = {f['source']: f for f in before['files']}
    af = {f['source']: f for f in after['files']}
    result = {}
    for src in sorted(set(bf) | set(af)):
        b = bf.get(src, {}).get('records', [])
        a = af.get(src, {}).get('records', [])
        sm = difflib.SequenceMatcher(a=[r['text'] for r in b], b=[r['text'] for r in a], autojunk=False)
        changes = []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == 'equal':
                continue
            changes.append({'op': op, 'before': b[i1:i2], 'after': a[j1:j2]})
        result[src] = {'changes': changes, 'missing_before': src not in bf, 'missing_after': src not in af}
    return result


def cmd_diff(args):
    d = diff_files(load_manifest(args.before), load_manifest(args.after))
    changed = 0
    for src, info in d.items():
        if not info['changes']:
            continue
        print(f'## {src}')
        for ch in info['changes']:
            for r in ch['before']:
                print(f"- [{r['id']}] {r['loc']}: {r['text']}")
                changed += 1
            for r in ch['after']:
                print(f"+ [{r['id']}] {r['loc']}: {r['text']}")
            if not ch['before']:
                changed += len(ch['after'])
            print()
    total = sum(1 for i in d.values() if i['changes'])
    print(f'{changed} lines changed in {total} of {len(d)} files.')
    return 1 if changed else 0


def cmd_receipt(args):
    before = load_manifest(args.before)
    after = load_manifest(args.after)
    log_path = Path(args.log) if args.log else Path(args.before) / 'review-log.json'
    log = json.loads(log_path.read_text(encoding='utf-8')) if log_path.is_file() else {'parts': {}, 'findings': []}
    gaps = []
    files = []
    read_tokens = log.get('parts', {})
    d = diff_files(before, after)
    findings = log.get('findings', [])
    for f in before['files']:
        read_parts, lines_read = 0, 0
        for p in f['parts']:
            tok = (read_tokens.get(p['file']) or '').strip()
            if tok and hashlib.sha256(tok.encode()).hexdigest() == p['token_sha256']:
                read_parts += 1
                lines_read += p['lines']
            else:
                gaps.append(f"{p['file']}: no valid read token" + (' (wrong token)' if tok else ''))
        info = d.get(f['source'], {'changes': []})
        removed = sum(len(c['before']) for c in info['changes'])
        added = sum(len(c['after']) for c in info['changes'])
        changed_ids = {r['id'] for c in info['changes'] for r in c['before']}
        part_names = {p['file'] for p in f['parts']}
        fixed_ids = set()
        for x in findings:
            if x.get('file') not in part_names or x.get('action') != 'fixed':
                continue
            ids = x.get('id')
            ids = [str(i) for i in ids] if isinstance(ids, list) else [str(ids)]
            fixed_ids.update(ids)
            for i in ids:
                if i not in changed_ids:
                    gaps.append(f"{x.get('file')} [{i}]: finding marked fixed but the line is unchanged")
        unlogged = sorted(changed_ids - fixed_ids)
        for i in unlogged:
            rec = next((r for c in info['changes'] for r in c['before'] if r['id'] == i), {})
            gaps.append(f"{f['source']} [{i}] {rec.get('loc', '')}: line changed without a finding")
        files.append({'source': f['source'], 'sha256_reviewed': f['sha256'], 'source_lines': f['source_lines'],
                      'extracted_lines': f['extracted_lines'], 'parts': len(f['parts']), 'parts_read': read_parts,
                      'lines_read': lines_read, 'lines_changed': max(removed, added), 'lines_removed': removed,
                      'lines_added': added, 'changed_without_finding': unlogged,
                      'generator': f.get('generator') or None})
    for f in after['files']:
        p = Path(f['path'])
        if not p.is_file():
            gaps.append(f"{f['source']}: source missing")
        elif sha256_file(p) != f['sha256']:
            gaps.append(f"{f['source']}: source changed after the after-extraction; re-extract")
    for i, x in enumerate(findings):
        if x.get('action') not in ('fixed', 'kept', 'deferred'):
            gaps.append(f'finding {i + 1}: action must be fixed, kept or deferred')
        if x.get('action') in ('kept', 'deferred') and not (x.get('note') or '').strip():
            gaps.append(f'finding {i + 1}: a kept or deferred finding needs a note')
    counts = {a: sum(1 for x in findings if x.get('action') == a) for a in ('fixed', 'kept', 'deferred')}
    total_lines = sum(f['extracted_lines'] for f in files)
    read = sum(f['lines_read'] for f in files)
    receipt = {
        'tool': 'extract_review_text.py receipt', 'version': VERSION,
        'created': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'before': str(Path(args.before).resolve()), 'after': str(Path(args.after).resolve()),
        'log': str(log_path.resolve()) if log_path.is_file() else None,
        'reviewer': log.get('reviewer') or None,
        'totals': {'files': len(files), 'extracted_lines': total_lines, 'lines_read': read,
                   'parts': sum(f['parts'] for f in files), 'parts_read': sum(f['parts_read'] for f in files),
                   'lines_changed': sum(f['lines_changed'] for f in files), 'findings': counts},
        'files': files, 'gaps': gaps,
        'complete': not gaps and read == total_lines,
        'limits': 'A read token shows the end of each part was opened. It does not prove attention to every '
                  'line, factual accuracy or editorial quality.'}
    text = json.dumps(receipt, indent=1, ensure_ascii=False) + '\n'
    if args.out:
        Path(args.out).write_text(text, encoding='utf-8')
        print(args.out)
    t = receipt['totals']
    print(f"{t['files']} files, {t['extracted_lines']} text lines, {t['lines_read']} read "
          f"({t['parts_read']}/{t['parts']} parts), {t['lines_changed']} changed; "
          f"findings fixed {counts['fixed']}, kept {counts['kept']}, deferred {counts['deferred']}.")
    for g in gaps:
        print(f'GAP: {g}')
    print('COMPLETE' if receipt['complete'] else 'INCOMPLETE')
    return 0 if receipt['complete'] else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('extract', help='write reviewable text and a manifest')
    e.add_argument('sources', nargs='+')
    e.add_argument('--out', required=True)
    e.add_argument('--root', help='project root for relative names and generator search (default: cwd)')
    e.add_argument('--generator', action='append', metavar='SOURCE=GENERATOR')
    e.add_argument('--no-find-generators', dest='find_generators', action='store_false')
    e.add_argument('--max-chars', type=int, default=MAX_CHARS)
    e.add_argument('--max-lines', type=int, default=MAX_LINES)
    i = sub.add_parser('init-log', help='write a review log template')
    i.add_argument('dir')
    i.add_argument('--force', action='store_true')
    df = sub.add_parser('diff', help='show changed text lines between two extractions')
    df.add_argument('before')
    df.add_argument('after')
    r = sub.add_parser('receipt', help='write a coverage receipt')
    r.add_argument('before')
    r.add_argument('after')
    r.add_argument('--log')
    r.add_argument('--out')
    args = ap.parse_args(argv)
    return {'extract': cmd_extract, 'init-log': cmd_init_log, 'diff': cmd_diff, 'receipt': cmd_receipt}[args.cmd](args)


if __name__ == '__main__':
    sys.exit(main())
