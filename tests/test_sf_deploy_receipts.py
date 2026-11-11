#!/usr/bin/env python3
"""Check hook evidence decisions with synthetic responses and no external calls."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / 'skills/sf-solo-devops/references/hooks/claude-hooks'
verdict = runpy.run_path(str(HOOKS / 'deploy-verdict.py'))['verdict']
JOB = '0Af000000000001'


def result(check=True, **overrides):
    data = {'id': JOB, 'status': 'Succeeded', 'done': True, 'checkOnly': check}
    data.update(overrides)
    return {'status': 0, 'result': data}


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sf-receipt-test-')
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)

    def test_structured_verdict_cases(self):
        cases = [
            ('Status: Succeeded', 'sf project deploy start --target-org example', 'UNKNOWN'),
            (result(), 'sf project deploy start --dry-run --target-org example --json', 'VALIDATE'),
            (result(False), 'sf project deploy start --target-org example --json', 'DEPLOY'),
            (result(False), 'sf project deploy start --dry-run --target-org example', 'UNKNOWN'),
            (result(True), 'sf project deploy validate --target-org example', 'VALIDATE'),
            (result(False), 'sf project deploy start', 'UNKNOWN'),
            (result(False, checkOnly='false'), 'sf project deploy start --target-org example', 'UNKNOWN'),
            (result(False, done=False), 'sf project deploy start --target-org example', 'UNKNOWN'),
            (result(False), 'sf project deploy report --target-org example --job-id 0Af000000000002', 'UNKNOWN'),
            (result(False, status='Failed'), 'sf project deploy start --target-org example', 'FAILED'),
            (result(False, id='not-a-job'), 'sf project deploy start --target-org example', 'UNKNOWN'),
        ]
        for i, (payload, command, expected) in enumerate(cases):
            text = payload if isinstance(payload, str) else json.dumps(payload)
            actual = verdict(text, command)
            (self.path / f'verdict-{i}.json').write_text(json.dumps({
                'payload': payload, 'command': command, 'expected': expected, 'actual': actual}, indent=2))
            self.assertEqual(actual, expected)

    def project(self):
        project = self.path / 'project'
        project.mkdir()
        def git(*args):
            return subprocess.run(['git', *args], cwd=project, check=True, capture_output=True, text=True)
        git('init', '-q', '-b', 'main')
        git('config', 'user.name', 'Synthetic test')
        git('config', 'user.email', 'test@example.invalid')
        (project / 'force-app').mkdir()
        (project / 'force-app/example.txt').write_text('fixture')
        git('add', 'force-app')
        git('commit', '-qm', 'fixture refs #7')
        return project, git

    def invoke(self, project, hook, payload, command, filename):
        fake = self.path / 'bin'
        fake.mkdir(exist_ok=True)
        for tool in ('sf', 'gh'):
            executable = fake / tool
            executable.write_text('#!/bin/sh\ntouch "' + str(self.path / (tool + '-called')) + '"\nexit 1\n')
            executable.chmod(0o755)
        env = {**os.environ, 'PATH': str(fake) + ':' + os.environ['PATH'], 'SOLO_GITHUB_UPDATES': '0'}
        event = {'tool_input': {'command': command}, 'tool_response': {
            'stdout': json.dumps(payload) if isinstance(payload, dict) else payload, 'stderr': ''}}
        process = subprocess.run(['bash', str(HOOKS / hook)], cwd=project, env=env,
                                 input=json.dumps(event), capture_output=True, text=True, timeout=10)
        (self.path / filename).write_text(json.dumps({'event': event, 'exitCode': process.returncode,
            'stdout': process.stdout, 'stderr': process.stderr}, indent=2))
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertFalse((self.path / 'sf-called').exists())
        self.assertFalse((self.path / 'gh-called').exists())

    def test_dirty_source_is_not_credited_to_commit(self):
        project, _ = self.project()
        (project / 'force-app/example.txt').write_text('uncommitted')
        self.invoke(project, 'record-validate.sh', result(),
            'sf project deploy start --dry-run --target-org example --json', 'dirty.json')
        self.assertFalse((project / '.claude/.validate-log').exists())

    def test_clean_validation_is_recorded_without_org_query(self):
        project, git = self.project()
        sha = git('rev-parse', 'HEAD').stdout.strip()
        self.invoke(project, 'record-validate.sh', result(),
            'sf project deploy validate --target-org example --json', 'validate.json')
        self.assertIn(sha, (project / '.claude/.validate-log').read_text())

    def test_text_cannot_create_deployment_proof(self):
        project, _ = self.project()
        self.invoke(project, 'auto-label-deploy.sh', 'Status: Succeeded',
            'sf project deploy start --target-org example --json', 'text.json')
        self.assertFalse((project / '.claude/.deploy-log').exists())

    def test_success_is_recorded_locally_with_no_external_messages(self):
        project, git = self.project()
        sha = git('rev-parse', 'HEAD').stdout.strip()
        self.invoke(project, 'auto-label-deploy.sh', result(False),
            'sf project deploy start --target-org example --json', 'deploy.json')
        self.assertIn(sha + ' ' + JOB, (project / '.claude/.deploy-log').read_text())


if __name__ == '__main__':
    unittest.main()
