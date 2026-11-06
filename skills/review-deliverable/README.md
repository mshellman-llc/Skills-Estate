<!-- Maintained reference: edit by hand and keep it consistent with skill.yaml and SKILL.md. No generator script exists in this repository. -->
# Quality Gate

> Run the required Estate release controls and refuse finalization without the prose review and evidence records, plus brand review when the artifact is styled.

**What it does.** Select and run the required Estate release controls before any Word document, PowerPoint deck, Excel workbook, PDF, HTML page, proposal, report, email, Slack message, or decision-bearing artifact is finalized.

**Use it when.** For every styled or client-facing output. Requires inspected evidence from the prose review (with a writing-diagnostics receipt for final narrative artifacts) and, for styled output, from brand-renderer plus the rendered result, not a claim that another skill was mentioned. Blocks release when a required runtime, receipt, source support, or rendered output is absent.

**Related.** Uses the bundled [`writing-diagnostics`](../writing-diagnostics/README.md) diagnostics. Contractual scope also requires the contract scope and obligation review mode in `write-statement-of-work`, which is not bundled here; existing receipts retain the `review-contract-scope` control identifier. Record the contract check as blocked when that workflow or its evidence is unavailable.

**Full trigger logic and boundaries:** [SKILL.md](SKILL.md) · tier `core`
