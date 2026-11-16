---
name: writing
description: "Write or review every word a person will read, in any format, against the owner's writing rules folder. Use before returning a reply, document, page, deck, message, interface label, commit message or pull request description. Reviews text, writes as the owner or as a brand, and logs wording corrections. Code and exact quotations are exempt."
---

# Writing

Load this skill before writing any text for a reader. It holds the method, the check script and the review record formats. The rules live in a folder the owner keeps outside this skill, and no rule text is copied here.

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

The check and both passes cover text in every format: chat replies, documents, pages, decks and speaker notes, headings, bullets, table cells, captions, chart titles and labels, interface text, file names, status pages, emails, chat messages, texts, posts, bios, commit messages, pull request descriptions and résumé lines. An outline, a set of headline options and a draft pasted into chat are in scope before the owner sees them.

Code and code comments are exempt. So are quotations kept word for word. A label or message string inside code is in scope. For a rendered or generated file, review the text extracted from the output.

## Choose the mode

1. Review is the default. Apply `rules.md` and `patterns.json` to the text.
2. Write as the owner when the piece goes out under the owner's name. Add `voice-profile.md`.
3. Write as a brand for a piece published under that brand. Add `brands/<brand>.md`. Use a brand voice only when its file exists; if the file is missing, ask which voice applies.
4. Learn when the owner corrects wording. Apply the fix to every affected passage. Then log it. Where the rules folder is on disk, add a row to `corrections.md`. Elsewhere, save it through the Hub with `save_update`, kind `decision`, key `writing-correction:<date>:<short-name>`. The record states the words before and after, the channel and audience, the date and the tool.

Writing in another person's voice is outside this skill.

## Set the register

Channels and audiences are not a fixed list. For each piece, write down the channel, who reads it, what they already know and what they must do. Those four answers set its length and structure. They also set how formal it is. Then read `registers.md` for an entry the owner has taught; a missing entry does not limit what you write. Pass the name to the check with `--register`. A name the check has not seen is accepted: the script adds it to `registers.md` with the date and the file, and the receipt says the name added no rules and lists the known names. When two entries fit, pass both with a comma, as in `client-facing,executive-page`.

## Run the check

```sh
python3 scripts/check.py --file PATH [--register NAME] --json
```

| Exit | Status | Meaning |
| --- | --- | --- |
| 0 | `pass` | Every in-scope line was scanned and no finding blocks |
| 1 | `fail` | `findings` lists each blocking line with its rule, the exact words and the fix |
| 2 | `incomplete` | The file could not be parsed, a rule could not run, or a part failed after two retries; `not_reviewed` names the lines |

The output carries `status`, `coverage` with `lines_total` and `lines_reviewed`, `findings`, `receipt` and `steps`. The script counts the lines each part scanned and compares them with the lines it extracted, so a gap returns `incomplete`. A file of any length is split into parts of at most 300 lines.

`review` counts the scanner flags that wait for a line-pass answer, such as a list of three; they do not block a scan.

Run with only `--file`, the check covers the scanner. `steps` then lists the line pass and document pass as `not_run`, and the reply calls the result a scan. Where the script cannot run, send the text to the Hub's scan tool. If neither is available, say the scan did not run.

Fix each finding by rewriting the sentence, then run the check again. Replacing a flagged word with a synonym leaves the same sentence in place.

## Review a file in full

A full review adds two passes to the scan. Each one writes a record that `check.py` validates.

### Choose the depth by reader

Run the full review on text read by people other than the owner: customers, clients, the public, a hiring team. Text only the owner reads, such as an admin page, an internal note or a status page for the owner, gets the scan alone unless the owner asks for the full review. Split a mixed piece by reader and give each part its own depth.

### Ask the owner first

Before the line pass, list what only the owner can settle: a fact no source supports, a policy, a price, a slogan or tagline, a brand claim. Ask those questions first, one at a time, in the form the owner prefers. Record each answer as a source, then start the line pass. A question that comes up later is a verdict with `owner_call: true`; it waits for the owner and does not go back to reviewers.

### Steps

1. List the documents the piece was written from in a JSON file of names, `SOURCES.json`. Run `check.py --file PATH --prepare REVIEW --sources SOURCES.json`. It writes the text in parts under `REVIEW/text/`, an outline and `REVIEW/assignments.json` with about 40 lines for each worker. Every `--prepare` run replaces those three outputs and writes its own receipt, marked `prepare`. It leaves the verdict, map and audit files alone.
2. Fix every scanner finding first.
3. Run the line pass in [line pass](references/line-pass.md). Give it to reviewers other than the writer, and send at least one worker group to a model from another family when the host has one. Each worker gets its lines, the full outline and the sources. It writes one verdict for every line and records whether a listed source supports each fact on it.
4. Run the document pass in [document pass](references/document-pass.md). One worker reads the whole text and fills the fixed map.
5. Validate both records with `check.py --file PATH --verdicts REVIEW/verdicts.json --document-map REVIEW/map.json --sources SOURCES.json --json`. The script rejects a line with no verdict, a quote that is not word for word in its line, a cited line ID that does not exist and a number the map does not trace.
6. Fix each finding at its source by locator, rebuild a generated file and run steps 1 to 5 again with `--round N`. Run `--prepare` with the last round's `--verdicts`: it writes `carried.json` with the verdicts that still stand and assigns only the lines that need one. Pass `--verdicts REVIEW/carried.json REVIEW/verdicts-w*.json` to validate the merged set. A verdict stops counting when its own line changed, or when `rules.md` or `patterns.json` changed; an edit to a neighbouring line leaves it standing. The document pass runs on the full text in every round.
7. Stop after round 2. From `--round 3` on, a fix marked `severity: style` is logged in the receipt and no longer blocks. Only errors block: a wrong or unsupported fact, a contradiction with another line, an instruction with no next step. Repeats, recaps and term choices in the map are logged the same way. Report the logged items once, as a list the owner can act on; do not loop on them.
8. Run the [spot audit](references/line-pass.md#spot-audit). The sample is one in five of the lines marked `ok`. A clean round passes only after it. A review that cannot edit the file never reaches a clean round, so it may audit the failed round, and the receipt then states what the audit covered. A miss is fixed on its own line, and its rule is swept across every line marked `ok` with `--recheck`, in place of a full line pass.
9. Log a miss the owner finds through Learn as a review miss.

With no workers available, one agent runs every step under one `reviewer` name, following the [single-reviewer steps](references/line-pass.md#one-reviewer).

A part or worker that fails is retried twice with half its lines. Lines still unreviewed after the retries make the result incomplete. List them in the reply and on the project's status page.

## Report

Read the receipt before reporting. State which steps ran and each step's status. List the owner decisions that wait (`owner_decisions`) and the logged style items (`logged`) apart from the blocking findings. A `failed` step makes the review incomplete. When the receipt records the audit as not independent, say so. Report line counts as coverage only.

In ordinary work, fix the wording and deliver it without describing the review. An AI-detector score is never a pass or a fail.

## Hooks

On Claude Code and Codex, `scripts/hook.py` scans every reply and every prose file a tool writes, and holds a reply for one rewrite when a finding blocks. It also holds a session while a deliverable it changed has no passing full review. `scripts/install_local.py` installs the scripts and the `/gate` command. With `--watch DIR` it adds a launchd agent that runs `scripts/gate_watch.py`, so each file that lands in DIR gets `/gate` through Claude Code headless. `scripts/writing_system.py` builds the copies of the owner's rules for other hosts and reports drift.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
