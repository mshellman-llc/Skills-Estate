---
skill: prepare-delivery-handoff
title: Handoff package for a signed Service Cloud support migration
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 5a20835369410ea3c73c2a29dbe76ca197f11b23126f9e8eb6305585a99ee0cb
---

## Request

The Tidewater Provisions deal signed on 30 October. Can you build the handoff package for the delivery team from the SOW excerpt and my deal notes in inputs/? I'm walking it to the delivery leads later this week, so I need to know what we promised and what is still open.

## Inputs

Run of the built `prepare-delivery-handoff` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `manifest.json`.

#### deal-notes.md

#### Deal notes (from the AE, Priya Nandakumar), 2026-11-03

Team on our side: Priya (AE), Tom Aldous (Pursuit Lead), Jun Park (CSE). Delivery leads not yet assigned beyond Sam Whitcombe (Solution Lead).

**Client people.** Marguerite Lindqvist (COO, signed, economic buyer, drove the deal). Callum Reyes (Head of Support, day-to-day contact, will own go-live). Dee Okafor (IT Manager, owns NetSuite). Dee was never in a deal meeting; Callum says she "will sort access".

**Things said during the sale**
- Demo call 2026-09-18 (recorded, Jun on it): Priya told Callum "we'll look at a customer portal as a phase 2 and won't charge for the design." Not in the SOW.
- Email 2026-10-06, Jun to Callum: "Most Zendesk macros can come across as canned responses." SOW silent on macros.
- Slack #tidewater 2026-10-21, Priya: Marguerite asked whether the team could be live before the 2027-02-14 half-term sales peak. Priya said "we'll do our best." SOW hard date is 2027-02-26.

**Late thread.** Email 2026-11-02, Callum to Priya: Support now wants 36 months of cases migrated (about 58,000), because of a warranty dispute backlog. SOW caps at 24 months and 40,000. Nobody has replied.

**Other.** Zendesk contract renews 2027-03-01. Callum says agents are nervous about the change. No similar build in our files except the Harbour & Vale Foods case routing from 2025 (routing rules workbook in Drive, "Routing-rules-template.xlsx").

I searched Slack #tidewater, my sent mail and the demo recording. I did not search Marguerite's or Dee's threads.

#### sow-excerpt.md

#### SOW-2026-0417 (executed 2026-10-30), excerpt. Quote Q-004821

Client: Tidewater Provisions Ltd. Fixed fee.

**1. Outcome.** Move order-issue handling from the shared inbox (support@ mailbox plus Zendesk) to Salesforce Service Cloud. Success is median first response on order-issue cases falling from 9 hours (baseline, client Q3 2026 report) to under 2 hours, measured over the 30 days after go-live.

**2. In scope.** (a) Service Cloud configuration for three queues: Missing Items, Late Delivery, Damaged Goods. (b) Email-to-case routing. (c) Read-only order lookup from NetSuite. (d) Migration of up to 24 months of Zendesk cases, capped at 40,000 cases. (e) Training for 12 agents, two sessions.

**3. Out of scope.** Customer portal. Telephony or CTI. WhatsApp or any social channel. Write-back to NetSuite. Data cleansing beyond de-duplication by customer email. Languages other than English.

**4. Fees (Q-004821).** Fixed fee GBP 148,500. Milestones: 30% on signature, 40% on UAT start, 30% on acceptance.

**5. Dates.** Kickoff week of 2027-01-11. Hard go-live 2027-02-26. UAT 2027-02-01 to 2027-02-12.

**6. Assumptions.** Client provides Salesforce and NetSuite sandbox access by 2027-01-04. Client names a NetSuite technical owner. Acceptance: median first response measured on the 30 days after go-live; UAT passes when all 14 agreed test scripts pass.

## Output

### Tidewater Provisions handoff package

The package is built and passes the structural gate. The warm transfer and acceptance have not happened, and nothing here records either.

#### What delivery inherits

1. **A fixed-fee build with one success test.** Median first response on order-issue cases must fall from 9 hours to under 2 hours, measured over the 30 days after go-live (SOW-2026-0417 section 1). The fee is GBP 148,500 under Q-004821, with payments of 30% at signature, 40% at UAT start and 30% at acceptance. Hard go-live is 2027-02-26.
2. **Three off-contract items the client may hold us to.** See "Promises" below.
3. **An unanswered change request.** On 2026-11-02 Callum Reyes asked for 36 months of Zendesk cases, about 58,000. The SOW caps migration at 24 months and 40,000 cases (section 2d). Both values are shown, and I routed it to Tom Aldous as a conflict. I did not treat it as a scope change.

#### Promises (section 07)

| Promise | Said where | In SOW? | Owner and route |
|---|---|---|---|
| Customer portal "as a phase 2", design not charged | Demo call 2026-09-18, Priya Nandakumar | No. Portal is out (section 3). Flagged liability | Tom Aldous: honor, price, or reset before kickoff |
| Zendesk macros "can come across as canned responses" | Email, Jun Park to Callum Reyes, 2026-10-06 | No. SOW silent. Flagged | Sam Whitcombe: confirm feasibility first |
| "We'll do our best" to be live before the 2027-02-14 peak | Slack #tidewater 2026-10-21, Priya Nandakumar | No. Conflicts with hard date 2027-02-26 | Tom Aldous: reset in writing with Marguerite Lindqvist |

Searched: Slack #tidewater, your sent mail, and the demo recording. Not searched: Marguerite's and Dee Okafor's threads, and Tom's and Jun's mailboxes beyond the one cited email. So "nothing else found" holds only for what was searched.

#### Still open (five gaps, each with an owner)

| Gap | Owner | Resolve by | Blocks |
|---|---|---|---|
| Any prior assessment or discovery (section 02) | Priya Nandakumar | 2026-11-06 | Warm transfer |
| Delivery-lens and maturity-gap flags from scope review (section 06) | Tom Aldous | 2026-11-06 | Warm transfer |
| Sandbox access request status, and whether Dee Okafor accepted the NetSuite owner role (section 04) | Callum Reyes, chased by Jun Park | 2026-11-20 | Kickoff |
| Program Lead, and whether Marguerite sits on the steering group (section 09) | Tom Aldous | 2026-11-13 | Kickoff |
| Manual steps in today's order-issue flow (section 03) | Sam Whitcombe | 2027-01-15 | Design sign-off |

Two stakeholder mismatches are flagged. Marguerite drove the deal and signed, but no source places her in delivery. Dee Okafor owns NetSuite and was in no deal meeting. Callum's "she will sort access" is unverified, and the signed sandbox deadline is 2027-01-04.

One risk you may not have spotted: the 30-day measurement window ends around 2027-03-28, but the Zendesk contract renews on 2027-03-01. Someone needs to ask the client what happens to Zendesk before acceptance.

#### Week one (section 11)

Five sessions, ordered by risk, each with an owner, attendees and a concrete output:

1. Settle migration volume: 24 or 36 months, with case counts by month. Owner Tom Aldous. Output: a written decision to hold the cap or raise a change order.
2. Confirm access and ownership for NetSuite and both sandboxes. Owner Jun Park. Output: a named owner in writing and verified logins.
3. Reset the go-live expectation against the 2027-02-14 peak. Owner Tom Aldous. Output: written client confirmation of 2027-02-26.
4. Map the as-is order-issue flow. Owner Sam Whitcombe. Output: a map of every manual step.
5. Decide Zendesk macros and the renewal position. Owner Sam Whitcombe. Output: a macro inventory and a written renewal position.

#### Definition of done (section 12)

Four binary criteria, all quoted from or tied to the SOW's acceptance methods: median under 2 hours over 30 days, all 14 UAT scripts pass, migrated case count matches the agreed export, and order lookup works without NetSuite write-back. The migration tolerance is not yet agreed.

The readiness checklist has 8 items: 4 blocked and 4 unknown, none ready. Blocked items: delivery team named, client owners, promises dispositioned, and mismatch resolution paths. Unknown items: the executed quote, sandbox access, kickoff scheduling, and maturity-gap flags. Blocked and unknown items do not fail the handoff. Hiding them would.

#### Gate and what I did by hand

I could not run scripts. I applied `check_handoff.py`'s rules to the manifest by hand: moment=package, sections=12/12, scope_items=13 (5 in, 8 out), promises=4, figures=5, gaps=5. Findings: 0. Every figure traces to the SOW or Q-004821, and I used no em dashes. Please run `python3 scripts/check_handoff.py out/manifest.json` to confirm.

Not done, and why:
- **Evidence-core ledger.** I built the claim sourcing directly into the manifest, not as a separate ledger file.
- **Brand renderer, review-writing diagnostics and review-deliverable.** None were run. No brand profile was supplied, so this is portable Markdown, and I reviewed the prose by hand for em dashes and heading case. Treat the package as a draft until those checks have run.
- **Source gaps.** I saw only the SOW excerpt, not the full SOW or the quote itself. Fee and dates come from the SOW text. The Salesforce, Drive and calendar sources were not available, and no transcript was read verbatim. The promise quotes come from your notes, so check them against the demo recording before the transfer.

#### Biggest judgment call

I held the 36-month request as an open conflict for the Pursuit Lead, not something to absorb. The other side: the client's warranty backlog is real, and a quick yes might protect the relationship at a tense start. But 58,000 cases is about 45% above the cap on a fixed fee, so the decision belongs to Tom Aldous, with the case counts from session 1 in hand.

#### Files

- `out/handoff-package.md`: the rendered package, all 12 sections, with the gate counts and outstanding actions.
- `out/manifest.json`: the manifest it is rendered from. Fix gaps here and re-render. Don't patch the Markdown.
- `out/answer.md`: this reply.

`DELIVERY-STATE.md` is not created. It is seeded only when delivery accepts the brief at moment 2.

### File: handoff-package.md

#### Handoff package: Tidewater Provisions Ltd

Order-issue handling migration to Salesforce Service Cloud
Moment: package (at signature). As of 2026-11-04.
Source snapshot: SOW-2026-0417 (executed 2026-10-30, excerpt), quote Q-004821.
Status: warm transfer not yet held; no acceptance recorded.

##### What delivery inherits

1. A fixed-fee build judged on one number: median first response on order-issue cases from 9 hours to under 2 hours.
2. Three off-contract items the client may hold us to: a free portal design, Zendesk macros as canned responses, and a go-live before the 2027-02-14 peak.
3. An unanswered client request (2026-11-02) to migrate 36 months of cases, about 58,000, against a 40,000 cap.

##### 01 The engagement

Standard: a new reader gets it in two minutes, and every figure traces to the SOW or quote.

- **Outcome.** Median first response falls from 9 hours (client Q3 2026 report) to under 2 hours, measured over the 30 days after go-live (SOW section 1).
- **Sold.** Service Cloud for Missing Items, Late Delivery and Damaged Goods queues; email-to-case routing; read-only NetSuite order lookup; migration of up to 24 months of Zendesk cases, capped at 40,000; training for 12 agents in two sessions (SOW section 2).
- **Out.** Customer portal, telephony or CTI, WhatsApp or any social channel, NetSuite write-back, data cleansing beyond de-duplication by customer email, non-English languages (SOW section 3).

**Contract baseline**

| Item | Value | Source |
|---|---|---|
| Fee model | Fixed fee | SOW section 4 |
| Total | GBP 148,500 | SOW section 4, Q-004821 |
| Payment | 30% signature, 40% UAT start, 30% acceptance | SOW section 4 |
| Kickoff | Week of 2027-01-11 | SOW section 5 |
| UAT | 2027-02-01 to 2027-02-12 | SOW section 5 |
| Hard go-live | 2027-02-26 | SOW section 5 |
| Signed assumptions | Sandbox access by 2027-01-04; client names a NetSuite technical owner; UAT passes when all 14 agreed scripts pass | SOW section 6 |

Scope list: 5 items in, 8 out; see the manifest.

##### 02 What came before

Standard: the team can name what is closed versus open.

**Gap.** Whether any assessment or discovery preceded the SOW is not known; none was supplied and Drive and Salesforce were not searched. Owner: Priya Nandakumar. Resolve by 2026-11-06. Blocks: warm transfer.

##### 03 Process and current state

Standard: real people and tools, every manual break marked and tied to the fix sold.

- Order issues arrive in the shared support@ mailbox and Zendesk. Median first response is 9 hours (SOW section 1).
- The break is slow first response; the sold fix is queue routing and email-to-case (SOW sections 1 and 2).

**Gap.** The manual steps between arrival and first reply, and who performs them, are not documented. Owner: Sam Whitcombe. Resolve by 2027-01-15. Blocks: design sign-off.

##### 04 System landscape

Standard: every system labeled, each owner named, every access dependency flagged.

| System | Label | Owner | Access |
|---|---|---|---|
| Zendesk | Replace; migration source | Not named | Renews 2027-03-01 (deal notes) |
| Shared support@ mailbox | Replace via email-to-case | Not named | Not stated |
| NetSuite | Connect, read-only | Dee Okafor, IT Manager | Due 2027-01-04; no request on the record |
| Salesforce Service Cloud | New platform | Delivery | Due 2027-01-04 |

**Gap.** Whether sandbox access has been requested, and whether Dee Okafor has accepted the technical owner role. Owner: Callum Reyes, chased by Jun Park. Resolve by 2026-11-20. Blocks: kickoff.

##### 05 Solution shape

Standard: ownership boundaries at orientation depth. The Solution Brief was not supplied and holds the detail.

- Service Cloud owns cases, queues and routing.
- NetSuite owns orders and is read from only.
- Zendesk is retired for these queues after a one-way migration.

##### 06 Decisions inherited

Standard: status, owner and rationale on each; open ones visible.

| Decision | Made by | Status |
|---|---|---|
| Three queues only (SOW 2a) | Signed SOW, 2026-10-30 | Settled |
| NetSuite read-only (SOW 2c, 3) | Signed SOW, 2026-10-30 | Settled |
| Migration cap 24 months, 40,000 cases (SOW 2d) | Signed SOW, 2026-10-30 | **Open.** Client asked on 2026-11-02 for 36 months, about 58,000. Owner: Tom Aldous |

**Gap.** No delivery-lens or maturity-gap flags were supplied from scope review. This is an unknown, not an absence. Owner: Tom Aldous. Resolve by 2026-11-06. Blocks: warm transfer.

##### 07 Sell-cycle promises

Standard: each promise sourced to where and when it was said; off-contract ones flagged with an owner.

**Searched:** Slack #tidewater, the AE's sent mail, the 2026-09-18 demo recording. **Not searched:** client-side threads of Marguerite Lindqvist and Dee Okafor, and the mailboxes of Tom Aldous and Jun Park beyond one cited email. "Nothing else found" applies only to what was searched.

| # | Promise | Said where, by whom | In SOW? | Owner and route |
|---|---|---|---|---|
| 1 | "We'll look at a customer portal as a phase 2 and won't charge for the design." | Demo call 2026-09-18, Priya Nandakumar | No. **Flagged liability** (portal is out, SOW section 3) | Tom Aldous: honor, price, or reset before kickoff |
| 2 | "Most Zendesk macros can come across as canned responses." | Email to Callum Reyes 2026-10-06, Jun Park | No. SOW silent. **Flagged** | Sam Whitcombe: confirm feasibility, then honor or reset |
| 3 | "We'll do our best" to be live before the 2027-02-14 half-term peak | Slack #tidewater 2026-10-21, Priya Nandakumar | No. **Conflicts with** hard date 2027-02-26 | Tom Aldous: reset in writing |
| 4 | Hard go-live 2027-02-26 | Executed SOW | Yes, SOW section 5 | None needed |

**Conflict, not a promise:** the 2026-11-02 email asks for 36 months of migration. The SOW says 24 (section 2d). Both values stand; it is routed to the Pursuit Lead and unanswered.

##### 08 Risks, assumptions, gaps

Standard: severity, owner, and a mitigation that is more than a restatement.

| Severity | Risk | Mitigation | Owner |
|---|---|---|---|
| High | Client wants about 58,000 cases against a 40,000 cap on a fixed fee | Reply to the client; decide between holding the cap and a change order before kickoff | Tom Aldous |
| High | Client expects go-live before 2027-02-14; SOW says 2027-02-26 | Reset in writing with the COO | Tom Aldous |
| Medium | NetSuite owner never met the team; access is a client assumption due 2027-01-04 | Introduce Dee Okafor this month; send a written access request | Jun Park |
| Medium | The 30-day measurement runs to about 2027-03-28; Zendesk renews 2027-03-01 | Get the client's renewal position; keep Zendesk readable until acceptance | Sam Whitcombe |
| Low to medium | Agents are nervous about the change (AE note, Inferred) | Involve agents in the 14 UAT scripts | Callum Reyes |

**Assumptions and what breaks if false**

- Sandbox access by 2027-01-04. If false, the 2027-02-01 UAT start moves, and the 40% milestone with it.
- 24 months fits within 40,000 cases. If false, migration effort exceeds the priced scope.

##### 09 The people

Standard: whose metric the project protects, who holds each dependency, every mismatch explicit.

| Side | Deal cycle | Delivery |
|---|---|---|
| Ours | Priya Nandakumar (AE), Tom Aldous (Pursuit Lead), Jun Park (CSE) | Sam Whitcombe (Solution Lead); Program Lead unassigned |
| Client | Marguerite Lindqvist (COO, signed), Callum Reyes (Head of Support) | Callum Reyes (owns go-live); Dee Okafor (NetSuite) |

- **Mismatch 1.** Marguerite drove the deal and signed, but no source places her on the delivery side. She raised the peak-season question (Slack 2026-10-21), so her expectation survives kickoff even if she does not.
- **Mismatch 2.** Dee Okafor owns the NetSuite dependency and was in no deal meeting. "Will sort access" is Callum's statement, unverified.
- **Postures.** Callum is the day-to-day contact (AE). Agents are nervous (AE note, Inferred). No posture is recorded for Marguerite or Dee.

**Gap.** Whether Marguerite joins the steering group, and who the Program Lead is. Owner: Tom Aldous. Resolve by 2026-11-13. Blocks: kickoff.

##### 10 Relevant prior engagements

Standard: a named artifact to reuse, with a pointer.

- Harbour & Vale Foods case routing (2025). Reuse `Routing-rules-template.xlsx` in Drive as the starting sequence for the three queues. The file was named in the AE notes and not opened for this package.

##### 11 Discovery sessions

Standard: each session has an owner, the right attendees, and an output that closes a named question. Ordered by risk.

| # | Session | Owner | Attendees | Output | Closes |
|---|---|---|---|---|---|
| 1 | Settle migration volume: 24 or 36 months, and the record count | Tom Aldous | Sam Whitcombe, Callum Reyes, client Zendesk admin | Case counts by month; written decision to hold the cap or raise a change order | Section 06 open decision; section 08 migration risk |
| 2 | Confirm access and ownership for NetSuite and both sandboxes | Jun Park | Dee Okafor, Callum Reyes | Named NetSuite owner in writing; logins verified by each side | Section 04 gap; section 09 mismatch 2 |
| 3 | Reset go-live expectation against the 2027-02-14 peak | Tom Aldous | Marguerite Lindqvist, Callum Reyes | Written client confirmation of 2027-02-26, or a change order request | Promise 3 |

[trimmed: the rest of this file, about 571 more words, is not shown]
