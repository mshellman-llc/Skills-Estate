# Writing

One entry point for writing and reviewing every word a person will read. It replaces `review-writing`, `writing-integrity` and `writing-diagnostics`. The rules stay in the owner's writing rules folder, whose README records the agreed design. This file records each decision made where that design gave no answer.

## Files

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Modes, register, the check and the full review |
| `scripts/check.py` | The check other tools call |
| `scripts/extract_review_text.py` | Text extraction for rendered and generated files |
| `references/line-pass.md` | Verdict record and its required questions |
| `references/document-pass.md` | The fixed map |
| `scripts/check_selftest.py` | 37 cases on synthetic files |

## The check

```sh
python3 scripts/check.py --file PATH [--register NAME] --json
```

Exit 0 is `pass`, 1 is `fail` and 2 is `incomplete`. The output has `status`, `coverage.lines_total`, `coverage.lines_reviewed`, `findings` and `receipt`. Each finding has `line`, `rule`, `text` and `fix`.

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
12. `--register` takes one name or several separated by commas, and adds ledger rules whose `scope` or `registers` list names it. The valid names are the entries in `registers.md`, the ledger's scopes and `commit`. An unknown name returns `incomplete` with that list. The design says registers are not a fixed list; a channel with no entry is checked with no `--register`. The receipt gives the count of rules each name added.

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
30. The map's `confidentiality` entry needs `retrieved: true`, or `none_applies` with a reason. A list rebuilt from other documents returns `incomplete`.
31. A section marked `"role": "title"` needs no `reader_acts`. It may hold a heading and two lines.
32. `structural_repeat` declares a deliberate repeat between named sections once. Entries marked `structural` inside it do not block.
33. A document finding joins the line fix on the same line and is counted once. This is automatic for five single-line rules, and by `merged_with` for repeats, terms and counts.
34. A scanner flag answer and a fix are independent: `false` on the flag with a fix for another rule is valid.
35. How `portable` and the verbless-sentence limit apply to headings, tiles and labels, and the order of the estimate rule and the source rule, are stated in the owner's `rules.md`. `references/line-pass.md` gives the method.

### Scope of this skill

21. The skill is named `writing`, as the design states. The estate naming policy prefers an action and a subject.
22. Learn saves corrections through the Hub. The profile store in `review-writing/scripts/learning.py` is not carried over.
23. `extract_review_text.py` is copied from `review-writing` with one change: it marks code with backticks and blockquotes with a leading `>` so the check can exempt them.

## Retirement

This change adds the skill and removes nothing. Retirement follows the three proof runs and has these steps:

- Remove the 21 files of `skills/review-writing/`, with its entries in the catalog, groups, guide, bundles, publication record and writing router.
- Remove the 32 files of `skills/writing-diagnostics/`. Its `writing_check.py` is called by `tools/writing_gate.py`, `tools/verify.py`, `config/required-runtimes.json` and eight test modules, and `brand-renderer` and `review-deliverable` load the skill as a runtime. Each caller needs a new target first.
- Remove the 8 files of `skills/manage-writing-profile/` once `author-style-runtime` and `apply-author-style` stop loading that skill.
- Remove `docs/writing-integrity-shared-rules.md` and the `writing-integrity` mentions in 8 source files.
- Replace `policies/writing.md`, a second copy of the rules, with a pointer to that folder.
- Update the references elsewhere in the source: 89 files name `review-writing`, 78 name `writing-diagnostics` and 15 name `manage-writing-profile`.
- Rebuild `plugins/` and `dist/` so the generated copies go, and delete the `.writing-receipts/` entries for the removed files.
- Outside this repository, delete the `writing-integrity` copies in the Claude Code and Codex skill trash and synced folders, the owner's voice account skill, and the old skill names in the generated instruction files.
