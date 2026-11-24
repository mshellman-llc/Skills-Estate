# Line pass

The line pass gives every in-scope line a written verdict. `check.py` rejects a record that covers only the lines the reviewer flagged.

## What the reviewer receives

`assignments.json` has one assignment for one independent reviewer. That reviewer reads the bounded text parts in order, with `outline.md`, the current `rules.md`, the register and the documents named under `sources`. The text parts never authorize more reviewers.

## What the reviewer asks

Judge each line against every rule in `rules.md`. Then answer three questions about it and record each answer as `true` or `false`.

| Field | Question |
| --- | --- |
| `portable` | Would this sentence fit unchanged in a piece about another company or subject? |
| `promise` | Does it promise a benefit where a fact or a mechanism belongs? |
| `tension` | Is it a heading that sets up a tension where a statement belongs? |

A `true` answer requires the verdict `fix`. The script rejects `ok` beside a `true`.

## Headings, tiles and labels

A heading, a tile title, a table header and a short label are judged with the content they name. Read the label and the line under it as one unit before answering `portable`. "Outcome" above a paragraph that states this project's result is `false`. A heading whose section would read the same for another client is `true`. The limit on verbless sentences covers sentences in running text; a label or a list item that is a noun phrase is outside it.

## Claims

Each verdict also records whether the line states a fact and where that fact comes from.

| `claims` | Meaning | Also required |
| --- | --- | --- |
| `none` | The line states no fact: a heading, a label, an instruction | Nothing |
| `supported` | A listed source states each fact the line carries | `source`, copied from `sources` |
| `unsupported` | A fact on the line is in none of the listed sources, or a source contradicts it | The verdict `fix` |

Read the source before answering. A line that matches an earlier draft is unchecked until a source confirms it. `check.py --sources FILE` takes the source list as a JSON list of names, and `--prepare` copies it into `assignments.json`. A full review with no source list is incomplete.

## Scanner flags

Some ledger rules carry `"judge": "line-pass"`. They match a shape a pattern cannot rule on, such as a list of three, which is correct when the source has three things. The scan never blocks on these rules. Each hit appears in the line's `flags` in `assignments.json`, and the verdict for that line must answer it.

Answer `false` when the flagged words are right as written: the three items are distinct and all come from the source. Answer `true` when the flag found a fault, and mark the line `fix`. A flagged line with no answer is rejected.

The flag answer and the fix are separate. A line can answer its flag `false` and still be marked `fix` for another rule, and that fix names the other rule.

## Verdict record

Copy `id`, `sha` and `section` from the assignment. They tie the verdict to the exact line and section the reviewer read. Copy the line's first three words into `first_words` and its last three into `last_words`, from the text you read; a line of three words or fewer gives the whole line in both. The script rejects a verdict whose words are not its own line's. Put the reviewer's name at the top of the file, and the reviewer's session ID in `session` when the host shows one. A verdict set whose reviewer or session is the piece's writer is rejected.

```json
{
  "rules_sha256": "copied from assignments.json",
  "reviewer": "external reviewer",
  "verdicts": [
    {"id": "0002", "sha": "5f0c1d2a9b7e", "section": "c41d88aa02f3", "verdict": "ok",
     "first_words": "Each ticket closes", "last_words": "the March queue",
     "portable": false, "promise": false, "tension": false,
     "claims": "supported", "source": "Support queue export, March",
     "flags": {"triad": false}},
    {"id": "0003", "sha": "91ab4470c2de", "section": "c41d88aa02f3", "verdict": "fix",
     "first_words": "The support team", "last_words": "with better tooling",
     "tension": false, "promise": false, "portable": true, "claims": "none",
     "rule": "R6: fits any team",
     "quote": "moves faster with better tooling",
     "replacement": "closes a ticket in two days since the March queue change"}
  ]
}
```

A `fix` names the rule, quotes the exact words from the line and gives the replacement. An empty replacement means the words are cut. Take every fact in a replacement from the listed sources.

Two more fields go on a `fix`:

| Field | Value | Meaning |
| --- | --- | --- |
| `severity` | `error` | The line states something wrong or unsupported, contradicts another line, or leaves the reader with no next step. The default |
| `severity` | `style` | Wording, rhythm, a repeat or a term choice. Blocks in round 1, logged in the final round 2 |
| `owner_call` | `true` | Only the owner can settle it: an unsourced fact, a policy, a price, a slogan. Blocks until the owner answers, and goes to the owner instead of back to reviewers |

The same reviewer can write separate files for bounded parts. Pass them all to `--verdicts`, with `carried.json` from `--prepare`; the script merges them.

## Lines the scanner passes

No scanner pattern matches these two lines, which came from a review that failed. The line pass must mark both.

| Line | Answer | Repair |
| --- | --- | --- |
| The company is adding products faster than its systems were built for. | `portable` is true: the sentence fits any growing company | Name the products, the system and the limit it reached |
| Revenue risk shows up while there is time to act. | `promise` is true: it promises a benefit | State which report shows which figure, and the number of days before the renewal date |

## Spot audit

Run `--prepare` again with `--verdicts`. `assignments.json` then carries `audit`: one in five of the lines marked `ok`, rounded up. The sample is drawn the same way in a clean round and in a failed one.

The audit file has the same format as the verdict file and holds one verdict for each sampled line, written by the same independent reviewer without sight of its first verdicts. Keep the same `reviewer` and `session` identity. Do not launch an auditor.

```json
{"rules_sha256": "the value in assignments.json", "reviewer": "external reviewer",
 "verdicts": [{"id": "0007", "sha": "0be2c1d9a4f3", "section": "77aa01c3e2b9", "verdict": "ok",
               "first_words": "Renewals start in", "last_words": "before the call",
               "promise": false, "portable": false, "tension": false, "claims": "none"}]}
```

Pass it with `--audit FILE`. A clean round passes only after the audit. In a round that already fails, the audit is optional; when it runs, the receipt states how many of the `ok` lines it covered and that the round still fails.

An audited line marked `fix` is fixed on that line. Its rule is then swept across every line the line pass marked `ok`: the same reviewer reads those lines for that rule alone and writes a recheck file, passed with `--recheck FILE`. The file names the swept rules and lists a verdict for each line marked `ok`.

```json
{"rules_sha256": "same as the audit file", "reviewer": "external reviewer", "rules": ["R6"],
 "verdicts": [{"id": "0012", "sha": "7d2a90c1e4b8", "verdict": "ok",
               "first_words": "Orders ship from", "last_words": "the Atlanta shop"},
              {"id": "0019", "sha": "4c1e0d2b9f3a", "verdict": "fix", "rule": "R6: any shop could say it",
               "first_words": "Every sticker is", "last_words": "made with love",
               "quote": "made with love", "replacement": "cut on a Cricut"}]}
```

The audit step passes when the recheck sweeps every missed rule and covers every line marked `ok`. Its fixes join the round's findings.

## Reviewer and round limits

One independent reviewer runs every pass in the same session. The writer applies fixes and never writes its own verdicts. Keep accepted verdicts with their original reviewer and session when preparing changed lines. The document map and spot audit name that same reviewer.

Use at most two rounds. Resume the original reviewer once after source corrections; never replace it or start another model. The policy state counts rounds across review directories. From round 2, style findings are logged. Errors and owner decisions still block publication. At the limit, report the remaining findings and stop. A technical failure does not create an extra reviewer or reset the budget.
