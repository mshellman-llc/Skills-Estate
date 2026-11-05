---
skill: sf-headless-screenshot
title: Screenshot evidence for a new fee field on a wholesale account page
source: fictional
model: claude-opus-5-5
date: 2026-11-05
skillSha256: 06cdf4bb69534ca8360c6e45568165ebed6f98c4d74aa7100a73fef3d453cfe1
---

## Request

$sf-headless-screenshot We deployed the Delivery Fee field to the Account page layout in the uat-orchard sandbox for ticket GH-118. Get me screenshot proof that it renders on account 001UAT000000AbCDE and that the Related tab still loads. Don't edit anything.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. The recording session made up the org alias `uat-orchard`, the ticket and the record ID. It had no Salesforce org, no SF CLI session, no `sfqa` installation and no approved browser, so nothing below was captured. Following the skill, the answer prepares the run and reports the browser check as pending. It does not describe screenshots that don't exist.

The user confirmed the org alias and record ID in the request. The flow has no write steps, so it needs no write authorization.

## Output

I couldn't capture anything. `SFQA_HOME` isn't set in this environment, so there's no selected `sfqa` installation to run, and the skill doesn't bundle one. The browser check for GH-118 is **pending**.

Once a supported `sfqa` installation is selected, this is the run. First confirm the tool and its dependencies:

```bash
: "${SFQA_HOME:?Set SFQA_HOME to the selected tool installation}"
test -f "$SFQA_HOME/sfqa.mjs"
node "$SFQA_HOME/sfqa.mjs" help
node "$SFQA_HOME/sfqa.mjs" doctor
```

If `doctor` reports Chromium missing, stop and report it. Don't point the tool at the installed macOS Chrome.

Then run this flow as `qa/GH-118/acceptance.json`. It only reads: it opens the record, checks the field label, opens the Related tab and checks that it loaded.

```json
{
  "org": "uat-orchard",
  "name": "GH-118 delivery fee field on Account",
  "outDir": "qa/GH-118",
  "text": true,
  "steps": [
    { "goto": "/lightning/r/Account/001UAT000000AbCDE/view", "wait": "record" },
    { "expectText": "Delivery Fee", "shot": "details", "critical": true },
    { "click": "a[role=\"tab\"]:has-text(\"Related\")", "shot": "related" },
    { "expectText": "Contacts", "shot": "related-loaded" }
  ]
}
```

```bash
node "$SFQA_HOME/sfqa.mjs" flow --flow qa/GH-118/acceptance.json --hard-refresh
```

`--hard-refresh` rules out a stale cached bundle right after the deploy. Exit code 2 means a step failed, and `<name>.FAILED.png` is the first file to open. A passing run isn't proof on its own: open `details.png` and confirm the Delivery Fee value is visible, then grep the `.txt` beside it for "Delivery Fee". Report any step with `slow: true` as a finding. This org has no measured baseline yet, so leave `--slow-threshold` at its default and record the `renderMs` values as the first samples.

`report.md` from that run can go straight into GH-118.
