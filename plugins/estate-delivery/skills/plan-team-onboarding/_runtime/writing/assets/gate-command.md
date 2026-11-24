---
description: Check internal writing in this session or review outgoing copy with one independent reviewer
argument-hint: FILE_OR_ARTIFACT_LINK [--audience internal|external]
---

Apply the writing skill to $ARGUMENTS. Default to internal work unless the task says the copy goes to a client, the public or a hiring team. A file in artifacts/ is not automatically external.

1. Run the writing scan and fix the wording in this session. Internal work ends with an in-line read; do not start Agent, Task, another model or a headless session.
2. For external copy, list its sources and prepare once: `python3 ~/.agents/writing/bin/check.py --file PATH --audience external --prepare REVIEW --sources SOURCES.json --writer WRITER_SESSION --json`. Use the writer's actual session ID. The assignment records one reserved reviewer session and a two-round budget.
3. Use only that independent reviewer for the line pass, claims check, document map and spot audit. Read long text in bounded parts within that same session. Every review record names the same reviewer and session. The writer applies corrections; the reviewer does not rewrite the source. Do not start worker groups, another model family, a separate auditor or nested agents.
4. When using headless Claude for the one reviewer, use `claude -p --session-id REVIEWER_SESSION` from the assignment and include the source file's absolute path in the request. Resume that same session once if corrections require the final round. Never launch a replacement process with a new session ID.
5. For outgoing copy, also run `evidence_scan.py --file PART --per-line --json` on the extracted text, with `--data-piece` when numbers are the subject. These are local checks; they do not start models.
6. Validate with `check.py --file PATH --audience external --verdicts REVIEW/verdicts.json --document-map REVIEW/map.json --audit REVIEW/audit.json --sources SOURCES.json --writer WRITER_SESSION --full --json`. To correct findings, prepare the same folder with `--round 2 --verdicts REVIEW/verdicts.json`, retain accepted verdicts, and resume the original reviewer once. Validate with the carried and changed verdicts together.
7. Stop after round 2, including failures or timeouts. Report remaining errors once and keep publication blocked. Do not reset the review folder or budget, ask another reviewer, or repeat until passing. More review requires a new explicit request from the owner.
