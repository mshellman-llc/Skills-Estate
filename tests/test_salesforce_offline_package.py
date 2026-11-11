#!/usr/bin/env python3
"""Use an assembled skill from a separate directory, without Salesforce access."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from portable import assemble
from estate import runtime_dependencies


class OfflinePackage(unittest.TestCase):
    def test_new_project_preview_and_installed_hook_refusals(self):
        with tempfile.TemporaryDirectory(prefix='sf-offline-package-') as tmp:
            base = Path(tmp)
            package = base / 'skill'
            assemble(ROOT, 'sf-solo-devops', package, runtime_dependencies('sf-solo-devops'))
            project = base / 'project'
            project.mkdir()
            (project / 'sfdx-project.json').write_text(json.dumps({
                'packageDirectories': [{'path': 'force-app', 'default': True}]}))
            field = project / 'force-app/main/default/objects/Request__c/fields/Status__c.field-meta.xml'
            field.parent.mkdir(parents=True)
            field.write_text('<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">'
                             '<fullName>Status__c</fullName><type>Text</type><length>40</length></CustomField>')
            # Install the package's actual standalone generator and all helper files.
            (project / 'scripts').mkdir()
            shutil.copy2(package / 'references/tools/gen-permset.py', project / 'scripts/gen-permset.py')
            shutil.copytree(package / 'references/hooks/claude-hooks', project / '.claude/hooks')
            fakebin = base / 'bin'
            fakebin.mkdir()
            sentinel = base / 'unexpected-external-call'
            for name in ('sf', 'sfdx', 'gh'):
                path = fakebin / name
                path.write_text('#!/bin/sh\ntouch "' + str(sentinel) + '"\nexit 1\n')
                path.chmod(0o755)
            env = {**os.environ, 'PATH': str(fakebin) + ':' + os.environ['PATH']}
            def run(name, args, payload=None):
                result = subprocess.run(args, cwd=project, env=env, input=payload,
                                        capture_output=True, text=True, timeout=15)
                (base / (name + '.json')).write_text(json.dumps({
                    'command': args, 'exitCode': result.returncode, 'stdout': result.stdout,
                    'stderr': result.stderr}, indent=2))
                return result
            generator = [sys.executable, str(project / 'scripts/gen-permset.py')]
            self.assertEqual(run('init', generator + ['--init']).returncode, 0)
            preview = base / 'permissions-preview.xml'
            self.assertEqual(run('preview', generator + ['--out', str(preview)]).returncode, 0)
            tree = ET.parse(preview)
            self.assertIn('Request__c.Status__c', [node.text for node in tree.iter()
                                                 if node.tag.endswith('}field')])
            self.assertEqual(run('drift', generator + ['--fail-on-drift']).returncode, 3)
            preflight = package / '_runtime/org-preflight/scripts/preflight.py'
            receipt = base / 'no-org-receipt.json'
            self.assertEqual(run('preflight', [sys.executable, str(preflight),
                             '--expect', '00D000000000001', '--receipt', str(receipt)]).returncode, 2)
            self.assertEqual(json.loads(receipt.read_text())['state'], 'refused')
            guard = project / '.claude/hooks/guard-sf-flags.sh'
            for name, command, expected in (
                ('local', 'sf project convert source --root-dir force-app --output-dir output', 0),
                ('no-org', 'sf project deploy start --dry-run --json', 2)):
                self.assertEqual(run(name, ['bash', str(guard)], json.dumps({
                    'tool_input': {'command': command}})).returncode, expected)
            self.assertFalse(sentinel.exists())
            self.assertFalse((project / '.sf').exists())

if __name__ == '__main__':
    unittest.main()
