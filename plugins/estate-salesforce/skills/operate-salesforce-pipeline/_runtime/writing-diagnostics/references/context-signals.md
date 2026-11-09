# Contextual review candidates

C25–C27 report observable structures for a reading pass. They never rewrite the
artifact, prove that a passage lacks value or evidence, or establish that a
requirement is invented. A clean result can miss all three behaviors. Keep exact
quotations, meaningful names, supported claims and useful repetition unchanged.

| Candidate | Observable signal | Limits and valid uses |
| --- | --- | --- |
| `C25-table-narration-candidate` | Prose immediately beside a simple table repeats every data row's content terms together in a clause matching only that row, with no unmatched content terms. The table has two to six data rows; the prose has six to 100 words. | Token overlap cannot judge usefulness, argument, every relationship, negation or accessibility. Number-word normalization covers zero through twenty; broader paraphrases can be missed. Useful summaries and accessible alternatives can match. Long tables, charts, legends, complex tables and broad paraphrases are outside this signal. |
| `C26-action-basis-candidate` | A generic question or directive about prerequisites for approval, or an action directive combined with closing-window pressure. | Wording and absent nearby evidence cannot prove that urgency or a gate is unearned. Explicit nearby requirement/source vocabulary in a clause without basic negation suppresses this narrow signal without verifying that source. Ordinary instructions and deadlines do not trigger by themselves. Many paraphrases are missed. |
| `C27-reaffirmation-candidate` | At least two distinct reassurance clauses within twelve subsequent sentences link back to a substantive claim with no extra content terms under a small normalization vocabulary. | Topic overlap is not semantic equivalence or evidence checking. Dates, numbers and explicit verification terms suppress this narrow signal. A single unsupported assurance, repeated identical statements and broader paraphrases are missed. Technical invariants, purposeful refrains and independent reminders may be valid. |

Review every sample against the surrounding content and supplied sources. Do not
invent a missing requirement, recheck or consequence to repair a candidate.
Preserve uncertainty and the exact scope of evidence. The broader editorial
review also covers restated figures, legend narration, misleading headings,
unsupported assurances and structure that misrepresents the content.

The adapter preserves simple table/paragraph boundaries in Markdown, visible
HTML and Word/PowerPoint XML. Office parts have separate review boundaries;
content on different slides is not treated as adjacent. Nested tables are not
interpreted as simple tables. An HTML table's explicit `aria-describedby` or
`aria-details` relationship identifies its text alternative, including a nested
paragraph, and excludes that alternative from C25 only. This is an accessibility
hint, not permission to relabel prose to avoid review. HTML script/style content
continues through the legacy checks; it is outside these visible-structure
signals. Other supported inputs use extracted text; flattened PDF, spreadsheet
and structured-data text does not establish table or page geometry. Locations
refer to extracted lines, HTML lines or Office part/paragraph positions, not
rendered coordinates.

The scanner fails explicitly above four million extracted characters, 20,000
blocks, 20,000 sentences per part, or 100 contextual candidates. It does not
silently return a partial pass. Split and review the complete artifact when a
limit is reached, retaining an inventory of the reviewed parts and considering
cross-part repetition in the reading pass.

## Retain a justified match

A candidate still makes the scanner return exit 1. Read all occurrences before
recording an assessment. With `prose_receipt.py emit`, repeat
`--retain-candidate RULE=REASON` once for each retained candidate rule and provide
`--retention-source SOURCE`. The reason must cover every occurrence of that rule
in this artifact; quote locations when their purposes differ. C24's existing
`--retain-framing-reason` remains supported. Only C24–C27 are eligible; this cannot
waive another diagnostic. Changed artifact bytes or checker/configuration
fingerprints require a renewed assessment. A valid record proves those binding
checks, not the truth of the reviewer's judgment.

For example, after checking the supplied approval policy:

```bash
python3 scripts/prose_receipt.py emit review.md --out receipt.json \
  --no-change-justification "The heading accurately introduces the supplied conditions." \
  --retain-candidate "C26-action-basis-candidate=All reported headings introduce the policy's actual approval conditions." \
  --retention-source "Supplied release policy REV-2, approval section"
```
