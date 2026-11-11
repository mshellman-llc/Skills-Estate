# Document pass

One worker reads the whole extracted text and fills a fixed map. The text holds words only, so a page of several hundred lines fits in one read. The pass runs on the full text in every round, because repeats, recaps and drifting terms cannot be judged from one part.

## Start with the reader

Write down who reads the piece and what they must decide or do. Check every section against that answer. A section the reader would not act on is a finding.

## Fetch the confidentiality list first

Each client project keeps a confidentiality list in the Knowledge Hub under the fact key `confidential.exec-copy`. Ask the Hub for that key in the project before reading the text. When the Hub returns it, set `retrieved` to `true` and name the fact in `list`.

When the Hub does not return it, stop. Report the review as incomplete and say the list could not be fetched. A list rebuilt from a memo or a brief is a guess, and the script rejects a map whose `retrieved` is not `true`. A piece that belongs to no client project records `none_applies` with the reason in place of `list` and `retrieved`.

## The map

Every key in this example is required except `structural_repeat`. An empty list means the worker looked and found none.

```json
{
  "text_sha256": "copied from assignments.json",
  "rules_sha256": "taken from the same file",
  "reader": {"who": "The finance lead for renewals",
             "must_decide_or_do": "Approve the forecast for 14 accounts"},
  "sections": [{"id": "0001", "point": "Names the page and its period", "role": "title"},
               {"id": "0003", "point": "States which accounts the forecast covers", "reader_acts": true}],
  "headings": [{"id": "0001", "matches": true}],
  "structural_repeat": {"reason": "Each capability returns as a roadmap item",
                        "sections": ["0003", "0020"]},
  "repeated_facts": [{"ids": ["0004", "0022"], "quote": "monthly forecast by product", "structural": true},
                     {"ids": ["0002", "0009"], "quote": "14 accounts"}],
  "counts": [{"id": "0006", "quote": "three reports", "stated": 3, "listed": 2}],
  "recaps": [{"id": "0011"}],
  "terms": [{"terms": ["forecast", "projection"], "ids": ["0002", "0007"]}],
  "leftover_lines": [{"id": "0012"}],
  "numbers": [{"id": "0002", "quote": "14", "source": "Renewal register, November export"},
              {"id": "0015", "quote": "six years", "source": "Service desk history, 2020 entry"}],
  "confidentiality": {"list": "Hub fact confidential.exec-copy", "retrieved": true, "hits": []},
  "provenance": [{"id": "0013", "quote": "per the October call"}]
}
```

| Key | What to record | What blocks |
| --- | --- | --- |
| `sections` | One entry for each section in `assignments.json`, with its point | `reader_acts` is false |
| `headings` | One entry for each heading | `matches` is false |
| `repeated_facts` | Each fact stated more than once, with its line IDs | Every entry not marked `structural` |
| `counts` | Each stated count beside the number of items listed | The two numbers differ |
| `recaps` | Lines that recap another section | Every entry |
| `terms` | Two or more terms used for one thing | Every entry |
| `leftover_lines` | Lines that exist only because of an earlier AI mistake | Every entry |
| `numbers` | Each number in `assignments.json`, with a named source or the ID of the line that states it is an assumption | No source and no `assumption_id` |
| `confidentiality` | The list that was fetched, and each line it covers | Every hit |
| `provenance` | Meeting references, source lists and evidence notes in finished copy | Every entry |

The script checks that every cited line ID exists, every quote is word for word in its line, every section and heading has an entry and every number has one. A number missing from the map leaves the pass incomplete.

## Title sections

A title section is a heading with at most two lines under it, such as a page title and its kicker. Give it `"role": "title"` and its point. It needs no `reader_acts` answer.

## Numbers

`assignments.json` lists the numbers the script found. Dates, times, years, version strings and list numbering are left out. A number that names a thing, such as Phase 2 or Table 4, is a label and is left out too.

A number written as a word, from two upward, is listed with `"kind": "word"`. Give it a `numbers` entry with its source when it states a fact about the world: "four separate projects." Give it a `counts` entry when it counts items the piece itself lists: "three phases."

## Repeats that are the structure

Some pieces state a thing twice on purpose, such as each capability and then the roadmap item that delivers it. Declare that once in `structural_repeat`, with a reason of five or more words and the first line ID of each section involved. A `repeated_facts` entry marked `"structural": true` then does not block, provided its lines sit in two or more of the declared sections. The receipt lists the declared repeats. Any other repeat still blocks.

`assignments.json` also carries `repeats`: identical sentences and figures the script found in more than one section. Check each one and record the real repeats under `repeated_facts`.

## One fault, one finding

The line pass and the document pass can both catch the same fault. The script counts it once and shows the document finding under `also` on the line fix. It does this without help for a heading that does not match, a recap, a leftover line, provenance and a section with `reader_acts` false, when the same line has a line fix. For a `repeated_facts`, `terms` or `counts` entry, add `"merged_with": "0042"`, naming the line whose fix covers the same fault.

## Documents over 2,000 lines

`assignments.json` sets `two_step_document_pass` to true. Section workers each list their section's point, facts with figures, counts, terms and headings, with line IDs. One worker then compares those lists across sections for repeats, recaps, conflicting figures and drifting terms, and writes the single map.
