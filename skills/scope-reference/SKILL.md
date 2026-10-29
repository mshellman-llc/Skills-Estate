---
name: scope-reference
description: Build a static scope summary or side-by-side option comparison from current quotes or a dated quote export. Reconciles every scope item, per-option hour value, status and staffing-snapshot price before producing a complete HTML reference. Use for scope matrices, tier comparisons and client leave-behinds. Route selectable proposal experiences to interactive-proposal, deal decision decks to ddoc, contracts to sow and quote changes to scoping-agent.
---

# Scope reference

Produce the reference itself: one self-contained HTML file with the scope matrix visible, plus a printable version when requested. A reader should be able to identify the difference between options and see what each price covers.

Before drafting, read [the build card](../_shared/build-card.md). Keep the commercial writing checks in [the proposal register](../prose-pass/references/registers/sow-proposal.md): preserve exact scope and avoid strengthening a delivery claim. Brand identity comes from the [canonical profile](references/estate/brand.md), resolved through `brand-renderer`. The skill contains no company palette or required logo.

## Resolve the input and mode

Name the client, quote IDs and requested order. One quote produces a single-option summary; several quotes produce a comparison. State the mode when beginning a real request. Do not assume that a more expensive option contains every cheaper option's items. Establish any ascending-scope relationship from the actual matrix.

Use the available quote connector for a current client reference. If it is unavailable, accept a user-supplied export with its source system, revision and capture time. The resulting reference describes that dated export. A local file does not establish current live state. Ask for a fresh export when the requested decision depends on changes since capture; never fabricate a connector or reuse remembered figures.

If neither a connector nor an export supplies the required scope, stop the dependent build and identify the missing records. A synthetic fixture is suitable for testing the skill, not for filling a client quote.

## Capture the full scope

Read [validation.md](validation.md) before assembling data. Save every quote's full item list and its active-item list. With an available scoping connector, this corresponds to `scoping_get_scope_hierarchy` with `activeOnly: false`, `includeHours: true`, `includeFinancials: false`, followed by the active-only read. Use the connector's actual schema; these operation names are an adapter example, not a promise that a tool is installed.

Retain stable item IDs and the quote's own hours. The four states remain distinct:

| State | Meaning |
|---|---|
| Included | Present and selected, without an optional flag. |
| Optional | Explicitly marked optional, even if also returned in the active read. |
| Available | Present but deselected. Adding it may require a price or schedule change. |
| Not included | Absent from that quote's full scope. |

Single-option mode still shows optional and available items when the quote contains them. Do not hide deselected work to force a two-state layout. An absent item in another option is not zero-hour work. The matrix shows each option's hours separately when they differ.

## Resolve price and staffing

List timeline snapshots first and identify the active snapshot ID. Read that snapshot by ID; do not select the newest merely because it was created last. Each displayed staffing variant needs its own actual snapshot, including revenue, currency, duration and staffing hours. Never derive another variant by multiplying a rate.

The headline price comes from the staffing snapshot. Per-item dollars are omitted because back-allocation may drift between snapshots. Item hours are scope estimates; staffing hours can also cover delivery activities. Do not force the two totals to match or infer that an optional item is already priced.

Display exact prices by default. If the user requests rounded prices, show the rounded amount as approximate and preserve the exact quote alongside it. Rounding never changes the working source. Show all requested staffing variants on the static page so printing retains every price and duration. A prospect-facing selector belongs in `interactive-proposal`.

## Reconcile before rendering

Use the source and presentation JSON contract in [validation.md](validation.md). The source holds captured facts; the presentation holds the intended matrix and option copy. The supplied validator compares them independently.

```bash
python3 scripts/scope_reference_validate.py SOURCE.json PRESENTATION.json
python3 scripts/build_scope.py SOURCE.json PRESENTATION.json OUTPUT.html
```

Both commands refuse mismatched item sets or states. They also reject changed names, conflicting IDs, missing description evidence and unsupported snapshot figures. The builder reruns reconciliation before writing. Keep the resulting `.reconciliation.json` with the artifact and inputs. Do not edit the final HTML to bypass a discrepancy.

Report the actual reconcile result and counts. Included and optional counts remain separate from available items. Never label a present-item count as an included-item count.

## Author and build

Read [build-guide.md](build-guide.md). Give each item a concise description grounded in its stored description, effort basis or supplied source. The portable input requires a reference to that evidence. A reference alone does not prove that an authored sentence is faithful; compare its meaning before delivery. For verbatim SOW descriptions, use the exported description field.

Preserve source names in the reconciliation record. If a name contains internal language that cannot appear in client copy, obtain an approved display-name mapping or correct the source. Never silently remove a material scope condition while sanitizing the wording.

Keep assumptions and exclusions that affect the client's choice visible. An unresolved internal issue belongs in the working record, but a condition that changes scope or price cannot be hidden from the reader. Do not recommend an option without supplied decision criteria.

## Inspect and deliver

Run brand preflight and the applicable writing checks through the packaged runtime. Read the complete output against the quote records. Inspect the matrix at desktop and narrow widths, and check every exported PDF page for missing rows or split labels. A clean numeric reconcile does not validate the option summaries.

Follow [the release gate](../_shared/release-gate.md). Keep failed attempts and the actual output alongside the source hashes and review record. Deliver the HTML and requested PDF with the quoted source date. Record any authorized knowledge-hub update separately; creating a local reference does not update the quote or publish it.
