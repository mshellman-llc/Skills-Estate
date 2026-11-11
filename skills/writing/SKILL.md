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

On a surface with no file access, get the current rules from the Knowledge Hub with `get_context`. If `rules.md` cannot be read from either place, report the review as incomplete and name the missing file. Do not review from a remembered copy.

When two rules disagree, the newer one applies. The owner's correction in the current conversation outranks every file.

## Scope

The check and both passes cover text in every format: chat replies, documents, pages, decks and speaker notes, headings, bullets, table cells, captions, chart titles and labels, interface text, file names, status pages, emails, chat messages, texts, posts, bios, commit messages, pull request descriptions and résumé lines. An outline, a set of headline options and a draft pasted into chat are in scope before the owner sees them.

Code and code comments are exempt. So are quotations kept word for word. A label or message string inside code is in scope. For a rendered or generated file, review the text extracted from the output.

## Choose the mode

1. Review is the default. Apply `rules.md` and `patterns.json` to the text.
2. Write as the owner when the piece goes out under the owner's name. Add `voice-profile.md`.
3. Write as a brand for a piece published under that brand. Add `brands/<brand>.md`. Use a brand voice only when its file exists; if the file is missing, ask which voice applies.
4. Learn when the owner corrects wording. Apply the fix to every affected passage. Then save it through the Hub with `save_update`, kind `writing-correction`. The saved record states what changed, for which channel and audience, on which date and in which tool.

Writing in another person's voice is outside this skill.

## Set the register

Channels and audiences are not a fixed list. For each piece, write down the channel, who reads it, what they already know and what they must do. Those four answers set its length and structure. They also set how formal it is. Then read `registers.md` for an entry the owner has taught; a missing entry does not limit what you write. Pass the channel or author name to the check with `--register`.

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

1. Run `check.py --file PATH --prepare REVIEW`. It writes the text in parts under `REVIEW/text/`, an outline and `REVIEW/assignments.json` with about 40 lines for each worker.
2. Fix every scanner finding first.
3. Run the line pass in [line pass](references/line-pass.md). Each worker gets its lines and the full outline, and writes one verdict for every line.
4. Run the document pass in [document pass](references/document-pass.md). One worker reads the whole text and fills the fixed map.
5. Validate both records with `check.py --file PATH --verdicts REVIEW/verdicts.json --document-map REVIEW/map.json --json`. The script rejects a line with no verdict, a quote that is not word for word in its line, a cited line ID that does not exist and a number the map does not trace.
6. Fix each finding at its source by locator, rebuild a generated file and run steps 1 to 5 again. A verdict stops counting when its line changed, when another line in its section changed, or when `rules.md` or `patterns.json` changed. The document pass runs on the full text in every round.
7. After a clean round, run `--prepare` again with `--verdicts`. `assignments.json` then lists an `audit` sample of one line in five. A separate worker reviews those lines without seeing the first verdicts, and `--audit FILE` validates them. One audited line marked `fix` sends every line back through the line pass.
8. Log a miss the owner finds through Learn as a review miss.

A part or worker that fails is retried twice with half its lines. Lines still unreviewed after the retries make the result incomplete. List them in the reply and on the project's status page.

## Report

Read the receipt before reporting. State which steps ran and each step's status. A `failed` step makes the review incomplete. A clean round is final only after the spot audit has run. Report line counts as coverage only.

In ordinary work, fix the wording and deliver it without describing the review.
