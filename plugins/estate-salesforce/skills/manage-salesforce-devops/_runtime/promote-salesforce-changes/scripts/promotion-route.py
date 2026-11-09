#!/usr/bin/env python3
"""Choose preparation from explicit stage IDs without contacting Salesforce."""
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current-stage-id', default='')
    parser.add_argument('--target-stage-id', required=True)
    parser.add_argument('--first-stage-id', required=True)
    args = parser.parse_args()
    if any(value != value.strip() or any(ord(c) < 32 for c in value)
           for value in (args.current_stage_id, args.target_stage_id, args.first_stage_id)):
        parser.error('stage IDs must not contain outer whitespace or control characters')
    if not args.target_stage_id.strip() or not args.first_stage_id.strip():
        parser.error('target-stage-id and first-stage-id must not be empty')
    if not args.current_stage_id:
        if args.target_stage_id == args.first_stage_id:
            result = {'action': 'skip', 'reason': 'development WI entering first linked stage without PipelineStageId'}
        else:
            print('BLOCKED: WI has no PipelineStageId and target is not the first linked stage; verify topology and WI state.', file=sys.stderr)
            return 1
    elif args.current_stage_id == args.target_stage_id:
        print('BLOCKED: current and target stages are identical.', file=sys.stderr)
        return 1
    else:
        result = {'action': 'prepare', 'reason': 'one-off promotion between existing pipeline stages'}
    print(json.dumps(result, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
