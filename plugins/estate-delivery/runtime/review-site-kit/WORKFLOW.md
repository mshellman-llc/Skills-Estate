---
name: review-site-kit
description: Internal runtime for the review-site series. Holds the data contract, tracker adapters, story map and decision calculations, page templates, the shared stylesheet, the renderer and the publish gates. Load it through tracker-intake, moscow-story-map, decision-register or review-site; it has no entrypoint of its own.
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.


# Review site kit

This runtime gives the four public skills one implementation of the data contract, the calculations and the checks. Change it here and every skill in the series picks up the change.

## Contents

- `schema/`: JSON Schemas for `site.json`, `tickets.json`, `stories.json`, `questions.json`, `journeys.json` and `processes.json`. [The data contract](references/data-contract.md) says who writes each file.
- `lib/rsk/`: the Python library, standard library only.
  - `tracker.py`: adapters for Jira CSV, any table CSV and canonical JSON. It also parses descriptions, writes intake records and computes deltas.
  - `stories.py`: story sync, readiness, Must share, unclassed tickets, the critical path and candidate stories for new tickets.
  - `decisions.py`: register checks, merging saved answers, and CSV and Markdown exports.
  - `render.py`: computes the page data and writes `dist/`.
  - `gate.py`: data, writing and browser gates.
  - `brand.py`: turns a brand profile into CSS custom properties.
- `assets/site/`: `page.html` (the shell), `site.css` (one stylesheet for every page), `site.js` (shared helpers and the store), and one script per page.
- `checks/browser_checks.cjs`: computed-style and DOM checks for the rules that a browser can test.
- `references/review-rules.md`: the rules log. Every rule names its check.
- `examples/northwind/`: a synthetic engagement with two tracker exports, used by `review-site init` and the tests.

## Change rules

Keep pages as fixed templates that read `data/site-data.js`. A page change goes in `assets/site/`, never in a rendered `dist/`. A new field goes in the schema first, then the library, then the page script.

When a reviewer comment produces a new rule, add it to [the review rules](references/review-rules.md) in the Skills Estate source repository with the date, and add a check to `checks/browser_checks.cjs` or `lib/rsk/gate.py` when the rule can be tested. Then run the series tests in `tests/test_review_site.py`.

Keep client names, tracker URLs, ticket keys, people and brand values out of this folder. They belong in each engagement's `config/site.json`, `content/` files and brand profile.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
