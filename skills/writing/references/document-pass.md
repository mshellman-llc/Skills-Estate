# Document pass

One worker reads the whole extracted text and fills a fixed map. The text holds words only, so a page of several hundred lines fits in one read. The pass runs on the full text in every round, because repeats, recaps and drifting terms cannot be judged from one part.

## Start with the reader

Write down who reads the piece and what they must decide or do. Check every section against that answer. A section the reader would not act on is a finding.

## The map

Every key is required. An empty list means the worker looked and found none.

```json
{
  "text_sha256": "copied from assignments.json",
  "rules_sha256": "taken from the same file",
  "reader": {"who": "The finance lead for renewals",
             "must_decide_or_do": "Approve the forecast for 14 accounts"},
  "sections": [{"id": "0001", "point": "States which accounts the forecast covers", "reader_acts": true}],
  "headings": [{"id": "0001", "matches": true}],
  "repeated_facts": [{"ids": ["0002", "0009"], "quote": "14 accounts"}],
  "counts": [{"id": "0006", "quote": "three reports", "stated": 3, "listed": 2}],
  "recaps": [{"id": "0011"}],
  "terms": [{"terms": ["forecast", "projection"], "ids": ["0002", "0007"]}],
  "leftover_lines": [{"id": "0012"}],
  "numbers": [{"id": "0002", "quote": "14", "source": "Renewal register, November export"}],
  "confidentiality": {"list": "Hub confidentiality list for the project", "hits": []},
  "provenance": [{"id": "0013", "quote": "per the October call"}]
}
```

| Key | What to record | What blocks |
| --- | --- | --- |
| `sections` | One entry for each section in `assignments.json`, with its point | `reader_acts` is false |
| `headings` | One entry for each heading | `matches` is false |
| `repeated_facts` | Each fact stated more than once, with its line IDs | Every entry |
| `counts` | Each stated count beside the number of items listed | The two numbers differ |
| `recaps` | Lines that recap another section | Every entry |
| `terms` | Two or more terms used for one thing | Every entry |
| `leftover_lines` | Lines that exist only because of an earlier AI mistake | Every entry |
| `numbers` | Each number in `assignments.json`, with a named source or the ID of the line that states it is an assumption | No source and no `assumption_id` |
| `confidentiality` | The list that was checked, and each line it covers | Every hit |
| `provenance` | Meeting references, source lists and evidence notes in finished copy | Every entry |

The script checks that every cited line ID exists, every quote is word for word in its line, every section and heading has an entry and every number has one. A number missing from the map leaves the pass incomplete.

For `confidentiality.list`, name the project's confidentiality list in the Hub. When the piece belongs to no client project, write why no list applies.

`assignments.json` also carries `repeats`: identical sentences and figures the script found in more than one section. Check each one and record the real repeats under `repeated_facts`.

## Documents over 2,000 lines

`assignments.json` sets `two_step_document_pass` to true. Section workers each list their section's point, facts with figures, counts, terms and headings, with line IDs. One worker then compares those lists across sections for repeats, recaps, conflicting figures and drifting terms, and writes the single map.
