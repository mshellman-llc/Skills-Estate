---
skill: evidence-core
title: ROM request stopped at the evidence gate for a billing portal migration
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 940140ceb630651a43b4c54fbfaa99c3e64f157af5fcf869df979da601794b40
---

## Request

Can you put together a ROM estimate for the Kestrel Valley Water Authority billing portal migration? The RFP excerpt, my discovery call notes and Dana's Slack message are in inputs/. I'd like to send a range to the sponsor on Friday.

## Inputs

Run of the `evidence-core` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `evidence-ledger.json`, `gate-report.json`.

#### dana-slack-message.txt

Dana Whitfield, 2026-10-28 16:12
for Kestrel just use our usual blended 165/hr. gut feel is around 2,400 hours so ~400k, which lines up with what the CFO has in mind. I haven't talked to delivery about it.

#### discovery-call-notes.md

#### Discovery call notes — Kestrel Valley Water Authority
2026-10-21, typed by me during the call (not a recording). Attendees: Tomas Reyes (Authority IT manager), Lindiwe Okafor (billing operations lead), me.

- Tomas: the portal replacement is the whole project. Confirmed about 48,000 accounts.
- Lindiwe: operations only ever looks back about 6 years; she thinks the 10 years in the RFP came from the records retention policy, not from portal users. Tomas did not agree or disagree.
- Integrations: Tomas listed the payment gateway, the meter data system and "the SMS vendor for outage and bill alerts". He said the SMS piece "might be handled by a separate contract". Left open.
- Tomas said the sponsor (CFO) has "somewhere around 400k in mind" but nothing is approved.
- Nobody on the call could say whether the legacy portal's data is clean. No data profiling has been done.
- Go-live of 30 June 2027 was restated as firm.

#### rfp-excerpt.md

#### Kestrel Valley Water Authority — RFP 2026-14 excerpt
Issued 2026-09-15

**3.1 Scope.** Replace the legacy customer billing portal with a hosted portal serving approximately 48,000 residential and commercial accounts.

**3.2 Data.** The successor portal must carry forward 10 years of billing history for every active account.

**3.3 Integrations.** The portal must integrate with (a) the Authority's payment gateway and (b) the meter data management system.

**3.4 Accessibility.** WCAG 2.2 AA conformance is required at go-live.

**3.5 Timeline.** Go-live no later than 30 June 2027, the end of the Authority's fiscal year.

**3.6 Budget.** Not stated in this RFP.

## Output

### Estimate readiness gap: Kestrel Valley billing portal

**I haven't produced a ROM range. The evidence doesn't support one yet, so I stopped at the evidence gate and wrote this memo.** A range sent to the sponsor on Friday would rest on an unreviewed hours guess and an unresolved scope question.

#### What the sources support

| Claim | Status | Source |
|---|---|---|
| Replace the legacy billing portal for about 48,000 accounts [CLM-001] | Confirmed | RFP 3.1; call notes 2026-10-21 |
| Two named integrations: payment gateway, meter data system [CLM-004] | Confirmed | RFP 3.3 |
| Go-live by 30 June 2027; WCAG 2.2 AA at go-live [CLM-010] | Confirmed | RFP 3.4, 3.5; call notes |
| Blended rate of $165/hr [CLM-008] | Inferred | Dana's message, 2026-10-28 (no rate card) |
| Sponsor has roughly $400,000 in mind, nothing approved [CLM-009] | Inferred | Call notes, second-hand |

#### Blockers

| Domain | Result | Blocker | Owner | Closes when |
|---|---|---|---|---|
| Scope basis | Insufficient | History depth conflict: RFP asks for 10 years [CLM-002], billing operations uses about 6 [CLM-003] (CNF-001) | Tomas Reyes, Authority IT manager | Authority states in writing what is migrated and what is archived |
| Scope basis | Insufficient | SMS alert integration may or may not be in scope [CLM-005] | Tomas Reyes | Authority confirms in or out in writing |
| Scope basis, Workstream effort | Insufficient | Legacy data quality unknown, no profiling done [CLM-006] | Tomas Reyes | Authority supplies a data extract sample |
| Workstream effort | Insufficient | The 2,400 hours is a guess made without delivery [CLM-007] | Dana Whitfield with a delivery lead (not yet named) | Delivery lead builds hours by workstream from confirmed scope |
| Role assumptions | Insufficient | No evidence supplied | Unassigned | Delivery lead states the roles and mix |
| Confidence | Insufficient | No basis to state one | Unassigned | Follows the closures above |
| Range reopeners | Insufficient | Cannot be listed until scope items close | Unassigned | Follows the closures above |
| Rates or cost basis | Conditional | Rate rests on a message | Dana Whitfield | Rate card or finance confirmation |
| Commercial posture | Conditional | Budget is hearsay | Dana Whitfield | Sponsor confirms a funding envelope |

Three domains have no owner. They need one before the next gate.

#### Things I did not do

- **I did not use 2,400 hours × $165.** That works out to $396,000, which matches the CFO's "around 400k". The match shows the guess was anchored to the budget. It is not evidence of effort. The message itself says delivery was not consulted.
- **I did not pick 10 or 6 years.** Both are kept as contested claims. The difference changes migration effort, and I can't size it without the Authority's answer.
- **I did not treat the SMS integration as in or out.** It stays a named gap.

#### Direction worth keeping

No executed commitment or approved design exists yet, so there is nothing to retain as a decision. The confirmed facts above (account count, two integrations, fixed date, accessibility) are a safe base for the scope conversation.

#### Next steps before Friday

1. Send Tomas three questions: history depth, SMS in or out, and a data extract sample. These close CNF-001, CLM-005 and CLM-006.
2. Ask Dana to name a delivery lead so [CLM-007] and role assumptions have an owner.
3. If the sponsor needs something on Friday, send the confirmed facts and these open questions, with no number.

**Next gate:** rerun the evidence check on a ledger with those blockers closed. If it passes, the ROM can be built.

#### Process notes and gaps

- I couldn't run `evidence_core.py`. I applied its rules by hand: authority caps, the Confirmed threshold of 70, load-bearing owner and closure checks, and the open load-bearing conflict. The result matches what the script would return: Insufficient, terminal.
- I set the call notes' authority at 65, below the 70 cap for transcripts, because they are typed notes and not a recording. I set Dana's message at 40, below the 50 cap, because she called it a gut feel.
- The files SKILL.md points to before writing (`_shared/build-card.md` and the readout-brief register) were not in the package. The `writing_check.py` checker was also absent. I did a manual read of this memo instead.
- The manual finalization pass for source markers applies to a full artifact. None was produced.

#### Files

- `out/evidence-ledger.json`: 3 sources, 10 claims, 1 open conflict, 7 coverage rows (the table above in ledger form).
- `out/gate-report.json`: status Insufficient, terminal, output type `readiness_gap_memo`.
