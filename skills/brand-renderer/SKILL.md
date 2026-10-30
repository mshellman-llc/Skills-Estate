---
name: brand-renderer
description: 'Render and check branded artifacts using a confirmed project profile or the shared neutral policy. Use for documents, decks, workbooks, PDFs, HTML, or brand-sensitive copy when the task needs visual identity applied without losing source meaning. Resolves required assets, preserves claims through export, and combines executable checks with inspection of the rendered result.'
---


# Brand renderer

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Render the requested output using the selected brand profile while preserving its
meaning in the final format. Use the canonical [brand policy](references/estate/brand.md)
for selection and neutral defaults. Set `SKILLS_BRAND_PROFILE` to an explicitly
selected profile; otherwise the runtime reads the current project's `brand.md`,
then the packaged neutral policy. A selected but missing or invalid profile is an
error, not permission to use another identity.

Run the relevant content and visual checks before delivery. Automated checks
support the review; they cannot decide whether an artifact answers its audience's
question or whether the rendered layout is usable.

## Shared rendering library

The producing skill owns the requested artifact and its information design.
Use this library when that artifact needs a visual profile. A plain chat reply
does not require a brand preflight. Writing-integrity applies to its prose.

What this skill holds constant across output formats:

- **Typography.** The profile's font stack and supplied font files, with
  tabular figures where digits align. System fonts need no bundled files.
- **Palette.** Renderer tokens are compiled from the selected profile.
  Additional chart colors must be recorded in that profile.
- **Assets.** Use the profile's supplied logo when present. The neutral profile
  has no logo; do not invent one.
- **Hierarchy.** A reader tells the claim from the caveat without reading the
  colour. Type and space carry the rank.
- **Accessibility.** Contrast floors, alt text, one `h1`, a named language.
- **Evidence integrity.** A figure reaches the rendered page still carrying its
  qualifier and its source. The parity gate reads exactly that.
- **Craft.** No emoji, no decorative glyphs, no colour-coded left borders, no
  gradient standing in for structure.

What the content decides, surface by surface:

- Slide composition, and whether a given slide carries a footer at all.
- Page structure, section order, and where a break falls.
- Canvas: a profile-defined surface chosen for the reading it supports.
- Logo position and which mark identifies a surface.
- Density: how much sits on one view.
- Visual encoding: which chart form fits the comparison, and what a table earns.

There is no universal footer, header bar, title position, card pattern, or slide
composition. A rule that forced one taught people to reshape the artifact to
clear the gate instead of to serve the reader. `reference/brand-gate.md` carries
the line between the two lists.

Weight follows consequence, not file format. Email and Slack get the voice rules
and a reading pass by default. They escalate to the full release gates when the
message carries a figure, an approval, scope, a commitment, or a decision. That
is the same trigger set the release validator fails closed on. The register is
[`email-slack.md`](../prose-pass/references/registers/email-slack.md); the
escalation rule is in
[`surface-policy.md`](../prose-pass/references/surface-policy.md).

## Controls provided to the producing workflow

The producing workflow uses these controls as needed for the artifact.

```
producing workflow -> writing-integrity -> authored prose review
producing workflow -> brand-renderer -> visual profile and rendering checks
producing workflow -> quality-gate -> assembled deliverable review
```

`writing-integrity` owns writing review. The internal `prose-pass` module supplies
diagnostic tools; the confirmed author profile supplies voice.
`quality-gate` owns the release decision. It fails closed on an unsupported
figure, scope, approval, or go or no-go.

Neither one resolves this skill back. A copy of brand-renderer inside
quality-gate would make each the other's runtime, and one upload would then ship
two renderers. A fix to either could reach a client artifact through the stale
copy of the other.

## First action: prove the runtime

Before rendering a styled artifact or diagnosing its assets, resolve this
module's directory and run:

```bash
python3 scripts/runtime_preflight.py --json
```

The preflight resolves packaged or sibling runtimes. For an external runtime, supply its inspected absolute directory through `ESTATE_PROSE_RUNTIME` or `ESTATE_QUALITY_RUNTIME`; it does not search account-specific mount paths. Use the absolute paths in that report for the logo, fonts, prose checker, prose
receipt tool, brand checker, and release validator. A failed preflight blocks
the affected rendering operation. A logo or font file is required only when
the selected profile specifies it. A neutral artifact can use system fonts.
A checker run with no receipt cannot release a final artifact.

## The release gates

An artifact is release-ready only when every gate has a disposition. No single
pass authorizes release.

1. **Parity gate** (`scripts/parity_audit.py`). Every claim, number, name, and
   evidence reference that belongs in the artifact survives into the rendered
   readable text, nothing forbidden was added, and protected qualifiers survived.
   This is lexical and structural support only: it cannot see computed CSS,
   clipping, off-canvas text, print visibility, or whether a qualifier sits with
   its claim unless you scope it with a selector.
2. **Visual gate** (human or model, mandatory, no script). Inspect the rendered
   views slide by slide and page by page. Confirm nothing is clipped, hidden,
   off-canvas, or visually detached from its qualifier. A `requiredViews` list
   raises this reminder; the flag is not a substitute.
3. **Prose gate** (the bundled `prose-pass` runtime plus a reading pass). Run the
   checker at the absolute `prose_check` path returned by runtime preflight. Its
   config sits at the prose runtime root as `house.json`.
   The reading pass catches the cadence a matcher cannot. See "Voice" below.
4. **Brand gate** (`scripts/brand_check.py`). Palette, borders, radii, type,
   assets, and the accessibility floor. Reads colors from the selected profile through `brand/tokens.py`,
   never from prose. The deterministic half of the visual gate; it does not
   replace looking at the thing. It gates identity, not layout: footer placement
   and slide composition come back as review flags. See "Token-backed brand
   checks" below.

Release note discipline: record a disposition for every parity or brand warning
and every visual review flag before shipping. Prose findings cannot be disposed.
Repair supported scanner findings, then read the complete result using Writing Integrity. A clean scan does not establish editorial quality.

## Workflow

1. Build the artifact to the brand canon and voice below.
2. Write a parity manifest listing what must survive: required phrases, forbidden
   phrases, evidence references, and protected claims with their qualifiers.
3. If the artifact is a deck, convert it first:
   `python3 scripts/extract_pptx.py deck.pptx --html deck.extracted.html`. The
   extractor is table-aware so numbers and rows in tables are not silently dropped.
4. Parity gate:
   `python3 scripts/parity_audit.py manifest.json artifact.html --strict`. Fix
   any error.
5. Prose gate using the `prose_check` path from runtime preflight and the
   `house.json` beside that runtime's `scripts/` directory.
   Fix every finding and rerun until the checker reports clean.
6. Brand gate: `python3 scripts/brand_check.py artifact.html`. Fix every failure.
7. Do the visual gate and the voice reading pass by eye.
8. Write the release note dispositions. Then ship.
9. Hand the gated artifact back to its owner. Delivery and publishing sit
   outside this skill.

Run the parity gate again after any prose fix. A voice edit can silently break a
`requiredPhrase` or a protected claim, and parity is what catches it.

## Scripts

Every script runs on `python3` with the standard library. Only
`extract_pptx.py` needs `python-pptx` (`pip install -r scripts/requirements.txt`).
No script in this skill touches the network. The parity gate parses HTML
and resolves selectors through `html_dom.py`, a local module, so it still runs on
a mount where nothing can be installed.

- `scripts/parity_audit.py manifest.json rendered.html [--json report.json] [--strict]`
  Lexical and structural parity. Exit 0 pass, 1 error or `--strict` warning, 2 bad
  manifest.
- `scripts/brand_check.py artifact [...] [--json out.json] [--strict]`
  The visual-layer gate. Reads `.html .htm .css .pptx .docx .js .py .md`; source
  files are linted too, because a renderer that hardcodes a hex emits it on every
  future artifact. Exit 0 clean, 1 failure or `--strict` flag, 2 missing tokens.
- `scripts/sync_tokens.py [--profile FILE] [--output FILE] [--check FILE]`
  Exports a JSON token snapshot or checks that a saved snapshot matches the
  selected profile. Exit 0 match, 1 drift, 2 invalid input. Python and Node
  renderers read the profile directly and do not need a cached snapshot.
- `scripts/palette_selftest.py [--skill SKILL.md]`
  Checks that the instructions delegate visual values to the profile and that
  the runtime tokens resolve to values in that profile.
- `scripts/extract_pptx.py deck.pptx [--html out.html] [--json out.json]`
  Table-aware PPTX to HTML transcript for the gates only. Never substitutes for
  the visual gate.
Each script has a selftest next to it (`*_selftest.py`). Run them after any edit;
each prints observed versus expected and exits nonzero on a mismatch:

```
python3 scripts/parity_audit_selftest.py
python3 scripts/brand_check_selftest.py
python3 scripts/palette_selftest.py
python3 scripts/extract_pptx_selftest.py
```

The bundle carries a local runtime for both dependencies. They stay authored and
verified in `prose-pass` and `quality-gate`; the bundler copies that exact source
into `_runtime/prose-pass` and `_runtime/quality-gate` so a cloud mount does not
depend on sibling discovery. Their skill metadata is stripped on the way in, so
the loader sees one skill and cannot route to a nested copy.

## Parity manifest

`manifestVersion` must be a string with major version `1`, one JSON manifest per
artifact. It lists `requiredPhrases`, `forbiddenPhrases`,
`requiredEvidenceReferences`, `protectedClaims` (each with `requiredQualifiers`
and an optional `selector`), `requiredSelectors`, and `requiredViews`. The full
field table is in `reference/authoring-policy.md`. Keep the manifest to
artifact-specific values; never embed a worked deliverable or recognizable
artifact structure.

## Brand canon

The [brand policy](references/estate/brand.md) is the neutral authority and defines
how to select a project profile. Read the selected profile before rendering.
Keep visual values there rather than copying them into a skill's instructions.

`brand/tokens.py` and `brand/tokens.js` compile the profile into compatible
renderer keys. `brand/token-roles.json` maps existing keys to semantic profile
roles; it contains no palette values. This preserves existing renderer APIs while
allowing a profile change to reach every consumer. The loaders record the
profile hash. `scripts/sync_tokens.py` can export the same values for a consumer
that needs a JSON file.

Use `scripts/resolve_assets.py --json` to resolve the profile's local logo and
font paths. Relative paths resolve beside the profile. The neutral policy needs
neither a logo nor downloaded fonts. A project requiring missing assets must
supply them or explicitly select an available alternative.

Apply the profile's border width and radius. Preserve readable contrast and
left-aligned long body text. A surface's layout follows its content: there is no
mandatory footer, repeated card grid, or fixed slide composition. A supplied
template is an optional input, and its identity must agree with the selected
profile. See [`brand-gate.md`](reference/brand-gate.md).

## Token-backed brand checks

`scripts/brand_check.py` checks the output against the runtime palette and
geometry rules. It also checks title underlines, long centered body text, and
sentence-case headings. The neutral policy does not prohibit a color because
it is warm or require a logo footer. Checks must follow the selected profile,
not preserve a former company's preferences.

The checker inspects literal color values and document XML. It cannot prove
computed CSS, font availability in a viewer, or complete visual accessibility.
Inspect the rendered output and confirm contrast and legibility before release.
An authoritative profile establishes where values came from; it does not prove
that the renderer applied them correctly.

## Voice and money

Writing-integrity governs prose review. The internal `prose-pass` module carries
the diagnostic engine; this rendering library supplies no competing voice.
Construction patterns expose the tell. The catalog covers em dashes, buzzword
vocabulary, the `not just X, but Y` flip, trailing "-ing" benefit clauses,
throat-clearing openers, rule-of-three triads for rhythm, plus monotone sentence
rhythm. Never strip genuine epistemic language as if it were a
tell: Confirmed, Inferred, Unknown, "estimated", ranges, "not priced", "blocked",
and "at risk" all stay, and a voice fix must never soften a protected caveat, a
figure, a conflict, or a conclusion.

`reference/authoring-policy.md` holds the seven-question reading pass, the money
rule (meaning not price; the confirmed pricing source owns the authoritative numbers), and fixture
discipline.

## Porting notes

`SKILL.md`, `scripts/`, `brand/`, `_shared/`, and `_runtime/` load into Console
Managed Agents and the Agent SDK skill loader unchanged. The cloud bundle carries
the prose runtime and brand assets it needs. Install `scripts/requirements.txt`
in environments that do not already provide the declared libraries.
