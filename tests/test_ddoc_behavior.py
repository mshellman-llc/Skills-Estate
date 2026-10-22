"""Exercise the deck gate with source values and inspect generated PPTX content."""
import base64
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
# A valid 1x1 PNG, so the synthetic logo is a real image.
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")


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

    def comparison_case(self, name, rows):
        manifest = self.decision()
        slide = manifest["slides"][2]
        if rows is None:
            del slide["rows"]
        else:
            slide["rows"] = rows
        return self.invoke(manifest, name)

    def test_comparison_without_usable_rows_is_rejected(self):
        for name, rows, message in (
            ("absent", None, "has no rows"),
            ("empty", [], "has no rows"),
            ("blank-label", [{"label": "  ", "values": ["One", "Two"]}], "blank label"),
            ("missing-label", [{"values": ["One", "Two"]}], "blank label"),
            ("missing-cell", [{"label": "Teams", "values": ["One"]}], "1 cells for 2 options"),
            ("extra-cell", [{"label": "Teams", "values": ["One", "Two", "Three"]}], "3 cells for 2 options"),
            ("no-values", [{"label": "Teams"}], "no values array"),
            ("blank-cell", [{"label": "Teams", "values": ["One", " "]}], "cell 2 is blank"),
            ("null-cell", [{"label": "Teams", "values": ["One", None]}], "cell 2 is blank"),
        ):
            with self.subTest(case=name):
                result, _ = self.comparison_case("comparison-" + name, rows)
                self.assertNotEqual(0, result.returncode)
                self.assertIn(message, result.stderr)

    def test_comparison_keeps_false_and_zero_cells(self):
        rows = [{"label": "Includes training", "values": [False, True]},
                {"label": "Open defects", "values": [0, 3]}]
        manifest = self.decision()
        manifest["slides"][2]["rows"] = rows
        result, pptx = self.invoke(manifest, "comparison-false-zero", build=True)
        self.assertEqual(0, result.returncode, result.stderr)
        with zipfile.ZipFile(pptx) as archive:
            xml = archive.read("ppt/slides/slide4.xml").decode()
        for text in ("Includes training", "Open defects", "<a:t>0</a:t>", "<a:t>3</a:t>", "<a:t>—</a:t>", "<a:t>●</a:t>"):
            self.assertIn(text, xml)

    def test_rendered_comparison_contains_labels_and_cells(self):
        manifest = self.decision()
        result, pptx = self.invoke(manifest, "comparison-rendered", build=True)
        self.assertEqual(0, result.returncode, result.stderr)
        with zipfile.ZipFile(pptx) as archive:
            xml = archive.read("ppt/slides/slide4.xml").decode()
        for row in manifest["slides"][2]["rows"]:
            self.assertIn(row["label"], xml)
            for value in row["values"]:
                self.assertIn(value, xml)

    def test_decision_example_renders_its_comparison_from_option_blocks(self):
        example = json.loads((ROOT / "skills/ddoc/references/example-decision-manifest.json").read_text())
        comparison = next(s for s in example["slides"] if s["kind"] == "comparison")
        blocks = {s["option"]: s["sections"] for s in example["slides"] if s["kind"] == "option_block"}
        names = [o["name"] for o in example["options"]]
        sources = {"In scope": "In scope", "Not in scope": "Not in scope", "Assumptions": "Assumptions"}
        self.assertEqual(list(sources), [r["label"] for r in comparison["rows"]])
        for row in comparison["rows"]:
            self.assertEqual([blocks[n][sources[row["label"]]][0] for n in names], row["values"])
        result, pptx = self.invoke(example, "comparison-example", build=True)
        self.assertEqual(0, result.returncode, result.stderr)
        with zipfile.ZipFile(pptx) as archive:
            xml = archive.read("ppt/slides/slide4.xml").decode()
        for row in comparison["rows"]:
            self.assertIn(row["label"], xml)
            for value in row["values"]:
                self.assertIn(value, xml)

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

    def profile_with_logo(self, name, logo):
        """Write a synthetic profile in its own directory; return (profile file, directory)."""
        text = (ROOT / "policies/brand.md").read_text()
        profile = json.loads(re.search(r"```json\s*\n(.*?)\n```", text, re.S)[1])
        profile["name"] = "Synthetic logo " + name
        profile["source"] = "Synthetic fixture for logo preflight tests"
        profile["logo"] = logo
        directory = self.run_dir / name
        directory.mkdir()
        file = directory / "brand.md"
        file.write_text("```json\n" + json.dumps(profile, indent=2) + "\n```\n")
        return file, directory

    def check_with_logo(self, name, logo, *, build=False):
        file, directory = self.profile_with_logo(name, logo)
        return directory, *self.invoke(self.base, name + "-deck", build=build,
                                       extra_env={"SKILLS_BRAND_PROFILE": str(file)})

    def test_null_logo_profile_passes_preflight(self):
        result, _ = self.invoke(self.base, "null-logo")
        self.assertEqual(0, result.returncode, result.stderr)

    def test_missing_declared_logo_fails_check_with_asset_path(self):
        directory, result, pptx = self.check_with_logo("missing-logo", "assets/absent.png")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("declared logo does not exist", result.stderr)
        self.assertIn(str(directory.resolve() / "assets/absent.png"), result.stderr)
        self.assertFalse(pptx.exists())

    def test_missing_declared_logo_fails_build_before_rendering(self):
        directory, result, pptx = self.check_with_logo("missing-logo-build", "absent.png", build=True)
        self.assertNotEqual(0, result.returncode)
        self.assertIn(str(directory.resolve() / "absent.png"), result.stderr)
        self.assertNotIn("renderer is unavailable", result.stderr)
        self.assertFalse(pptx.exists())

    def test_logo_resolves_against_profile_directory_not_cwd(self):
        other = self.run_dir / "elsewhere"
        other.mkdir()
        (other / "logo.png").write_bytes(PNG)
        directory, result, _ = self.check_with_logo("relative-logo", "logo.png")
        self.assertNotEqual(0, result.returncode)
        self.assertIn(str(directory.resolve() / "logo.png"), result.stderr)

    def test_logo_directory_is_rejected(self):
        file, directory = self.profile_with_logo("directory-logo", "logo.png")
        (directory / "logo.png").mkdir()
        result, _ = self.invoke(self.base, "directory-logo-deck",
                                extra_env={"SKILLS_BRAND_PROFILE": str(file)})
        self.assertNotEqual(0, result.returncode)
        self.assertIn(str(directory.resolve() / "logo.png"), result.stderr)

    @unittest.skipIf(not hasattr(os, "geteuid") or os.geteuid() == 0, "permissions are not enforced")
    def test_unreadable_declared_logo_fails_check(self):
        file, directory = self.profile_with_logo("unreadable-logo", "logo.png")
        logo = directory / "logo.png"
        logo.write_bytes(PNG)
        logo.chmod(0)
        self.addCleanup(logo.chmod, 0o600)
        result, _ = self.invoke(self.base, "unreadable-logo-deck",
                                extra_env={"SKILLS_BRAND_PROFILE": str(file)})
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot be read", result.stderr)
        self.assertIn(str(directory.resolve() / "logo.png"), result.stderr)

    def test_valid_synthetic_logo_passes_preflight_in_both_forms(self):
        for name, declared in (("string-logo", "logo.png"), ("object-logo", {"path": "logo.png"})):
            with self.subTest(form=name):
                file, directory = self.profile_with_logo(name, declared)
                (directory / "logo.png").write_bytes(PNG)
                result, _ = self.invoke(self.base, name + "-deck",
                                        extra_env={"SKILLS_BRAND_PROFILE": str(file)})
                self.assertEqual(0, result.returncode, result.stderr)

    def test_valid_synthetic_logo_is_embedded_in_built_deck(self):
        file, directory = self.profile_with_logo("built-logo", "logo.png")
        (directory / "logo.png").write_bytes(PNG)
        result, pptx = self.invoke(self.base, "built-logo-deck", build=True,
                                   extra_env={"SKILLS_BRAND_PROFILE": str(file)})
        self.assertEqual(0, result.returncode, result.stderr)
        with zipfile.ZipFile(pptx) as archive:
            self.assertTrue([n for n in archive.namelist() if n.startswith("ppt/media/")])

    def test_every_shipped_example_passes_preflight(self):
        examples = sorted((ROOT / "skills/ddoc/references").glob("example-*.json"))
        self.assertGreaterEqual(len(examples), 1)
        for example in examples:
            with self.subTest(example=example.name):
                result, _ = self.invoke(json.loads(example.read_text()), "shipped-" + example.stem)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertIn("0 failures", result.stdout)

    def test_decision_example_options_amounts_and_durations_match_its_quote(self):
        example = json.loads((ROOT / "skills/ddoc/references/example-decision-manifest.json").read_text())
        snapshot = set(example["quote_snapshot"].values())
        weeks = {"12": "Twelve", "17": "Seventeen", "24": "Twenty four"}
        blocks = {s["option"]: s for s in example["slides"] if s["kind"] == "option_block"}
        for option in example["options"]:
            with self.subTest(option=option["name"]):
                self.assertIn(int(re.sub(r"\D", "", option["investment"])), snapshot)
                number = option["duration"].split()[0]
                self.assertTrue(blocks[option["name"]]["sections"]["Timeline"][0].startswith(weeks[number]))
        recommended = next(o for o in example["options"] if o["recommended"])
        text = json.dumps(example["slides"])
        self.assertIn(("We recommend " + recommended["name"]).lower(), text.lower())
        self.assertNotIn("Tier", text)

    def test_confirmation_examples_carry_snapshot_values_for_their_investment(self):
        for name in ("confirmation-manifest", "ai-readiness", "org-assessment"):
            with self.subTest(example=name):
                example = json.loads((ROOT / f"skills/ddoc/references/example-{name}.json").read_text())
                figure = example["figures"][0]
                self.assertEqual(figure["value"], example["quote_snapshot"][figure["quote_field"]])
                amount = next(s for s in example["slides"] if s["kind"] == "investment")["amount"]
                self.assertEqual(figure["value"], int(re.sub(r"\D", "", amount)))
                self.assertIn("need_from_you", [s["kind"] for s in example["slides"]])

    def test_documentation_matches_builder_order_and_checks(self):
        patterns = (ROOT / "skills/ddoc/references/ddoc-patterns.md").read_text()
        section = patterns.split("## Confirmation mode skeleton")[1].split("## Structural rules")[0]
        order = [section.index(f"`{kind}`") for kind in
                 ("investment", "assumptions", "need_from_you", "confirm")]
        self.assertEqual(sorted(order), order)
        skill = (ROOT / "skills/ddoc/SKILL.md").read_text()
        self.assertNotIn("retired role", skill)
        self.assertIn("declared profile logo", skill)

    def test_touched_references_carry_no_private_names_or_placeholder_provider(self):
        banned = ("Pewag", "Aleysian", "Meridian", "Estate issues", "Estate has", "Estate team",
                  "Estate-Brand", "Jim ")
        for file in (ROOT / "skills/ddoc/references").iterdir():
            with self.subTest(file=file.name):
                text = file.read_text()
                for word in banned:
                    self.assertNotIn(word, text)

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
