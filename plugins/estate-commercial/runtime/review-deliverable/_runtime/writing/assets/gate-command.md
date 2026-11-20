---
description: Run the full writing review on a file or artifact before it goes to a client or goes public
argument-hint: FILE_OR_ARTIFACT_LINK
---

Run the writing skill's full review on $ARGUMENTS.

1. For a claude.ai artifact link, read the page with the artifact tools and save its HTML to a working folder. For a file, use it where it is.
2. Write the names of the documents the piece was written from to `SOURCES.json`.
3. Run `python3 ~/.agents/writing/bin/check.py --file PATH --prepare REVIEW --sources SOURCES.json --json` and fix every scanner finding at its source.
4. Give each worker group in `REVIEW/assignments.json` to a reviewer other than the writer. Send at least one group to the other model family when its command line tool is installed: `codex exec` from Claude Code, `claude -p` from Codex. Each reviewer writes one verdict per line.
5. Run the document pass on the full text. Then run the spot audit with a reviewer that wrote none of the verdicts.
6. For a piece bound for a client or the public, scan each file in `REVIEW/text/` with `evidence_scan.py --file PART --per-line --json` from the same bin folder, adding `--data-piece` when the numbers are the subject. Correct each flag in the source file. If `evidence_scan.py` is not installed, say so in the report.
7. Run `check.py --file PATH --verdicts REVIEW/verdicts.json --document-map REVIEW/map.json --audit REVIEW/audit.json --sources SOURCES.json --full --json`. Fix each finding at its source and repeat until the receipt passes.
8. Report the receipt path, the status of each step, the evidence scan result and whether the audit was independent. An AI-detector score is never a pass or a fail.
