#!/usr/bin/env python3
"""Rank competing candidates with one named scoring method and show the arithmetic.

The output is a proposal for a named decision owner, who settles the order.
MoSCoW values belong to capture-requirements and are never changed here.

Methods, chosen with --framework:
  ice          impact * confidence * ease
  odi          importance + max(importance - satisfaction, 0), customer ratings on 0-10
  opportunity  importance * (1 - satisfaction), importance on 0-10, satisfaction on 0-1
  rice         (reach * impact * confidence) / effort, impact on the 0.25/0.5/1/2/3 scale
  weighted     sum of weight * score over the criteria listed in the file
  wsjf         (business_value + time_criticality + risk_reduction) / job_size

Evidence rules applied while scoring:
  Confidence in ice or rice may be a fraction or a percent. Anything above 1
  is divided by 100. A value no higher than 10 is flagged as well, since it
  looks like a rating. Unsourced confidence above 0.5 is scored as 0.5.
  Effort and job size without a source in sources.effort are flagged as not
  ready to publish. For odi and opportunity, importance needs a customer
  source; without one the score is a hypothesis.
  Satisfaction above 1 for opportunity is treated as a rating and divided by 10.
  Any item naming neither a job nor a problem is flagged.
  Run notes list ties and rescaled weights. For ice and rice they also report
  a top impact value held by more than 30% of four or more scored items.

Exit codes:
  0  every item was scored; flags and notes may still appear
  1  a report was produced and at least one item was rejected
  2  the input could not be used (unreadable file, invalid JSON, wrong shape,
     no items, invalid weighted criteria, or an unwritable --output path);
     stderr carries a message starting with "error:" and no report is printed

Usage:
  python3 priority_score.py CANDIDATES.json --framework rice [--format json] [--output PATH]
"""
import argparse
import json
import math
import re
import sys

FRAMEWORKS = ('ice', 'odi', 'opportunity', 'rice', 'weighted', 'wsjf')
DISPLAY_NAMES = {
    'ice': 'ICE',
    'odi': 'ODI opportunity algorithm',
    'opportunity': 'Opportunity Score',
    'rice': 'RICE',
    'weighted': 'weighted decision matrix',
    'wsjf': 'WSJF',
}
REQUIRED_FIELDS = {
    'ice': ('impact', 'confidence', 'ease'),
    'odi': ('importance', 'satisfaction'),
    'opportunity': ('importance', 'satisfaction'),
    'rice': ('reach', 'impact', 'confidence', 'effort'),
    'wsjf': ('business_value', 'time_criticality', 'risk_reduction', 'job_size'),
}
POSITIVE_FIELD = {'rice': 'effort', 'wsjf': 'job_size'}
RICE_IMPACT_SCALE = (0.25, 0.5, 1.0, 2.0, 3.0)
CONFIDENCE_CAP = 0.5
TOP_IMPACT_SHARE = 0.3
TOP_IMPACT_MINIMUM = 4
WEIGHT_TOLERANCE = 0.01
PLAIN_NUMBER = re.compile(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?')
REPORT_KEYS = ('framework', 'ranking', 'errors', 'notes')


class InputError(Exception):
    """Raised when the candidate file or the output path makes scoring impossible."""


def fmt(number):
    """Write a number compactly: 3 rather than 3.0, at most six decimal places."""
    number = float(number)
    if number.is_integer() and abs(number) < 1e15:
        return str(int(number))
    text = ('%.6f' % number).rstrip('0').rstrip('.')
    return '0' if text in ('', '-0') else text


def as_number(value):
    """Return a finite float for a JSON number or plain numeric text, otherwise None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, str):
        value = value.strip()
        if not PLAIN_NUMBER.fullmatch(value):
            return None
    elif not isinstance(value, (int, float)):
        return None
    try:
        number = float(value)
    except (OverflowError, ValueError):
        return None
    return number if math.isfinite(number) else None


def as_text(value):
    """Return display text for an id, title, job or problem; other JSON types give ''."""
    if isinstance(value, bool):
        return ''
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return fmt(value) if math.isfinite(value) else ''
    if isinstance(value, str):
        return ' '.join(value.split())
    return ''


def has_source(value):
    """True when a sources entry holds non-blank text, directly or inside a list or object."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(has_source(entry) for entry in value)
    if isinstance(value, dict):
        return any(has_source(entry) for entry in value.values())
    return False


def kind_of(value):
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'a boolean'
    if isinstance(value, str):
        return 'a string'
    if isinstance(value, (int, float)):
        return 'a number'
    return 'an array' if isinstance(value, list) else 'an object'


def reason(exc):
    return getattr(exc, 'strerror', None) or str(exc)


def load(path):
    """Read the candidate file and return its items plus any criteria array."""
    try:
        with open(path, encoding='utf-8-sig') as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f'cannot read {path}: {reason(exc)}')
    try:
        data = json.loads(text)
    except RecursionError:
        raise InputError(f'{path} is nested too deeply to parse')
    except ValueError as exc:
        where = f' ({exc.msg} at line {exc.lineno}, column {exc.colno})' if isinstance(exc, json.JSONDecodeError) else ''
        raise InputError(f'{path} is not valid JSON{where}')
    if isinstance(data, list):
        items, criteria = data, None
    elif isinstance(data, dict) and isinstance(data.get('items'), list):
        items, criteria = data['items'], data.get('criteria')
    else:
        raise InputError(f'{path} must hold a JSON array of items or an object whose "items" key is an array')
    if not items:
        raise InputError(f'{path} contains no items to score')
    return items, criteria


def read_criteria(raw):
    """Check weighted criteria and return (name, weight) pairs plus an optional rescaling note."""
    if not isinstance(raw, list) or not raw:
        raise InputError('weighted scoring needs a non-empty "criteria" array of {"name", "weight"} objects')
    criteria, names = [], set()
    for position, entry in enumerate(raw, 1):
        if not isinstance(entry, dict):
            raise InputError(f'criterion {position} is {kind_of(entry)}; write each one as an object with a name and a weight')
        name = entry.get('name')
        if not isinstance(name, str) or not name.strip():
            raise InputError(f'criterion {position} has no name')
        if name in names:
            raise InputError(f'criterion name {json.dumps(name)} appears twice')
        weight = as_number(entry.get('weight'))
        if weight is None or weight < 0:
            raise InputError(f'criterion {json.dumps(name)} needs a numeric weight of 0 or more')
        names.add(name)
        criteria.append((name, weight))
    total = sum(weight for _, weight in criteria)
    if total <= 0:
        raise InputError('criterion weights add up to 0; give at least one criterion a positive weight')
    if abs(total - 1) <= WEIGHT_TOLERANCE:
        return criteria, None
    note = f'Criterion weights summed to {fmt(total)}; each weight was divided by that total before scoring.'
    return [(name, weight / total) for name, weight in criteria], note


def missing_message(names):
    noun = 'field' if len(names) == 1 else 'fields'
    return f'missing required {noun}: ' + ', '.join(names)


def quoted(value, limit=40):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[:limit - 3] + '...'


def invalid_message(pairs):
    return 'not a number: ' + ', '.join(f'{name}={quoted(value)}' for name, value in pairs)


def read_fields(item, names, problems):
    """Collect required numeric fields; record absent, null and non-numeric ones as problems."""
    missing = [name for name in names if item.get(name) is None]
    invalid = [(name, item[name]) for name in names if item.get(name) is not None and as_number(item[name]) is None]
    if missing:
        problems.append(missing_message(missing))
    if invalid:
        problems.append(invalid_message(invalid))
    return {name: as_number(item[name]) for name in names if item.get(name) is not None}


def read_scores(item, criteria, problems):
    """Collect one numeric score per weighted criterion from the item's scores object."""
    scores = item.get('scores')
    if scores is None:
        problems.append(missing_message(['scores']))
        return {}
    if not isinstance(scores, dict):
        problems.append('scores needs to be an object mapping each criterion name to a number')
        return {}
    absent = [name for name, _ in criteria if scores.get(name) is None]
    if absent:
        message = 'no score for criteria: ' + ', '.join(json.dumps(name) for name in absent)
        unknown = [key for key in scores if key not in dict(criteria)]
        if unknown:
            message += ' (unrecognized keys in scores: ' + ', '.join(json.dumps(key) for key in unknown) + ')'
        problems.append(message)
    invalid = [('scores.' + name, scores[name]) for name, _ in criteria
               if scores.get(name) is not None and as_number(scores[name]) is None]
    if invalid:
        problems.append(invalid_message(invalid))
    return {name: as_number(scores[name]) for name, _ in criteria if scores.get(name) is not None}


def confidence_used(raw, sources, flags):
    """Turn a percent into a fraction, then cap unsourced confidence above 0.5."""
    value = raw / 100 if raw > 1 else raw
    if 1 < raw <= 10:
        flags.append(f'confidence {fmt(raw)} was read as {fmt(raw)}% ({fmt(value)}); '
                     'enter a 0-10 rating as a fraction instead, such as 0.8 for 8')
    if value > CONFIDENCE_CAP and not has_source(sources.get('confidence')):
        shown = fmt(raw) if raw == value else f'{fmt(raw)} ({fmt(value)})'
        flags.append(f'confidence {shown} has no written source; scored at the {fmt(CONFIDENCE_CAP)} cap')
        value = CONFIDENCE_CAP
    return value


def flag_unsized(label, sources, flags):
    if not has_source(sources.get('effort')):
        flags.append(f'{label} has no engineering source in sources.effort; '
                     'do not publish this ranking until engineering sizes it')


def flag_importance(sources, flags):
    if not has_source(sources.get('importance')):
        flags.append('importance has no customer source in sources.importance; '
                     'treat this score as a hypothesis built on internal estimates')


def compute(framework, values, criteria, sources, flags):
    """Return (score, arithmetic, impact) for one item; impact is None outside ice and rice."""
    if framework == 'ice':
        impact, ease = values['impact'], values['ease']
        confidence = confidence_used(values['confidence'], sources, flags)
        return impact * confidence * ease, f'{fmt(impact)} * {fmt(confidence)} * {fmt(ease)}', impact
    if framework == 'rice':
        reach, impact, effort = values['reach'], values['impact'], values['effort']
        confidence = confidence_used(values['confidence'], sources, flags)
        if not any(abs(impact - step) < 1e-9 for step in RICE_IMPACT_SCALE):
            scale = ', '.join(fmt(step) for step in RICE_IMPACT_SCALE)
            flags.append(f'impact {fmt(impact)} is off the RICE scale ({scale})')
        flag_unsized('effort', sources, flags)
        arithmetic = f'({fmt(reach)} * {fmt(impact)} * {fmt(confidence)}) / {fmt(effort)}'
        return reach * impact * confidence / effort, arithmetic, impact
    if framework == 'odi':
        importance, satisfaction = values['importance'], values['satisfaction']
        flag_importance(sources, flags)
        arithmetic = f'{fmt(importance)} + max({fmt(importance)} - {fmt(satisfaction)}, 0)'
        return importance + max(importance - satisfaction, 0), arithmetic, None
    if framework == 'opportunity':
        importance, satisfaction = values['importance'], values['satisfaction']
        if satisfaction > 1:
            converted = satisfaction / 10
            flags.append(f'satisfaction {fmt(satisfaction)} looked like a 0-10 rating and was converted to {fmt(converted)}')
            satisfaction = converted
        flag_importance(sources, flags)
        return importance * (1 - satisfaction), f'{fmt(importance)} * (1 - {fmt(satisfaction)})', None
    if framework == 'wsjf':
        size = values['job_size']
        parts = [values['business_value'], values['time_criticality'], values['risk_reduction']]
        flag_unsized('job size', sources, flags)
        arithmetic = '(' + ' + '.join(fmt(part) for part in parts) + f') / {fmt(size)}'
        return sum(parts) / size, arithmetic, None
    terms = [(weight, values[name]) for name, weight in criteria]
    arithmetic = ' + '.join(f'{fmt(weight)} * {fmt(score)}' for weight, score in terms)
    return sum(weight * score for weight, score in terms), arithmetic, None


def assess(item, position, framework, criteria, seen):
    """Return (row, impact, None) for a scored item, or (None, None, message) for a rejected one."""
    if not isinstance(item, dict):
        return None, None, f'item {position}: expected a JSON object, found {kind_of(item)}'
    problems = []
    key = as_text(item.get('id'))
    if key and key in seen:
        label = f'{key} (item {position})'
        problems.append(f'same id as item {seen[key]}; later duplicates are rejected')
    elif key:
        label = key
        seen[key] = position
    else:
        title = as_text(item.get('title'))
        label = f'"{title}" (item {position})' if title else f'item {position}'
        problems.append('id is missing' if item.get('id') is None else 'id must be a non-empty string or a number')
    sources = item.get('sources')
    if sources is None:
        sources = {}
    elif not isinstance(sources, dict):
        problems.append(f'sources must be an object, found {kind_of(sources)}')
    if framework == 'weighted':
        values = read_scores(item, criteria, problems)
    else:
        values = read_fields(item, REQUIRED_FIELDS[framework], problems)
    positive = POSITIVE_FIELD.get(framework)
    if positive and values.get(positive) is not None and values[positive] <= 0:
        problems.append(f'{positive} must be greater than 0, found {fmt(values[positive])}')
    if problems:
        return None, None, f'{label}: ' + '; '.join(problems)
    flags = []
    score, arithmetic, impact = compute(framework, values, criteria, sources, flags)
    job = as_text(item.get('job')) or as_text(item.get('problem'))
    if not job:
        flags.append('no job or problem stated; rank the problem first (see frame-jobs-to-be-done)')
    # Adding 0.0 turns a rounded -0.0 into 0.0 for the report.
    score = round(score, 2) + 0.0
    row = {'id': item['id'], 'title': as_text(item.get('title')), 'job': job, 'score': score,
           'formula': f'{arithmetic} = {fmt(score)}', 'flags': flags, 'rank': 0}
    return row, impact, None


def rank(items, framework, criteria, weight_note):
    """Score every item and assemble the report object."""
    scored, errors, seen = [], [], {}
    for position, item in enumerate(items, 1):
        row, impact, problem = assess(item, position, framework, criteria, seen)
        if problem:
            errors.append(problem)
        else:
            scored.append((row, impact))
    notes = [weight_note] if weight_note else []
    impacts = [impact for _, impact in scored if impact is not None]
    if framework in ('ice', 'rice') and len(impacts) >= TOP_IMPACT_MINIMUM:
        top = max(impacts)
        count = sum(1 for impact in impacts if impact == top)
        if count / len(impacts) > TOP_IMPACT_SHARE:
            notes.append(f'{count} of {len(impacts)} scored items ({round(100 * count / len(impacts))}%) '
                         f'share the highest impact value ({fmt(top)}). Recalibrate: reserve the top value '
                         'for items whose impact rests on behavior or revenue data.')
    ranking = [row for row, _ in scored]
    ranking.sort(key=lambda row: -row['score'])
    for number, row in enumerate(ranking, 1):
        row['rank'] = number
    groups = {}
    for row in ranking:
        groups.setdefault(row['score'], []).append(as_text(row['id']))
    tied = [f'{fmt(score)} ({", ".join(ids)})' for score, ids in groups.items() if len(ids) > 1]
    if tied:
        notes.append('Tied scores: ' + '; '.join(tied) + '. The formula leaves ties unresolved; settle each '
                     'in the decision meeting using an explicit tiebreaker, for example closer strategic fit or less effort.')
    return {'framework': framework, 'ranking': ranking, 'errors': errors, 'notes': notes}


def cell(text):
    return ' '.join(str(text).split()).replace('|', '\\|')


def render_markdown(report):
    lines = [f'# Priority proposal: {DISPLAY_NAMES[report["framework"]]}', '',
             'Proposal only: the decision owner sets the final order; MoSCoW values stay with capture-requirements.', '']
    if report['ranking']:
        lines += ['| Rank | ID | Title | Score | Formula | Flags |', '| --- | --- | --- | --- | --- | --- |']
        for row in report['ranking']:
            values = [row['rank'], as_text(row['id']), row['title'], fmt(row['score']),
                      '`' + row['formula'] + '`', '; '.join(row['flags']) or 'none']
            lines.append('| ' + ' | '.join(cell(value) for value in values) + ' |')
        lines.append('')
    else:
        lines += ['No candidate could be scored; the rejected items below give the reasons.', '']
    if report['notes']:
        lines += ['## Notes', ''] + ['- ' + note for note in report['notes']] + ['']
    if report['errors']:
        lines += ['## Rejected items', ''] + ['- ' + error for error in report['errors']] + ['']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Score candidate items and print a ranked proposal.')
    parser.add_argument('candidates', help='JSON file holding the candidate items')
    parser.add_argument('--framework', required=True, choices=FRAMEWORKS, help='scoring method to apply')
    parser.add_argument('--format', choices=('markdown', 'json'), default='markdown',
                        help='report format; markdown is the default')
    parser.add_argument('--output', metavar='PATH', help='write the report to PATH instead of standard output')
    args = parser.parse_args(argv)
    try:
        items, raw_criteria = load(args.candidates)
        criteria, weight_note = read_criteria(raw_criteria) if args.framework == 'weighted' else (None, None)
        report = rank(items, args.framework, criteria, weight_note)
        if args.format == 'json':
            text = json.dumps({key: report[key] for key in REPORT_KEYS}, indent=2, ensure_ascii=False) + '\n'
        else:
            text = render_markdown(report)
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as handle:
                    handle.write(text)
            except OSError as exc:
                raise InputError(f'cannot write {args.output}: {reason(exc)}')
            print(f'report written to {args.output}', file=sys.stderr)
        else:
            sys.stdout.write(text)
    except InputError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    sys.exit(main())
