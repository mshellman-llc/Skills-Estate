---
name: deck-builder
description: 'Stage-gated production of a multi-slide proposal, pitch, or sales deck from a brief to a finished deck: a one-message gate up front to lock the argument, then an accumulating polish-review loop at the end. Use when building a multi-slide deck and you want discipline plus a self-improving final QA pass. Defers all brand, color, and visual decisions to brand-renderer and the final copy pass to prose-pass. Do NOT use for the specific Aleysian Deal Decision deck presented before the proposal (that is ddoc) or an interactive HTML proposal page (that is interactive-proposal).'
---

# Deck Builder

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`deck.md`](../prose-pass/references/registers/deck.md). Inputs, not a final pass.**

Build a deck the way you'd build software: lock the argument and structure before
touching design, save an artifact at each stage, and run a fixed QA pass that
gets smarter every time.

This skill owns **process**. It does not own brand. All color, type, logo, and
layout decisions come from `brand-renderer`, which reads the tokens in
`_shared/aleysian-brand`. The final copy pass comes from
`prose-pass`. Do not invent a visual system here.

## When to use

- Any proposal, pitch, or client deck with more than ~5 slides.
- When a deck "feels sparse / awkward / off" and needs a structured rebuild.
- Not for a one-off single slide. Use `brand-renderer` directly.

## Project shape

Work inside whatever engagement folder the project uses. Resolve it, do not assume
one: ask, or take it from the path you were invoked in. Save one artifact per stage:

```text
deck/
  00_brief.md          # the input: audience, decision, constraints
  01_one_message.md    # the single thesis (GATE 1)
  02_submessages.md    # 3–6 supporting claims
  03_structure.md      # slide-by-slide plan
  04_copy.md           # real headline + body text per slide
  05_design_notes.md   # brand application notes (from brand-renderer)
  deck.(pptx|html)     # the build
  06_polish_todo.md    # output of the QA pass (GATE 2)
```

## Stage gates: do not skip, save before advancing

### GATE 1: One message (the most important step)

Before any slides, reduce the deck to **one sentence the reader must remember.**

1. Name the decision context: who reads this, what they must decide, what their
   anxiety is.
2. Separate the *offer* from the *thesis*. A product/service name is not a message.
3. Write one sentence in one of these shapes:
   - `X is not just A; it is B that enables C.`
   - `Start with X to achieve Y and prepare for Z.`
4. Reject any message that is a feature list, a vague benefit, a vendor-centered
   claim, or too broad to prove inside this deck.
5. Save to `01_one_message.md`: the message, why it's right, and what the deck
   should deliberately **not** try to say.

Do not advance until this sentence exists and is provable by the deck you're about to plan.

### Stage 2: Submessages

3–6 claims that, together, prove the one message. Each must be defensible with
evidence the deck can actually show. Save to `02_submessages.md`.

### Stage 3: Structure

Slide-by-slide plan. Fewest slides that prove the message. For each slide:
title, role in the argument, primary visual type, required copy, evidence.
Cut any slide that only says "we will provide" or repeats a prior point.
Save to `03_structure.md`.

### Stage 4: Copy

Real headlines and body text per slide. Short headlines, body broken at meaning
units, terms unified. Save to `04_copy.md`. **Run `prose-pass` on this** before it goes
into the build.

### Stage 5: Design + build

Invoke **`brand-renderer`** for the brand system, then build the deck (`pptx`
skill for PowerPoint, or HTML/CSS if a browser-previewable / diffable deck is
wanted). Capture any brand-application notes in `05_design_notes.md`. Never bake
real body text into images.

### GATE 2: Polish review (the self-improving step)

Run the QA checklist below against the built deck, then **append every new
recurring fix to `polish-learnings.md`** so the next deck's first build avoids it.

1. **Read `polish-learnings.md` first** and apply it as a pre-checklist.
2. Walk the checklist:
   - **Argument:** every slide supports the one message; no orphan slides; chapter/section labels match the structure.
   - **Text:** headlines short; no awkward orphan line; key text bold enough; terms unified; ran through `prose-pass`.
   - **Layout:** no right/bottom clipping; cards aligned; no giant empty whitespace (fill with a diagram, criteria, or next-step cards, not decoration); banners/callouts centered.
   - **Icons/images:** visual center aligned to its background shape; assets not blurry, cropped, or too small.
   - **Thumbnail test:** each slide must be understandable at thumbnail size; if not, strengthen hierarchy.
   - **Export:** PDF/PNG export does not break layout.
3. Write `06_polish_todo.md`: critical fixes, nice-to-haves, and exact locations
   (slide #, CSS selector) to edit.
4. **Append any fix you made more than once to `polish-learnings.md`.** This is
   what makes the next deck start cleaner. Treat it like memory.

## Rules

- One artifact per stage, saved before advancing. No skipping straight to the build.
- Process lives here; brand lives in `brand-renderer`; copy quality lives in `prose-pass`.
- If a brief is thin, place assumptions in `00_brief.md` and keep moving, don't stall.

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
