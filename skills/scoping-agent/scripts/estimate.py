#!/usr/bin/env python3
"""Calculate a sourced effort range without a CRM or an assumed rate card."""
import argparse
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sys

SCENARIOS = ('low', 'expected', 'high')


def number(value, label, positive=False):
    if isinstance(value, bool):
        raise ValueError(label + ' must be a number')
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(label + ' must be a number')
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise ValueError(label + ' must be finite and ' + ('positive' if positive else 'nonnegative'))
    return result


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' needs a source value')
    return value.strip()


def decimal_text(value):
    return format(value, 'f')


def records(value, label):
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError(label + ' must be a list of objects')
    return value


def estimate(model):
    if not isinstance(model, dict):
        raise ValueError('The scope model must be a JSON object')
    supported = {'source', 'currency', 'rates', 'items', 'capacity', 'assumptions', 'exclusions'}
    if set(model) - supported:
        raise ValueError('Unsupported scope fields: ' + ', '.join(sorted(set(model) - supported)))
    for key in ('assumptions', 'exclusions'):
        if not isinstance(model.get(key, []), list) or any(not isinstance(v, str) or not v.strip() for v in model.get(key, [])):
            raise ValueError(key + ' must contain text entries')
    source = model.get('source') or {}
    if not isinstance(source, dict):
        raise ValueError('source must be an object')
    reference = text(source.get('reference'), 'source.reference')
    revision = text(source.get('revision'), 'source.revision')
    rates = {}
    for row in records(model.get('rates', []), 'rates'):
        role = text(row.get('role'), 'rate role')
        if role in rates:
            raise ValueError('Duplicate rate role: ' + role)
        rates[role] = {'rate': number(row.get('rate'), role + ' rate'),
                       'source': text(row.get('source'), role + ' rate source')}
    currency = text(model.get('currency'), 'currency') if rates else None
    rows = model.get('items')
    if not isinstance(rows, list) or not rows:
        raise ValueError('items must contain the scoped work')
    totals = {key: {'hours': Decimal(0), 'fee': Decimal(0)} for key in SCENARIOS}
    by_role = {}
    output = []
    seen = set()
    for item in records(rows, 'items'):
        item_id = text(item.get('id'), 'item ID')
        if item_id in seen:
            raise ValueError('Duplicate item ID: ' + item_id)
        seen.add(item_id)
        name = text(item.get('name'), item_id + ' name')
        description = text(item.get('description'), item_id + ' description')
        item_source = text(item.get('source'), item_id + ' source')
        status = item.get('status', 'estimated')
        if status not in ('estimated', 'unestimated'):
            raise ValueError(item_id + ' status must be estimated or unestimated')
        if status == 'unestimated':
            if 'allocations' in item and item['allocations'] != []:
                raise ValueError(item_id + ' is unestimated and cannot carry allocations')
            discovery = text(item.get('discovery_needed'), item_id + ' discovery_needed')
            basis = text(item['basis'], item_id + ' estimate basis') if 'basis' in item else None
            output.append({'id': item_id, 'name': name, 'description': description,
                           'source': item_source, 'status': status, 'basis': basis,
                           'discovery_needed': discovery, 'scenarios': None})
            continue
        basis = text(item.get('basis'), item_id + ' estimate basis')
        allocations = item.get('allocations')
        if not isinstance(allocations, list) or not allocations:
            raise ValueError(item_id + ' needs role-hour allocations')
        scenarios = {key: {'hours': Decimal(0), 'fee': Decimal(0)} for key in SCENARIOS}
        roles_seen = set()
        for allocation in records(allocations, item_id + ' allocations'):
            role = text(allocation.get('role'), item_id + ' role')
            if role in roles_seen:
                raise ValueError(item_id + ' repeats role ' + role)
            roles_seen.add(role)
            if rates and role not in rates:
                raise ValueError('No sourced rate for role: ' + role)
            supplied = allocation.get('hours')
            if not isinstance(supplied, dict) or set(supplied) != set(SCENARIOS):
                raise ValueError(item_id + ' needs low, expected and high hours for ' + role)
            hours = {key: number(supplied[key], item_id + ' ' + role + ' ' + key) for key in SCENARIOS}
            if not hours['low'] <= hours['expected'] <= hours['high']:
                raise ValueError(item_id + ' has an unordered hour range')
            role_hours = by_role.setdefault(role, {key: Decimal(0) for key in SCENARIOS})
            for key in SCENARIOS:
                fee = hours[key] * rates[role]['rate'] if rates else Decimal(0)
                scenarios[key]['hours'] += hours[key]
                scenarios[key]['fee'] += fee
                role_hours[key] += hours[key]
        for key in SCENARIOS:
            for field in ('hours', 'fee'):
                totals[key][field] += scenarios[key][field]
        output.append({'id': item_id, 'name': name, 'description': description,
                       'basis': basis, 'source': item_source, 'status': status,
                       'scenarios': {key: {'hours': decimal_text(v['hours']), 'fee': decimal_text(v['fee']) if rates else None}
                                     for key, v in scenarios.items()}})
    capacity = {}
    for row in records(model.get('capacity', []), 'capacity'):
        role = text(row.get('role'), 'capacity role')
        if role in capacity or role not in by_role:
            raise ValueError('Duplicate or unknown capacity role: ' + role)
        people = number(row.get('people'), role + ' people', positive=True)
        weekly = number(row.get('hours_per_person_week'), role + ' weekly hours', positive=True)
        availability = number(row.get('availability'), role + ' availability', positive=True)
        if availability > 1:
            raise ValueError('Availability cannot exceed 1 for ' + role)
        capacity[role] = people * weekly * availability
    bounds = None
    if capacity:
        missing = set(by_role) - set(capacity)
        if missing:
            raise ValueError('Capacity does not cover scoped roles: ' + ', '.join(sorted(missing)))
        bounds = {key: decimal_text(max(by_role[role][key] / capacity[role] for role in by_role))
                  for key in SCENARIOS}
    complete = all(item['status'] == 'estimated' for item in output)
    subtotal = ({key: {'hours': decimal_text(v['hours']), 'fee': decimal_text(v['fee']) if rates else None}
                 for key, v in totals.items()} if by_role else None)
    return {'format': 2, 'status': 'working-estimate' if complete else 'incomplete-estimate',
            'source': {'reference': reference, 'revision': revision}, 'currency': currency,
            'items': output, 'totals_complete': complete,
            'totals': subtotal if complete else None, 'estimated_subtotal': subtotal,
            'role_hours': {role: {key: decimal_text(v) for key, v in values.items()}
                           for role, values in by_role.items()},
            'rates': [{'role': role, 'rate': decimal_text(v['rate']), 'source': v['source']}
                      for role, v in rates.items()],
            'capacity_lower_bound_weeks': bounds, 'capacity_scope': 'estimated-items',
            'rounding': 'unrounded decimal amounts',
            'assumptions': model.get('assumptions', []), 'exclusions': model.get('exclusions', [])}


def markdown(result):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    total = result['estimated_subtotal']
    priced = result['currency'] is not None
    columns = '| Scenario | Hours |' + (' Fee (' + cell(result['currency']) + ') |' if priced else '')
    divider = '| --- | ---: |' + (' ---: |' if priced else '')
    lines = ['# Project estimate', '',
        'Working estimate from ' + result['source']['reference'] + ', revision ' + result['source']['revision'] + '.', '']
    if not result['totals_complete']:
        lines += ['Some scope remains unestimated. Full-project hours and price are withheld.', '']
    if total is not None:
        lines += ['## ' + ('Scenario totals' if result['totals_complete'] else 'Estimated work subtotal'), '', columns, divider]
        for key in SCENARIOS:
            lines.append('| ' + key.capitalize() + ' | ' + total[key]['hours'] + ' |' +
                         (' ' + total[key]['fee'] + ' |' if priced else ''))
    else:
        lines += ['No work has an effort estimate yet.', '']
    lines += ['', '## Scope and estimate basis', '']
    for item in result['items']:
        lines += ['### ' + item['name'], '', item['description'], '',
                  '- Item ID: ' + item['id'], '- Source: ' + item['source']]
        if item['basis'] is not None:
            lines.append('- Estimate basis: ' + item['basis'])
        if item['status'] == 'unestimated':
            lines += ['- Status: unestimated', '- Discovery needed: ' + item['discovery_needed'], '']
            continue
        lines += ['', columns, divider]
        for key in SCENARIOS:
            values = item['scenarios'][key]
            lines.append('| ' + key.capitalize() + ' | ' + values['hours'] + ' |' +
                         (' ' + values['fee'] + ' |' if priced else ''))
        lines.append('')
    if result['role_hours']:
        lines += ['## Role effort', '', '| Role | Low hours | Expected hours | High hours |',
                  '| --- | ---: | ---: | ---: |']
        for role, hours in result['role_hours'].items():
            lines.append('| ' + cell(role) + ' | ' + ' | '.join(hours[key] for key in SCENARIOS) + ' |')
        lines.append('')
    if result['rates']:
        lines += ['## Supplied rates', '', '| Role | Rate (' + cell(result['currency']) + '/hour) | Source |',
                  '| --- | ---: | --- |']
        for rate in result['rates']:
            lines.append('| ' + cell(rate['role']) + ' | ' + rate['rate'] + ' | ' + cell(rate['source']) + ' |')
        lines.append('')
    if result['capacity_lower_bound_weeks']:
        lines += ['## Capacity', '',
            'These workload bounds cover estimated items only. Dependencies and waiting time may extend the schedule.', '',
            '| Scenario | Minimum weeks at supplied capacity |', '| --- | ---: |']
        for key in SCENARIOS:
            lines.append('| ' + key.capitalize() + ' | ' + result['capacity_lower_bound_weeks'][key] + ' |')
        lines.append('')
    for key in ('assumptions', 'exclusions'):
        if result[key]:
            lines += ['## ' + key.capitalize(), '']
            lines += ['- ' + str(item) for item in result[key]]
            lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        output = args.output
        document = output.with_suffix('.md')
        if output.suffix != '.json' or output == args.source or output.exists() or document.exists():
            raise ValueError('Choose an unused .json output path; existing files are preserved')
        raw = args.source.read_bytes()
        result = estimate(json.loads(raw))
        result['input_sha256'] = hashlib.sha256(raw).hexdigest()
        result['calculator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        rendered = markdown(result)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('x') as stream:
            stream.write(json.dumps(result, indent=2) + '\n')
        with document.open('x') as stream:
            stream.write(rendered)
        print(json.dumps({'estimate': str(output), 'document': str(document), 'status': result['status']}))
        return 0
    except (OSError, ValueError, TypeError, KeyError, InvalidOperation) as exc:
        print('Estimate could not be calculated: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
