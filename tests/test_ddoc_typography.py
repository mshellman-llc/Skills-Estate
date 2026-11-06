"""Check that DDOC comparison and option-detail slides honor the profile's slide minimum.

Every assertion reads the generated PPTX XML (run sizes, text, geometry, emphasis) or an
explicit fit refusal from the builder. Nothing here compares source strings with each other.
"""
import copy
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "skills/build-deal-decision-deck/scripts/build_ddoc.js"
EXAMPLE = ROOT / "skills/build-deal-decision-deck/references/example-decision-manifest.json"
NODE = os.environ.get("ESTATE_NODE") or shutil.which("node")
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
EMU = 914400


def shapes(xml):
    """Each text-bearing or plain shape as {text, runs:[(text, size_pt, bold)], box}."""
    out = []
    for sp in ET.fromstring(xml).iterfind(".//p:sp", NS):
        off = sp.find(".//a:xfrm/a:off", NS)
        ext = sp.find(".//a:xfrm/a:ext", NS)
        box = None if off is None or ext is None else tuple(
            round(int(v) / EMU, 3) for v in (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy")))
        runs = []
        for run in sp.iterfind(".//a:r", NS):
            props = run.find("a:rPr", NS)
            size = props.get("sz") if props is not None else None
            runs.append((run.findtext("a:t", "", NS), int(size) / 100 if size else None,
                         props is not None and props.get("b") == "1"))
        text = "\n".join("".join(t.text or "" for t in para.iterfind(".//a:t", NS))
                         for para in sp.iterfind(".//a:p", NS))
        out.append({"text": text, "runs": runs, "box": box})
    return out


class TypographyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not NODE:
            raise RuntimeError("Node is required; set ESTATE_NODE")
        runs = ROOT / ".local/verification/ddoc"
        runs.mkdir(parents=True, exist_ok=True)
        cls.run_dir = Path(tempfile.mkdtemp(prefix="typography-", dir=runs))
        cls.example = json.loads(EXAMPLE.read_text())
        cls.base = json.loads((ROOT / "examples/build-deal-decision-deck/confirmation.json").read_text())

    def invoke(self, manifest, name, *, env=None):
        file = self.run_dir / (name + ".json")
        file.write_text(json.dumps(manifest, indent=2) + "\n")
        out = file.with_suffix(".pptx")
        result = subprocess.run([NODE, str(BUILDER), str(file), "-o", str(out)],
                                capture_output=True, text=True, cwd=ROOT,
                                env={**os.environ, **(env or {})})
        file.with_suffix(".log").write_text(result.stdout + result.stderr)
        return result, out

    def profile(self, name, minimum):
        text = (ROOT / "policies/brand.md").read_text()
        profile = json.loads(re.search(r"```json\s*\n(.*?)\n```", text, re.S)[1])
        profile["name"] = "Synthetic minimum " + name
        profile["source"] = "Synthetic fixture for typography tests"
        profile["type"]["slide_min_pt"] = minimum
        file = self.run_dir / (name + "-brand.md")
        file.write_text("```json\n" + json.dumps(profile, indent=2) + "\n```\n")
        return {"SKILLS_BRAND_PROFILE": str(file)}

    def slide_xml(self, pptx, title):
        """The slide whose title shape (full-width, at the shared header position) reads `title`.

        Matching any text on the slide would also hit an option name repeated in a comparison
        header, so only the header-position title shape counts.
        """
        with zipfile.ZipFile(pptx) as archive:
            names = sorted((n for n in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                           key=lambda n: int(re.search(r"(\d+)\.xml$", n)[1]))
            for n in names:
                xml = archive.read(n).decode()
                for sp in shapes(xml):
                    box = sp["box"]
                    if sp["text"] == title and box and box[1] == 0.82 and box[3] == 0.56 and box[2] > 8:
                        return xml
        self.fail(f"no slide with a title shape {title!r} in {pptx}")

    def small(self):
        """A short two-option decision manifest, so larger minimums have room to fit."""
        manifest = copy.deepcopy(self.base)
        manifest["mode"] = "decision"
        manifest["options"] += [{"name": "Expanded pilot", "recommended": False,
                                 "duration": "6 weeks", "investment": "$36,000"}]
        manifest["quote_snapshot"]["quote.expanded"] = 36000
        manifest["figures"].append({"label": "Expanded fee", "value": 36000,
                                    "quote_field": "quote.expanded"})
        manifest["slides"] = manifest["slides"][:2] + [
            {"kind": "comparison", "title": "Pilot options",
             "rows": [{"label": "Teams", "values": ["One", "Two"]},
                      {"label": "Training", "values": [False, True]},
                      {"label": "Open defects", "values": [0, 3]}]},
            {"kind": "option_block", "option": "Approval pilot", "title": "Approval pilot",
             "sections": {"Included": ["Configure the approval policy for one team."],
                          "Timeline": ["Four weeks from kickoff."]}},
            {"kind": "option_block", "option": "Expanded pilot", "title": "Expanded pilot",
             "sections": {"Included": ["Configure the approval policy for two teams."],
                          "Timeline": ["Six weeks from kickoff."]}},
            {"kind": "outside_all", "title": "Outside both pilot options",
             "bullets": ["Historical data cleanup requires a separate estimate."]},
            {"kind": "need_from_you", "title": "Inputs for either option",
             "steps": [{"text": "Confirm the routing policy.", "owner": "Sponsor", "when": "Before kickoff"}]},
            {"kind": "decision", "title": "Select the pilot scope",
             "steps": [{"text": "Select the included teams.", "owner": "Sponsor", "when": "Before kickoff"}]},
        ]
        return manifest

    # ------------------------------------------------------------ normal example

    def test_example_comparison_text_is_at_least_18pt_and_complete(self):
        result, pptx = self.invoke(self.example, "example-18")
        self.assertEqual(0, result.returncode, result.stderr)
        slide = next(s for s in self.example["slides"] if s["kind"] == "comparison")
        xml = self.slide_xml(pptx, slide["title"])
        body = [sp for sp in shapes(xml) if sp["text"] != slide["title"]]
        for sp in body:
            for text, size, _ in sp["runs"]:
                if text.strip():
                    self.assertGreaterEqual(size, 18, f"{text!r} is {size} pt")
        rendered = "\n".join(sp["text"] for sp in body)
        for option in self.example["options"]:
            for field in ("name", "duration", "investment"):
                self.assertIn(option[field], rendered)
        for row in slide["rows"]:
            self.assertIn(row["label"], rendered)
            for value in row["values"]:
                self.assertIn(value, rendered)
        self.assertEqual(1, rendered.count("RECOMMENDED"))

    def test_example_comparison_keeps_recommended_emphasis_and_order(self):
        result, pptx = self.invoke(self.example, "example-emphasis")
        self.assertEqual(0, result.returncode, result.stderr)
        slide = next(s for s in self.example["slides"] if s["kind"] == "comparison")
        by_text = {sp["text"]: sp for sp in shapes(self.slide_xml(pptx, slide["title"]))}
        for row in slide["rows"]:
            for i, value in enumerate(row["values"]):
                bold = by_text[value]["runs"][0][2]
                self.assertEqual(i == 1, bold, f"{value!r} emphasis")
            xs = [by_text[v]["box"][0] for v in row["values"]]
            self.assertEqual(sorted(xs), xs)
            self.assertEqual(3, len(set(xs)))
        for row in slide["rows"]:  # one row, one band: every cell shares the row's top
            tops = {by_text[v]["box"][1] for v in row["values"]}
            self.assertEqual(1, len(tops))

    def test_example_option_blocks_are_readable_complete_and_share_geometry(self):
        result, pptx = self.invoke(self.example, "example-options")
        self.assertEqual(0, result.returncode, result.stderr)
        blocks = [s for s in self.example["slides"] if s["kind"] == "option_block"]
        self.assertEqual(3, len(blocks))
        layouts = []
        for block in blocks:
            xml = self.slide_xml(pptx, block["title"])
            found = shapes(xml)
            recommended = next(o for o in self.example["options"] if o["name"] == block["option"])["recommended"]
            for sp in found:
                if sp["text"] in (block["title"],) or not sp["text"]:
                    continue
                for text, size, _ in sp["runs"]:
                    if text.strip():
                        self.assertGreaterEqual(size, 18, f"{block['option']}: {text!r} is {size} pt")
            self.assertEqual(recommended, any(sp["text"] == "RECOMMENDED" for sp in found))
            layout = []
            for key, items in block["sections"].items():
                heading = next(sp for sp in found if sp["text"] == key.upper())
                body = next(sp for sp in found if sp["text"] == "\n".join(items))
                layout.append((key, heading["box"], body["box"]))
            layouts.append(layout)
            self.assertEqual(list(block["sections"]), [k for k, _, _ in layout])
        self.assertEqual(layouts[0], layouts[1])
        self.assertEqual(layouts[1], layouts[2])

    # ----------------------------------------------------------- larger minimum

    def test_larger_profile_minimum_is_applied_to_generated_runs(self):
        env = self.profile("min-24", 24)
        manifest = self.small()
        result, pptx = self.invoke(manifest, "small-24", env=env)
        self.assertEqual(0, result.returncode, result.stderr)
        comparison = manifest["slides"][2]
        xml = self.slide_xml(pptx, comparison["title"])
        body = [sp for sp in shapes(xml) if sp["text"] != comparison["title"]]
        rendered = "\n".join(sp["text"] for sp in body)
        for row in comparison["rows"]:
            self.assertIn(row["label"], rendered)
        for value in ("One", "Two", "0", "3", "—", "●", "6 weeks", "$36,000"):
            self.assertIn(value, rendered)
        for sp in body:
            for text, size, _ in sp["runs"]:
                if text.strip():
                    self.assertGreaterEqual(size, 24, f"{text!r} is {size} pt")
        for block in manifest["slides"][3:5]:
            found = shapes(self.slide_xml(pptx, block["title"]))
            for sp in found:
                if sp["text"] == block["title"]:
                    continue
                for text, size, _ in sp["runs"]:
                    if text.strip():
                        self.assertGreaterEqual(size, 24, f"{text!r} is {size} pt")

    def test_missing_minimum_falls_back_to_18(self):
        text = (ROOT / "policies/brand.md").read_text()
        profile = json.loads(re.search(r"```json\s*\n(.*?)\n```", text, re.S)[1])
        profile["name"] = "Synthetic no minimum"
        profile["source"] = "Synthetic fixture for typography tests"
        del profile["type"]["slide_min_pt"]
        file = self.run_dir / "no-min-brand.md"
        file.write_text("```json\n" + json.dumps(profile) + "\n```\n")
        manifest = self.small()
        result, pptx = self.invoke(manifest, "small-no-min", env={"SKILLS_BRAND_PROFILE": str(file)})
        self.assertEqual(0, result.returncode, result.stderr)
        found = [sp for sp in shapes(self.slide_xml(pptx, "Approval pilot"))
                 if sp["text"] != "Approval pilot"]
        self.assertTrue(any(sp["runs"] for sp in found))
        for sp in found:
            for text, size, _ in sp["runs"]:
                if text.strip():
                    self.assertGreaterEqual(size, 18, f"{text!r} is {size} pt")

    # ------------------------------------------------------------- dense content

    def test_dense_comparison_is_refused_not_shrunk(self):
        manifest = self.small()
        cell = " ".join(["Detailed supported scope statement"] * 12)
        manifest["slides"][2]["rows"] = [{"label": f"Dimension {i}", "values": [cell, cell]}
                                         for i in range(6)]
        result, pptx = self.invoke(manifest, "dense-comparison")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot fit at the 18 pt slide minimum", result.stderr)
        self.assertIn("Pilot options", result.stderr)
        self.assertIn("approved copy revision", result.stderr)
        self.assertNotIn("smaller slide_min_pt", result.stderr)
        self.assertFalse(pptx.exists())

    def test_dense_option_block_is_refused_not_shrunk(self):
        manifest = self.small()
        manifest["slides"][4]["sections"]["Included"] = [
            " ".join(["Configure the approval policy for another team."] * 40)]
        result, pptx = self.invoke(manifest, "dense-option")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot fit at the 18 pt slide minimum", result.stderr)
        self.assertIn("Expanded pilot", result.stderr)
        self.assertFalse(pptx.exists())

    def test_example_is_refused_when_the_minimum_leaves_no_room(self):
        result, pptx = self.invoke(self.example, "example-40", env=self.profile("min-40", 40))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("cannot fit at the 40 pt slide minimum", result.stderr)
        self.assertFalse(pptx.exists())

    def test_invalid_minimum_is_rejected(self):
        result, pptx = self.invoke(self.small(), "bad-min", env=self.profile("min-bad", "large"))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("slide_min_pt", result.stderr)
        self.assertFalse(pptx.exists())


if __name__ == "__main__":
    unittest.main()
