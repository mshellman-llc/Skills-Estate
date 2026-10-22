"""Exercise actual local Hub workflows and conflict handling with saved outputs."""
import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/knowledge-hub/scripts"
sys.path.insert(0, str(SCRIPTS))
import hub_runtime as runtime
import hub_resolver as resolver


class HubBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        output = ROOT / ".local/verification/knowledge-hub"
        output.mkdir(parents=True, exist_ok=True)
        cls.attempt = Path(tempfile.mkdtemp(prefix="behavior-", dir=output))
        cls.env = {**os.environ, "GIT_AUTHOR_NAME": "Synthetic test",
                   "GIT_AUTHOR_EMAIL": "test@example.invalid",
                   "GIT_COMMITTER_NAME": "Synthetic test",
                   "GIT_COMMITTER_EMAIL": "test@example.invalid"}
        cls.sequence = 0

    def invoke(self, script, *args, expected=0):
        type(self).sequence += 1
        proc = subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, args)],
                              capture_output=True, text=True, env=self.env)
        stem = self.attempt / "{:03d}-{}".format(self.sequence, Path(script).stem)
        stem.with_suffix(".log").write_text(proc.stdout + proc.stderr)
        stem.with_suffix(".command.json").write_text(json.dumps(
            {"script": script, "args": list(map(str, args)), "exitCode": proc.returncode}, indent=2))
        self.assertEqual(expected, proc.returncode, proc.stdout + proc.stderr)
        return json.loads(proc.stdout) if proc.stdout.strip() else {"error": proc.stderr}

    def make_hub(self, name, git=False):
        hub = self.attempt / name
        args = ["--json", "init", "--hub", hub, "--client", "Example Manufacturing",
                "--opportunity", "opp-pilot", "--engagement", "eng-pilot"]
        if not git:
            args += ["--no-git"]
        self.invoke("hub_workspace.py", *args)
        return hub

    def test_create_read_update_and_stale_write_preserves_current_record(self):
        hub = self.make_hub("record-lifecycle")
        self.assertTrue((hub / "00-CLIENT.md").is_file())
        self.assertTrue((hub / "engagements/eng-pilot/00-ENGAGEMENT.md").is_file())
        first = self.attempt / "discovery-original.md"
        first.write_text("# Discovery\n\nSynthetic finding: one team uses email approvals.\n")
        revised = self.attempt / "discovery-revised.md"
        revised.write_text("# Discovery\n\nSynthetic finding: the owner confirmed the approval policy.\n")
        prefix = ["--hub", hub, "--opportunity", "opp-pilot"]
        create = self.invoke("hub_records.py", *prefix, "write", "opportunity.discovery",
                             "--input", first, "--create")
        read = self.invoke("hub_records.py", *prefix, "read", "opportunity.discovery")
        self.assertEqual(first.read_text(), read["content"])
        self.assertEqual(create["afterHash"], read["sha256"])
        update = self.invoke("hub_records.py", *prefix, "write", "opportunity.discovery",
                             "--input", revised, "--expected-hash", read["sha256"])
        refused = self.invoke("hub_records.py", *prefix, "write", "opportunity.discovery",
                              "--input", first, "--expected-hash", read["sha256"], expected=1)
        self.assertEqual("conflict-held", refused["state"])
        current = self.invoke("hub_records.py", *prefix, "read", "opportunity.discovery")
        self.assertEqual(revised.read_text(), current["content"])
        self.assertEqual(update["afterHash"], current["sha256"])
        context = self.invoke("hub_records.py", *prefix, "context", "proposal")
        self.assertEqual(4, len(context["records"]))
        self.assertEqual(2, sum(r.get("state") == "missing" for r in context["records"]))

    def test_simultaneous_writers_cannot_both_replace_the_same_version(self):
        hub = self.make_hub("simultaneous-writers")
        result = runtime.write_local_record(hub, "account/profile.md", "Original\n", None)
        barrier = threading.Barrier(2)
        def write(text):
            barrier.wait()
            try:
                return runtime.write_local_record(hub, "account/profile.md", text, result["afterHash"])
            except runtime.VersionConflict as exc:
                return {"state": "conflict-held", "error": str(exc)}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(write, ("Writer one\n", "Writer two\n")))
        (self.attempt / "concurrent-results.json").write_text(json.dumps(results, indent=2))
        self.assertEqual(["conflict-held", "written-and-confirmed"], sorted(r["state"] for r in results))
        self.assertIn((hub / "account/profile.md").read_text(), ("Writer one\n", "Writer two\n"))

    def test_init_keeps_uncommitted_user_work_out_of_automatic_commit(self):
        hub = self.make_hub("idempotent-init", git=True)
        before = subprocess.check_output(["git", "-C", str(hub), "rev-parse", "HEAD"], text=True)
        (hub / "AGENTS.md").write_text("# User edited index\n")
        (hub / "user-note.md").write_text("User work not ready to commit.\n")
        self.invoke("hub_workspace.py", "--json", "init", "--hub", hub, "--opportunity", "opp-second")
        after = subprocess.check_output(["git", "-C", str(hub), "rev-parse", "HEAD"], text=True)
        self.assertEqual(before, after)
        self.assertEqual("# User edited index\n", (hub / "AGENTS.md").read_text())
        manifest = json.loads((hub / "hub.yaml").read_text())
        self.assertFalse(manifest["stores"]["local"]["syncedFilesystem"])

    def test_path_escape_and_unregistered_identity_fail(self):
        hub = self.make_hub("identity-boundary")
        self.invoke("hub_workspace.py", "--json", "init", "--hub", hub,
                    "--opportunity", "../../outside", expected=2)
        result = self.invoke("hub_records.py", "--hub", hub, "--opportunity", "unknown",
                             "read", "opportunity.discovery", expected=1)
        self.assertIn("not registered", result["error"])
        outside = self.attempt / "outside"
        outside.mkdir()
        (hub / "escape").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(runtime.UnsafePath):
            runtime.write_local_record(hub, "escape/record.md", "bad", None)
        self.assertFalse((outside / "record.md").exists())

    def test_drive_update_plan_uses_existing_id_and_never_create(self):
        contract = resolver.ContentUpdateContract(
            "replace_contents", "document_id", "markdown", "if_version")
        capabilities = resolver.detect_capabilities(["replace_contents"], contract)
        plan = resolver.plan_record_write("client.profile", "parent", "# Updated\n",
                    capabilities, existing="# Before\n", update_contract=contract,
                    file_id="synthetic-existing-id", expected_version="revision-2")
        self.assertEqual("replace_contents", plan["tool"])
        self.assertEqual("synthetic-existing-id", plan["arguments"]["document_id"])
        self.assertEqual("revision-2", plan["arguments"]["if_version"])
        self.assertTrue(plan["requiresReadback"])
        (self.attempt / "drive-update-plan.json").write_text(json.dumps(plan, indent=2))
        with self.assertRaises(resolver.ContentUpdateUnsupported):
            resolver.plan_record_write("client.profile", "parent", "# Update\n",
                                      {"content_update": True}, existing="# Before\n")

    def test_manifest_authority_prevents_implicit_local_fallback(self):
        hub = self.make_hub("authority")
        path = hub / "hub.yaml"
        manifest = json.loads(path.read_text())
        manifest["primaryStore"] = "google-drive"
        path.write_text(json.dumps(manifest, indent=2))
        result = self.invoke("hub_records.py", "--hub", hub, "read", "client.front_door", expected=1)
        self.assertIn("unavailable", result["error"])


if __name__ == "__main__":
    unittest.main()
