---
name: deck-builder
description: "Build or repair a pitch, briefing or scope decision deck around the audience decision, supported claims and explanatory visuals. Preserve editable output and inspect the rendered slides."
---

## Choose the requested task

Use the primary workflow below unless the request matches a mode in this table. For a matching mode, read its complete linked workflow and required references, then produce that mode's output. Preserve its calculations, failure handling and acceptance checks. One request does not require every mode.

| Requested mode | Complete workflow |
| --- | --- |
| scope decision deck | [ddoc](_runtime/ddoc/WORKFLOW.md) |



# Deck Builder

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [`deck.md`](_runtime/prose-pass/references/registers/deck.md). Read both before drafting.**

Plan what the deck must explain before choosing layouts. Save the evidence and slide plan before rendering.
Each slide must answer an audience question through its content. A claim repeated
in several text boxes does not explain the claim.

This skill owns the narrative and information design. `brand-renderer` applies
the selected canonical [brand profile](references/estate/brand.md). Brand identity
does not determine the diagram or force a fixed slide composition. Writing review
comes from `writing-integrity`.

## When to use

- A proposal, pitch, technical briefing or reading deck.
- When a deck "feels sparse / awkward / off" and needs a structured rebuild.
- Apply the same reasoning to a requested slide repair; preserve its place in the wider argument.

## Project shape

Work inside whatever engagement folder the project uses. Resolve it, do not assume
one: ask, or take it from the path you were invoked in. The following files retain each stage:

```text
deck/
  00_brief.md          # the input: audience, decision, constraints
  01_one_message.md    # the single thesis (GATE 1)
  02_submessages.md    # supporting claims and evidence
  03_structure.md      # slide-by-slide plan
  04_copy.md           # real headline + body text per slide
  05_design_notes.md   # brand application notes (from brand-renderer)
  deck.(pptx|html)     # the build
  06_polish_todo.md    # output of the QA pass (GATE 2)
```

## Stage gates: do not skip, save before advancing

Read [Visual argument](references/visual-argument.md) before planning. Establish
whether the audience will hear a presenter or read the deck alone. A reading
edition must carry its own explanation. Preserve detailed evidence in the deck
or an appendix when the decision needs it.

### Gate 1: Main claim

Before any slides, reduce the deck to **one sentence the reader must remember.**

1. Name the audience and decision. Record their existing knowledge and supplied
   concerns. Do not invent emotional reactions.
2. Separate the *offer* from the *thesis*. A product/service name is not a message.
3. Write a direct claim tied to the decision and its evidence. For example:
   `Prove the nightly reconciliation on a complete batch before switching finance operations.`
   Use the actual decision; do not copy a rhetorical sentence pattern.
4. Reject any message that is a feature list, a vague benefit, a vendor-centered
   claim, or too broad to prove inside this deck.
5. The thesis record contains the message, why it's right, and what the deck
   should deliberately **not** try to say.

Do not advance until this sentence exists and is provable by the deck you're about to plan.

### Stage 2: Submessages

Identify the claims needed to support the thesis. Each needs evidence the deck
can show. Record a missing source before choosing a representation that requires
it. Do not invent financial benefits or measured results to populate a chart.

### Stage 3: Structure

The structure record gives each slide a role in the argument. Record the audience
question and supported takeaway. Identify its evidence, the relationship to show,
the proposed visual and why the next slide follows.
Cut any slide that only says "we will provide" or repeats a prior point.
Sketch the visual before fitting prose into a layout. A sequence diagram should
expose what each actor knows; a scope diagram should locate the boundary. The
plan is complete when every claim has an explanation and evidence.

### Stage 4: Copy

The copy record has the actual headline and body text for each slide. Name the action or behavior the slide explains. Remove a subtitle that repeats the headline. Keep headlines short, break body text at meaning units, and use consistent terms. **Run `prose-pass` on this** before it goes
into the build. Diagram labels may name an actor, state, field or transition concisely. Review their meaning and consistency; do not expand them into prose merely to satisfy sentence length. This does not exempt labels from writing review.

### Stage 5: Design + build

Invoke **`brand-renderer`** for the selected visual profile, then build the deck (`pptx`
skill for PowerPoint, or HTML/CSS if a browser-previewable / diffable deck is
wanted). Capture any brand-application notes in `05_design_notes.md`. Never bake
real body text into images.

The bundled HTML route is documented in [HTML production](references/html-production.md). It creates editable text, applies the selected profile, and supports PDF export. For PowerPoint, use an available presentation tool and keep its editable source. Never rename an HTML file to `.pptx`.

Use a renderer that can express the selected visual. Route unsupported chart
types or annotated screenshots to an available plotting or presentation tool.
Never silently replace a diagram with numbered prose because the bundled
renderer lacks the required form. Keep the source data with the visual.

### Gate 2: Review the finished deck

Run the QA checklist below against the built deck, then record each recurring fix in the project
copy of `polish-learnings.md` so the next deck's first build avoids it.

1. **Read `polish-learnings.md` first** and apply it as a pre-checklist.
2. Walk the checklist:
   - **Argument:** every slide supports the one message; no orphan slides; chapter/section labels match the structure.
   - **Explanation:** answer each storyboard question from the finished slide. Identify the actual element that supplies the answer. Check that arrows and branches have defined meanings. A populated field does not prove that a reader can understand the relationship.
   - **Text:** headlines short; no awkward orphan line; key text bold enough; terms unified; ran through `prose-pass`.
   - **Layout:** no clipping or label collisions. Preserve evidence when adjusting density. Empty space does not require an extra card; use the space the explanation needs.
   - **Icons/images:** visual center aligned to its background shape; assets not blurry, cropped, or too small.
   - **Thumbnail test:** inspect the argument's progression and visual hierarchy. Read detailed diagrams at delivery size; thumbnails cannot validate their labels.
   - **Export:** PDF/PNG export does not break layout.
3. Write `06_polish_todo.md`: critical fixes, nice-to-haves, and exact locations
   (slide #, CSS selector) to edit.
4. Append any fix that recurs to the project learning record. Include the slide and repair.
   Propose changes to the canonical skill through estate maintenance; an installed package
   stays immutable so that its source and deployed hashes remain consistent.

## Rules

- One artifact per stage, saved before advancing. No skipping straight to the build.
- Process lives here; brand lives in `brand-renderer`; writing review follows `writing-integrity`.
- If a brief is thin, record assumptions and identify missing evidence. Continue the supported work; keep proposed behavior distinct from observed results.

## Release gate (required)

Run the release checks before delivery. The complete requirements are in
[`release-gate.md`](_shared/release-gate.md).

1. Apply writing-integrity to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run quality-gate before you call it final.

Do not present the artifact as finished until every check that applies has passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
