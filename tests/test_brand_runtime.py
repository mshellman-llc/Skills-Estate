"""Behavioral checks for the shared profile in source and isolated packages."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "skills/brand-renderer/brand"
SPEC = importlib.util.spec_from_file_location("estate_profile_test", BRAND / "brand_profile.py")
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)
NODE = os.environ.get("ESTATE_NODE") or shutil.which("node")


class BrandRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.neutral = profile.load_profile(ROOT / "policies/brand.md")
        self.clean_env = {k: v for k, v in os.environ.items() if k != "SKILLS_BRAND_PROFILE"}

    def write_profile(self, name="brand.md", **changes):
        value = json.loads(json.dumps(self.neutral))
        value.update(changes)
        path = self.directory / name
        path.write_text("```json\n" + json.dumps(value) + "\n```\n")
        return path

    def test_explicit_missing_profile_never_falls_back(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            profile.resolve_profile(self.directory / "missing.md", cwd=ROOT)

    def test_project_profile_precedes_neutral(self):
        selected = self.write_profile()
        with patch.dict(os.environ, self.clean_env, clear=True):
            self.assertEqual(selected.resolve(), profile.resolve_profile(cwd=self.directory, anchor=BRAND / "tokens.py"))

    def test_profile_edit_changes_renderer_values_without_rebuild(self):
        selected = self.write_profile()
        script = "import json; from tokens import T; print(json.dumps(T.hex))"
        env = {**self.clean_env, "PYTHONPATH": str(BRAND), "SKILLS_BRAND_PROFILE": str(selected)}
        before = subprocess.check_output([sys.executable, "-c", script], env=env, cwd=self.directory, text=True)
        changed = {**self.neutral["colors"], "accent": "#7B321A"}
        self.write_profile(colors=changed)
        after = subprocess.check_output([sys.executable, "-c", script], env=env, cwd=self.directory, text=True)
        self.assertEqual(json.loads(before)["teal"], self.neutral["colors"]["accent"])
        self.assertEqual(json.loads(after)["teal"], "#7B321A")
        self.assertEqual(json.loads(after)["textPrimary"], self.neutral["colors"]["text"])

    def test_isolated_package_uses_its_vendored_policy(self):
        package = self.directory / "isolated"
        shutil.copytree(BRAND, package / "brand")
        policy = package / "references/estate/brand.md"
        policy.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "policies/brand.md", policy)
        script = "from tokens import T; print(T.path); print(T.hex['textPrimary'])"
        env = {**self.clean_env, "PYTHONPATH": str(package / "brand")}
        result = subprocess.check_output([sys.executable, "-c", script], cwd=self.directory, env=env, text=True)
        self.assertIn(str(policy), result)
        self.assertIn(self.neutral["colors"]["text"], result)

    def test_profile_colors_are_not_rejected_for_being_warm(self):
        selected = self.write_profile(colors={**self.neutral["colors"], "accent": "#7B321A"})
        env = {**self.clean_env, "PYTHONPATH": str(BRAND), "SKILLS_BRAND_PROFILE": str(selected)}
        result = subprocess.check_output(
            [sys.executable, "-c", "from tokens import T; assert not T.is_warm(T.hex['teal'])"],
            cwd=self.directory, env=env, text=True)
        self.assertEqual("", result)

    def test_python_and_node_compile_identical_tokens(self):
        self.assertTrue(NODE, "Node is required for cross-renderer verification; set ESTATE_NODE")
        selected = self.write_profile(colors={**self.neutral["colors"], "accent": "#7B321A"})
        expected = profile.compile_tokens(profile.load_profile(selected), selected)
        script = "const p=require(process.argv[1]); console.log(JSON.stringify(p.compileTokens(p.loadProfile(process.argv[2]),process.argv[2])))"
        result = subprocess.check_output(
            [NODE, "-e", script, str(BRAND / "brand_profile.js"), str(selected)],
            cwd=self.directory, env=self.clean_env, text=True)
        self.assertEqual(expected, json.loads(result))

    def test_node_renderer_loads_explicit_profile(self):
        self.assertTrue(NODE, "Node is required for renderer verification; set ESTATE_NODE")
        selected = self.write_profile(colors={**self.neutral["colors"], "accent": "#7B321A"})
        script = "const t=require(process.argv[1]); console.log(JSON.stringify({accent:t.hex.teal,text:t.hex.textPrimary}))"
        result = subprocess.check_output(
            [NODE, "-e", script, str(BRAND / "tokens.js")], cwd=self.directory,
            env={**self.clean_env, "SKILLS_BRAND_PROFILE": str(selected)}, text=True)
        self.assertEqual({"accent": "#7B321A", "text": self.neutral["colors"]["text"]}, json.loads(result))


if __name__ == "__main__":
    unittest.main()
