"""Portable maintenance contracts, using synthetic stores and no accounts/network."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
HUB_SCRIPT = ROOT / 'skills/knowledge-hub/scripts/hub_runtime.py'
PUBLISH_SCRIPT = ROOT / 'skills/skill-estate-sync/scripts/record_publish.py'
spec = importlib.util.spec_from_file_location('portable_maintenance_hub', HUB_SCRIPT)
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


class PortableMaintenanceTests(unittest.TestCase):
    def test_discovery_requires_base_before_any_directory_access(self):
        with patch.object(Path, 'is_dir', side_effect=AssertionError('implicit filesystem lookup')):
            for base in (None, '', '  '):
                with self.assertRaises(hub.MissingIdentity):
                    hub.synced_drive_mounts(base=base)
                with self.assertRaises(hub.MissingIdentity):
                    hub.find_synced_hub_roots(base=base)

    def test_explicit_accounts_remain_ambiguous_and_never_grant_write_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for account in ('a@example.invalid', 'b@example.invalid'):
                path = base / ('GoogleDrive-' + account) / 'My Drive/Clients/Example/AI Knowledge Hub'
                path.mkdir(parents=True)
                (path / '00-CLIENT.md').write_text('Synthetic example\n')
            rows = hub.find_synced_hub_roots(client='Example', base=base)
            self.assertEqual(len(rows), 2)
            self.assertTrue(all(row['readable'] for row in rows))
            self.assertTrue(all(row['writableByDefault'] is False for row in rows))
            selected = hub.find_synced_hub_roots(client='Example', base=base, email='b@example.invalid')
            self.assertEqual(len(selected), 1)
            self.assertEqual(selected[0]['account'], 'GoogleDrive-b@example.invalid')

    def test_guarded_write_still_requires_current_hash_and_reports_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = hub.write_local_record(root, 'record.md', 'Synthetic first\n', None)
            with self.assertRaises(hub.VersionConflict):
                hub.write_local_record(root, 'record.md', 'Unverified overwrite', None)
            second = hub.write_local_record(root, 'record.md', 'Synthetic second\n', first['afterHash'])
            self.assertEqual(second['state'], 'written-and-confirmed')
            self.assertEqual(second['afterHash'], hashlib.sha256((root / 'record.md').read_bytes()).hexdigest())
            with self.assertRaises(hub.VersionConflict):
                hub.write_local_record(root, 'record.md', 'Stale overwrite', first['afterHash'])

    def invoke(self, *args, cwd):
        return subprocess.run([sys.executable, str(PUBLISH_SCRIPT), *map(str, args)],
                              cwd=cwd, capture_output=True, text=True,
                              env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, timeout=20)

    def make_inputs(self, root):
        config_dir = root / 'configured'; config_dir.mkdir()
        dist = root / 'bundles'; dist.mkdir()
        (dist / 'alpha.skill').write_bytes(b'synthetic alpha bundle')
        (dist / 'beta.skill').write_bytes(b'synthetic beta bundle')
        config = config_dir / 'surfaces.json'
        config.write_text(json.dumps({'cloud_surfaces': [{'name': 'selected', 'kind': 'cloud'}],
                                      'ledger': 'claims.json'}))
        return config, dist, config_dir / 'claims.json'

    def test_publication_requires_inputs_and_cannot_write_bundled_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.invoke('--surface', 'selected', cwd=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('--config', result.stderr)
            self.assertEqual(list(root.iterdir()), [])
            config, dist, ledger = self.make_inputs(root)
            config.write_text(json.dumps({'ledger': str(PUBLISH_SCRIPT.parent.parent / 'publish-ledger.json'),
                                          'cloud_surfaces': [{'name': 'selected'}]}))
            before = (PUBLISH_SCRIPT.parent.parent / 'publish-ledger.json').read_bytes()
            result = self.invoke('--config', config, '--dist', dist, '--surface', 'selected', cwd=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('outside the reusable skill directory', result.stderr)
            self.assertEqual((PUBLISH_SCRIPT.parent.parent / 'publish-ledger.json').read_bytes(), before)
            self.assertFalse(ledger.exists())

    def test_publication_uses_config_relative_ledger_and_exact_selected_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config, dist, ledger = self.make_inputs(root)
            args = ('--config', config, '--dist', dist)
            result = self.invoke(*args, '--surface', 'selected', '--only', 'alpha', '--date', '2026-01-01', cwd=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('does not verify', result.stdout)
            record = json.loads(ledger.read_text())['surfaces']['selected']
            self.assertEqual(record, {'bundles': {'alpha': hashlib.sha1(b'synthetic alpha bundle').hexdigest()},
                                      'last_recorded': '2026-01-01'})
            before = ledger.read_bytes()
            result = self.invoke(*args, '--status', cwd=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('never recorded: 1', result.stdout)
            self.assertEqual(ledger.read_bytes(), before)
            (dist / 'alpha.skill').write_bytes(b'changed synthetic bundle')
            result = self.invoke(*args, '--status', cwd=root)
            self.assertIn('changed since : 1', result.stdout)
            self.assertEqual(ledger.read_bytes(), before)

    def test_migration_cli_uses_only_supplied_folder_scope_and_never_edits_sources(self):
        script = ROOT / 'skills/knowledge-hub/scripts/migration_report.py'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'source'
            hub_path = source / 'Synthetic Sales' / 'Example' / 'knowledge-hub'
            hub_path.mkdir(parents=True)
            document = hub_path / '01-company-profile.md'
            document.write_text('Synthetic profile, unchanged by audit')
            before = document.read_bytes()
            mapping = root / 'scopes.json'
            mapping.write_text(json.dumps({'Synthetic Sales': 'opportunity'}))
            report = root / 'report.json'
            command = [sys.executable, str(script), str(source), '--json-output', str(report)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(report.read_text())['hubs'][0]['proposedContextType'], 'unclassified')
            result = subprocess.run(command + ['--bucket-scopes', str(mapping)], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(report.read_text())['hubs'][0]['proposedContextType'], 'opportunity')
            self.assertEqual(document.read_bytes(), before)
            mapping.write_text(json.dumps({'Synthetic Sales': 'invented-lifecycle'}))
            prior = report.read_bytes()
            result = subprocess.run(command + ['--bucket-scopes', str(mapping)], capture_output=True, text=True, timeout=20)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('bucket scopes must map', result.stderr)
            self.assertEqual(report.read_bytes(), prior)
            self.assertEqual(document.read_bytes(), before)

    def test_unknown_destination_and_missing_explicit_ledger_refuse_without_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config, dist, ledger = self.make_inputs(root)
            result = self.invoke('--config', config, '--dist', dist, '--surface', 'unselected', cwd=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('unknown surface', result.stderr)
            self.assertFalse(ledger.exists())
            config.write_text(json.dumps({'cloud_surfaces': [{'name': 'selected'}]}))
            result = self.invoke('--config', config, '--dist', dist, '--surface', 'selected', cwd=root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('explicit ledger path', result.stderr)
            self.assertFalse(ledger.exists())


if __name__ == '__main__':
    unittest.main()
