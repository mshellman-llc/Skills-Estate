# Durable AI tell catalog

The patterns that don't decay. Word and phrase lists live exclusively in `scripts/rewrite_scan.py`. That dated, swappable data changes as lexical tells fade. This file covers what regexes cannot catch and what persists across model generations.

These patterns govern all authored language. Apply them to conversation, reviews,
tickets, code comments, UI copy, skills, internal notes, and narrative artifacts. Preserve exact captured evidence and required syntax. Authored text inside logs, structured data, or quotes still receives the full review.
Short text can still carry a hard tell; density rules need enough text to measure.

Two evidence notes shape how to apply it. Expert human judgment with a checklist is the most accurate AI-detection method known. A panel of frequent LLM users misclassified 1 of 300 articles in ACL 2025 testing, beating every automated detector. The scanner provides counts; you provide that judgment. No single sign is proof because every pattern here also occurs in human writing. Density and co-occurrence are the signal.

## Structural

- Uniform paragraph length and symmetrical organization; predictable flow. Human structure is lumpy.
- List-like enumeration: bullet-heavy sections that should be prose. Bullets only for genuinely list-like content.
- Inline-header lists: bullets where each item opens with a bold header restating itself. Strip the header, write the point.
- Formulaic openings such as `In the rapidly evolving world of...`: lead with the news or insight.
- Sections that close by restating themselves: a mini-summary or call-to-action repeating what was just said. Cut.
- Parallel gerund openers: consecutive sentences starting with present participles such as `Leveraging X... Building on that... Recognizing the need...`. Vary the starts.
- Formatting tells (scanner counts these): em-dash density, bold overuse (one bolded phrase per major section, max), emoji in headers, title-case subheadings (use sentence case).

## Sentence rhythm

- Uniform complexity and similar lengths throughout create low burstiness. Mix 3-5 word sentences with 25+ word ones; use fragments where the voice does.
- Suspiciously clean grammar: no fragments, no run-ons, ever.
- `It's not X — it's Y` is negative parallelism. Editors and platform classifiers target it as a reliable tell. Rewrite as a direct positive statement. Max one per piece.
- Compulsive rule of three: every list has exactly three items, every description three adjectives. Use two, four, or a sentence. Max one triad per piece.

## Lexical judgment (beyond the scanner's lists)

- **Synonym cycling**: rotating "developers... engineers... practitioners... builders" to avoid repetition. Repeat the clearest word.
- **Copula avoidance**: `serves as`, `boasts`, `represents`, and `features` replace `is` and `has`. Default to is or has unless a specific verb adds meaning.
- **Quiet-riser density**: "significant," "notable," "potential," "findings," "crucial" are each fine alone and still climbing in LLM output. Three in a paragraph: rewrite the paragraph.
- **Template phrases**: slot-fill constructions ("a [adjective] step towards [adjective] infrastructure"). Describe the specific capability or outcome.

## Voice

- Emotional flatness, balanced phrasing, no subjective markers, constant confidence level.
- Emotional flatline: `What surprised me most` and `I was fascinated to discover` are filler wearing an emotion costume. If you claim an emotion, the surrounding writing must earn it; otherwise present the thing directly.

## Rhetorical

- Meta-signposting ("here's the thing," "the key is"), rhetorical question + immediate answer, false binaries, over-explaining.
- **Significance inflation**: delete clauses such as `marking a pivotal moment in the evolution of...` when the sentence works without them.
- **Stakes inflation**: ordinary friction escalated to existential crisis. Test for severity language with no anchoring number. Name the impact, such as deals lost or cycle time. Significance inflation puffs importance. Stakes inflation manufactures threat.
- **Audience indictment**: the reader is positioned as failing before the solution arrives. Examples include `What most companies get wrong about X` and `leaving money on the table`. State the problem as a condition with a fact attached.
- **False balance**: "While challenges exist, the opportunities far outweigh them." Take the position.
- **Too-polished quotes**: "As one stakeholder noted, 'This solution transformed our ability to...'" Real quotes have texture. Use a real one or none.
- **Superficial -ing analyses**: trailing participle strings as pseudo-analysis ("symbolizing the region's commitment, reflecting decades of investment"). Replace with facts or cut.
- **False ranges**: unrelated extremes for fake breadth, such as `from the Big Bang to dark matter`. List actual topics. This contested signal is the weakest tell in the catalog, so flag only blatant cases.
- **Promotional language**: tourism-brochure prose. If you wouldn't say it in conversation, cut it.
- **Vague attributions**: "Experts believe," "Studies show" without a named source. Cite specifically or drop.
- **Notability name-dropping**: prestige citations piled up to manufacture credibility. One specific reference with context beats four name-drops.

## AI-correction artifacts

Fingerprints left by an editor managing AI output rather than patterns AI wrote: sentences that exist to explain, justify, or hedge corrected content. The test: would a person writing from scratch have included this sentence? The scanner greps all four classes; fixes here.

- **Class A, scope callouts**: cut `This document covers...` and `This is not an exhaustive guide...`. Scope should be evident from content.
- **Class B, cross-reference callouts**: cut `As mentioned above...` and `Refer to X for more details...` unless they navigate a non-obvious location in a long document. Write a bridge sentence when the connection needs explanation.
- **Class C, correction hedging**: cut `It's important to clarify...`, `Results may vary...`, and `In most cases...`. Name any genuine exception.
- **Class D, editorial framing**: cut `To provide context...`, `With that in mind...`, and `Building on the above...`. Connect the sentences directly or fix the paragraph order.

## Repeated framing candidates (C24)

`C24-formulaic-the-framing` reports recurring “The + noun” labels and prose
announcements as `WARN` candidates. Two distinct anchored frames, or three
distinct short labels, trigger a document-level review. Repeated copies of one
stable name do not trigger it. Anchors help identify vague framing in prose;
they are not banned words. Three short labels can trigger with unfamiliar nouns.

The detector reads extracted authored text from the existing input adapters.
Its sample line numbers refer to that extracted text, not original slide or
source coordinates. Quotes, code formatting and internal file names do not
disable review. The scanner never changes those spans. Preserve exact evidence,
identifiers, meaningful names and deliberate repetition when reviewing a match.
An intentional set such as “The Witness,” “The Messenger” and “The Keeper” can
match when presented as standalone labels. That needs a contextual decision,
not forced renaming. A clean result can miss long labels and unfamiliar prose
frames. The broader Writing Integrity review still applies.

New prose receipts identify the checker code and configuration. A retained C24
assessment requires that fingerprint as well as the artifact hash, reason and
source reference. A changed checker requires renewed review. Older installed
validators cannot gain this capability from a new receipt alone; migrate the
whole scanner, receipt and review-deliverable dependency chain together.

## Word choice (scanner-enforced: C18-C21, C23)

- **Copula avoidance** (C18): `serves as` and `stands as` replace is or are. Keep another verb only when it adds meaning.
- **Gravity markers** (C19): `the honest answer`, `worth flagging`, `the full picture`, `the cleanup story`, `make no mistake`, and `at its core` assert importance without evidence. Name what breaks or state the fact. `load-bearing` remains an allowed house term.
- **Dig or dive** (C20): replace `dig into`, `dive into`, and `deep dive` with the object being examined.
- **Vague hedge verbs** (C21): replace `appears to` and `seems to` with a direct statement or named uncertainty. `what good looks like` remains an allowed fixed idiom.
- **Trailing hedge adverbs** (C23): cut sentences ending in `regardless.`, `nonetheless.`, or `nevertheless.`.

## Headings (judgment, not scanner-enforced)

The house uses colon headings deliberately ("Gating: run the checker"), so this stays judgment rather than a hard rule.

- Use a short topic heading when the reader needs a label. Keep an action-oriented or sentence-shaped heading when it helps the reader perform a real task; verbs alone do not create urgency. Preserve required headings and genuine deadlines or approval conditions.
- Avoid "Topic: clause" where the clause is an explanation. Move the explanation into the body.
- Sentence case, not title case.

## PR and review prose (register: registers/pr-review.md)

- Active voice. Not "X is added" but "Adds X". Commit subjects take the imperative: "Add X".
- Not "Tests cover X" but "Added tests covering X".
- No test counts, pass/fail tallies, or CI status. Describe what the tests cover.
- No "X, not Y" contrast (C2 already flags the parallel form). State the positive directly.
- Apply C23 to sentence endings.

## Outbound email and messages (register: registers/email-slack.md)

- No punchy journalistic cadence: dramatic one-sentence paragraphs, a rhetorical question then its answer ("The result? X."), or escalating triads.
- Match the sender's plain voice. A message that could go to any recipient unchanged is filler.

## Contextual repetition and urgency

Review prose beside tables, charts and lists for information it adds. Remove
mere readouts when the display already serves the reader; retain interpretation,
useful summaries, qualifications and accessible alternatives. Review headings
and calls to action for an actual task, requirement or consequence. Preserve real
deadlines and approval conditions; do not invent pressure or new prerequisites.
Across the piece, remove repeated assurances of the same fact unless they add
new verification, a changed condition or a needed reminder. Keep valid uses of
“holds,” “unchanged” and similar wording. These judgments require the surrounding
content and sources. [C25–C27](context-signals.md) surface narrow review candidates;
they do not automate these judgments. Apply the full
[Writing Integrity guidance](../../../references/patterns.md#repetition-and-urgency).
