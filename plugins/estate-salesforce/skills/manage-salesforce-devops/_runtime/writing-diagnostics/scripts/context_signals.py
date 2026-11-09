"""Read-only contextual review signals, not judgments of usefulness or truth.

The heuristics deliberately miss broad semantic cases. No match authorizes an
edit; no absence of a match establishes that a claim or requirement is justified.
"""
from dataclasses import dataclass, field
from html.parser import HTMLParser
import re

MAX_CHARS = 4_000_000
MAX_BLOCKS = 20_000
TABLE = 'C25-table-narration-candidate'
ACTION = 'C26-action-basis-candidate'
REAFFIRM = 'C27-reaffirmation-candidate'
RULES = frozenset({TABLE, ACTION, REAFFIRM})


@dataclass
class ReviewBlock:
    kind: str
    text: str
    location: str
    rows: list = field(default_factory=list)
    element_id: str = ''
    purpose: str = ''
    ancestor_ids: tuple = ()


def _cells(line):
    return [cell.strip() for cell in line.strip().strip('|').split('|')]


def markdown_blocks(text):
    lines, result, index = str(text).splitlines(), [], 0
    while index < len(lines):
        raw = lines[index]
        if not raw.strip():
            index += 1
            continue
        divider = (index + 1 < len(lines) and '|' in raw and
                   len(_cells(lines[index + 1])) >= 2 and
                   all(re.fullmatch(r':?-{3,}:?', c.replace(' ', '')) for c in _cells(lines[index + 1])))
        pipe_grid = (raw.strip().startswith('|') and raw.strip().endswith('|') and
                     index + 1 < len(lines) and lines[index + 1].strip().startswith('|') and len(_cells(raw)) >= 2)
        if divider or pipe_grid:
            start, rows = index, [_cells(raw)]
            index += 2 if divider else 1
            while index < len(lines) and '|' in lines[index] and lines[index].strip():
                rows.append(_cells(lines[index])); index += 1
            result.append(ReviewBlock('table', '\n'.join(lines[start:index]), f'line {start + 1}', rows))
            continue
        start, parts = index, [raw]
        index += 1
        heading = bool(re.match(r'^\s*#{1,6}\s+', raw))
        if not heading:
            while index < len(lines) and lines[index].strip() and not re.match(r'^\s*#{1,6}\s+', lines[index]):
                if index + 1 < len(lines) and '|' in lines[index] and re.search(r'\|?\s*:?-{3,}', lines[index + 1]):
                    break
                parts.append(lines[index]); index += 1
        result.append(ReviewBlock('heading' if heading else 'prose', '\n'.join(parts), f'line {start + 1}'))
    return result


HTML_VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class HTMLReview(HTMLParser):
    """Visible table and paragraph boundaries; never execute document content."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.parts, self.rows, self.row, self.cell = [], [], [], [], None
        self.kind, self.line, self.table_line = 'prose', 1, 1
        self.table_depth, self.hidden = 0, 0
        self.complex_table = False
        self.element_id, self.accessible_ids = '', set()
        self.elements = []
        self.part_ids = ()

    def flush(self):
        text = ''.join(self.parts).strip()
        if text:
            self.blocks.append(ReviewBlock(self.kind, text, f'HTML line {self.line}', element_id=self.element_id, ancestor_ids=self.part_ids))
        self.parts = []
        self.element_id = ''
        self.part_ids = ()

    def handle_starttag(self, tag, attrs):
        if tag not in HTML_VOID:
            self.elements.append((tag, dict(attrs).get('id', '')))
        if tag in {'script', 'style'}:
            self.hidden += 1
        if self.hidden:
            return
        if tag == 'table':
            attributes = dict(attrs)
            self.accessible_ids.update(attributes.get('aria-describedby', '').split())
            self.accessible_ids.update(attributes.get('aria-details', '').split())
            if self.table_depth:
                self.complex_table = True
            else:
                self.flush(); self.table_line = self.getpos()[0]; self.rows = []; self.complex_table = False
            self.table_depth += 1
        elif self.table_depth:
            if tag == 'tr': self.row = []
            if tag in {'td', 'th'}: self.cell = []
            if tag == 'br' and self.cell is not None: self.cell.append(' ')
        elif tag in {'p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'br'}:
            self.flush(); self.line = self.getpos()[0]
            self.kind = 'heading' if re.fullmatch(r'h[1-6]', tag) else 'prose'
            self.element_id = dict(attrs).get('id', '')

    def handle_endtag(self, tag):
        for index in range(len(self.elements) - 1, -1, -1):
            if self.elements[index][0] == tag:
                del self.elements[index:]
                break
        if tag in {'script', 'style'}:
            self.hidden = max(0, self.hidden - 1); return
        if self.hidden: return
        if self.table_depth:
            if tag in {'td', 'th'} and self.cell is not None:
                self.row.append(''.join(self.cell).strip()); self.cell = None
            elif tag == 'tr' and self.row: self.rows.append(self.row); self.row = []
            elif tag == 'table':
                self.table_depth -= 1
                if not self.table_depth:
                    if not self.complex_table:
                        self.blocks.append(ReviewBlock('table', '', f'HTML line {self.table_line}', self.rows))
                    else:
                        self.blocks.append(ReviewBlock('unstructured-table', '', f'HTML line {self.table_line}'))
                    self.kind = 'prose'; self.line = self.getpos()[0]
        elif tag in {'p', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'}:
            self.flush(); self.kind = 'prose'

    def handle_data(self, data):
        if self.hidden: return
        if self.table_depth:
            if self.cell is not None: self.cell.append(data)
        else:
            if not self.parts:
                self.part_ids = tuple(identifier for _, identifier in self.elements if identifier)
            self.parts.append(data)


def html_blocks(raw):
    parser = HTMLReview(); parser.feed(raw); parser.close(); parser.flush()
    for block in parser.blocks:
        if {block.element_id, *block.ancestor_ids} & parser.accessible_ids:
            block.purpose = 'accessible-alternative'
    return parser.blocks


def office_blocks(trees):
    """Paragraphs and simple Word/slide tables in document order, with part IDs."""
    result = []
    local = lambda node: node.tag.rsplit('}', 1)[-1]
    words = lambda node: ''.join(n.text or '' for n in node.iter() if local(n) == 't')

    def visit(node, member, counter):
        tag = local(node)
        if tag == 'tbl':
            if any(local(child) == 'tbl' for child in node.iter() if child is not node):
                result.append(ReviewBlock('unstructured-table', '', f'{member} nested table'))
                return
            rows = [[words(cell) for cell in row if local(cell) == 'tc'] for row in node if local(row) == 'tr']
            result.append(ReviewBlock('table', '', f'{member} table {len(result) + 1}', rows))
        elif tag == 'p':
            text = words(node).strip()
            if text:
                counter[0] += 1
                result.append(ReviewBlock('prose', text, f'{member} paragraph {counter[0]}'))
        else:
            for child in node: visit(child, member, counter)
    def part_order(item):
        match = re.fullmatch(r'ppt/slides/slide(\d+)\.xml', item[0])
        return (1, int(match.group(1))) if match else (0, item[0])

    for member, tree in sorted(trees, key=part_order):
        if member == 'word/document.xml' or re.fullmatch(r'ppt/slides/slide\d+\.xml', member):
            # Separate slides/parts are independently read surfaces; never invent adjacency.
            result.append(ReviewBlock('boundary', '', member))
            visit(tree, member, [0])
    return result


STOP = set('a an the and or of to for in on at by as with is are was were be been being has have had this that these those it its their there from above below table shows show says said respectively'.split())
NUMBERS = dict(zip('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split(), map(str, range(21))))
ALIASES = {'excluded': 'exclude', 'excludes': 'exclude', 'exclusion': 'exclude', 'boundary': 'scope', 'boundaries': 'scope', 'queued': 'waiting', 'queue': 'waiting'}


def tokens(text):
    value = re.sub(r'(?<=\d),(?=\d)', '', text.lower())
    return {ALIASES.get(word, NUMBERS.get(word, word)) for word in re.findall(r"[\w]+(?:[.-][\w]+)*%?", value) if word not in STOP}


def _table_signals(blocks):
    result = []
    for index, table in enumerate(blocks):
        # Short complete readouts only; long-table summaries are intentionally outside this signal.
        if table.kind != 'table' or not 3 <= len(table.rows) <= 7:
            continue
        if not all(len(row) == len(table.rows[0]) >= 2 for row in table.rows):
            continue
        rows = [tokens(' '.join(row)) for row in table.rows[1:]]
        vocabulary = tokens(' '.join(cell for row in table.rows for cell in row))
        for near in (index - 1, index + 1):
            if not 0 <= near < len(blocks): continue
            paragraph = blocks[near]
            if paragraph.kind != 'prose' or paragraph.purpose == 'accessible-alternative' or not 6 <= len(paragraph.text.split()) <= 100: continue
            content = tokens(paragraph.text)
            clauses = [tokens(clause) for clause in re.split(r'[.;,!?]|\band\b', paragraph.text, flags=re.I)]
            # Require each row's terms together; a bag of all cells can hide swapped values.
            if content and not content - vocabulary and all(row and any(row <= clause and sum(other <= clause for other in rows) == 1 for clause in clauses) for row in rows):
                result.append((TABLE,
                    'Adjacent prose repeats the labels/values of a short table without unmatched content terms. '
                    'Review whether the readout adds value for this reader; useful summaries, qualifications and accessible alternatives may be retained. This is not a redundancy verdict.',
                    [f'{table.location}: {len(rows)} data rows', f'{paragraph.location}: {paragraph.text[:300]}']))
    return result


GATE = re.compile(r'\b(?:what|which\s+(?:items|actions|tasks)|items\s+that)\b.{0,45}\b(?:must|has\s+to|have\s+to|needs?\s+to|required\s+to)\b.{0,55}\b(?:close[ds]?|resolv(?:e[ds]?|ing)|finish(?:ed)?|complete[ds]?|happen(?:s|ed)?|change[ds]?)\b.{0,35}\b(?:approv\w*|sign[ -]?off|authori[sz]\w*)\b', re.I)
VAGUE_GATE = re.compile(r'\b(?:close|resolve|finish|complete)\s+(?:these|those|everything|the\s+following)\b.{0,50}\b(?:approv\w*|sign[ -]?off)\b', re.I)
IMPERATIVE = re.compile(r'(?:^|[.!?]\s+|\n)\s*(?:[#>*-]+\s*)?(?:act|choose|approve|resolve|close|enable|turn|submit|sign|complete)\b', re.I)
DIRECTIVE = re.compile(r'\b(?:must|need\s+to|have\s+to|has\s+to)\b.{0,65}\b(?:now|today|immediately|urgently)\b', re.I)
PRESSURE = re.compile(r'\b(?:window|chance|time|opportunity)\b.{0,30}\b(?:clos\w*|running\s+out|expir\w*)\b|\bbefore\s+it(?:[’\']s|\s+is)\s+too\s+late\b|\bkeep\b.{0,35}\b(?:window|chance|opportunity)\b.{0,15}\bopen\b', re.I)
BASIS = re.compile(r'\b(?:policy|contract|signed\s+agreement|registrar|regulation|acceptance\s+(?:criterion|criteria)|source|requirement)\b', re.I)


def _action_signals(blocks):
    result = []
    for index, block in enumerate(blocks):
        if block.kind not in {'prose', 'heading'}: continue
        text = re.sub(r'\s+', ' ', block.text)
        if len(text) > 2000: continue
        gate = GATE.search(text) or VAGUE_GATE.search(text)
        pressure = (DIRECTIVE.search(text) or IMPERATIVE.search(text)) and PRESSURE.search(text)
        if not gate and not pressure: continue
        # Explicit nearby supporting material is outside this deliberately narrow signal.
        nearby = ' '.join(b.text for b in blocks[max(0, index - 1):index + 3] if b.kind != 'table')
        supporting = [clause for clause in re.split(r'[.!?;\n]', nearby)
                      if BASIS.search(clause) and not re.search(r"\b(?:no|not|without|lacks?|none|unverified|doesn[’']t|isn[’']t)\b", clause, re.I)]
        if supporting and len(tokens(' '.join(supporting))) >= 6: continue
        result.append((ACTION,
            'A generic approval prerequisite or a directive paired with closing-window pressure needs a basis review. '
            'Check the actual task and supplied requirements; wording and absent nearby evidence do not prove that urgency is unearned. Preserve genuine conditions and deadlines.',
            [f'{block.location}: {text[:350]}']))
    return result


REAFFIRM_FORM = re.compile(r'\b(?:still\s+(?:holds?|stands?|applies?|true)|remains?\s+(?:true|intact|unchanged|the\s+same|valid|in\s+force)|(?:is|are)\s+(?:still\s+)?unchanged|continues?\s+to\s+(?:hold|apply))\b', re.I)
STATE_WORDS = set('still hold holds stand stands applies true remain remains intact unchanged same valid original continues continue apply'.split())
REFERENTS = set('that this it original same scope limit protection point claim assurance result conclusion'.split())
NEW_CHECK = re.compile(r'\b(?:rechecked|verified|tested|inspected|amendment|revision|signed|compared|retested)\b', re.I)


def _reaffirmation_signals(blocks):
    sentences = []
    for block in blocks:
        if block.kind not in {'prose', 'heading'}: continue
        for sentence in re.split(r'(?<=[.!?])\s+|\n+', block.text):
            if sentence.strip(): sentences.append((sentence.strip(), block.location))
            if len(sentences) > MAX_BLOCKS:
                raise ValueError('Contextual review exceeds 20000 sentences; split and review the complete artifact explicitly.')
    result, used = [], set()
    for index in range(len(sentences) - 1, -1, -1):
        anchor, location = sentences[index]
        subject = tokens(anchor) - STATE_WORDS
        if len(subject) < 2 or REAFFIRM_FORM.search(anchor): continue
        group = []
        for other in range(index + 1, min(len(sentences), index + 13)):
            text, where = sentences[other]
            if other in used or not REAFFIRM_FORM.search(text) or NEW_CHECK.search(text): continue
            content_text = re.sub(r'^\s*(?:to be clear|as before|again)[,:]?\s*', '', text, flags=re.I)
            content = tokens(REAFFIRM_FORM.sub('', content_text)) - STATE_WORDS - REFERENTS
            if re.search(r'\d', text) or content - subject: continue
            if content & subject or (not content and re.search(r'\b(?:that|this|it|original|boundary|scope|limit)\b', text, re.I)):
                group.append((other, text, where))
        if len(group) >= 2 and len({text.lower() for _, text, _ in group}) >= 2:
            used.update(number for number, _, _ in group)
            result.append((REAFFIRM,
                'Multiple nearby reassurance clauses refer back to a claim without additional content terms in this signal. '
                'Review what each adds; new verification, technical limits, independently used reminders and purposeful repetition may justify retention. This does not prove the assertions unsupported.',
                [f'{location}: {anchor[:250]}'] + [f'{where}: {text[:250]}' for _, text, where in group[:2]]))
    return result


def context_candidates(text):
    if len(text) > MAX_CHARS:
        raise ValueError('Contextual review exceeds the 4-million-character input limit; split and review the complete artifact explicitly.')
    blocks = getattr(text, 'review_blocks', None)
    if blocks is None: blocks = markdown_blocks(text)
    if len(blocks) > MAX_BLOCKS:
        raise ValueError('Contextual review exceeds 20000 blocks; split and review the complete artifact explicitly.')
    result, section = [], []
    for block in [*blocks, ReviewBlock('boundary', '', 'end')]:
        if block.kind == 'boundary':
            result.extend(_table_signals(section) + _action_signals(section) + _reaffirmation_signals(section))
            section = []
        else:
            section.append(block)
    if len(result) > 100:
        raise ValueError('Contextual review exceeds 100 candidates; split and review the complete artifact explicitly. No partial result is a completed scan.')
    return result
