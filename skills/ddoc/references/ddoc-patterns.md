# DDOC patterns

Both skeletons and the manifest schema.

## Manifest shape

```json
{
  "mode": "decision | confirmation",
  "client": "Client name",
  "title": "Deck title, carries the point",
  "date": "YYYY-MM-DD",
  "quote_number": "SYNTHETIC-001",
  "quote_snapshot": {"quote.total_fixed_fee": 24000},
  "options": [
    {"name": "Tier 2", "recommended": true, "duration": "4 weeks",
     "summary": ["One sentence per line.", "Specific to this option."]}
  ],
  "figures": [
    {"label": "Tier 2 investment", "value": 24000, "quote_field": "quote.total_fixed_fee"}
  ],
  "slides": [ ... ]
}
```

Every figure maps to a named quote field and its exact source value in
`quote_snapshot`. The builder rejects missing or conflicting source values.
Reconcile every displayed price, hour, duration, and count during content review;
the explicit figure list does not automatically extract all numbers from prose.
The mapping accompanies the deck as an audit table.

## Slide kinds

| kind | Shape |
|---|---|
| `heard` | `items: [{text, evidence, source}]`. Only `client_stated` renders |
| `comparison` | Rendered from `options`. No body content of its own |
| `option_block` | `option` plus `sections: {"Label": ["sentence."]}`. Identical section keys across every option |
| everything else | `title`, optional `subtitle`, `bullets`, optional `callout`, optional `notes` |

## Decision mode skeleton

Required slides are enforced by the builder. Departures from the reference order
produce a warning and require a deliberate content review.

1. `heard` · what we heard, in their words
2. `recommendation` · what we recommend and why, up front
3. `comparison` · options side by side, one screen, three columns maximum
4. `option_block` · one per option, identical skeleton
5. `outside_all` · what sits outside every option
6. `need_from_you` · what we need from you
7. `decision` · decision and next step, with a date

## Confirmation mode skeleton

1. `heard`
2. `recommendation`
3. `outcomes` · what you get, as outcomes
4. `scope_in`
5. `scope_out` · each exclusion routed to a paid next step
6. `assumptions`
7. `timeline`
8. `team`
9. `need_from_you`
10. `investment`
11. `confirm`

Optional twelfth slide when the client is price-anchoring: what we deliberately left out and
why. Name the excluded lower-cost option and the reason it does not meet the confirmed
requirements. Keep that explanation tied to evidence.

**Why slides 9 and 11 are load-bearing here.** Decision mode has built-in tension: the client
must choose. Confirmation mode has none, so the check has to be manufactured. Slide 9 gives
the client something to react to, and their reaction is what reveals whether the assumptions
on slide 6 are real. A confirmation-mode DDOC that skips slide 9 is a proposal with a
different cover.

A combined `scope` slide can replace `scope_in` and `scope_out` when it contains
both lists. A `deliverables` slide can express the required outcomes through
named outputs. The builder accepts these compact forms while retaining timeline,
team, assumptions, client inputs, investment, and the confirmation action.

## Structural rules, both modes

- **Lead with the recommendation.** A firm presenting three equal options is telling the
  client it does not know their business. Recommend one; present the others as legitimate
  bounded alternatives with the tradeoff named honestly.
- **Three options maximum.** Four is a catalog and catalogs get deferred.
- **Identical geometry.** Same layout, same section order, same word-count band per option.
  The builder warns past a 1.4x spread, because volume reads as effort rather than scope.
- **One deck.** Separate decks per option destroy the contrast, drift in structure, and leave
  the client holding three versions with no single thing they approved.

## Failure modes

The ones that recur.

| Failure | What it looks like | Fix |
|---|---|---|
| Fragment over-correction | "$87,900, firm. This is the SOW." | One complete sentence naming the fee and where the detail lives |
| Gimmick header | "Wear math, automated" | State the point plainly |
| Label header | "Overview", "Our Approach" | Carry the slide's actual point |
| Colon tic | "Outcome: improved visibility" repeated down the slide | Rewrite as sentences |
| Slot-fill symmetry | "Everything in Tier 1, plus X" across three cards | Write each card for what it does |
| Line budget overflow | A support line wrapping to a third line | Cut words, preserve the sentence |
| Figure drift | Slide says one number, quote says another | Blocking finding. Flag it, adjust neither side |
| Missing recommendation | Three options presented as equals | Mark one recommended and say why |
| Unattributed heard slide | Statements the client never made | Evidence class per item, only client_stated renders |
