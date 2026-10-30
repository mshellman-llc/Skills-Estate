# Release gates

Three gates, both modes, every time. None of them authorizes release alone. A clean tool run
proves the mechanical floor and nothing above it, so each gate ends in a disposition you wrote,
not an exit code you read.

Run them. Do not narrate them. Report the result and the dispositions.

## Why the gate wiring is spelled out here

Writing Integrity owns the prose review. Its retained internal `prose-pass` runtime consolidated the older
separate checkers: `../prose-pass/scripts/prose_check.py` gates the mechanical and
structural tells against `house.json`, and `../prose-pass/scripts/rewrite_scan.py --tie-out`
reconciles figures. Do not keep
a local word list; prose-pass is the single authoritative home.

## Gate 1: parity

Every number, name, source reference, and protected caveat that must survive the render is listed
in a manifest, and the gate proves it survived. Write the manifest before the HTML. Deciding what
must survive is a scoping act, and doing it first changes what you build.

```bash
S=../brand-renderer/scripts   # parity_audit lives in the brand-renderer sibling skill
python3 $S/parity_audit.py manifest.json page.html --strict
```

Manifest shape, per `brand-renderer` schema 1.0:

```json
{
  "manifestVersion": "1.0",
  "artifactId": "synthetic-scope-explorer",
  "decisionJob": "interactive_proposal",
  "requiredPhrases": ["28", "33", "35", "No pricing on this page"],
  "forbiddenPhrases": ["$"],
  "requiredEvidenceReferences": ["REQ-EXAMPLE-001"],
  "requiredSelectors": ["main", "h1"],
  "requiredViews": ["hero-default", "hero-last-version", "scope-excluded", "sources-open"]
}
```

Two gotchas that cost time if you meet them cold:

- **The schema rejects unknown keys, comment keys included.** Adding `_note` or `_comment` fails as
  `AUDIT_CONFIGURATION_ERROR`. Keep commentary in this file.
- **Do not copy the banned-vocabulary list into `forbiddenPhrases`.** The lexicon lives in
  `rewrite_scan.py` and gate 3 enforces it. A manifest carrying those words makes gate 3 fail on the
  manifest. Use `forbiddenPhrases` only for what is specific to this page, such as `$` in explorer
  mode or a competitor name that must not print.

Mode-specific content:

- **Proposal mode.** Every version total goes in `requiredPhrases`, formatted exactly as it
  renders. `requiredEvidenceReferences` carries the Q-number.
- **Explorer mode.** `$` goes in `forbiddenPhrases`. This is the check that makes the no-pricing
  promise mechanical instead of aspirational. `requiredEvidenceReferences` carries the Opportunity
  Id and the source document filename.

`requiredSelectors` defaults to `["main","h1"]`, so the page skeleton must carry a `<main>`
landmark. This is the most commonly missed error in this skill.

**Proposal mode also runs figure tie-out.**

```bash
python3 ../prose-pass/scripts/rewrite_scan.py --tie-out quote_export.json page.html
```

A figure on the page that is not in the quote is invention and a hard fail. A quote figure missing
from the page is a warning: confirm the omission was a choice.

## Gate 2: visual

Run `scripts/qa_proposal.py` and inspect its saved views in every version state. Lexical checks cannot prove
that something is visible, unclipped, and attached to its qualifier.

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 1000})
    pg.goto("file:///abs/path/page.html"); pg.wait_for_timeout(1200)
    pg.screenshot(path="qa-hero-default.png", clip={"x":0,"y":0,"width":1280,"height":1000})
    for k in ["B", "C"]:                      # every version tab, not just the first
        pg.click(f'.tab[data-k="{k}"]'); pg.wait_for_timeout(900)
        pg.screenshot(path=f"qa-hero-{k}.png", clip={"x":0,"y":0,"width":1280,"height":1000})
    pg.click('.tab[data-k="A"]'); pg.wait_for_timeout(700)     # leanest version
    pg.screenshot(path="qa-scope-excluded.png", full_page=True)
    pg.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
    pg.wait_for_timeout(400); pg.screenshot(path="qa-sources-open.png", full_page=True)
    pg.pdf(path="print-test.pdf", format="Letter", print_background=True)
    pg.set_viewport_size({"width": 390, "height": 900}); pg.wait_for_timeout(400)
    pg.screenshot(path="qa-mobile.png", clip={"x":0,"y":0,"width":390,"height":900})
    b.close()
```

Then open the images and check, in this order:

1. The default version state and every other version state. A switcher that looks right on tab one
   and breaks on tab three is the signature failure of this page type.
2. Excluded scope in the leanest version. It must read as deliberately absent, not as a rendering
   fault: dashed border, "not in this version" label, still legible.
3. The metric. It must sit on the exact target value, not on a tween frame.
4. Disclosures open. Long routes and audit rows are where overflow hides.
5. The print PDF. Page count, no orphaned headings, dark surfaces still dark.
6. Mobile at 390px. The version tabs and the metric break first.

Record which views you inspected. `requiredViews` raises the reminder; your disposition closes it.

## Gate 3: prose

```bash
python3 ../prose-pass/scripts/prose_check.py page.html --config ../prose-pass/house.json
python3 ../prose-pass/scripts/rewrite_scan.py page.html --quiet
```

Strong tells block. Review flags each need a written disposition. The flags this page type raises
most, and how to think about them:

- **RULE_OF_THREE.** A real field list is a real field list. "Project name, project type, delivery
  address" is enumeration. "Fast, scalable, and reliable" is rhetoric. Cut the second kind only.
- **RHETORICAL_QUESTION.** Decision headings phrased as the question the client must answer are
  load-bearing and stay. Questions used as transitions go.
- **ABSOLUTE_OVERSTATEMENT.** Confirm each is literally true. "Zero currency on the page" is true
  and provable by the parity gate. "Every requirement covered" needs the count behind it.
- **VAGUE_THIS_OPENER.** Name the subject. On a page a prospect skims, "This means" costs you the
  sentence.

Then read it. The scanner cannot see genericity, and genericity is what loses. Every sentence
should carry a number, a named system, a named owner, or a consequence. A sentence that could
appear in any consultancy's proposal is a defect even when it passes every check.

## The release note

Four lines, kept with the deliverable:

```
Parity   0 errors, 1 warning (visual reminder, closed by 6 inspected views)
Visual   6 views + print PDF inspected at 1280 and 390
Prose    0 strong tells, 5 review flags dispositioned (6 questions load-bearing, 37 triads
         are field enumerations, 4 absolutes verified literal)
Tie-out  n/a in explorer mode, no quote exists
```

## Synthetic regression example

`synthetic-scope-explorer.manifest.json` describes the bundled fictional scope fixture. Run the packaged builder and `scripts/qa_proposal.py` to generate current evidence. Historical examples do not prove the current build works.
