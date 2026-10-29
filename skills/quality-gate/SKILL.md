---
name: quality-gate
description: 'Select and run the required artifact release controls before any Word document, PowerPoint deck, Excel workbook, PDF, HTML page, proposal, report, email, Slack message, or decision-bearing artifact is finalized. Use for every styled or client-facing output. Requires inspected evidence from the prose review (with a prose-pass receipt for final narrative artifacts) and, for styled output, from brand-renderer plus the rendered result, not a claim that another skill was mentioned. Blocks release when a required runtime, receipt, source support, or rendered output is absent.'
---


# Quality gate

Read [`build-card.md`](../_shared/build-card.md). Open the finished artifact
and its sources before judging it. For a styled artifact, locate the
`brand-renderer` preflight report (`runtime_preflight.py --json`) and the
`brand_check.py` result. Record a missing asset or a passed control only after
the report supplies an absolute path or fails. Run an available missing check
directly; ask the user only for an input or decision the available sources
cannot supply.

## Where this sits

The producing workflow owns the artifact. This module reviews the result and
the evidence supporting it. Writing review follows writing-integrity, while
the rendering library checks the selected visual profile:

```
producing workflow -> writing-integrity -> authored prose review
producing workflow -> brand-renderer -> rendering checks
producing workflow -> quality-gate -> deliverable review
```

This skill ships no renderer and packages none. A copy of `brand-renderer` here
would make each skill the other's runtime, and one upload would ship two
renderers whose fixes could diverge. Evidence for the brand control arrives as
the caller's preflight report and `brand_check.py` output, cited by path. An
absent report is a `blocked` verdict, never a `pass`.

## Preconditions

- Identify the artifact type, audience, lifecycle stage, and decision supported.
- Confirm the artifact and its evidence record are available for review.

## Route the checks

1. Review every piece of authored prose under `writing-integrity`, including
   instructions, labels and internal records. Read the complete result and
   repair actual defects; sound prose does not need arbitrary edits. The quality
   record names this check `prose-pass`, the control `quality_gate.py` looks for.
   Run the `prose-pass` diagnostics on saved files; they report only detectable
   patterns, so a clean scan does not show that the prose was read.
   For a final narrative artifact, emit the receipt with
   `prose-pass/scripts/prose_receipt.py emit`, validate it, and put its path in
   the check's `receipt` field and the document path in `artifact.path`.
   `quality_gate.py` validates the receipt against that document's current bytes
   and reruns its prose check. A bundled gate uses the prose validator inside its
   containing package, including a shared `_runtime` folder. It refuses an
   external sibling or a validator symlink that leaves that package. Relative
   paths resolve from the quality record's directory; newly emitted receipts
   store an absolute artifact path. Regenerate an older receipt with a relative
   artifact path before final release. A blocked prose check can record the
   missing receipt while
   withholding release. Sound prose may pass unchanged only with a justified
   no-change assessment in the receipt.
2. For a styled artifact, cite `brand-renderer` evidence: the preflight report
   and the `brand_check.py` result, by path. Then render or open the actual file
   and inspect every page, slide or screen for clipping, contrast, missing
   content, wrong figures and broken controls. A color scan cannot establish
   legibility or layout. If the rendered output is missing or cannot be
   produced, the brand check is `blocked`. Brand controls identity, so an
   off-palette hex or a redrawn mark is a fail. A font substitution passes only
   when it is the selected profile's documented fallback and the record
   discloses it; any other substitution is a fail.
   Composition is content-driven, so a review flag on footer placement or
   slide layout takes a disposition and stands.
3. Apply `sow-quality` to SOW or contractual scope content.
4. Apply the producing skill's deterministic validator when one exists.
5. Reconcile claims, figures, approvals, scope, status, and go/no-go conclusions
   with their sources. Recompute totals and compare quoted numbers with the
   source. A claim whose source is missing, conflicting or too thin to support
   it is `blocked` until the source is found or the claim is removed. Marking it
   as an assumption is an alternative only for lower-risk provisional analysis,
   as in Grade. Approvals, deployment or publication status, and unsupported
   committed financial figures stay fail-closed: find the source or remove the
   claim, and never record an approval as an assumption. A generated file is not
   evidence that anyone approved,
   sent, published or deployed it. When the request included a write, check the
   destination and state the layer reached: prepared locally, committed,
   published, or verified in the destination.

Prose-pass receipts apply to narrative artifacts: briefs, proposals, SOWs,
decks, readouts, one-pagers, decision documents. Raw evidence, transcripts,
ledgers, and machine-readable files keep their exact source spans unchanged and
take accuracy checks instead of a voice rewrite. Any summary, label or comment
written around those spans is authored prose and is reviewed under item 1.

Ordinary email and Slack take a reading pass against the writing standard, no
receipt. They arrive here only once the message carries a consequential figure,
an approval, scope, a commitment, or a decision. A short message about a number
gets the same source check as a document about one.

## Grade

1. Record every check as pass, fail, blocked, or not applicable.
2. Cite the exact artifact section or validator evidence supporting the result.
3. Fail closed when any high-risk assertion lacks support.
4. Permit a lower-risk provisional draft only when gaps and limitations are explicit.

## Failure behavior

- Do not mark a check complete merely because another skill is mentioned.
- Do not claim a downstream control ran without invocation or deterministic evidence.
- Return a remediation list when release is blocked.

## Output contract

Return a durable Markdown quality record. Include artifact identity, selected controls, performed checks, assertion evidence, release verdict, blockers, remediation, plus Knowledge Hub update status (`not_applicable` when the workflow has no hub write). The command validates record structure and the final narrative receipt. Citation and hub-status fields remain reported evidence; the command does not verify those destinations or prove that a person read the artifact. Exit 0 means the record is valid, including an honest blocked record. Require `released: true` before treating the result as release permission. Library callers pass the record directory as `base_dir` when using relative paths. Regenerate receipts after moving artifacts to another machine or folder. Reading the artifact and checking its sources remain required.
