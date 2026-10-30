---
name: sow
description: 'Generate Statements of Work (.docx) from a confirmed quote JSON and a selected contract profile, in Waterfall (fixed scope), Agile (adaptive scope), and Assess (advisory, readout-gated) variants. Use when asked to generate the SOW, draft the SOW from the quote, build the SOW for a Q-number, or turn a quote into a Statement of Work. The quote is the source of truth; this skill renders it, does not price (the Pricing System prices), and does not author scope language (scoping-agent does). It builds the .docx, resolves placeholders with an audit trail, verifies the required-clause gate, and hands off to the embedded contract review mode. For authoring quality review, select the embedded contract scope and obligation review mode; DDOC remains a deck workflow.'
---


# Statement of work

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`sow-proposal.md`](../prose-pass/references/registers/sow-proposal.md). Inputs, not a final pass.**

Draft or generate the requested editable statement of work from the current quote,
confirmed scope baseline, contracting entities, approved template and applicable
agreement. The selected sources govern numbers, scope, acceptance and payment terms.
This workflow does not invent pricing or scope commitments.

## Select a supported production route

Build a source-to-document mapping for scope, deliverables, responsibilities,
acceptance, timeline, pricing, payment milestones, assumptions, exclusions and change
control. Resolve revisions and conflicting sources before asserting final terms.
Use the available document tool with the supplied template for ordinary drafting,
revisions, or agreements that do not fit this generator's input contract. Missing
entity details or approved terms permit a clearly labeled draft with unresolved
fields visible. Preserve contractual meaning and mandated wording, including its
punctuation. Historical clauses and example profiles supply no approval.

The optional generator below supports only its documented model and contract-profile
shape. Use it when that shape faithfully represents the actual agreement. Its fixed
variant structures, reconciliation requirements, upfront field or Exhibit A layout
must not create a payment term, acceptance rule, scope cap or requirement for an
existing CRM record. In particular, an independently sourced fixed fee may differ from hours times
rate; this generator's per-role revenue equality cannot represent that model.
Preserve the agreed fee and use the document-tool route for it. If other supplied
terms cannot be represented faithfully, use the document-tool route; do not force the agreement into the generator or fill missing
values from examples. For either route reconcile totals and milestones, inspect
cross-references and placeholders, compare required clauses with the supplied template,
then run the embedded contract review. Inspect every rendered page before finalizing.
Creating a document does not approve, send or execute it.

The following variant and CLI sections describe the optional generator. The selected
agreement remains controlling; unsupported terms require the document-tool route.

## Variants

Four, passed as the second CLI argument to `scripts/generate_sow.js`. One generator handles all four by branching internally; there is no separate builder file per variant.

- **Letter of engagement** (`loe`), a short fixed-fee advisory engagement under the selected agreement. Carries scope, fee, timing, assumptions, selected agreement terms, acceptance, and signatures. It does not silently inherit the full SOW clause set.
- **Waterfall** (`waterfall`), fixed-scope build. Phase-gated, Exhibit A basis of estimate, UAT gates production. The default.
- **Agile** (`agile`), adaptive build. Sprint stages, backlog, same Exhibit A discipline.
- **Assess** (`assess`), advisory engagement. Assessments and strategy plays. It differs structurally from the build variants and is not a tuning of them:
  - Delivery methodology is Discover, Assess, Recommend stages, not build phases. The stages describe analysis flow and carry no phase gates.
  - Deliverables are the actual scope items from the quote, not the fixed build artifact set.
  - Acceptance is **readout-gated**: the deliverables are accepted on completion of the executive readout. No defect severity, no UAT, no production gate.
  - Scope is fixed by the **Section 4 deliverable list**. There is **no Exhibit A**; an assessment is not sized by volumetrics like "up to N products".
  - Fee model is **fixed fee**. A conflicting T&M quote fails rather than being changed by the renderer.

The contract shell is shared across every variant: parties and notice, Sections 1, 2, 6, 7, 11, the Miscellaneous Terms, and the signature block. Only the build-specific middle changes.

## Input: the quote model

The generator reads one JSON file, the quote model. `fixtures/quote.example.json` is a runnable synthetic example; copy its shape and replace it with sourced engagement data. `fixtures/assessment.example.json` exercises the advisory variants. The older rich/degraded models under `scripts/` remain source-shape references; they need the additional context fields below before rendering.

```bash
node scripts/generate_sow.js fixtures/quote.example.json waterfall \
  --contract fixtures/contract.example.json --example --output output/example-sow.docx
```

**Required.** Structural or financial inconsistencies stop the build. Unresolved narrative fields also stop the build unless `--draft` was explicitly requested. A draft is visibly marked and cannot pass the contract verifier.

| Path | Notes |
|---|---|
| `source.reference` | Confirmed quote identifier and revision, or a clearly synthetic fixture reference |
| `projectContext` | `accountName`, `opportunityName`, `quoteName`, `businessNeed`, `businessDriver`, `psaEffectiveDate`, `clientAddress`, `clientContact`, `primaryContact`, `executiveSponsor`, `providerLead`, `accountsPayable`, `testScriptOwnership`, `returnBy` |
| `pricingModel` | Explicit `tm` or `fixed`; assessment and letter variants require `fixed` |
| `deliveryMethodology`, `scopeNote` | Confirmed method and supporting activities; do not turn a generic delivery template into scope |
| `deliverables[]` | Confirmed `name`, `description`, `format`; required for build variants |
| `projectSummary` | `totalValue`, `totalHours`, `durationWeeks`, `teamSize`, `totalScopeItems` |
| `timeline.summary.blendedRate` | Printed against the calculated rate for comparison |
| `timeline.bands[0]` | `startDate`, `endDate` |
| `timeline.bands[0].phases[]` | `name`, `weeks`, `weekNumbers[]`, `purpose` |
| `timeline.bands[0].resources[]` | `role`, `titleLevel`, `billRate`, `totalHours`, `totalRevenue`, `hoursByPhase{}`, `responsibility`; optional explicit `discountAmount` |
| `scopeItemsByCapability[]` | `name`, `children[]`, `scopeItems[]` each with `name`, `description`, `assumptions` |

`description` and `assumptions` accept HTML (`<p>`, `<li>`) or plain text with `-` bullets.

**Optional.** Each of these replaces a mined or inferred value, and every substitution is logged.

`platform`, `targetPlatform`, `sourceSystem`, `engagementType`, `engagementDriver`, `purposeNarrative`, `engagementBoundary`, `boundarySummary`, `exclusions[]`, `changeOrderTriggers[]`, `basisOfEstimate[{dimension, footprint}]`, `locBasisNote`, `exhibitA[{text, item}]`.

**The three-way tie.** The generator reconciles before it renders, and prints PASS or FAIL. The model must satisfy all of:

- every resource's `hoursByPhase` values sum to its own `totalHours`; offsetting errors in different roles do not cancel
- each resource's hours times rate, less an explicit discount, equals its revenue
- the sum of all `totalHours` equals `projectSummary.totalHours`
- the sum of all `totalRevenue` equals `projectSummary.totalValue`

A failure writes a diagnostic build record and produces no DOCX. Return the discrepancy to the quote owner; do not substitute a recomputed commercial commitment. The source blended rate and scope count must also reconcile.

### Build the model from the available quote source

A local JSON export in the documented shape is sufficient. No proprietary scoping application or live connector is required. If the connected pricing system exposes the following tools, use its current export contract; these names describe an optional adapter, not tools this skill guarantees are installed. Confirm one quote revision and one selected band before filling gaps.

| Tool | Returns | When |
|---|---|---|
| `scoping_get_sow_data` | `projectContext`, `projectSummary`, `scopeItemsByCapability`, and `timeline` with bands, phases, and resources | Always, first |
| `scoping_get_scope_hierarchy` | Per-item hours and financials, with `includeHours:true` and `includeFinancials:true` | For the Section 9 fee tables |
| `scoping_get_quote` | Quote-level resources and the rate-card grid | When the fee table needs the resource grid |
| `scoping_manage_scope_items` | Write-back of a corrected description or assumption | On request, with confirmation, never silent |

Given a Q-number rather than a record Id, resolve it first with a SOQL query on `Quote__c.Name`.

**Read every rate from the quote.** Never hardcode a role rate; rates move in the live data, so memory is not a source.

**Discrepancy handling.** Stop the build and retain the diagnostic record. Obtain a corrected source model from the owner. Never change an authorized figure to make the document reconcile.

## Workflow

1. **Read the quote** from its confirmed local export or available pricing-system adapter. Confirm the Q-number, the active timeline snapshot, the scope line items, and the total before rendering anything.
2. **Build the quote model** in the shape above. This is the step that turns the MCP response into `model.json`.
3. **Pick the variant** from the engagement shape, not from preference. Fixed deliverables with acceptance criteria is Waterfall. A backlog with a rate of delivery is Agile. Analysis with a readout is Assess.
4. **Render.** `node scripts/generate_sow.js model.json <variant> --contract contract.json --output output/sow.docx`. Add `--profile brand.md` for a selected brand. Writes the DOCX, a build record, and a resolution log. Existing outputs are preserved; use a new attempt path.
5. **Work the resolution log.** Every bracketed field is resolved before the document leaves the building. A missing source value is flagged, never filled.
6. **Verify the actual contract and quote.** `python3 scripts/verify_contract.py OUT.docx --contract contract.json --quote model.json --variant <variant> --output verification.json`. This compares selected clause text, identities, scope descriptions, quote values, and build hashes. It must pass. The older `verify_clauses.py` checks the reference clause table only and cannot approve a different contract profile.
7. **Read [the contract review workflow](../sow-quality/SKILL.md)**, embedded as the contract scope and obligation review mode, for the authoring pass: structural de-slop, the Basis of Estimate framework, and cross-reference discipline.
8. **Gate.** Parity, visual, prose. Written disposition each.

## Contract and brand inputs

The `--contract` JSON is the canonical source for this engagement's provider identity,
notice address, contact, clause text, and upfront percentage. It must include `status`,
`source`, `provider`, `upfrontPercent`, and a complete `clauses` object with the same
keys and shapes as `fixtures/contract.example.json`. Keep the confirmed profile and
payment instructions in the private project. Reuse that profile across its SOWs.
Do not copy bank details or contract approvals into this reusable skill.

`status: confirmed` records the user's confirmed source. The example profile uses
`status: example`; it runs only with `--example` and a model explicitly marked
synthetic, and every generated example is labeled. Its terms are test data and
carry no approval for a real engagement. A passing text check proves that the
selected wording survived rendering; it does not establish legal approval.

The separate canonical brand profile owns colors, Office font, and optional logo.
The neutral profile needs no proprietary files. A declared missing logo fails;
a supplied raster logo preserves its aspect ratio. `--profile` or
`SKILLS_BRAND_PROFILE` selects the profile, then project `brand.md`, then the
packaged neutral policy.

## What a clean run means

Complete source inputs can produce zero unresolved fields. That is expected when
the quote and contract profile supply the information. Missing information is never
filled from remembered company conventions. `--draft` permits a marked working
copy; the build record retains every unresolved field and the verifier fails it.

Run the source-contract check, render the DOCX, inspect every page, and check the
contents links, tables, signatures, and scoped assumptions. Retain each attempt,
including failures and screenshots. A generated report does not replace the DOCX.

## Per option

One SOW per option. A three-tier playbook carries three SOWs, not one with a tier table.
Use a descriptive output path, for example: `10 <Playbook Short Name> - SOW - <Band Name>.docx`,
for example `10 CPQ to RCA Migration - SOW - Remediate & Migrate.docx`. The real band name,
never `Tier 2`; the code stays in the manifest, never in the filename.

## Rules

- **The quote is the only source for a number.** No price, duration, or headcount that the quote does not ground.
- Place volumetric assumptions and any change-control triggers where the selected agreement requires them. Preserve fixed scope caps and contractual rights; Exhibit A and the historical soft/hard taxonomy apply only when adopted by that agreement.
- **One authoritative home per mechanic.** Exhibit A does not restate Change Order mechanics. Section 7.2 does not lead with consequences before establishing the rule.
- **Preserve role names and responsibilities from the quote.** Use `roleAliases` only when an explicit mapping is part of the source. Do not silently turn an Account Executive into an engagement-delivery role.
- Use the selected writing policy for authored wording. Preserve exact quotations and mandated clause punctuation; scanner flags never authorize changing contract terms.
- Preserve supplied exclusions and their actual handling process. A proposed next step stays proposed; do not invent paid follow-on work.

## The assumptions in the SOW should already be familiar

Where the project has an approved decision deck or prior scope record, compare its assumptions with the SOW and flag discrepancies. Preserve the actual approval state; neither an absent deck nor a generated document establishes client acceptance. Use the confirmed scope baseline when no deck exists.

## Clause coverage and files

The selected contract profile is the authority for the actual build.
`verify_contract.py` checks its wording, including the assessment and engagement-letter
branches, against the generated document. Missing or changed text fails. It also
checks input and artifact hashes so a changed quote cannot reuse an old passing build.

- `scripts/generate_sow.js` renders all four variants, preserves scope paragraphs and bullets, mines assumptions and Change Order triggers, and reconciles the quote before rendering.
- `scripts/input_contract.js` validates the inputs and performs per-role financial and phase reconciliation.
- `scripts/approved_clauses.js` is a legacy filename for the neutral reference clause structure. It supplies required keys; builds use the explicit profile's values. It is not a claim of approval.
- `scripts/verify_contract.py` checks the actual selected contract and quote against the DOCX.
- `scripts/verify_clauses.py` and `references/required-clauses.md` retain the reference anchor checker and its regression cases.
- `fixtures/` contains runnable synthetic quote and contract examples.
- `references/cpq-migration-exclusions.md` retains detailed migration exclusion examples. Select only exclusions supported by the actual engagement.

## Runtime

Node.js with `docx` is required for generation. A declared logo also needs
`image-size`; Python 3 runs the verifiers. Use the host's bundled dependencies when
available. Otherwise run `pnpm install --frozen-lockfile --ignore-scripts` in this skill directory using its committed lockfile. The portable package includes its shared brand runtime and
policy. It does not require a company drive or a neighboring skill checkout.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion, and
not something a reviewer does later. Full spec in
[`release-gate.md`](../_shared/release-gate.md).

1. Apply writing-integrity to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not present the artifact as finished until every check that applies has passed.
