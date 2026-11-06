#!/usr/bin/env python3
"""Exercise both shipped generators with synthetic projects; no Salesforce calls."""
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = runpy.run_path(str(ROOT / 'skills/deliver-salesforce-change/scripts/gen_permset_selftest.py'))
NS = {'s': 'http://soap.sforce.com/2006/04/metadata'}


class PermsetBehavior(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='permset-behavior-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.projects = []
        self.counter = 0
        for skill in ('deliver-salesforce-change', 'configure-salesforce-project'):
            project = self.base / skill
            metadata = Path(FIXTURE['build_fixture'](str(project)))
            script = ROOT / 'skills' / skill / 'references/tools/gen-permset.py'
            self.projects.append((project, metadata, script))

    def run_tool(self, project, script, *args, env=None):
        self.counter += 1
        result = subprocess.run([sys.executable, str(script), *map(str, args)], cwd=project,
                                env=env, text=True, capture_output=True, timeout=30)
        (self.base / f'command-{self.counter:03}.json').write_text(json.dumps({
            'argv': list(map(str, args)), 'project': project.name, 'exitCode': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}, indent=2))
        return result

    def configure(self, project, **changes):
        path = project / 'config/permset-gen.json'
        cfg = json.loads(path.read_text())
        cfg.update(changes)
        path.write_text(json.dumps(cfg))

    def output(self, project, script):
        path = self.base / f'{project.name}-{self.counter}.xml'
        result = self.run_tool(project, script, '--out', path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return ET.parse(path).getroot()

    def test_xml_escaping_and_standard_exclusion(self):
        for project, _, script in self.projects:
            self.configure(project, label='R&D <Review>', description='A & B < C',
                           exclude_objects=['Account'])
            xml = self.output(project, script)
            self.assertEqual(xml.find('s:label', NS).text, 'R&D <Review>')
            self.assertEqual(xml.find('s:description', NS).text, 'A & B < C')
            self.assertNotIn('Account', [x.text for x in xml.findall('s:objectPermissions/s:object', NS)])

    def test_fields_split_across_packages_are_preserved(self):
        for project, metadata, script in self.projects:
            package = project / 'extra/main/default'
            field = package / 'objects/Widget__c/fields/Extra__c.field-meta.xml'
            field.parent.mkdir(parents=True)
            field.write_text(FIXTURE['FIELD'] % ('Extra__c', '<type>Text</type>'))
            (project / 'sfdx-project.json').write_text(json.dumps({'packageDirectories': [
                {'path': 'force-app', 'default': True}, {'path': 'extra'}]}))
            xml = self.output(project, script)
            names = [x.text for x in xml.findall('s:fieldPermissions/s:field', NS)]
            self.assertIn('Widget__c.XID__c', names)
            self.assertIn('Widget__c.Extra__c', names)
            field.rename(field.with_name('XID__c.field-meta.xml'))
            conflict = self.run_tool(project, script)
            self.assertEqual(conflict.returncode, 2)
            self.assertIn('conflicting metadata', conflict.stderr)

    def test_bad_paths_and_config_types_refuse(self):
        for project, _, script in self.projects:
            config = project / 'config/permset-gen.json'
            good = config.read_text()
            for changes in ({'output': '../escape.xml'}, {'output': '/tmp/escape.xml'},
                            {'api_name': '../escape'}, {'output': 'config/permset-gen.json'},
                            {'derive': {'fields': True}},
                            {'derive': {'tabs': 'false'}}, {'no_delete': 'Account'},
                            {'description': 20}):
                config.write_text(good)
                self.configure(project, **changes)
                result = self.run_tool(project, script)
                self.assertEqual(result.returncode, 2, (changes, result.stdout, result.stderr))
            self.assertFalse((self.base / 'escape.xml').exists())

    def test_preview_preserves_files_and_rejects_project_targets(self):
        for project, _, script in self.projects:
            output = self.base / (project.name + '-existing.xml')
            output.write_text('preserve me')
            for target in (output, project / 'new.xml'):
                result = self.run_tool(project, script, '--out', target)
                self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(), 'preserve me')
            link = self.base / (project.name + '-link.xml')
            link.symlink_to(output)
            self.assertEqual(self.run_tool(project, script, '--out', link).returncode, 2)
            self.assertEqual(output.read_text(), 'preserve me')

    def test_unverified_git_refuses_write(self):
        fakebin = self.base / 'fakebin'
        fakebin.mkdir()
        fakegit = fakebin / 'git'
        fakegit.write_text('#!/bin/sh\nexit 1\n')
        fakegit.chmod(0o755)
        for project, metadata, script in self.projects:
            env = {**os.environ, 'PATH': str(fakebin)}
            result = self.run_tool(project, script, '--write', env=env)
            self.assertEqual(result.returncode, 2)
            self.assertIn('verified Git worktree', result.stderr)
            self.assertFalse((metadata / 'permissionsets').exists())

    def test_package_escape_and_symlink_refuse(self):
        outside = self.base / 'outside'
        outside.mkdir()
        for project, metadata, script in self.projects:
            config = project / 'sfdx-project.json'
            good = config.read_text()
            config.write_text(json.dumps({'packageDirectories': [{'path': '../outside'}]}))
            self.assertEqual(self.run_tool(project, script).returncode, 2)
            config.write_text(good)
            field = metadata / 'objects/Widget__c/fields/Escape__c.field-meta.xml'
            secret = outside / (project.name + '.xml')
            secret.write_text(FIXTURE['FIELD'] % ('Escape__c', '<type>Text</type>'))
            field.symlink_to(secret)
            self.assertEqual(self.run_tool(project, script).returncode, 2)

    def test_malformed_metadata_fails_before_output(self):
        for project, metadata, script in self.projects:
            field = metadata / 'objects/Widget__c/fields/XID__c.field-meta.xml'
            field.write_text('<CustomField><type>Text</CustomField>')
            target = self.base / (project.name + '-bad.xml')
            result = self.run_tool(project, script, '--out', target)
            self.assertEqual(result.returncode, 2)
            self.assertIn('malformed metadata XML', result.stderr)
            self.assertFalse(target.exists())

    def test_argument_errors_and_external_init_refuse(self):
        for project, _, script in self.projects:
            for args in (('--out',), ('--tree',), ('--config',), ('--unexpected',),
                         ('--out', 'test.xml', '--write'),
                         ('--init', '--config', str(self.base / 'external.json'))):
                self.assertEqual(self.run_tool(project, script, *args).returncode, 2)
            self.assertFalse((self.base / 'external.json').exists())


if __name__ == '__main__':
    unittest.main()
