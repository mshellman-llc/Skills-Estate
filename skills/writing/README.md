# Writing

One entry point for writing and reviewing every word a person will read. It replaces `review-writing`, `writing-integrity` and `writing-diagnostics`. The rules stay in the owner's writing rules folder, whose README records the agreed design. This file records each decision made where that design gave no answer.

## Files

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Modes, register, the check and the full review |
| `scripts/check.py` | The check other tools call |
| `scripts/extract_review_text.py` | Text extraction for rendered and generated files |
| `scripts/rendered_read_guard.py` | PreToolUse hook that sends whole-file reads of large rendered files to the extractor |
| `references/file-review.md` | The extracted-text procedure for pages, workbooks, documents and decks |
| `references/line-pass.md` | Verdict record and its required questions |
| `references/document-pass.md` | The fixed map |
| `scripts/check_selftest.py` | 46 cases on synthetic files |

## The check

```sh
python3 scripts/check.py --file PATH [--register NAME] --json
```

Exit 0 is `pass` after a full review or `scan-pass` after a scan alone, 1 is `fail` and 2 is `incomplete`. The output has `status`, `coverage.lines_total`, `coverage.lines_reviewed`, `findings` and `receipt`. Each finding has `line`, `rule`, `text` and `fix`.

## Decisions

### Where the rules come from

1. The rules folder path is not written in this repository, because the estate's separation rule keeps workstation paths out of skills. `check.py` reads `--rules-dir`, then the `WRITING_HOME` variable, then the path in `~/.agents/writing/home`.
2. When the rules folder has no `patterns.json`, `check.py` reads the scanner's ledger in `~/.agents/humanize`, or in `HUMANIZE_HOME` when that variable is set. The receipt records which ledger ran. A run given `--rules-dir` uses that folder only. That folder gained its own `patterns.json` on 2026-11-11, so the fallback now covers only a machine where the folder is not mounted.
3. With no ledger in either place, the run returns `incomplete`. A rule whose pattern does not compile also returns `incomplete` and names the rule.

### What the check covers

4. Run with only `--file`, the check runs the scanner on every in-scope line. Its receipt lists the line pass, document pass and spot audit as `not_run`. Passing `--verdicts`, `--document-map`, `--audit` or `--full` makes both passes required, and a missing or rejected record returns `incomplete`. A full review also needs `rules.md` in the rules folder.
5. Formats read: Markdown, plain text, reStructuredText, files with no extension, git message files, JSON content files, HTML, SVG, JavaScript, `.xlsx`, `.docx` and `.pptx`. Any other format returns `incomplete`. A file over 50 MB returns `incomplete`.
6. Exempt lines: fenced code, HTML `pre`, `code`, `kbd`, `samp` and `var` text, Markdown blockquotes, HTML `blockquote` text, YAML front matter, HTML comments in Markdown, and git comment lines and trailers. Git handling applies to git message files and to any file checked with `--register commit`. A block that opens with `---` counts as front matter only when every line in it is shaped like YAML. Inside a line, inline code, link targets, web addresses, `q` text and text in double quotes up to 240 characters are masked before the scan. The 240-character limit matches the existing scanner.
7. A code fence that never closes returns `incomplete`, because the script cannot tell which later lines are prose.
8. A line with no letters or digits after masking is exempt. Coverage counts in-scope lines only, and the receipt lists exempt lines by reason.

### Findings

9. A ledger rule marked `"judge": "line-pass"` never blocks from the scan. Its hits are counted under `review`, listed in the receipt, and each one needs a `true` or `false` answer in that line's verdict. Lists of three use this mark, because a pattern cannot tell a true count from a padded one. For every other rule, blocking follows the ledger's own settings. A hit on an active rule at or above `hard_weight` blocks at any length. Lighter rules block when the text reaches `flag_density` or a rule repeats past `repeat_limit` and `repeat_density`, in a text of at least `min_words`. Other hits, and every candidate rule, are counted under `advisories` and listed in the receipt.
10. `line` is the source line when the locator is a line number. For workbooks, Word files and decks it is the extracted line number. Each finding also carries `id` and `loc`.
11. The output adds `steps`, `advisories`, `review`, `coverage.lines_exempt`, and on an incomplete run `reason` and `not_reviewed`. The four agreed keys are unchanged.
12. `--register` takes one name or several separated by commas, and adds ledger rules whose `scope` or `registers` list names it. Registers are not a fixed list, so a name the check has not seen is accepted. The script appends it to `registers.md` under "Names first seen by the check" with the date, the file and "No rules yet." The receipt says the name added no rules and lists the known names: the entries in `registers.md`, the ledger's scopes and `commit`. For a known name the receipt gives the count of rules it added.

### Coverage and failures

13. Each part of at most 300 lines returns the IDs it scanned and a digest of their text. The run recomputes the digest from the extraction and compares the IDs with the in-scope lines. Any difference returns `incomplete`.
14. A part gets 30 seconds. A part that fails or times out is split in half and retried, twice at most. Lines still unscanned are named in `not_reviewed`.
15. Receipts go to `~/.agents/writing/receipts`, or to `--receipt-dir` or `WRITING_RECEIPTS`. A run that cannot write its receipt returns `incomplete`. `--verify-receipt FILE` rechecks a receipt against the current file and ledger.

### Review records

16. A verdict is tied to its line by a hash of the line, a hash of the line's section and a hash of the rules. A change to any of the three makes the script reject the verdict, which implements the rule that a changed line sends its section back and a changed rule sends every line back.
17. The three line questions are required fields on every verdict: `portable`, `promise` and `tension`.
18. The document pass traces every number except dates, times, years from 1900 to 2099, version strings and list numbering. Numbers written as words are covered by the map's `counts` entry.
19. The spot audit sample is one in five of the lines marked `ok`, rounded up, chosen with the text hash as the seed so the same text gives the same sample.
20. The regression set holds the two failing lines the design quotes. The other lines from that session need its transcript, with client details removed, before they can be added.

### Changes after the first full review, 2026-11-11

A full review of one executive page listed 15 places where the skill was unclear. These decisions answer them.

24. The spot audit samples from every `ok` verdict in any round. A clean round returns `incomplete` until the audit has run. In a round that fails, the audit is optional and its step states how many `ok` lines it covered.
25. The verdict file and the audit file each carry `reviewer`. The receipt records the audit as not independent when either name is missing or the two match.
26. A `--prepare` run is a scan plus the working files. Its receipt carries `"purpose": "prepare"`. `--prepare` with `--verdicts` alone only adds the audit sample.
27. A number after a label word such as phase, step, table or section is a label, and the map owes it no source.
28. A number written as a word, from two upward, needs a `numbers` entry or a `counts` entry on its line. "One" is left out because it is too common as a pronoun.
29. The claims check is its own step. Each verdict carries `claims`, and a `supported` claim names a source from the `--sources` list. A full review with no source list returns `incomplete`.
30. The map's `confidentiality` entry needs `retrieved: true`, or `none_applies` with a reason. A list rebuilt from other documents returns `incomplete`. The list is read from the owner's current Hub on the local machine; the older Hub behind the claude.ai connector does not hold it.
31. A section marked `"role": "title"` needs no `reader_acts`. It may hold a heading and two lines.
32. `structural_repeat` declares a deliberate repeat between named sections once. Entries marked `structural` inside it do not block.
33. A document finding joins the line fix on the same line and is counted once. This is automatic for five single-line rules, and by `merged_with` for repeats, terms and counts.
34. A scanner flag answer and a fix are independent: `false` on the flag with a fix for another rule is valid.
35. How `portable` and the verbless-sentence limit apply to headings, tiles and labels, and the order of the estimate rule and the source rule, are stated in the owner's `rules.md`. `references/line-pass.md` gives the method.

### Scope of this skill

21. The skill is named `writing`, as the design states. The estate naming policy prefers an action and a subject.
22. Learn saves corrections through the Hub. The profile store in `review-writing/scripts/learning.py` is not carried over.
23. `extract_review_text.py` is copied from `review-writing` with one change: it marks code with backticks and blockquotes with a leading `>` so the check can exempt them.

### One writing skill, 2026-11-19

The owner confirmed on 2026-11-19 that the estate keeps one writing skill.

36. `review-writing` is folded into this skill and removed. `extract_review_text.py` was already here; `rendered_read_guard.py`, its selftest and the extracted-text procedure (`references/file-review.md`) moved here. Its rule text (`references/patterns.md`, `expanded-writing-review.md`, `context-rules.md`, `detailed-review.md`, `examples.md`), its profile store (`learning.py`, `build_kit.py`, `review_selftest.py`, the setup kit) and their selftests are removed. Rule text now lives only in the owner's folder. Corrections go to `corrections.md` or the Hub.
37. Every skill that cited `review-writing` now cites `writing`. The writing router lists `writing` as its one prose review. `config/required-runtimes.json` bundles `writing` in every package in place of `review-writing`, and `writing-diagnostics` stays retired with `writing` as its successor.
38. The description carries the names the owner uses for this work, "writing integrity", "prose pass", "de-AI" and "humanize", so each one selects the skill.
39. A scan alone returns `scan-pass`. Only a full review returns `pass`, which keeps a reply from reporting a scan as a passed review. `--verify-receipt` rejects a `pass` receipt with no line pass. Exit 0 covers both statuses so existing callers keep working.
40. Each verdict carries `first_words` and `last_words`, the first and last three words of its own line, compared with the extracted text after spacing is normalised. The line hash already ties a verdict to its line; the words show that the reviewer read it. The recheck file carries them too.
41. A verdict set is rejected when its reviewer is the writer. The writers are every session `hook.py` logged writing or changing the piece in `writers.jsonl`, up to the last write that left the file at the content under review, plus every name passed with `--writer`. The hook records the file's sha256 after each write; when no logged write matches the current content, every logged write counts. The reviewer is the `reviewer` names, the optional `session` field and every session the hook logged writing the verdict file. A set with no `reviewer` is rejected. The hook sees only files written with a file tool; for a piece a script or shell command generated, pass `--writer`. A session that applies review fixes is a writer of the text it changed, so it cannot review that text. The same rule covers the audit and recheck files.
42. A map that marks more than one in-scope line in ten as a structural repeat is rejected. The brief put this limit on the verdict set. Structural repeats are declared in the document map, which is where the check reads them.
43. On a surface where `check.py` cannot run, the skill reads the text against the rules files and says the scan did not run. The earlier text named a Hub scan tool that does not exist (Hub decision 271).
