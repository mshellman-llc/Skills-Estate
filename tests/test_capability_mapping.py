"""Exercise the capability-mapping builder, workshop round trip and rendered page."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/capability-mapping"
sys.path.insert(0, str(ROOT / "tools"))
from test_capabilities import integration


def load_builder():
    spec = importlib.util.spec_from_file_location("capability_builder", SKILL / "scripts/build_capability_map.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CapabilityMappingTests(unittest.TestCase):
    def test_selftest_passes(self):
        run = subprocess.run([sys.executable, str(SKILL / "scripts/capability_mapping_selftest.py")],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_cli_refuses_invalid_model_with_named_errors(self):
        model = json.loads((SKILL / "fixtures/synthetic-model.json").read_text())
        model["capabilities"][0]["domain"] = "D99"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps(model))
            run = subprocess.run([sys.executable, str(SKILL / "scripts/build_capability_map.py"), "build", str(path),
                                  "--output-dir", str(Path(tmp) / "out")], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn("unknown domain D99", run.stderr)
            self.assertFalse((Path(tmp) / "out").exists())

    def test_custom_bands_change_the_ranking(self):
        builder = load_builder()
        model = json.loads((SKILL / "fixtures/synthetic-model.json").read_text())
        model["meta"]["priority_bands"] = {"invest_now": 9, "plan": 4, "monitor": 1}
        computed = builder.compute(model)
        bands = {c["id"]: c["final_band"] for c in computed["capabilities"] if c["scored"]}
        self.assertEqual(bands["C-SUP-01"], "Invest now")
        self.assertEqual(bands["C-SAL-01"], "Plan")
        self.assertEqual(computed["summary"]["thresholds"]["invest_now"], 9)

    def test_workshop_capture_round_trip(self):
        try:
            import openpyxl
        except ImportError:
            self.skipTest("openpyxl is unavailable")
        builder = load_builder()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "ws"
            builder.workshop("Awareness, Acquisition", "Workshop", out, "2026-11-02")
            wb = openpyxl.load_workbook(out / "workshop-capture.xlsx")
            self.assertEqual(wb.sheetnames, ["Lifecycle board", "Scoring", "Rubric", "Stages"])
            ws = wb["Scoring"]
            header = [c.value for c in ws[1]]
            row = dict.fromkeys(header)
            row.update({"Capability ID": "C1", "Capability": "Lead management", "Domain": "Sales", "Level": 2,
                        "Definition": "Capture and qualify leads.", "Status": "partial", "Stage IDs": "S1, S2",
                        "Current (0-5)": 1, "Target (0-5)": 3, "Impact": "high", "Basis": "hypothesis", "People": "Red"})
            ws.append([row[h] for h in header])
            wb.save(out / "filled.xlsx")
            merged = builder.ingest(out / "filled.xlsx", json.loads((out / "model.json").read_text()))
            cap = merged["capabilities"][0]
            self.assertEqual((cap["domain"], cap["stages"], cap["dimensions"]), ("D1", ["S1", "S2"], {"people": "red"}))
            self.assertEqual(builder.compute(merged)["capabilities"][0]["priority_score"], 6)
            row.update({"Capability ID": "C2", "Capability": "Quoting", "Stage IDs": "S7"})
            ws.append([row[h] for h in header])
            wb.save(out / "bad.xlsx")
            with self.assertRaises(builder.ModelError) as caught:
                builder.ingest(out / "bad.xlsx", json.loads((out / "model.json").read_text()))
            self.assertTrue(any("unknown stage S7" in e for e in caught.exception.errors))
            with self.assertRaises(FileExistsError):
                builder.workshop("Awareness", "Workshop", out, "2026-11-02")

    @integration("browser")
    def test_rendered_page_views_and_mobile_width(self):
        node = os.environ.get("ESTATE_NODE") or shutil.which("node")
        self.assertTrue(node, "Node is required")
        out = ROOT / ".local/verification/capability-map"
        if out.exists():
            shutil.rmtree(out)
        builder = load_builder()
        builder.build(json.loads((SKILL / "fixtures/synthetic-model.json").read_text()), out / "build")
        runner = out / "check.cjs"
        runner.write_text(r'''
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('playwright');
(async () => {
 const [source, out] = process.argv.slice(2);
 const browser = await chromium.launch(require(process.env.ESTATE_BROWSER_POLICY).launchOptions());
 const page = await browser.newPage({viewport:{width:1440,height:1000}});
 const errors=[]; page.on('pageerror', e => errors.push(e.message));
 try {
  await page.goto(require('url').pathToFileURL(source).href);
  assert.equal(await page.title(), 'Northfield Climate capability map');
  assert.equal(await page.locator('[role=alert]').count(), 0);
  assert.equal(await page.locator('#map .tile').count(), 13);
  assert.equal(await page.locator('.dom').count(), 5);
  assert.equal(await page.locator('#baseline').evaluate(n => n.textContent.includes('--bl-seq-600:#24265B')), true);
  assert.equal(await page.locator('#tokens').count(), 0, 'Baseline tokens are inlined unchanged, not remapped');
  assert.match(await page.locator('#headline').innerText(), /^The first transformation release leaves two of four goals short\.$/);
  assert.equal(await page.locator('#release').isVisible(), true);
  assert.equal(await page.locator('#rel-gaps li').count(), 4, 'Two goals left short and two delivery risks');
  assert.equal(await page.locator('#phase2 li').count(), 6);
  assert.match(await page.locator('#phase2 li').first().innerText(), /Customer self-service[\s\S]*Remaining score 4/);
  assert.equal(await page.locator('#decisions li').count(), 2);
  assert.equal(await page.locator('#gapchart rect:not(.hl)').count(), 13, 'One after-release marker per scored capability with a known current and target');
  assert.equal(await page.locator('#firsts .first').count(), 5);
  assert.match(await page.locator('#firsts .first').first().innerText(), /Service parts inventory management[\s\S]*Invest now, 1 → 4, score 9/);
  assert.match(await page.locator('#firsts .first').last().innerText(), /Work order execution[\s\S]*Plan, 1 → 3, score 4/);
  const tileBg = await page.locator('#map .tile[data-id="C-SUP-01"]').evaluate(n => getComputedStyle(n).backgroundColor);
  assert.equal(tileBg, 'rgb(36, 38, 91)', 'Invest now tiles use bl-seq-600');
  assert.match(await page.locator('#map .tile[data-id="C-MKT-03"]').innerText(), /Score OPEN/);
  assert.match(await page.locator('#map .tile[data-id="C-SAL-03"]').innerText(), /Retire review/);
  assert.equal(await page.locator('#map .tile[data-id="C-SVC-01"]').count(), 0, 'A parent with children is a group label, not a tile');
  await page.hover('#map .tile[data-id="C-SUP-01"]');
  assert.match(await page.locator('#tip').innerText(), /Parts sit in three warehouses/);
  assert.match(await page.locator('#tip').innerText(), /KPIs\s+Repeat part purchases, down; Visits delayed for parts, down/);
  await page.locator('#view label').filter({hasText:'Current maturity'}).click();
  assert.match(await page.locator('#map .tile[data-id="C-SUP-01"]').innerText(), /1 Initial, target 4/);
  await page.locator('#view label').filter({hasText:'Priority'}).click();
  assert.equal(await page.locator('#gapchart g.row').count(), 13);
  assert.match(await page.locator('#goals').innerText(), /Lower fleet emissions per service visit[\s\S]*No capability delivers this goal/);
  assert.equal(await page.locator('#life .stage').count(), 7);
  assert.equal(await page.locator('#why li').count(), 5);
  assert.match(await page.locator('#ranked').evaluate(n => n.textContent), /Monitor \(computed Plan\)/);
  await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  await page.reload();
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth), false);
  assert.equal(await page.locator('#gapchart').evaluate(n => n.scrollWidth > n.clientWidth), true, 'The gap chart scrolls inside its card on a phone');
  await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({passed:true}));
 } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exit(1); });
''')
        env = dict(os.environ, ESTATE_BROWSER_POLICY=str(ROOT / "skills/brand-renderer/scripts/browser_launch_policy.cjs"))
        run = subprocess.run([node, str(runner), str(out / "build/capability-map.html"), str(out)],
                             capture_output=True, text=True, cwd=ROOT, env=env, timeout=120)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
