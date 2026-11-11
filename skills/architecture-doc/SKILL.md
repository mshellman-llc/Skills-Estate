---
name: architecture-doc
description: 'Build formal Aleysian-branded architecture and system-design documents for a client, grounded in named sources with every claim sourced and the brand and prose gates applied. Covers architecture intent (what and why) plus engineering views: components, interfaces, data model, APIs, serving path, deployment, and trade-offs. Use for a client-facing architecture document, platform architecture, architecture reference, or a sourced technical design document, even if the user does not say Aleysian. Do NOT use for a fast, unbranded, inline working design or exploratory architecture discussion (that is system-design), a client proposal or SOW (solution-brief, sow), or a journey map (journey-mapping).'
---

# Aleysian Architecture Doc

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Build architecture and system-design documents the Aleysian way: a consolidated, branded reference grounded in authoritative sources, sourced claim by claim, with brand canon applied during the build and the house gates run before it ships.

Two altitudes, one method. The **architecture doc** carries the what and why. The **system
design** carries the engineering how. Their section spines are under "The two documents" below.

They are complementary. The system design points to the architecture for the what and why and does not repeat it. Where a confirmed decisions record exists, it is the authoritative source both documents defer to.

This skill produces the architecture. The Aleysian design system (tokens, stylesheet, logos) comes from `_shared/aleysian-brand`, and the release gates come from `brand-renderer` and `prose-pass`. Those are the house single sources for brand and voice; this skill references them rather than duplicating them.

---

## House rules (apply throughout, not as a post-pass)

- **Source every claim.** Each fact traces to a named doc, decisions record, transcript, or record, carried inline as a source line. An unsourced fact is a defect. Source lines are legitimate content, not clutter.
- **Never fill a gap with a plausible projection.** If a source does not cover it, it is a gap. Gaps and open decisions go to the operator in chat, never into the document. The delivered artifact carries no gap-flags, no "TBD", no "to be confirmed".
- **Design proposals are the author's job, and are not gap-filling.** A system design proposes a data model, an API, a mechanism. Frame each as a proposal and state its trade-off. That is design, not fabrication. Where a genuine fork exists, take a position in the doc, state what it gave up, and flag the fork to the operator in chat.
- **One source of truth, and precedence.** Name the authoritative source. Where sources conflict, the authoritative or newer one governs. Remove the superseded framing, do not annotate it. A banner over stale text is not a fix.
- **Numbers cascade.** A change in one artifact updates every artifact in the set.
- **Brand canon during the build.** State the design system before building, and apply it as you write, not as a cleanup pass.
- **Aleysian voice.** No em dashes; use a period and a new sentence. No en dash for ranges; write "to". Middle dot for inline separators. Digits, not spelled numbers. Serial comma. No forbidden words (leverage, robust, transformative, seamless, ecosystem, and the rest of the house list). No section sign; write "section". No emoji; use inline SVG for a functional icon. Sentence case. Borders 1px, radii capped at 8px on a 4 and 8 scale.

---

## When to use

- Build an architecture or system-design reference for a product or platform.
- Consolidate a brief, a decisions record, and notes into one branded document.
- "Build me the architecture like the [X] one."
- Produce the engineering design (data model, API, serving path) for a system.
- Turn a confirmed decisions record into a clean, consistent architecture set, and cleanse any earlier artifacts that now conflict.

## When NOT to use

- A client-facing proposal, SOW, or deal-decision deck (use `solution-brief`, `sow-quality`, `ddoc`).
- A journey map or service blueprint (use `journey-mapping`).
- Requirements capture, epics, and user stories (use `requirements-capture`).
- Pricing or scoping (that routes to the scoping path; this skill invents no numbers).
- A slide deck (use `pptx` or `ddoc`).
- A quick, unbranded working design for an internal system, where the sourcing discipline and the
  brand and prose gates would be overhead. Use `system-design`.

---

## Required inputs

- **The authoritative source material.** A brief, a decisions record, a stand-up or build plan, discovery notes. Name them and write down the precedence before building.
- **The design system and the gates.** Aleysian tokens, stylesheet, and logos from `_shared/aleysian-brand`. The brand gate from `brand-renderer`, the prose gate from `prose-pass`.
- **The operator, to resolve genuine forks.** Do not guess a fork. Default it in the doc with the trade-off stated, and flag it in chat.

If the load-bearing sources are missing or thin, say so to the operator and stop, rather than filling the document from plausible guesses.

---

## The two documents

Every section in both carries a source line.

**Architecture doc, the what and why.** Overview, product shape, architecture at a glance,
security posture, cost and ownership, stand-up or build, jobs to be done, growth, risks.

**System design, the engineering how.** Overview, requirements, high-level design, identity and
authorization, data model, API, credential and serving, records and cascade, governance and
audit, scale and reliability, trade-offs.

The fillable skeleton for each section, with what belongs in it and what does not, is in
`references/architecture-templates.md`. Read it before drafting the spine. Three altitude rules
are worth carrying without opening the file, because they are the ones that get violated:

- **Security** is posture in the architecture doc and engineering detail in the system design.
- **Cost** covers base infrastructure only. Note that usage grows with volume rather than
  inventing a scaling model for it.
- **Trade-offs** are where requirements and proposals part company. Requirements are sourced.
  Design choices are proposals, and each states what it traded and when to revisit.

---

## The build (workflow)

1. **Ingest the sources.** Read them in full. Name the authoritative one and write down the precedence.
2. **State the design system.** Name the brand system and the gates before building. Aleysian tokens from `_shared/aleysian-brand`, the brand and prose gates from `brand-renderer` and `prose-pass`.
3. **Resolve the frame.** If the authoritative source changed the frame (tenancy, scope, an approval gate, a name), rebuild on the new frame. Do not patch the old one.
4. **Draft the spine.** The sections, each with its source line. Get the whole outline sourced before writing prose.
5. **Write to Aleysian voice.** Prose, not slop. Design proposals framed as proposals with the trade-off stated.
6. **Build the HTML.** Reuse the Aleysian stylesheet and logos through placeholders (`{{STYLE}}`, `{{LOGO_WHITE_B64}}`, `{{MARK_COLOR_B64}}`), inject, and assert no placeholder remains.
7. **Run the gates.** Brand gate to zero failures. Prose gate (documents only) to exit 0. The rule most likely to trip is the balanced two-clause sentence (C1). Fix it by splitting the true two-clause sentences into sentences of unequal length; leave the serial-comma lists.
8. **Look at it.** Render and inspect. Parity: every substantive claim survived the render.
9. **Flag the forks.** Open decisions and gaps go to the operator in chat, never into the document.
10. **Deliver.** Present the file. If numbers changed, cascade them to the rest of the set.

---

## Failure patterns

- **A banner over stale text.** Reframing means a rebuild on the new frame, not a sticky note on the old one.
- **Gaps flagged inside the artifact.** Gaps go to chat. The document stays clean.
- **Invented numbers.** A plausible figure with no source is worse than naming the gap to the operator.
- **Mixing altitudes.** The architecture repeats the system design, or the system design re-argues the why. Keep them complementary.
- **Mirroring a source.** Reproducing a source's structure or wording. A source is input, not a template. Rewrite in Aleysian voice.
- **Skipping the gate.** Shipping with a brand failure or a prose fail.
- **House-voice defects.** Em dashes, spelled numbers, the section sign, emoji, forbidden words.
- **Stale frame residue.** Approval, tenancy, or a name carried from an old frame after the frame changed.

---

## Output format

One self-contained Aleysian-branded HTML document per altitude.

- **Hero.** The white logo, a kicker, the title, and a metadata row (owner, status, stack, and one more that fits the system).
- **Body.** An eyebrow per section, a systems-map diagram where it helps, tables for structured content, and a source line per section.
- **Footer.** The color mark, the brandline, and a rev line naming the sources and the date.
- **Source-line convention.** `Source: [named doc], section N` or `[decisions record], section N`. For a design proposal, `design proposal, consistent with [source]`.

**Gate commands** (paths from the installed skills):

```
python3 <brand-renderer>/scripts/brand_check.py FILE
python3 <prose-pass>/scripts/prose_check.py --config <prose-pass>/house.json FILE
```

Expect `PASS: 0 failure(s)` on the brand gate and exit 0 on the prose gate. The prose gate is for documents. A UI mock is not run through it, because its labels and fragments are correct for an interface and would read as prose defects.

---

## Release gates (before it ships)

- Every substantive claim has a source line.
- No gap-flags, no "TBD", no "to confirm" in the document. Gaps live in the operator's chat instead.
- Superseded framing removed, not annotated. Precedence honored.
- Brand gate: zero failures. Prose gate: exit 0.
- Parity: all substance survived the render, and a human or model looked at it.
- Numbers cascaded to the rest of the set.

---

## Reference files

- `references/architecture-templates.md`: the fillable skeletons for the architecture doc and the system design, the source-line convention, the systems-map and trade-offs patterns, the HTML build pattern, and the pre-ship checklist.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion, and
not something a reviewer does later. Full spec in
[`release-gate.md`](../_shared/release-gate.md).

1. Run prose-pass on the prose. It rewrites AI patterns and gates the result. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not present the artifact as finished until every check that applies has passed.
