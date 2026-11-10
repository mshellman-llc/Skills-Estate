---
skill: review-site-runtime
title: Refreshing a field service review site from a second Jira export
source: fictional
model: claude-opus-5-5
date: 2026-11-05
skillSha256: 33f4b81ea9544446b46f9b4f4076b80267d4399184c314d0093eb03db1b6ec6a
---

## Request

$build-review-site The delivery lead sent this week's Jira export for the field service portal. Refresh the review site from it, tell me which stories need a second look, and run the publish checks.

## Inputs

review-site-runtime has no entrypoint of its own. This run used it through `build-review-site`, the public skill that loads it, and ran the bundled scripts for real. The engagement is the kit's synthetic example, `examples/northwind/` ("Field Service MVP"). `review_site.py init` copied it into a scratch project. The run then refreshed the site twice: first from `jira-2026-01-09.csv` to set a baseline, then from `jira-2026-01-16.csv` as this week's export. The browser gate was skipped with `--skip-browser` because the recording session had no approved browser, so that check is reported pending.

```bash
python3 scripts/review_site.py init --project site
python3 scripts/review_site.py refresh --project site --input jira-2026-01-09.csv --origin "Jira CSV export by delivery lead" --scope "Coordinator portal project, all open issues"
python3 scripts/review_site.py refresh --project site --input jira-2026-01-16.csv --origin "Jira CSV export by delivery lead" --scope "Coordinator portal project, all open issues"
python3 scripts/review_site.py check --project site --skip-browser
```

## Output

Second refresh, as printed by `review_site.py refresh`:

```json
{
  "intake": {
    "status": "recorded",
    "tickets": 12,
    "added": 1,
    "removed": 0,
    "changed": 3,
    "conflicts": []
  },
  "queue": {
    "affected_stories": 3,
    "new_tickets": 1,
    "removed": 0,
    "file": "site/tracker/review-queue.md"
  },
  "build": {
    "status": "rendered",
    "dist": "site/dist",
    "files": 14,
    "brand": "Neutral",
    "brand_substitutions": [],
    "must_share": 0.8462,
    "unclassed": 2
  },
  "status": "rendered"
}
```

The generated `tracker/review-queue.md`, unedited:

```markdown
# Review queue

## Stories whose tickets changed

- Duplicate check (st-dup)
  - NW-12 status: In Progress -> Done
  - NW-12 category: wip -> done
- Region queues (st-route)
  - NW-13 points: None -> 3.0
- Close with work notes (st-close)
  - NW-31 summary: Close the visit with work notes -> Close the visit with work notes and photos

## New tickets to map or class

- NW-25 Visit reminder texts [To Do]; candidates: Book from the request (st-book), Technician calendar (st-cal), Customer survey (st-survey)
```

Publish checks from `review_site.py check --skip-browser` [trimmed to the rule results]:

```json
{
  "status": "pending",
  "failed": [],
  "pending": ["B0"],
  "results": [
    {"rule": "D1", "status": "passed", "detail": []},
    {"rule": "D2", "status": "passed", "detail": []},
    {"rule": "D3", "status": "passed", "detail": []},
    {"rule": "W1", "status": "passed", "strings": 93,
     "findings": [{"rule": "C12-verbatim-recycling", "severity": "WARN",
       "message": "23 phrases of 4+ words appear more than once. Consolidate to one authoritative home.",
       "samples": ["a second open request", "second open request for", "open request for the"],
       "fields": ["journeys.changes[0].after", "processes.request.dedupe", "stories.st-dup.what"]}],
     "read": "WARN findings need a reading pass before publishing"},
    {"rule": "B0", "status": "pending", "detail": "browser checks skipped on request"}
  ]
}
```

The site rebuilt into `dist/` with the overview, build, decisions, mockups and workflow pages. Three stories need a look. "Close with work notes" now includes photos, so check whether its `what` still describes the story. NW-25 is a new ticket with no story yet; the kit suggests three candidates. The data and writing gates passed, with one repetition warning to read. The browser gate is still pending, so the site is not ready to publish.
