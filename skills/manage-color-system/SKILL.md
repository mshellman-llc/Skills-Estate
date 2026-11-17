---
name: manage-color-system
description: "Assess, question, decide, propose and apply UI color systems in Material 3 role language. Audits token files (CSS or Design System tokens.json) and component CSS for contrast in WCAG and APCA, role coverage, palette drift, wrong ratio notes, off-system hex values and a stale compiled stylesheet; builds themed role tokens with standard and high-contrast levels from tonal palettes; reviews color changes before they ship. Use when colors, tokens, themes or a brand palette are created, changed or judged, or before publishing a page that sets its own colors. Not for a full WCAG audit of an interface (audit-accessibility), applying a confirmed brand to a deliverable (manage-brand-profile) or building a chart (build-editorial-chart)."
---

# Manage color system

A color system has three layers. Palettes hold fixed colors at numbered tones. Roles name what a color does (surface, on-surface, outline, primary) and pick a tone per theme and contrast level. Components read roles and never a palette step. Most color problems are a break between two layers: a component that reads a hex, a role that changes its palette, a palette step whose number lies about its lightness.

This skill works in that model. The engine in `scripts/` measures and generates; this file says when to use it and how to decide.

## When not to use

- A full accessibility review of an interface (keyboard, semantics, focus order, WCAG beyond color) belongs to `audit-accessibility`. This skill covers color only.
- Applying a confirmed client or project brand to a document or page belongs to `manage-brand-profile`. This skill designs and repairs the color system that a profile carries.
- Building a chart belongs to `build-editorial-chart`. This skill checks the chart palette.

## Engine

Node 18 or later, nothing to install. Material Color Utilities and culori are bundled in `scripts/vendor/deps.mjs` with their license notices (`THIRD-PARTY.md`); `scripts/lib/apca.mjs` implements APCA 0.0.98G-4g.

```sh
cd <skill>/scripts
node selftest.mjs
node color-steward.mjs audit tokens.css --components bundle.css --json audit.json
node color-steward.mjs pair "#86898f" "#eeeff3"
node color-steward.mjs palette "#283549"
node color-steward.mjs scheme "#283549" --variant neutral --error "#C4302B"
node color-steward.mjs cvd "#283549" "#525f75" "#7a879e"
node propose.mjs ../recipes/<system>.json --out tokens.css --json tokens.json
node color-steward.mjs audit built-tokens.css --source tokens.json   # flags a compiled stylesheet that lags its source
node icons.mjs normalize <icon-pack-svg-dir> <out-dir> --map ../references/icon-roles.json
node icons.mjs check <out-dir>
```

Tone means HCT tone (CIELAB L*), 0 black to 100 white. Contrast uses WCAG 2.2 ratios as the pass line and APCA Lc as the second reading, because WCAG 2 overrates light text on dark grounds.

## Modes

Pick the mode from the request. Several can run in one task.

1. Assess. Run `audit` on the token file and every stylesheet that sets color. When a stylesheet is compiled from a source file, pass both, since pages load the compiled one. Read each finding, check it against the rendered page, and drop false alarms with a reason. Report findings as pictures: the failing pair rendered, its measured ratio, and the fix rendered beside it.
2. Question. Ask the owner only what the numbers cannot settle: brand anchors to pin, whether a hue may enter the system, how far muted text may drop on dark grounds, which surfaces carry the brand color. One question at a time, shown as options she can pick from.
3. Decide. Apply the decision rules below. A rule that settles the question needs no question.
4. Propose. Write or edit a recipe (`recipes/*.json`): palettes from a seed or hue and chroma, pinned brand values, one entry per role with the grounds it sits on and its target. Run `propose.mjs`, then `audit` the output. A proposal ships only with zero failing pairs, and every ratio in its notes is computed.
5. Apply. Map components to roles with `references/component-roles.json`. Replace every hex in component CSS with a role. Keep old token names as aliases until every consumer moves.
6. React. When someone changes colors, review the diff: new literals, a role used against a ground it was never solved for, a hover that lowers contrast, a hue named token that holds a grey. Audit the changed files.
7. Watch. Before publishing any page, deck or chart that sets colors, audit its CSS. Raise what fails in chat once; fix what the rules settle without asking.

## Decision rules

- Roles come in pairs. Text on a fill uses that fill's on- role: on-primary on primary, on-secondary-container on secondary-container. Never pair across.
- Solve every role against every ground it can sit on, and list those grounds in the recipe. A role checked only against the page ground fails on cards and wells.
- Text: 4.5:1 minimum, 7:1 in the high-contrast level. Labels under 16px also need APCA Lc 60 or more. Control edges, focus rings and chart marks: 3:1.
- Outline is for control edges and must reach 3:1. Outline-variant is decorative: dividers, hairline grids, chip edges whose text already meets 4.5:1.
- Containers are fills. Text never uses a container role.
- Surface container tiers name emphasis, not lightness. In a dark theme a higher tier is lighter; in a light theme it is darker. Use surface-dim and surface-bright when an area must stay dimmest or brightest in both themes.
- Fixed roles (primary-fixed) keep one value in both themes. Use them for brand fills, never where contrast with the ground is needed.
- A palette step is one value in every theme. Themes change which step a role picks.
- State is an overlay in the content color at fixed opacity: hover 8%, focus 10%, pressed 10%, dragged 16%; disabled content 38%, disabled container 12%. Components do not invent rgba hovers.
- Error and other semantic colors are harmonized toward the brand hue so they sit in the palette. Brand colors are never harmonized.
- Every theme ships standard and high contrast. High contrast lifts text to 7:1 and edges to 4.5:1 from the same recipe.
- Chart series differ in lightness first. Adjacent series stay at least 0.08 apart in OKLab under normal vision and simulated protanopia, deuteranopia and tritanopia; series below 3:1 on their ground get direct labels.
- Notes in token files never hold hand-typed ratios. Generate them. A ratio in a note names its ground (`6.3:1 on surface in Day`) so the audit can check it; a note it cannot attribute is skipped, not passed.
- A compiled stylesheet ships with its source. After changing the source, rebuild the compiled file before a component reads a new role, or the component reads nothing.
- A hard-coded color in a component stylesheet is a finding unless it is a pinned brand asset with a comment.

## Icons

An icon is a color-system graphic, so it follows the same roles.

- Every ink is `currentColor`. The icon takes the role of the text it sits with: `on-surface-variant` at rest, `on-surface` when active, `on-primary` on a filled button, `on-secondary-container` on a tonal one, `on-error` on a destructive one.
- A status icon takes its signal hue and sits beside its word: Approved, In review, Blocked. The error mark takes `error`.
- In a duotone icon the solid layer carries the meaning and reaches 3:1 on its ground. The 30% layer is decoration. An icon drawn only in the faint layer gets that layer made solid.
- Size 16, 18 or 24px on the 24px grid; a pressable icon gets a 40px target.
- `normalize` strips editor metadata, sets `currentColor`, keeps the duotone opacity and names each icon by its job. `check` fails a fixed color, a missing viewBox or an icon with no solid layer.
- Icon art from a licensed pack stays in the brand's design system or the project, never in this repository. `references/icon-roles.json` names the Stockholm source and the color role for every job.

## Owner decisions on file

Read the current brand profile first (estate-writing:manage-brand-profile for client work). For Megan's own work, Bearing is the one design system:

- Day ground #EEEFF3 and Night ground #161824 are pinned. Brand navy #283549 is pinned as primary-fixed. Bearing runs the color v2 roles from `recipes/bearing-v2.json`, with the earlier names kept as aliases and a high-contrast version of each theme.
- Emphasis comes from size, weight and the Night to Day contrast. Four signal hues (coral, blue, green, orange) carry status, step order and categories only: as a symbol, a dot, a short rule or one soft-tinted card. Never text, a heading, a link or a large fill.
- Every status pairs its hue with a shape and a word, so color never carries it alone.
- Alerts and errors sit on the page's own neutral surface with a thin rule or a small mark. `error` (crimson) appears only in the mark, the rule and the message text; Blocked status stays signal coral. No tinted alert panels, and no component left in its default AI-builder look.
- Set type in Instrument Sans only; never Times.
- Bearing's icons are the Stockholm Premium set, duotone, normalized as above, in Bearing's Icons asset group. Doodle illustration sets are not UI icons.

## Output

Substantial results go into an interactive, mobile-first page in the active brand: findings as rendered pairs, palettes as tone strips, proposals as a before and after the reader can toggle by theme and contrast level, and owner decisions as options to pick. The chat gets the outcome, the counts that matter and the one decision waiting.

Deliver the recipe, the generated tokens.css and the audit JSON with any proposal. State the completion state exactly: proposed, generated, audited, applied to the system, published.

## References

- `scripts/selftest.mjs`: runs the audit and the proposal on the Bearing fixtures and checks the results.

- `references/component-roles.json`: Material 3 components mapped to Bearing components and roles.
- `references/icon-roles.json`: one row per icon job.
- `references/material3-color.md`: the Material 3 color model this skill follows.
- `recipes/bearing-v2.json`: the Bearing recipe; copy it to start a client system.
- `fixtures/`: Bearing's tokens and component color rules as they stood before v2, used by the self-test.
