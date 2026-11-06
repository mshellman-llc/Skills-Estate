# Build card

Before producing a deck, document, page, workbook, PDF, or other artifact, resolve
its required inputs, output format, brand profile, and runtime. Keep the
producing skill's specialized method and acceptance criteria.

## Resolve the profile and runtime

The canonical brand rules live in a Markdown profile, not in this card or in
each skill. Use an explicit profile or `SKILLS_BRAND_PROFILE` when supplied,
otherwise the project's `brand.md`, otherwise the packaged estate neutral
profile. An explicitly selected missing or invalid profile is an error.

Run the installed brand renderer's preflight:

```bash
python3 <brand-renderer>/scripts/runtime_preflight.py --json
```

It returns the selected profile, required asset paths, and local prose, brand,
and quality validator paths. Use those paths rather than assuming a company
drive, cloud mount, or neighboring skill exists.

Use the profile's colors, typography, and layout values through the shared
Python or JavaScript token runtime. Do not copy a palette into the producing
skill. A logo is optional unless the selected profile requires one. When a logo
or font file is declared, validate that file and preserve its proportions;
do not invent a replacement. System fonts and the neutral profile support work
without proprietary assets.

For Office outputs, use the profile's `type.office` font. Resolve a missing
renderer or library before beginning the build, and include its installation or
configuration in the supported workflow.

## Produce the requested artifact

Follow [the output contract](output-contract.md). Create the requested deck,
document, page, data record, or operational result. Save source data and a
supporting record when they help reproduce or verify it. A generic Markdown
report is not a substitute for the requested output.

Keep client facts and confirmed figures tied to their sources. Label synthetic
examples and estimates. Keep the current deliverable, its source inputs, command results and the
smallest reproduction needed to explain a failure. Preserve distinct source
revisions; remove superseded generated attempts after checking their consumers.

## Write for the audience

Apply the user's writing requirements and any confirmed project voice profile
while drafting. Use concrete subjects, plain verbs, supported claims, and terms
the intended reader understands. Preserve qualifiers that affect meaning.

Read the applicable register for the format:

| Output | Register |
|---|---|
| Slide deck, DDOC, PPTX | [Deck](../_runtime/writing-diagnostics/references/registers/deck.md) |
| SOW, proposal, contract prose | [SOW and proposal](../_runtime/writing-diagnostics/references/registers/sow-proposal.md) |
| Brief, readout, report, one-pager, journey map | [Readout and brief](../_runtime/writing-diagnostics/references/registers/readout-brief.md) |
| Email, Slack, short-form message | [Email and Slack](../_runtime/writing-diagnostics/references/registers/email-slack.md) |

## Check the finished result

Follow [the release gate](release-gate.md). Run applicable validators using the
paths returned by preflight:

```bash
python3 <writing-diagnostics>/scripts/prose_check.py --config <writing-diagnostics>/house.json FILE
python3 <brand-renderer>/scripts/brand_check.py FILE
```

Use `writing-diagnostics/scripts/prose_receipt.py` when the producing workflow requires
a narrative receipt. Review meaning and evidence as well as mechanical results.
Open or render the artifact, inspect every page or slide, and exercise its
interactions. Fix missing content, clipping, illegible contrast, wrong figures,
and broken controls before delivery.

A hook is available only when its installation and invocation were verified.
Run the finished-output checks explicitly regardless of hook configuration.

Writing Integrity owns writing review. The `writing-diagnostics` paths above refer to its retained internal diagnostics; Prose Pass is retired as a standalone skill.
