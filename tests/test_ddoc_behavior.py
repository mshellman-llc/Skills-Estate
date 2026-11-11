"""Exercise the deck gate with source values and inspect generated PPTX content."""
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "skills/ddoc/scripts/build_ddoc.js"
NODE = os.environ.get("ESTATE_NODE") or shutil.which("node")


class DeckBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not NODE:
            raise RuntimeError("Node is required; set ESTATE_NODE")
        runs = ROOT / ".local/verification/ddoc"
        runs.mkdir(parents=True, exist_ok=True)
        # Keep the inputs, generated files, and logs, including failed attempts.
        cls.run_dir = Path(tempfile.mkdtemp(prefix="behavior-", dir=runs))
        cls.base = json.loads((ROOT / "examples/ddoc/confirmation.json").read_text())

    def invoke(self, manifest, name, *, build=False, extra_env=None):
        file = self.run_dir / (name + ".json")
        file.write_text(json.dumps(manifest, indent=2) + "\n")
        args = [NODE, str(BUILDER), str(file)]
        if build:
            args += ["-o", str(file.with_suffix(".pptx"))]
        else:
            args += ["--check"]
        result = subprocess.run(args, capture_output=True, text=True, cwd=ROOT,
                                env={**os.environ, **(extra_env or {})})
        file.with_suffix(".log").write_text(result.stdout + result.stderr)
        return result, file.with_suffix(".pptx")

    def test_missing_quote_source_value_is_rejected(self):
        manifest = copy.deepcopy(self.base)
        del manifest["quote_snapshot"]
        result, _ = self.invoke(manifest, "missing-quote")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("no source value", result.stderr)

    def test_conflicting_quote_value_is_rejected(self):
        manifest = copy.deepcopy(self.base)
        manifest["quote_snapshot"]["quote.total"] = 25000
        result, _ = self.invoke(manifest, "conflicting-quote")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("does not match quote_snapshot", result.stderr)

    def test_seller_inference_cannot_render_as_client_statement(self):
        manifest = copy.deepcopy(self.base)
        manifest["slides"][0]["items"][0]["evidence"] = "inferred"
        result, _ = self.invoke(manifest, "inferred-heard")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("Only client_stated", result.stderr)

    def decision(self):
        manifest = copy.deepcopy(self.base)
        manifest["mode"] = "decision"
        manifest["options"] += [{"name": "Expanded pilot", "recommended": False,
                                "duration": "6 weeks", "investment": "$36,000"}]
        manifest["quote_snapshot"]["quote.expanded"] = 36000
        manifest["figures"].append({"label": "Expanded fee", "value": 36000, "quote_field": "quote.expanded"})
        manifest["slides"] = manifest["slides"][:2] + [
            {"kind": "comparison", "title": "Pilot options",
             "rows": [{"label": "Teams", "values": ["One", "Two"]}]},
            {"kind": "option_block", "option": "Approval pilot", "title": "Approval pilot",
             "sections": {"Included": ["Configure the approval policy for one team."]}},
            {"kind": "option_block", "option": "Expanded pilot", "title": "Expanded pilot",
             "sections": {"Included": ["Configure the approval policy for two teams."]}},
            {"kind": "outside_all", "title": "Outside both pilot options",
             "bullets": ["Historical data cleanup requires a separate estimate."]},
            {"kind": "need_from_you", "title": "Inputs for either option",
             "steps": [{"text": "Confirm the routing policy.", "owner": "Sponsor", "when": "Before kickoff"}]},
            {"kind": "decision", "title": "Select the pilot scope",
             "steps": [{"text": "Select the included teams.", "owner": "Sponsor", "when": "Before kickoff"}]},
        ]
        return manifest

    def test_option_word_count_reads_actual_content(self):
        manifest = self.decision()
        manifest["slides"][4]["sections"]["Included"] = ["Additional supported detail. " * 30]
        result, _ = self.invoke(manifest, "unbalanced-options")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("option_block word counts range", result.stdout)

    def test_confirmation_build_contains_required_copy_and_neutral_brand(self):
        result, pptx = self.invoke(self.base, "confirmation-built", build=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.inspect_deck(pptx, self.base, "#2F5D8A")

    def test_decision_build_contains_both_options(self):
        manifest = self.decision()
        result, pptx = self.invoke(manifest, "decision-built", build=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.inspect_deck(pptx, manifest, "#2F5D8A")

    def test_separate_scope_slides_keep_their_bullets(self):
        manifest = copy.deepcopy(self.base)
        scope_index = next(i for i, s in enumerate(manifest["slides"]) if s["kind"] == "scope")
        manifest["slides"][scope_index:scope_index + 1] = [
            {"kind": "scope_in", "title": "Included work",
             "bullets": ["Configure the approval policy for one team."]},
            {"kind": "scope_out", "title": "Excluded work",
             "bullets": ["Additional teams need a separate estimate."]},
        ]
        manifest["slides"][2] = {"kind": "outcomes", "title": "Expected outcome",
                                 "bullets": ["Every pilot request has a named approver."]}
        result, pptx = self.invoke(manifest, "separate-scope", build=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.inspect_deck(pptx, manifest, "#2F5D8A")
        with zipfile.ZipFile(pptx) as archive:
            xml = "".join(archive.read(n).decode() for n in archive.namelist()
                          if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
        for text in ("Configure the approval policy for one team.",
                     "Additional teams need a separate estimate.",
                     "Every pilot request has a named approver."):
            self.assertIn(text, xml)

    def test_alternate_profile_changes_actual_pptx(self):
        text = (ROOT / "policies/brand.md").read_text()
        profile = json.loads(re.search(r"```json\s*\n(.*?)\n```", text, re.S)[1])
        profile["name"] = "Synthetic copper"
        profile["source"] = "Synthetic fixture for renderer tests"
        profile["colors"]["accent"] = "#7B321A"
        profile["type"]["office"] = "Helvetica"
        file = self.run_dir / "copper-brand.md"
        file.write_text("```json\n" + json.dumps(profile, indent=2) + "\n```\n")
        result, pptx = self.invoke(self.base, "confirmation-copper", build=True,
                                  extra_env={"SKILLS_BRAND_PROFILE": str(file)})
        self.assertEqual(0, result.returncode, result.stderr)
        self.inspect_deck(pptx, self.base, "#7B321A", font="Helvetica")
        with zipfile.ZipFile(pptx) as archive:
            slide_xml = "".join(archive.read(n).decode() for n in archive.namelist()
                                if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
        self.assertNotIn("2F5D8A", slide_xml)

    def inspect_deck(self, file, manifest, accent, font="Arial"):
        with zipfile.ZipFile(file) as archive:
            slides = [n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]
            self.assertEqual(len(manifest["slides"]) + 1, len(slides))
            xml = "\n".join(archive.read(n).decode() for n in slides)
            metadata = archive.read("docProps/core.xml").decode() + archive.read("docProps/app.xml").decode()
        self.assertNotIn("aleysian", (xml + metadata).lower())
        self.assertNotIn("Plus Jakarta Sans", xml)
        self.assertIn(accent.lstrip("#"), xml)
        self.assertIn(f'typeface="{font}"', xml)
        for slide in manifest["slides"]:
            self.assertIn(slide["title"], xml)
        for option in manifest["options"]:
            self.assertIn(option["name"], xml)


if __name__ == "__main__":
    unittest.main()
