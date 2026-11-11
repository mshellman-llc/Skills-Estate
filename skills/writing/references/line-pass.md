# Line pass

The line pass gives every in-scope line a written verdict. `check.py` rejects a record that covers only the lines a worker flagged.

## What each worker receives

`assignments.json` lists the workers. Each worker gets about 40 `lines` and the whole of `outline.md`. The outline holds every heading and each section's first line, and a worker uses it to judge a line against the piece it belongs to. Give each worker the current `rules.md` and the register for the piece.

## What each worker asks

Judge each line against every rule in `rules.md`. Then answer three questions about it and record each answer as `true` or `false`.

| Field | Question |
| --- | --- |
| `portable` | Would this sentence fit unchanged in a piece about another company or subject? |
| `promise` | Does it promise a benefit where a fact or a mechanism belongs? |
| `tension` | Is it a heading that sets up a tension where a statement belongs? |

A `true` answer requires the verdict `fix`. The script rejects `ok` beside a `true`.

## Verdict record

Copy `id`, `sha` and `section` from the assignment. They tie the verdict to the exact line and section the worker read.

```json
{
  "rules_sha256": "copied from assignments.json",
  "verdicts": [
    {"id": "0002", "sha": "5f0c1d2a9b7e", "section": "c41d88aa02f3", "verdict": "ok",
     "portable": false, "promise": false, "tension": false},
    {"id": "0003", "sha": "91ab4470c2de", "section": "c41d88aa02f3", "verdict": "fix",
     "tension": false, "promise": false, "portable": true,
     "rule": "rule 3: fits any team",
     "quote": "moves faster with better tooling",
     "replacement": "closes a ticket in two days since the March queue change"}
  ]
}
```

A `fix` names the rule, quotes the exact words from the line and gives the replacement. An empty replacement means the words are cut. Take every fact in a replacement from the sources for the piece; the replacement in this example assumes the source gives the two days and the March change.

Several workers can write to separate files. Merge their `verdicts` lists into one file before running the check.

## Lines the scanner passes

No scanner pattern matches these two lines, which came from a review that failed. The line pass must mark both.

| Line | Answer | Repair |
| --- | --- | --- |
| The company is adding products faster than its systems were built for. | `portable` is true: the sentence fits any growing company | Name the products, the system and the limit it reached |
| Revenue risk shows up while there is time to act. | `promise` is true: it promises a benefit | State which report shows which figure, and the number of days before the renewal date |

## Later rounds

A changed line has a new `sha`, and every line in its section has a new `section` value. The script rejects the old verdicts for those lines, and `--prepare` lists them again. A change to `rules.md` or `patterns.json` changes `rules_sha256` and sends every line back. The owner can ask for a full pass at any time; delete the verdict file to start one.
