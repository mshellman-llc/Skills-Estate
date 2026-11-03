#!/usr/bin/env python3
"""Self-test for capability-mapping. It uses the standard library and makes no network calls.

Checks that the method and references still carry the maturity scale, the
five dimensions, the gap and band formula and the outputs, that the builder
computes the synthetic fixture as documented, and that invalid models are
refused with named errors. The workbook check runs only when openpyxl is
installed and reports itself as skipped otherwise.

Exit 0 when every case matches, 1 otherwise.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile

SKILL = Path(__file__).resolve().parent.parent
FILES = {name: SKILL / name for name in (
    "SKILL.md", "references/method.md", "references/model-schema.md", "references/workshop-kit.md",
    "references/rendered-outputs.md", "assets/capability-map.html", "fixtures/synthetic-model.json")}
fail: list[str] = []


def expect(label, got, want):
    print(f"  {label:62} got={str(got):<10} want={want}")
    if got != want:
        fail.append(f"{label}: got {got}, want {want}")


for name, path in FILES.items():
    if not path.exists():
        print(f"  missing {name}")
        sys.exit(1)

entry = FILES["SKILL.md"].read_text(encoding="utf-8")
method = FILES["references/method.md"].read_text(encoding="utf-8")
schema = FILES["references/model-schema.md"].read_text(encoding="utf-8")
kit = FILES["references/workshop-kit.md"].read_text(encoding="utf-8")
html = FILES["assets/capability-map.html"].read_text(encoding="utf-8")

fm = re.match(r'^---\nname: capability-mapping\ndescription: "(.*)"\n---\n', entry, re.S)
expect("frontmatter names the skill", bool(fm), True)
if fm:
    expect("description under the 1024 character limit", 0 < len(fm.group(1)) <= 1024, True)
    for owner in ("process", "journey-mapping", "solution-brief"):
        expect(f"description routes the neighbor {owner}", owner in fm.group(1), True)

for level in ("Absent", "Initial", "Repeatable", "Defined", "Managed", "Optimized"):
    expect(f"method keeps maturity level {level}", f"| {level} |" in method, True)
for dim in ("People:", "Process:", "Data:", "Technology:", "Organization:"):
    expect(f"method keeps dimension {dim}", dim in method, True)
for band in ("Invest now", "Plan", "Monitor", "Hold", "Retire review"):
    expect(f"method defines band {band}", band in method, True)
for rule in ("one map for a business", "single occurrence", "Include manual capabilities", "priority_override",
             "Value realization", "votes", "enabling capability", "V2MOM"):
    expect(f"method keeps rule: {rule}", rule in method, True)
for row in ("External activities", "Internal activities", "Pains", "Opportunities", "Capabilities needed"):
    expect(f"workshop board keeps row {row}", row in kit, True)
expect("schema documents computed fields", "final_band" in schema and "priority_score" in schema, True)
expect("starter has the MODEL slot", html.count("const MODEL = {") == 1, True)
expect("starter requests nothing but the Inter font", re.findall(r'(?:src|href)="(https?:[^"]+)"', html),
       ["https://fonts.googleapis.com/css2?family=Inter:wght@400..700&display=swap"])
expect("starter has the Baseline and icon slots", "/*__BASELINE_CSS__*/" in html and "/*__ICONS__*/" in html, True)
expect("starter uses the Baseline root class", '<body class="bl">' in html, True)

for path in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
    for target in re.findall(r"\]\(([^)#]+)\)", path.read_text(encoding="utf-8")):
        if target.startswith(("http", "estate/", "../../", "references/estate/")):
            continue
        expect(f"link resolves: {path.name} -> {target}", (path.parent / target).exists(), True)

spec = importlib.util.spec_from_file_location("builder", SKILL / "scripts" / "build_capability_map.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
model = json.loads(FILES["fixtures/synthetic-model.json"].read_text(encoding="utf-8"))
computed = builder.compute(model)
caps = {c["id"]: c for c in computed["capabilities"]}
expect("parts inventory gap", caps["C-SUP-01"]["gap"], 3)
expect("parts inventory score", caps["C-SUP-01"]["priority_score"], 9)
expect("parts inventory ranks first", caps["C-SUP-01"]["rank"], 1)
expect("parent with children is not scored", caps["C-SVC-01"]["scored"], False)
expect("redundant capability goes to retire review", caps["C-SAL-03"]["final_band"], "Retire review")
expect("override keeps the computed band", (caps["C-SVC-02"]["band"], caps["C-SVC-02"]["final_band"]), ("Plan", "Monitor"))
expect("missing impact is OPEN", caps["C-MKT-03"]["band"], "OPEN")
expect("ties share a rank", caps["C-FIN-01"]["rank"] == caps["C-MKT-02"]["rank"], True)
expect("unlinked goal is found", [f["ref"] for f in computed["findings"] if f["kind"] == "goal-unlinked"], ["G4"])
expect("band counts", computed["summary"]["bands"],
       {"Invest now": 4, "Plan": 1, "Monitor": 4, "Hold": 2, "Retire review": 1, "OPEN": 1})


def refused(mutate, needle):
    bad = copy.deepcopy(model)
    mutate(bad)
    try:
        builder.compute(bad)
    except builder.ModelError as error:
        return any(needle in e for e in error.errors)
    return False


expect("duplicate name is refused", refused(lambda m: m["capabilities"][1].update(name="audience SEGMENTATION and activation"), "repeats the name"), True)
expect("new capability above 0 is refused", refused(lambda m: m["capabilities"][9].update(current=1), "is new"), True)
expect("reported basis without sources is refused", refused(lambda m: m["capabilities"][0].update(sources=[]), "cites no sources"), True)
expect("unknown stage is refused", refused(lambda m: m["capabilities"][0].update(stages=["S99"]), "unknown stage"), True)
expect("a KPI list of non-strings is refused", refused(lambda m: m["capabilities"][0].update(kpis=[3]), "kpis must be a list"), True)
expect("score on a parent is refused", refused(lambda m: m["capabilities"][5].update(current=2), "belongs on the children"), True)

with tempfile.TemporaryDirectory() as tmp:
    result = builder.build(model, Path(tmp) / "out")
    out = Path(tmp) / "out"
    page = (out / "capability-map.html").read_text(encoding="utf-8")
    readout = (out / "capability-readout.md").read_text(encoding="utf-8")
    expect("page embeds the computed model", '"final_band"' in page and '"placeholder": true' not in page, True)
    expect("page inlines the Baseline styles", "/*__BASELINE_CSS__*/" not in page and "--bl-cat-1" in page, True)
    expect("readout lists the Invest now section", "## Invest now" in readout, True)
    expect("readout reports the unlinked goal", "G4 Lower fleet emissions per service visit: no linked capability." in readout, True)
    try:
        builder.build(model, out)
        expect("rebuild into the same directory is refused", False, True)
    except FileExistsError:
        expect("rebuild into the same directory is refused", True, True)
    if result["workbook"] == "written":
        import openpyxl
        ws = openpyxl.load_workbook(out / "capability-assessment.xlsx")["Capabilities"]
        expect("workbook rows equal scored capabilities", ws.max_row - 1, computed["summary"]["scored"])
        expect("workbook score is a live formula", str(ws["L2"].value).startswith("=IF("), True)
        header = [c.value for c in ws[1]]
        parts = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[1] == "C-SUP-01"][0]
        expect("workbook carries the KPIs", parts[header.index("KPIs")], "Repeat part purchases, down; Visits delayed for parts, down")
    else:
        print("  workbook checks skipped: openpyxl is unavailable")

if fail:
    print(f"\n{len(fail)} check(s) failed:")
    for f in fail:
        print("  - " + f)
    sys.exit(1)
print("\nall capability-mapping checks passed")
