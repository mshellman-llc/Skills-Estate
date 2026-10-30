<!-- Maintained reference: edit by hand and keep it consistent with skill.yaml and SKILL.md. No generator script exists in this repository. -->
# Quality Gate

> Run the required Estate release controls and refuse finalization without the prose review and evidence records, plus brand review when the artifact is styled.

**What it does.** Select and run the required Estate release controls before any Word document, PowerPoint deck, Excel workbook, PDF, HTML page, proposal, report, email, Slack message, or decision-bearing artifact is finalized.

**Use it when.** For every styled or client-facing output. Requires inspected evidence from the prose review (with a prose-pass receipt for final narrative artifacts) and, for styled output, from brand-renderer plus the rendered result, not a claim that another skill was mentioned. Blocks release when a required runtime, receipt, source support, or rendered output is absent.

**Related.** Calls [`prose-pass`](../prose-pass/README.md), [`sow-quality`](../sow-quality/README.md); Used by 20 skills.

**Full trigger logic and boundaries:** [SKILL.md](WORKFLOW.md) · tier `core`
