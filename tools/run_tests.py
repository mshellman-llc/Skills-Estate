#!/usr/bin/env python3
"""Run deterministic tests by default; report deferred integration and configuration checks."""
import argparse
from collections import Counter
import contextlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from test_capabilities import CAPABILITIES, ENVIRONMENT_KEY, preflight


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def collect(start=None):
    start = Path(start or ROOT / 'tests')
    loader = unittest.TestLoader()
    suite = loader.discover(str(start))
    tests = list(flatten(suite))
    duplicates = [name for name, count in Counter(test.id() for test in tests).items() if count > 1]
    if duplicates:
        raise ValueError('Duplicate test IDs: ' + ', '.join(duplicates))
    return tests


def requirement(test):
    method = getattr(test, getattr(test, '_testMethodName', ''), None)
    return getattr(method, 'estate_integration', None)


def configuration(test):
    method = getattr(test, getattr(test, '_testMethodName', ''), None)
    return getattr(method, 'estate_configuration', None)


@contextlib.contextmanager
def selected_environment(enabled):
    previous = os.environ.get(ENVIRONMENT_KEY)
    os.environ[ENVIRONMENT_KEY] = ','.join(sorted(enabled))
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(ENVIRONMENT_KEY, None)
        else:
            os.environ[ENVIRONMENT_KEY] = previous


def run(tests, enabled=(), stream=None):
    enabled = set(enabled)
    unknown = enabled - set(CAPABILITIES)
    if unknown:
        raise ValueError('Unknown integration capabilities: ' + ', '.join(sorted(unknown)))
    pending = [{'test': test.id(), 'capability': requirement(test)} for test in tests
               if requirement(test) and requirement(test) not in enabled]
    waiting = {item['test'] for item in pending}
    pending += [{'test': test.id(), 'configuration': configuration(test)[0]} for test in tests
                if configuration(test) and test.id() not in waiting and not configuration(test)[1]()]
    summary = {'selected_integrations': sorted(enabled), 'discovered': len(tests),
               'deferred': pending, 'deferred_count': len(pending)}
    with selected_environment(enabled):
        try:
            summary['preflight'] = [preflight(name) for name in sorted(enabled)]
        except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
            return {**summary, 'status': 'preflight_failed', 'error': str(error), 'executed': 0}, 2
        result = unittest.TextTestRunner(stream=stream or sys.stderr, verbosity=2).run(unittest.TestSuite(tests))
    deferred_ids = {item['test'] for item in pending}
    other_skips = [{'test': test.id(), 'reason': reason} for test, reason in result.skipped
                   if test.id() not in deferred_ids]
    summary.update(executed=result.testsRun - len(result.skipped),
                   passed=result.testsRun - len(result.skipped) - len(result.failures) - len(result.errors),
                   failures=len(result.failures), errors=len(result.errors), other_skips=other_skips,
                   status=('failed' if not result.wasSuccessful() else
                           'incomplete' if other_skips else
                           'passed_with_deferred' if pending else 'passed'))
    return summary, 0 if result.wasSuccessful() and not other_skips else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integration', action='append', choices=CAPABILITIES, default=[])
    parser.add_argument('--all-integrations', action='store_true')
    parser.add_argument('--list', action='store_true', help='List test requirements without running tests or preflight')
    parser.add_argument('--report', type=Path, help='Write the execution and deferred-check summary as JSON')
    args = parser.parse_args(argv)
    tests = collect()
    if args.list:
        summary = {'tests': [{'test': test.id(), 'capability': requirement(test)} for test in tests]}
        code = 0
    else:
        summary, code = run(tests, CAPABILITIES if args.all_integrations else args.integration)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
