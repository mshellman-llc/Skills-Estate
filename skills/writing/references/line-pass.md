# Line pass

The line pass gives every in-scope line a written verdict. `check.py` rejects a record that covers only the lines a worker flagged.

## What each worker receives

`assignments.json` lists the workers. Each worker gets about 40 `lines` and the whole of `outline.md`. The outline holds every heading and each section's first line, and a worker uses it to judge a line against the piece it belongs to. Give each worker the current `rules.md`, the register for the piece and the documents named under `sources`.

## What each worker asks

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

Copy `id`, `sha` and `section` from the assignment. They tie the verdict to the exact line and section the worker read. Put the reviewer's name at the top of the file.

```json
{
  "rules_sha256": "copied from assignments.json",
  "reviewer": "line-pass worker 2",
  "verdicts": [
    {"id": "0002", "sha": "5f0c1d2a9b7e", "section": "c41d88aa02f3", "verdict": "ok",
     "portable": false, "promise": false, "tension": false,
     "claims": "supported", "source": "Support queue export, March",
     "flags": {"triad": false}},
    {"id": "0003", "sha": "91ab4470c2de", "section": "c41d88aa02f3", "verdict": "fix",
     "tension": false, "promise": false, "portable": true, "claims": "none",
     "rule": "R6: fits any team",
     "quote": "moves faster with better tooling",
     "replacement": "closes a ticket in two days since the March queue change"}
  ]
}
```

A `fix` names the rule, quotes the exact words from the line and gives the replacement. An empty replacement means the words are cut. Take every fact in a replacement from the listed sources.

Several workers can write to separate files. Merge their `verdicts` lists into one file before running the check.

## Lines the scanner passes

No scanner pattern matches these two lines, which came from a review that failed. The line pass must mark both.

| Line | Answer | Repair |
| --- | --- | --- |
| The company is adding products faster than its systems were built for. | `portable` is true: the sentence fits any growing company | Name the products, the system and the limit it reached |
| Revenue risk shows up while there is time to act. | `promise` is true: it promises a benefit | State which report shows which figure, and the number of days before the renewal date |

## Spot audit

Run `--prepare` again with `--verdicts`. `assignments.json` then carries `audit`: one in five of the lines marked `ok`, rounded up. The sample is drawn the same way in a clean round and in a failed one.

The audit file has the same format as the verdict file and holds one verdict for each sampled line, written without sight of the first verdicts. Its `reviewer` names who audited.

```json
{"rules_sha256": "the value in assignments.json", "reviewer": "audit worker",
 "verdicts": [{"id": "0007", "sha": "0be2c1d9a4f3", "section": "77aa01c3e2b9", "verdict": "ok",
               "promise": false, "portable": false, "tension": false, "claims": "none"}]}
```

Pass it with `--audit FILE`. A clean round passes only after the audit. In a round that already fails, the audit is optional; when it runs, the receipt states how many of the `ok` lines it covered and that the round still fails. One audited line marked `fix` sends every line back through the line pass.

## One reviewer

One agent can run the whole review when no workers are available. It takes the worker groups in order and reads `outline.md` before each group. It writes the map after the last group, then audits its own sample. It puts the same name in `reviewer` in both files. The receipt then records the audit as not independent, and the reply says so.

## Later rounds

A changed line has a new `sha`, and every line in its section has a new `section` value. The script rejects the old verdicts for those lines, and `--prepare` lists them again. A change to `rules.md` or `patterns.json` changes `rules_sha256` and sends every line back. The owner can ask for a full pass at any time; delete the verdict file to start one.
