#!/usr/bin/env python3
"""Check every in-scope line of one file against the writing rules folder.

    check.py --file PATH [--register NAME] --json

Exit 0: pass. Exit 1: findings that block. Exit 2: the check could not
complete. A file that cannot be parsed, a rule that cannot run and a part that
fails after its retries all return 2 and name the lines not reviewed.

JSON on stdout:

    {"status": "pass|fail|incomplete",
     "coverage": {"lines_total": N, "lines_reviewed": N},
     "findings": [{"line": N, "rule": "id", "text": "...", "fix": "..."}],
     "receipt": "path"}

In scope: every word a person will read. Exempt: code, quotations kept word for
word, front matter and lines with no words. The file is extracted to numbered
lines, split into parts of at most 300 lines and scanned with the pattern
ledger in the rules folder. Each part returns the IDs and a digest of the lines
it scanned; the run compares them with the extraction and returns incomplete on
any gap.

Other options:

    --rules-dir DIR       rules folder (otherwise $WRITING_HOME, then the path
                          in ~/.agents/writing/home)
    --receipt-dir DIR     where receipts are written
    --prepare DIR         write the text parts, outline and worker assignments
                          for the line pass and document pass
    --verdicts FILE       line-pass verdicts to validate
    --document-map FILE   document-pass map to validate
    --audit FILE          spot-audit verdicts to validate
    --sources FILE        the source list for the claims check (JSON list of names)
    --full                require the line pass and the document pass
    --verify-receipt FILE recheck a saved receipt against the current file

Standard library only.
"""
import argparse
import bisect
import datetime as dt
import hashlib
import json
import os
import random
import re
import signal
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_review_text as ext  # noqa: E402

VERSION = 1
PART_LINES = 300            # largest part any reader or scan receives
WORKER_LINES = 40           # lines per line-pass worker
LONG_DOCUMENT_LINES = 2000  # above this the document pass works in two steps
AUDIT_SHARE = 5             # the spot audit re-reviews one line in five
CHUNK_SECONDS = 30
MAX_BYTES = 50 * 1024 * 1024
PLAIN_SUFFIXES = {'.md', '.markdown', '.mdx', '.txt', '.text', '.rst', ''}
GIT_MESSAGES = {'COMMIT_EDITMSG', 'MERGE_MSG', 'TAG_EDITMSG', 'SQUASH_MSG'}
TRAILER = re.compile(r'^(?:co-authored-by|signed-off-by|reviewed-by|acked-by|claude-session|change-id)\s*:', re.I)
WORD = re.compile(r"[A-Za-z0-9][\w'’-]*")
HEADING = re.compile(r'^(?:> )?#{1,6} ')
SINGLE_LINE_FAULTS = ('heading does not match its content', 'recap of another section',
                      'line exists only because of an earlier mistake', 'provenance in finished copy',
                      'reader would not act on this section')
TITLE_SECTION_LINES = 3     # a title section is a heading and at most two lines under it
MAP_KEYS = ('reader', 'sections', 'headings', 'repeated_facts', 'counts', 'recaps', 'terms',
            'leftover_lines', 'numbers', 'confidentiality', 'provenance')


class Incomplete(Exception):
    """The check cannot finish; the run reports incomplete and never pass."""


def sha(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# ---------------------------------------------------------------------------
# Rules folder and ledger
# ---------------------------------------------------------------------------

def rules_home(arg):
    if arg:
        return Path(arg).expanduser(), '--rules-dir'
    if os.environ.get('WRITING_HOME'):
        return Path(os.environ['WRITING_HOME']).expanduser(), 'WRITING_HOME'
    pointer = Path(os.environ.get('WRITING_POINTER') or Path.home() / '.agents' / 'writing' / 'home')
    if pointer.is_file():
        value = pointer.read_text(encoding='utf-8').strip()
        if value:
            return Path(value).expanduser(), str(pointer)
    return None, None


def load_rules(arg):
    home, how = rules_home(arg)
    info = {'home': str(home) if home else None, 'resolved_by': how, 'rules_md_sha256': None}
    candidates = []
    if home:
        candidates.append((home / 'patterns.json', 'rules folder'))
        rules_md = home / 'rules.md'
        if rules_md.is_file():
            info['rules_md_sha256'] = sha(rules_md.read_bytes())
    legacy = Path(os.environ.get('HUMANIZE_HOME') or Path.home() / '.agents' / 'humanize') / 'patterns.json'
    if not arg:
        candidates.append((legacy, 'scanner ledger outside the rules folder'))
    for path, source in candidates:
        if path.is_file():
            try:
                raw = path.read_bytes()
                ledger = json.loads(raw.decode('utf-8'))
                ledger['rules'], ledger.setdefault('config', {})
            except (OSError, ValueError, KeyError, TypeError) as error:
                raise Incomplete(f'pattern ledger {path} cannot be read: {error}')
            info.update(ledger=str(path), ledger_source=source, ledger_sha256=sha(raw))
            info['rules_sha256'] = sha(info['ledger_sha256'] + (info['rules_md_sha256'] or ''))
            return ledger, info
    raise Incomplete('no pattern ledger found; pass --rules-dir, set WRITING_HOME or write the rules '
                     'folder path to ~/.agents/writing/home')


def valid_registers(home, ledger):
    """Names --register accepts: entries in registers.md, ledger scopes and the built-in commit."""
    names = {'commit'}
    for rule in ledger['rules']:
        if rule.get('scope', 'general') != 'general':
            names.add(rule['scope'])
        names.update(rule.get('registers') or [])
    listing = Path(home) / 'registers.md' if home else None
    if listing and listing.is_file():
        names.update(m.strip() for m in re.findall(r'^### +(.+?)\s*$', listing.read_text(encoding='utf-8'), re.M))
    return sorted(names)


def note_registers(registers, home, ledger, source):
    """Registers are not a fixed list. A name the check has not seen is accepted and recorded in registers.md.

    Returns the names that were new, each with a note on whether the record was written.
    """
    known = valid_registers(home, ledger)
    new = {}
    for name in registers:
        if name in known or name in new:
            continue
        if not home or re.search(r'[\n#`]', name):
            new[name] = 'not recorded'
            continue
        listing = Path(home) / 'registers.md'
        entry = (f'\n### {name}\n\nFirst seen {dt.date.today().isoformat()} by the check, on `{source}`. '
                 'No rules yet. Add what she teaches about this register here.\n')
        try:
            text = listing.read_text(encoding='utf-8') if listing.is_file() else '# Registers\n'
            heading = '## Names first seen by the check'
            if heading not in text:
                text = text.rstrip('\n') + f'\n\n{heading}\n'
            listing.write_text(text.rstrip('\n') + '\n' + entry, encoding='utf-8')
            new[name] = 'recorded in registers.md'
        except OSError as error:
            new[name] = f'not recorded: {error}'
    return new, known


def compile_rule(rule):
    flags = re.MULTILINE | (0 if rule.get('cs') else re.IGNORECASE)
    if 'terms' in rule:
        alts = '|'.join(sorted((re.escape(t).replace(r'\ ', r'\s+') for t in rule['terms']), key=len, reverse=True))
        suffix = r'(?:s|es|d|ed|ing|ly)?' if rule.get('inflect') else ''
        return re.compile(r'(?<![\w-])(?:' + alts + ')' + suffix + r'(?![\w-])', flags)
    return re.compile(rule['pattern'], flags)


def active_rules(ledger, registers):
    """Rules that apply to this run, compiled. A rule that cannot compile stops the run."""
    cfg = ledger['config']
    scopes = {'general'} | set(registers)
    out = []
    for rule in ledger['rules']:
        if rule.get('status') not in ('active', 'candidate'):
            continue
        named = set(rule.get('registers') or [])
        if rule.get('scope', 'general') not in scopes and not (named & scopes):
            continue
        if rule.get('id') == 'em-dash' and not cfg.get('em_dash', False) and not (named & scopes):
            continue
        try:
            out.append((rule, compile_rule(rule)))
        except (re.error, KeyError, TypeError) as error:
            raise Incomplete(f'rule {rule.get("id")} cannot run: {error}')
    return out


# ---------------------------------------------------------------------------
# Extraction and scope
# ---------------------------------------------------------------------------

def blank(match):
    return ' ' * len(match.group(0))


def mask(text):
    """Blank the exempt spans of one line: inline code, link targets, addresses and quotations."""
    text = re.sub(r'`[^`\n]+`', blank, text)
    text = re.sub(r'\]\([^)\s]+\)', lambda m: ']' + ' ' * (len(m.group(0)) - 1), text)
    text = re.sub(r'https?://\S+', blank, text)
    return re.sub(r'"[^"\n]{1,240}"|“[^”\n]{1,240}”', blank, text)


YAML_LINE = re.compile(r'^(?:\s*#.*|[A-Za-z_][\w.-]*:(?:\s.*)?|\s+\S.*|-\s.*|)$')


def front_matter(lines):
    """True when the file opens with a YAML block: every line before the closing marker is YAML-shaped."""
    if not lines or lines[0].strip() != '---':
        return False
    for line in lines[1:]:
        if line.strip() in ('---', '...'):
            return True
        if not YAML_LINE.match(line.rstrip()):
            return False
    return False


def plain_lines(raw, git_message):
    """Markdown, plain text and commit messages: (locator, text, exemption) per nonblank line."""
    out, fence, fence_line, comment = [], None, 0, False
    lines = raw.splitlines()
    front = front_matter(lines)
    for n, line in enumerate(lines, 1):
        stripped = line.strip()
        exempt = None
        if front:
            exempt = 'metadata'
            if n > 1 and stripped in ('---', '...'):
                front = False
        elif fence:
            exempt = 'code'
            if stripped.startswith(fence) and not stripped.strip(fence[0]):
                fence = None
        elif comment:
            exempt = 'metadata'
            comment = '-->' not in stripped
        elif re.match(r'(`{3,}|~{3,})', stripped):
            fence, fence_line, exempt = re.match(r'(`{3,}|~{3,})', stripped).group(1), n, 'code'
        elif stripped.startswith('<!--'):
            exempt, comment = 'metadata', '-->' not in stripped
        elif stripped.startswith('>'):
            exempt = 'quotation'
        elif git_message and (stripped.startswith('#') or TRAILER.match(stripped)):
            exempt = 'metadata'
        if stripped:
            out.append((f'L{n}', stripped if exempt else line.rstrip(), exempt))
    if fence:
        raise Incomplete(f'code fence opened at line {fence_line} never closes; the lines after it cannot be scoped')
    return out


def extract(path, git_message=False):
    """Numbered records for every extracted line, each marked in scope or exempt with a reason."""
    if not path.is_file():
        raise Incomplete(f'{path} is not a file')
    if path.stat().st_size > MAX_BYTES:
        raise Incomplete(f'{path.name} is over {MAX_BYTES // (1024 * 1024)} MB')
    suffix = path.suffix.lower()
    source_lines = None
    try:
        if suffix in PLAIN_SUFFIXES or path.name in GIT_MESSAGES:
            raw = path.read_bytes().decode('utf-8-sig')
            if '\x00' in raw:
                raise Incomplete(f'{path.name} is binary')
            source_lines = raw.count('\n') + (0 if raw.endswith('\n') or not raw else 1)
            triples = plain_lines(raw, path.name in GIT_MESSAGES or git_message)
        elif suffix == '.json':
            raw = path.read_bytes().decode('utf-8-sig')
            json.loads(raw)
            source_lines = raw.count('\n') + 1
            triples = [(ln.loc, ln.text, None) for ln in ext.json_text_lines(raw, 1, 'Content text')]
        elif suffix in ext.TEXT_SUFFIXES:
            lines, source_lines = ext.extract_lines(path)
            triples = [(ln.loc, ln.text, 'quotation' if ln.text.startswith('> ') else None) for ln in lines]
        else:
            raise Incomplete(f'{suffix} files are not a format this check reads')
    except Incomplete:
        raise
    except Exception as error:  # a parse failure is reported, never passed over
        raise Incomplete(f'{path.name} could not be parsed: {type(error).__name__}: {error}')
    records, section = [], 0
    for i, (loc, text, exempt) in enumerate(triples, 1):
        masked = mask(text)
        if exempt is None and not WORD.search(masked):
            exempt = 'code' if '`' in text else 'quotation' if re.search(r'["“]', text) else 'no words'
        if HEADING.match(text):
            section += 1
        match = re.match(r'L(\d+)', loc)
        records.append({'id': f'{i:04d}', 'loc': loc, 'line': int(match.group(1)) if match else i,
                        'text': text, 'masked': masked if exempt in (None, 'no words') else '',
                        'exempt': exempt, 'section': section, 'sha': sha(text)[:12]})
    by_section = {}
    for r in records:
        if not r['exempt']:
            by_section.setdefault(r['section'], []).append(r['text'])
    for r in records:
        r['section_sha'] = sha('\n'.join(by_section.get(r['section'], [])))[:12]
    return records, source_lines


def in_scope(records):
    return [r for r in records if not r['exempt']]


def text_sha(records):
    return sha('\n'.join(r['text'] for r in in_scope(records)))


def parts(records, size=PART_LINES):
    """Split into parts of at most `size` lines, at a paragraph or section break when one is near."""
    out, start = [], 0
    while start < len(records):
        end = min(start + size, len(records))
        if end < len(records):
            for cut in range(end, max(start + size - 60, start + 1), -1):
                a, b = records[cut - 1], records[cut]
                if b['section'] != a['section'] or b['line'] - a['line'] > 1:
                    end = cut
                    break
        out.append(records[start:end])
        start = end
    return out


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------

class _Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise _Timeout()


def scan_chunk(chunk, rules):
    """Run every rule over one part. Returns the IDs scanned, their digest and the raw hits."""
    texts = [r['masked'] for r in chunk]
    joined = '\n'.join(texts)
    starts, pos = [], 0
    for t in texts:
        starts.append(pos)
        pos += len(t) + 1
    hits = []
    for rule, compiled in rules:
        for m in compiled.finditer(joined):
            found = m.group(0)
            if not found.strip():
                continue
            lead = len(found) - len(found.lstrip(' \n\t.!?:;,'))
            record = chunk[bisect.bisect_right(starts, m.start() + lead) - 1]
            if record['exempt']:
                continue
            hits.append({'id': record['id'], 'rule': rule['id'], 'text': ' '.join(found[lead:].split())[:120]})
    scanned = [(r['id'], t) for r, t in zip(chunk, joined.split('\n')) if not r['exempt']]
    return {'ids': [i for i, _ in scanned],
            'digest': sha('\n'.join(f'{i}\t{t}' for i, t in scanned)),
            'words': sum(len(WORD.findall(t)) for _, t in scanned),
            'hits': hits}


def guarded_scan(chunk, rules):
    timed = hasattr(signal, 'SIGALRM')
    if timed:
        try:
            previous = signal.signal(signal.SIGALRM, _alarm)
            signal.setitimer(signal.ITIMER_REAL, CHUNK_SECONDS)
        except ValueError:      # not the main thread
            timed = False
    try:
        return scan_chunk(chunk, rules)
    finally:
        if timed:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous)


def run_part(chunk, rules, attempt=0):
    """Scan a part; on failure retry up to twice with half the lines. Returns (results, failures)."""
    try:
        result = guarded_scan(chunk, rules)
        result['attempt'] = attempt
        return [result], []
    except Exception as error:
        reason = 'timed out' if isinstance(error, _Timeout) else f'{type(error).__name__}: {error}'
        if attempt < 2 and len(chunk) < 2:
            return run_part(chunk, rules, attempt + 1)
        if attempt >= 2:
            return [], [{'ids': [r['id'] for r in chunk if not r['exempt']], 'reason': reason, 'attempts': attempt + 1}]
        mid = len(chunk) // 2
        done_a, failed_a = run_part(chunk[:mid], rules, attempt + 1)
        done_b, failed_b = run_part(chunk[mid:], rules, attempt + 1)
        return done_a + done_b, failed_a + failed_b


def judge(hits, words, ledger, rules):
    """Apply the ledger: which hits block on sight, which the line pass must judge, which are advisory.

    A rule marked "judge": "line-pass" matches a shape a scanner cannot rule on, such as a list of
    three. Its hits never block from the scan; each one needs an answer in the line's verdict.
    """
    cfg = ledger['config']
    by_id = {rule['id']: rule for rule, _ in rules}
    totals = {}
    for h in hits:
        totals[h['rule']] = totals.get(h['rule'], 0) + 1
    kept = [h for h in hits if totals[h['rule']] >= by_id[h['rule']].get('min_count', 1)]
    review = [dict(h, fix=by_id[h['rule']].get('repair', '')) for h in kept
              if by_id[h['rule']].get('judge') == 'line-pass' and by_id[h['rule']].get('status') == 'active']
    kept = [h for h in kept if by_id[h['rule']].get('judge') != 'line-pass']
    weight = {i: (r.get('weight', 1) if r.get('status') == 'active' else 0) for i, r in by_id.items()}
    per500 = 500 / max(words, cfg.get('density_floor_words', 250))
    long_enough = words >= cfg.get('min_words', 40)
    dense = long_enough and sum(weight[h['rule']] for h in kept) * per500 >= cfg.get('flag_density', 4)
    counts = {}
    for h in kept:
        if weight[h['rule']]:
            counts[h['rule']] = counts.get(h['rule'], 0) + 1
    repeated = {i for i, n in counts.items() if long_enough and n >= cfg.get('repeat_limit', 3)
                and n * per500 >= cfg.get('repeat_density', 1.5)}
    blocking, advisory = [], []
    for h in kept:
        w = weight[h['rule']]
        hard = w >= cfg.get('hard_weight', 3)
        target = blocking if w and (hard or dense or h['rule'] in repeated) else advisory
        target.append(dict(h, fix=by_id[h['rule']].get('repair', '')))
    return blocking, advisory, review


# ---------------------------------------------------------------------------
# Whole-document aids
# ---------------------------------------------------------------------------

NOT_FIGURES = re.compile(
    r'\b\d{4}-\d{2}(?:-\d{2})?\b|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b|\b\d{1,2}:\d{2}(?::\d{2})?\b|\b\d+(?:\.\d+){2,}\b|'
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.? \d{1,2}(?:st|nd|rd|th)?\b|'
    r'\b(?:19|20)\d{2}\b|^\s*(?:[-*|>#]\s*)*\d+[.)](?=\s)')
FIGURE = re.compile(r'(?<![\w.])[$€£]?\d[\d,]*(?:\.\d+)?(?:%|[kKmMbB]\b|x\b)?')
# A number that names a thing: Phase 2, Steps 1 and 3, Table 4. These are labels, and no source is owed.
LABELS = re.compile(
    r'\b(?:phase|step|stage|section|figure|table|option|tier|round|part|sprint|wave|release|version|level|item|'
    r'appendix|chapter|page|line|rule|slide|tab|week|day|track|workstream|milestone|gate|exhibit|annex)s? '
    r'\d+(?:(?:, \d+)*,? (?:and|or|to|through) \d+)?\b', re.I)
WORD_NUMBER = re.compile(
    r'\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|'
    r'eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|billion|dozen)\b', re.I)


def figures(masked):
    """Numbers a reader could take as a claim. Dates, times, years, versions and list numbers are left out."""
    cleaned = LABELS.sub(blank, NOT_FIGURES.sub(blank, masked))
    return [m.group(0).rstrip(',') for m in FIGURE.finditer(cleaned)]


def word_numbers(masked):
    """Numbers written as words, from two upward. Each needs a source or a counts entry in the map."""
    return [m.group(0) for m in WORD_NUMBER.finditer(masked)]


def repeats(records):
    """Identical sentences and figures that appear in more than one section."""
    sentences, numbers = {}, {}
    for r in in_scope(records):
        for s in re.split(r'(?<=[.!?])\s+', r['masked']):
            s = ' '.join(s.split())
            if len(s.split()) >= 6:
                sentences.setdefault(s.lower(), []).append(r)
        for f in figures(r['masked']):
            if len(re.sub(r'\D', '', f)) >= 2:
                numbers.setdefault(f, []).append(r)
    out = []
    for kind, table in (('repeated-sentence', sentences), ('repeated-figure', numbers)):
        for key, found in table.items():
            if len({r['section'] for r in found}) > 1:
                first = found[0]
                where = ', '.join(sorted({r['id'] for r in found}))
                out.append({'id': first['id'], 'rule': kind, 'text': key[:120],
                            'fix': f'Appears in more than one section (lines {where}); state it once or confirm each use.'})
    return out


def outline(records):
    """Every heading and each section's first in-scope line."""
    out, body_shown = [], set()
    for r in in_scope(records):
        if HEADING.match(r['text']):
            out.append(r)
        elif r['section'] not in body_shown:
            body_shown.add(r['section'])
            out.append(r)
    return out


def section_heads(records):
    """The first in-scope line of each section, by section number."""
    heads = {}
    for r in in_scope(records):
        heads.setdefault(r['section'], r)
    return heads


# ---------------------------------------------------------------------------
# Line pass, spot audit and document pass: validate what the reviewers wrote
# ---------------------------------------------------------------------------

def load_json(path, what):
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise Incomplete(f'{what} {path} cannot be read: {error}')
    if not isinstance(data, dict):
        raise Incomplete(f'{what} {path} is not a JSON object')
    return data


def check_verdict(v, record, flagged=()):
    """Why one verdict is rejected, or None when it stands."""
    if v.get('sha') != record['sha']:
        return 'the line changed after this verdict was written'
    if v.get('section') != record['section_sha']:
        return 'another line in its section changed after this verdict was written'
    if v.get('verdict') not in ('ok', 'fix'):
        return 'verdict must be ok or fix'
    flags = [v.get(k) for k in ('portable', 'promise', 'tension')]
    if any(not isinstance(f, bool) for f in flags):
        return 'portable, promise and tension must each be answered true or false'
    answers = v.get('flags') if isinstance(v.get('flags'), dict) else {}
    for rule in flagged:
        if not isinstance(answers.get(rule), bool):
            return f'the scanner flagged this line for {rule}; flags.{rule} must be true (a real fault) or false'
    flags += [answers[rule] for rule in flagged]
    if v['verdict'] == 'ok':
        return 'a true answer to a line question or a scanner flag needs a fix' if any(flags) else None
    if not str(v.get('rule') or '').strip():
        return 'a fix names its rule'
    quote = v.get('quote')
    if not isinstance(quote, str) or not quote.strip() or quote not in record['text']:
        return 'the quote is not word for word in the line'
    if not isinstance(v.get('replacement'), str) or v['replacement'] == quote:
        return 'a fix gives a replacement that differs from the quote'
    return None


def line_pass(records, data, rules_sha256, flags=None):
    """Returns (findings, rejected, missing). Every in-scope line needs one valid verdict."""
    flags = flags or {}
    scope = {r['id']: r for r in in_scope(records)}
    findings, rejected, seen = [], [], set()
    stale = data.get('rules_sha256') != rules_sha256
    for v in data.get('verdicts') or []:
        vid = v.get('id') if isinstance(v, dict) else None
        if vid not in scope:
            rejected.append({'id': str(vid), 'reason': 'no in-scope line has this ID'})
            continue
        if vid in seen:
            rejected.append({'id': vid, 'reason': 'more than one verdict for this line'})
            continue
        reason = ('the rules changed after this verdict was written' if stale
                  else check_verdict(v, scope[vid], flags.get(vid, ())))
        if reason:
            rejected.append({'id': vid, 'reason': reason})
            continue
        seen.add(vid)
        if v['verdict'] == 'fix':
            findings.append({'id': vid, 'rule': 'line-pass: ' + str(v['rule']).strip(),
                             'text': v['quote'], 'fix': v['replacement'] or 'Cut these words.'})
    bad = {r['id'] for r in rejected}
    missing = [i for i in scope if i not in seen and i not in bad]
    return findings, rejected, missing


def source_names(path):
    """Names in the source list given with --sources: a JSON list of strings or of objects with a name."""
    try:
        data = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise Incomplete(f'source list {path} cannot be read: {error}')
    items = data.get('sources') if isinstance(data, dict) else data
    names = [str(i.get('name') if isinstance(i, dict) else i).strip() for i in (items or [])]
    names = [n for n in names if n and n != 'None']
    if not names:
        raise Incomplete(f'source list {path} names no sources')
    return names


def claims_check(records, data, names):
    """Each line's verdict says whether the line states a factual claim and which listed source supports it."""
    scope = {r['id'] for r in in_scope(records)}
    problems, seen = [], set()
    for v in data.get('verdicts') or []:
        vid = v.get('id') if isinstance(v, dict) else None
        if vid not in scope or vid in seen:
            continue
        seen.add(vid)
        claims = v.get('claims')
        if claims not in ('none', 'supported', 'unsupported'):
            problems.append({'id': vid, 'reason': 'claims must be none, supported or unsupported'})
        elif claims == 'supported' and str(v.get('source') or '').strip() not in names:
            problems.append({'id': vid, 'reason': 'a supported claim names a source from the source list'})
        elif claims == 'unsupported' and v.get('verdict') != 'fix':
            problems.append({'id': vid, 'reason': 'an unsupported claim needs a fix'})
    problems += [{'id': i, 'reason': 'no claims answer'} for i in sorted(scope - seen)]
    return problems


def audit_sample(records, verdicts):
    """A fifth of the lines the line pass marked ok, chosen from the text so the choice repeats."""
    ok = sorted(v['id'] for v in verdicts.get('verdicts') or [] if isinstance(v, dict) and v.get('verdict') == 'ok')
    if not ok:
        return []
    chooser = random.Random(text_sha(records))
    return sorted(chooser.sample(ok, max(1, -(-len(ok) // AUDIT_SHARE))))


def spot_audit(records, verdicts, data, rules_sha256, flags=None):
    """Returns (findings, rejected, missing). One miss sends every line back through the line pass."""
    scope = {r['id']: r for r in in_scope(records)}
    wanted = [i for i in audit_sample(records, verdicts) if i in scope]
    sub = [scope[i] for i in wanted]
    findings, rejected, missing = line_pass(sub, data, rules_sha256, flags)
    for f in findings:
        f['rule'] = 'spot-audit miss, full line pass required: ' + f['rule'].split(': ', 1)[-1]
    first, second = str(verdicts.get('reviewer') or '').strip(), str(data.get('reviewer') or '').strip()
    marked_ok = sum(1 for v in verdicts.get('verdicts') or [] if isinstance(v, dict) and v.get('verdict') == 'ok')
    info = {'sampled': len(wanted), 'lines_marked_ok': marked_ok, 'line_pass_reviewer': first or None,
            'audit_reviewer': second or None, 'independent': bool(first and second and first != second)}
    return findings, rejected, missing, info


def document_pass(records, data, rules_sha256):
    """Validate the fixed map. Returns (findings, problems); any problem leaves the pass incomplete."""
    scope = {r['id']: r for r in in_scope(records)}
    problems, findings = [], []

    def line(item, key='id'):
        value = item.get(key) if isinstance(item, dict) else None
        if value not in scope:
            problems.append(f'{key} {value!r} is not an in-scope line ID')
            return None
        return scope[value]

    def quoted(item, record):
        quote = item.get('quote')
        if not isinstance(quote, str) or not quote or record is None or quote not in record['text']:
            problems.append(f'quote {quote!r} is not word for word in line {item.get("id")}')
            return False
        return True

    def add(record, rule, text, fix, merged_with=None, ids=()):
        item = {'id': record['id'], 'rule': 'document-pass: ' + rule, 'text': text[:160], 'fix': fix}
        if merged_with is not None:
            if merged_with not in ids:
                problems.append(f'merged_with {merged_with!r} is not one of the lines of {text[:40]!r}')
            else:
                item['id'], item['merged_with'] = merged_with, merged_with
        findings.append(item)

    for key in MAP_KEYS:
        if key not in data:
            problems.append(f'the map has no "{key}" entry')
    if problems:
        return findings, problems
    if data.get('text_sha256') != text_sha(records):
        problems.append('the text changed after this map was written; the document pass reruns on the full text')
    if data.get('rules_sha256') != rules_sha256:
        problems.append('the rules changed after this map was written')
    reader = data['reader'] if isinstance(data['reader'], dict) else {}
    for key in ('who', 'must_decide_or_do'):
        if len(str(reader.get(key) or '').split()) < 3:
            problems.append(f'reader.{key} is not written out')

    heads = section_heads(records)
    covered = set()
    for item in data['sections']:
        record = line(item)
        if record is None:
            continue
        covered.add(record['section'])
        if len(str(item.get('point') or '').split()) < 3:
            problems.append(f'section at line {record["id"]} has no point written out')
        if item.get('role') == 'title':
            size = sum(1 for r in scope.values() if r['section'] == record['section'])
            if size > TITLE_SECTION_LINES:
                problems.append(f'section at line {record["id"]} has {size} lines; a title section has at most '
                                f'{TITLE_SECTION_LINES}')
            continue
        if not isinstance(item.get('reader_acts'), bool):
            problems.append(f'section at line {record["id"]} does not say whether the reader acts on it')
        elif not item['reader_acts']:
            add(record, 'reader would not act on this section', record['text'],
                'Rewrite the section for what this reader must decide or do, or cut it.')
    for number, head in heads.items():
        if number not in covered:
            problems.append(f'the section that starts at line {head["id"]} is missing from the map')

    wanted = {r['id'] for r in scope.values() if HEADING.match(r['text'])}
    for item in data['headings']:
        record = line(item)
        if record is None:
            continue
        wanted.discard(record['id'])
        if not isinstance(item.get('matches'), bool):
            problems.append(f'heading {record["id"]} has no true or false for matches')
        elif not item['matches']:
            add(record, 'heading does not match its content', record['text'],
                'Rename the heading to state what the section says.')
    for missing in sorted(wanted):
        problems.append(f'heading {missing} is missing from the map')

    structure = data.get('structural_repeat')
    allowed = set()
    if structure is not None:
        named = [scope[i]['section'] for i in (structure.get('sections') or []) if i in scope] \
            if isinstance(structure, dict) else []
        if len(set(named)) < 2 or len(named) != len(structure.get('sections') or []) \
                or len(str(structure.get('reason') or '').split()) < 5:
            problems.append('structural_repeat needs a reason of five or more words and the first line IDs of '
                            'two or more sections')
        else:
            allowed = set(named)
    declared = []
    for item in data['repeated_facts']:
        found = [scope[i] for i in (item.get('ids') or []) if i in scope]
        if len(found) < 2 or len(found) != len(item.get('ids') or []):
            problems.append(f'repeated fact {item.get("quote")!r} needs two or more in-scope line IDs')
        elif not any(isinstance(item.get('quote'), str) and item['quote'] and item['quote'] in r['text'] for r in found):
            problems.append(f'quote {item.get("quote")!r} is in none of its lines')
        elif item.get('structural'):
            sections = {r['section'] for r in found}
            if not allowed or not sections <= allowed or len(sections) < 2:
                problems.append(f'repeated fact {item["quote"]!r} is marked structural, but its lines are not spread '
                                'across the sections named in structural_repeat')
            else:
                declared.append({'quote': item['quote'], 'ids': [r['id'] for r in found]})
        else:
            add(found[1], 'fact stated more than once', item['quote'],
                'State the fact once; lines ' + ', '.join(r['id'] for r in found) + ' repeat it.',
                merged_with=item.get('merged_with'), ids=[r['id'] for r in found])
    for item in data['counts']:
        record = line(item)
        if record is None or not quoted(item, record):
            continue
        stated, listed = item.get('stated'), item.get('listed')
        if not isinstance(stated, int) or not isinstance(listed, int):
            problems.append(f'count at line {record["id"]} needs whole numbers for stated and listed')
        elif stated != listed:
            add(record, 'count does not match the items listed', item['quote'],
                f'The text says {stated} and lists {listed}; make them agree.',
                merged_with=item.get('merged_with'), ids=[record['id']])
    for key, rule, fix in (
            ('recaps', 'recap of another section', 'Cut the recap; the other section already says it.'),
            ('leftover_lines', 'line exists only because of an earlier mistake', 'Cut the line.'),
            ('provenance', 'provenance in finished copy', 'Remove the source note, meeting reference or evidence note.')):
        for item in data[key]:
            record = line(item)
            if record is not None:
                add(record, rule, str(item.get('quote') or record['text']), fix)
    for item in data['terms']:
        names = [t for t in (item.get('terms') or []) if isinstance(t, str) and t.strip()]
        found = [scope[i] for i in (item.get('ids') or []) if i in scope]
        if len(names) < 2 or not found:
            problems.append(f'terms entry {names!r} needs two or more terms and the line IDs that use them')
        else:
            add(found[0], 'more than one term for one thing', ' / '.join(names),
                'Keep one of these terms and use it on lines ' + ', '.join(r['id'] for r in found) + '.',
                merged_with=item.get('merged_with'), ids=[r['id'] for r in found])

    needed = {(r['id'], f) for r in scope.values() for f in figures(r['masked']) + word_numbers(r['masked'])}
    for item in data['counts']:      # a count of the document's own items is its own source
        if isinstance(item, dict) and isinstance(item.get('quote'), str):
            needed = {(i, f) for i, f in needed
                      if not (i == item.get('id') and WORD_NUMBER.fullmatch(f) and f in item['quote'])}
    for item in data['numbers']:
        record = line(item)
        if record is None or not quoted(item, record):
            continue
        needed = {(i, f) for i, f in needed if not (i == record['id'] and f in item['quote'])}
        source, assumption = str(item.get('source') or '').strip(), item.get('assumption_id')
        if assumption is not None and assumption not in scope:
            problems.append(f'assumption_id {assumption!r} is not an in-scope line ID')
        elif not source and assumption is None:
            add(record, 'number with no source', item['quote'],
                'Trace the number to a named source, or state in the text that it is an assumption.')
    for rid, figure in sorted(needed):
        problems.append(f'the number {figure} on line {rid} is not in the map')

    conf = data['confidentiality'] if isinstance(data['confidentiality'], dict) else {}
    if len(str(conf.get('none_applies') or '').split()) >= 3:
        pass
    elif conf.get('retrieved') is not True:
        problems.append('the confidentiality list was not retrieved (confidentiality.retrieved is not true); stop and '
                        'report the review as incomplete, and do not rebuild the list from other documents')
    elif not str(conf.get('list') or '').strip():
        problems.append('confidentiality.list does not name the list that was checked')
    for item in conf.get('hits') or []:
        record = line(item)
        if record is not None:
            add(record, 'confidential material', str(item.get('quote') or record['text']),
                'Remove it; the project confidentiality list covers it.')
    return findings, problems, declared


def merge_faults(findings):
    """Count one fault once: a document finding joins the line fix on the same line when both name one fault.

    That holds for the single-line document rules, and for any entry the map marks with merged_with.
    """
    line_fix = {f['id']: f for f in findings if f['rule'].startswith('line-pass: ')}
    kept = []
    for f in findings:
        rule = f['rule'][len('document-pass: '):] if f['rule'].startswith('document-pass: ') else None
        target = line_fix.get(f['id'])
        if rule and target is not None and (rule in SINGLE_LINE_FAULTS or f.get('merged_with')):
            target.setdefault('also', []).append(f['rule'])
            continue
        kept.append(f)
    return kept


# ---------------------------------------------------------------------------
# Prepare the reviewers' working files
# ---------------------------------------------------------------------------

def shown(r):
    note = f' (exempt: {r["exempt"]})' if r['exempt'] else ''
    return f'[{r["id"]}] {r["loc"]}{note}: {r["text"]}'


def workers(records):
    """Groups of about WORKER_LINES in-scope lines; a section stays with one worker when it fits."""
    groups, current = [], []
    by_section = {}
    for r in in_scope(records):
        by_section.setdefault(r['section'], []).append(r)
    for block in by_section.values():
        if current and len(current) + len(block) > WORKER_LINES:
            groups.append(current)
            current = []
        while len(block) > WORKER_LINES:
            groups.append(block[:WORKER_LINES])
            block = block[WORKER_LINES:]
        current = current + block
    if current:
        groups.append(current)
    return groups


def prepare(path, records, rules, out, verdicts=None, review=(), sources=None):
    out = Path(out)
    (out / 'text').mkdir(parents=True, exist_ok=True)
    for old in (out / 'text').glob('part-*.md'):
        old.unlink()
    names = []
    for n, part in enumerate(parts(records), 1):
        name = f'part-{n:03d}.md'
        (out / 'text' / name).write_text('\n'.join(shown(r) for r in part) + '\n', encoding='utf-8')
        names.append(name)
    lines = [f'# Outline of {path.name}', '', 'Every heading and the first line of each section.', '']
    lines += [shown(r) for r in outline(records)]
    (out / 'outline.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    scope = in_scope(records)
    flagged = {}
    for item in review:
        flagged.setdefault(item['id'], []).append({'rule': item['rule'], 'text': item['text']})

    def entry(r):
        return {'id': r['id'], 'sha': r['sha'], 'section': r['section_sha'], 'loc': r['loc'],
                'text': r['text'], 'flags': flagged.get(r['id'], [])}
    plan = {
        'file': str(path), 'source_sha256': sha(path.read_bytes()), 'text_sha256': text_sha(records),
        'rules_sha256': rules['rules_sha256'], 'lines_in_scope': len(scope), 'parts': names,
        'two_step_document_pass': len(scope) > LONG_DOCUMENT_LINES,
        'workers': [{'worker': n, 'lines': [entry(r) for r in group]}
                    for n, group in enumerate(workers(records), 1)],
        'sections': [{'id': head['id'], 'text': head['text']} for head in section_heads(records).values()],
        'headings': [r['id'] for r in scope if HEADING.match(r['text'])],
        'numbers': [{'id': r['id'], 'quote': f} for r in scope for f in figures(r['masked'])]
        + [{'id': r['id'], 'quote': f, 'kind': 'word'} for r in scope for f in word_numbers(r['masked'])],
        'sources': sources or [],
        'repeats': repeats(records),
    }
    if verdicts:
        wanted = set(audit_sample(records, verdicts))
        plan['audit'] = [entry(r) for r in scope if r['id'] in wanted]
    (out / 'assignments.json').write_text(json.dumps(plan, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    return out / 'assignments.json'


# ---------------------------------------------------------------------------
# Run, receipt and command line
# ---------------------------------------------------------------------------

def receipt_dir(arg):
    return Path(arg or os.environ.get('WRITING_RECEIPTS') or Path.home() / '.agents' / 'writing' / 'receipts').expanduser()


def run(args):
    path = Path(args.file).expanduser().resolve()
    registers = [x.strip() for x in (args.register or '').split(',') if x.strip()]
    full = bool(args.full or args.verdicts or args.document_map or args.audit) and not (
        args.prepare and not (args.full or args.document_map or args.audit))
    record = {'tool': 'writing check', 'version': VERSION, 'started': now(), 'file': str(path),
              'register': registers, 'status': 'incomplete', 'reason': '',
              'coverage': {'lines_total': 0, 'lines_reviewed': 0}, 'steps': [], 'parts': [],
              'not_reviewed': [], 'findings': [], 'advisories': [], 'review': []}
    steps, reasons = record['steps'], []

    def step(name, status, detail):
        steps.append({'step': name, 'status': status, 'detail': detail})
        if status == 'failed':
            reasons.append(f'{name}: {detail}')

    records, findings = [], []
    try:
        ledger, rules_info = load_rules(args.rules_dir)
        new_names, known = note_registers(registers, rules_info['home'], ledger, path)
        rules = active_rules(ledger, registers)
        added = {name: sum(1 for r, _ in rules if r.get('scope') == name or name in (r.get('registers') or []))
                 for name in registers}
        record['rules'] = dict(rules_info, rules_applied=len(rules), register_rules=added, new_registers=new_names)
        detail = f'{len(rules)} rules from {rules_info["ledger"]} ({rules_info["ledger_source"]})'
        for name, count in added.items():
            if name in new_names:
                detail += (f'; register {name} is new and added no rules ({new_names[name]}); known names: '
                           + ', '.join(known))
            else:
                detail += f'; register {name} adds {count} rules' + ('' if count else ', its guidance is in registers.md')
        step('rules', 'ok', detail)
        records, source_lines = extract(path, 'commit' in registers)
        record.update(sha256=sha(path.read_bytes()), bytes=path.stat().st_size, text_sha256=text_sha(records))
    except Incomplete as error:
        step('rules' if not steps else 'extract', 'failed', str(error))
        return finish(record, args, reasons, records)
    scope = in_scope(records)
    exempt = {}
    for r in records:
        if r['exempt']:
            exempt[r['exempt']] = exempt.get(r['exempt'], 0) + 1
    record['coverage'] = {'lines_total': len(scope), 'lines_reviewed': 0, 'lines_exempt': exempt,
                          'lines_extracted': len(records), 'source_lines': source_lines}
    step('extract', 'ok', f'{len(records)} lines extracted, {len(scope)} in scope, {sum(exempt.values())} exempt')

    by_id = {r['id']: r for r in records}
    hits, words, reviewed, failed = [], 0, [], []
    for n, part in enumerate(parts(records), 1):
        done, failures = run_part(part, rules)
        for result in done:
            got = set(result['ids'])
            expected = [(r['id'], r['masked']) for r in part if r['id'] in got]
            if result['digest'] != sha('\n'.join(f'{i}\t{t}' for i, t in expected)):
                failures.append({'ids': result['ids'], 'reason': 'scan digest does not match the extracted lines', 'attempts': 1})
                continue
            reviewed += result['ids']
            hits += result['hits']
            words += result['words']
        failed += failures
        ids = [r['id'] for r in part if not r['exempt']]
        so_far = set(reviewed)
        record['parts'].append({'part': n, 'first': part[0]['id'], 'last': part[-1]['id'], 'lines_in_scope': len(ids),
                                'lines_reviewed': len([i for i in ids if i in so_far]),
                                'retries': max([x['attempt'] for x in done] or [0]),
                                'failures': [f['reason'] for f in failures]})
    so_far = set(reviewed)
    missing = [r['id'] for r in scope if r['id'] not in so_far]
    extra = len(reviewed) != len(set(reviewed))
    record['coverage']['lines_reviewed'] = len(set(reviewed) & {r['id'] for r in scope})
    record['not_reviewed'] = [{'id': i, 'loc': by_id[i]['loc']} for i in missing]
    if missing or extra or failed:
        detail = f'{len(missing)} of {len(scope)} in-scope lines were not scanned'
        if failed:
            detail += '; ' + '; '.join(sorted({f['reason'] for f in failed}))
        step('scan', 'failed', detail)
    else:
        step('scan', 'ok', f'{len(scope)} of {len(scope)} in-scope lines scanned in {len(record["parts"])} parts')
    blocking, advisory, review = judge(hits, words, ledger, rules)
    findings += blocking
    record['words'] = words
    record['advisories'] = [present(a, by_id) for a in advisory + repeats(records)]
    record['review'] = [present(r, by_id) for r in review]
    flags = {}
    for item in review:
        if item['rule'] not in flags.setdefault(item['id'], []):
            flags[item['id']].append(item['rule'])
    if review and steps[-1]['status'] == 'ok':
        steps[-1]['detail'] += f'; {len(review)} flags on {len(flags)} lines wait for a line-pass verdict'

    if full:
        verdicts = None
        if not rules_info['rules_md_sha256']:
            step('rules.md', 'failed', 'the rules folder has no rules.md for the line pass to apply')
        if args.verdicts:
            try:
                verdicts = load_json(args.verdicts, 'verdict file')
                found, rejected, absent = line_pass(records, verdicts, rules_info['rules_sha256'], flags)
                findings += found
                if rejected or absent:
                    record['line_pass'] = {'rejected': rejected, 'no_verdict': absent}
                    step('line pass', 'failed', f'{len(absent)} lines have no verdict and {len(rejected)} verdicts were rejected')
                else:
                    step('line pass', 'ok', f'{len(scope)} of {len(scope)} lines have a valid verdict, {len(found)} marked fix')
            except Incomplete as error:
                step('line pass', 'failed', str(error))
        else:
            step('line pass', 'failed', 'no verdict file was given')
        try:
            names = source_names(args.sources) if args.sources else None
            if names is None:
                step('claims check', 'failed', 'no source list was given with --sources')
            elif verdicts is None:
                step('claims check', 'failed', 'no verdict file to read the claims answers from')
            else:
                unanswered = claims_check(records, verdicts, names)
                if unanswered:
                    record['claims_check'] = {'problems': unanswered}
                    step('claims check', 'failed', f'{len(unanswered)} lines have no valid claims answer; the first: '
                         f'{unanswered[0]["id"]}, {unanswered[0]["reason"]}')
                else:
                    step('claims check', 'ok', f'{len(scope)} lines answered against {len(names)} listed sources')
        except Incomplete as error:
            step('claims check', 'failed', str(error))
        if args.document_map:
            try:
                found, problems, declared = document_pass(records, load_json(args.document_map, 'document map'),
                                                          rules_info['rules_sha256'])
                findings += found
                record['document_pass'] = {'problems': problems, 'declared_repeats': declared}
                if problems:
                    step('document pass', 'failed', f'{len(problems)} problems in the map; the first: {problems[0]}')
                else:
                    step('document pass', 'ok', f'map complete, {len(found)} findings'
                         + (f', {len(declared)} repeats declared as structure' if declared else ''))
            except Incomplete as error:
                step('document pass', 'failed', str(error))
        else:
            step('document pass', 'failed', 'no document map was given')
        findings = merge_faults(findings)
        if args.audit and verdicts is not None:
            try:
                found, rejected, absent, info = spot_audit(records, verdicts, load_json(args.audit, 'audit file'),
                                                           rules_info['rules_sha256'], flags)
                record['spot_audit'] = info
                scope_note = f'{info["sampled"]} of the {info["lines_marked_ok"]} lines marked ok were re-reviewed'
                independence = '' if info['independent'] else (
                    '; not independent, because the audit file does not name a reviewer other than the line-pass reviewer')
                if found:
                    findings += found
                    step('spot audit', 'failed', f'{scope_note}; {len(found)} need a fix, so every line goes back '
                         f'through the line pass{independence}')
                elif rejected or absent:
                    step('spot audit', 'failed', f'{len(absent)} sampled lines have no verdict and {len(rejected)} were rejected')
                else:
                    step('spot audit', 'ok', scope_note + ' and stand'
                         + (f'; the round still fails on its {len(findings)} findings' if findings else '') + independence)
            except Incomplete as error:
                step('spot audit', 'failed', str(error))
        elif findings or reasons:
            step('spot audit', 'not_run', 'optional in a round that does not pass; the lines marked ok were not re-reviewed')
        else:
            step('spot audit', 'failed', 'a clean round passes only after the spot audit; run --prepare with --verdicts '
                 'for the sample, then pass --audit')
    else:
        for name in ('line pass', 'claims check', 'document pass', 'spot audit'):
            step(name, 'not_run', 'not part of this run; a pass here covers the scan only')

    if args.prepare:
        try:
            made = prepare(path, records, rules_info, args.prepare,
                           load_json(args.verdicts, 'verdict file') if args.verdicts else None, review,
                           source_names(args.sources) if args.sources else None)
            record['purpose'] = 'prepare'
            step('prepare', 'ok', f'{made} and the text parts were rewritten; verdict, map and audit files were not touched')
        except (OSError, Incomplete) as error:
            step('prepare', 'failed', str(error))
    record['findings'] = [present(f, by_id) for f in sorted(findings, key=lambda f: f['id'])]
    return finish(record, args, reasons, records)


def present(item, by_id):
    r = by_id[item['id']]
    out = {'line': r['line'], 'rule': item['rule'], 'text': item['text'], 'fix': item['fix'], 'id': r['id'], 'loc': r['loc']}
    if item.get('also'):
        out['also'] = item['also']
    return out


def finish(record, args, reasons, records):
    record['finished'] = now()
    if reasons:
        record['status'], record['reason'] = 'incomplete', '; '.join(reasons)
    else:
        record['status'] = 'fail' if record['findings'] else 'pass'
    folder = receipt_dir(args.receipt_dir)
    name = re.sub(r'[^A-Za-z0-9._-]+', '-', Path(record['file']).name)[:60]
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target = folder / f'{name}-{sha(record["file"])[:8]}-{stamp}.json'
    try:
        folder.mkdir(parents=True, exist_ok=True)
        record['receipt'] = str(target)
        target.write_text(json.dumps(record, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    except OSError as error:
        record['receipt'] = None
        record['status'] = 'incomplete'
        record['reason'] = '; '.join(filter(None, [record['reason'], f'receipt could not be written: {error}']))
    return record


def summary(record):
    out = {'status': record['status'],
           'coverage': {k: record['coverage'][k] for k in ('lines_total', 'lines_reviewed')},
           'findings': record['findings'], 'receipt': record['receipt']}
    if 'lines_exempt' in record['coverage']:
        out['coverage']['lines_exempt'] = sum(record['coverage']['lines_exempt'].values())
    if record['status'] == 'incomplete':
        out['reason'] = record['reason']
        out['not_reviewed'] = record['not_reviewed']
    out['steps'] = record['steps']
    out['advisories'] = len(record['advisories'])
    out['review'] = len(record.get('review', []))
    return out


def verify_receipt(path):
    """Recheck a receipt: the file and ledger are unchanged and the counts support the status."""
    try:
        record = load_json(path, 'receipt')
        problems = []
        source = Path(record['file'])
        if not source.is_file() or sha(source.read_bytes()) != record.get('sha256'):
            problems.append('the file changed after this receipt was written')
        ledger = Path((record.get('rules') or {}).get('ledger') or '')
        if not ledger.is_file() or sha(ledger.read_bytes()) != record['rules'].get('ledger_sha256'):
            problems.append('the pattern ledger changed after this receipt was written')
        cov = record['coverage']
        counted = sum(p['lines_reviewed'] for p in record.get('parts', []))
        if record['status'] != 'incomplete' and not (cov['lines_total'] == cov['lines_reviewed'] == counted):
            problems.append('the line counts do not support the status')
        if record['status'] == 'pass' and record['findings']:
            problems.append('a pass receipt lists findings')
        if record['status'] != 'incomplete' and any(s['status'] == 'failed' for s in record['steps']):
            problems.append('a step failed but the status is not incomplete')
    except (Incomplete, KeyError, TypeError) as error:
        print(json.dumps({'valid': False, 'problems': [f'receipt cannot be checked: {error}']}))
        return 2
    print(json.dumps({'valid': not problems, 'status': record['status'], 'problems': problems,
                      'steps': [{'step': s['step'], 'status': s['status']} for s in record['steps']]}, indent=1))
    return 0 if not problems else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description='Check every in-scope line of one file against the writing rules folder.')
    parser.add_argument('--file')
    parser.add_argument('--register', help='channel, audience or author name; adds the ledger rules scoped to it')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--rules-dir')
    parser.add_argument('--receipt-dir')
    parser.add_argument('--prepare', metavar='DIR')
    parser.add_argument('--verdicts', metavar='FILE')
    parser.add_argument('--document-map', metavar='FILE')
    parser.add_argument('--audit', metavar='FILE')
    parser.add_argument('--sources', metavar='FILE')
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--verify-receipt', metavar='FILE')
    try:
        args = parser.parse_args(argv)
    except SystemExit as stop:
        if stop.code and '--json' in (sys.argv[1:] if argv is None else argv):
            print(json.dumps({'status': 'incomplete', 'coverage': {'lines_total': 0, 'lines_reviewed': 0},
                              'findings': [], 'receipt': None, 'reason': 'the command line could not be read'}))
        return 2 if stop.code else 0
    if args.verify_receipt:
        return verify_receipt(args.verify_receipt)
    if not args.file:
        print('check.py: --file is required', file=sys.stderr)
        return 2
    try:
        record = run(args)
    except Exception as error:  # an unexpected failure is incomplete, never a pass
        record = {'status': 'incomplete', 'coverage': {'lines_total': 0, 'lines_reviewed': 0}, 'findings': [],
                  'receipt': None, 'reason': f'{type(error).__name__}: {error}', 'not_reviewed': [], 'steps': [],
                  'advisories': []}
    code = {'pass': 0, 'fail': 1}.get(record['status'], 2)
    if args.json:
        print(json.dumps(summary(record), indent=1, ensure_ascii=False))
        return code
    cov = record['coverage']
    print(f'{record["status"].upper()}: {cov["lines_reviewed"]} of {cov["lines_total"]} in-scope lines scanned, '
          f'{len(record["findings"])} findings')
    for s in record['steps']:
        print(f'  {s["step"]}: {s["status"]} - {s.get("detail", "")}')
    for f in record['findings']:
        print(f'  line {f["line"]} [{f["id"]}] {f["rule"]}: "{f["text"]}"\n      {f["fix"]}')
    if record.get('reason'):
        print('Not complete: ' + record['reason'])
    print(f'Receipt: {record["receipt"]}')
    return code


if __name__ == '__main__':
    sys.exit(main())
