#!/usr/bin/env python3
"""Structural and distributional prose checks.

Word-level style filters catch banned vocabulary and characters. This catches
banned *shapes*, and the density of shapes that are individually legal.

Rules are specified in ../references/construction-rules.md. House-specific
budgets and vocabulary go in a JSON config; see ../references/house-overlay.md.

Usage:
    python3 prose_check.py FILE [FILE ...]
    python3 prose_check.py --json FILE
    python3 prose_check.py --config house.json FILE
    python3 prose_check.py --em-dash-budget 1 FILE

Exit codes:
    0  no findings
    1  one or more findings, including WARN
    2  bad invocation / unreadable input

Supports .md, .txt, .html, .docx, .pptx. No third-party dependencies.
"""

import argparse
import json
import re
import textwrap
import sys
import zipfile
from collections import Counter
from pathlib import Path
from framing import framing_candidates
from context_signals import context_candidates

# --------------------------------------------------------------------------
# Text extraction
# --------------------------------------------------------------------------

OOXML_PARTS = {
    ".docx": lambda n: n == "word/document.xml",
    ".pptx": lambda n: n.startswith("ppt/slides/slide") and n.endswith(".xml"),
}


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix in OOXML_PARTS:
        keep = OOXML_PARTS[suffix]
        chunks = []
        with zipfile.ZipFile(path) as z:
            for name in sorted(z.namelist()):
                if not keep(name):
                    continue
                xml = z.read(name).decode("utf-8", "replace")
                # Paragraph and line breaks become newlines so sentence and
                # heading detection survives the round trip.
                xml = re.sub(r"</a:p>|</w:p>|<w:br/>|<a:br/>", "\n", xml)
                xml = re.sub(r"<[^>]+>", "", xml)
                chunks.append(xml)
        return unescape_xml("\n".join(chunks))

    raw = path.read_text(encoding="utf-8", errors="replace")

    if suffix in {".md", ".markdown"}:
        raw = strip_quoted(raw)

    if suffix in {".html", ".htm"}:
        raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
        raw = re.sub(r"<(p|div|br|li|h[1-6]|tr)\b[^>]*>", "\n", raw, flags=re.I)
        raw = re.sub(r"<[^>]+>", " ", raw)
        raw = unescape_xml(raw)

    return raw


def strip_quoted(md: str) -> str:
    """Remove material the author is quoting rather than writing.

    A rules document that cites bad prose as an example would otherwise fail on
    its own examples. Fenced blocks, inline code spans, and blockquotes are all
    verbatim citation, so they are excluded from analysis. Line count is
    preserved so heading and adjacency checks stay aligned.
    """
    out = []
    in_fence = False
    protected_index = 0

    def protected_token(_match) -> str:
        nonlocal protected_index
        protected_index += 1
        n = protected_index
        suffix = ""
        while n:
            n, rem = divmod(n - 1, 26)
            suffix = chr(97 + rem) + suffix
        return " qzxprotected{} ".format(suffix)

    for line in md.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence or line.lstrip().startswith(">"):
            out.append("")
            continue
        # Remove Markdown link targets before sentence splitting. A target such
        # as `output-contract.md` contains punctuation that otherwise creates a
        # fake sentence boundary. Replace inline code with a neutral token so
        # the surrounding authored sentence keeps its grammar while the quoted
        # literal remains outside lexical checks.
        line = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", line)
        out.append(re.sub(r"`[^`]*`", protected_token, line))
    return "\n".join(out)


def unescape_xml(s: str) -> str:
    for entity, char in (
        ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
        ("&quot;", '"'), ("&apos;", "'"), ("&#8217;", "’"),
        ("&nbsp;", " "),
    ):
        s = s.replace(entity, char)
    return s


# --------------------------------------------------------------------------
# Tokenising
# --------------------------------------------------------------------------

# A single Markdown newline is usually a hard wrap inside one sentence. Split
# after terminal punctuation or across a blank line. Treating every wrapped line
# as a sentence manufactured fragments in skill instructions and README files.
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])(?:[ \t]+|\n+)|\n{2,}")

# Finite-verb proxy. A sentence with none of these and no -ed/-es/-ing verb form
# is treated as verbless. Deliberately generous: we would rather miss a fragment
# than flag a real sentence.
VERBS = {
    "is", "are", "was", "were", "be", "been", "being", "am",
    "has", "have", "had", "do", "does", "did", "can", "could",
    "will", "would", "shall", "should", "may", "might", "must",
    "runs", "run", "ran", "holds", "hold", "held", "takes", "take",
    "makes", "make", "gets", "get", "goes", "go", "comes", "come",
    "sits", "sit", "carries", "carry", "needs", "need", "owns", "own",
    "stays", "stay", "means", "mean", "shows", "show", "gives", "give",
    "sees", "see", "says", "say", "knows", "know", "works", "work",
    "exists", "exist", "appears", "appear", "follows", "follow",
    "opens", "open", "stops", "stop", "leaves", "leave", "moves", "move",
    "requires", "require", "answers", "answer", "recurs", "recur",
    "ships", "ship", "pays", "pay", "deploys", "deploy", "waits", "wait",
    "blocks", "block", "clears", "clear", "fires", "fire", "scored",
    "use", "uses", "write", "writes", "read", "reads", "run", "runs",
    "locate", "locates", "include", "includes", "deliver", "delivers",
    "link", "links", "record", "records", "name", "names", "fix", "fixes",
    "decide", "decides", "report", "reports", "emit", "emits",
    "validate", "validates", "rewrite", "rewrites", "inspect", "inspects",
    "confirm", "confirms", "list", "lists", "return", "returns",
    "gate", "gates", "keep", "keeps",
    "state", "states", "invent", "invents",
}

VERB_SUFFIX = re.compile(r"\w+(?:ed|ing|ates|ises|izes|fies)$")

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at", "by",
    "for", "with", "from", "as", "is", "are", "was", "were", "be", "it", "its",
    "this", "that", "these", "those", "not", "no", "one", "all", "any", "each",
    "they", "their", "we", "our", "you", "your", "so", "then", "than", "when",
}


def words(text: str):
    return re.findall(r"[A-Za-z][A-Za-z'’-]*", text)


def sentences(text: str):
    for raw in SENTENCE_SPLIT.split(text):
        s = raw.strip()
        if s:
            yield s


def has_finite_verb(sentence: str) -> bool:
    toks = [w.lower() for w in words(sentence)]
    if any(t in VERBS for t in toks):
        return True
    return any(VERB_SUFFIX.match(t) for t in toks)


def is_heading(line: str) -> bool:
    """Headings in extracted text: markdown hashes, or a short line with no
    terminal punctuation. Slide titles land in the second case."""
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return True
    if len(words(stripped)) > 12:
        return False
    return stripped[-1] not in ".!?,;:"


# --------------------------------------------------------------------------
# Patterns
# --------------------------------------------------------------------------

# C1: ", and/but/so" followed by a token that reliably opens a new independent
# clause (determiner, pronoun, expletive, or a capitalised subject).
BALANCED_CLAUSE = re.compile(
    r",\s+(?:and|but|so|yet)\s+"
    r"(?:the|a|an|it|its|they|their|we|our|you|your|this|that|these|those|"
    r"there|no|none|nothing|[A-Z][a-z]+)\b"
)

ANTITHESIS = [
    (re.compile(r",\s+not\s+(?:a|an|the|yet)\b", re.I), "X, not Y"),
    (re.compile(r"\bnot\s+\w+[^.]{0,40},\s+but\b", re.I), "not X, but Y"),
    (re.compile(r"\bthe\s+most\s+\w+\b[^.]{0,50}\bthe\s+most\s+\w+", re.I), "most-A is most-B"),
    (re.compile(r"\b\w+\s+\w+s\s+it\s+and\s+the\s+\w+\s+\w+s\s+it\b", re.I), "X does it and Y blocks it"),
]

NUMBER_WORDS = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|\d+)"
# A count-headline modifies a plural noun: "Nine stages", "Your four examples".
# A row that merely starts with a digit is enumeration, not rhetoric.
NUMBER_FORWARD_HEADING = re.compile(
    rf"^\s*(?:#+\s*)?(?:the\s+|your\s+|all\s+)?{NUMBER_WORDS}\s+\w+?s\b", re.I
)
SPELLED_COUNT = re.compile(
    r"^\s*(?:#+\s*)?(?:the|your|all)?\s*"
    r"(?:two|three|four|five|six|seven|eight|nine|ten)\b", re.I
)

DEFERENCE = [
    re.compile(r"\byou\s+asked\b", re.I),
    re.compile(r"\bas\s+(?:you\s+)?requested\b", re.I),
    re.compile(r"\bin\s+your\s+order\b", re.I),
    re.compile(r"\byour\s+(?:four|three|two|five|\d+)\s+\w+", re.I),
    re.compile(r"\bthe\s+\w+\s+you\s+(?:asked|wanted|named)\b", re.I),
    re.compile(r"\bper\s+your\s+request\b", re.I),
]

SELF_NARRATION = [
    re.compile(r"^\s*the\s+story\s*$", re.I | re.M),
    re.compile(r"^\s*what\s+it\s+means\s*$", re.I | re.M),
    re.compile(r"\bin\s+this\s+section\s+we\b", re.I),
    re.compile(r"\bclick\s+(?:any|each|the)\b", re.I),
    re.compile(r"\bquestion,?\s+answered\b", re.I),
    re.compile(r"\bretellable\b", re.I),
]

# C7: rhetorical triad. Three single-word evaluative adjectives in an "a, b,
# and c" series ("fast, clean, and simple"), where one true item would carry the
# point. Deliberately narrow. A corpus study of 689 real "a, b, and c" hits
# across the estate found the old comma-shape detector fired almost entirely on
# factual enumerations ("Waterfall, Agile, and Assess"; "30, 60, and 90 days";
# "authors, gates, and builds"). Requiring three adjective items and rejecting
# the tail of longer lists, proper nouns, and plural or verb forms took
# precision to 100% with zero false positives on that corpus. See patterns.md.
_TRIAD_ITEMS = re.compile(
    r"(?P<a>[A-Za-z][\w'-]*),\s+(?P<b>[A-Za-z][\w'-]*),?\s+(?:and|or)\s+(?P<c>[A-Za-z][\w'-]*)\b"
)
_ADJ_SUFFIX = ("able", "ible", "ive", "ous", "ful", "less")
_PLURAL_KEEP = ("ss", "us", "is", "ous")
TRIAD_ADJECTIVES = {
    "fast", "quick", "rapid", "clean", "simple", "easy", "safe", "secure",
    "robust", "scalable", "reliable", "flexible", "powerful", "seamless",
    "compelling", "concise", "intuitive", "modern", "elegant", "efficient",
    "sleek", "lightweight", "cheap", "affordable", "smart", "clear", "bold",
    "crisp", "slick", "nimble", "lean", "sharp", "smooth", "polished",
    "cohesive", "consistent", "flawless", "effortless", "frictionless",
    "performant", "delightful", "beautiful", "clever", "modular", "durable",
    "resilient", "accurate", "precise", "rich", "strong", "solid", "slim",
}


def _triad_is_adjective(word):
    w = word.lower()
    if w in TRIAD_ADJECTIVES:
        return True
    return len(w) > 4 and w.endswith(_ADJ_SUFFIX)


def _triad_is_plural(word):
    w = word.lower()
    return w.endswith("s") and not w.endswith(_PLURAL_KEEP)


def rhetorical_triads(text):
    """Three single-word evaluative adjectives in an "a, b, and c" series.

    Narrow by design: rejects the tail of a 4+ item list, proper nouns, and
    plural or verb forms, so factual enumerations do not register.
    """
    hits = []
    for m in _TRIAD_ITEMS.finditer(text):
        a, b, c = m.group("a"), m.group("b"), m.group("c")
        if text[:m.start("a")].rstrip().endswith(","):
            continue  # tail of a longer Oxford list, not a triad
        if b[0].isupper() or c[0].isupper():
            continue  # named entities, not rhetoric
        if a[0].isupper() and m.start("a") != 0:
            continue  # a capital is allowed only sentence-initially
        items = [a, b, c]
        if any(_triad_is_plural(w) for w in items):
            continue  # verb triad or plural-noun list
        if not all(_triad_is_adjective(w) for w in items):
            continue
        hits.append(m.group(0).strip())
    return hits

UNSOURCED_QUANTIFIER = re.compile(
    r"\b(?:thousands\s+of|hundreds\s+of|most\s+of\s+the|most\s+\w+s\b|"
    r"many\s+\w+s\b|the\s+majority\s+of|countless|numerous)\b", re.I
)

FEAR_FRAME = re.compile(r"\b(?:exposure|recurs?\s+(?:every|annually)|depreciating\s+asset)\b", re.I)

RANGE_NOTATIONS = {
    "en-dash": re.compile(r"\d\s*–\s*\d"),
    "hyphen": re.compile(r"\d\s*-\s*\d"),
    "to-word": re.compile(r"\d+\s+to\s+\d+"),
}

APPROX_NOTATIONS = {
    "tilde": re.compile(r"~\s*\d"),
    "plus-suffix": re.compile(r"\d\+"),
    "circa-word": re.compile(r"\b(?:approx\.?|approximately|about|roughly)\s+\d", re.I),
}

ALL_CAPS_BLOCK = re.compile(
    r"^[^a-z\n]*\b[A-Z]{2,}\b(?:[^a-z\n]*\b[A-Z]{2,}\b){2,}[^a-z\n]*$", re.M
)

EM_DASH = "—"

# C18-C23: bendrucker word-choice and hedging tells, mechanized where a regex is
# low-risk. Heading-shape ("Topic: clause") stays judgment-only in patterns.md,
# because the house deliberately uses colon headings ("Gating: run the checker").
COPULA_AVOIDANCE = re.compile(r"\b(?:serves?|stands?)\s+as\b", re.I)
# "load-bearing" is deliberately absent: the house uses it as a term of art
# ("load-bearing evidence", "load-bearing claim"), not as a gravity marker.
GRAVITY_MARKERS = re.compile(
    r"\b(?:the honest answer|worth flagging|the full picture|the cleanup story|"
    r"make no mistake|at its core)\b", re.I,
)
DIG_DIVE = re.compile(r"\b(?:dig|digs|digging|dive|dives|diving)\s+into\b|\bdeep\s+dive\b", re.I)
# "looks like" is excluded: "what good looks like" is a fixed idiom, not a hedge.
HEDGE_VERB = re.compile(r"\b(?:appears?\s+to|seems?\s+to)\b", re.I)
TRAILING_HEDGE_ADVERB = re.compile(r"\b(?:regardless|nonetheless|nevertheless|notwithstanding)\s*\.", re.I)

# Layer 1, mechanical. A clause-justification tail explains a claim's own benefit
# in a trailing subordinate or participial phrase. It is the em dash's cousin:
# take away the tail and the sentence states the fact instead of selling it.
JUSTIFICATION_TAIL = re.compile(
    r",\s+(?:which|that)\s+(?:allows?|enables?|ensures?|means?|lets?|makes?|helps?)\b"
    r"|,\s+(?:allowing|enabling|ensuring|helping|letting|driving|delivering|"
    r"unlocking|streamlining|empowering|facilitating|positioning)\b",
    re.I,
)


# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "em_dash_budget": 0,
    "balanced_clause_per_words": 200,
    "triad_per_words": 500,   # retained for back-compat; C7 no longer amortizes
    "triad_enabled": True,     # C7 rhetorical-triad detection (adjective triads)
    "banned_terms": [],
    "allowed_repeated_phrases": [],
    # Layer 1, house-specific. Empty here; the Estate values live in house.json.
    "hedge_openers": [],          # phrases that clear the throat before the point (FAIL)
    "banned_chars": [],           # characters that must not appear, e.g. the section sign (FAIL)
    "flag_justification_tails": True,  # ", which enables..." benefit tails (WARN)
}


def load_config(path):
    """House overrides. Every key is optional; omitted keys keep the default."""
    cfg = dict(DEFAULT_CONFIG)
    if path:
        user = json.loads(Path(path).read_text(encoding="utf-8"))
        # Keys beginning with "_" are treated as comments and ignored.
        user = {k: v for k, v in user.items() if not k.startswith("_")}
        unknown = set(user) - set(DEFAULT_CONFIG)
        if unknown:
            raise ValueError(f"unknown config key(s): {', '.join(sorted(unknown))}")
        cfg.update(user)
    return cfg


class Finding:
    def __init__(self, rule, severity, message, samples=None):
        self.rule = rule
        self.severity = severity
        self.message = message
        self.samples = samples or []

    def as_dict(self):
        return {
            "rule": self.rule,
            "severity": self.severity,
            "message": self.message,
            "samples": self.samples[:3],
        }


def check(text: str, cfg=None):
    cfg = cfg or dict(DEFAULT_CONFIG)
    findings = []
    wordcount = max(len(words(text)), 1)
    lines = text.splitlines()
    sents = list(sentences(text))

    framing = framing_candidates(text)
    if framing:
        findings.append(Finding(
            'C24-formulaic-the-framing', 'WARN',
            f'{len(framing)} distinct repeated The + noun frames are review candidates. '
            'Read their content and purpose; this is not a verdict or a rename instruction. '
            'Preserve ordinary grammar, deliberate names and repetition, exact quotations '
            'and required identifiers. Locations refer to extracted text.',
            [f"line {item['line']} ({item['shape']}): {item['sample']}" for item in framing],
        ))

    for rule, message, samples in context_candidates(text):
        findings.append(Finding(rule, "WARN", message, samples))

    def per(n, unit):
        return round(n * unit / wordcount, 2)

    # --- Em dashes -------------------------------------------------------
    em = text.count(EM_DASH)
    allowed = cfg["em_dash_budget"]
    if em > allowed:
        findings.append(Finding(
            "em-dash", "FAIL",
            f"{em} em dashes, budget {allowed}.",
            [s for s in sents if EM_DASH in s],
        ))

    # --- C1 balanced two-clause sentences --------------------------------
    bal = [s for s in sents if BALANCED_CLAUSE.search(s)]
    budget = wordcount / float(cfg["balanced_clause_per_words"])
    if bal and len(bal) > budget * 2:
        sev = "FAIL"
    elif bal and len(bal) > budget:
        sev = "WARN"
    else:
        sev = None
    if sev:
        findings.append(Finding(
            "C1-balanced-clause", sev,
            f"{len(bal)} balanced two-clause sentences, budget {budget:.1f} "
            f"({per(len(bal), 200)} per 200 words). Em-dash residue: split into "
            f"sentences of unequal length.",
            bal,
        ))

    # --- C2 antithesis ---------------------------------------------------
    anti = []
    for pattern, label in ANTITHESIS:
        for s in sents:
            if pattern.search(s):
                anti.append(f"[{label}] {s}")
    if len(anti) > 1:
        findings.append(Finding(
            "C2-antithesis", "WARN",
            f"{len(anti)} antithesis constructions, budget 1 per document.",
            anti,
        ))

    # --- C4 number-forward headings --------------------------------------
    heads = [ln.strip() for ln in lines if is_heading(ln)]
    numeric_heads = [
        h for h in heads
        # A legend row ("1 holding up") or a numbered step is enumeration, not
        # rhetoric. Require a real headline: three words minimum, and either a
        # spelled-out count or enough words to be a sentence-like title.
        if len(words(h)) >= 3
        and NUMBER_FORWARD_HEADING.match(h)
        and (SPELLED_COUNT.match(h) or len(words(h)) >= 5)
    ]
    if len(numeric_heads) > 1:
        findings.append(Finding(
            "C4-number-forward-heading", "WARN",
            f"{len(numeric_heads)} headings built on a count, budget 1. "
            f"Name the content; put the count in the body.",
            numeric_heads,
        ))

    # --- C6 fragment stacking --------------------------------------------
    # Headings, slide titles, and table cells are legitimately verbless. Only
    # body sentences count toward the fragment budget.
    heading_set = {h for h in heads}
    # Separate list items are separate contexts. Check prose within an item
    # and its continuation instead of blanking the whole list.
    def fragment_parts(block):
        parts, current = [], []
        in_item = False
        previous_blank = False
        for raw_line in textwrap.dedent(block).strip('\n').splitlines():
            removed_marker = '<!--' in raw_line or '-->' in raw_line
            line = raw_line.replace('<!--', '').replace('-->', '')
            stripped = line.strip()
            bullet = re.match(r'^\s*(?:[-*+] |\d+[.)] )', line)
            marker = removed_marker and re.fullmatch(r'[A-Z][A-Z0-9_-]*:(?:BEGIN|END)', stripped)
            if bullet:
                if current:
                    parts.append('\n'.join(current))
                current = [line[bullet.end():]]
                in_item = True
            elif in_item and stripped.startswith('#'):
                if current:
                    parts.append('\n'.join(current))
                current = []
                in_item = False
            elif marker or stripped.startswith(('|', '#')):
                current.append('')
            else:
                if in_item and previous_blank and stripped and not line[:1].isspace():
                    parts.append('\n'.join(current))
                    current = []
                    in_item = False
                current.append(line)
            previous_blank = not stripped
        if current:
            parts.append('\n'.join(current))
        return parts

    fragment_blocks = [part for block in getattr(text, 'fragment_blocks', [text])
                       for part in fragment_parts(block)]
    block_flags = [[(s, not has_finite_verb(s)) for s in sentences(block) if s not in heading_set]
                   for block in fragment_blocks]
    verbless_flags = [item for block in block_flags for item in block]
    verbless = [s for s, flag in verbless_flags if flag and 2 <= len(words(s)) <= 7]
    consecutive = [
        f"{a} / {b}"
        for block in block_flags
        for (a, fa), (b, fb) in zip(block, block[1:])
        if fa and fb and 2 <= len(words(a)) <= 7 and 2 <= len(words(b)) <= 7
    ]
    if consecutive:
        findings.append(Finding(
            "C6-fragment-stacking", "WARN",
            f"{len(consecutive)} runs of consecutive verbless sentences, budget 0. "
            f"{len(verbless)} verbless sentences overall.",
            consecutive,
        ))

    # --- C7 rhetorical triads --------------------------------------------
    # Three evaluative adjectives said for rhythm ("fast, clean, and simple"),
    # where one true item would carry the point. Factual enumerations do not trip
    # this: see rhetorical_triads() and the corpus note in patterns.md. WARN, not
    # FAIL, because a distinct-property adjective triad ("secure, scalable, and
    # auditable") can be legitimate and is a human call. Any hit fires; there is
    # no word-count budget, since the measured false-positive rate is zero.
    triads = []
    for s in sents:
        triads.extend(rhetorical_triads(s))
    if cfg.get("triad_enabled", True) and triads:
        findings.append(Finding(
            "C7-triad", "WARN",
            f"{len(triads)} rhetorical triad(s): three adjectives where one is "
            "probably the true one. Name it.",
            triads,
        ))

    # --- C10 deference ---------------------------------------------------
    # A sentence counts once however many patterns it trips.
    defer = [s for s in sents if any(p.search(s) for p in DEFERENCE)]
    if defer:
        findings.append(Finding(
            "C10-deference", "FAIL",
            f"{len(defer)} deference phrases, budget 0. Deliver the answer without "
            f"labelling whose question it answers.",
            defer,
        ))

    # --- C9 self-narration -----------------------------------------------
    narr = [s for s in sents for p in SELF_NARRATION if p.search(s)]
    if narr:
        findings.append(Finding(
            "C9-self-narration", "FAIL",
            f"{len(narr)} self-narration markers, budget 0.",
            narr,
        ))

    # --- C12 verbatim recycling ------------------------------------------
    # N-grams are built per line so a phrase never spans a slide or table-cell
    # boundary. Lines that recur three or more times are page furniture
    # (footers, confidentiality labels, page numbers) and are excluded.
    repetition_lines = getattr(text, 'repetition_text', text).splitlines()
    furniture_lines = getattr(text, 'furniture_text', text).splitlines()
    line_counts = Counter(ln.strip().lower() for ln in furniture_lines if ln.strip())
    furniture = {ln for ln, n in line_counts.items() if n >= 3}

    grams = Counter()
    dates = re.compile(r'\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b', re.I)
    for ln, furniture_allowed in getattr(text, 'repetition_lines', [(line, True) for line in repetition_lines]):
        stripped = ln.strip()
        if not stripped or (furniture_allowed and stripped.lower() in furniture):
            continue
        # A date occupies one token; table columns remain separate fields.
        for field in (re.split(r'(?<!\\)\|', stripped) if stripped.startswith('|') else [stripped]):
            for span in [dates.sub(lambda match: '-'.join(match.group().split()), field)]:
                toks = [t.lower() for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9'’%$.-]*", span)]
                for i in range(len(toks) - 3):
                    grams[" ".join(toks[i:i + 4])] += 1

    exempt = [p.lower() for p in cfg["allowed_repeated_phrases"]]
    repeats = [
        g for g, n in grams.most_common()
        if n > 1
        # At least two content words, so "of the first and" does not register.
        and sum(1 for t in g.split() if t not in STOPWORDS) >= 2
        # Strings that must match across documents by contract are deliberate.
        and not any(g in e or e in g for e in exempt)
    ]
    if repeats:
        findings.append(Finding(
            "C12-verbatim-recycling", "WARN",
            f"{len(repeats)} phrases of 4+ words appear more than once. "
            f"Consolidate to one authoritative home.",
            repeats,
        ))

    # --- C15 unsourced quantifiers ---------------------------------------
    quant = [s for s in sents if UNSOURCED_QUANTIFIER.search(s)]
    if quant:
        findings.append(Finding(
            "C15-unsourced-quantifier", "WARN",
            f"{len(quant)} unsourced quantifiers. Give a number with a source, or nothing.",
            quant,
        ))

    # --- C16 notation drift ----------------------------------------------
    used_ranges = [name for name, p in RANGE_NOTATIONS.items() if p.search(dates.sub(' ', text))]
    if len(used_ranges) > 1:
        findings.append(Finding(
            "C16-notation-drift", "WARN",
            f"{len(used_ranges)} range notations in one document: {', '.join(used_ranges)}. "
            f"Pick one.",
        ))
    used_approx = [name for name, p in APPROX_NOTATIONS.items() if p.search(text)]
    if len(used_approx) > 1:
        findings.append(Finding(
            "C16-approximation-drift", "WARN",
            f"{len(used_approx)} approximation notations: {', '.join(used_approx)}. Pick one.",
        ))

    # --- C17 fear framing ------------------------------------------------
    fear = [s for s in sents if FEAR_FRAME.search(s)]
    if fear:
        findings.append(Finding(
            "C17-fear-framing", "WARN",
            f"{len(fear)} recurring-loss frames. State the figure and its period.",
            fear,
        ))

    # --- C18 copula avoidance --------------------------------------------
    copula_n = len(COPULA_AVOIDANCE.findall(text))
    if copula_n > 1:
        findings.append(Finding(
            "C18-copula-avoidance", "WARN",
            f"{copula_n} 'serves as'/'stands as' constructions, budget 1. "
            f"Use is/are unless a specific verb carries meaning.",
            [s for s in sents if COPULA_AVOIDANCE.search(s)],
        ))

    # --- C19 gravity markers ---------------------------------------------
    grav = [s for s in sents if GRAVITY_MARKERS.search(s)]
    if grav:
        findings.append(Finding(
            "C19-gravity-marker", "WARN",
            f"{len(grav)} gravity markers, budget 0. Assert with substance, not a "
            f"label: name what breaks, or state the fact.",
            grav,
        ))

    # --- C20 dig/dive into -----------------------------------------------
    dig = [s for s in sents if DIG_DIVE.search(s)]
    if dig:
        findings.append(Finding(
            "C20-dig-dive", "WARN",
            f"{len(dig)} 'dig into'/'dive into'/'deep dive', budget 0. Name what "
            f"you are looking at.",
            dig,
        ))

    # --- C21 vague hedge verbs -------------------------------------------
    hv_n = len(HEDGE_VERB.findall(text))
    if hv_n > 1:
        findings.append(Finding(
            "C21-hedge-verb", "WARN",
            f"{hv_n} vague hedge verbs (appears to / seems to / looks like), "
            f"budget 1. State it directly, or name the uncertainty.",
            [s for s in sents if HEDGE_VERB.search(s)],
        ))

    # --- C23 trailing hedge adverbs --------------------------------------
    tha = [s for s in sents if TRAILING_HEDGE_ADVERB.search(s)]
    if tha:
        findings.append(Finding(
            "C23-trailing-hedge-adverb", "WARN",
            f"{len(tha)} trailing hedge adverbs (regardless. / nonetheless.), "
            f"budget 0. Cut it.",
            tha,
        ))

    # --- House banned terms ----------------------------------------------
    if cfg["banned_terms"]:
        pat = re.compile(
            r"\b(?:" + "|".join(re.escape(t) for t in cfg["banned_terms"]) + r")\b", re.I
        )
        hits = [s for s in sents if pat.search(s)]
        if hits:
            findings.append(Finding(
                "house-banned-term", "FAIL",
                f"{len(hits)} sentences contain house-banned vocabulary.",
                hits,
            ))

    # --- House hedge openers ---------------------------------------------
    if cfg["hedge_openers"]:
        hpat = re.compile("|".join(cfg["hedge_openers"]), re.I)
        hedges = [s for s in sents if hpat.search(s)]
        if hedges:
            findings.append(Finding(
                "house-hedge-opener", "FAIL",
                f"{len(hedges)} throat-clearing hedge openers, budget 0. Open on the point.",
                hedges,
            ))

    # --- House banned characters (e.g. the section sign) -----------------
    if cfg["banned_chars"]:
        present = [c for c in cfg["banned_chars"] if c in text]
        if present:
            findings.append(Finding(
                "house-banned-char", "FAIL",
                f"banned character(s) present: {' '.join(present)}. Write the word in full.",
                [s for s in sents if any(c in s for c in present)],
            ))

    # --- Clause-justification tails (layer 1) ----------------------------
    if cfg["flag_justification_tails"]:
        tails = [s for s in sents if JUSTIFICATION_TAIL.search(s)]
        if tails:
            findings.append(Finding(
                "justification-tail", "WARN",
                f"{len(tails)} clause-justification tails. Cut the tail or state the fact plainly.",
                tails,
            ))

    # --- All-caps blocks -------------------------------------------------
    caps = ALL_CAPS_BLOCK.findall(text)
    caps = [c.strip() for c in caps if len(words(c)) >= 3]
    if caps:
        findings.append(Finding(
            "all-caps-block", "FAIL",
            f"{len(caps)} all-caps blocks, budget 0. Sentence case throughout.",
            caps,
        ))

    return findings, wordcount


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

SEV_ORDER = {"FAIL": 0, "WARN": 1}


def main():
    # Preserve the historical command name without retaining its quotation bypass.
    from writing_check import main as universal_main
    return universal_main()


if __name__ == "__main__":
    sys.exit(main())
