---
name: review-contract-scope
description: 'Quality gate for client-facing Statements of Work and other contract-class deliverables (MSAs, Change Orders, proposals with contractual scope). Use to review, audit, de-slop, tighten, or finalize a SOW or contract, as the final authoring pass after a SOW is generated and before scope review, or to apply the Basis of Estimate framework to a new tier. It audits structure and language: structural de-slop, Basis of Estimate (source-backed quantity meanings and change triggers), and cross-reference discipline. It does not compute pricing (the Pricing System does) or author or render the SOW itself (that is sow).'
---


# Review contract scope

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`sow-proposal.md`](../writing-diagnostics/references/registers/sow-proposal.md). Inputs, not a final pass.**

## Source authority and synthetic examples

Read the selected contract, confirmed quote and project review policy before editing.
Preserve roles, quantities, obligations, approval requirements and mandated wording.
The bundled examples are newly constructed editorial illustrations, not contract
terms. Use the actual agreement's structure, billing treatment, triggers and section
numbers. A fixed-scope cap must not become a nonbinding estimate; a fixed-fee
agreement must not acquire T&M billing. Raise contradictions as findings.

## Preserve the complete review contract

Read the complete document with its controlling quote, approved template and scope
baseline. Preserve parties, amounts, dates, approval state, obligations and required
disclosures. Distinguish an editorial correction from a commercial or legal decision.
Check that each deliverable has observable acceptance, each responsibility has an
owner, and each dependency is distinguished from a promise. Verify milestone totals,
dates, defined terms, attachments, exclusions and clause references against their
sources. Return edits and material unresolved decisions with exact document locations.
Remove duplication only when obligations and clause interactions remain intact. An
edited document stays unapproved until its authorized owner approves it.

## What this skill is for

This is the authoring-quality pass that runs on a client-facing SOW after pricing is set and before it goes to scope review. It does not write scope, compute hours, or set price. It makes a finished SOW read like a senior consultant wrote it: every mechanic stated once, in one place, with no AI tells and no internal reasoning leaking onto the page.

Three responsibilities, in priority order:

1. **Structural de-slop.** The worst AI tells in a contract are not word-level (those are checked by the internal diagnostics used by Writing Integrity). They are structural: the same clause restated three to five times, and rules followed by a sentence explaining why the rule exists. Fix these first. See `references/structural-deslop.md`.
2. **Basis of Estimate framework.** Review quantities (counts, code volume, catalog scale) against their agreed status as estimates, commitments or caps. Preserve the actual baseline and any distinction between volumetric (soft) and binary workstream (hard) triggers; do not invent either. See `references/basis-of-estimate.md`.
3. **Cross-reference discipline.** Each mechanic gets one authoritative home; every other mention points to it. See `references/section-ownership.md`.

## Boundaries (what this skill does NOT do)

- It does not compute or change pricing, hours, or staffing. Those values come from the confirmed quote or supplied commercial source; `scope-project` prepares authorized revisions. If a number looks wrong, flag it for the user; do not invent or adjust it.
- It does not generate the playbook artifact set (Overview, DDOC, Pricing Sheet, Proposal). That is the playbook system.
- Follow the selected project’s documented review and signoff process. Do not invent reviewers or treat an editing pass as contract approval. Keep assumptions specific to the actual engagement and its estimating basis.
- It does not reconcile to the pricing sheet by itself. Numbers in the SOW must trace to the authoritative pricing sheet; if they do not, that is a finding to surface, not a thing to fix silently.

## The workflow

Run these in order. Do not claim a section is clean without running the verification script against it.

### Step 1: Read the whole SOW first
Extract the complete document, including tables, and read it end to end before editing anything. The structural tells are only visible across sections. A single section can look fine while the document repeats one mechanic five times.

```bash
python3 scripts/slop_scan.py SOW.docx --text
```

### Step 2: Run the slop scan
The script reports repeated mechanics, justification-tail candidates, rule-of-three piles, em-dash and section-sign counts, and meta-commentary patterns. It finds candidates; you judge them. The bundled extractor uses Python’s standard library to read DOCX paragraphs, tables, headers, footers and notes; no external `extract-text` command is required. Read the rendered document separately for text in drawings or embedded objects and for layout. Corrupt or unsupported files fail explicitly.

```bash
python scripts/slop_scan.py SOW.docx
```

### Step 3: Apply the structural fixes
For each repeated mechanic, decide its one authoritative home (see `references/section-ownership.md` for mapping the actual agreement), state it fully there, and reduce every other instance to a one-sentence cross-reference or cut it. For each justification tail, cut the why unless it defends an exception or a stricter-than-default term (the exception rule is in `references/structural-deslop.md`).

If you are editing the generator (a `gen_*.js` docx-js script), edit the source and regenerate. If you are editing a delivered `.docx` with no generator, use tracked changes per the `docx` skill so the user sees every change.

### Step 4: Apply the word-level prose pass
Use `review-writing` to review meaning, voice and sentence construction during drafting. Its internal diagnostic tools check detectable wording patterns. Keep the SOW-specific structural review here; preserve the figure comparisons and required review receipt.

### Step 5: Verify before asserting
Re-run the scan. Confirm that authorized repetition repairs hold and every dollar/hour figure still traces to the commercial source. Review each remaining flag. Preserve exact quoted or mandated wording even when it contains flagged punctuation; record its source and required review disposition instead of editing an obligation to obtain a scanner pass. Report the actual counts and the remaining human review findings. A passing scan is a bounded diagnostic result; it does not prove semantic correctness or contract approval.

```bash
python scripts/slop_scan.py SOW.docx --verify
```

## Authored wording and preservation rules

- In authored cross-references, write "Section 4" in full. Preserve the source spelling in exact quotations or mandated language.
- Preserve the role names and responsibilities in the selected contract. Use Client Services Executive (CSE) only when that is the confirmed project role; never substitute it for an agreed Client Lead, Account Executive or other role.
- Apply the selected writing policy to authored headings and body. Retain exact quotations and mandated contract language; a diagnostic flag is not permission to change them.
- Never fill a gap with a plausible-sounding projection. If a number or fact is missing, flag it.
- If review reveals scope that the staffing cannot cover, surface the mismatch without adjusting price or scope.
- Bold defined-term lead-ins are contract register, not an AI tell. Keep them.

## Quick reference: the three structural tells

| Tell | What it looks like | Fix |
|------|--------------------|-----|
| Repetition-as-thoroughness | Same clause/mechanic stated 3 to 5 times across sections | One authoritative home, others cross-reference it |
| Clause-justification | A rule followed by a sentence explaining why the rule exists | Cut the why, UNLESS it defends an exception or stricter term |
| Rule-of-three + meta-commentary | Verb piles ("does not remediate, re-architect, or add"); sentences answering internal questions the client never asked | Collapse the pile; delete the meta-commentary |

See `references/examples.md` for newly constructed synthetic before/after pairs.
