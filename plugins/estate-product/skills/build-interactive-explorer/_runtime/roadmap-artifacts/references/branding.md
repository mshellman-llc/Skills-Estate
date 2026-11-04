# Branding

A roadmap carries exactly one identity: the governing org's confirmed brand, or the kit's own mode defaults (the Coursify, Venture and Avalon looks). The kit never picks colors by taste. It maps recorded brand roles onto its settings and reports every gap.

## Decide the identity first

Check these in order and stop at the first that applies. State the choice in one line before building, for example "Using the Acme profile (confirmed 2026-10-02)" or "No confirmed brand; using the kit's mode defaults."

1. **The user's own words** in the request: a named client, brand or style.
2. **A `brand.md` profile** in the project folder, or one the user pastes or attaches. This is the `client-brand` skill's format. When that skill is installed, follow its rules too.
3. **The org's Design System artifact** on claude.ai. Run `Artifact` `action: "list"` with `type: "Design System"`, read the relevant one, and copy its color, type and radius tokens into a `brand.md`.
4. **Design tokens in the codebase**: `DESIGN.md`, a tokens JSON (W3C design tokens), CSS custom properties, or a Tailwind theme. In Claude Code, `design-steward:audit` finds which values are settled.
5. **A connected design tool**: Figma variables or a Canva Brand Kit. Canva's `list-brand-kits` returns kit names only, so ask the user which kit applies and get the values from them or from the kit's source guide.
6. **Otherwise the kit's mode defaults** (build without `--brand`). Use `themes/neutral.json` instead when the user wants the plain estate neutral identity.

Values gathered in steps 3 to 5 make a **draft**. Show the user the role table with sources. Build with `--allow-draft` only if they say to proceed on the draft. Mark it `confirmed` only after they confirm it.

Never guess a brand from a company name, a logo in a screenshot, a domain or an earlier artifact. Never carry one org's tokens into another org's roadmap.

## What a brand changes, and what it doesn't

The kit has three formats, and each roadmap is built in one of them: **Relaxed** (the default, after Coursify), **Compact** (after Venture CRM) and **Editorial** (after Avalon). A format fixes layout and treatment: Relaxed's filled cards and colored stat tiles, Compact's bordered columns and tinted tags, Editorial's hairline columns, numbered items, big numbers and dark timeline band. A brand changes colors and fonts in all three. Corners are rounded by default in every mode; a plan can choose square, or the brand profile's radius. Status tones (good, warning, critical) are fixed and never themed.

## Settings

`scripts/brand.py` writes these custom properties on `:root`. Any setting it leaves out keeps each mode's own default.

| Setting | Profile role | Used for |
|---|---|---|
| `--brand-background` | page ground / background | Page, cards, Relaxed panels |
| `--brand-surface` | alternate surface | Stat strip, table heads, Relaxed page ground |
| `--brand-border` | border | Rules, gridlines, card outlines |
| `--brand-text` | text | Text; Editorial's dark band if `dark` is missing |
| `--brand-muted` | muted text | Secondary text |
| `--brand-accent` | primary | Buttons, focus ring, Editorial big numbers and corner shape |
| `--brand-on-accent` | text on primary | Text on the accent. Picked by contrast if missing |
| `--brand-highlight` | accent / secondary | Editorial's second corner shape and band markers, Compact's first column dot. Falls back to chart 2 |
| `--brand-dark`, `--brand-on-dark` | dark, text on dark | Editorial's timeline band. Falls back to `text` |
| `--brand-chart-1` to `-6`, `--brand-chart-N-on` | chart 1 to chart 6 | Legend groups: card chips and fills, bars, swatches, Relaxed stat tiles |
| `--brand-chart-N-tint`, `--brand-chart-N-ink` | chart N tint / ink (optional) | Compact's soft chips and bars. Without them, Compact uses the solid chart color |
| `--brand-font-body`, `--brand-font-headings` | Type: body, headings | All text, headings |
| `--brand-radius` | Layout: radius | Corners only when the plan sets `meta.corners: "brand"`. Otherwise corners stay rounded (the default) or square |

`--brand-background`, `-text`, `-muted`, `-border`, `-surface`, `-accent`, `-font-body` and `-font-headings` are the same names the estate's brand-renderer emits, so `python3 tools/estate.py`'s profile output can theme a roadmap directly.

## Profile formats

`brand.py` reads three formats:

- **client-brand table** (`brand.md` with `## Colors` table rows like `| primary | #0F5C4A | … |`, plus `chart 1` … `chart 6`, `accent`, `dark` rows).
- **Estate profile** (`brand.md` with a JSON block holding `colors`, `type`, `layout`), as in `policies/brand.md`.
- **Kit JSON** (`themes/*.json`).

Fonts named with "Google Fonts" in the Type section are imported. Licensed font files listed under `font_files` in kit JSON are embedded.

## Gaps and contrast

`scripts/brand.py` reports three lists:

- **Picked from recorded colors**: settings filled from another recorded role, such as highlight from chart 2, or a text-on-color pair chosen by contrast.
- **Not in the profile**: settings left unset, so each mode keeps its default for them. A profile with 3 chart colors leaves slots 4 to 6 on the mode's palette; tell the user, since a roadmap with more than 3 groups then mixes palettes.
- **Contrast warnings**: every pair under 4.5:1.

Contrast failures are reported, not fixed. Tell the user which pairs fail. Do not lighten, darken or swap a brand color unless they decide to, and do not call the result "on brand" while substitutions or draft values are in it.

## Applying a theme elsewhere

The theme is a plain CSS file of `--brand-*` custom properties. To theme a roadmap inside an existing site, load `theme.css` after `rk.css`, or map the site's own variables in one block:

```css
:root { --brand-accent: var(--color-primary); --brand-text: var(--color-text); --brand-font-body: var(--font-sans); }
```

All three modes are light; neither source design defines a dark theme.
