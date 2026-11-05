"""Read-only candidates for recurring 'The + noun' framing.

This is a structural heuristic, not a noun blacklist or a rename instruction.
Names, quotations and intentional repetition can legitimately match it.
"""
import re

# These anchors improve precision for two-label sets and prose announcements.
# Three distinct short labels can be reported without any anchor vocabulary.
ANCHORS = frozenset('bet|call|problem|workspace|project|promise|engine|win|snag|'
                    'move|finish|knot|route|marker|headline|lever|window|horizon|'
                    'vehicle|receipt|nest|launchpad|looking glass|spark|relay|'
                    'landing|compass|handshake|archive|unlock|play|payoff|pivot|'
                    'takeaway|trick|catch|twist|bottom line|big picture'.split('|'))
WORD = r"[A-Za-z]+(?:['’][A-Za-z]+)?"
LABEL = re.compile(rf'^the\s+({WORD}(?:\s+{WORD}){{0,2}})$', re.I)
ANNOUNCEMENT = re.compile(
    rf'(?<!\w)the\s+({WORD}(?:[ \t]+{WORD}){{0,2}})[ \t]+(?:is|are|was|were)\b', re.I)
RELATIONAL = {'of', 'for', 'in', 'on', 'at', 'to', 'and', 'or', 'with', 'from', 'by'}
CLAUSE_WORDS = {'is', 'are', 'was', 'were', 'has', 'have', 'had', 'will', 'can',
                'must', 'should', 'says', 'said', 'does', 'did', 'grades', 'works'}
NON_LABEL_WORDS = RELATIONAL | CLAUSE_WORDS


def framing_candidates(text):
    """Return one document-level set, keeping samples and their observed shape.

    At least two different labels and two anchors, or three different short
    labels, are needed. Prose needs at least two different anchored copula
    announcements. Repeated instances of one name alone are insufficient.
    Locations refer to extracted text, not source document coordinates.
    """
    matches = []
    for number, raw in enumerate(str(text).splitlines(), 1):
        # Markdown cells and standalone labels share the same authored surface.
        # Retain full prose for the independent announcement scan below.
        for cell in raw.split('|'):
            value = re.sub(r'^\s*(?:#{1,6}\s+|>\s*|[-*+]\s+|\d+[.)]\s+)', '', cell).strip()
            value = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', value)
            value = re.split(r'\s+[—–-]\s+|:\s*', value, maxsplit=1)[0]
            value = value.strip(' \t*_`"“”\'‘’')
            match = LABEL.fullmatch(value)
            if match:
                noun = match[1].lower()
                if not NON_LABEL_WORDS.intersection(noun.split()):
                    matches.append({'noun': noun, 'shape': 'label', 'line': number, 'sample': value})
        for match in ANNOUNCEMENT.finditer(raw):
            noun = match[1].lower()
            if noun in ANCHORS:
                matches.append({'noun': noun, 'shape': 'announcement', 'line': number,
                                'sample': match[0]})
    # A label repeated as page furniture or a stable name is not a series.
    unique = {}
    for item in matches:
        unique.setdefault(item['noun'], item)
    labels = {m['noun'] for m in matches if m['shape'] == 'label'}
    anchored = set(unique) & ANCHORS
    if len(labels) < 3 and len(anchored) < 2:
        return []
    return list(unique.values())
