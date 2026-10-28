---
name: playbook-builder
description: 'Define, add, replace, deduplicate, audit, or maintain a productized offering, service, play, or playbook in a consistent catalog format. Use it to turn a rough idea into a sellable playbook, write internal and external one-pagers, settle scope, deliverables, value and buyer, audit a catalog against research findings, or keep a family of plays consistent when one entry changes. Works for any consulting, product, or service catalog, not just AI.'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Playbook Builder

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Defines offerings with high clarity and keeps a catalog of them consistent. Two layers: **think** with the Clarity Framework (seven questions), then **present** in a fixed house format (scope, deliverables, value, buyer, Tldr, Eli5, and two one-pagers). Get the thinking right and the artifacts follow.

Use it to define a new offering, audit an existing catalog against fresh inputs, detect and resolve duplication, add or replace an entry in the house style, and maintain the corpus when one entry changes.

## When you are invoked, first locate yourself

Figure out which job the user is asking for. They overlap, but the entry point differs:

- **Define** a brand-new offering from scratch or from a rough idea. Start with the Clarity Framework, then render the house format.
- **Audit** an existing catalog against findings (a conference brief, market research, a strategy note). Score each play against the input's themes, name gaps, and flag actions. See `references/audit.md`.
- **Deduplicate**: decide whether a new offering is already covered by an existing one, and whether to add or replace. See "The add-vs-replace decision" below.
- **Add / replace** one entry in an existing catalog while leaving the rest untouched. Obey the corpus-integrity rules below.
- **Maintain**: re-render the full corpus after a change, carrying unchanged entries verbatim.

If the user hands you an existing catalog, read it first and match its exact house style rather than imposing this one. The templates here are the default when none exists.

## Layer 1: think in the Clarity Framework

Seven questions, worked in this order. The audience constrains everything, so "who" comes first for reasoning. Full guidance with traps sits in `references/clarity-framework.md`. Read it when defining or auditing an offering.

1. **Who is it for?** Define by posture and situation, not just firmographics. Name the disqualifiers at both ends. Design for the economic buyer (who can say yes); accept a junior sponsor only as a credible path to that buyer.
2. **What is it?** One sentence that lands with zero context. Name the category and what it is *not* (positioning, not scope).
3. **Why should they care? (the client)** The outcome in the client's language. Lead with the change in their situation, not features.
4. **Why should we care? (us)** Our objective and the handoff. For anything free or loss-leading, this is the design driver: reverse-engineer every other answer from what you want it to lead to.
5. **What's included?** Concrete scope: activities and deliverables, specific enough to estimate.
6. **What's not included?** The boundaries. **Every boundary doubles as a doorway.** State each limit as the on-ramp to a paid next step.
7. **How do we deliver it?** Mechanics only: format, flow, effort, who runs it, how long. Keep the handoff out of here; that lives in question 4.

Mark each answer **locked** or **open**, using the words rather than a symbol or a score. An offering is not ready to sell until all seven are locked. Gaps cluster in 3, 4 and 6, so check those first.

**Reasoning order vs presentation order.** Think Who-first, but client- and sales-facing artifacts lead with **What**: people need to know what they are reading about before anything else lands.

## Layer 2: present in the house format

`references/house-format.md` is the **normative** spec for the entry structure and the field list. `references/play-entry-template.md` is the fill-in copy of it. This section summarises both.

Every entry carries five fact blocks, then four rendered views:

- Fact blocks (the source of truth, bulleted and concrete): **In scope**, **Out of scope**, **Deliverables promised**, **Business value**, **Target buyer**.
- **Tldr**: one or two sentences.
- **Eli5**: plain language, a metaphor is fine, no jargon.
- **Internal one-pager**: all seven questions, including "why should we care".
- **External one-pager**: the same, minus "why should we care", in the client's second person, with internal guardrails softened.

The one-pagers restate the fact blocks for two audiences. They introduce no new claims.

Three files describe this shape (here, `references/house-format.md`, `references/play-entry-template.md`). If they ever disagree, `references/house-format.md` wins and the other two get corrected in the same pass. Do not let a field get renamed in one place only.

**Naming note.** "Internal one-pager" and "external one-pager" are sections *inside* a catalog entry. Where a house artifact set already reserves the name "One-Pager" for a standalone client deliverable, say which you mean rather than letting the two collide.

## The add-vs-replace decision

When a new offering might overlap an existing one:

1. Lay the two side by side on the seven questions. Same slot (same buyer, same position in the ladder, same free/paid tier) means they are the same offering, not two.
2. If they are the same, **replace, do not add.** A second near-duplicate SKU splits pipeline and confuses sellers and clients, the exact problem a clean catalog exists to prevent.
3. When replacing, carry over whichever version is sharper on each of the seven questions, and reconcile conflicts explicitly (effort, buyer, framing). Do not silently average them.
4. If the new offering is genuinely a *different rung* (lighter or heavier, earlier or later in the ladder), keep both, but make the **boundary between them crisp** in each one's "what's not included". Each should name the other as the adjacent step. A vague boundary is how a new entry collapses into an existing one.

## Non-negotiable discipline rules

Apply these in every job.

- **Never fabricate numbers.** Prices, durations, dates, headcounts, ROI figures: if the source does not ground it, do not invent it. Write it as an open decision for a human to set. Leaving a band open, or setting it deliberately high enough to be deliverable, beats publishing a figure the team cannot hit.
- **Flag decisions, don't assume them.** When a choice needs a human (a fee band, a routing rule, a numbering scheme, a boundary), name it explicitly in a "decisions to lock" list rather than quietly picking one.
- **Every boundary is a doorway.** Each "not included" line should route to the paid next step, so the section seeds conversions instead of reading as a wall of disclaimers.
- **Separate their motive from ours.** "It builds our pipeline" is question 4, never question 3. Keep client value in the client's language.
- **Ground every claim.** The one-pagers add no new facts beyond the fact blocks. If a one-pager needs a fact that is not in that block, either add it to the block deliberately or cut it.
- **Match the destination.** When editing an existing catalog, reproduce its heading style, separators, and section names exactly. Do not "improve" the format of untouched entries.
- **Write in the destination's voice.** A catalog entry is published copy, so it inherits the destination's documented voice standard; where one is documented, that standard governs. Check for it before writing and follow it.

## Voice

The Estate default: zero em dashes anywhere including headings, confident and direct, no buzzwords. Beyond vocabulary, strip the machine-written sentence shapes (antithesis flips, trailing "-ing" benefit clauses, throat-clearing openers, rhetorical triads). `references/voice.md` carries the full list and the one hard limit: a voice pass never softens a figure, a boundary, or a caveat.

## Corpus integrity (when adding or replacing inside an existing catalog)

- **Carry unchanged entries verbatim.** Never re-transcribe an entry you are not changing; re-typing introduces drift. Copy the source file and edit only the target sections.
- **Verify with a diff.** After editing, run `scripts/verify_corpus.py` and confirm the entries you did not touch are byte-identical:

  ```
  python3 scripts/verify_corpus.py --source OLD.md --edited NEW.md --changed 07 preamble
  ```

  Declare every id you meant to change, plus `preamble` if you bumped the version line. The script fails on any undeclared difference, on duplicate entry ids, and on an undeclared preamble edit. It ignores only trailing blank lines and one trailing `---` separator per entry. Run `python3 scripts/verify_corpus.py --selftest` if you want to confirm the checker itself is sound before trusting a PASS.
- **A PASS is evidence, not proof.** It confirms the text you did not declare is unchanged. It says nothing about whether the entry you *did* change is correct, grounded, or in voice. Those are still your job.
- **Cascade cross-references and numbering.** If you renumber or rename an entry, update every "(see play NN)" reference across the corpus. If you add an entry, decide its number deliberately and flag any collision with other numbering schemes (catalog numbers, internal IDs, worksheet numbers) as a decision rather than resolving it silently.
- **Record provenance.** Bump the version line and add a short revision note stating what changed, what stayed, and what remains open. Do not leave a stale "nothing here is new" claim in place after adding something new.

## Know whether the catalog is authored or generated

Before editing anything, find out which file a human actually owns.

- **Hand-authored catalog**: a markdown file someone maintains directly. Edit it in place, then verify with `scripts/verify_corpus.py`.
- **Generated catalog**: the published file is built from a source by a script. Editing the rendered output is wrong even when it looks right, because the next build silently discards it. Find the source file and the build step, edit the source, run the build, then verify.

If you cannot tell which one you are looking at, stop and ask. A generated file usually says so in a header, sits next to a build script, or is paired with a per-entry source directory.

## Workflow

1. Identify the job (define, audit, dedup, add-replace, maintain).
2. Read the relevant reference: `references/clarity-framework.md` for define and dedup, `references/house-format.md` for rendering, `references/audit.md` for audits.
3. Establish whether the catalog is authored or generated, and locate the file a human owns.
4. Copy that file to a writable location and match its style.
5. Do the thinking (seven questions) before writing any artifact.
6. Render using `references/play-entry-template.md` (single entry) or `references/audit-template.md` (audit).
7. Apply every discipline rule, including the voice pass. Collect open choices into a "decisions to lock" list.
8. If you touched a corpus, run `scripts/verify_corpus.py` and report the result.
9. Deliver, then surface the decisions list and any numbering or boundary flags.

## Files in this skill

- `references/clarity-framework.md`: the seven questions in depth, with traps. Read for define and dedup.
- `references/house-format.md`: the normative entry spec and the internal and external one-pager rules. Read for rendering.
- `references/audit.md`: how to audit a catalog against findings and structure the deliverable.
- `references/voice.md`: the house voice standard, the sentence shapes to strip, and what a voice pass may never touch.
- `references/play-entry-template.md`: fill-in template for one catalog entry.
- `references/audit-template.md`: structure for an audit deliverable.
- `scripts/verify_corpus.py`: proves unchanged entries carried over verbatim. Supports `--selftest`.
