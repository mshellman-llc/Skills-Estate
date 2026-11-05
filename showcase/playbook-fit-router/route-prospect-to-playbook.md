---
skill: playbook-fit-router
title: Routing a distributor prospect to the right playbook from call notes
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 190748cd28c50baad5b6260742889081c1effa47bbc8025ab5073a3d12476bbe
---

## Request

I've pasted my notes from the first call with Harbourview Foods and our three current playbook qualifiers. Which playbook fits, and what do I still need to find out on the next call?

## Inputs

Run of the built `offering-fit` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `run.json`, `signals.json`.

#### discovery-notes.md

#### Harbourview Foods, discovery call 1, 2026-10-28

Attendees: Priya Raman (Head of Sales Operations, Harbourview), Tom Beck (our AE). My own notes, no recording.

**What Priya said**
- Harbourview uses Salesforce CPQ in production. Quotes go to about 40 distributors.
- Discounts need manual discount approval, done by email. "Some quotes sit for days waiting on a yes."
- They keep two price books: one for the US, one in CAD for Canada.
- Priya owns the CPQ configuration herself.
- No plans to replace CPQ.
- Service Cloud and case routing work is out of scope for this year. The support team is handled separately.

**My read (not confirmed with the client)**
- Reps probably do manual pricing in spreadsheets before quoting. Tom believes this from a past deal.
- Tom thinks the CFO, Marcus Odell, will sponsor. Nobody has spoken to him.
- Distributor accounts are likely duplicate accounts between their ERP and Salesforce. No one mentioned it. I'm guessing from the size of the distributor base.

**Not covered**
- How long a quote takes today, in numbers.
- Budget, timeline, sponsor.

#### qualifiers.md

#### Current playbook qualifiers (JSON twins, one file each in the project's qualifier folder)

q2c-01.json
```json
{"playbook_code":"Q2C-01","playbook_name":"Quote-to-cash on Salesforce CPQ",
"tags":{"systems":["salesforce cpq","price book"],"pain":["discount approval","manual pricing","quoting","quote approval"]},
"gates":[{"id":"q2c-g1","question":"Salesforce CPQ licensed and in use?","pass_on":"yes"},
{"id":"q2c-g2","question":"Named sales ops owner?","pass_on":"yes"},
{"id":"q2c-g3","question":"Client quantified quote cycle time?","pass_on":"yes"},
{"id":"q2c-g4","question":"Executive sponsor confirmed?","pass_on":"yes"},
{"id":"q2c-g5","question":"Staying on CPQ (no replacement planned)?","pass_on":"yes"}],
"tiers":[{"name":"Focused","signals":["one price book"]},{"name":"Extended","signals":["two price books","regional approvers"]}],
"disqualifiers":[{"condition":"no salesforce licence","route_to":"paid scoping"}]}
```

svc-02.json
```json
{"playbook_code":"SVC-02","playbook_name":"Service Cloud case routing",
"tags":{"systems":["service cloud","omni-channel"],"pain":["case routing","backlog"]},
"gates":[{"id":"svc-g1","question":"Service Cloud licensed?","pass_on":"yes"},
{"id":"svc-g2","question":"Support lead named?","pass_on":"yes"},
{"id":"svc-g3","question":"Case volume stated by client?","pass_on":"yes"},
{"id":"svc-g4","question":"Sponsor confirmed?","pass_on":"yes"},
{"id":"svc-g5","question":"Work funded this year?","pass_on":"yes"}],
"tiers":[{"name":"Core","signals":["one queue"]},{"name":"Multi-channel","signals":["omni-channel"]}],
"disqualifiers":[{"condition":"no salesforce licence","route_to":"paid scoping"}]}
```

dat-03.json
```json
{"playbook_code":"DAT-03","playbook_name":"Account unification on Data Cloud",
"tags":{"systems":["data cloud","erp"],"pain":["duplicate accounts","identity resolution"]},
"gates":[{"id":"dat-g1","question":"Data Cloud licensed?","pass_on":"yes"},
{"id":"dat-g2","question":"Data owner named?","pass_on":"yes"},
{"id":"dat-g3","question":"Duplicate rate measured by client?","pass_on":"yes"},
{"id":"dat-g4","question":"Sponsor confirmed?","pass_on":"yes"},
{"id":"dat-g5","question":"Source systems listed?","pass_on":"yes"}],
"tiers":[{"name":"Two-source","signals":["two source systems"]}],
"disqualifiers":[{"condition":"no salesforce licence","route_to":"paid scoping"}]}
```

Approved qualifier schema: not supplied.

## Output

### Harbourview Foods: playbook fit

**Route to Q2C-01 (quote-to-cash on Salesforce CPQ). Fit is "possible", score 0.62, 0.03 below the "strong" line.** The match rests mostly on what Priya Raman said, but two of its tag hits come from Tom's beliefs, so the match is classed `seller_asserted`. It is not yet a confirmed recommendation. Two gates are still open, and they are what keep it from strong.

This run is diagnostic only. No approved qualifier schema was supplied, so the three qualifiers were checked only for the minimum fields the router needs, not validated against a schema. Don't use the ranking for a decision until that validation is done. I also couldn't run `route.py`, so I applied its rules and default weights by hand. Re-running the script on `out/signals.json` and `out/qualifiers/` should reproduce the numbers below.

#### Ranking

Coverage: 3 of 3 qualifiers scored, none skipped.

| Rank | Playbook | Fit | Score | Evidence class | Tier hypothesis |
|---|---|---|---|---|---|
| 1 | Q2C-01 Quote-to-cash on Salesforce CPQ | possible | 0.62 | seller_asserted (7 client_stated, 2 seller_asserted) | Extended, confidence 0.5 |
| 2 | DAT-03 Account unification on Data Cloud | weak | 0.06 | inferred | none |
| 3 | SVC-02 Service Cloud case routing | weak | 0.00 | none | none |

No disqualifier fired on any playbook.

#### Why Q2C-01 scored

Sources are Priya Raman (Head of Sales Operations) and Tom Beck's notes from the 2026-10-28 call. Those notes are the only record, with no recording or transcript, so each client statement is only as exact as Tom's note of it.

Client stated:
- Harbourview uses Salesforce CPQ in production, quoting to about 40 distributors (tag "salesforce cpq").
- Discounts go through manual discount approval by email, and "some quotes sit for days waiting on a yes" (tag "discount approval").
- Two price books, one for the US and one in CAD for Canada (tag "price book"; also the Extended tier signal "two price books").
- Priya owns the CPQ configuration (gate q2c-g2 passed).
- No plans to replace CPQ (gate q2c-g5 passed). Gate q2c-g1 (CPQ licensed and in use) also passed.

Seller asserted, from Tom and not confirmed by the client:
- Reps do manual pricing in spreadsheets before quoting. Tom's basis is a past deal. This scored on the tags "manual pricing" and "quoting".
- Marcus Odell (CFO) will sponsor. No one has spoken to him. This signal scored nothing, since it matches no tag.

Components: tags 0.70 (4.2 of a possible 6), gates 0.60 (three of five passed, all client stated), tier 0.50 (one of the two Extended signals seen). Weighted at 0.4, 0.4 and 0.2, that gives 0.28 + 0.24 + 0.10 = 0.62. The tier hypothesis is Extended on one signal, the two price books. The other Extended signal, regional approvers, was never mentioned. Treat the tier as a hypothesis for the quote, not a selection.

#### Why the others did not score

- **SVC-02:** Priya said Service Cloud and case routing work is out of scope this year. The router caught both tags as ruled out (`negated_tag_hits`) and gave them no score. This is a client statement, not a gap in the notes, so there is nothing to pursue now.
- **DAT-03:** The only support is the note-taker's guess about duplicate accounts between the ERP and Salesforce, from the size of the distributor base. Nobody mentioned it. It scored 0.3 per tag and caps that match at `inferred`. Worth one question on the next call, no more.

#### Agenda for the next call

Unanswered gates for Q2C-01:
1. **Quote cycle time (q2c-g3).** Priya said quotes "sit for days"; she did not give a number. Ask for the current turnaround and where in the process it is measured.
2. **Executive sponsor (q2c-g4).** Tom's view that Marcus Odell will sponsor is unconfirmed. Ask Priya who signs off on a CPQ change and whether she can bring that person to the next call.

If both gates pass on client-stated answers, the gate component rises from 0.60 to 1.00. That adds 0.16 and lifts Q2C-01 to about 0.78, in the "strong" range.

Seller-asserted points to put on the client's record, so they don't turn into assumptions in a later design document:
- Whether reps price by hand in spreadsheets before the quote enters CPQ.
- Whether the Canada price book has separate approvers (the Extended tier signal).

Optional: ask how distributor accounts are matched between the ERP and Salesforce, to test the DAT-03 guess.

#### Limits

- This does not price the work or lock a tier.
- Gate answers use per-playbook ids (q2c-g1 and so on) so one playbook's answers cannot score another. If the qualifier set reuses ids such as g1 across playbooks, the answers will collide.
- The negation check is cue-based. I read each signal against the cues, and I wrote the SVC-02 signal so it states plainly that the work is out of scope.

#### Files

- `out/signals.json`: 7 cited signals and 3 gate answers, each with an evidence class and source.
- `out/qualifiers/q2c-01.json`, `svc-02.json`, `dat-03.json`: the three qualifiers split from your paste, unchanged.
- `out/run.json`: the run record with weights, coverage, per-match evidence and the schema-validation status ("not performed"). Marked as computed by hand.
- `out/answer.md`: this reply.
