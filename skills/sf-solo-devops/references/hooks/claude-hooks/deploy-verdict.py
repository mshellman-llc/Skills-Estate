#!/usr/bin/env python3
"""Interpret a complete CLI JSON result without contacting an org."""
import json
import re
import shlex
import sys


def verdict(payload, command):
    try:
        data = json.loads(payload)
        args = shlex.split(command)
        result = data['result']
        target = []
        job = []
        for i, arg in enumerate(args):
            for names, dest in ((('--target-org', '-o'), target), (('--job-id', '-i'), job)):
                if arg in names:
                    dest.append(args[i + 1])
                elif any(arg.startswith(name + '=') for name in names):
                    dest.append(arg.split('=', 1)[1])
        if len(target) != 1 or not target[0] or target[0].startswith('-'):
            return 'UNKNOWN'
        result_id = result.get('id', '')
        if not re.fullmatch(r'0Af[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?', result_id):
            return 'UNKNOWN'
        if len(job) > 1 or (job and job[0] != result_id):
            return 'UNKNOWN'
        status = result.get('status')
        if status in ('Failed', 'Canceled'):
            return 'FAILED'
        if (type(data.get('status')) is not int or data['status'] != 0 or
                status != 'Succeeded' or result.get('done') is not True or
                type(result.get('checkOnly')) is not bool):
            return 'UNKNOWN'
        check_only = result['checkOnly']
        requested_check = '--dry-run' in args or 'validate' in args
        if requested_check and not check_only:
            return 'UNKNOWN'
        if 'start' in args and not requested_check and check_only:
            return 'UNKNOWN'
        return 'VALIDATE' if check_only else 'DEPLOY'
    except (ValueError, TypeError, KeyError, IndexError, AttributeError):
        return 'UNKNOWN'


if __name__ == '__main__':
    print(verdict(sys.stdin.read(), sys.argv[1] if len(sys.argv) == 2 else ''))
