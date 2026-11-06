---
skill: maintain-discovery-record
title: Starting a pursuit findings ledger after the first call
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 51d21c7ee14f73df4a09ba9cb86ef8ff3a5a7f938c5f3523c021d662f01d1df3
---

## Request

Update the Tidewater Freight Co. pursuit findings ledger from today's first discovery call. There is no existing ledger yet — start one. Notes and account background are in ./inputs/.

## Inputs

Run of the built `synthesize-discovery` task package in its "maintain pursuit findings" mode. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Files it also produced, not shown here: `ledger.json`.

#### account-notes.md

#### Tidewater Freight Co. — account notes (fictional)

- Regional less-than-truckload (LTL) carrier, 14 terminals across Virginia, the Carolinas and Georgia. About 1,900 employees, 1,100 tractors.
- Revenue about $410M (FY2025, company-reported in a trade-press interview).
- Customer service runs from one contact center in Norfolk: 62 agents, three shifts. Today they use a 2014-era on-premise ticketing tool ("ServiceDesk Pro") plus shared Outlook inboxes for claims.
- Transportation management system (TMS): "RouteLine 9", hosted by the vendor, REST API available for shipment status and proof-of-delivery images.
- Pain points raised by the inbound lead form: customers can't self-serve shipment status; freight-claims cycle averages 41 days; no single view of a shipper account across terminals.
- Inbound lead came from the VP of Customer Experience after a webinar on Service Cloud for logistics.


#### call-1-notes.md

#### Discovery call 1 — Tidewater Freight Co. (fictional). Notes taken by our AE.

Attendees: Dana Whitfield (VP CX), Marcus Oyelaran (Dir. IT Apps, second half), our AE, our solution consultant.

- Dana: "About 30% of our inbound calls are 'where is my freight.' If customers could look that up themselves we'd free up a third of the floor."
- Contact center: 62 agents. Average handle time on status calls 4.5 minutes. Dana estimated 1,800 status calls per day; she said she'd confirm with the WFM report.
- Claims: 41-day average cycle. Priya's team keys claims from email into a spreadsheet, then into ServiceDesk Pro. Dana: "Claims is where we lose customers."
- Target: online shipment tracking and online claim filing live before peak season — Dana said "October next year."
- Marcus: RouteLine 9 has a REST API for shipment status and POD images. Rate limit is 20 requests per second per tenant. He does not know whether claims data can be written back to RouteLine. "I'd need to ask the vendor."
- Marcus is concerned about owning another platform with a 3-person apps team.
- Budget: Dana said the CFO "would want to see something under half a million for phase one" — not a confirmed budget.
- Decision: Dana sponsors; CFO Tom Becker signs over $250K; Marcus has effective veto on architecture.
- Next step: second call with Priya (claims) and Marcus in two weeks.

## Output

### Tidewater Freight Co. — pursuit findings ledger, started after discovery call 1 (2026-11-04)

I started the ledger from the AE's call notes and the account background. It has 19 supported claims and 8 ranked open questions. It does not answer or close anything. The only call evidence is the AE's notes, not a transcript, so I recorded no question as closed. No commercial number is created or sized.

#### Assumptions and gaps

- **Evidence is secondary.** The notes (S-02) are not a verbatim transcript and most bullets carry no speaker label. Quotes below are exactly as the notes record them, and I can't confirm they are Dana's or Marcus's literal words. The account notes (S-01) are undated.
- **Where "Confirmed" is used.** Only for facts that two sources support and that the speaker owns: the 62 agents, the ServiceDesk Pro and Outlook tooling, and the RouteLine 9 API. Every client-stated metric stays Inferred because no report backs it.
- **No capability catalog, opportunity ID, quote or pricing was supplied.** Scope lines are descriptive and carry no capability codes. I did not size anything.
- **"October next year" is read as October 2027**, since today is 2026-11-04. That is my reading, and Q-05 asks about it.
- **I ran the steps by hand.** I couldn't run `evidence-core`, `check_brief.py`, `review-writing` or `review-deliverable`. I registered sources S-01 and S-02 and applied the gate rules by hand (details below). No tool receipts exist.
- **Not persisted to a Hub record.** No connector was available, so this is a returned patch. The only copy is `ledger.json` in `./out/`.

#### Column A: what we know

| Claim | Source | Confidence | As-of |
| --- | --- | --- | --- |
| Regional LTL carrier, 14 terminals across Virginia, the Carolinas and Georgia, about 1,900 employees, 1,100 tractors | S-01 account notes, undated | Inferred | undated |
| Revenue about $410M (FY2025), company-reported in a trade-press interview | S-01 | Inferred | FY2025 |
| One Norfolk contact center, three shifts | S-01 | Inferred | undated |
| The contact center has 62 agents | S-01; S-02 call notes 2026-11-04 | Confirmed | 2026-11-04 |
| Tools: 2014-era on-premise ServiceDesk Pro plus shared Outlook inboxes for claims | S-01; S-02 (claims keyed into ServiceDesk Pro) | Confirmed | 2026-11-04 |
| Claims start in email; Priya's team keys them into a spreadsheet, then ServiceDesk Pro (Priya's surname and title not recorded) | S-02 (speaker not recorded); S-01 | Inferred | 2026-11-04 |
| Claims cycle averages 41 days; no claims report cited | S-01; S-02 | Inferred | 2026-11-04 |
| Dana Whitfield (VP CX): "Claims is where we lose customers." | S-02, Dana Whitfield | Inferred | 2026-11-04 |
| Dana Whitfield: "About 30% of our inbound calls are 'where is my freight.' If customers could look that up themselves we'd free up a third of the floor." Her estimate, not a report | S-02, Dana Whitfield | Inferred | 2026-11-04 |
| Average handle time on status calls is 4.5 minutes | S-02 (speaker not recorded) | Inferred | 2026-11-04 |
| About 1,800 status calls per day (Dana's estimate; she will confirm with the WFM report). Basis: 1,800 at 30% implies about 6,000 inbound calls a day. 1,800 × 4.5 min is about 135 agent-hours a day, roughly 27% of 62 agents' time if each works one 8-hour shift (our arithmetic, shift length assumed). Plausible against "a third of the floor", not verified | S-02, Dana Whitfield | Inferred | 2026-11-04 |
| Goal: online tracking and online claim filing live before peak season; Dana said "October next year" (read as October 2027, not confirmed as a hard date) | S-02, Dana Whitfield | Inferred | 2026-11-04 |
| TMS is RouteLine 9, vendor-hosted, with a REST API for shipment status and POD images | S-01; S-02, Marcus Oyelaran | Confirmed | 2026-11-04 |
| RouteLine API rate limit is 20 requests per second per tenant (Marcus; not checked against vendor docs) | S-02, Marcus Oyelaran | Inferred | 2026-11-04 |
| Marcus Oyelaran (Dir. IT Apps) is concerned about owning another platform with a 3-person apps team | S-02, Marcus Oyelaran | Inferred | 2026-11-04 |
| Dana said the CFO "would want to see something under half a million for phase one"; relayed, not a confirmed budget | S-02, Dana Whitfield | Inferred | 2026-11-04 |
| Decision path as stated: Dana sponsors; CFO Tom Becker signs over $250K; Marcus has effective veto on architecture. Speaker not recorded; Tom Becker did not attend | S-02 | Inferred | 2026-11-04 |
| Lead form pains: no customer self-serve status, 41-day claims cycle, no single shipper-account view across terminals (the third was not discussed on call 1) | S-01 | Inferred | undated |
| Lead came from the VP CX after a webinar on Service Cloud for logistics; the call notes record no platform preference | S-01 | Inferred | undated |

#### Column B: ranked unknowns

| ID | Question | Rank | Unblocks | Why open |
| --- | --- | --- | --- | --- |
| Q-01 | What does phase one include (online tracking, online claim filing, the cross-terminal account view), and what does "under half a million" have to cover (licences, implementation, run cost)? Can Tom Becker confirm a number? | High | Phase-one boundary and every scope line below; budget fit | Only Dana's relayed figure and a $250K CFO signature threshold; no budget document or phase definition; CFO absent |
| Q-02 | Does ServiceDesk Pro stay, get replaced, or sit behind the new front end? | High | Case-management and platform foundation line; ServiceDesk Pro integration or migration line | Tool named in both sources, no disposition recorded; Marcus's ownership concern has no decision attached |
| Q-03 | Can claim data be written back to RouteLine 9 through the vendor API, and if not, where does the claim record live? | High | Online claim filing integration line (RouteLine write-back) | Marcus: "I'd need to ask the vendor." No vendor documentation supplied |
| Q-04 | How many claims arrive per month, through which channels, with what attachments, and what happens between receipt and settlement? | High | Claims intake and workflow line; online claim form scope | Only the 41-day average and the email-to-spreadsheet path; no volume, attachments, steps or owners; Priya absent |
| Q-05 | Is October 2027 a hard date, what does "live" mean on that date, and does it cover both tracking and claims? | Medium | Delivery phasing and staffing assumptions across the tracking and claims lines | "October next year" with no reason, contingency or capability coverage recorded |
| Q-06 | How many shipment-status lookups per second do you expect at peak once customers self-serve, and are there other consumers of the RouteLine API? | Medium | Tracking integration design line (caching and throttling) | 20 requests per second tenant limit known; expected online volume and other consumers not recorded |
| Q-07 | How do shippers and consignees identify themselves today (account number, PRO number, login), and where does the shipper master record live? | Medium | Customer identity and access line; shipper account view line | Neither source says how customers are identified or where account data sits |
| Q-08 | Who would run and support the solution after go-live, given a 3-person apps team: Tidewater staff, a managed service, or a mix? | Medium | Run and support / managed-service line | Marcus raised the concern; no support model discussed |

**Who can answer.** Q-01 needs Dana plus the CFO, who was absent. Q-02 and Q-03 need Marcus and the RouteLine vendor. Q-04 needs Priya. I put the questions in that order because Q-01 sets the boundary for the rest.

**Gate before design:** Q-01 and Q-03 must be answered first. Q-01 fixes what phase one is, and Q-03 decides whether claim filing can write into RouteLine at all.

#### Scope at stake (proposed; for the scoping owner, nothing committed)

| Candidate line | Phase | Flag in place |
| --- | --- | --- |
| Online shipment tracking via RouteLine status and POD API | Phase one per Dana (Q-01) | Do not size until Q-01, Q-06 |
| Online claim filing and RouteLine write-back | Phase one per Dana (Q-01) | Do not size until Q-01, Q-03, Q-04 |
| Claims intake and workflow | Unconfirmed | Do not size until Q-04 |
| ServiceDesk Pro disposition (integrate, retain or replace) | Unconfirmed | Do not size until Q-02 |
| Customer identity and shipper account view | Unconfirmed | Do not size until Q-01, Q-07 |
| Run and support model | Unconfirmed | Do not size until Q-08 |

Capability codes: not supplied. These lines are pattern-free; none is derived from an RFP, because none exists in the inputs.

#### Decisions, risks and assumptions

| Item | Reference | Status |
| --- | --- | --- |
| Decision: Dana sponsors; CFO Tom Becker signs over $250K; Marcus has effective veto on architecture | AE notes 2026-11-04, no timestamp, speaker not recorded | Proposed |
| Decision: second call with Priya (claims) and Marcus in about two weeks (around 2026-11-18, date not set) | AE notes 2026-11-04 | Proposed |
| Risk: an architecture veto sits with someone who is already worried about platform ownership. Trigger: a proposal that adds a platform without a run-and-support answer (Q-08) | Marcus's stated concern | Open |
| Risk: the CFO signs over $250K and has not been in the room. Trigger: a phase-one figure in Q-01 that Tom Becker has not seen | Decision path above | Open |
| Assumption: "October next year" means October 2027 | Our reading; Q-05 | Assumption |

No decision changes prior scope, since there was no prior scope. Neither conflicts nor contested sources turned up between S-01 and S-02.

#### Next discovery actions

| Action | Closes | Owner |
| --- | --- | --- |
| Ask the RouteLine vendor whether the API accepts claim writes | Q-03 | Marcus Oyelaran, who said he would ask |
| Get the WFM report for status-call volume. It supports the value case; it did not earn its own question because it does not change scope | Validates the 1,800 per day claim | Dana Whitfield, who offered it |
| Cover claims volume, channels, attachments and steps on the second call | Q-04 | Priya, with the AE leading; role-level owner, not named in the notes |
| Raise phase-one scope and the budget range with Dana, and ask for access to Tom Becker | Q-01 | AE, owner not assigned in the notes |
| Cover ServiceDesk Pro, identity and the support model on the second call | Q-02, Q-07, Q-08 | Marcus; owner of the session not assigned |
| Ask Dana for the reason behind the October date | Q-05 | AE |
| Get the full transcript or a verbatim export of call 1 and re-run ingestion | Retrieval gap | AE (assumed) |

#### Gate result, by hand

- Every Column A row has a source and a confidence of Confirmed or Inferred. None is Unknown.
- Column B has 8 rows, each with a non-empty question, rank and unblocks. The order is four High then four Medium, and the IDs run Q-01 to Q-08.
- No hours, rates, fees or totals appear. The $500K and $250K figures are quoted as client statements, not budgets.
- Not run: `check_brief.py`, `evidence-core`, `review-writing` and `review-deliverable`. The hand check above does not replace their receipts, so I'm not calling this final until those run.

#### Biggest judgment call

I ranked Q-04 (claims process and volume) High. The argument for Medium is that claims volume only changes effort inside a workstream that can still be sized. The argument for High is that Dana named claims as where Tidewater loses customers, and the notes say nothing about the process or volume. Without them I can't size the claims workstream at all, which is the High definition. I kept High.

#### Files

- `./out/ledger.json` — the ledger in the JSON format the gate expects: sources, Column A, Column B, decision log and scope-revision proposal. Its content is reproduced in the tables above.
- `./out/answer.md` — this answer.
