---
name: render-offering-brief
description: 'Render a defined offering into a two-page internal sales brief and one-page external PDF. Use for playbook handouts, sales enablement sheets, or a catalog of offering PDFs. Accepts structured Markdown or rich JSON with qualification criteria, talking tracks, delivery steps, and scope boundaries. Applies the project brand profile or neutral estate profile, checks actual PDF page counts and browser layout, and retains outputs for review.'
---

# Render offering brief

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../writing-diagnostics/references/registers/readout-brief.md). Inputs, not a final pass.**

Turns one playbook into two branded PDFs, using the same visual system every time:

- **Internal brief** (`*-internal-brief.pdf`): sales enablement, two pages. The seven Clarity questions as numbered sections (01-07), with optional qualifier/disqualifier boxes, a talking-tracks table, numbered delivery steps, and Positioning / Two-gears callouts. Footer, "INTERNAL USE ONLY".
- **External one-pager** (`*-external-onepager.pdf`): client-facing, one page. Headline, subtitle, intro, a "What you get" grid, a two-column "who it's for / why it matters" band, a "How it works" callout, and a footer with the cost/CTA line.

This is the rendering mode of **manage-service-offering**. Its primary workflow,
[manage-service-offering](../manage-service-offering/SKILL.md), defines the offering and its
house-format entry. The separate [plan-offering-artifacts](../plan-offering-artifacts/SKILL.md)
mode plans the artifact package and its dependencies. This workflow renders
the agreed entry to PDF; it does not define the offering or mark the suite complete.

## Shared brand and runtime

Select a confirmed profile with `--profile /path/to/brand.md`; otherwise the renderer uses the current project's `brand.md` or the packaged neutral estate profile. Colors, font stack, minimum body type size, radius, and optional logo come from that profile. A missing declared font or logo fails the build. The neutral profile needs no logo or custom font. Keep client assets in their project.

The layout files contain component rules, not a separate brand authority. Use the author's confirmed voice profile for wording; the renderer does not impose a company voice or invent contact details.

The renderer uses Python `Jinja2` and `pypdf`, plus Node.js, Playwright and Chromium. Install the pinned requirements into a project virtual environment and the Node dependencies locally:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install --ignore-scripts
npx playwright install chromium
PYTHON=.venv/bin/python bash scripts/setup.sh
```

Set `ESTATE_NODE` when Node is not on PATH, `ESTATE_NODE_MODULES` when Playwright lives outside the current project's `node_modules`, and `PW_CHROMIUM` to use an existing Chromium executable. The renderer launches an isolated browser and blocks remote resources. It does not use personal browser sessions.

## Two input modes

**Plain, from the house format.** Point the renderer at a manage-service-offering entry or a whole corpus. It maps the seven internal answers and six external answers straight into the templates. The rich components stay off, so you get a clean 7-part brief and a standard one-pager. Best for rendering a catalog quickly and consistently.

```bash
# one entry by its number
python scripts/render_playbook.py --md CATALOG.md --entry 01 --out ./pdfs
# the whole catalog
python scripts/render_playbook.py --md CATALOG.md --all --out ./pdfs
```

**Rich, from a JSON spec.** Supply a spec to light up the extra components: qualifier/disqualifier boxes, talking-tracks table, a delivery bar, numbered steps, Positioning/Two-gears callouts, an external kicker, subtitle, and a labelled two-column band with a centered note. Use this for a flagship offering you want to look like the hand-built exemplar.

```bash
python scripts/render_playbook.py --json spec.json --out ./pdfs --prefix "01-"
```

The JSON schema and the full field-to-slot mapping are in `references/field-mapping.md`. Read it before hand-authoring a spec.

## How to choose

- Rendering a catalog, or a play that only has the standard seven/six answers: use `--md`. Fast, consistent, nothing to author.
- A front-door or flagship offering that deserves the qualifier boxes, talking tracks, and step-by-step delivery: author a JSON spec (start from `references/field-mapping.md`), render with `--json`, and it will match the exemplar layout.
- You can mix: render the whole catalog with `--all`, then render flagship plays with `--json` into a separate attempt directory. Existing output files are never overwritten.

## Discipline

- **Render only what the source says.** The PDFs restate the playbook's facts; they add none. Do not invent a headline claim, a metric, a price, or a duration to fill a slot. If a required slot has no grounded content, obtain it before rendering. Omit optional slots when their source is absent.
- **Free vs paid footer.** The renderer sets the external footer from the tier in the heading: `(free)` gets "What it costs: nothing. It is how we start."; anything else gets a neutral "Ready when you are." Do not label a paid play as free.
- **Same visual every time.** Don't hand-tune spacing or colors per play. If content overflows, revise the wording without dropping scope, claims, or qualifiers, then render another attempt. Keep the failed output.

## Workflow

1. Read the offering source and confirm the requested audience. Use the primary `manage-service-offering` workflow for offering definition; this mode renders the agreed definition.
2. Run the dependency preflight and select the brand profile.
3. Use `--md` for standard entries or `--json` for the richer components. Read [field-mapping.md](references/field-mapping.md) before authoring JSON.
4. Render into a new, empty attempt directory. Strict parsing rejects unknown labels and required-content gaps. Source HTML permits only inline emphasis; scripts, images, arbitrary attributes, and resource loads are rejected.
5. Inspect the saved HTML, PDF, page images, and checks. The browser checks page bounds and footer overlap; `pypdf` checks the actual PDF page count. Render the PDF pages to images and inspect every page before delivery.
6. Compare the PDF text with the source: scope, exclusions, audience, delivery steps, quantities, and contact details. Parser tests alone do not establish an acceptable deliverable.
7. Deliver the two requested PDFs, or the requested single variant. Retain the source, all attempts, checks, and manifest. A failed render can leave a PDF for diagnosis; its presence is not a passing result.

## Output and failure handling

A successful run writes a source/profile/asset manifest with artifact hashes and page counts. The internal brief has two pages; the external handout has one. Missing content, assets, dependencies, overflow, footer collisions, and unexpected PDF page counts fail the run. Repair the cause and use a new output directory.

`--no-strict` permits parser warnings for an explicitly requested diagnostic draft; it does not bypass required JSON fields or PDF layout checks. Never deliver a draft whose source fields were ignored.

## Files

- `templates/internal_brief.html`, `templates/external_onepager.html`: the two layouts, including optional rich components.
- `assets/brand.css`: layout rules using the shared profile's CSS variables.
- `scripts/render_playbook.py`: Markdown parsing, JSON rendering and manifest generation.
- `scripts/pdf_runtime.py`, `scripts/render_pdf.mjs`: input validation, actual PDF generation and layout checks.
- `scripts/setup.sh`: read-only dependency and profile preflight.
- `fixtures/synthetic-offering.json`: a fictional offering covering the rich components.
- `references/field-mapping.md`: field schema and Markdown-to-slot mapping.
