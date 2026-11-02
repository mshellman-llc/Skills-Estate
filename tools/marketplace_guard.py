"""Require automated verification of the exact source about to be published."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PENDING_EXIT = 75


class VerificationPending(ValueError):
    """Verification has not finished, so a later check can still pass."""


def matching_runs(revision, payload):
    return [run for run in payload.get('workflow_runs', [])
            if run.get('head_sha') == revision and run.get('head_branch') == 'main'
            and run.get('path') == '.github/workflows/verify.yml']


def verified_run(revision, payload):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Publication needs a full source commit SHA')
    matches = matching_runs(revision, payload)
    if not matches:
        raise ValueError('Publication blocked: no verification run for this exact main revision')
    latest = max(matches, key=lambda run: (run.get('id', 0), run.get('run_attempt', 0)))
    if latest.get('status') != 'completed':
        raise VerificationPending('Publication waiting: latest verification for this revision has not finished')
    if latest.get('conclusion') != 'success':
        raise ValueError('Publication blocked: latest verification for this revision is not successful')
    return latest['id']


def generated_only_parent(root, revision):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args])
    if git('rev-parse', 'HEAD').decode().strip() != revision:
        raise ValueError('Publication revision differs from the checked-out commit')
    parents = git('rev-list', '--parents', '-n', '1', revision).decode().split()[1:]
    if len(parents) != 1:
        raise ValueError('Generated publication fallback requires exactly one parent')
    parent = parents[0]
    changed = git('diff', '--name-only', '--no-renames', '-z', parent, revision).decode().split('\0')[:-1]
    if not changed or any(not (name.startswith('plugins/') or name == '.claude-plugin/marketplace.json') for name in changed):
        raise VerificationPending('Publication waiting: no verification run has started for this revision')
    for commit in (parent, revision):
        records = git('ls-tree', '-r', '-z', commit, '--', 'plugins', '.claude-plugin/marketplace.json').split(b'\0')
        if any(row and row.split(b' ', 1)[0] not in {b'100644', b'100755'} for row in records):
            raise ValueError('Generated publication files cannot be symlinks or submodules')
    return parent


def verify_publication(root, revision, payload):
    verified = revision
    if not matching_runs(revision, payload):
        verified = generated_only_parent(root, revision)
    return {'verified_run': verified_run(verified, payload),
            'checkout_commit': revision, 'verified_source_commit': verified}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('revision')
    parser.add_argument('runs', type=Path, nargs='+')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    payload = {'workflow_runs': [run for file in args.runs
                                for run in json.loads(file.read_text()).get('workflow_runs', [])]}
    try:
        print(json.dumps(verify_publication(args.root, args.revision, payload)))
    except VerificationPending as pending:
        print(pending, file=sys.stderr)
        raise SystemExit(PENDING_EXIT)
