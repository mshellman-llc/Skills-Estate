#!/usr/bin/env python3
"""Detect AI writing tropes in repository prose.

Self-contained. Standard library only. No install, no third-party packages.
Runs on any Python 3.7+ interpreter.

Modes:
  audit  <path...>   Walk directories/globs, report every trope with file:line:col.
                     Exits non-zero on any finding, so it gates in CI or pre-commit.
  score  <input>     Report trope density per 1000 words for one file/text/stdin.
                     Informational: always exits 0.
  --input <input>    Lint one file/text/stdin, report matches as line:col (no path),
                     exit non-zero on any finding. This is the audit gate over one input.

Detection runs on prose with code stripped (fenced blocks and inline spans are
blanked in place so line and column numbers stay accurate). Every reported match
is measured from the text, never guessed.
"""

import argparse
import glob as globmod
import os
import re
import sys

# ---------------------------------------------------------------------------
# Porter stemmer (public-domain algorithm; compact reference port).
# Used so inflected forms collapse to one stem: "leveraging" == "leverage",
# "meticulously" == "meticulous", while "cleanly" != "clean".
# ---------------------------------------------------------------------------


class _Porter:
    def __init__(self):
        self.b = ""
        self.k = 0
        self.j = 0

    def _cons(self, i):
        ch = self.b[i]
        if ch in "aeiou":
            return False
        if ch == "y":
            return True if i == 0 else (not self._cons(i - 1))
        return True

    def _m(self):
        n = 0
        i = 0
        while True:
            if i > self.j:
                return n
            if not self._cons(i):
                break
            i += 1
        i += 1
        while True:
            while True:
                if i > self.j:
                    return n
                if self._cons(i):
                    break
                i += 1
            i += 1
            n += 1
            while True:
                if i > self.j:
                    return n
                if not self._cons(i):
                    break
                i += 1
            i += 1

    def _vowelinstem(self):
        for i in range(self.j + 1):
            if not self._cons(i):
                return True
        return False

    def _doublec(self, j):
        if j < 1:
            return False
        if self.b[j] != self.b[j - 1]:
            return False
        return self._cons(j)

    def _cvc(self, i):
        if i < 2 or not self._cons(i) or self._cons(i - 1) or not self._cons(i - 2):
            return False
        return self.b[i] not in "wxy"

    def _ends(self, s):
        length = len(s)
        if length > self.k + 1:
            return False
        if self.b[self.k - length + 1 : self.k + 1] != s:
            return False
        self.j = self.k - length
        return True

    def _setto(self, s):
        self.b = self.b[: self.j + 1] + s + self.b[self.j + len(s) + 1 :]
        self.k = self.j + len(s)

    def _r(self, s):
        if self._m() > 0:
            self._setto(s)

    def _step1ab(self):
        if self.b[self.k] == "s":
            if self._ends("sses"):
                self.k -= 2
            elif self._ends("ies"):
                self._setto("i")
            elif self.b[self.k - 1] != "s":
                self.k -= 1
        if self._ends("eed"):
            if self._m() > 0:
                self.k -= 1
        elif (self._ends("ed") or self._ends("ing")) and self._vowelinstem():
            self.k = self.j
            if self._ends("at"):
                self._setto("ate")
            elif self._ends("bl"):
                self._setto("ble")
            elif self._ends("iz"):
                self._setto("ize")
            elif self._doublec(self.k):
                if self.b[self.k] not in "lsz":
                    self.k -= 1
            elif self._m() == 1 and self._cvc(self.k):
                self._setto("e")

    def _step1c(self):
        if self._ends("y") and self._vowelinstem():
            self.b = self.b[: self.k] + "i" + self.b[self.k + 1 :]

    def _step2(self):
        if self.k <= 0:
            return
        ch = self.b[self.k - 1]
        pairs = {
            "a": [("ational", "ate"), ("tional", "tion")],
            "c": [("enci", "ence"), ("anci", "ance")],
            "e": [("izer", "ize")],
            "l": [("bli", "ble"), ("alli", "al"), ("entli", "ent"),
                  ("eli", "e"), ("ousli", "ous")],
            "o": [("ization", "ize"), ("ation", "ate"), ("ator", "ate")],
            "s": [("alism", "al"), ("iveness", "ive"), ("fulness", "ful"),
                  ("ousness", "ous")],
            "t": [("aliti", "al"), ("iviti", "ive"), ("biliti", "ble")],
            "g": [("logi", "log")],
        }
        for suf, rep in pairs.get(ch, []):
            if self._ends(suf):
                self._r(rep)
                return

    def _step3(self):
        ch = self.b[self.k]
        pairs = {
            "e": [("icate", "ic"), ("ative", ""), ("alize", "al")],
            "i": [("iciti", "ic")],
            "l": [("ical", "ic"), ("ful", "")],
            "s": [("ness", "")],
        }
        for suf, rep in pairs.get(ch, []):
            if self._ends(suf):
                self._r(rep)
                return

    def _step4(self):
        ch = self.b[self.k - 1] if self.k > 0 else ""
        suffixes = {
            "a": ["al"], "c": ["ance", "ence"], "e": ["er"], "i": ["ic"],
            "l": ["able", "ible"], "n": ["ant", "ement", "ment", "ent"],
            "o": ["ion", "ou"], "s": ["ism"], "t": ["ate", "iti"],
            "u": ["ous"], "v": ["ive"], "z": ["ize"],
        }
        for suf in suffixes.get(ch, []):
            if self._ends(suf):
                if suf == "ion":
                    if self.j >= 0 and self.b[self.j] in "st" and self._m() > 1:
                        self.k = self.j
                elif self._m() > 1:
                    self.k = self.j
                return

    def _step5(self):
        self.j = self.k
        if self.b[self.k] == "e":
            a = self._m()
            if a > 1 or (a == 1 and not self._cvc(self.k - 1)):
                self.k -= 1
        if self.b[self.k] == "l" and self._doublec(self.k) and self._m() > 1:
            self.k -= 1

    def stem(self, word):
        word = word.lower()
        if len(word) <= 2:
            return word
        self.b = word
        self.k = len(word) - 1
        self.j = self.k
        self._step1ab()
        self._step1c()
        self._step2()
        self._step3()
        self._step4()
        self._step5()
        return self.b[: self.k + 1]


_PORTER = _Porter()
_STEM_CACHE = {}


def stem(word):
    w = _STEM_CACHE.get(word)
    if w is None:
        w = _PORTER.stem(word)
        _STEM_CACHE[word] = w
    return w


# ---------------------------------------------------------------------------
# Text preparation.
# ---------------------------------------------------------------------------

WORD_TOKEN = re.compile(r"[a-zA-Z]+")
FENCED_CODE_BLOCK = re.compile(r"```[\s\S]*?```")
INLINE_CODE = re.compile(r"`[^`]+`")
PROSE_EXTENSIONS = {"md", "markdown", "txt", "mdx", "rst", "adoc"}


def strip_code(text):
    """Blank code so patterns run on prose, preserving line/column offsets."""

    def blank_fence(m):
        return "\n" * m.group(0).count("\n")

    text = FENCED_CODE_BLOCK.sub(blank_fence, text)
    text = INLINE_CODE.sub(lambda m: " " * len(m.group(0)), text)
    return text


def count_words(text):
    return len(WORD_TOKEN.findall(text))


def is_prose_file(path):
    ext = path.rsplit(".", 1)[-1].lower() if "." in os.path.basename(path) else ""
    return ext in PROSE_EXTENSIONS


def position_at(text, index):
    line = 1
    last_newline = -1
    for i in range(min(index, len(text))):
        if text[i] == "\n":
            line += 1
            last_newline = i
    return line, index - last_newline


def position_of_sample(text, sample):
    lower = text.lower()
    candidates = [sample, sample.split(" / ")[0] if sample else ""]
    for cand in candidates:
        if not cand:
            continue
        idx = lower.find(cand.lower())
        if idx >= 0:
            return position_at(text, idx)
    return 1, 1


# ---------------------------------------------------------------------------
# Sentence / paragraph splitting.
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT = re.compile(r"(?<!\d)[.!?]+(?=\s|$)|\n+")
_HEADING = re.compile(r"^#{1,6}\s")
_TABLE_ROW = re.compile(r"^\|")


def split_sentences(text):
    out = []
    for piece in _SENTENCE_SPLIT.split(text):
        s = piece.strip()
        if not s or _TABLE_ROW.match(s) or _HEADING.match(s):
            continue
        out.append(s)
    return out


def split_paragraphs(text):
    paras = []
    for block in re.split(r"\n{2,}", text):
        sents = split_sentences(block)
        if sents:
            paras.append(sents)
    return paras


# ---------------------------------------------------------------------------
# Wordlist loading and matching.
# ---------------------------------------------------------------------------

_WORDLIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "wordlists")


def _read_lines(path):
    try:
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        return []
    lines = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines


def _compile_stem_set(lines):
    stems = set()
    for entry in lines:
        for word in WORD_TOKEN.findall(entry.lower()):
            stems.add(stem(word))
    return stems


def _compile_weighted(lines):
    entries = []
    for line in lines:
        m = re.match(r"^(\S+)\s+([0-9]+(?:\.[0-9]+)?)$", line)
        if not m:
            continue
        weight = float(m.group(2))
        if weight <= 0:
            continue
        entries.append((stem(m.group(1).lower()), weight, m.group(1)))
    return entries


def _compile_phrases(lines):
    phrases = []
    for line in lines:
        toks = [stem(w) for w in WORD_TOKEN.findall(line.lower())]
        if toks:
            phrases.append((toks, line))
    return phrases


def stem_set_hits(text, stems):
    count = 0
    sample = ""
    for word in WORD_TOKEN.findall(text):
        if stem(word.lower()) in stems:
            count += 1
            if not sample:
                sample = word
    return count, sample


def phrase_hits(text, phrases):
    tokens = [stem(w) for w in WORD_TOKEN.findall(text.lower())]
    count = 0
    sample = ""
    for stems, original in phrases:
        occ = _count_subsequence(tokens, stems)
        if occ:
            count += occ
            if not sample:
                sample = original
    return count, sample


def _count_subsequence(haystack, needle):
    if not needle:
        return 0
    count = 0
    i = 0
    while i + len(needle) <= len(haystack):
        if haystack[i : i + len(needle)] == needle:
            count += 1
            i += len(needle)
        else:
            i += 1
    return count


def weighted_hits(text, entries):
    counts = {}
    for word in WORD_TOKEN.findall(text):
        s = stem(word.lower())
        counts[s] = counts.get(s, 0) + 1
    total = 0.0
    samples = []
    for entry_stem, weight, original in entries:
        c = counts.get(entry_stem, 0)
        if c:
            total += c * weight
            if len(samples) < 3:
                samples.append(original)
    return total, samples


VOCABULARY = _compile_stem_set(_read_lines(os.path.join(_WORDLIST_DIR, "vocabulary.txt")))
FLOWERY = _compile_phrases(_read_lines(os.path.join(_WORDLIST_DIR, "flowery-phrases.txt")))
MARKETING = _compile_weighted(_read_lines(os.path.join(_WORDLIST_DIR, "marketing-verbs.txt")))
SOFT = _compile_weighted(_read_lines(os.path.join(_WORDLIST_DIR, "soft-phrasing.txt")))


# ---------------------------------------------------------------------------
# Function-based detectors (cross-sentence and context-sensitive).
# ---------------------------------------------------------------------------

_DETERMINER = re.compile(r"^(?:the|a|an|it|them|this|that|its)\b", re.I)
_NO_X = re.compile(r"\bno\s+((?:\w+\s+){0,3}?)(\w+)\s+(?:needed|required|necessary)\b", re.I)
_DEVERBAL = re.compile(r"(?:tion|sion|ment)s?$", re.I)
_NO_X_FUNCTION = {"longer", "more", "further", "additional", "extra", "fewer", "less", "other"}
_NO_X_ACTION = {
    "change", "changes", "fix", "fixes", "edit", "edits", "work", "move", "moves",
    "update", "updates", "override", "overrides", "touch", "tweak", "tweaks", "patch",
    "patches", "bump", "bumps", "swap", "swaps", "merge", "merges", "sync", "run",
    "runs", "check", "checks", "review", "reviews", "test", "tests", "cleanup", "dedup",
    "retry", "retries", "rebuild", "rebase", "restart", "reload", "rerun", "refactor",
}


def _is_status_head(head):
    w = head.lower()
    return w in _NO_X_FUNCTION or w in _NO_X_ACTION or bool(_DEVERBAL.search(w))


def no_x_needed(text):
    for m in _NO_X.finditer(text):
        gap = m.group(1) or ""
        head = m.group(2) or ""
        if any(_DETERMINER.match(tok) for tok in gap.split()):
            continue
        if _is_status_head(head):
            continue
        return 1, m.group(0).strip()
    return 0, ""


_RESULT_SENTENCES = [
    re.compile(r"\b(?:all\s+)?\d+(?:/\d+)?\s+(?:\w+\s+)*(?:pass|fail|succeed)", re.I),
    re.compile(r"\b(?:all|every|both)\s+(?:\w+\s+)*(?:pass(?:es|ed|ing)?|green)", re.I),
    re.compile(r"\b(?:0|zero)\s+(?:errors?|failures?|warnings?)\b", re.I),
    re.compile(r"\b\S+\s+(?:(?:is|are)\s+)?(?:now\s+)?(?:green|clean)\b", re.I),
    re.compile(r"\bonce\s+\S+\s+pass", re.I),
    re.compile(r"^(?:\w+\s+){0,3}pass(?:es|ed|ing)?(?:\s|$)", re.I | re.M),
]


def test_result(text):
    for sentence in re.split(r"[.!?\n]+", text):
        s = sentence.strip()
        for pat in _RESULT_SENTENCES:
            m = pat.search(s)
            if not m:
                continue
            after = s[m.end():].strip()
            if _DETERMINER.match(after):
                continue
            return 1, m.group(0)
    return 0, ""


_LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s")
_CLAUSE_CONNECTOR = re.compile(r";|—|[A-Za-z] [-–] [A-Za-z]")
_SEMICOLON_SPLICE = re.compile(r"[a-z]; [a-z]", re.I)


def _is_connector_sentence(sentence):
    if _LIST_ITEM.match(sentence):
        return ";" in sentence
    return bool(_CLAUSE_CONNECTOR.search(sentence))


def connector_density(text):
    sentences = [s for s in split_sentences(text) if len(s.split()) >= 4]
    if len(sentences) < 5:
        return 0, ""
    connected = [s for s in sentences if _is_connector_sentence(s)]
    if len(connected) < 3 or len(connected) / len(sentences) < 0.3:
        return 0, ""
    first = connected[0]
    m = _CLAUSE_CONNECTOR.search(first)
    i = m.start() if m else 0
    return len(connected), first[max(0, i - 20):i + 24].strip()


def semicolon_splice(text, minimum=2):
    spliced = [s for s in split_sentences(text)
               if not _LIST_ITEM.match(s) and _SEMICOLON_SPLICE.search(s)]
    if len(spliced) < minimum:
        return 0, ""
    first = spliced[0]
    m = _SEMICOLON_SPLICE.search(first)
    i = m.start() if m else 0
    return len(spliced), first[max(0, i - 20):i + 24].strip()


_NEGATION_CUE = re.compile(r"\b(?:not|never)\b|\bno\s|n't\b", re.I)
_ADVERSATIVE = re.compile(r"^\s*(?:However|But|Yet|Nevertheless|Nonetheless|Still|That said),?\s", re.I)


def adversative_negation_flip(text):
    sentences = split_sentences(text)
    for i in range(len(sentences) - 1):
        if _NEGATION_CUE.search(sentences[i]) and _ADVERSATIVE.match(sentences[i + 1]):
            return 1, "%s / %s" % (sentences[i][:60], sentences[i + 1][:40])
    return 0, ""


def burstiness(text):
    sentences = [s for s in split_sentences(text) if len(s.split()) >= 2]
    if len(sentences) < 8:
        return 0, ""
    counts = [len([w for w in s.split() if w]) for s in sentences]
    mean = sum(counts) / len(counts)
    if mean == 0:
        return 0, ""
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    cv = (variance ** 0.5) / mean
    if cv >= 0.55:
        return 0, ""
    return 1, "CV=%.2f over %d sentences" % (cv, len(sentences))


_QUESTION_OPENER = re.compile(
    r"^\s*(?:What|Why|How|When|Where|Who|Which|Is|Are|Does|Do|Can|Should|Could|Would|Will)\b", re.I
)


def question_answer_cadence(text):
    paras = split_paragraphs(text)
    if len(paras) < 4:
        return 0, ""
    openers = [p[0][:60] for p in paras if p and _QUESTION_OPENER.match(p[0])]
    if len(openers) < 2:
        return 0, ""
    return len(openers), openers[0]


_DISCOURSE_TIER1 = [re.compile(p, re.I) for p in [
    r"\bhowever\b", r"\bnevertheless\b", r"\bnonetheless\b", r"\bnotwithstanding\b",
    r"\bconversely\b", r"\bin contrast\b", r"\bon the other hand\b", r"\bthat said\b",
    r"\bby contrast\b",
]]
_DISCOURSE_TIER2 = [re.compile(p, re.I) for p in [
    r"^(?:also|moreover|furthermore|in addition|additionally),?\s",
    r"^(?:therefore|thus|hence|consequently|as a result),?\s",
    r"^(?:similarly|likewise),?\s",
    r"^(?:specifically|for example|for instance|in particular),?\s",
    r"^(?:finally|first|second|third|lastly),?\s",
]]


def _has_discourse_marker(sentence):
    if any(p.search(sentence) for p in _DISCOURSE_TIER1):
        return True
    return any(p.match(sentence) for p in _DISCOURSE_TIER2)


def discourse_marker_density(text):
    sentences = [s for s in split_sentences(text) if len(s.split()) >= 3]
    if len(sentences) < 5:
        return 0, ""
    marked = [s for s in sentences if _has_discourse_marker(s)]
    if len(marked) / len(sentences) < 0.2:
        return 0, ""
    return len(marked), marked[0][:60]


_RULE_OF_THREE = re.compile(
    r"\b(\w+(?:\s\w+){0,2}), (\w+(?:\s\w+){0,2}), (?:and|or) (\w+(?:\s\w+){0,2})\b", re.I
)


def rule_of_three(text):
    """Lexical proxy for the tricolon (escalating triad). Flags a three-item
    comma list "X, Y, and Z". Lexical only: no part-of-speech tagger, so it
    catches the common list shape rather than deep parallelism."""
    m = _RULE_OF_THREE.search(text)
    if not m:
        return 0, ""
    return 1, m.group(0)


# ---------------------------------------------------------------------------
# Pattern registry.
#   kind: "regex" (re object), "func" (callable -> (count, sample)),
#         "vocab" (stem set), "phrase" (phrase list), "weighted" (entries+threshold)
#   prose_only: pattern applies only to prose (skipped for non-prose source files)
# ---------------------------------------------------------------------------

PATTERNS = [
    dict(cat="spaced em dash", kind="regex", prose_only=False,
         test=re.compile(r" — "),
         msg=lambda m: "Spaced em dash is an AI tell. Split the clauses into two sentences. "
                       "Do not swap in a semicolon or unspaced dash: the run-on is the problem."),
    dict(cat="AI vocabulary", kind="vocab", prose_only=False, test=VOCABULARY,
         msg=lambda m: '"%s" is AI-typical vocabulary. Use a plainer word.' % m),
    dict(cat="copula avoidance", kind="regex", prose_only=False,
         test=re.compile(r"\b(?:serves|stands) as\b", re.I),
         msg=lambda m: '"%s" avoids a simple copula. Use "is" or "are".' % m),
    dict(cat="reaching for", kind="regex", prose_only=False,
         test=re.compile(r"\breach(?:ing|es|ed)?\s+for\b", re.I),
         msg=lambda m: '"%s" is figurative filler. Say "use" or "prefer X over Y".' % m),
    dict(cat="promotional language", kind="regex", prose_only=False,
         test=re.compile(r"\b(boasts|vibrant|showcasing|nestled|groundbreaking|renowned|diverse array)\b", re.I),
         msg=lambda m: '"%s" reads as promotional. Use a neutral word.' % m),
    dict(cat="no X needed brag", kind="func", prose_only=False, test=no_x_needed,
         msg=lambda m: '"%s" advertises what the design avoids. Say what it does.' % m),
    dict(cat="test result reporting", kind="func", prose_only=False, test=test_result,
         msg=lambda m: 'Do not report test counts or CI status ("%s"). Describe what is covered.' % m),
    dict(cat="parallelism", kind="regex", prose_only=False,
         test=re.compile(r"\bnot (?:just|only) .{1,50}, but (?:also )?", re.I),
         msg=lambda m: '"Not just X, but also Y" is an AI parallelism. Simplify the sentence.'),
    dict(cat="contrast not", kind="regex", prose_only=False,
         test=re.compile(r"\b\w[\w\s]{2,40},\s+not\s+\w[\w\s]{2,30}(?=[.!?,\n]|$)", re.I),
         msg=lambda m: '"%s" is a rhetorical "X, not Y" contrast. State the positive directly.' % m),
    dict(cat="dig into", kind="regex", prose_only=False,
         test=re.compile(r"\b(?:dig|digs|digging|dug|dive|dives|diving|dove|dived|wade|wades|wading|waded)\s+into\b", re.I),
         msg=lambda m: '"%s" is exploration filler. Say what you are looking at.' % m),
    dict(cat="hedging observation", kind="regex", prose_only=False,
         test=re.compile(r"\b(?:looks|appears|seems)\s+(?:like|to)\b", re.I),
         msg=lambda m: '"%s" hedges. State the observation or name the uncertainty.' % m),
    dict(cat="filler", kind="regex", prose_only=False,
         test=re.compile(r"\b(?:it's worth noting that|importantly|interestingly|it should be noted|as mentioned|in terms of)\b", re.I),
         msg=lambda m: '"%s" is filler. Cut it.' % m),
    dict(cat="tests cover preamble", kind="regex", prose_only=False,
         test=re.compile(r"^Tests\s+(?:cover|verify|ensure|validate)\b", re.M),
         msg=lambda m: '"Tests cover ..." elides the subject. Use "Added tests covering ...".'),
    dict(cat="rides on", kind="regex", prose_only=False,
         test=re.compile(r"\brid(?:e|es|ing)\s+(?:on|atop|alongside)\b", re.I),
         msg=lambda m: '"%s" is figurative dependency language. Say "depends on" or "reuses".' % m),
    dict(cat="can bite", kind="regex", prose_only=False,
         test=re.compile(r"\b(?:can|could|will|may|might)\s+bite\b", re.I),
         msg=lambda m: '"%s" is figurative risk language. Name the failure and its condition.' % m),
    dict(cat="surface as verb", kind="regex", prose_only=False,
         test=re.compile(r"\bsurfac(?:e|es|ed|ing)\s+(?:the|a|an|that|this|these|those|any|all|each|its|their|every)\b", re.I),
         msg=lambda m: '"%s" uses "surface" as a verb. Say "show", "report", or "expose".' % m),
    dict(cat="rule of three", kind="func", prose_only=False, test=rule_of_three,
         msg=lambda m: '"%s" is a three-item triad. Vary the structure or cut an item.' % m),
    # Prose-only (skipped for non-prose source files).
    dict(cat="connector density", kind="func", prose_only=True, test=connector_density,
         msg=lambda m: 'Many sentences fuse clauses with semicolons or dashes (e.g. "%s"). '
                       'This is run-on structure. Split each into two sentences.' % m),
    dict(cat="semicolon splice", kind="func", prose_only=True,
         test=lambda t: semicolon_splice(t, 2),
         msg=lambda m: 'Semicolons join independent clauses (e.g. "%s"). Split into two sentences.' % m),
    dict(cat="flowery phrasing", kind="phrase", prose_only=True, test=FLOWERY,
         msg=lambda m: '"%s" is stock phrasing. State the mechanism plainly.' % m),
    dict(cat="passive PR summary", kind="regex", prose_only=True,
         test=re.compile(r"\b(?:is|was|are|were)\s+(?:added|updated|removed|refactored|introduced|created|deleted|modified|improved)\b", re.I),
         msg=lambda m: '"%s" is passive voice. Rewrite so something does the verb.' % m),
    dict(cat="path bullet", kind="regex", prose_only=True,
         test=re.compile(r"^\s*-\s*\*\*[^*\n]+\*\*\s*:\s*", re.M),
         msg=lambda m: '"- **path**: ..." bullets read as file manifests. Describe the change in prose.'),
    dict(cat="trailing hedge", kind="regex", prose_only=True,
         test=re.compile(r"\b(?:regardless|nonetheless|anyway)\.\s*(?:$|\n)", re.I | re.M),
         msg=lambda m: '"%s" dangles as a hedge. Drop it or rewrite the clause.' % m.strip()),
    dict(cat="label bold", kind="regex", prose_only=True,
         test=re.compile(r"^\s*\*\*[A-Z][A-Za-z ]+(?::\*\*|\*\*:)\s", re.M),
         msg=lambda m: '"**Label:**" reads as templated. Use a #### header instead.'),
    dict(cat="consequence chain", kind="regex", prose_only=True,
         test=re.compile(r",\s*so\s+(?:the|it|they|this|that|a)\b", re.I),
         msg=lambda m: '"%s" chains clauses with ", so". State cause and effect separately.' % m),
    dict(cat="adversative negation-flip", kind="func", prose_only=True, test=adversative_negation_flip,
         msg=lambda m: 'Negation then concession: "%s". Merge into one sentence or drop the negation.' % m),
    dict(cat="sentence burstiness", kind="func", prose_only=True, test=burstiness,
         msg=lambda m: 'Low sentence-length variation (%s). Vary sentence rhythm.' % m),
    dict(cat="question-answer cadence", kind="func", prose_only=True, test=question_answer_cadence,
         msg=lambda m: 'Repeated question-opener paragraphs (e.g. "%s"). State the point directly.' % m),
    dict(cat="discourse-marker density", kind="func", prose_only=True, test=discourse_marker_density,
         msg=lambda m: 'High discourse-marker density (e.g. "%s"). Cut markers that carry no meaning.' % m),
]

WEIGHTED_PATTERNS = [
    dict(cat="marketing verbs", entries=MARKETING, threshold=3.0, prose_only=False,
         msg=lambda ex: "Marketing verbs stack up (%s). Describe concretely what changed." % ", ".join(ex)),
    dict(cat="soft phrasing", entries=SOFT, threshold=3.0, prose_only=True,
         msg=lambda ex: "Soft phrasing piles up (%s). Describe what the code does plainly." % ", ".join(ex)),
]


# ---------------------------------------------------------------------------
# Scanning.
# ---------------------------------------------------------------------------


def _regex_results(stripped, pat):
    results = []
    for m in pat["test"].finditer(stripped):
        line, col = position_at(stripped, m.start())
        results.append((line, col, pat["cat"], pat["msg"](m.group(0))))
    return results


def _sample_result(stripped, pat, count, sample):
    if count == 0:
        return []
    line, col = position_of_sample(stripped, sample)
    return [(line, col, pat["cat"], pat["msg"](sample))]


def scan_all(text, file_path=None):
    stripped = strip_code(text)
    prose = file_path is None or is_prose_file(file_path)
    results = []
    for pat in PATTERNS:
        if pat["prose_only"] and not prose:
            continue
        kind = pat["kind"]
        if kind == "regex":
            results.extend(_regex_results(stripped, pat))
        elif kind == "func":
            count, sample = pat["test"](stripped)
            results.extend(_sample_result(stripped, pat, count, sample))
        elif kind == "vocab":
            count, sample = stem_set_hits(stripped, pat["test"])
            # vocab reports every occurrence at its own position
            if count:
                for m in re.finditer(r"[a-zA-Z]+", stripped):
                    if stem(m.group(0).lower()) in pat["test"]:
                        line, col = position_at(stripped, m.start())
                        results.append((line, col, pat["cat"], pat["msg"](m.group(0))))
        elif kind == "phrase":
            count, sample = phrase_hits(stripped, pat["test"])
            results.extend(_sample_result(stripped, pat, count, sample))
    for group in WEIGHTED_PATTERNS:
        if group["prose_only"] and not prose:
            continue
        total, samples = weighted_hits(stripped, group["entries"])
        if total < group["threshold"]:
            continue
        line, col = position_of_sample(stripped, samples[0] if samples else "")
        results.append((line, col, group["cat"], group["msg"](samples)))
    results.sort(key=lambda r: (r[0], r[1]))
    return results


# ---------------------------------------------------------------------------
# Scoring.
# ---------------------------------------------------------------------------

_SINGLE_COMMENT = re.compile(r"(?:^|\s)(?://|#)[^\n]*", re.M)
_BLOCK_COMMENT = re.compile(r"/\*[\s\S]*?\*/")
_HTML_COMMENT = re.compile(r"<!--[\s\S]*?-->")
_TRIPLE_QUOTED = re.compile(r"(\"\"\"|''')[\s\S]*?\1")


def extract_comments(text):
    parts = []
    for m in _SINGLE_COMMENT.finditer(text):
        parts.append(re.sub(r"^\s*(?://|#)\s?", "", m.group(0)))
    for m in _BLOCK_COMMENT.finditer(text):
        body = re.sub(r"^/\*+", "", m.group(0))
        body = re.sub(r"\*+/$", "", body)
        body = "\n".join(re.sub(r"^\s*\*\s?", "", ln).strip() for ln in body.split("\n"))
        parts.append(body.strip())
    for m in _HTML_COMMENT.finditer(text):
        parts.append(m.group(0)[4:-3].strip())
    for m in _TRIPLE_QUOTED.finditer(text):
        parts.append(m.group(0)[3:-3].strip())
    return "\n".join(p for p in parts if p)


def score_group(text, file_path, custom_stems, group_name):
    stripped = strip_code(text)
    word_count = count_words(stripped)
    counts = {}
    for line, col, cat, msg in scan_all(text, file_path):
        counts[cat] = counts.get(cat, 0) + 1
    if custom_stems:
        c, _ = stem_set_hits(stripped, custom_stems)
        counts["custom vocabulary"] = c
    cats = []
    for cat, hits in counts.items():
        density = 0.0 if word_count == 0 else hits / (word_count / 1000.0)
        cats.append((cat, hits, density))
    cats.sort(key=lambda x: (-x[2], x[0]))
    return group_name, word_count, cats


def build_report(text, file_path, do_comments, custom_stems):
    groups = [score_group(text, file_path, custom_stems, "prose")]
    if do_comments:
        comments = extract_comments(text)
        if comments.strip():
            groups.append(score_group(comments, None, custom_stems, "comments"))
    return groups


# ---------------------------------------------------------------------------
# Plain-text table rendering (no third-party deps).
# ---------------------------------------------------------------------------


def render_table(rows, headers):
    all_rows = [headers] + rows
    widths = [max(len(str(r[i])) for r in all_rows) for i in range(len(headers))]
    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    out = [line]
    for idx, row in enumerate([headers] + rows):
        cells = " | ".join(str(row[i]).ljust(widths[i]) for i in range(len(headers)))
        out.append("| " + cells + " |")
        if idx == 0:
            out.append(line)
    out.append(line)
    return "\n".join(out)


def render_report(groups):
    sections = []
    for name, word_count, cats in groups:
        header = "%s (%d words)" % (name, word_count)
        if not cats:
            sections.append(header + "\nNo patterns detected.")
            continue
        rows = [[cat, str(hits), "%.1f" % density] for cat, hits, density in cats]
        sections.append(header + "\n" + render_table(rows, ["Category", "Hits", "Density /1k"]))
    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# File collection for audit.
# ---------------------------------------------------------------------------

_SKIP_SEGMENTS = {"node_modules", ".git"}
_WORDLIST_PATH = re.compile(r"(?:^|/)wordlists/[^/]+\.txt$")


def should_skip(path):
    parts = path.split(os.sep)
    if any(seg in _SKIP_SEGMENTS for seg in parts):
        return True
    if _WORDLIST_PATH.search(path.replace(os.sep, "/")):
        return True
    return False


def collect_files(target):
    files = []
    if os.path.isdir(target):
        for root, dirs, names in os.walk(target):
            dirs[:] = [d for d in dirs if d not in _SKIP_SEGMENTS]
            for name in names:
                path = os.path.join(root, name)
                if not should_skip(path) and is_prose_file(path):
                    files.append(path)
    else:
        for path in globmod.glob(target, recursive=True):
            if os.path.isfile(path) and not should_skip(path) and is_prose_file(path):
                files.append(path)
    return sorted(set(files))


def _relative(path):
    try:
        rel = os.path.relpath(path, ".")
    except ValueError:
        return path
    return path if rel.startswith("..") else rel


# ---------------------------------------------------------------------------
# I/O.
# ---------------------------------------------------------------------------


def read_input(arg):
    if arg and os.path.isfile(arg):
        with open(arg, encoding="utf-8") as fh:
            return fh.read(), arg
    if arg:
        return arg, None
    return sys.stdin.read(), None


def load_custom(path):
    if not path:
        return None
    return _compile_stem_set(_read_lines(path))


# ---------------------------------------------------------------------------
# Commands.
# ---------------------------------------------------------------------------


def legacy_audit(args):
    files = []
    seen = set()
    for target in args.path:
        for f in collect_files(target):
            if f not in seen:
                seen.add(f)
                files.append(f)
    files.sort()

    by_cat = {}
    by_file = {}
    total = 0
    found_any = False
    for path in files:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        results = scan_all(text, path)
        if not results:
            continue
        found_any = True
        by_file[path] = len(results)
        for line, col, cat, msg in results:
            total += 1
            by_cat[cat] = by_cat.get(cat, 0) + 1
            print("%s:%d:%d: %s: %s" % (_relative(path), line, col, cat, msg))

    if found_any and not args.no_summary:
        cat_rows = sorted(by_cat.items(), key=lambda x: -x[1])
        sys.stderr.write(render_table([[c, str(n)] for c, n in cat_rows], ["Category", "Count"]) + "\n")
        noisy = sorted(by_file.items(), key=lambda x: -x[1])[:10]
        sys.stderr.write(render_table([[_relative(p), str(n)] for p, n in noisy], ["File", "Violations"]) + "\n")
        sys.stderr.write("%d violations across %d files.\n" % (total, len(by_file)))

    return 1 if found_any else 0


def cmd_audit(args):
    from pathlib import Path
    import glob
    from writing_check import main as writing_main
    files = set()
    for target in args.path:
        matches = glob.glob(target, recursive=True)
        if not matches:
            print('No input matched: ' + target, file=sys.stderr)
            return 2
        for match in matches:
            path = Path(match)
            if path.is_dir():
                for parent, dirs, names in os.walk(path):
                    dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '__pycache__'}]
                    files.update(str(Path(parent) / name) for name in names)
            else:
                files.add(str(path))
    if not files:
        print('No files to check', file=sys.stderr)
        return 2
    # Keep the older lexical diagnostics as well as the universal gate.
    old_result = legacy_audit(args)
    strict_result = writing_main(sorted(files))
    return max(old_result, strict_result)


def cmd_score(args):
    text, file_path = read_input(args.input)
    custom = load_custom(args.wordlist)
    if args.no_comments:
        do_comments = False
    elif args.comments:
        do_comments = True
    else:
        do_comments = file_path is not None and not is_prose_file(file_path)
    groups = build_report(text, file_path, do_comments, custom)
    if args.json:
        import json
        payload = {"filePath": file_path, "groups": [
            {"group": g, "wordCount": wc,
             "categories": [{"category": c, "hits": h, "density": d} for c, h, d in cats]}
            for g, wc, cats in groups]}
        print(json.dumps(payload, indent=2))
    else:
        print(render_report(groups))
    return 0


def cmd_input(arg):
    from writing_check import main as writing_main
    import tempfile
    from pathlib import Path
    if arg and arg != '-':
        return writing_main([arg])
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'stdin.txt'
        path.write_text(sys.stdin.read())
        return writing_main([str(path)])


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    # Top-level --input single-input gate (used by rewrite-style callers).
    if argv and argv[0] == "--input":
        rest = argv[1:]
        return cmd_input(rest[0] if rest else None)

    parser = argparse.ArgumentParser(
        prog="scan", description="Detect AI writing tropes in repository prose.")
    sub = parser.add_subparsers(dest="command")

    p_audit = sub.add_parser("audit", help="Walk paths/globs and gate on tropes (exit non-zero on findings).")
    p_audit.add_argument("path", nargs="*")
    p_audit.add_argument("--no-summary", action="store_true", help="Suppress the trailing summary tables.")

    p_score = sub.add_parser("score", help="Score one input for trope density per 1000 words (exit 0).")
    p_score.add_argument("input", nargs="?")
    p_score.add_argument("--json", action="store_true", help="Emit JSON for comparing two runs.")
    p_score.add_argument("--comments", action="store_true", help="Force comment extraction on.")
    p_score.add_argument("--no-comments", action="store_true", help="Force comment extraction off.")
    p_score.add_argument("--wordlist", help="Score an extra stemmed vocabulary file as 'custom vocabulary'.")

    args = parser.parse_args(argv)
    if args.command == "audit":
        if not args.path:
            p_audit.print_help()
            return 1
        return cmd_audit(args)
    if args.command == "score":
        return cmd_score(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
