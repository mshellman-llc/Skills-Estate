# Candidate file and scorer behavior

`scripts/priority_score.py` reads one JSON file of candidates and writes a ranked report.

## Shape of the file

The top level is either an array of items or an object holding an `items` array. Weighted scoring also needs a `criteria` array in that object. Other top-level keys are ignored, so a file can carry a description of its own data.

A one-item RICE file, with synthetic values:

```json
[
  {
    "id": "BKG-014",
    "title": "Saved traveler profiles",
    "problem": "Repeat customers retype passenger details on every booking",
    "reach": 1800,
    "impact": 1,
    "confidence": 0.8,
    "effort": 3,
    "sources": {
      "confidence": "usability study, 12 sessions (synthetic)",
      "effort": "engineering sizing meeting (synthetic)"
    }
  }
]
```

## Item keys

| Key | Required | Meaning |
| --- | --- | --- |
| `id` | Yes | A non-empty string or a number that traces back to its record, unique within the file |
| Method fields | Yes | Listed in the next table |
| `sources` | No | An object saying where values came from; the scorer reads only its `confidence`, `effort` and `importance` keys, and further keys such as `reach` can record other sources for the provenance audit |
| `job`, `problem` | No | What the item serves; an item with neither is flagged |
| `title` | No | Display text for the report |

Good ids are Requirement Numbers such as `ABC-012`, epic prefixes, job IDs and roadmap card IDs. True and false never count as ids. Ids are compared as text, so `7` and `"7"` are the same id. When two items share an id, only the first can be scored and every later one is rejected.

A required field that is absent or `null` counts as missing. Numeric fields take JSON numbers or plain numeric strings such as `"12"` and `"0.8"`. Booleans, text like `"80%"` or `"high"`, and non-finite values are rejected.

| `--framework` | Required fields |
| --- | --- |
| `ice` | `impact` and `ease`, each 1-10; `confidence` as a fraction or a percent |
| `odi` | `importance` and `satisfaction`, both customer ratings on 0-10 |
| `opportunity` | `importance` on 0-10; `satisfaction` on 0-1, where a value above 1 is read as a 0-10 rating, converted and flagged |
| `rice` | `reach` per stated period; `impact` of 0.25, 0.5, 1, 2 or 3; `confidence` in the same form as for `ice`; `effort` above 0 |
| `weighted` | `scores`, an object giving a number for each criterion name |
| `wsjf` | `business_value`, `time_criticality`, `risk_reduction` and a `job_size` above 0 |

A source counts as present when its `sources` entry holds non-blank text, directly or inside a list or object. The scorer cannot judge whether a source is genuine; the session lead checks that.

## Weighted criteria

`criteria` is a non-empty array of objects, each with a `name` (a non-empty string used by no other criterion) and a `weight` (a number of 0 or more). The weights must add up to more than 0. If their total misses 1 by more than 0.01, the scorer divides every weight by the total and records a note. A missing or empty `criteria` array, a malformed criterion or a zero total stops the run with exit code 2. Other methods ignore `criteria`.

## Rejected items

The scorer rejects an item, lists it under errors and carries on with the rest when:

- the item is not a JSON object (for example a bare string, number or array);
- its `id` is absent, empty or of the wrong type, or repeats an earlier id;
- a required field is missing; one message names all of them, and for weighted scoring that includes `scores` itself and each criterion absent from it;
- a required value is not numeric;
- `sources` or `scores` is present but not an object;
- `effort` (RICE) or `job_size` (WSJF) is 0 or less.

Each message begins with the item's id. When the id is unusable, the title or the item's position in the list takes its place. A run with any rejection exits 1.

## Adjustments and flags

These items are still scored, with a value adjusted or a flag attached:

| Condition | Result |
| --- | --- |
| `confidence` (ice, rice) above 1 | Read as a percent and divided by 100 |
| `confidence` above 1 and no higher than 10 | An extra flag: the value was probably a 0-10 rating, which belongs in the file as a fraction |
| `confidence` above 0.5 with an empty `sources.confidence` | Scored as 0.5; the flag quotes the value as entered |
| RICE `effort` or WSJF `job_size` with an empty `sources.effort` | Flagged as not sized by engineering; do not publish the ranking yet |
| RICE `impact` that is not one of the allowed scale values | Flagged |
| Opportunity Score `satisfaction` above 1 | Divided by 10 and flagged as converted |
| ODI or Opportunity Score `importance` with an empty `sources.importance` | Flagged as a hypothesis resting on internal estimates |
| Neither `job` nor `problem` | Flagged with a pointer to rank the problem first through `frame-jobs-to-be-done` |

## Run notes

- A weighted run whose weights were rescaled gets a note giving the original total.
- An ICE or RICE run with four or more scored items gets a note when more than 30% of them share the highest impact value, asking the team to recalibrate. Rejected items never count toward that share.
- Scored items that share a rounded score produce a note that lists every tie. The formula never breaks a tie; the decision meeting settles it with a named rule.

## Ordering and arithmetic

Scores are rounded to two decimal places and sorted from highest to lowest. Equal scores keep their order from the file. Ranks are consecutive, starting at 1, with no gaps even where scores tie. Each row's `formula` writes out the arithmetic with the numbers actually used, after any conversion or cap, for example `(2400 * 2 * 0.8) / 6 = 640`. Numbers in a formula drop trailing zeros and show at most six decimal places.

## Report formats

The Markdown report, which is the default, opens with a title naming the method and one sentence saying the ranking is a proposal whose final order the decision owner sets, while MoSCoW stays with `capture-requirements`. A table follows with rank, ID, title, score, formula and flags, showing "none" when an item has no flags. Notes come next, then the rejected items. When nothing could be scored, the report says so and leaves the table out.

With `--format json` the report is an object with exactly four keys: `framework`, `ranking`, `errors` and `notes`. Each ranking row has exactly `id`, `title` (empty when absent), `job` (the job, otherwise the problem, otherwise empty), `score`, `formula`, `flags` and `rank`.

`--output PATH` writes the report to that file instead of standard output and prints a one-line confirmation on stderr.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Every item was scored; flags and notes may still be present |
| 1 | The report was produced and at least one item was rejected |
| 2 | No usable report: the file was unreadable, invalid JSON, the wrong shape or empty; the weighted criteria were invalid; or the `--output` path could not be written. A message beginning `error:` goes to stderr and no report appears |

A command-line usage error, such as a missing `--framework`, also exits 2.
