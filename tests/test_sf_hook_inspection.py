"""Inspect installed synthetic wiring without changing project state or calling CLIs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / "skills/sf-solo-devops/references/hooks"


class Inspection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sf-hook-inspection-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.project = self.folder / "project"
        self.project.mkdir()
        self.env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null",
                    "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic Test")
        self.git("config", "user.email", "test@example.invalid")
        shutil.copytree(HOOKS / "githooks", self.project / ".githooks")
        shutil.copytree(HOOKS / "claude-hooks", self.project / ".claude/hooks")
        shutil.copyfile(HOOKS / "claude-settings-template.json",
                        self.project / ".claude/settings.json")
        for f in (self.project / ".githooks").iterdir():
            f.chmod(0o755)
        for f in (self.project / ".claude/hooks").glob("*.sh"):
            f.chmod(0o755)
        self.git("add", ".")
        self.git("commit", "-qm", "Synthetic installed files")
        self.count = 0
        fake_bin = self.folder / "bin"
        fake_bin.mkdir()
        for name in ("sf", "gh", "jq"):
            f = fake_bin / name
            f.write_text('#!/bin/sh\nprintf "%s\\n" called > "' +
                         str(self.folder / (name + "-called")) + '"\nexit 91\n')
            f.chmod(0o755)
        self.env["PATH"] = str(fake_bin) + ":" + os.environ["PATH"]

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.project), *args],
                              env=self.env, check=True, capture_output=True, text=True)

    def snapshot(self, project):
        return {str(f.relative_to(project)): [hashlib.sha256(f.read_bytes()).hexdigest(),
                                              f.stat().st_mode & 0o777]
                for f in project.rglob("*") if f.is_file() and ".git" not in f.parts}

    def invoke(self, project=None):
        project = project or self.project
        before = self.snapshot(project)
        config_before = (self.project / ".git/config").read_bytes()
        result = subprocess.run(["bash", str(project / ".claude/hooks/verify-git-hooks.sh")],
                                cwd=self.folder, env={**self.env, "CLAUDE_PROJECT_DIR": str(project)},
                                text=True, capture_output=True, timeout=15)
        self.count += 1
        (self.folder / f"inspection-{self.count}.json").write_text(json.dumps({
            "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, indent=2))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, self.snapshot(project))
        self.assertEqual(config_before, (self.project / ".git/config").read_bytes())
        for name in ("sf", "gh", "jq"):
            self.assertFalse((self.folder / (name + "-called")).exists())
        return json.loads(result.stdout)

    def test_configured_stack_is_inspected_without_running_hooks(self):
        self.git("config", "core.hooksPath", ".githooks")
        report = self.invoke()
        self.assertEqual(report["state"], "wiring_present")
        self.assertFalse(report["configuration_changed"])
        self.assertIn(".claude/hooks/guard-sf-flags.py", report["checked"])

    def test_existing_manager_and_unset_config_are_preserved(self):
        self.assertIn("unset", " ".join(self.invoke()["review"]))
        self.git("config", "core.hooksPath", ".husky/_")
        report = self.invoke()
        self.assertEqual(report["configured_hooks_path"], ".husky/_")
        self.assertIn("Reconcile", " ".join(report["review"]))

    def test_missing_helper_and_nonexecutable_script_are_reported(self):
        (self.project / ".claude/hooks/deploy-verdict.py").unlink()
        (self.project / ".claude/hooks/guard-sf-flags.sh").chmod(0o644)
        report = self.invoke()
        problems = " ".join(report["problems"])
        self.assertIn("deploy-verdict.py is missing", problems)
        self.assertIn("guard-sf-flags.sh is not executable", problems)

    def test_malformed_settings_are_reported(self):
        (self.project / ".claude/settings.json").write_text('{"hooks":')
        self.assertEqual(self.invoke()["state"], "unavailable")

    def test_active_worktree_is_inspected_instead_of_main(self):
        wt = self.folder / "worktree"
        self.git("worktree", "add", "-qb", "synthetic-work", str(wt))
        (wt / ".claude/hooks/guard-sf-flags.py").unlink()
        report = self.invoke(wt)
        self.assertEqual(report["project"], str(wt.resolve()))
        self.assertIn("guard-sf-flags.py is missing", " ".join(report["problems"]))
        self.assertTrue((self.project / ".claude/hooks/guard-sf-flags.py").is_file())

    def test_escaping_hook_symlink_is_not_treated_as_installed(self):
        external = self.folder / "external.sh"
        external.write_text("#!/bin/sh\nexit 0\n")
        external.chmod(0o755)
        hook = self.project / ".claude/hooks/guard-sf-flags.sh"
        hook.unlink()
        hook.symlink_to(external)
        report = self.invoke()
        self.assertIn("resolves outside", " ".join(report["problems"]))


if __name__ == "__main__":
    unittest.main()
