# Brand gate reference

Visual values come from the selected Markdown profile. The estate neutral policy
is packaged at `references/estate/brand.md`; a confirmed project profile can
replace it through `SKILLS_BRAND_PROFILE` or the current project's `brand.md`.

## What the checker enforces

Every literal palette color must resolve to the profile. Renderer compatibility
keys are mapped in `brand/token-roles.json`; their values are compiled at runtime
by the Python and Node loaders. No brand CSS repository or company account is
required. Use `scripts/sync_tokens.py --output tokens.json` only for consumers
that need a snapshot, and `--check tokens.json` to detect drift.

The checker applies the selected border width and radius and checks for title
underlines and long centered body copy. It reports sentence-case and label
tracking issues for review. It does not ban warm colors that the selected profile
allows. The neutral policy has no logo and imposes no footer convention.

## What the artifact decides

Choose page structure, chart encoding, density, and slide composition for the
content and audience. A deck and a workbook can share an identity without using
the same layout. The profile supplies visual values; it does not establish
that a repeated card grid or a particular logo position suits the content.

Use only supplied logo assets, with their recorded usage rights. A profile's
relative asset paths resolve beside that profile. System font stacks need no
font files; explicitly required font files must resolve before rendering.

## Decks and document exports

The DDOC builders can consume the compiled tokens. A supplied template remains
an option when the task requires it. Inspect its palette, fonts, logos, document
properties, and notes for conflicting identity before using it.

Run the checker against generated files, then inspect rendered slides or pages.
The PPTX extractor preserves table text for parity checks; it is not a visual
preview. Re-run parity after content edits so figures and protected qualifiers
remain present in the exported result.

## Contrast and limits

Check foreground/background contrast in the actual rendered view. Body text
needs at least 4.5:1 and large text at least 3:1. If a confirmed profile cannot
meet a required use, choose an accessible combination within that profile or
request an explicit profile correction. Do not recreate a historical exception
as permission for unreadable text.

The checker sees literal colors and document XML. It does not fully evaluate CSS
variables, inherited styles, image colors, or font substitution by viewers. Its
passing result supports the visual review; it cannot replace it.
