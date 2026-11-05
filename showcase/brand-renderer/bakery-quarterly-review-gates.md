---
skill: brand-renderer
title: Gating a bakery's quarterly review page against the neutral profile
source: fictional
model: claude-opus-5-5
date: 2026-11-05
skillSha256: a547727f6e59008212becc0315e6d268f90e46080d99d8cd6a54f75ac29cd852
---

## Request

Check this one-page Q3 wholesale review for Harbor Lane Bakery before it goes to the owners. Use the default brand. The 18% growth figure has to keep its "estimated" caveat and its source, and the Saturday delivery cost must stay marked as not priced.

## Inputs

A short HTML page (`draft.html`) and a parity manifest, both written for this run. Harbor Lane Bakery is a made-up company. No project profile was selected, so the runtime used the packaged neutral profile, Baseline. The bundled scripts ran for real: `runtime_preflight.py`, `parity_audit.py` and `brand_check.py`. The prose gate and the visual gate are outside this record.

```json
{"manifestVersion": "1.0",
 "requiredPhrases": ["Two cafe accounts asked for Saturday delivery"],
 "forbiddenPhrases": ["guaranteed growth"],
 "requiredEvidenceReferences": ["invoice export, 2026-10-02"],
 "protectedClaims": [
  {"id": "revenue-growth", "text": "Wholesale orders grew 18% from Q2 to Q3", "requiredQualifiers": ["estimated", "September invoice export"], "selector": "#claim-revenue"},
  {"id": "route-cost", "text": "The route cost", "requiredQualifiers": ["not priced"]}
 ]}
```

The draft's style rules included `border:2px solid #E2E2E3` on the card, `color:#FF7A00` on the growth figure and the heading "Quarterly Wholesale Review". The page had no `main` element and no media queries.

## Output

`runtime_preflight.py --json` [trimmed]: `"ok": true`, `"profile_name": "Baseline"`, `"logo": null`, `"uses_system_fonts": true`, `"missing": []`.

First pass, `parity_audit.py manifest.json draft.html --strict` [trimmed to findings and summary]:

```json
"errors": [
  {"code": "REQUIRED_SELECTOR_MISSING", "detail": "main"},
  {"code": "MAIN_LANDMARK_MISSING", "detail": "A main landmark is required"}
],
"warnings": [
  {"code": "CLAIM_ASSOCIATION_MANUAL_REVIEW", "detail": "route-cost: qualifiers checked globally because no selector was supplied"},
  {"code": "PRINT_QUERY_ABSENT", "detail": "No print media query text found"},
  {"code": "RESPONSIVE_QUERY_ABSENT", "detail": "No width-based media query text found"}
],
"summary": {"errorCount": 2, "warningCount": 3, "lexicalStructuralPass": false, "releasePass": false}
```

Exit 1. `brand_check.py draft.html`:

```
  BRAND CHECK   tokens: authoritative (Baseline)

  draft.html
    FAIL  OFF_PALETTE        draft.html:7  #ff7a00 has no token in the selected brand profile.
    FAIL  BORDER_WIDTH       draft.html:6  border 2px; borders are always 1px.
    warn  TITLE_CASE_HEADING draft.html:11  "Quarterly Wholesale Review" looks title-cased; headings are sentence case.

  FAIL: 2 failure(s), 1 review flag(s)
```

Exit 1. The fixes changed the page, not the claims:

- The content is wrapped in `main`, with a width query and a print query added.
- The card border is now 1px. The growth figure uses the profile's accent token, `#37437D`, and is set in bold.
- The heading is now "Quarterly wholesale review".
- The Saturday delivery paragraph has the id `claim-route`, and the manifest's `route-cost` claim now names that selector, so its "not priced" qualifier is checked inside its own paragraph.

Second pass on `fixed.html`. `parity_audit.py --strict` returns `"errorCount": 0, "warningCount": 0, "lexicalStructuralPass": true, "releasePass": false` and exits 0. `brand_check.py`:

```
  BRAND CHECK   tokens: authoritative (Baseline)

  fixed.html
    clean

  PASS: 0 failure(s), 0 review flag(s)
```

The parity and brand gates pass. `releasePass` is still false by design. Release also needs the prose gate, a look at the rendered page and a release note with a disposition for each gate, and none of those ran here.
