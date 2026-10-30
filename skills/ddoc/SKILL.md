---
name: ddoc
description: 'Authors, gates, and builds the DDOC, the client-facing Deal Decision deck presented immediately before the proposal: interactive copy approval first, then the PPTX build. Two modes: decision mode when the client chooses between options, confirmation mode when there is one option. build_ddoc.js --check gates a manifest without rendering, so copy can be gated where the renderer cannot be installed. Use when asked to build, review, de-slop, gate, or rebuild a DDOC, deal decision deck, options deck, scope deck, or the deck presented before the proposal. Trigger on DDOC, options deck, version slide, discussion document, the deck that goes with the SOW, or a Q-number paired with a deck request. Do NOT use for SOW review (sow-quality), prose editing (writing-integrity), PPTX mechanics (pptx), or a generic multi-slide proposal deck (deck-builder).'
---


# Deal Decision deck

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`deck.md`](../prose-pass/references/registers/deck.md). Inputs, not a final pass.**

The DDOC is the Deal Decision deck: a client-facing PPTX that runs immediately before the proposal. Its job is getting the client on record accepting a boundary before the provider contracts to it.

"Deal Desk document" and "discussion document" are retired names for this same artifact. If either surfaces, build the Deal Decision deck described here.

## The discipline

Copy approved first, then built. Rendering after approval is cheap; re-rendering after rejection is not. Rejected decks fail on copy, not on layout.

The gate that enforces this is `build_ddoc.js --check`. It runs the full preflight without rendering, so the copy can be gated in any environment, including ones where the renderer cannot be installed. Run it at the end of Phase 1 and again at Phase 4.

## Phase 0: pin the mode and the source

**Mode is a scope fact, not an authoring preference.** It follows from the option count.

- **Decision mode.** The client is choosing between options. One deck covering all of them, never one deck per option. Contrast is the mechanism: a client shown one option evaluates it against doing nothing, which is always cheaper. Two or three options. Never four.
- **Confirmation mode.** One option. Same skeleton, comparison replaced by boundary confirmation. A single-option playbook still gets a DDOC, because the artifact's job is the boundary, not the comparison.

Then pin:

1. **Audience.** Who is in the room and what decision the meeting produces. Sponsor, budget holder, technical veto.
2. **Source.** The quote identifier and its source data, from an available integration or a supplied local export. Confirm totals and scope line items. Populate `quote_snapshot` with each `quote_field` and its actual source value; the builder rejects a figure that differs or has no source value.
3. **Existing draft.** If there is a PPTX, run `python3 scripts/extract_slide_text.py <deck.pptx>` and present the extracted copy as the starting point rather than starting clean. The extractor also takes `--json`, `--manifest`, `--figures`, and `--diagnostic`; run it with `-h` for current usage.

Do not proceed until the mode, audience, source, and any existing draft are pinned.

## Phase 1: build the manifest

The manifest is JSON, not a deck. Schema and both skeletons are in `ddoc-patterns.md`. Populate from the quote and the source documents.

Flag anything inferred with `[FLAG: reason]`. Never fill a gap with a plausible-sounding projection. The builder refuses to render an unresolved flag, which is deliberate.

Gate the manifest before showing it to anyone:

```bash
node scripts/build_ddoc.js manifest.json --check
```

This catches structural problems (missing slides, option count, evidence classes, line budgets) before a human spends attention on wording.

## Phase 2: diagnostic scan

Run the prose gate over the manifest's authored text. `writing-integrity` owns this review. Its bundled internal `prose-pass` runtime provides `prose_check.py`; resolve that runtime and run its script:

```bash
python3 ../prose-pass/scripts/prose_check.py extracted.txt --config ../prose-pass/house.json
```

Exit code 0 is a pass, 1 is a fail. Report the counts the scanner prints, never an adjective. "Clean" is not a finding; "0 fail, 2 warn" is.

Then run a figure tie-out against the quote. A figure mismatch and a section symbol are blockers and must clear before Phase 4.

## Phase 3: slide-by-slide review

One slide at a time. Never batch. For each: present the copy as it will appear, surface the Phase 2 flags for that slide, propose a rewrite with what changed and why, and wait. Approved moves on; edit requested is applied and re-presented; deferred is flagged and must clear before Phase 4.

Worked before-and-after pairs for every failure mode below are in `examples.md`. Read it before proposing a rewrite; it shows the accepted fix rather than describing it.

Rules applied during review, beyond the scanner:

- Every body line is a complete declarative sentence. Fragments are a hard fail.
- Headers carry the slide's point, not a label. "Three versions, one decision" rather than "Overview".
- Colon constructions on body lines are almost always wrong. A label earns one; a sentence rarely does.
- Symmetry is broken by wording, not truncation. Three cards opening "Everything in Tier 1 plus" are rewritten specifically for what each does.
- Assumptions are framed as the conditions under which the price holds, not as fine print. That framing is what makes the Change Order conversation survivable.
- Scope reads as boundaries and outcomes, not feature lists.
- Every not-included line routes to a paid next step.
- Line budgets are hard. A line that overflows on the rendered slide is a build-time failure.

## Phase 4: build and gate

```bash
node scripts/build_ddoc.js manifest.json --check          # gate: preflight only, no render
node scripts/build_ddoc.js manifest.json -o OUT.pptx      # build once the gate passes
```

Then rasterize and inspect every slide for overflow, leftover placeholder text, and figure drift. Report what was checked, not that it looks good. All three release gates need a written disposition before delivery.

The builder refuses to render on a preflight failure. It checks skeleton presence and order, option count, exactly one recommended option, identical section sets across option blocks, word-count parity across options, evidence classes on the heard slide, figure-to-quote-field mapping against `quote_snapshot`, a declared profile logo that exists and is readable, em dashes, the section symbol, unresolved flags, and line budgets. Fix the manifest, not the deck.

## The heard slide carries evidence classes

Every item on "what we heard" is `{text, evidence, source}`. Only `client_stated` renders. `seller_asserted` and `inferred` items either become questions on the "what we need from you" slide or are dropped. The classes and sources go into speaker notes, not onto the slide.

A slide that attributes to the client something they never said is the fastest way to lose a room. The worked pair in `examples.md` shows the required correction.

Source material reaches the team through whatever the account uses: Google Drive, Gmail, Slack, Salesforce, or a connected meeting-notes integration. No single tool is standard. Read what is actually there through the available MCP integrations, prefer a complete speaker-labeled transcript over a summary, and never substitute a similarly titled note for the one that was named.

## Brand

Use the shared [brand policy](references/estate/brand.md) or the confirmed project
profile. The Node renderer reads it through `brand_runtime.js`; set
`SKILLS_BRAND_PROFILE` to select an explicit profile. Preserve identical geometry
across options so the comparison follows scope. Logo and provider identity are
optional inputs, never inherited from a former company.

A profile with `logo` null needs no asset. A declared logo is resolved relative to the
directory of the selected profile file, the same rule the renderer uses. `--check`
fails with the resolved path when that file does not exist or cannot be read, before
any rendering.

## Boundaries

- Does not price. The quote owns the number; this renders it.
- Does not author scope language. Scope comes from the quote or the user; this audits and cleans it.
- Writing review belongs to writing-integrity; the bundled internal diagnostic tools support that review.
- Does not build the SOW. That is `sow`.
- Authors and builds the DDOC: copy approval, then the PPTX build. Copy approval and the slide-copy editorial rules both live in this skill; the per-slide-type editorial rules are in `references/slide-copy-patterns.md`.

## Running unattended

Phases 0 and 3 need a human. On a scheduled or headless run, do not simulate the approvals.

Do this instead: build the manifest, run `--check` and the prose gate, and stop with the findings and the unresolved flags. Say plainly that copy approval is outstanding. Never render a client-facing deck on an unattended run, and never record an approval nobody gave.

## Files

- `scripts/build_ddoc.js` · the builder and the gate. pptxgenjs for rendering, preflight for gating. `--check` runs the gate alone.
- `scripts/render.js` · rendering helpers. Must sit beside `build_ddoc.js` in `scripts/`.
- `scripts/extract_slide_text.py` · pull copy out of an existing deck. Needs `python-pptx` (see `scripts/requirements.txt`); everything else here is stdlib.
- `references/ddoc-patterns.md` · both skeletons, the manifest schema, and the failure-mode table.
- `references/slide-copy-patterns.md` · slide-type editorial rules for the copy (problem, capability hierarchy, options, differentiators, investment, timeline, next steps, anti-patterns).
- `references/slide-layouts.md` · line budgets per layout.
- `references/examples.md` · worked before-and-after pairs for every failure mode.
- `references/example-*.json` · worked manifest and input examples.

## Dependencies

The **gate** needs Node only. `build_ddoc.js --check` runs with no third-party packages, by design: the renderer is loaded lazily inside `build()` so a missing renderer can never disable the quality gate. Do not move those requires back to module scope.

The **renderer** needs `pptxgenjs` (`npm install pptxgenjs`). Where the npm registry is unreachable (for example an install that returns 403), the renderer cannot run and `--check` is the only usable path; build the PPTX in an environment with registry access.

The diagnostic commands (`prose_check.py`, `house.json`) remain in the bundled internal `prose-pass` runtime. Use Writing Integrity for review; do not install a separate Prose Pass skill.

PPTX validation and rasterization for the visual gate are environment-specific. Use the host's presentation skill and its documented render-and-verify workflow (for example, the Claude `pptx` skill or the Codex `presentations` skill). If neither is available, substitute an equivalent validation and rasterization step and state which one was used in the release note. Do not claim the visual gate passed without naming the mechanism that rendered the slides.

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
