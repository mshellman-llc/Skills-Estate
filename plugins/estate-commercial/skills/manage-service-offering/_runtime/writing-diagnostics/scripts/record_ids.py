"""Record IDs in reader prose (C28).

A person reading a page, brief, report or reply should meet plain names, not
system keys such as PER-01, DEC-02 or I1.s24. Data files, ledgers, code and a
source index keep their IDs. This module extracts the reader prose of a
document, leaves those system-facing parts out, and counts the ID mentions a
reader has to decode.

A mention is free when it is the first mention of that ID and sits beside a
name: it does not open a sentence, a heading or a table row, and its sentence
or row carries fewer than three distinct IDs. Every other mention counts
against the budget.
"""
from html.parser import HTMLParser
import re

RULE = 'C28-record-id-density'
DEFAULT_PER_WORDS = 200
MINIMUM_BUDGET = 2
CLUSTER = 3

# PER-01, DEC-002, RI-09; S1, H3; I1.s24 and other sentence locators.
ID_TOKEN = re.compile(
    r'(?<![\w./#@$:-])'
    r'(?:[A-Z]{1,4}-\d{2,3}|[A-Z]{1,3}\d{1,2}\.s\d{1,3}|[A-Z]\d{1,2})'
    r'(?![\w-]|\.\d)')
# Standards, encodings and calendar quarters share the shape but name no record.
NOT_RECORDS = re.compile(r'^(?:(?:AES|EN|ES|IEC|ISO|K|RFC|RSA|SHA|UTF)-\d+|Q[1-4])$')

# A heading that opens a system-facing section: everything under it, down to
# the next heading of the same or a higher level, is left out.
SOURCE_HEADING = re.compile(
    r'\b(?:source index|sources|record of sources|references|appendix|traceability|'
    r'crosswalk|evidence (?:index|ledger|list)|ledger|record ids?|id index)\b', re.I)
SOURCE_MARK = re.compile(r'source-index')

FENCE = re.compile(r'^\s*(```|~~~)')
CODE_SPAN = re.compile(r'`[^`\n]*`')
LINK_TARGET = re.compile(r'\]\([^)]*\)')
URL = re.compile(r'https?://\S+')
COMMENT = re.compile(r'<!--.*?-->', re.S)
TAG = re.compile(r'</?[A-Za-z][^>\n]*>')
SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')
LEADING_MARKUP = re.compile(r'^(?:\s*(?:#{1,6}|[-*+]|\d+[.)]|>|\*\*|__|\*|_|\(|\[)\s*)+')
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")


def record_ids(text):
    return [match for match in ID_TOKEN.finditer(text) if not NOT_RECORDS.match(match.group())]


def markdown_reader_prose(text):
    """Reader lines of Markdown or plain text, without code, link targets or source sections."""
    lines = str(text).splitlines()
    if lines and lines[0].strip() == '---':
        end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == '---'), None)
        if end is not None:
            lines = lines[end + 1:]
    kept, in_fence, skip_level = [], False, None
    for line in COMMENT.sub(' ', '\n'.join(lines)).splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = re.match(r'^\s*(#{1,6})\s+(.*)$', line)
        if heading:
            level = len(heading.group(1))
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and SOURCE_HEADING.search(heading.group(2)):
                skip_level = level
        if skip_level is not None:
            continue
        for pattern in (CODE_SPAN, LINK_TARGET, URL, TAG):
            line = pattern.sub(' ', line)
        kept.append(line)
    return '\n'.join(kept)


class HTMLReaderProse(HTMLParser):
    """Visible text a reader meets; tooltips, link targets and source indexes stay out."""
    HIDDEN = {'script', 'style', 'code', 'pre', 'template', 'noscript'}
    BLOCKS = {'p', 'div', 'li', 'br', 'dt', 'dd', 'blockquote', 'section', 'article',
              'header', 'footer', 'figcaption', 'caption', 'summary', 'details', 'nav'}
    VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
            'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.parts, self.stack = [], [], []
        self.row, self.cell = None, None
        self.heading, self.skip_level = None, None

    def hidden(self):
        return any(hide for _, hide in self.stack) or self.skip_level is not None

    def flush(self):
        text = ' '.join(''.join(self.parts).split())
        if text:
            self.lines.append(text)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        marked = 'data-source-index' in values or SOURCE_MARK.search(
            (values.get('class') or '') + ' ' + (values.get('id') or ''))
        level = int(tag[1]) if re.fullmatch(r'h[1-6]', tag) else None
        if level and self.skip_level is not None and level <= self.skip_level:
            self.skip_level = None
        if tag not in self.VOID:
            self.stack.append((tag, bool(marked) or tag in self.HIDDEN))
        if level:
            self.flush()
            self.heading = (level, [])
        elif tag == 'tr':
            self.flush()
            self.row = []
        elif tag in {'td', 'th'} and self.row is not None:
            self.cell = []
        elif tag in self.BLOCKS:
            self.flush()

    def handle_endtag(self, tag):
        if self.heading and re.fullmatch(r'h[1-6]', tag):
            level, parts = self.heading
            self.heading = None
            text = ' '.join(''.join(parts).split())
            if self.skip_level is None and SOURCE_HEADING.search(text):
                self.skip_level = level
            elif not self.hidden() and text:
                self.lines.append('#' * level + ' ' + text)
        elif tag in {'td', 'th'} and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            if any(self.row):
                self.lines.append('| ' + ' | '.join(self.row) + ' |')
            self.row = None
        elif tag in self.BLOCKS:
            self.flush()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.heading:
            self.heading[1].append(data)
        elif self.hidden():
            return
        elif self.cell is not None:
            self.cell.append(data)
        elif self.row is None:
            self.parts.append(data)


def html_reader_prose(raw):
    parser = HTMLReaderProse()
    parser.feed(raw)
    parser.close()
    parser.flush()
    return '\n'.join(parser.lines)


def units(prose):
    """Sentences, headings and table rows, each with whether it is a table row."""
    paragraph = []

    def sentences():
        for sentence in SENTENCE_SPLIT.split(' '.join(paragraph)):
            if sentence.strip():
                yield sentence.strip(), False

    for line in prose.splitlines():
        stripped = line.strip()
        if stripped.startswith('|'):
            yield from sentences(); paragraph = []
            cells = [cell.strip() for cell in stripped.strip('|').split('|')]
            if not all(re.fullmatch(r':?-{3,}:?', cell.replace(' ', '')) for cell in cells if cell):
                yield cells, True
        elif not stripped or re.match(r'^(?:#{1,6}\s|[-*+]\s|\d+[.)]\s)', stripped):
            yield from sentences(); paragraph = []
            if stripped:
                paragraph.append(stripped)
        else:
            paragraph.append(stripped)
    yield from sentences()


def opens_with_id(text):
    rest = LEADING_MARKUP.sub('', text)
    first = ID_TOKEN.match(rest)
    return bool(first) and not NOT_RECORDS.match(first.group())


def record_id_finding(text, per_words=DEFAULT_PER_WORDS):
    """Return (count, budget, wordcount, samples) when reader prose overuses record IDs, else None."""
    prose = getattr(text, 'reader_prose', None)
    if prose is None:
        prose = markdown_reader_prose(text)
    if not prose.strip():
        return None
    wordcount = len(WORD.findall(prose))
    seen, count, samples = set(), 0, []
    for unit, row in units(prose):
        if row:
            cells = [cell for cell in unit if cell]
            mentions = [m.group() for cell in cells for m in record_ids(cell)]
            label = bool(cells) and opens_with_id(cells[0])
            sample = '| ' + ' | '.join(unit) + ' |'
        else:
            mentions = [m.group() for m in record_ids(unit)]
            label = opens_with_id(unit)
            sample = unit
        if not mentions:
            continue
        cluster = len(set(mentions)) >= CLUSTER
        charged = 0
        for index, mention in enumerate(mentions):
            free = mention not in seen and not cluster and not (label and index == 0)
            seen.add(mention)
            if not free:
                charged += 1
        if charged:
            count += charged
            samples.append(sample)
    budget = max(MINIMUM_BUDGET, wordcount / float(per_words))
    if count <= budget:
        return None
    return count, budget, wordcount, samples
