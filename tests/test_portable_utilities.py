"""Portable adapters require caller context and leave private hosts untouched."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PortableUtilityTests(unittest.TestCase):
    def setUp(self):
        self.health = load('portable_health', ROOT / 'skills/beastmode-health/scripts/collect_evidence.py')

    def test_unconfigured_health_template_never_reads_a_personal_store(self):
        config = json.loads((ROOT / 'skills/beastmode-health/references/evidence-index.json').read_text())
        with patch.object(self.health.sqlite3, 'connect') as connect, patch.object(self.health.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'explicitly configured absolute path'):
                self.health.collect(config)
            connect.assert_not_called()
            run.assert_not_called()
        for value in ('', ' ', 'relative/runtime'):
            config['runtimeRoot'] = value
            with self.assertRaisesRegex(ValueError, 'absolute path'):
                self.health.collect(config)

    def test_explicit_health_runtime_preserves_backup_checks_and_no_implicit_jobs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'backups').mkdir()
            backup = root / 'backups/accepted-3.enc'
            backup.write_bytes(b'synthetic encrypted backup fixture')
            digest = hashlib.sha256(backup.read_bytes()).hexdigest()
            (root / 'manifest.json').write_text(json.dumps({'generation': 3}))
            dbpath = root / 'index.sqlite'
            with sqlite3.connect(dbpath) as db:
                db.executescript('CREATE TABLE settings(key TEXT, value TEXT); CREATE TABLE bridge(data TEXT); CREATE TABLE jobs(kind TEXT,state TEXT,started TEXT);')
                db.execute('INSERT INTO settings VALUES (?,?)', ('last_backup', json.dumps({'destination': str(backup), 'sha256': digest, 'generation': 3, 'at': '2026-01-01T00:00:00Z', 'offService': False})))
                db.execute('INSERT INTO settings VALUES (?,?)', ('last_restore', json.dumps({'backupHash': digest, 'generation': 3, 'state': 'passed', 'at': '2026-01-01T00:00:00Z'})))
            before = dbpath.read_bytes()
            config = {'schemaVersion': 2, 'runtimeRoot': str(root), 'bridgeMaxAgeSeconds': 900,
                      'skillEntrypoints': [], 'launchdJobs': [], 'mountRoots': []}
            with patch.object(self.health.subprocess, 'run') as run:
                report = self.health.collect(config)
                run.assert_not_called()
            rows = {row['area']: row for row in report['rows']}
            self.assertEqual('verified-now', rows['local-backup']['status'])
            self.assertEqual('verified-now', rows['restore']['status'])
            self.assertEqual('not-rechecked', rows['skill-links']['status'])
            self.assertEqual('not-rechecked', rows['launchd']['status'])
            self.assertEqual(before, dbpath.read_bytes())
            backup.write_bytes(b'changed synthetic fixture')
            rows = {row['area']: row for row in self.health.collect(config)['rows']}
            self.assertEqual('needs-attention', rows['local-backup']['status'])
            self.assertEqual('needs-attention', rows['restore']['status'])

    def test_health_cli_requires_an_explicit_configuration(self):
        script = ROOT / 'skills/beastmode-health/scripts/collect_evidence.py'
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertEqual(2, result.returncode)
        self.assertIn('--index', result.stderr)

    def test_preflight_explicit_runtime_does_not_fall_back(self):
        preflight = load('portable_preflight', ROOT / 'skills/brand-renderer/scripts/runtime_preflight.py')
        with tempfile.TemporaryDirectory() as directory:
            missing = str(Path(directory) / 'missing-runtime')
            with patch.dict(os.environ, {'ESTATE_PROSE_RUNTIME': missing}), patch.object(preflight.subprocess, 'run') as run:
                run.return_value = subprocess.CompletedProcess([], 0, '{"ok": true}', '')
                report = preflight.resolve()
            self.assertFalse(report['ok'])
            self.assertIsNone(report['prose_check'])
            self.assertIn('prose_check', report['missing'])
        with patch.dict(os.environ, {'ESTATE_PROSE_RUNTIME': 'relative-path'}):
            with self.assertRaisesRegex(ValueError, 'absolute runtime directory'):
                preflight.resolve()

    def test_personal_profile_is_external_and_sources_keep_licenses(self):
        path = ROOT / 'skills/author-writing-style/SKILL.md'
        text = path.read_text()
        self.assertIn('explicitly supplied', text)
        self.assertIn('no person', text)
        for private in ('Megan', '$660K', '184 tests', '--profile megan', '/Volumes/BeastMode'):
            self.assertNotIn(private, text)
        for name in ('accessibility-audit', 'analytics-strategy', 'usability-testing'):
            self.assertIn('Copyright (c) 2026 RampStack Co.', (ROOT / 'skills' / name / 'LICENSE').read_text())


if __name__ == '__main__':
    unittest.main()
