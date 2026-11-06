"""Exercise the portable maintainer entry against real isolated estate tooling."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/skill-estate-sync"
sys.path.insert(0, str(ROOT / "tools"))
from portable import assemble


class EntryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / "canonical"
        self.home = self.base / "home"
        self.home.mkdir()
        for directory in ("tools", "policies", "skills/demo/scripts"):
            (self.repo / directory).mkdir(parents=True)
        for name in ("estate.py", "portable.py", "catalog.py", "releases.py", "committed_source.py",
                     "plugins.py", "plugin_version.py", "browse.py", "promote_maintenance.py"):
            shutil.copy2(ROOT / "tools" / name, self.repo / "tools" / name)
        (self.repo / "policies/skill-standard.md").write_text("# Test skill standard\n")
        (self.repo / "skills/demo/SKILL.md").write_text(
            "---\nname: demo\ndescription: Produce a local example\n---\n"
            "Run scripts/work.py to produce a local example.\n")
        (self.repo / "skills/demo/scripts/work.py").write_text("print('example')\n")
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        self.commit_source()
        self.package = self.base / "isolated/skill-estate-sync"
        assemble(ROOT, "skill-estate-sync", self.package, [])
        self.bridge = self.package / "scripts/manage_estate.py"
        self.commands = []
        self.addCleanup(lambda: (self.base / "commands.json").write_text(json.dumps(self.commands, indent=2)))

    def commit_source(self):
        subprocess.run(['git', '-C', str(self.repo), 'add', 'tools', 'skills', 'policies'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Test',
                        '-c', 'user.email=test@example.com', '-c', 'core.hooksPath=/dev/null',
                        'commit', '-qm', 'fixture'], check=True)

    def run_cli(self, *args, explicit=True, expected=0):
        command = [sys.executable, str(self.bridge), "--home", str(self.home)]
        if explicit:
            command += ["--repo", str(self.repo)]
        command += list(args)
        result = subprocess.run(command, cwd=self.base, capture_output=True, text=True)
        self.commands.append({"command": command, "exit": result.returncode,
                              "stdout": result.stdout, "stderr": result.stderr})
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_installed_update_uses_bundled_code_and_preserves_authoring_checkout(self):
        # This is an old/dirty authoring checkout: invoking its CLI is a failure.
        old = self.repo / 'tools/estate.py'
        old.write_text("raise SystemExit('WRONG AUTHORING UPDATER')\n")
        untracked = self.repo / 'skills/unfinished.txt'
        untracked.write_text('unfinished work')
        pointer = self.home / '.config/skills-estate/repository'
        pointer.parent.mkdir(parents=True)
        pointer.symlink_to(self.repo)
        fake_bin = self.base / 'bin'
        fake_bin.mkdir()
        git = fake_bin / 'git'
        git.write_text('#!/bin/sh\necho "offline fixture fetch" >&2\nexit 1\n')
        git.chmod(0o755)
        before = {p: p.read_bytes() for p in (old, untracked)}
        # The package is detached from its builder and has no .git directory.
        env = dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ['PATH'])
        result = subprocess.run([sys.executable, str(self.bridge), '--home', str(self.home), 'update'],
                                cwd=self.base, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('offline fixture fetch', result.stderr)
        self.assertNotIn('WRONG AUTHORING', result.stderr)
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertEqual(pointer.resolve(), self.repo.resolve())
        self.assertFalse((self.package / 'scripts/.local').exists())
        self.assertFalse((self.home / '.local/state/skills-estate/active.json').exists())
        receipts = list((self.home / '.local/state/skills-estate').glob('update-*/update.json'))
        self.assertEqual(len(receipts), 1)
        self.assertEqual(json.loads(receipts[0].read_text())['state'], 'failed')

    def test_release_activation_and_rollback_select_bundled_updater_bytes(self):
        import estate
        import releases
        repo, home = self.repo.resolve(), self.home.resolve()
        package_a = self.package.resolve()
        module_a = package_a / 'scripts/estate_tools/updater.py'
        module_a.write_text("print('SELECTED-UPDATER-A')\n" + module_a.read_text())
        package_b = self.base.resolve() / 'second-package'
        shutil.copytree(package_a, package_b)
        module_b = package_b / 'scripts/estate_tools/updater.py'
        module_b.write_text(module_b.read_text().replace('SELECTED-UPDATER-A', 'SELECTED-UPDATER-B'))
        # Any fallback to the authoring checkout would fail differently.
        old = repo / 'tools/estate.py'
        old.write_text("raise SystemExit('WRONG AUTHORING UPDATER')\n")
        fake_bin = self.base.resolve() / 'rollback-bin'
        fake_bin.mkdir()
        fake_git = fake_bin / 'git'
        fake_git.write_text('#!/bin/sh\necho offline-rollback-fixture >&2\nexit 1\n')
        fake_git.chmod(0o755)
        env = dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ['PATH'])
        installed = home / '.agents/skills/skill-estate-sync'

        def activate(package):
            with releases.home_lock(home):
                release_id = releases.snapshot(repo, home, {'skill-estate-sync': package},
                                               'synthetic-test', 'owner', estate.tree_hash)
                releases.activate(repo, home, release_id, estate.tree_hash,
                                  account_provided=['skill-estate-sync'])
            return release_id

        def check_selected(marker, release_id):
            before = estate.tree_hash(installed.resolve())
            command = [sys.executable, str(installed / 'scripts/manage_estate.py'),
                       '--home', str(home), 'update']
            result = subprocess.run(command, cwd=self.base, env=env, capture_output=True, text=True)
            self.commands.append({'command': command, 'exit': result.returncode,
                                  'stdout': result.stdout, 'stderr': result.stderr})
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), marker)
            self.assertIn('offline-rollback-fixture', result.stderr)
            self.assertNotIn('WRONG AUTHORING', result.stderr)
            self.assertEqual(estate.tree_hash(installed.resolve()), before)
            self.assertEqual((home / '.config/skills-estate/repository').resolve(), repo)
            observed = releases.inspect(home, estate.tree_hash)
            self.assertTrue(observed['ok'])
            self.assertEqual(observed['release_id'], release_id)

        first = activate(package_a)
        check_selected('SELECTED-UPDATER-A', first)
        second = activate(package_b)
        self.assertNotEqual(first, second)
        check_selected('SELECTED-UPDATER-B', second)
        estate.rollback(repo, home, first)
        check_selected('SELECTED-UPDATER-A', first)
        self.assertEqual(old.read_text(), "raise SystemExit('WRONG AUTHORING UPDATER')\n")

    def test_updater_modules_are_exact_and_authoring_collisions_are_rejected(self):
        from portable import UPDATER_MODULES
        for module in UPDATER_MODULES:
            self.assertEqual((self.package / 'scripts/estate_tools' / (module + '.py')).read_bytes(),
                             (ROOT / 'tools' / (module + '.py')).read_bytes())
        source = self.base / 'fixture-source'
        shutil.copytree(SKILL, source / 'skills/skill-estate-sync')
        shutil.copytree(ROOT / 'tools', source / 'tools')
        collision = source / 'skills/skill-estate-sync/scripts/estate_tools/unexpected.py'
        collision.parent.mkdir()
        collision.write_text('unreviewed replacement')
        with self.assertRaisesRegex(ValueError, 'generated'):
            assemble(source, 'skill-estate-sync', self.base / 'bad-package', [])

    def test_detached_entry_builds_installs_detects_drift_and_restores(self):
        self.run_cli("validate")
        self.run_cli("build")
        self.run_cli("bundle")
        installed = json.loads(self.run_cli("install").stdout)
        current = json.loads(self.run_cli("status", explicit=False).stdout)
        self.assertTrue(current["ok"])
        self.assertFalse(current["cloud"]["claude-account"]["verified_live"])
        self.assertEqual(current["cloud"]["claude-account"]["packages"]["demo"], "pending")
        package = self.home / ".claude/skills/demo"
        self.assertEqual((package / "scripts/work.py").read_text(), "print('example')\n")
        self.run_cli("restore", str(Path(installed["backup"]) / "receipt.json"), explicit=False)
        self.assertFalse(package.exists())
        self.run_cli("status", expected=1)

    def test_missing_registration_does_not_guess_or_install(self):
        self.run_cli("sync", explicit=False, expected=2)
        self.assertFalse((self.repo / "build").exists())
        self.assertFalse((self.home / ".claude").exists())

    def test_packaged_compatibility_selftest_runs_away_from_source(self):
        result = subprocess.run([sys.executable, str(ROOT / "tools/run_preserved_test.py"),
                                 str(self.package / "scripts/estate_sync_selftest.py"),
                                 "--output", str(self.base / "packaged-selftest")],
                                cwd=self.base, capture_output=True, text=True)
        self.commands.append({"stdout": result.stdout, "stderr": result.stderr, "exit": result.returncode})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        log = (Path(receipt["attempt"]) / "console.log").read_text()
        self.assertIn("Canonical shared-runtime integration not checked: isolated package", log)
        self.assertEqual(len(list(self.package.rglob("SKILL.md"))), 1)

    def test_existing_work_is_preserved_until_explicit_adopt_and_is_restorable(self):
        existing = self.home / ".agents/skills/demo"
        existing.mkdir(parents=True)
        (existing / "my-work.txt").write_text("Keep this work\n")
        self.run_cli("build")
        self.run_cli("install", expected=2)
        self.assertEqual((existing / "my-work.txt").read_text(), "Keep this work\n")
        self.assertFalse((self.home / ".claude/skills/demo").exists())
        adopted = json.loads(self.run_cli("adopt").stdout)
        self.assertTrue(existing.is_symlink())
        self.run_cli("restore", str(Path(adopted["backup"]) / "receipt.json"))
        self.assertFalse(existing.is_symlink())
        self.assertEqual((existing / "my-work.txt").read_text(), "Keep this work\n")

    def test_source_change_requires_rebuild_and_copied_drift_fails_status(self):
        self.run_cli("sync")
        self.assertFalse((self.home / ".agents/skills/demo").exists())
        self.run_cli("install")
        dest = self.home / ".agents/skills/demo"
        source = dest.resolve()
        dest.unlink()
        shutil.copytree(source, dest)
        (dest / "scripts/work.py").chmod(0o644)
        (dest / "scripts/work.py").write_text("print('changed')\n")
        status = json.loads(self.run_cli("status", expected=1).stdout)
        self.assertIn("drift", [rows["demo"] for rows in status["local"].values()])
        (self.repo / "policies/skill-standard.md").write_text("# Changed policy\n")
        self.commit_source()
        self.run_cli("install", expected=2)
        self.assertEqual((dest / "scripts/work.py").read_text(), "print('changed')\n")

    def test_flat_audit_fails_missing_and_resource_drift_in_both_formats(self):
        source = self.base / "flat"
        skill = source / "org-preflight"
        (skill / "scripts").mkdir(parents=True)
        (skill / "SKILL.md").write_text("# Org preflight\n")
        (skill / "scripts/check.py").write_text("print('source')\n")
        surface = self.base / "surface"
        surface.mkdir()
        config = self.base / "surfaces.json"
        config.write_text(json.dumps({"surfaces": [{"name": "test", "path": str(surface)}]}))
        for state in ("missing", "resource-drift"):
            if state == "resource-drift":
                shutil.copytree(skill, surface / skill.name)
                (surface / skill.name / "scripts/check.py").write_text("print('drift')\n")
            for mode in ([], ["--json"]):
                result = subprocess.run([sys.executable, str(SKILL / "scripts/estate_diff.py"),
                    "--source", str(source), "--config", str(config), *mode],
                    capture_output=True, text=True)
                self.commands.append({"state": state, "mode": mode, "exit": result.returncode,
                                      "stdout": result.stdout, "stderr": result.stderr})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                if mode:
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload["local_surface_drift"]["org-preflight"]["test"], state)

    def test_flat_cloud_claims_use_selected_source_and_never_imply_readback(self):
        source = self.base / "flat-repo/skills"
        (source / "org-preflight").mkdir(parents=True)
        (source / "org-preflight/SKILL.md").write_text("# Org preflight\n")
        config = self.base / "flat-repo/surfaces.json"
        config.write_text(json.dumps({"surfaces": [], "cloud_surfaces": [{"name": "test-account"}]}))
        def audit():
            r = subprocess.run([sys.executable, str(SKILL / "scripts/estate_diff.py"),
                "--source", str(source), "--config", str(config), "--json"],
                capture_output=True, text=True)
            self.commands.append({"stdout": r.stdout, "stderr": r.stderr, "exit": r.returncode})
            self.assertEqual(r.returncode, 0, r.stderr)
            return json.loads(r.stdout)["cloud_publications"]
        empty = audit()
        self.assertFalse(empty["surfaces"][0]["bundle_inventory_available"])
        dist = source.parent / "dist"
        dist.mkdir()
        (dist / "org-preflight.skill").write_bytes(b"synthetic archive hash fixture")
        pending = audit()
        self.assertTrue(pending["surfaces"][0]["bundle_inventory_available"])
        self.assertEqual(pending["surfaces"][0]["never_recorded"], ["org-preflight"])
        self.assertFalse(pending["verified"])


if __name__ == "__main__":
    unittest.main()
