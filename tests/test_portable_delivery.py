"""Verify explicit account inputs without reading credentials or reaching a network."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'skills/sf-deploy-engine/scripts/engine.sh'
DOCTOR = ROOT / 'skills/sf-deploy-engine/scripts/doctor.sh'


class PortableDeliveryTests(unittest.TestCase):
    def test_engine_does_not_reuse_an_implicit_token(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            home = root / 'home'
            legacy = home / '.config/sf-deploy-engine/token'
            legacy.parent.mkdir(parents=True)
            legacy.write_text('SYNTHETIC_LEGACY_TOKEN')
            bindir = root / 'bin'
            bindir.mkdir()
            curl = bindir / 'curl'
            curl.write_text('#!/usr/bin/env python3\nimport os,sys,pathlib\nargs=sys.argv[1:]\npathlib.Path(os.environ["MOCK_LOG"]).write_text("\\n".join(args))\np=pathlib.Path(args[args.index("-o")+1]);p.write_text("{\\"environments\\":{}}")\nprint("200",end="")\n')
            curl.chmod(0o700)
            log = root / 'curl.log'
            env = dict(os.environ, HOME=str(home), PATH=str(bindir)+os.pathsep+os.environ['PATH'],
                       ENGINE_URL='https://engine.example.invalid', MOCK_LOG=str(log))
            env.pop('SFDE_TOKEN', None)
            env.pop('SFDE_TOKEN_FILE', None)
            run = subprocess.run(['bash', str(ENGINE), 'status'], cwd=root, env=env, text=True, capture_output=True)
            self.assertNotEqual(0, run.returncode)
            self.assertIn('explicitly selected', run.stderr)
            self.assertFalse(log.exists())
            self.assertEqual('SYNTHETIC_LEGACY_TOKEN', legacy.read_text())
            self.assertNotIn('SYNTHETIC_LEGACY_TOKEN', run.stdout+run.stderr)
            env['SFDE_TOKEN_FILE'] = str(legacy)
            run = subprocess.run(['bash', str(ENGINE), 'status'], cwd=root, env=env, text=True, capture_output=True)
            self.assertEqual(0, run.returncode, run.stderr)
            self.assertIn('"environments": {}', run.stdout)
            self.assertIn('Authorization: Bearer SYNTHETIC_LEGACY_TOKEN', log.read_text())
            self.assertNotIn('SYNTHETIC_LEGACY_TOKEN', run.stdout+run.stderr)
            log.unlink()
            env['SFDE_TOKEN_FILE'] = 'relative-token'
            run = subprocess.run(['bash', str(ENGINE), 'status'], cwd=root, env=env, text=True, capture_output=True)
            self.assertNotEqual(0, run.returncode)
            self.assertFalse(log.exists())

    def test_doctor_token_resolution_has_no_default_account(self):
        text = DOCTOR.read_text()
        block = text[text.index('TOKEN="${SFDE_TOKEN:-}"'):text.index('STATUS_JSON=""')]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            legacy = root / '.config/sf-deploy-engine/token'
            legacy.parent.mkdir(parents=True)
            legacy.write_text('SYNTHETIC_PRIVATE_TOKEN')
            env = dict(os.environ, HOME=str(root))
            env.pop('SFDE_TOKEN', None)
            env.pop('SFDE_TOKEN_FILE', None)
            run = subprocess.run(['bash', '-c', block+'\nprintf "%s" "$TOKEN"'], env=env, capture_output=True, text=True)
            self.assertEqual('', run.stdout)
            env['SFDE_TOKEN_FILE'] = str(legacy)
            run = subprocess.run(['bash', '-c', block+'\nprintf "%s" "$TOKEN"'], env=env, capture_output=True, text=True)
            self.assertEqual('SYNTHETIC_PRIVATE_TOKEN', run.stdout)

if __name__ == '__main__':
    unittest.main()
