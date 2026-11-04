---
name: roadmap-artifacts
description: Build interactive roadmaps (now/next/later boards, Gantt timelines, swimlanes, sprint trains, launch countdowns, RAID overlays, outcome roadmaps, GTM, content, brand/demand and OKR roadmaps) as embeddable components in the governing org's brand, with data from connected tools such as Google Sheets, Linear, Jira, Asana or Notion. Use whenever the user asks for a roadmap, timeline, release plan, migration plan, launch plan, campaign calendar or delivery plan as an artifact, page section or embedded element, or wants an existing roadmap rebranded, connected to live data, or turned from a feature list into outcomes. Do not use it to rank candidates (use prioritization) or to plan a sprint (use sprint-planning).
---

# Roadmap artifacts

The kit has three formats: **Relaxed** (the default: a friendly dashboard, after Coursify), **Compact** (a dense working tool, after Venture CRM) and **Editorial** (a strategy page, after Avalon). Each roadmap is built in one format, set with `meta.mode`; viewers cannot switch it. A brand changes colors, fonts and radius in all three; the components and each mode's treatment stay the same.

A roadmap is three things kept apart:

- **Plan**: a JSON file of the work (`references/schema.md`). This is the only thing you write per roadmap.
- **Theme**: a CSS file of `--brand-*` settings compiled from the org's brand profile (`references/branding.md`). Without a profile, each mode keeps its default look.
- **Kit**: the fixed renderer and components (`assets/rk.js`, `assets/rk.css`, and `assets/rk-live.js` for live data).

Never write roadmap CSS or markup by hand, and never restyle the kit per roadmap. That is what keeps every roadmap in an org consistent, and every org's roadmaps in that org's brand.

## Workflow

1. **Template.** Pick one from `references/catalog.md`. If nothing fits, pick the closest block recipe and say which.
2. **Brand.** Resolve the identity in the order given in `references/branding.md` and state it in one line. Use only confirmed values. Draft values need the user's go-ahead.
3. **Data.** If the work lives in a connected tool, read it there (snapshot) and decide with the user whether the page should stay live (`references/connectors.md`). Otherwise build from the request. Ask only for an input that changes the plan's structure. Infer the rest, say so in `meta.source`, and list the inferences in the follow-up.
4. **Plan.** Write the plan JSON. Fill every column and lane with specifically named work tied to an outcome.
5. **Build.** `python3 scripts/build.py plan.json --brand <profile> --out <dir>`. It validates the plan, compiles the theme, prints the brand report, and writes a folder of separate files. Relay any neutral substitutions and contrast warnings to the user.
6. **Deliver** to the right target (below), then write the template's follow-up analysis in chat, not in the page.

## Outcome mode

When a now/next/later roadmap should commit to outcomes rather than features, follow [outcome roadmaps](references/outcome-roadmaps.md). Rank candidates with `prioritization` first, and take jobs and desired outcomes from `jtbd-framing` where they exist. Each Now card has a named owner and an Outcome written as baseline → target. It cites its evidence and lists dependencies by RAID ID. Now holds at most three cards. Later holds problems, not dates. Run `python3 scripts/outcome_check.py plan.json` before `build.py`; it exits 1 when Now is over the cap or a Now Outcome has nothing to measure.

## Targets

- **Skills Estate page** (single file, no network): `python3 scripts/rk_embed.py page plan.json --output attempt-001/roadmap.html`, with `--profile brand.md` for a confirmed project profile; otherwise the estate neutral profile applies. The stylesheet is rewritten to the profile's roles only: no web fonts, no fixed colors, the profile radius on every corner and the profile border width. Run `brand-renderer` on the result. `interactive-proposal` and `journey-mapping` inline the same components through `rk_embed.assets()`; `jtbd-framing` builds its readouts with `page`. Live bindings are refused here; build a snapshot.
- **claude.ai Artifact** (`--target artifact`, the default): publish `index.html` with the `files` map that `build.py` prints, plus its `capabilities` when the plan has live bindings. To update, edit `plan.json` and republish the same `file_path`.
- **An existing website or app** (`--target web`, or copy the files): put `rk.css`, `theme.css`, `rk.js` (and `rk-live.js`) in the site's static assets, then place `<rk-roadmap src="/path/plan.json"></rk-roadmap>` wherever the roadmap belongs. It works in React, Vue and plain HTML because it is a standard custom element. Live bindings work only inside claude.ai Artifacts. Elsewhere the snapshot renders.
- **Inside another artifact or page you are building**: include the same files and either the `<rk-roadmap>` element or `RoadmapKit.mount(plan, element)`. Several roadmaps can share one page.
- **No shell available**: write the files yourself. Copy `rk.css`, `rk.js` and `rk-live.js` unchanged, write `theme.css` by hand from the brand roles in `references/branding.md`, write `plan.json`, and use the page markup that `build.py` would produce: two stylesheet links, `<rk-roadmap src="plan.json">` and the script tags.

## Updating a plan

The page has a "Copy plan JSON" button. When the user pastes JSON back, treat it as the current plan: card moves they made are decisions. Keep the same `id` so saved board state lines up.

## Rules

- One identity per roadmap. Use recorded brand values only. Missing roles fall back to neutral and get reported. Contrast failures are reported, not fixed.
- Legend groups use palette slots `c: 1` to `6`, which map to the brand's chart colors. Status, risk, confidence and capacity use tones (`good`, `warn`, `crit`, `info`, `muted`), which are fixed by the kit and never themed.
- At most 6 legend groups.
- Card titles name initiatives ("Import clients from QuickBooks in one step"), not categories.
- Live bindings need a `verified` note from a real observed result. Never ship guessed payload paths.
- Read-only connectors only. The kit never writes back to a source tool.
- Mark invented inputs as example data in `meta.source`.
- Show evidence as numbers: `cite` on cards, callouts and rows, with one `evidence` block (or the host page's list). Never label every card with its basis.

## Files

- `assets/rk.css`, `assets/rk.js`, `assets/rk-live.js`: the kit, with the Relaxed, Compact and Editorial formats.
- `themes/neutral.json`: the estate neutral profile as kit JSON. `themes/example-brand.md`: a fictional `brand.md` showing the format.
- `scripts/build.py`: validator and bundle builder. `scripts/outcome_check.py`: the outcome-mode check, with `scripts/outcome_check_selftest.py` and its fixtures. `scripts/brand.py`: brand profile → theme CSS and report. `scripts/rk_embed.py`: single-file estate pages and the inline assets other estate skills embed.
- `references/schema.md`, `references/catalog.md`, `references/branding.md`, `references/connectors.md`, `references/outcome-roadmaps.md`.
- `UPSTREAM.md` and `LICENSE-UPSTREAM`: provenance and license for the outcome-mode material.
- `examples/*.json`: six worked plans. `06-sheets-live.json` is the live-data example.
