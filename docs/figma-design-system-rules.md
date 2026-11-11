# Figma design system rules

Rules for turning Figma designs into estate artifacts through the Figma MCP server. They describe the code as of commit `365ca43` (2026-10-29) plus the Roadmap Kit drafted in session at `/home/user/roadmap-kit`, which is not yet in this repository.

The estate has no app, framework or component library in the usual sense. It is a library of agent skills that generate documents, decks and standalone HTML pages. A Figma design reaches the estate in two ways:

- **Brand values** (colors, type, radius, border) become a brand profile. Every renderer reads that profile.
- **Component designs** (a card, a timeline bar, a proposal section) become changes to a skill's template or a kit component, written against profile tokens.

Never paste Figma hex values, font names or pixel values directly into a template.

## 1. Token definitions

### Where tokens live

| Source | Path | Role |
|---|---|---|
| Brand policy and neutral profile | `policies/brand.md` | The estate's branding authority. A JSON block holds the neutral profile. Edit here, then run `python3 tools/estate.py sync`, which copies it into each skill package that needs it. |
| Project profile | `brand.md` in the user's project folder (outside this repo) | Same JSON block format. Selected by name, by `SKILLS_BRAND_PROFILE`, or by being in the current project. |
| Profile loader and compiler | `skills/brand-renderer/brand/brand_profile.py`, `brand_profile.js` | `resolve_profile`, `load_profile`, `compile_tokens`, `css`. |
| Legacy key map | `skills/brand-renderer/brand/token-roles.json` | Maps old renderer keys (`deepNavy`, `teal`, `offWhite` …) to profile roles. Holds no colors. |
| Python and Node token access | `skills/brand-renderer/brand/tokens.py`, `tokens.js` | Renderer-compatible keys resolved from the selected profile. |
| CLI | `tools/brand.py <profile> [--tokens]` | Emits `:root` CSS or the compiled token JSON. |

### Profile format

```json
{
  "name": "Neutral",
  "status": "confirmed",
  "source": "Plain fallback with no design system, 2026-11-11",
  "colors": { "background": "#FFFFFF", "text": "#111111", "muted": "#555555",
              "border": "#DDDDDD", "surface": "#F5F5F5", "accent": "#111111" },
  "type": { "body": "system-ui, …", "headings": "system-ui, …", "office": "Arial",
            "body_min_pt": 11, "screen_min_px": 16, "slide_min_pt": 18 },
  "logo": null,
  "layout": { "border_px": 1, "radius_px": 6, "heading_case": "sentence" }
}
```

### Transformation

`brand_profile.css()` emits one CSS variable per color role and two font variables:

```css
:root {
  --brand-background: #FFFFFF;  --brand-text: #111111;  --brand-muted: #555555;
  --brand-border: #DDDDDD;      --brand-surface: #F5F5F5; --brand-accent: #111111;
  --brand-font-body: system-ui, …;  --brand-font-headings: system-ui, …;
}
```

`html_profile.py` embeds the selected profile (and logo or fonts as data URIs) into a standalone HTML artifact. `scripts/sync_tokens.py` exports or checks a JSON snapshot.

Two gaps to know about:

- Templates use `--brand-border-width` and `--radius`, but `css()` does not emit them. Each template sets them itself from `layout`.
- `skills/map-journey/assets/journey-map.html` uses unprefixed variables (`--bg`, `--accent`, `--muted`) instead of `--brand-*`.

### Roadmap Kit tokens (not yet in the repo)

The kit uses its own `--rk-*` set, compiled by `skills/build-roadmap/scripts/brand.py`. It reads the `manage-brand-profile` table format, not the estate JSON block. Before the kit joins the estate, its compiler should read profiles through `brand_profile.load_profile` and map roles as follows:

| Estate role | Kit token |
|---|---|
| `background` | `--rk-bg` |
| `surface` | `--rk-surface-2` |
| `text` | `--rk-ink` |
| `muted` | `--rk-ink-2`, `--rk-ink-3` |
| `border` | `--rk-line` |
| `accent` | `--rk-accent` |
| `layout.radius_px` | `--rk-radius` |
| `type.body`, `type.headings` | `--rk-font-body`, `--rk-font-display` |

Chart series colors (`--rk-c1` … `--rk-c6`) need a recorded `chart` palette in the profile. The brand policy requires chart colors to be identified as a chart palette, not as brand colors.

### Rules for Figma variables

1. Read variables with `get_variable_defs` on the node the user names. Never guess a token from a screenshot.
2. Map each Figma variable to a profile role. Variables with no matching role go to the user as a question, not into a template.
3. Values from Figma make a `draft` profile with `source` set to the Figma file URL, node ID and retrieval date. They apply only after the user confirms them or authorizes the draft for one artifact.
4. A Figma file's colors never edit `policies/brand.md`. The neutral profile changes only by explicit decision. Client values belong in the client's project `brand.md`, outside this repo.
5. Check contrast after mapping: body text 4.5:1, large text 3:1. Report failures; do not adjust a brand color to pass.

## 2. Component library

There is no shared UI component library. Each HTML-producing skill owns its template:

| Skill | Template | Notes |
|---|---|---|
| `build-interactive-proposal` | `skills/build-interactive-proposal/templates/proposal.html` | Uses `--brand-*`. Build script checks source IDs and quote parity. |
| `render-offering-brief` | `skills/render-offering-brief/templates/external_onepager.html`, `internal_brief.html` | |
| `map-journey` | `skills/map-journey/assets/journey-map.html` | Unprefixed variables (see gap above). |
| `build-deck` | `skills/build-deck/assets/deck.css` | Uses `--brand-*`, `--brand-border-width`, `--slide-body`. |
| `assess-solution-delivery`, `compare-scope-options`, `prepare-sales-pursuit` | `skills/<name>/assets/` | One asset each. |
| Roadmap Kit (proposed `build-roadmap`) | `assets/rk.css`, `rk.js`, `rk-live.js` | 27 components with IDs A1 to G4. The live specimen sheet is the documentation. |

The brand-renderer SKILL.md sets the boundary: identity (palette, type, borders, radius, logo, contrast) is shared and checked; composition (slide layout, card patterns, footers, density) belongs to each producing skill. There is no mandatory card pattern, header bar or footer.

### Rules for Figma components

1. Get the node with `get_design_context`, which returns reference code and a screenshot. Treat its code as a reference. Rewrite it in the target template's markup and `--brand-*` (or `--rk-*`) variables.
2. Map each Figma component to an existing template section or kit component ID before writing code. A Figma card maps to kit `C1`, a Gantt bar to `E2`, and so on. List any Figma component with no match and ask whether it is new.
3. Change the shared component, not one artifact. For the kit, a change lands in `rk.css` or `rk.js` so every roadmap gets it.
4. Code Connect (`add_code_connect_map`) can record the mapping. Use label `Web Components` for `<rk-roadmap>` and `Javascript` for `rk.js` renderers. Map only after the component exists in the repo.

## 3. Frameworks and libraries

- **Languages:** Python 3 (standard library) for all build, check and render scripts; plain JavaScript for browser renderers and Node token access.
- **UI frameworks:** none. Templates are static HTML with inline or adjacent CSS. The Roadmap Kit renders from JSON with vanilla JS and one custom element.
- **Styling:** plain CSS with custom properties. No preprocessor, CSS-in-JS or utility framework.
- **Document generation:** `docx` 9.6.1 and `pptxgenjs` 4.0.1 (Node), `python-pptx` for extraction only.
- **Browser QA:** `playwright` 1.62.1.
- **Package manager:** pnpm 11.25.0 (`package.json`). There is no bundler. `tools/estate.py sync` builds skill packages and ZIPs into `build/` and `dist/`, which are generated.

Figma's reference code is often React and Tailwind. Translate it to the target template's HTML and CSS variables. Do not add React, Tailwind or a bundler to a skill.

## 4. Asset management

- Assets come from the selected profile. `scripts/resolve_assets.py --json` resolves its logo and font paths; relative paths resolve beside the profile.
- Standalone HTML embeds assets as data URIs (`html_profile.data_uri`). Roadmap Kit bundles publish the logo as a separate file beside `plan.json`.
- No CDN configuration. The only allowed external fetch in claude.ai Artifacts is Google Fonts.
- The neutral profile has no logo, imagery or bundled fonts.
- Client logos and licensed fonts stay in the client's project, never in this repository.

### Rules for Figma assets

1. Download logos and images with `download_assets` only when the profile records them and their usage rights allow it.
2. Never redraw, trace or recolor a logo from a Figma screenshot. Use the exported file unchanged.
3. Store downloaded assets beside the project's `brand.md`, not under `skills/`.

## 5. Icon system

There is none, by policy. The neutral profile allows no decorative icons, and brand-renderer forbids emoji and decorative glyphs. Meaning comes from type, space and labels.

The Roadmap Kit has three functional symbols drawn in CSS, with no icon font or SVG set:

- **Diamond:** milestone.
- **Hatched square:** buffer.
- **Swatch square:** legend group.

### Rule for Figma icons

An icon in a Figma design needs a stated function before it enters a template. If the function exists already (milestone, status), use the kit symbol. Otherwise ask whether a functional icon set should be added to the profile. Never import decorative icons.

## 6. Styling approach

- **Method:** global CSS custom properties on `:root`, consumed by component classes in each template. The kit namespaces everything under `.rk` and `rk-` class prefixes so it can sit inside other pages.
- **Themes:** estate templates are light only. The kit adds dark mode through a theme file. It uses `prefers-color-scheme` guarded by `:root:not([data-theme="light"])`, plus `[data-theme="dark"]` and `[data-rk-theme]` overrides. A profile with no dark values stays light.
- **Responsive:** each template has its own breakpoint (`proposal.html` at 700px, the kit at 720px). Grids collapse to one column. Wide timelines and tables scroll inside their own container, never the page.
- **Print:** `proposal.html` has `@media print`. The kit does not yet.
- **Gates:** `skills/brand-renderer/scripts/brand_check.py` lints HTML, CSS, JS and Python for literal hex values that are not in the profile. Any hardcoded hex taken from Figma fails this gate.

```css
/* Right: profile-driven */
.panel { border: var(--brand-border-width) solid var(--brand-border); background: var(--brand-surface); }
/* Wrong: pasted from Figma */
.panel { border: 1px solid #E2DCD0; background: #F2EEE6; }
```

## 7. Project structure

```
policies/            brand.md, workflow.md, writing.md, skill-standard.md   (authorities)
skills/<name>/       SKILL.md, skill.yaml, scripts/, templates/ or assets/, references/
skills/_shared/      build-card.md, output-contract.md, release-gate.md
skills/brand-renderer/brand/    profile loader, token compiler, HTML embedder
tools/               estate.py (validate, sync, status, install), brand.py, catalog.py
config/              skill catalog, groups, plugin bundles, runtimes
examples/            synthetic fixtures per skill
build/, dist/        generated; never edit
```

Each skill is self-contained and declares its runtimes, inputs, outputs and dependencies in `skill.yaml`. Shared policy is copied into packages at build time and checked by hash.

## Workflow: Figma to an estate artifact

1. Get the Figma file URL from the user; the connector cannot list files. Extract `fileKey` and `nodeId` (convert `-` to `:`).
2. `create_session` with the file key and a one-line task description. Reuse its session ID on later calls.
3. For brand values, use `get_variable_defs`, then write a draft `brand.md` in the project with the source URL and date. Show the role table and get confirmation.
4. For a component, load the `figma-design-to-code` skill, then call `get_design_context`. Map the node to a template section or kit ID, and rewrite it with profile variables.
5. Render, then run `brand_check.py` and inspect the result at desktop and 400px widths.
6. Before delivery, run `python3 tools/estate.py validate`, `python3 -m unittest discover -s tests -v` and `python3 tools/estate.py sync`.
