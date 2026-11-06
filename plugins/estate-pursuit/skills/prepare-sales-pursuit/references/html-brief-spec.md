# HTML brief specification

`assets/brief-template.html` is a working shell. The CSS and JavaScript are complete and tested — you are filling in content, not rebuilding mechanics.

Copy it to a working file, fill the `{{SLOTS}}` and the five JavaScript registries, then run:

```bash
python scripts/build_brief.py draft.html -o "Client-call-brief.html" --verify
```

The build script inlines the fonts, logo, and background as base64, converts `<i data-lucide>` markup to inline SVG, and renders the result headlessly to catch unfilled slots, dangling footnotes, and console errors.

---

## The five JavaScript registries

Everything dynamic renders from these. Fill them and the sections build themselves.

The registry examples below describe an invented community workshop, with fictional sources and values. Never use them as evidence for a live client.

### `FN` — footnotes

```js
const FN = {
  t1: ["Synthetic registration interview",
       "Invented source SYNTH-T1, 2030-01-11, excerpt 00:02:00 to 00:05:00.", ""],
  register: ["Synthetic workshop register",
             "Invented signed register, 2030-01-12; 40 places across two sessions.", ""],
};
```

`[title, detail, url]`. The URL may be empty for internal sources with no link. Every `<button class="fn" data-fn="KEY">` needs a matching key — the verifier catches misses.

Reuse keys freely. The same source cited fifteen times uses one key fifteen times; the visible chip number is just a label.

Write the detail field so someone can re-find the source cold: timestamps, document IDs, transcript coverage ranges, filing dates. "Slack" is not a citation.

### `FLOW` — the money flow explorer

```js
const FLOW = {
  rev: { t: "Synthetic workshop fees · $800",
         b: ["<b>Who pays:</b> attendees book a place directly with the coordinator.",
             "<b>Payment rule:</b> this fictional example charges $20 for each of 40 places."] },
};
```

Keys match the `data-flow` attribute on each `.fnode` button. HTML is allowed in the bullets — bold the load-bearing phrase.

Six to eight nodes works well: revenue streams (one per segment or channel), pricing mechanics, program or deal lifecycle, working capital, legal entities, cash out. Put assumptions in the bullets where they belong rather than hiding them in the register only.

### `QS` — discovery questions

```js
const QS = [
  ["T1", "When is a place reserved?",
   "Does submitting a form reserve a place, or does the coordinator confirm it later?",
   "This separates the request from the actual booking decision."],
];
```

`[tier, short title, the question as spoken, why it matters]`. Tiers `T1` through `T4`; headings and the progress counter render automatically. Keep them in tier order.

Write the third field as something a person can actually say out loud. A seller can read your sentence. They cannot read your bullet.

### `ASM` — the assumptions register

```js
const ASM = [
  ["A-01", "Submitting a form reserves a place", "Low",
   "No. The synthetic interview does not establish reservation behavior."],
];
```

`[id, assumption, confidence, verdict]`. Verdicts starting "No" render red, "Yes" render teal — that colour cue is what a seller scans under pressure, so phrase the verdict so its first word carries the meaning.

Mirror `10-assumptions-register.md` exactly. Two sources of truth that drift is worse than one.

### `DRILL` — rapid recall cards

```js
const DRILL = [
  ["What needs verification before recommending an automatic booking flow?",
   "Confirm <b>who reserves the place</b> and what the attendee sees when a session is full."],
];
```

`[question, answer html]`. Aim for twenty.

This is the most-used feature in the artifact — it converts a document into practice. Do not skimp on it, and do not write cards that only test recall of trivia. The good ones make someone rehearse the sentence they will actually say: the differentiated facts, the reframes, the numbers they will be asked for, and the topics to avoid.

---

## Section order, and why

The sequence is deliberate. Someone reads top-down under time pressure and should be able to stop at any point and still be more useful than when they started.

1. **Hero** — the situation in one sentence. Not a company description, what is *going on*.
2. **60-second brief** — differentiated facts first, then the one message, then the wedge. If someone reads only this, they can hold the room.
3. **The room** — people, with a "how to reach them" on each. The read is the point; biography is context.
4. **Company** — KPIs, segments, and a "what they can say yes to" card covering covenants, cash, and approval friction. Sellers consistently forget that deal shape is constrained by the client's balance sheet, not their appetite.
5. **Money flow** — the interactive explorer. This is what separates a partner who read the filings from one who read the website.
6. **The problem** — verbatim client quotes.
7. **Competition** — per-competitor cards, head-to-head table, where we are exposed.
8. **Product context** — accordions, honest about risk.
9. **Talk track** — time-boxed, copyable lines, phasing, next steps.
10. **Questions** — from `QS`.
11. **Landmines** — short and blunt.
12. **Assumptions** — from `ASM`, plus commonly-misstated facts and unverified gaps.

Reorder if a pursuit genuinely demands it. Do not drop the assumptions section or the landmines — those are what make the brief trustworthy rather than merely confident.

---

## Content patterns that carry weight

**The `.reach` box.** Every fact card in the 60-second brief should end with one. A fact without a move is trivia. The label says what kind of move it is — "Use it as one question", "Validate first, then reframe", "Let him say it" — and the body is the exact words.

**Verbatim quotes with `<cite>`.** Their language, not your summary. This is the single easiest way to make a brief feel researched rather than generated.

**Fair treatment of competitors.** Give each one a genuine strengths paragraph. A brief that only lists weaknesses reads as spin and gets discounted wholesale, including the parts that are right.

**Conflict callouts.** Where sources disagree, use a `.asm` block to show both and say which to use. Costs three lines, prevents a bad number reaching a client.

**Tension you do not resolve.** When the research surfaces a real fork — lead with the painful business unit or the profitable one, pain story or P&L story — say so in a `.asm` block and give the reasoning both ways. The seller knows things about this account you do not.

---

## Brand constraints

Use **brand-renderer** with the caller's explicitly selected project profile. Without one, keep the neutral profile. The reusable template supplies no employer identity, logo, palette or mandatory font. Do not search personal folders for brand assets.

- Use the resolved profile's CSS variables; do not insert a remembered company palette.
- Embed only declared, accessible assets. Missing required assets block branded output.
- Keep text left-aligned where readability requires it and preserve generous whitespace.
- Review writing with review-writing. Apply author-specific preferences only from a confirmed supplied profile.
- Preserve accessible controls, readable contrast and a consistent icon style.

---

## Verification

Always run `--verify`. The script checks for unfilled slots, footnote chips pointing at nonexistent `FN` keys, whether the font actually loaded, whether the drill deck is thin, and whether every interaction still works after your edits. It writes a screenshot next to the output.

Look at the screenshot. Rendering bugs are invisible in source and obvious in a picture.

Two failure modes worth watching for specifically:

**A CDN sneaking back in.** If you hand-edit and reintroduce a `<script src="https://…">`, the brief breaks offline — which is exactly when it gets opened. The build script strips the Lucide CDN tag, but any other external reference is on you.

**Registry and markdown drift.** The `ASM` array and `10-assumptions-register.md` must agree. When you revise one, revise both.
