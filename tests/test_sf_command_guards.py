#!/usr/bin/env python3
"""Run shipped hooks against synthetic events and fake executables only."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / 'skills/sf-solo-devops/references/hooks/claude-hooks'

class Guards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sf-hook-test-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.count = 0

    def invoke(self, command):
        self.count += 1
        event = json.dumps({'tool_input': {'command': command}})
        result = subprocess.run(['bash', str(HOOKS / 'guard-sf-flags.sh')], input=event,
                                text=True, capture_output=True, timeout=10)
        (self.path / f'event-{self.count}.json').write_text(json.dumps({
            'input': json.loads(event), 'exitCode': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}, indent=2))
        return result

    def test_local_preparation_does_not_need_org(self):
        for cmd in ('sf --version', 'sf project deploy start --help',
                    'sf project convert source --root-dir force-app --output-dir out',
                    'sf project generate project --name example',
                    'sf project generate manifest --source-dir force-app',
                    'python3 scripts/gen-permset.py --out /tmp/new.xml',
                    'echo "sf project deploy start"', 'sf config list'):
            self.assertEqual(self.invoke(cmd).returncode, 0, cmd)

    def test_org_operations_require_explicit_target(self):
        for cmd in ('sf project deploy start --dry-run', 'sf data query -q "SELECT Id FROM Organization"',
                    'sf project generate manifest --from-org test',
                    'sf project deploy start --target-org',
                    'sf project deploy start --target-org=',
                    'sf project deploy start --target-org a -o b'):
            self.assertEqual(self.invoke(cmd).returncode, 2, cmd)
        for cmd in ('sf project deploy start --dry-run --target-org confirmed',
                    'sf data query --target-org=confirmed --query "SELECT Id FROM Organization"',
                    '/usr/local/bin/sf project deploy report -o confirmed --job-id 0AfExample'):
            self.assertEqual(self.invoke(cmd).returncode, 0, cmd)

    def test_every_call_is_checked_and_latest_job_refused(self):
        for cmd in ('sf project deploy start; sf data query --target-org safe -q "SELECT Id FROM Organization"',
                    'sf project deploy report --target-org safe --use-most-recent',
                    'sf project deploy report --target-org safe --use-most-recent=true',
                    'sf project retrieve start --target-org safe --output-dir scratch'):
            self.assertEqual(self.invoke(cmd).returncode, 2, cmd)

    def test_deployment_guard_allows_policy_tests_and_refuses_unknown_checkout(self):
        commands = [
            ('sf project deploy start --dry-run --target-org confirmed --test-level RunLocalTests', 0),
            ('sf project deploy start --dry-run --target-org confirmed --test-level RunAllTestsInOrg', 0),
            ('sf project deploy validate --target-org confirmed --test-level RunLocalTests', 0),
            ('sf project deploy start --target-org confirmed --source-dir classes', 2),
            ('sf project deploy quick --target-org confirmed --job-id 0AfExample', 2),
        ]
        for i, (command, expected) in enumerate(commands):
            result = subprocess.run(['bash', str(HOOKS / 'guard-sf-deploy.sh')], cwd=self.path,
                input=json.dumps({'tool_input': {'command': command}}),
                text=True, capture_output=True, timeout=10)
            (self.path / f'deploy-guard-{i}.json').write_text(json.dumps({
                'command': command, 'exitCode': result.returncode, 'stderr': result.stderr}))
            self.assertEqual(result.returncode, expected, (command, result.stderr))

    def test_worktree_preparation_does_not_call_sf(self):
        # A fake CLI writes a sentinel if invoked. The hook must not call it,
        # even when the main checkout has an alias and a worktree has none.
        project = self.path / 'project'
        project.mkdir()
        def git(*args):
            subprocess.run(['git', *args], cwd=project, check=True, capture_output=True)
        git('init', '-q')
        git('config', 'user.email', 'test@example.invalid')
        git('config', 'user.name', 'Synthetic test')
        (project / 'README.md').write_text('Synthetic project\n')
        git('add', 'README.md')
        git('commit', '-qm', 'fixture')
        wt = self.path / 'worktree'
        git('worktree', 'add', '-q', str(wt), '-b', 'test-worktree')
        (project / '.sf').mkdir()
        (project / '.sf/config.json').write_text('{"target-org":"not-authorized"}')
        fake = self.path / 'bin'
        fake.mkdir()
        sentinel = self.path / 'sf-called'
        (fake / 'sf').write_text('#!/bin/sh\ntouch "' + str(sentinel) + '"\n')
        (fake / 'sf').chmod(0o755)
        result = subprocess.run(['bash', str(HOOKS / 'ensure-worktree-config.sh')], cwd=wt,
            env={**os.environ, 'PATH': str(fake) + ':' + os.environ['PATH']},
            input=json.dumps({'tool_input': {'command': 'sf project convert source'}}),
            text=True, capture_output=True, timeout=10)
        (self.path / 'prepare-result.json').write_text(json.dumps({
            'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}))
        self.assertEqual(result.returncode, 0)
        self.assertFalse(sentinel.exists())
        self.assertFalse((wt / '.sf').exists())

if __name__ == '__main__':
    unittest.main()
