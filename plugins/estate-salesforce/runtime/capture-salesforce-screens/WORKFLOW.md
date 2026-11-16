---
name: capture-salesforce-screens
description: 'Drive the sfqa CLI to run headless clickpath assertions against a Salesforce org and record each page''s visible text. It writes text evidence only, signs in through the SF CLI and keeps credentials out of the transcript. Trigger when you need to verify what a Salesforce page shows without a human watching: after deploying UI-affecting metadata and needing verification evidence, when estate-ac-qa needs its browser driver, or when a ticket needs proof that a value rendered. Do not trigger for interactive browser exploration (use sf-browser-automation) or for non-Salesforce pages.'
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.



# Capture salesforce screens

Checks real Lightning pages in a real headless Chromium, authenticated off the
SF CLI without an interactive login. The evidence is
text: the page's visible text and per-step assertions. Never take screenshots
or keep PNG or other raster captures; they cost tokens and credits and prove
less than an assertion on the rendered text.

**Tool:** point `SFQA_HOME` at the explicitly selected installation for this task.
Verify that its `sfqa.mjs` exists and inspect its current help before use. This
skill does not bundle that executable or establish that a cached installation is
approved. If no supported tool is available, report the browser check pending.

```bash
: "${SFQA_HOME:?Set SFQA_HOME to the selected tool installation}"
test -f "$SFQA_HOME/sfqa.mjs"
node "$SFQA_HOME/sfqa.mjs" help
```

Use an explicitly confirmed org alias and page or record ID from the task.
The examples below are synthetic; replace their identifiers before invocation.
A write in a clickpath needs the user's authorization for that target.

## When to use this

Use this skill when you need a headless, unattended clickpath assertion or a
read of a page's rendered text in a Salesforce org. Typical callers:

- **`estate-ac-qa`** loads this as its Step 0 browser driver
- Any agent that needs evidence that a deployed change renders
- Manual requests to "check the page" or "confirm the record shows the value"

For interactive exploration in a visible Chrome the user is watching, use
`sf-browser-automation` instead. This skill is headless-only.

## No image output

Use only `flow` with text output, and only steps that assert or record text.
Do not use `sfqa shot`, `sfqa batch` or `sfqa watch`, the `shot` step key, or
the `--full-page`, `--selector` crop, `--mask` and `--scale` flags: each
exists to write an image. Before the first run, confirm from `sfqa help` that a
`flow` run without `shot` steps writes no image files, failure captures
included. If the selected version always writes images, do not run it; report
the browser check pending and use a recorded data read instead. After every
run, list `outDir` and confirm it holds no image files.

## First run

```bash
node "$SFQA_HOME/sfqa.mjs" doctor            # checks SF CLI + Chromium
```

If Chromium is missing, report the dependency. Install a supported browser only when authorized. Do not launch installed macOS Chrome through Node or Playwright; use a permitted connected browser or supported isolated Chromium environment. Never retry the blocked launch path.

## Clickpath + acceptance criteria (the QA workhorse)

```bash
node "$SFQA_HOME/sfqa.mjs" flow --flow acceptance.json
```

```json
{
  "org": "CONFIRMED_ORG_ALIAS",
  "name": "GH-42 invoice summary fees",
  "outDir": "qa/GH-42",
  "text": true,
  "steps": [
    { "goto": "/lightning/r/Account/001.../view", "wait": "record" },
    { "expectText": ["Account Health Summary", "Annual Revenue"] },
    { "click": "a[role=\"tab\"]:has-text(\"Related\")" },
    { "expectText": "Contacts" },
    { "click": "button:has-text(\"Edit\")", "wait": "edit" },
    { "fill": { "selector": "input[name=\"Name\"]", "value": "Acme Corp" } },
    { "click": "button[name=\"SaveEdit\"]", "wait": "record" },
    { "expectText": "Acme Corp", "critical": true }
  ]
}
```

Writes `report.json`, `report.md` (per-step pass/fail) and, with `text`, each
page's visible text into `outDir`. Exit code 2 if any step failed, so it works
as a gate. `report.md` pastes straight into a GitHub issue or PR comment. Grep
the text files to confirm a value rendered. For a phone-width check, run the
same flow with `--viewport 390x844` and compare its text with the desktop run.
Check `ready` in each receipt: `false` means a readiness stage timed out and
the text may come from a partly-loaded page.

**Step keys:** `goto`, `wait`, `waitFor`, `settle`, `quiet`, `dismiss`, `click`,
`hover`, `type`, `fill`, `press`, `scroll`, `scrollTo`, `expectText`,
`expectNoText`, `critical`, `name`. Do not use `shot`. Do not use `clickAt`
either: it targets coordinates read from a picture. Click by selector.

## When to trust the detector

`flow` uses readiness heuristics. Verify them against representative pages in
the selected org before relying on them; prior measurements from another org do
not establish current readiness. When a heuristic should not have the final say,
for example an LWC doing an external callout that legitimately takes 20s, add a
`waitFor` on the text the page must show and an `expectText` after it, rather
than watching frames.

## Slowness is a finding, report it

Every page load reports `renderMs` (when the page actually stopped changing, the QA
signal) and `totalMs` (includes ~3.9s of our own confirmation window). `slow: true`
appears when `renderMs` exceeds `--slow-threshold` (default 5000).

Treat a slow page as a defect worth mentioning, not just a longer wait. Likely
causes: slow SOQL, an external callout, or a stale LWC needing recompile. Retry
with `--hard-refresh` to rule the last one out.

**Calibrate per org.** Measure representative pages in the authorized target and
record the samples before selecting `--slow-threshold`. A threshold from another
project is not a baseline for this one.

## How readiness works, and why you rarely need to tune it

Lightning boots async, keeps long-poll connections open forever (so `networkidle`
never fires), and renders into **shadow DOM** (so `document.querySelector` cannot
see its components). The tool therefore waits on a signal that needs no knowledge
of Salesforce internals: **the page stopped changing.**

Specifically: text length steady **and** no DOM mutation, across **all frames**, for
2500ms in the described implementation; confirm the selected tool's current
settings. Text can stabilize before all components arrive, an iframe can load
while the main frame is quiet, and persistent network connections can outlive
rendering. A quiet window is a heuristic, not proof that required content loaded.

Practical consequences:

- **Do not pass `settle` after a click.** Interaction steps auto-wait for quiet.
  Adding `settle` *disables* that and reverts you to guessing.
- `--wait <mode>` (`auto`, `record`, `list`, `edit`, `setup`, `none`) is only a
  speed hint. `auto` works on every page family, including Object Manager (which
  lives on a different domain and matches no standard content selector).
- Setup / Object Manager pages are a Lightning+Aura+Visualforce mix and are slower
  and uglier than anything you ship. Prefer testing real front-end pages.
- After deploying an LWC, add `--hard-refresh` to defeat a stale compiled bundle.
- Raise `--settle` only for genuinely animated content, e.g. dashboards.

## Clicking

`click: "<selector>"` dispatches **real mouse/keyboard events via CDP**, never a
JS `.click()`. Playwright hit-tests and enforces actionability. If a human could
not click it (covered by an overlay, hidden, disabled), the step **fails** rather
than silently passing. That is the QA-correct behaviour and the main reason not
to use JS clicks.

## Useful flags

| Flag | Why |
| --- | --- |
| `--dismiss` | Close toasts / walkthrough tooltips / splash modals first |
| `--viewport 390x844` | Mobile-width rendering, read through its text |
| `--hard-refresh` | Reload bypassing HTTP cache, stale LWC after a deploy |
| `--slow-threshold <ms>` | Flag slow pages as a finding (calibrate per org) |
| `--text` | Write visible page text (grep this to verify values) |

## Sessions

Inspect the selected tool's session configuration before use. Reuse a cached
session only after verifying its org and account match the task. Keep cookies in
private storage outside packages and reports. A username or matching alias alone
does not authorize reuse in another account context.

When supported by the selected tool, `sfqa session --org CONFIRMED_ORG_ALIAS
--refresh` renews that session and `--clear` removes it. Authentication changes
remain separate authorized account actions. Do not silently choose a cached org.

## Credential safety (why this is safe to run unattended)

- **No bearer token is ever handled.** Auth redeems a **single-use** frontdoor URL
  from `sf org open --url-only`, consumed in-process by `page.goto()`. It is burned
  by that one navigation. The legacy `frontdoor.jsp?sid=<accessToken>` trick is
  *not* used and no longer works on current orgs anyway.
- The URL is never printed. Every byte the process writes passes through a
  redaction filter that scrubs `otp`/`cshc`/`sid`/token shapes, including from
  uncaught exceptions and Playwright errors that quote the URL.
- Playwright tracing and HAR recording are deliberately disabled; both would
  persist the session cookie to disk.
- **Never** run `sf org open --url-only` or `sf org display --json` yourself and
  paste the output. That puts a live credential in the transcript. Let the tool
  consume them internally.

## Gotchas

- Deploy succeeding is not verification, and neither is a green `ready`. Grep
  the text files and read the failed step in `report.md`.
- If a run leaves an image file, such as a failure capture, the selected tool
  version is not compatible with this skill. Report it and stop using that
  version; do not keep, attach or push the file.
- Inspect the actual browser path and supported launch policy before running. The tool configuration does not override the prohibition on direct installed macOS Chrome launches. Record any headless rendering limits.
- Each invocation uses a fresh browser profile, so the HTTP cache is always cold
  between runs. Stale LWC bundles only matter *within* one batch/flow run.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
