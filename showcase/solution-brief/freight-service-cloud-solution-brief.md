---
skill: solution-brief
title: Solution brief for a freight carrier service platform
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: f7f08afe359072e7f542a43e2a827d1e0f425a5d91789f790a69f3282f401978
---

## Request

Write the solution brief for Tidewater Freight Co. phase one so our delivery lead can judge whether it's deliverable before we send the proposal. Everything known is in ./inputs/. Evidence is limited to these notes — say where it's thin.

## Inputs

Run of the built `solution-brief` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### solution-notes.md

#### Tidewater Freight Co. — account notes (fictional)

- Regional less-than-truckload (LTL) carrier, 14 terminals across Virginia, the Carolinas and Georgia. About 1,900 employees, 1,100 tractors.
- Revenue about $410M (FY2025, company-reported in a trade-press interview).
- Customer service runs from one contact center in Norfolk: 62 agents, three shifts. Today they use a 2014-era on-premise ticketing tool ("ServiceDesk Pro") plus shared Outlook inboxes for claims.
- Transportation management system (TMS): "RouteLine 9", hosted by the vendor, REST API available for shipment status and proof-of-delivery images.
- Pain points raised by the inbound lead form: customers can't self-serve shipment status; freight-claims cycle averages 41 days; no single view of a shipper account across terminals.
- Inbound lead came from the VP of Customer Experience after a webinar on Service Cloud for logistics.


#### Proposed solution (fictional) — after discovery calls 1 and 2

- Service Cloud for 71 users; Experience Cloud portal for shippers (tracking by PRO number, online claims with photo upload).
- Integration: middleware (MuleSoft is NOT licensed; client already owns Azure Integration Services) calling RouteLine 9 REST API for shipment status and POD images. Rate limit 20 req/s per tenant. Read-only in phase one.
- Claims: case record type "Freight Claim" with approval routing over $2,500; claims data stays in Salesforce in phase one (vendor confirmed RouteLine cannot accept claim write-back until its 2027 release).
- Migration: ~3,500 claims from spreadsheet + ServiceDesk Pro CSV export; 120 KB articles from SharePoint.
- Team: client IT has 3 people part-time; client wants to own the platform after hypercare.
- Commercials: ROM range given was $360K–$470K; client signals phase one must stay under $500K.
- Timeline: go-live before October peak; contract signature expected in about 6 weeks; ~10 months available.
- Known risks raised: RouteLine API outages during month-end; portal load during peak (Dana estimates 6,000 tracking lookups/hour at peak); Marcus's team capacity.

## Output

### Tidewater Freight Co. phase one: Technical Readiness Memo

**Verdict: not ready for a full Solution Brief. Don't send the proposal on technical grounds yet.** The evidence gate returned Insufficient, so I stopped at this memo. I did not build the solution graph or the ten-view brief. The notes support a plausible shape. They don't support a judgment that it can be delivered.

#### 1. Direction worth retaining

These points are inferred from two sets of notes. None comes from an executed commitment or a current authorized design record.

- **Shape:** Service Cloud for 71 users and an Experience Cloud shipper portal. The portal offers tracking by PRO number and online claims with photo upload. [S2]
- **Integration:** Azure Integration Services, which the client already owns, replaces MuleSoft, which isn't licensed. It calls the RouteLine 9 REST API for shipment status and proof-of-delivery (POD) images. It is read-only in phase one. [S2]
- **Claims:** a "Freight Claim" case record type, with approval routing above $2,500. Claims data stays in Salesforce because the vendor says RouteLine can't accept write-back until its 2027 release. [S2]
- **Migration:** about 3,500 claims from a spreadsheet and a ServiceDesk Pro CSV export, plus 120 SharePoint articles. [S2]
- **Peak load looks manageable on paper.** Dana's estimate of 6,000 lookups an hour is about 1.7 requests a second. That is roughly 8% of the 20 req/s tenant limit, if each lookup makes one RouteLine call. It could be far higher if a lookup also fetches POD images or retries. The call pattern isn't in the notes. This is my arithmetic, not a sourced figure. [S2]

#### 2. Gate result (run by hand)

Required domains come from the `solution_brief` contract. Both sources are meeting or lead-form notes with bounded authority, and the revenue figure is trade-press. Nothing is Confirmed at authority 70 or higher. Every domain that has a claim is therefore at most Inferred, which the gate counts as Conditional.

| Domain | Result | Why |
|---|---|---|
| Scope | Conditional | Inclusions are listed. There is no exclusion list and phase two is undefined. |
| System context | Conditional | Salesforce, RouteLine, Azure, SharePoint and ServiceDesk Pro are named. Ownership and data flow are not. |
| Architecture | Conditional | No component design. Middleware is named but its role, hosting and error handling are not described. |
| Integrations | Conditional | One interface (RouteLine REST). Authentication, payloads, POD image size and the call pattern are unknown. |
| Data | Conditional | Migration volumes only. There is no field mapping, data quality, retention or cutover approach. |
| Decisions | Conditional | Only the middleware choice, and it was forced by licensing. The approver for claims over $2,500 is not named. |
| Risks | Conditional | Three risks are named, with no owner, trigger or mitigation. |
| Assumptions | Conditional | Nothing is stated as an assumption, so none has an owner or closure condition. |
| **Security and governance** | **Insufficient** | No evidence. Nothing covers shipper identity and login, access to claim and POD data, or audit of approvals. |
| **Failure paths** | **Insufficient** | The risks name RouteLine month-end outages and peak portal load. No behavior is defined for what the portal and agents see when RouteLine is down. |
| **Technical approval conditions** | **Insufficient** | None exist. |

Overall: **Insufficient.** Three required domains have no usable claim.

#### 3. Blockers and closure conditions

Owners are roles, not people. The notes name no one on our side, and "Dana" and "Marcus" have no stated role or surname.

| # | Blocker | Owner (proposed) | Closure condition | Work that must wait |
|---|---|---|---|---|
| B1 | Security model absent: shipper authentication, data sharing across terminals, PII in claims and photos, approval audit | Solution architect with client IT/security lead | Written security and identity approach agreed with the client's technical owner | Portal design, the Freight Claim record type, the data model |
| B2 | No designed failure behavior for RouteLine outage, rate limiting or peak portal load | Solution architect | For each interface: cache or stale-data policy, what the shipper sees, what agents see, retry and alerting rules. The RouteLine month-end outage pattern is quantified, and Dana's 6,000/hour is tied to the expected call count per lookup. | Interface build, load testing, the go-live date |
| B3 | Interface contract unverified. We have no RouteLine API documentation or sandbox access and no vendor confirmation of the rate limit. The "no write-back until 2027" statement is a relayed vendor claim. | Delivery lead with client TMS owner | Vendor-issued API spec, rate-limit terms and write-back statement received in writing | Any build-reference detail; the read-only boundary should not be treated as settled until then |
| B4 | No bottom-up estimate. The $360K–$470K ROM has no stated basis. The under-$500K ceiling leaves $30K–$140K of headroom. | Deal Desk, from the delivery lead's estimate | An effort estimate by workstream and role that reproduces the range | The proposal price and any technical-to-price traceability |
| B5 | No delivery staffing shape. Only the client side is stated: 3 part-time IT people who want to own the platform after hypercare. | Delivery lead | Roles, allocation and a client-enablement plan that fit part-time capacity | The staffing feasibility judgment |

#### 4. Other gaps and tensions to resolve

- **Timeline.** Signature is about 6 weeks out and about 10 months are available. From today (2026-11-04) that puts signature near mid-December 2026 and the end of the window near October 2027. "Go-live before October peak" then leaves almost no slack for hypercare. The notes don't say when the peak starts or whether "10 months" ends at go-live or at the end of hypercare. This is my inference from the dates.
- **User count.** The contact center has 62 agents, but the proposal licenses 71 users. The 9 extra seats are unexplained. They could be supervisors, claims staff or terminal users, and the answer changes both licensing and scope.
- **"Phase one" is not defined as a boundary.** Excluded and future scope are not listed. That includes write-back to RouteLine, which is only implied for 2027 or later.
- **Migration risk is unexamined.** 3,500 claims arrive from two sources (a spreadsheet and a CSV), and the notes mention no deduplication, status mapping or open-claim cutover. Claims also live in shared Outlook inboxes today, and nothing says whether those are in migration scope.
- **Ownership.** The client wants to own the platform after hypercare with 3 part-time people. That is an enablement and managed-support question, not just a risk line.
- **Risks have no owner.** "Marcus's team capacity" is the only people-related risk, and the notes don't say whose team it is.
- **Business drivers are asserted, not measured.** The 41-day claims cycle and the lack of a single account view come from the lead form. No target or measure of success is stated.

#### 5. Next gate

1. Close B1–B3 by getting the security approach, failure-behavior design and RouteLine vendor documentation. Record each as a governed claim with an owner.
2. Confirm the open items in section 4 on a third discovery call, which would be the first source with real authority. Ask for the peak dates, the 9 extra seats, Dana's and Marcus's roles, and the claims approver.
3. Get the delivery lead's bottom-up estimate and staffing (B4, B5) so Deal Desk can reconcile them against the ROM.
4. Rerun the content-sufficiency gate for the `solution_brief` contract. If it comes back Conditional with owners and closure conditions, build the approval-mode brief.

Whether to send the proposal is a commercial call. If it must go before B1–B3 close, make the proposal conditional on discovery outputs and don't commit to a date or fixed price.

#### 6. Evidence references

| ID | Source | Authority and limits |
|---|---|---|
| S1 | `inputs/solution-notes.md`, "account notes". Lead-form facts and a trade-press revenue figure. | Low. Self-reported by the client. The $410M revenue is company-reported in a trade-press interview. |
| S2 | `inputs/solution-notes.md`, "Proposed solution", written after discovery calls 1 and 2. | Bounded, because they are meeting notes. No executed commitment, no signed statement of work, and no vendor documents. |

#### How this was produced

- Both scripts, `evidence_core.py` and `solution_graph.py`, were **not run**. I applied the gate by hand from `_runtime/evidence-core/scripts/evidence_core.py`. A domain with no claim is Insufficient, and a domain with only Inferred claims is Conditional. Any Insufficient domain makes the whole gate Insufficient and terminal.
- The Insufficient result means no graph was assembled, as the skill requires. No JSON ledger or gate-report file was written.
- The release-gate checks (writing-integrity, brand-renderer and quality-gate scripts) were not run. I reviewed the prose by hand against the readout-brief register. This memo is plain Markdown and has no brand rendering.
- Gaps went into this memo because it is the terminal artifact. There are no `[TBD]` markers.

#### Files

- `out/answer.md`: this memo. The full content is above.
