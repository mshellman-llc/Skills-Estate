---
name: writing
description: "Write or review every word a person will read, in any format, against the owner's writing rules folder. Use before returning a reply, document, page, deck, message, interface label, commit message or pull request description, and when asked for writing integrity, a prose pass, a de-AI pass or to humanize text. Reviews text, reviews rendered pages, workbooks and decks on their extracted text, writes as the owner or as a brand, and logs wording corrections. Code and exact quotations are exempt."
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.


# Writing

Load this skill before writing any text for a reader. It is the estate's one writing skill: other skills send their prose here. It also answers to "writing integrity", "prose pass", "de-AI" and "humanize". It holds the method, the check script, the extracted-text procedure and the review record formats. The rules live in a folder the owner keeps outside this skill, and no rule text is copied here.

## Find the rules folder

`scripts/check.py` takes the folder from `--rules-dir`, then from the `WRITING_HOME` variable, then from the path written in `~/.agents/writing/home`. Read the files a task needs from that folder at the start of the task.

| File | Holds | Read for |
| --- | --- | --- |
| `rules.md` | The writing standard | Every mode |
| `patterns.json` | Phrases and habits the scanner checks | `check.py` reads it |
| `registers.md` | Guidance learned for a channel or audience | Every mode |
| `voice-profile.md` | How the owner sounds as the author | Owner-voice mode |
| `brands/<brand>.md` | One brand's voice | Brand mode |
| `corrections.md` | Dated log of wording corrections | Learn |

On a surface with no file access, read the current rules through the Knowledge Hub. When the Hub cannot be reached, use the owner's bundled rules skill if the host lists one, and record its build stamp in the review record. Look the rules up without narrating the lookup. Mention it only when every source fails; then report the review as incomplete and name the missing file. Do not review from a remembered copy.

When two rules disagree, the newer one applies. The owner's correction in the current conversation outranks every file.

## Scope

The writing rules cover text in every format: chat replies, documents, pages, decks and speaker notes, headings, bullets, table cells, captions, chart titles and labels, interface text, file names, status pages, emails, chat messages, texts, posts, bios, commit messages, pull request descriptions and résumé lines. The reader-based allocation below also applies to outlines, headline options and drafts.

Code and code comments are exempt. So are quotations kept word for word. A label or message string inside code is in scope. For a rendered or generated file, review the text extracted from the output.

## Choose the mode

1. Review is the default. Apply `rules.md` and `patterns.json` to the text.
2. Write as the owner when the piece goes out under the owner's name. Add `voice-profile.md`.
3. Write as a brand for a piece published under that brand. Add `brands/<brand>.md`. Use a brand voice only when its file exists; if the file is missing, ask which voice applies.
4. Learn when the owner corrects wording. Apply the fix to every affected passage. Then log it. Where the rules folder is on disk, add a row to `corrections.md`. Elsewhere, save it through the Hub with `save_update`, kind `decision`, key `writing-correction:<date>:<short-name>`. The record states the words before and after, the channel and audience, the date and the tool. `scripts/sync_corrections.py --apply` copies those Hub records into `corrections.md`, and `install_local.py --sync-corrections` runs it every day.

Writing in another person's voice is outside this skill.

## Set the register

Channels and audiences are not a fixed list. For each piece, write down the channel, who reads it, what they already know and what they must do. Those four answers set its length and structure. They also set how formal it is. Then read `registers.md` for an entry the owner has taught; a missing entry does not limit what you write. Pass the name to the check with `--register`. A name the check has not seen is accepted: the script adds it to `registers.md` with the date and the file, and the receipt says the name added no rules and lists the known names. When two entries fit, pass both with a comma, as in `client-facing,executive-page`. An entry that says "Pass `x`" is an alias: the check runs `x` in its place, or both names when the entry says "with it".

## Run the check

```sh
python3 scripts/check.py --file PATH [--register NAME] --json
```

| Exit | Status | Meaning |
| --- | --- | --- |
| 0 | `pass` | A full review: the scan, line pass, claims check, document pass and spot audit all ran and nothing blocks |
| 0 | `scan-pass` | Only the scanner ran, every in-scope line was scanned and no finding blocks |
| 1 | `fail` | `findings` lists each blocking line with its rule, the exact words and the fix |
| 2 | `incomplete` | The file could not be parsed, a rule could not run, or a part failed after two retries; `not_reviewed` names the lines |

The output carries `status`, `coverage` with `lines_total` and `lines_reviewed`, `findings`, `receipt` and `steps`. The script counts the lines each part scanned and compares them with the lines it extracted, so a gap returns `incomplete`. Text parts hold at most 300 lines for reading. Parts are not separate reviewer assignments.

`review` counts the scanner flags that wait for a line-pass answer, such as a list of three; they do not block a scan.

Run with only `--file`, the check covers the scanner. Its status is `scan-pass`, and `steps` lists the line pass and document pass as `not_run`. Report it as a scan, never as a pass; only a full review returns `pass`. Where the script cannot run, read the text against `rules.md` and `patterns.json` and say the scan did not run.

Fix each finding by rewriting the sentence, then run the check again. Replacing a flagged word with a synonym leaves the same sentence in place.

## Review a file in full

A full review adds two passes to the scan. Each one writes a record that `check.py` validates.

### Choose the depth by reader

Internal work stays in the main session. Chat replies, internal drafts, administration, instructions and private review pages get the scanner and an in-line review. Do not start a subagent, another model or a headless session for them. A file's name, format or folder does not determine its audience.

Only copy leaving the owner gets one independent reviewer: client deliverables, published pages and career copy. That reviewer completes every required check in the same session. It cannot be the writer or edit the source copy. It may read long text in bounded parts. Do not split those parts among agents, require another model family, or start an auditor, replacement reviewer or nested agent.

### Prepare and review

1. Settle facts, policy, prices and brand choices that only the owner can decide before starting the reviewer. A new owner decision stops the review and goes to the owner; it never triggers another review round.
2. Save source names in `SOURCES.json`. For outgoing copy, run `check.py --file PATH --audience external --prepare REVIEW --sources SOURCES.json --writer WRITER_SESSION --json`. Use the writer's actual session ID, including when work was written through a shell. The review policy records one assignment, a reserved reviewer session and a two-round limit by the source file's absolute path. Renaming a review folder does not reset it.
3. Fix scanner findings before review. Give the one reviewer the bounded text parts, outline, rules, register and sources. The reviewer writes the line verdicts, a document map and the spot-audit sample under one `reviewer` and `session` identity. Follow [line pass](references/line-pass.md) and [document pass](references/document-pass.md). The writer applies source changes.
4. Validate with `check.py --file PATH --audience external --verdicts REVIEW/verdicts.json --document-map REVIEW/map.json --audit REVIEW/audit.json --sources SOURCES.json --writer WRITER_SESSION --full --json`. The script enforces one reviewer across every pass and rejects records from the writer. A passing scan alone is not a full review.
5. If findings need a correction, retain accepted verdicts and use the same review folder. Prepare with `--round 2 --verdicts REVIEW/verdicts.json`, then resume that same reviewer once for changed lines and the document map. Pass the carried and changed verdict files together. The same reviewer audits without looking at its earlier verdict for each sampled line. The audit is a self-check by the independent reviewer; it is not another independent review.
6. Stop after the second round, including technical failures and timeouts. Style findings in that final round are logged instead of blocking; factual errors, unsupported claims and unresolved owner decisions still block publication. Report remaining errors once. Do not reset the budget, relabel the reviewer, change a folder, spawn replacements or repeat until passing. Further review requires a new explicit request from the owner.

On hosts without scripts, apply these same audience, reviewer and round limits in the conversation. When no independent reviewer is available, finish the internal draft and state that the external review is pending. Do not turn it into a reviewer pool.

## Report

Read the receipt before reporting. State which steps ran and each step's status. List the owner decisions that wait (`owner_decisions`) and the logged style items (`logged`) apart from the blocking findings. A `failed` step makes the review incomplete. The independent reviewer runs its own spot check; do not describe that spot check as a second independent review. Report line counts as coverage only.

In ordinary work, fix the wording and deliver it without describing the review. An AI-detector score is never a pass or a fail.

## Review rendered and generated files

When the piece is an HTML or SVG page, a page built by a script, a workbook, a Word document or a deck, review its extracted text instead of its markup. Follow [file review](references/file-review.md) every time, using `scripts/extract_review_text.py`:

1. Run its `extract` command on the files with `--out REVIEW/before --root PROJECT`, then `init-log REVIEW/before`.
2. Read every part to its end and record its read token. Review every line against the rules, including lines no scanner flags, and log each finding with its line ID and action.
3. Repair each finding where it originates: the HTML line, the generator or its data, or the workbook string the locator names. Rebuild generated files. Then check the rest of the piece for the same failure.
4. Extract again into `REVIEW/after`, run `diff` on the two folders and read every changed line.
5. Run `receipt` on the two folders. Claim full coverage only when it prints `COMPLETE`, and report its files, lines read and lines changed.

A read token shows that a part was opened to its end. It does not prove attention to every line. `check.py` runs on the same files, so a full review of a page uses this extraction for its line IDs.

`scripts/rendered_read_guard.py` is a PreToolUse hook that turns a whole-file read of a large page, workbook, document or deck toward the extractor. `install_local.py` copies it to `~/.agents/writing/bin/`, where the host's hook settings point.

## Hooks

On Claude Code and Codex, `scripts/hook.py` scans every reply and every prose file a tool writes, and allows at most two in-line correction attempts for a reply. It holds external copy that was explicitly declared with `--audience external` while its full review is pending, with at most two reminders. Internal files never start that gate. It also logs which session wrote each file, so `check.py` can reject verdicts written by the writer. `scripts/install_local.py` installs the scripts, the read guard and the `/gate` command. With `--watch DIR` it adds a launchd agent that runs `scripts/gate_watch.py`, so each file that lands in DIR gets `/gate` through Claude Code headless. Before the `Artifact` tool or an MCP publish tool sends content, `hook.py` checks those exact bytes and denies the call when they fail. That check runs once `~/.claude/settings.json` has a PreToolUse entry with the matcher `Artifact|mcp__.*[Pp]ublish.*` that runs `hook.py --tool claude-code`. `scripts/writing_system.py` builds the copies of the owner's rules for other hosts and reports drift. Its `instructions` command builds `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` from one source and, with `--install`, writes them into the home folder.
