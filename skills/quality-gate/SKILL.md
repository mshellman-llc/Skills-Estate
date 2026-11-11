---
name: quality-gate
description: 'Select and run the required artifact release controls before any Word document, PowerPoint deck, Excel workbook, PDF, HTML page, proposal, report, email, Slack message, or decision-bearing artifact is finalized. Use for every branded or client-facing output. Requires executable evidence from prose-pass and brand-renderer, not a claim that another skill was mentioned, and blocks release when a required runtime or receipt is absent.'
---

# Quality gate

> **Before grading:** read [`build-card.md`](../_shared/build-card.md). For a
> branded artifact, ask the caller for the `runtime_preflight.py --json` report
> `brand-renderer` produced before it drafted. Do not record a missing asset or a
> passed control until that report has supplied an absolute path or failed.

## Where this sits

`brand-renderer` is the entry point for every branded surface. It runs the
runtime preflight, renders, gates, and then calls this skill for the release
decision. The direction is one way:

```
brand-renderer -> prose-pass   -> the authored artifact
brand-renderer -> quality-gate -> the release decision
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

1. Apply `prose-pass` to client-facing prose. For a narrative artifact being
   marked final, this means the full rewrite pass, never the checker alone: the
   pass must produce a receipt (`prose-pass/scripts/prose_receipt.py emit`).
   Validate that receipt. Reference it on the prose-pass check's `receipt` field.
   `quality_gate.py` refuses a record that
   claims a final narrative artifact without one. Sound prose may pass
   unchanged only with a justified no-change assessment in the receipt.
2. Cite `brand-renderer` evidence when brand rendering or branded presentation is
   required: the preflight report and the `brand_check.py` result, by path. Brand
   controls identity, so an off-palette hex, a redrawn mark, or a substituted font
   is a fail. Composition is content-driven, so a review flag on footer placement
   or slide layout takes a disposition and stands.
3. Apply `sow-quality` to SOW or contractual scope content.
4. Apply the producing skill's deterministic validator when one exists.
5. Require evidence review for unsupported claims, figures, approvals, scope, status, or go/no-go conclusions.

Prose-pass receipts apply to narrative artifacts: briefs, proposals, SOWs,
decks, readouts, one-pagers, decision documents. They do not apply to raw
evidence, transcripts, ledgers, or machine-readable files; running a voice
rewrite over evidence corrupts the record it exists to protect.

Ordinary email and Slack take a reading pass against the voice rules, no receipt.
They arrive here only once the message carries a consequential figure, an
approval, scope, a commitment, or a decision. That is the same list the
fail-closed rule below reads, which is why a short message about a number gets
the same discipline as a document about one.

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

Return a durable Markdown quality record. Include artifact identity, selected controls, performed checks, assertion evidence, release verdict, blockers, remediation, plus Knowledge Hub update status.
