"""Offline promotion checks with retained fixtures and a strict fake sf CLI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from portable import assemble

COMMANDS = ["devops:promotion:validate", "devops:promote",
            "devops:work-item:prepare", "devops:promotion:complete"]


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.package = self.base / "dx-devops-promote"
        assemble(ROOT, "dx-devops-promote", self.package, [])
        self.manifest = self.base / "plugin.json"
        self.value = {"version": "2.2.0", "commandIDs": COMMANDS,
                      "commands": [{"id": "devops:promote", "flags": {"skip-validation": {}}}]}
        self.manifest.write_text(json.dumps(self.value))
        self.fake = self.base / "sf"
        self.fake.write_text(
            "#!" + sys.executable + "\nimport json,os,sys\nfrom pathlib import Path\n"
            "p=Path(__file__).parent\n"
            "with (p/'calls.jsonl').open('a') as f:f.write(json.dumps(sys.argv[1:])+'\\n')\n"
            "assert sys.argv[1:]==['plugins','inspect','@salesforce/plugin-devops-center','--json']\n"
            "assert os.environ.get('SF_DISABLE_LOG_FILE')=='true'\n"
            "print((p/'plugin.json').read_text())\n")
        self.fake.chmod(0o755)
        self.count = 0

    def call(self, script, *args, expected=0):
        self.count += 1
        command = [sys.executable, str(self.package / "scripts" / script), *args]
        result = subprocess.run(command, cwd=self.base,
            env={**os.environ, "SF_BIN": str(self.fake)}, capture_output=True, text=True, timeout=3)
        (self.base / f"command-{self.count}.json").write_text(json.dumps({
            "command": command, "exit": result.returncode, "stdout": result.stdout,
            "stderr": result.stderr, "manifest": self.manifest.read_text(),
            "validation": (self.base / "validation.json").read_text() if (self.base / "validation.json").exists() else None}, indent=2))
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_supplied_manifest_never_calls_cli_or_claims_an_org_check(self):
        result = json.loads(self.call("preflight.py", "--manifest", str(self.manifest)).stdout)
        self.assertFalse((self.base / "calls.jsonl").exists())
        self.assertFalse(result["org_verified"])
        self.assertFalse(result["promotion_verified"])
        self.assertIn("installed plugin not checked", result["basis"])
        self.assertEqual(result["checked_commands"], COMMANDS)

    def test_local_inspection_calls_only_plugins_inspect(self):
        result = json.loads(self.call("preflight.py").stdout)
        self.assertEqual(result["capability_check"], "passed")
        calls = [json.loads(line) for line in (self.base / "calls.jsonl").read_text().splitlines()]
        self.assertEqual(calls, [["plugins", "inspect", "@salesforce/plugin-devops-center", "--json"]])

    def test_missing_complete_and_optional_combine_are_detected(self):
        self.call("preflight.py", "--manifest", str(self.manifest), "--require-combine", expected=1)
        value = {**self.value, "commandIDs": COMMANDS + ["devops:work-item:combine"]}
        self.manifest.write_text(json.dumps([value]))
        self.call("preflight.py", "--manifest", str(self.manifest), "--require-combine")
        value["commandIDs"] = [item for item in COMMANDS if item != "devops:promotion:complete"]
        self.manifest.write_text(json.dumps(value))
        self.call("preflight.py", "--manifest", str(self.manifest), expected=1)

    def test_malformed_versions_structures_and_flags_refuse(self):
        cases = [None, [], [self.value, self.value],
                 {**self.value, "version": "2.0.0-rc.1"},
                 {**self.value, "version": True}, {**self.value, "version": "latest"},
                 {**self.value, "version": "1.9.9"}, {**self.value, "commandIDs": "wrong"},
                 {**self.value, "commands": [{"id": "devops:promote", "flags": {"skip-validation": False}}]}]
        for value in cases:
            self.manifest.write_text(json.dumps(value))
            self.call("preflight.py", "--manifest", str(self.manifest), expected=1)
        self.manifest.write_text("{broken")
        self.call("preflight.py", "--manifest", str(self.manifest), expected=1)

    def test_routes_and_missing_argument_return_without_hanging(self):
        common = ("--target-stage-id", "first", "--first-stage-id", "first")
        skip = json.loads(self.call("promotion-route.py", *common).stdout)
        self.assertEqual(skip["action"], "skip")
        prepare = json.loads(self.call("promotion-route.py", "--current-stage-id", "earlier", *common).stdout)
        self.assertEqual(prepare["action"], "prepare")
        self.call("promotion-route.py", "--current-stage-id", "first", *common, expected=1)
        self.call("promotion-route.py", "--target-stage-id", expected=2)
        self.call("promotion-route.py", "--current-stage-id", " ", *common, expected=2)
        self.assertFalse((self.base / "calls.jsonl").exists())

    def test_combine_plan_parses_success_and_refuses_failed_or_ambiguous_data(self):
        validation = self.base / "validation.json"
        parent, child = "1fk000000000001", "1fk000000000002"
        details = {"parentWorkitemId": parent, "childWorkitemsId": [child]}
        def save(result, status=0):
            validation.write_text(json.dumps({"status": status, "result": result}))
        save({"success": True, "combineDetails": details})
        plan = json.loads(self.call("combine-plan.py", "--validation", str(validation)).stdout)
        self.assertEqual(plan["arguments"], ["--parent-work-item-id", parent, "--child-work-item-id", child])
        self.assertFalse(plan["execution_performed"])
        save({"success": True, "combineDetails": None})
        self.assertFalse(json.loads(self.call("combine-plan.py", "--validation", str(validation)).stdout)["combine"])
        invalid = [{"success": False, "combineDetails": details},
                   {"success": True}, {"success": True, "combineDetails": {}},
                   {"success": True, "combineDetails": {**details, "childWorkitemsId": [child, child]}},
                   {"success": True, "combineDetails": {**details, "parentWorkitemId": "$(bad)"}},
                   {"success": True, "combineDetails": {**details, "childWorkitemsId": [parent]}}]
        for result in invalid:
            save(result)
            self.call("combine-plan.py", "--validation", str(validation), expected=1)
        save({"success": True, "combineDetails": details}, status=False)
        self.call("combine-plan.py", "--validation", str(validation), expected=1)
        self.assertFalse((self.base / "calls.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
