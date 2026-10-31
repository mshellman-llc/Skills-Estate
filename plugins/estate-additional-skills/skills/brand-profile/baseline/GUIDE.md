# Baseline guide

Baseline is the default design system for skills and artifacts when no other brand is selected. Load `baseline.css`, put `class="bl"` on the page root, and build from its `--bl-*` tokens and component classes. Icons are in `baseline-icons.svg` and `baseline-icons.json`.

## Palette

F, navy and pastel, is the default and needs no class. E, ink and amber, is the alternate: add `theme-ink` to the root (`class="bl theme-ink"`). Use E only when it is requested. Use tokens, never literal hex values, so both palettes work.

## Rules

- Inter is the only typeface. Do not use monospace without a strong reason, and never JetBrains Mono.
- Charts use a dark-to-light ramp of the palette's own color (`--bl-cat-1` to `--bl-cat-5`), never mixed hues. Keep a legend and a fixed series order.
- Do not use colored side accents on cards, rows, badges or callouts. Show category or state with a dot, icon or label.
- Icons are the Stockholm duotone set. Use `<svg class="i sk" viewBox="0 0 24 24">` with the markup from `baseline-icons.json`, or `<use>` from the sprite.

## Badges

`.badge` is a hairline chip: a thin neutral outline with a small status dot, set with `.accent`, `.success`, `.warning` or `.danger`. Use a badge for the one status that matters on a record, such as in a page header. In table rows, lists and metadata, use plain text.

## Avatars

`.av` uses the tonal ramp. People are round and take one of `.t1` to `.t4`, chosen from their name so each person keeps the same step. Accounts and other objects use `.av.square.neutral`.

## Status and licensing

The owner reported on 2026-10-30 that Stockholm's use here is cleared. Other icon packs on the canvas are not in this kit, and the CRM Dashboard license bars redistribution.
