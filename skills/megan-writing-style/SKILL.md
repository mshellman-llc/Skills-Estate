---
name: "megan-writing-style"
description: "Use when drafting or editing prose in Megan's own voice — portfolio, About, bio, case studies, cover letters, LinkedIn, or emails she sends as herself. Enforces her anti-slop rules."
---


# Megan's writing style

Megan writes plain, direct, and specific. She would rather under-explain and trust the reader than restate a point. Draft in this voice, and check every draft against the rules below before showing it to her.

## Hard rules (she has called these out by name)

1. **Trust the reader to infer.** Never restate a point you just made. Never add a sentence that explains what the previous sentence meant — e.g. cut "That's the same standard I bring to a client's system."
2. **No empty "builder" constructions.** Don't write "I build systems that make expert work repeatable" or "...the pipelines and tooling that do the work." Name the actual thing: "a deal-intelligence engine, a discovery-to-scope pipeline, 42 AI skills."
3. **No X-not-Y antithesis.** Not "grounded in evidence, not opinion," not "systems, not slideware," not "deprecate deliberately, not delete." State the positive directly.
4. **No origin-story throat-clearing.** Skip "what's stayed constant since a college classroom..." openers. One plain personal line is fine; varnish is not.
5. **Banned phrases:** "at the intersection of," "my work sits where...," "proven ability to," "my career spans," "demonstrating my ability to," "whether it's [X] or [Y]," "at the end of the day," "what's stayed consistent/constant," "the [X] thing that matters," and anything that overstates or reiterates.
6. **No defensive disclaimers. Evidence controls stay internal.** Her ledgers, program records, and evidence notes track what is verified, estimated, or not proven. None of that goes into what she sends or publishes. In her own copy, state what happened with confidence and leave out what isn't supported. Accuracy comes from which claims you choose, not from disclaiming the ones you didn't make.
   - Never write: "not verified," "unverified," "not claimed," "I don't claim," "I do not claim," "does not prove," "directional," "not a controlled study/benchmark," "product-state counts, not adoption," "Where it stood," "remained outside that release," "no sold deal was recorded," "the outcome was not verified," or any sentence explaining what a number is not.
   - No state notes, provenance banners, or "saved locally / not published" lines inside the copy.
   - A qualifier survives only as part of the fact, in a word: "an estimated $660K–$1.07M," "lost," a date. Never a separate sentence about it, never a closing caveat.
   - If a claim only works with a caveat sentence attached, cut it or restate the true thing plainly ("I built it; it passes 184 tests." and stop).
   - Why: these endings make her sound unsure and devalue her immediately. Senior people state what they did.

## Extended tells (research-backed — same standard, applied harder)

7. **Overused AI vocabulary — swap for plain words:** delve, tapestry, realm, landscape, navigate, leverage, robust, seamless / seamlessly, resonate, underscore, testament, pivotal, intricate, meticulous, vibrant, boast, embark, comprehensive, vital, elevate, unlock, harness, foster, streamline.
8. **Signpost / transition filler:** "It's important to note," "Moreover," "Furthermore," "Notably," "Importantly," "That said," "In today's [X] landscape." Cut it or use a plain connective.
9. **Inflated mission-statement sentences:** "X isn't just Y, it's Z," "not a tool, a revolution." (The "isn't just… it's…" inflation is the tell; also covered by rule 3.)
10. **Colon or question drumroll:** "The best part? …" / "The result: …" as manufactured suspense. Just say it.
11. **Fragment-stacking for effect:** "Short. Isolated. Profound." One fragment is a choice; three is a tic.
12. **Comma piles / rule-of-three padded for rhythm:** three-or-more items strung for cadence, or a feature pile like "history, evidence, decisions, patterns, and visibility." Use the true count; each item genuinely distinct.
13. **Sentences that say nothing:** sweeping or emotional lines with no real noun, number, or named thing.
14. **Hollow intensifiers:** seamlessly, effortlessly, significantly, truly, incredibly, deeply. Delete or make concrete.
15. **Flattery / reassurance asides:** "You're not imagining it," "Great question."
16. **Trailing significance clauses:** "..., highlighting the need for X," "..., ensuring alignment." End the sentence at the fact.

## What good looks like

- Concrete nouns, real numbers, named systems. Every sentence carries a specific.
- Short sentences mixed with long. Rough edges are fine.
- A three-item list only when the three items are genuinely distinct (assess / scope / decide), never for rhythm.
- Em dashes are fine — she has said the em dash isn't the problem; the empty phrase around it is. (Em-dash-as-AI is an unreliable signal; don't strip them.)
- Domain terms are fine — CPQ, idempotent, canonical, lead-to-cash, RCA.
- End flat and confident on the last true thing, not on an aphorism and not on a caveat.

## Process

This is Megan's personal voice, first person. She works independently; no employer or house voice applies. A client's voice applies only to copy written for that client, and only from a confirmed profile in `client-brand`.

When she flags a draft as slop, fix it and don't reproduce the same pattern elsewhere in the piece. Before handing back any draft, scan it for the rule 6 phrases and remove every hit by restating or cutting the claim. If a proof gap matters, tell Megan in chat; do not write it into the draft.

Where the scanner is installed (Claude Code or Codex on her machine), run it on the finished file as a catch-net for a whole document:

```bash
/usr/bin/python3 ~/.agents/humanize/tellscan.py scan <file> --profile megan
```

It enforces rules 2, 3, 5 and 6 as hard rules and leaves em dashes and domain terms alone. Judge by these rules, not the linter. On surfaces without it, check the rules by reading and do not claim a scan ran. When she corrects a new habit, record it with `tellscan.py learn "<phrase>" --repair "<fix>" --scope megan` where the scanner exists.

General structure and protected-meaning rules come from `writing-integrity`. The canonical workspace rule is "Internal records vs reader-facing copy" in `/Volumes/BeastMode/AGENTS.md`.

Sources for the extended tells: Reuters Institute, "How AI-generated prose diverges from human writing"; PlusAI, "The most overused ChatGPT words"; Reinhart et al., PNAS 2025; Wikipedia, "Signs of AI writing."