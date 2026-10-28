---
name: sow-quality
description: 'Quality gate for Estate client-facing Statements of Work and other contract-class deliverables (MSAs, Change Orders, proposals with contractual scope). Use to review, audit, de-slop, tighten, or finalize a SOW or contract, as the final authoring pass after a SOW is generated and before scope review, or to apply the Basis of Estimate framework to a new tier. It audits structure and language: structural de-slop, Basis of Estimate (volumetric assumptions into Exhibit A with soft and hard Change Order triggers), and cross-reference discipline. It does not compute pricing (the Pricing System does) or author or render the SOW itself (that is sow).'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Estate SOW Quality Gate

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`sow-proposal.md`](../prose-pass/references/registers/sow-proposal.md). Inputs, not a final pass.**

## What this skill is for

This is the authoring-quality pass that runs on a client-facing SOW after pricing is set and before it goes to scope review. It does not write scope, compute hours, or set price. It makes a finished SOW read like a senior consultant wrote it: every mechanic stated once, in one place, with no AI tells and no internal reasoning leaking onto the page.

Three responsibilities, in priority order:

1. **Structural de-slop.** The worst AI tells in a contract are not word-level (those are handled by the `prose-pass` skill). They are structural: the same clause restated three to five times, and rules followed by a sentence explaining why the rule exists. Fix these first. See `references/structural-deslop.md`.
2. **Basis of Estimate framework.** Volumetric assumptions (counts, Apex/LOC volume, catalog scale) belong in Exhibit A, framed as the basis of the estimate, not commitments. The scope body references them. Change Order triggers split into volumetric (soft) and binary workstream additions (hard). See `references/basis-of-estimate.md`.
3. **Cross-reference discipline.** Each mechanic gets one authoritative home; every other mention points to it. See `references/section-ownership.md`.

## Boundaries (what this skill does NOT do)

- It does not compute or change pricing, hours, or staffing. That lives in the Salesforce Pricing System (built via `scoping-agent`). If a number looks wrong, flag it for the user; do not invent or adjust it.
- It does not generate the playbook artifact set (Overview, DDOC, Pricing Sheet, Proposal). That is the playbook system.
- It does not override the Estate Playbook Process Guidelines. This skill operates inside that process: the SOW it produces still goes through scope review (Functional + CS + Tech cosign) before Deal Desk. The most-important-part rule from the Guidelines holds: the Assumptions section must be specific enough to hold across deals without being so narrow it fits one client.
- It does not reconcile to the pricing sheet by itself. Numbers in the SOW must trace to the authoritative pricing sheet; if they do not, that is a finding to surface, not a thing to fix silently.

## The workflow

Run these in order. Do not claim a section is clean without running the verification script against it.

### Step 1: Read the whole SOW first
Extract the prose (not tables) and read it end to end before editing anything. The structural tells are only visible across sections. A single section can look fine while the document repeats one mechanic five times.

```bash
extract-text SOW.docx | grep -v '^|' | grep -v '^[[:space:]]*$' | cat -n
```

### Step 2: Run the slop scan
The script reports repeated mechanics, justification-tail candidates, rule-of-three piles, em-dash and section-sign counts, and meta-commentary patterns. It finds candidates; you judge them. Both this script and the `extract-text` command above need the `extract-text` binary (from the docx skill environment) on PATH; the script itself is otherwise stdlib.

```bash
python scripts/slop_scan.py SOW.docx
```

### Step 3: Apply the structural fixes
For each repeated mechanic, decide its one authoritative home (see `references/section-ownership.md` for the standard CPQ SOW homes), state it fully there, and reduce every other instance to a one-sentence cross-reference or cut it. For each justification tail, cut the why unless it defends an exception or a stricter-than-default term (the exception rule is in `references/structural-deslop.md`).

If you are editing the generator (a `gen_*.js` docx-js script), edit the source and regenerate. If you are editing a delivered `.docx` with no generator, use tracked changes per the `docx` skill so the user sees every change.

### Step 4: Apply the word-level prose pass
Hand off to the `prose-pass` skill conventions for word-level patterns (buzzwords, hollow transitions, parallel gerunds). Do not duplicate that work here; this skill owns structure, `prose-pass` owns vocabulary. Both run during the build, not as a separate later pass.

### Step 5: Verify before asserting
Re-run the scan. Confirm: each mechanic appears once, repetition counts dropped, em-dash count is zero, section-sign count is zero, and every dollar/hour figure still traces to the pricing sheet. Only then report the SOW as clean, and report the counts, not an adjective.

```bash
python scripts/slop_scan.py SOW.docx --verify
```

## Hard rules (Estate house style, always)

- Never use the section-sign symbol. Write "Section 4" in full.
- Role naming: "Client Services Executive (CSE)" only. Never "Accountable Executive" or "AE".
- Em dashes drive to zero in SOW headings and body. Use colons, parens, or commas.
- Never fill a gap with a plausible-sounding projection. If a number or fact is missing, flag it.
- Better to raise a price than present scope Estate cannot staff. This skill does not set price, but if de-slopping reveals scope that the staffing cannot cover, surface it.
- Bold defined-term lead-ins are contract register, not an AI tell. Keep them.

## Quick reference: the three structural tells

| Tell | What it looks like | Fix |
|------|--------------------|-----|
| Repetition-as-thoroughness | Same clause/mechanic stated 3 to 5 times across sections | One authoritative home, others cross-reference it |
| Clause-justification | A rule followed by a sentence explaining why the rule exists | Cut the why, UNLESS it defends an exception or stricter term |
| Rule-of-three + meta-commentary | Verb piles ("does not remediate, re-architect, or add"); sentences answering internal questions the client never asked | Collapse the pile; delete the meta-commentary |

See `references/examples.md` for before/after pairs drawn from the Tier 1 CPQ Lift & Shift SOW.
