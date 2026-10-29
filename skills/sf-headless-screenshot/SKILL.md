---
name: sf-headless-screenshot
description: 'Drive the sfqa CLI to capture headless screenshots and run clickpath assertions against a Salesforce org. No interactive login, no credential exposure. Trigger when you need to capture what a Salesforce page looks like without a human watching: after deploying UI-affecting metadata and needing verification evidence, when estate-ac-qa needs its browser driver, or when a ticket needs screenshot proof of a rendered page. Do not trigger for interactive browser exploration (use sf-browser-automation) or for non-Salesforce pages.'
---


# Salesforce Headless Screenshot

Captures real Lightning pages from a real headless Chromium, authenticated off
the SF CLI. No interactive login, no credential in the transcript.

**Tool:** resolve `SFQA_HOME` once for the current host, then use it throughout:

```bash
if [[ -z "${SFQA_HOME:-}" ]]; then
  if [[ -f "$HOME/.agents/tools/sfqa/sfqa.mjs" ]]; then
    SFQA_HOME="$HOME/.agents/tools/sfqa"
  else
    SFQA_HOME="$HOME/.claude/tools/sfqa"
  fi
fi
```

Run it as `node "$SFQA_HOME/sfqa.mjs"` (or `"$SFQA_HOME/bin/sfqa"`).
The explicit environment variable supports custom installs; Codex and Claude defaults
remain automatic. Full flag list: `sfqa help`.

## When to use this

Use this skill when you need a headless, unattended screenshot or clickpath
assertion against a Salesforce org. Typical callers:

- **`estate-ac-qa`** loads this as its Step 0 browser driver
- Any agent that needs visual evidence of a deployed change
- Manual requests for "show me the page" or "screenshot the record"

For interactive exploration in a visible Chrome the user is watching, use
`sf-browser-automation` instead. This skill is headless-only.

## First run

```bash
node "$SFQA_HOME/sfqa.mjs" doctor            # checks SF CLI + Chromium
```

If Chromium is missing: `cd "$SFQA_HOME" && npx playwright install chromium`.

## Single screenshot

```bash
node "$SFQA_HOME/sfqa.mjs" shot \
  --org StevenC2 \
  --url /lightning/r/Account/001TH00000jd34FYAQ/view \
  --wait record \
  --out qa/GH-42/account.png --text
```

Writes `account.png`, `account.meta.json` (URL, title, readiness) and, with
`--text`, `account.txt` containing the page's visible text, which is what you
should grep to confirm a value rendered.

Prints a JSON receipt. **Check `ready`**: `false` means a readiness stage timed
out and the image may show a partly-loaded page.

## Many screenshots (one browser, one session)

```bash
node "$SFQA_HOME/sfqa.mjs" batch --list shots.json
```

```json
{
  "org": "StevenC2",
  "outDir": "qa/GH-42",
  "viewport": "1600x1000",
  "text": true,
  "shots": [
    { "name": "quote",    "url": "/lightning/r/Quote/0Q0.../view", "wait": "record", "fullPage": true },
    { "name": "accounts", "url": "/lightning/o/Account/list",      "wait": "list" },
    { "name": "fields",   "url": "/lightning/setup/ObjectManager/Account/FieldsAndRelationships/view" }
  ]
}
```

## Clickpath + acceptance criteria (the QA workhorse)

```bash
node "$SFQA_HOME/sfqa.mjs" flow --flow acceptance.json
```

```json
{
  "org": "StevenC2",
  "name": "GH-42 invoice summary fees",
  "outDir": "qa/GH-42",
  "text": true,
  "steps": [
    { "goto": "/lightning/r/Account/001.../view", "wait": "record" },
    { "expectText": ["Account Health Summary", "Annual Revenue"], "shot": "details" },
    { "click": "a[role=\"tab\"]:has-text(\"Related\")", "shot": "related" },
    { "expectText": "Contacts" },
    { "click": "button:has-text(\"Edit\")", "wait": "edit", "shot": "edit-modal" },
    { "fill": { "selector": "input[name=\"Name\"]", "value": "Acme Corp" } },
    { "click": "button[name=\"SaveEdit\"]", "wait": "record" },
    { "expectText": "Acme Corp", "shot": "saved", "critical": true }
  ]
}
```

Writes numbered PNGs plus `report.json` and `report.md` (inline screenshots,
per-step pass/fail) into `outDir`. Exit code 2 if any step failed, so it works as
a gate. `report.md` pastes straight into a GitHub issue or PR comment.

**Step keys:** `goto`, `wait`, `waitFor`, `settle`, `quiet`, `dismiss`, `click`,
`clickAt`, `hover`, `type`, `fill`, `press`, `scroll`, `scrollTo`, `expectText`,
`expectNoText`, `shot`, `critical`, `name`.

## When to trust the detector, and when to use your own eyes

`shot`/`batch`/`flow` auto-detect readiness. It is deterministic (16/16 identical
runs across four page families), so trust it for bulk capture.

Use `watch` when a heuristic shouldn't have the final say, for example an LWC doing
an external callout that legitimately takes 20s, a page that looks wrong, or
anything unfamiliar:

```bash
node "$SFQA_HOME/sfqa.mjs" watch --org StevenC2 \
  --url /lightning/r/Account/001.../view --every 2000 --for 20000 --out-dir qa/watch
```

It captures a frame every N ms and **decides nothing**. Read the frames, judge
visually, and re-run with a larger `--for` if `stillMoving` is true.

## Slowness is a finding, report it

Every capture reports `renderMs` (when the page actually stopped changing, the QA
signal) and `totalMs` (includes ~3.9s of our own confirmation window). `slow: true`
appears when `renderMs` exceeds `--slow-threshold` (default 5000).

Treat a slow page as a defect worth mentioning, not just a longer wait. Likely
causes: slow SOQL, an external callout, or a stale LWC needing recompile. Retry
with `--hard-refresh` to rule the last one out.

**Calibrate per org.** On the StevenC2 sandbox, front-end pages genuinely render in
5-8s (Account list ~5.5s, Opportunity record ~8s), so the 5000 default flags nearly
everything. Use `--slow-threshold 9000` there.

## How readiness works, and why you rarely need to tune it

Lightning boots async, keeps long-poll connections open forever (so `networkidle`
never fires), and renders into **shadow DOM** (so `document.querySelector` cannot
see its components). The tool therefore waits on a signal that needs no knowledge
of Salesforce internals: **the page stopped changing.**

Specifically: text length steady **and** no DOM mutation, across **all frames**, for
2500ms. All three parts were required to make it deterministic:

- Text alone captured a 2659-char Account record page whose finished state is 4386.
- Main-frame-only mutation captured Apex Classes at 1587 chars (finished: 6617).
  Setup embeds a Visualforce iframe that attaches late, and while it loads the main
  frame is perfectly quiet.
- Network activity is unusable in both directions: long-polling re-bumps it every
  1.2-5.3s *after* render, a warm cache lets it go quiet *mid*-render, and
  `/aura?r=...` requests stay in-flight 6+ seconds so in-flight never hits zero.
- A 1500ms window returned a 277-char Object Manager page on 2 of 3 runs; measured
  plateaus reach ~1.5s, hence 2500ms.

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

## Clicking: selector vs coordinates

Both dispatch **real mouse/keyboard events via CDP**, never a JS `.click()`.

- `click: "<selector>"` -- Playwright hit-tests and enforces actionability. If a
  human could not click it (covered by an overlay, hidden, disabled), the step
  **fails** rather than silently passing. That is the QA-correct behaviour and the
  main reason not to use JS clicks.
- `clickAt: [x, y]` -- raw coordinates, zero DOM knowledge. Use this when you have
  just looked at a screenshot and want to click what you see. Coordinates are in
  CSS pixels of the viewport (`--viewport`), not the retina pixels of the PNG:
  with the default `--scale 2`, divide the pixel position in the image by 2.

## Useful flags

| Flag | Why |
| --- | --- |
| `--full-page` | Whole scrollable page, not just the viewport |
| `--selector <css>` | Crop to one component (e.g. a single LWC) |
| `--mask <css,css>` | Cover elements, redact PII before sharing |
| `--dismiss` | Close toasts / walkthrough tooltips / splash modals first |
| `--viewport 390x844` | Mobile-width rendering |
| `--headed` | Watch it run, for debugging |
| `--hard-refresh` | Reload bypassing HTTP cache, stale LWC after a deploy |
| `--slow-threshold <ms>` | Flag slow pages as a finding (calibrate per org) |
| `--text` | Write visible page text (grep this to verify values) |

## Sessions

Cookies are cached per org at `~/.sfqa/sessions/<username>.json`, mode `0600`, so
repeat runs skip re-auth. Expired cookies are detected on the first navigation and
re-minted automatically. To force a fresh session:
`sfqa session --org X --refresh`. To wipe one: `sfqa session --org X --clear`.

If auth genuinely fails, the fix is always `sf org login web --alias <org>`.

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

- Deploy succeeding is not verification, and neither is a green `ready`. Look at
  the PNG, and grep the `.txt`.
- On failure the tool writes `<out>.FAILED.png`. Check it first when diagnosing.
- Screenshots are retina (`--scale 2`), so a 1600x1000 viewport yields a 3200x2000
  PNG. Use `--scale 1` for smaller files.
- Front-end pages in the StevenC2 sandbox render in ~5-8s; Setup is slower still.
- The browser defaults to real Chrome (`channel: 'chromium'`), not Playwright's
  `chrome-headless-shell`, so rendering matches what a human sees. `--headless-shell`
  trades that fidelity for speed.
- Each invocation uses a fresh browser profile, so the HTTP cache is always cold
  between runs. Stale LWC bundles only matter *within* one batch/flow run.
