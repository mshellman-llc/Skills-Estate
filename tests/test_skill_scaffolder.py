"""Exercise authoring from an isolated package, with actual files and refusal cases."""
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
from estate import runtime_dependencies

WORKFLOW = """## When to use
Extract explicit action items from supplied meeting notes.

## Workflow
Read the supplied notes. Include a row only when the notes state a future action.
Copy the named owner and due date literally; use an empty cell when either is absent.
Write UTF-8 CSV with columns action,owner,due_date,source_line.
Quote CSV cells that contain commas. Retain the exact source line for each row.
Check every row against the notes and report the saved file path.
"""


class ScaffolderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="estate-scaffolder-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        self.package = self.folder / "skill-creation-walkthrough"
        assemble(ROOT, "skill-creation-walkthrough", self.package,
                 runtime_dependencies("skill-creation-walkthrough"))
        self.project = self.folder / "project"
        self.project.mkdir()
        self.workflow = self.folder / "workflow.md"
        self.workflow.write_text(WORKFLOW)
        self.count = 0

    def invoke(self, *extra):
        self.count += 1
        command = [sys.executable, str(self.package / "scripts/scaffold_skill.py"),
                   "meeting-actions", "--root", str(self.project),
                   "--display-name", "Meeting actions",
                   "--description", "Extract explicit meeting actions into a CSV when notes are supplied.",
                   "--owner", "Example: author #1", "--category", "analysis",
                   "--runtime", "codex", "--workflow", str(self.workflow), *extra]
        process = subprocess.run(command, cwd=self.folder,
                                 text=True, capture_output=True, timeout=10)
        (self.folder / f"command-{self.count}.json").write_text(json.dumps({
            "command": command, "exit_code": process.returncode,
            "stdout": process.stdout, "stderr": process.stderr}, indent=2))
        return process

    def test_isolated_package_creates_supplied_workflow_and_exact_runtime(self):
        reference = self.folder / "notes.md"
        reference.write_text("Example source. Ada will draft the checklist by Friday.\n")
        process = self.invoke("--reference", str(reference))
        self.assertEqual(process.returncode, 0, process.stderr)
        created = self.project / "skills/meeting-actions"
        entry = (created / "SKILL.md").read_text()
        self.assertIn(WORKFLOW.rstrip(), entry)
        self.assertEqual((created / "references/notes.md").read_bytes(), reference.read_bytes())
        metadata = json.loads((created / "skill.yaml").read_text())
        self.assertEqual(metadata["runtimes"], ["codex"])
        self.assertEqual(metadata["status"], "draft")
        self.assertEqual(metadata["depends_on"], [])
        self.assertEqual(metadata["knowledge_hub"]["requirement"], "not-applicable")
        receipt = json.loads((created / "fixtures/scaffold-receipt.json").read_text())
        self.assertEqual(receipt["runtime_verified"], [])
        self.assertIn('steward: "Example: author #1"', (created / "fixtures/governance.yaml").read_text())
        self.assertEqual(len(list(self.package.rglob("SKILL.md"))), 1)

    def test_existing_skill_and_broken_symlink_are_preserved(self):
        parent = self.project / "skills"
        parent.mkdir()
        destination = parent / "meeting-actions"
        destination.mkdir()
        (destination / "existing.txt").write_text("keep")
        self.assertEqual(self.invoke().returncode, 2)
        self.assertEqual((destination / "existing.txt").read_text(), "keep")
        (destination / "existing.txt").unlink()
        destination.rmdir()
        destination.symlink_to(self.folder / "missing")
        self.assertEqual(self.invoke().returncode, 2)
        self.assertTrue(destination.is_symlink())

    def test_escaping_parent_symlink_is_refused(self):
        outside = self.folder / "outside"
        outside.mkdir()
        (self.project / "skills").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.invoke().returncode, 2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_missing_reference_and_placeholder_workflow_leave_no_skill(self):
        self.assertEqual(self.invoke("--reference", str(self.folder / "absent.md")).returncode, 2)
        self.assertFalse((self.project / "skills").exists())
        self.workflow.write_text("TODO: write the real workflow")
        self.assertEqual(self.invoke().returncode, 2)
        self.assertFalse((self.project / "skills").exists())

    def test_runtime_and_hub_are_explicit_without_claiming_connections(self):
        process = self.invoke("--runtime", "claude-code", "--knowledge-hub", "required")
        self.assertEqual(process.returncode, 0, process.stderr)
        metadata = json.loads((self.project / "skills/meeting-actions/skill.yaml").read_text())
        self.assertEqual(metadata["runtimes"], ["codex", "claude-code"])
        self.assertEqual(metadata["depends_on"], ["knowledge-hub"])
        self.assertEqual(metadata["connectors"]["required"], [])
        self.assertEqual(metadata["knowledge_hub"]["reads"], [])


if __name__ == "__main__":
    unittest.main()
