---
name: writing-diagnostics
description: Internal diagnostic and figure-preservation tools used by review-writing. This module supplies scanners and review records; it does not select an author voice or act as a second editor.
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.


# Writing diagnostics

This internal runtime supplies scanners and review records for `review-writing`. Load it through that workflow.

Read [review-writing](_runtime/review-writing/WORKFLOW.md) before using these tools.
That workflow owns writing review. A confirmed personal profile supplies the
author's voice. A visual brand profile controls appearance; it cannot select an
author voice or change a fact. These tools report detectable patterns; they do not rewrite
text or establish editorial quality.

Use the tools on every kind of authored prose, including instructions and
internal records. Keep exact source evidence and executable syntax unchanged.
Review the new wording around those spans. A file extension or audience label
does not exclude authored language from review.

## Review a saved file

```bash
python3 scripts/writing_check.py --config house.json FILE
python3 scripts/writing_check.py --config house.json --json FILE
```

The checker reads prose from supported document formats and structured text
fields. Exit 0 means it found no patterns, 1 means it found a pattern and 2 means
the check could not finish. Read its output and the complete document. Repair
the argument or sentence that caused a finding, then rerun the check.

`C24-formulaic-the-framing` reports recurring label and announcement shapes as
review candidates. It does not establish that a name or quotation is wrong.
Keep a justified match unchanged and record the reason when a review record is
required. A retained candidate still produces exit 1; do not claim a clean scan
or change a valid passage solely to obtain exit 0.
For a receipt, use `--retain-framing-reason "REASON" --retention-source "SOURCE"`
with `prose_receipt.py emit` after reading every candidate. The assessment is
bound to the artifact hash and applies only to C24; it cannot waive other rules.
C25–C27 add narrow review candidates for table readouts, action basis and repeated
reassurance. Read [contextual signals](references/context-signals.md) for their
observable conditions, format limits and rule-specific retention procedure.
These candidates cannot establish redundancy, unearned urgency or lack of evidence.
The validator checks the record. The reviewer remains responsible for the judgment.

Do not change the filename, label prose internal or put authored wording in a
quote to obtain a pass. A literal source span remains verbatim only when its
source and exact extent are identified in the internal review record. Keep
reviewing the surrounding authored text. Do not reclassify an invented claim
or an awkward sentence as captured evidence.

`prose_check.py` is a compatibility command for the same supported input path.
The older lexical engine also reports vocabulary and construction diagnostics.
Read [surface policy](references/surface-policy.md) for source-span handling.

## Review recurring patterns

Read [construction rules](references/construction-rules.md) and
[patterns](references/patterns.md) when investigating a recurring construction.
Use the applicable register for format-specific advice:

| Format | Reference |
| --- | --- |
| Slides | [Deck](references/registers/deck.md) |
| Contract or proposal | [SOW and proposal](references/registers/sow-proposal.md) |
| Report or brief | [Readout](references/registers/readout-brief.md) |
| Short message | [Email and Slack](references/registers/email-slack.md) |
| Other authored text | [General](references/registers/general.md) |

Registers supply examples and format checks under review-writing. Preserve
required terms and confirmed voice when a legacy example uses another style.
Read headings with their body text. Remove repeated explanations and subtitles
that repeat a title. A vocabulary substitution cannot repair an empty claim.

```bash
python3 scripts/scan.py audit docs "*.md"
python3 scripts/scan.py score draft.md --json
python3 scripts/scan.py --input FILE
```

The audit command includes supported structured files and returns an error for
unsupported input. The score command reports lexical density for comparison;
its success does not establish compliance. It strips some executable spans for
that measurement. Use the complete authored-language check for release review.

Vocabulary sources remain in `scripts/rewrite_scan.py`. The generated wordlists
come from `scripts/sync_wordlists.py`; preserve their synchronization check.
Weighted lists retain their existing weights. Changes to detection require
representative positive examples and valid prose examples, not a lower budget
chosen to pass a particular draft.

## Preserve figures and meaning

Before a substantive rewrite, retain the source version. Reconcile figures:

```bash
python3 scripts/rewrite_scan.py --tie-out SOURCE REWRITE
```

An added figure needs its source. A missing source figure requires checking
whether the omission was authorized. The writing pass cannot approve a price,
scope change or commercial commitment. Use the confirmed quote or versioned
estimate and preserve its assumptions. Keep client-stated figures attributed.

Compare the finished text with its source for changed ownership and conditions.
Retain factual uncertainty and meaningful author choices. Never add a number,
quotation or anecdote to make vague writing sound specific.

## Record a required review

When the producing workflow requires a narrative review record, use:

```bash
python3 scripts/prose_receipt.py emit FILE --out receipt.json \
    --before-file SOURCE \
    --protected "commercial figures from the supplied quote" \
    --change "replaced the generic claim with the supported action"
python3 scripts/prose_receipt.py validate receipt.json
```

The record binds the file hash to the checker result and declared edits. The
validator rechecks measurable assertions and figure changes. A no-change result
needs an actual reading assessment; arbitrary edits are unnecessary. A record
does not independently establish that an editor understood the document.

Brief replies receive writing review without a receipt. Captured transcripts
remain evidence and are never rewritten for style. Newly authored descriptions
in records still receive the same writing review as any other prose.

## Select configuration

The canonical baseline is `house.json`. An explicit configuration can add
checks; it cannot disable the maintained rules. The scripts and word data ship
together and need no neighboring installed skill. See
[configuration](references/house-overlay.md) and the [tellscan rule map](references/tellscan-rule-map.md) when maintaining the diagnostic
engine. Every supported artifact still needs a complete reading against its
facts and intended reader after the commands pass.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
