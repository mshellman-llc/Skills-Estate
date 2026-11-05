---
skill: deal-desk
title: Deal Desk packet for a fixed-fee data warehouse quote with unconfirmed staffing
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: a994c1f2862ed00ea7f6678f0ff288cf41200066b678d62a505428ed41a94729
---

## Request

Please prepare the Deal Desk packet for the Larkspur data warehouse quote, Q-4417, ahead of Thursday's meeting. The quote export, our margin policy and my deal notes (including the SOW draft figures) are in the inputs folder.

## Inputs

Run of the built `commercial-review` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `deal-desk-packet-Q-4417.md.fix`.

#### deal-notes.md

#### Deal notes from Aaliyah Brandt (AE), 2026-11-03

- Opportunity: Larkspur data warehouse. Stage: proposal. Source: referral from a partner bank. First call 2026-09-09; scoping call 2026-10-08 (agreed the three source systems and two reports).
- ROM shown 2026-10-15: $150,000 to $180,000. Client said it was "inside the range we expected".
- Trigger: regulator's quarterly reporting is manual and late. Hard deadline: go-live before 2027-03-01 for Q1 filing.
- Stated criteria: reporting accuracy and a fixed price. My read (inferred): they will trade scope for the date.
- Competitor: Birchwell Analytics, offering a lower fee with a smaller team.
- Client: Marcus Oyelaran (CFO, sponsor), Ines Calderon (head of data, day-to-day), Hollis Park (IT security, can block data access).
- Estate side: Aaliyah Brandt (AE), Tomasz Okafor (delivery lead), Rosa Lindqvist (finance).
- Deal Desk meets Thursday 2026-11-05.
- SOW draft (v2) says: fee $168,000, four source systems, two UAT rounds, data access by 2026-11-30.
- Delivery has not told me whether they have signed off hours.

#### margin-policy.md

#### Fixed-fee margin policy

Source: Finance Operations page "Margin and approvals", checked by Rosa Lindqvist on 2026-11-02.

Gross margin floor: 30%.

Approval ladder by computed margin:
- 35% or above: Engagement director
- 30% to under 35%: Commercial director
- 20% to under 30%: Managing director
- Under 20%: Chief executive

Protective clauses in the SOW master:
- 4.2 Inventory assumptions: a change in the number of source systems triggers a change order.
- 6.1 Client availability: late data access moves dates and allows a change order.
- 7.3 Hypercare: requests beyond two weeks are billed separately.

No clause covers contractor substitution or extra validation rounds.

#### quote-Q-4417.md

#### Quote Q-4417 (export 2026-11-03)

Client: Larkspur Regional Credit Union. Project: Member data warehouse consolidation.
Pricing model: fixed fee, $165,000. Rate-card value of the hours: $169,200.

| Role | Hours | Bill rate | Cost rate |
|---|---|---|---|
| Engagement lead | 120 | $190 | $120 |
| Solution architect | 160 | $230 | $150 |
| Data engineer | 320 | $175 | $125 |
| Developer | 240 | $165 | $115 |
| QA analyst | 100 | $140 | $90 |

Phases:
- 1 Discovery: 3 weeks, 150 hours, $30,000
- 2 Build: 8 weeks, 600 hours, $100,000
- 3 Validation and cutover: 3 weeks, 190 hours, $35,000

Staffing note: the $125 data engineer cost rate assumes Dana Reyes (in-house). Her availability from 2026-12-01 is not confirmed. A contractor would cost $150 per hour.

Assumptions:
1. Three source systems: core banking, card processor, loan origination.
2. Two reporting integrations.
3. Client provides data access by 2026-11-30.
4. Two UAT rounds.
5. Two weeks of hypercare.

Out of scope: real-time streaming, member portal changes.

## Output

The Larkspur packet for Q-4417 is built, but it asks for "not ready", not approval. The margin is 30.3% against a 30% floor, which leaves $500 of cushion. Delivery has not given a cosign answer, and the data engineer is unconfirmed.

#### Margin

| Figure | Value |
|---|---|
| Fixed fee | $165,000 |
| Internal cost | $115,000 (940 hours x cost rates) |
| Gross margin | $50,000, which is 30.3% |
| Floor | 30%, from the margin policy checked by Rosa Lindqvist on 2026-11-02 |
| Approver at 30.3% | Commercial director |

The margin is provisional because one person is unconfirmed. The quote's $125 data engineer cost rate assumes Dana Reyes, whose availability from 2026-12-01 is not confirmed. A contractor at $150 gives 25.5%, which is below the floor and routes to the Managing director.

| Scenario | Cost | Margin |
|---|---|---|
| Quoted staffing | $115,000 | 30.3% |
| Half the data engineer hours to a contractor | $119,000 | 27.9% |
| All data engineer hours to a contractor | $123,000 | 25.5% |
| Third UAT round (40 developer hours) | $119,600 | 27.5% |
| Fourth source system, no change order (80 data engineer, 20 QA hours) | $126,800 | 23.1% |

The 40, 80 and 20 hour sizes are mine, not the quote's. Tomasz Okafor should replace them with delivery estimates. I assigned no probabilities.

#### Flags you should not miss

1. **Delivery cosign is pending.** Your notes say delivery has not reported on the hours. I recorded `pending`, signer Tomasz Okafor, date 2026-11-05. I did not infer an answer. Please ask him directly, and I will update the record with his words.
2. **The schedule may miss the deadline.** The quote runs 14 weeks. If work starts 2026-12-01, it ends about 2027-03-09, after the 2027-03-01 go-live. The start date is not in the evidence, so this is flagged and not asserted.
3. **SOW draft v2 conflicts with the quote.** It says $168,000 and four source systems. The quote says $165,000 and three. The quote wins. I did not edit the SOW. It needs correcting at source before Larkspur sees it.
4. **Two margin risks have no protective clause.** Contractor substitution and extra validation rounds are not covered by SOW master 4.2, 6.1 or 7.3. Those three clauses do cover the source system count, late client access and hypercare.
5. **The fee is $4,200 under rate card** ($169,200). The quote does not say who approved that concession.

#### Asks (overall action: not ready)

1. Approve $165,000 only if the data engineer is confirmed in-house. Recommend approve with that condition.
2. Correct SOW draft v2 to the quote.
3. Add protective terms for contractor substitution and a third validation round. These are proposals until the client accepts them.
4. Hold the $4,200 rate-card gap as conceded if staffing is confirmed, and reclaim it if not. Reclaiming it gives 32.0%.

My pricing recommendation is to hold $165,000 and not match Birchwell's lower fee, since the room above the floor is $500. Lever effects are shown in the packet. I changed no prices, because pricing belongs to scoping-agent against the quote.

The decisions log is empty, as it should be before the meeting. Five action items are assigned, all due 2026-11-05.

#### Gaps in the evidence

These sections carry named unknowns with an owner and a resolve-by date, not guesses:

- Stakeholder postures and maturity tags
- Last touch, confidence level, win wedge and exec presence
- The DDOC option and methodology
- Weekly staffing allocation

#### Checks, and what I could not run

- **Gate (`deal_desk_gate.py`):** I could not run scripts. I applied its documented rules by hand.
  - Cost recomputes to $115,000 from the role rows.
  - Margin recomputes to 30.30%, matching the stated 30.3 (tolerance 0.5 points).
  - 30.30 is above 30, so `above` is correct.
  - It lands in the 30 to 35 band, so the route is Commercial director.
  - Pricing model is fixed fee, cosign status is `pending` with a named signer and date, and there is one approval action.
  - **Disposition:** 0 failures found by hand. Please run the script before the packet ships, because a hand check is not the gate.
- **Tie-out (`quote_tieout_check.py`):** also done by hand, with the quote as the source.
  - **Matches:** hours, rates, phase totals, the data access date and the two UAT rounds.
  - **Conflicts:** 2, both in SOW draft v2 (fee and source system count).
  - **Not carried in the SOW excerpt:** the two integrations, hypercare and the out-of-scope lines. I could not tell whether the full SOW includes them.
- **Scoping system:** unavailable. I used the 2026-11-03 quote export and did not re-confirm the Q-number live.
- **Rendering:** I did not run the brand renderer or its visual, parity and brand gates, so there is no HTML or docx yet. The packet is Markdown, and the margin is the first figure with its table. The gauge against the floor still needs rendering.
- **Writing check:** I could not run `writing_check.py`. I read the prose by hand for em dashes, sentence-case headings and AI vocabulary, and found none. This is a manual substitute only.

#### The judgment call I would argue against

I chose "not ready" over "approve with conditions". The other side says the margin clears the floor, the conditions are clear, and Deal Desk can approve now with staffing and cosign as conditions. That would save a day before the client date. I held back because a conditional approval from a desk with no delivery answer looks like approval of hours nobody has reviewed. If Tomasz Okafor confirms on Thursday, this converts in the room.

#### Files

All in `./out/`:

- `deal-desk-packet-Q-4417.md`: the full packet with every catalog section, the embedded figures block and the empty decisions log. The figures block carries the 30% floor, the four-band ladder, route Commercial director, cosign `pending` (Tomasz Okafor, 2026-11-05) and action `not_ready`.
- `04-decisions-assumptions.md`: the decision record. It lists what was asked, that nothing has been decided, my assumptions, and that the quote supersedes SOW draft v2 on fee and system count.
- `deal-desk-packet-Q-4417.md.fix`: a stray placeholder file I created by mistake. It has no content and can be deleted.

### File: 04-decisions-assumptions.md

#### Decisions and assumptions: Larkspur data warehouse (Deal Desk)

As of 2026-11-04. Quote Q-4417.

##### Asked

Deal Desk on 2026-11-05 is asked for one action: not ready now, moving to approve with conditions once delivery answers. Four specific asks sit under it (fee conditional on in-house data engineer, SOW correction, new protective terms, the $4,200 rate-card gap). See the packet.

##### Decided by humans

Nothing yet. The decisions log is empty and stays empty until the meeting.

##### Assumptions made in preparing the packet

- Policy values (30% floor, four-band ladder) were taken from the supplied margin policy, checked by Rosa Lindqvist on 2026-11-02. Re-verify if the meeting slips.
- The quote export of 2026-11-03 was used as supplied. The scoping system was not reachable, so the Q-number was not re-confirmed live.
- Delivery cosign: pending, Tomasz Okafor, due 2026-11-05. Nobody answered.
- Scenario sizes for a fourth source system (80 data engineer, 20 QA hours) and a third UAT round (40 developer hours) are mine, not the quote's.

##### Supersedes

SOW draft v2 on fee ($168,000) and source systems (four): the quote governs at $165,000 and three.

### File: deal-desk-packet-Q-4417.md

#### Deal Desk readout: Larkspur member data warehouse

Internal only. Contains margin, cost rates and candid risk. Quote Q-4417, exported 2026-11-03. Packet as of 2026-11-04. Meeting: Thursday 2026-11-05.

##### Margin: 30.3% against a 30% floor

| Figure | Value | Computation |
|---|---|---|
| Fixed fee | $165,000 | Quote Q-4417 |
| Internal cost | $115,000 | Sum of role hours x cost rate (economics table) |
| Gross margin | $50,000 | $165,000 - $115,000 |
| Gross margin % | 30.3% | $50,000 / $165,000 |
| Floor | 30% | Finance Operations "Margin and approvals", checked 2026-11-02 |
| Position | 0.3 points ($500) above the floor | Provisional, see below |

The margin is provisional. It depends on one unconfirmed person. If a contractor fills the data engineer role, margin falls to 25.5%, which is below the floor and moves the approval to the Managing director. One more source system without a change order takes it to 23.1%.

| Field | Entry |
|---|---|
| Deal | Larkspur Regional Credit Union, member data warehouse consolidation |
| Stage | Proposal |
| Submitted by | Aaliyah Brandt (AE) |
| Total program value | $165,000 (single program, three phases) |
| Phase price at this desk | $165,000, all three phases |
| Phase count | 3 |
| Confidence | Not supplied. Named unknown, owner Aaliyah Brandt, resolve by 2026-11-05, blocks the win-probability discussion only |
| Competitor | Birchwell Analytics (lower fee, smaller team; AE notes 2026-11-03) |

Larkspur's quarterly regulatory reporting is manual and late, and it needs automating before the Q1 filing. The offer is a fixed-fee consolidation of three source systems into one reporting warehouse, live before 2027-03-01. The fee clears the floor by $500, so one staffing change or one extra system removes the cushion.

##### Flags a reviewer must not miss

1. **Staffing unconfirmed.** The data engineer (320 hours) assumes Dana Reyes at $125 cost. Her availability from 2026-12-01 is not confirmed (quote staffing note). Resolve: Tomasz Okafor, by 2026-11-05. Blocks the margin verdict.
2. **Delivery cosign is pending.** The AE notes say delivery has not reported whether hours are signed off. No answer exists. Status is `pending`, signer Tomasz Okafor, date 2026-11-05.
3. **Schedule against the deadline.** The quote runs 14 weeks. If work starts on 2026-12-01, the date Dana Reyes is needed, it ends about 2027-03-09, after the 2027-03-01 go-live deadline. The start date is not in the evidence. Resolve: Tomasz Okafor, by 2026-11-05.
4. **SOW draft v2 disagrees with the quote.** It states fee $168,000 (quote: $165,000) and four source systems (quote: three). The quote wins. A fourth system is worth about $11,800 of unrecovered cost under this fee. Owner: Aaliyah Brandt, with the statement-of-work skill.
5. **No protective clause** covers contractor substitution or extra validation rounds. Both are margin risks.
6. **Thin cushion on the ladder.** 30.3% routes to the Commercial director. The pessimistic staffing case routes to the Managing director.
7. **Fee sits $4,200 under rate card** ($169,200). The quote does not record who approved the concession. Named unknown, owner Aaliyah Brandt, resolve by 2026-11-05.

##### Sales context

| Row | Entry | Source |
|---|---|---|
| Stage | Proposal | AE notes 2026-11-03 |
| Source | Referral from a partner bank | AE notes |
| First conversation | 2026-09-09 | AE notes |
| Scoping call | 2026-10-08. Agreed three source systems and two reports | AE notes |
| ROMs shown | $150,000 to $180,000 on 2026-10-15. Client said it was "inside the range we expected" | AE notes |
| Buying signal (observed) | Client described the ROM as in range. No further signal recorded | AE notes |
| Trigger event | Regulator's quarterly reporting is manual and late | AE notes |
| Decision criteria, stated | Reporting accuracy and a fixed price | AE notes |
| Decision criteria, inferred | They will trade scope for the date. AE read, untested | AE notes, inference |
| Hard deadline | Go-live before 2027-03-01 for the Q1 filing | AE notes |
| Last touch | Not supplied. Owner Aaliyah Brandt, resolve by 2026-11-05, blocks nothing | Named unknown |

##### Stakeholders

| Side | Name | Role | Maturity tag | Notes |
|---|---|---|---|---|
| Client | Marcus Oyelaran | CFO, sponsor | Not supplied | Sponsor per AE notes |
| Client | Ines Calderon | Head of data | Not supplied | Day-to-day contact |
| Client | Hollis Park | IT security | Not supplied | Can block data access (AE notes); affects the 2026-11-30 access date |
| Estate | Aaliyah Brandt | AE | n/a | |
| Estate | Tomasz Okafor | Delivery lead | n/a | Cosign owner |
| Estate | Rosa Lindqvist | Finance | n/a | Checked the margin policy 2026-11-02 |

Postures and maturity tags are not in the supplied evidence, so none are stated. Owner Aaliyah Brandt, resolve by 2026-11-05. The sponsor sits in finance, while the person who can block access sits in IT security, so the data-access assumption depends on someone outside the sponsor's line.

##### Win strategy

| Row | Entry |
|---|---|
| Wedge | Not supplied beyond the fixed price and the date. Named unknown, owner Aaliyah Brandt, resolve by 2026-11-05 |
| Risk to winning | Birchwell offers a lower fee with a smaller team. A price cut here goes through the floor |
| Competitive posture | Birchwell: lower fee, smaller team (AE notes). No other detail |
| Exec presence | Not supplied. Named unknown, owner Aaliyah Brandt, resolve by 2026-11-05 |

##### Scope and solution

| Phase | Workstream | Duration | Hours | Price |
|---|---|---|---|---|
| 1 | Discovery | 3 weeks | 150 | $30,000 |
| 2 | Build | 8 weeks | 600 | $100,000 |
| 3 | Validation and cutover | 3 weeks | 190 | $35,000 |
| | Program total | 14 weeks | 940 | $165,000 |

The DDOC and its confirmed option were not supplied, so workstream names come from the quote's phase names only. Named unknown, owner Aaliyah Brandt, resolve by 2026-11-05, blocks the SOW scope section.

**In scope:** consolidation of core banking, card processor and loan origination data; two reporting integrations; two UAT rounds; two weeks of hypercare.

**Out of scope:** real-time streaming; member portal changes (quote).

###### Assumptions

| Area | Assumption | If broken |
|---|---|---|
| Source systems | There are three: core banking, card processor, loan origination | A fourth adds about 80 data engineer and 20 QA hours, $11,800 of cost; margin 23.1%. Change order under clause 4.2 |
| Integrations | There are two reporting integrations | The quote gives no hours per integration. Treat a third as a change order; sizing owed by Tomasz Okafor |
| Data access | Client provides access by 2026-11-30 | Dates move and a change order is allowed under clause 6.1. With no schedule slack recorded, any delay worsens flag 3 |
| UAT | Two rounds | A third round of 40 developer hours adds $4,600 of cost; margin 27.5%. No clause |
| Hypercare | Two weeks | Requests beyond two weeks are billed separately under clause 7.3 |
| Staffing | Dana Reyes fills the data engineer role at $125 per hour | A contractor at $150 adds $8,000; margin 25.5% |

The 40-hour figure for a third UAT round and the 80 and 20 hour figures for a fourth system are scenario sizes chosen for this packet, not quote values. Tomasz Okafor should replace them with delivery estimates.

###### Risks and mitigation

| Severity | Risk | Mitigation | Owner |
|---|---|---|---|
| High | Dana Reyes is unavailable from 2026-12-01 and a contractor is needed, cutting margin to 25.5% | None committed. Needs resourcing confirmation | Tomasz Okafor |
| High | Client adds a fourth source system during discovery | Clause 4.2 in the SOW master; acceptance by the client not confirmed | Aaliyah Brandt |
| High | 14-week plan overruns the 2027-03-01 deadline | None committed. Start date unknown | Tomasz Okafor |
| Medium | Late data access from IT security | Clause 6.1 | Aaliyah Brandt |
| Medium | Extra validation rounds | No coverage. Flag | Tomasz Okafor |
| Medium | SOW draft carries the wrong fee and system count | Correct at source before release | Aaliyah Brandt |
| Low | Hypercare requests beyond two weeks | Clause 7.3 | Tomasz Okafor |

Known gap: if scope or margin changes after approval, re-alignment is required before the SOW is final. That check belongs to deal governance and is not built here.

###### Methodology

Not supplied (sprint length, cadence, deployments, reference engagements). Named unknown, owner Tomasz Okafor, resolve by 2026-11-05, blocks nothing at this desk.

##### Economics

| Role | Hours | Bill rate | Subtotal at rate | Cost rate | Cost |
|---|---|---|---|---|---|
| Engagement lead | 120 | $190 | $22,800 | $120 | $14,400 |
| Solution architect | 160 | $230 | $36,800 | $150 | $24,000 |
| Data engineer | 320 | $175 | $56,000 | $125 | $40,000 |
| Developer | 240 | $165 | $39,600 | $115 | $27,600 |
| QA analyst | 100 | $140 | $14,000 | $90 | $9,000 |
| Total | 940 | | $169,200 | | $115,000 |


[trimmed: the rest of this file, about 887 more words, is not shown]
