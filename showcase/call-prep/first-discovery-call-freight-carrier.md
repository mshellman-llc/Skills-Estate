---
skill: call-prep
title: First discovery call with a regional freight carrier
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: e12fbf1eacebf3e8d801f837e8453941265cc49ad27c2683da4b9d4b391cff60
---

## Request

Prep me for Thursday's 45-minute first discovery call with Tidewater Freight Co. Dana Whitfield (VP Customer Experience) is the lead and Marcus Oyelaran (IT) joins for the second half. Everything I have is in ./inputs/.

## Inputs

Run of the built `call-prep` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Files it also produced, not shown here: `tidewater-freight-evidence.json`, `tidewater-freight-pursuit-brief.md`.

#### account-notes.md

#### Tidewater Freight Co. — account notes (fictional)

- Regional less-than-truckload (LTL) carrier, 14 terminals across Virginia, the Carolinas and Georgia. About 1,900 employees, 1,100 tractors.
- Revenue about $410M (FY2025, company-reported in a trade-press interview).
- Customer service runs from one contact center in Norfolk: 62 agents, three shifts. Today they use a 2014-era on-premise ticketing tool ("ServiceDesk Pro") plus shared Outlook inboxes for claims.
- Transportation management system (TMS): "RouteLine 9", hosted by the vendor, REST API available for shipment status and proof-of-delivery images.
- Pain points raised by the inbound lead form: customers can't self-serve shipment status; freight-claims cycle averages 41 days; no single view of a shipper account across terminals.
- Inbound lead came from the VP of Customer Experience after a webinar on Service Cloud for logistics.


#### contacts.md

#### Contacts (fictional)

| Name | Title | Notes |
|---|---|---|
| Dana Whitfield | VP, Customer Experience | Lead source. Owns the contact center and claims. Joined 8 months ago from a parcel carrier. |
| Marcus Oyelaran | Director, IT Applications | Owns RouteLine integration. Skeptical of "another platform." |
| Priya Raman | Claims Manager | Runs a team of 9 claims adjusters. |
| Tom Becker | CFO | Not on the first call; signs anything over $250K. |


#### email-thread.md

From: Dana Whitfield
To: (our account executive)
Subject: Re: Intro call Thursday

Thanks for reaching out. Thursday at 10 works. Marcus from IT will join for the second half. Our big question is whether we can get customers tracking shipments and filing claims online by peak season next fall, and what that would roughly cost. We've been burned by a long implementation before, so we care a lot about phasing.

## Output

### Tidewater Freight Co.: prep for Thursday 2026-11-05, 10:00

I built a call brief for Thursday and seeded a Pursuit Brief, since neither existed. Everything below comes from your three input files. None of them is dated, so treat every fact as "as of an unknown date."

#### Top three facts

1. **Dana's ask is specific and time-boxed.** She wants customers tracking shipments and filing claims online by peak season next fall, wants a rough cost, and cares about phasing because a past implementation ran long (her email).
2. **The pain is operational.** One Norfolk contact center (62 agents), a 2014-era on-premise ticketing tool, claims in shared Outlook inboxes, a 41-day average claims cycle, and no cross-terminal account view (account notes, from their inbound form).
2. **Marcus holds the feasibility answer.** He owns the RouteLine 9 integration, and RouteLine has a REST API for shipment status and proof-of-delivery images (contacts, account notes). Whether it covers what a claims portal needs is unknown.

#### Landmines

- **Cost.** Dana asked for a rough cost in writing. You gave me no pricing, and pricing belongs to scoping-agent. The brief sets the intent: name the cost drivers, promise a ranged estimate after scoping, give no number.
- **Marcus.** Your contacts sheet has a note characterizing him. Don't repeat it to anyone. The brief builds his half around the thing the sheet supports: he owns the integration.
- **Tom Becker's $250K signing level** is internal. Ask Dana about approvals in general terms.
- **Dana's background** (8 months in role, from a parcel carrier) is internal. Don't assume she lived through the past implementation, and don't compare Tidewater to her old employer.
- **Who started this?** The account notes say an inbound form after a webinar; Dana's reply says "Thanks for reaching out." Don't say which.
- **Service Cloud** was the webinar topic. That shows interest, not a product choice. Don't pitch before she defines "online tracking and claims."

#### The call plan

Objective: learn what phase 1 means in Dana's words and what the RouteLine and ServiceDesk Pro environment allows. Not a price, a date, or a solution commitment.

| Minutes | Segment | Lead |
|---|---|---|
| 0-3 | Introductions, confirm time box, Marcus joins at about minute 22 | You |
| 3-12 | Why now, what "online tracking and claims" means, the peak-season date | Dana |
| 12-22 | Claims journey, account view, the earlier implementation | Dana |
| 22-25 | Marcus joins; one-minute recap | You |
| 25-36 | RouteLine API, ServiceDesk Pro, Outlook inboxes, constraints, security review | Marcus |
| 36-43 | React to a phased shape; cost question | Both |
| 43-45 | Next steps and owners | You |

Highest-ranked questions (13 in the full brief):

1. What does "filing claims online" include: submitting with documents, tracking status, or both? What would a customer see on day one?
2. When does peak season start, and what must be live before it? What is the smallest thing that would help?
3. What made the earlier implementation long, and what would a phase need to deliver to count as a win?
4. How does a claim travel from first email to payment, and how is the 41 days measured?
5. What is your approval process for a project like this, and who else decides?
6. For Marcus: what does the RouteLine API expose, what are the access limits, and what must stay in ServiceDesk Pro and the Outlook inboxes?
7. For Marcus: what does your security and architecture review involve, and how long does it take?

#### Assumptions I made (none is safe to state as fact)

| ID | Assumption | Confidence | Safe to say to client |
|---|---|---|---|
| A-01 | "Online tracking and claims" means a customer portal for status and claim submission | Medium | Yes, as a question |
| A-02 | Shipment status is the cheapest first phase because the RouteLine API exists | Medium | Yes, as a hypothesis |
| A-03 | Claims filing needs a new intake and workflow because claims sit in Outlook | Medium | Yes, as a question |
| A-04 | The project may exceed $250K and need CFO approval | Low | No |
| A-05 | The past implementation predates Dana | Low | No |
| A-06 | IT will want proof the integration work is bounded | Medium | Yes, as a question |
| A-07 | "Peak season next fall" means fall 2027 | Low | Yes, as a question |
| A-08 | The webinar signals a platform category, not a chosen product | Medium | Yes, as a question |

#### Figures

All single-source, so there were no conflicts to reconcile, but none is independently confirmed.

| Figure | Value | Source |
|---|---|---|
| Claims cycle | 41 days average | Account notes (inbound form) |
| Agents | 62 | Account notes |
| Terminals | 14 | Account notes |
| Revenue | about $410M, FY2025 | Account notes (trade-press interview, not seen) |
| CFO signing threshold | over $250K | Contacts (internal, not for the client) |

#### Follow-up

- Same day: send Dana her goals and phasing criteria in her words. Propose a claims-workflow session with Priya Raman (Claims Manager) and a technical session with Marcus.
- Within one day: hand the transcript or notes to discovery-brief.
- Within two days: update the Pursuit Brief.
- Before any cost conversation: pass confirmed scope to scoping-agent.

Recommended sequence in the Pursuit Brief: Call 1 discovery (Thursday), Call 2 claims workflow with Priya, Call 3 RouteLine technical session with Marcus, Call 4 scope and cost review with Dana.

#### Gaps and what I cut

- **Sections omitted:** talk track (no recording of your voice, so the brief gives intents only), Q&A bank (no questions from Tidewater beyond Dana's two asks), and the HTML brief and atomic knowledge base (not enough evidence to earn them).
- **Public research not done.** The run was limited to your inputs, so there are no filings, trade-press, competitor, or RouteLine vendor findings. The $410M figure is second-hand.
- **No CRM, calendar, or discovery ledger available.** A zero-result CRM search is a finding when run; here it was not run. Call length, time zone, and our side's attendees are unconfirmed beyond "Thursday at 10" in Dana's email. I read "Thursday" as 2026-11-05 from today's date.
- **Staleness:** every source is undated.
- **Scripts not run.** I could not run scripts in this session, so I applied their documented rules by hand:
  - `check_pursuit_brief.py` (both modes): I confirmed each required section heading, `Assumption` labels on every assumptions bullet, the last-updated line, the Purpose, Desired outcome and Prerequisites lines on each call, the link to the Pursuit Brief, no placeholders, and no em dashes. I read these off the text rather than executing the checker.
  - `reconcile.py`: every figure has a source and a stated meaning, and no figure appears with two values. It would warn that no source carries a date.
  - **Writing review:** I did not run writing-integrity or the quality gate, and the brand-renderer step did not apply because no styled artifact was produced. I read the prose by hand against the writing standard. I have no counts to report.

#### Biggest judgment call: no number on Thursday

I recommend giving Dana no cost figure on this call. The case against: she asked in writing, a first call that dodges the one question she raised can read as evasive, and a defensible order-of-magnitude range (for example, by phase) could build trust with a buyer who has been burned. The case for holding: I have no pricing basis, and the scope is undefined (portal only, or claims workflow and account view too?). Whatever you say first becomes her anchor, and she will carry it to the CFO. If you decide to give a range, get it from scoping-agent beforehand and tie it to a named phase, not to the whole ask.

A second fork: I put shipment status first as the likely phase 1 (A-02). If Dana says claims filing is the real pain, that ordering flips, and the claims-workflow call with Priya moves ahead of the technical call.

#### Files (in `./out/`)

- `tidewater-freight-call-brief-2026-11-05.md`: the call brief. Full content is summarized above, including the agenda, ranked questions, risks, and the assumptions register.
- `tidewater-freight-pursuit-brief.md`: the seeded Pursuit Brief, with context, situation, outcomes, confirmed facts, assumptions, unknowns, stakeholders and missing roles, risks, qualification, four recommended calls, next steps, and decisions needed.
- `tidewater-freight-evidence.json`: the figure and sensitivity ledger.

### File: tidewater-freight-call-brief-2026-11-05.md

#### Tidewater Freight Co. call brief: first discovery call, Thursday 2026-11-05, 10:00

All people and figures come from the fictional files in `inputs/`. Source tags: [AN] account-notes.md, [CT] contacts.md, [ET] email-thread.md. None of the three files carries a date, so every fact is as of the file's last edit, which is unknown.

This is Call 1 in `tidewater-freight-pursuit-brief.md` (the Pursuit Brief). What it should feed back: confirmed scope language, the phasing answer, the integration facts, and who else must be in the room.

##### Call objective

1. Learn what "customers tracking shipments and filing claims online by peak season next fall" means to Dana in practice, and what a phased version she would accept looks like.
2. Learn from Marcus in the second half what the RouteLine 9 and ServiceDesk Pro environment allows, so the next call can be scoped.

##### Desired decisions or outcomes

- Dana's own words for the phase 1 target and the date it must be live.
- Agreement on a claims-workflow session with Priya Raman and the person who owns the Outlook claims inboxes.
- Marcus's agreement to a technical follow-up on the RouteLine API.
- Agreement on how the cost conversation will proceed (see Risks, item 1).
- Not an outcome of this call: a price, a solution commitment, or a date commitment.

##### Attendees and roles

| Person | Role | In the room | Source |
|---|---|---|---|
| Dana Whitfield | VP, Customer Experience; owns contact center and claims; call lead on their side | Whole call | [CT], [ET] |
| Marcus Oyelaran | Director, IT Applications; owns RouteLine integration | Second half | [CT], [ET] |
| Our account executive (you) | Runs the call | Whole call | [ET] |

Not on the call: Priya Raman (Claims Manager, 9 adjusters) and Tom Becker (CFO, signs anything over $250K) [CT]. Our side's other attendees are unknown; add a note-taker if one is available.

##### Known context

- Tidewater is a regional LTL carrier: 14 terminals in Virginia, the Carolinas and Georgia, about 1,900 employees, 1,100 tractors [AN].
- Revenue is about $410M for FY2025, company-reported in a trade-press interview [AN]. We have not seen the interview.
- One Norfolk contact center, 62 agents, three shifts. Tools are ServiceDesk Pro (2014-era, on-premise) plus shared Outlook inboxes for claims [AN].
- TMS is RouteLine 9, vendor-hosted, with a REST API for shipment status and proof-of-delivery images [AN].
- Pain points from the inbound form: no customer self-service for shipment status, claims cycle averages 41 days, no single view of a shipper account across terminals [AN].
- Dana's email: Thursday at 10 works, Marcus joins for the second half. Her big question is whether customers can track shipments and file claims online by peak season next fall, and roughly what it costs. They have been burned by a long implementation before and care about phasing [ET].
- Lead source was Dana after a webinar on Service Cloud for logistics [AN, CT].

Figures (single source each; no conflicts found, but none is independently confirmed):

| Figure | Value | Source | Note |
|---|---|---|---|
| Claims cycle | 41 days average | [AN], from the lead form | Dana's team's number. Ask how it is measured (filing to payment? first notice to close?) |
| Agents | 62, three shifts | [AN] | |
| Terminals | 14 | [AN] | |
| Revenue | about $410M, FY2025 | [AN] | Trade-press, company-reported, not seen |
| Approval threshold | over $250K needs CFO | [CT] | Internal. Do not cite to the client |

##### Run of show

1. Open neutrally and confirm the time box and that Marcus joins at about minute 22.
2. Let Dana define success in her own terms before anything is proposed.
3. Walk the claims journey from the customer's side, then the agent's side.
4. Ask about the earlier long implementation through the lens of phasing.
5. When Marcus joins, recap in one minute and hand him the floor on integration.
6. Test a phased shape as a hypothesis, not a proposal.
7. Handle the cost question (intent below), agree next steps, stop on time.

##### Agenda

| Minutes | Segment | Lead |
|---|---|---|
| 0-3 | Introductions, confirm time box and goals for the call | You |
| 3-12 | Dana: why now, what "online tracking and claims" means, the peak-season date | Dana |
| 12-22 | Dana: claims journey, contact center, account view, the earlier implementation | Dana |
| 22-25 | Marcus joins; one-minute recap | You |
| 25-36 | Marcus: RouteLine API, ServiceDesk Pro, Outlook inboxes, constraints, security review | Marcus |
| 36-43 | React to a phased shape; cost question | Both |
| 43-45 | Next steps and owners | You |

##### Questions

No discovery ledger exists for this pursuit, so every question below is call-specific, written from the three inputs. Ranked by effect on the next step.

For Dana (minutes 3-22):

1. What does "customers filing claims online" include for you: submitting a claim with documents, tracking its status, or both? What would a customer see on day one? (Resolves A-01.)
2. When does peak season start, and what has to be live before it? What happens to the business if only part is ready? (Resolves A-07.)
3. You mentioned a long implementation that hurt. What made it long, and what would a phase need to deliver to count as a win? (Phasing criteria. Do not ask who was at fault.)
4. How does a claim travel today, from the customer's first email to payment? Where does it wait? How is the 41 days measured?
5. Which customers or shippers matter most for self-service, and what do they ask your agents most often?
6. Who besides you decides on this, and what does your approval process look like for a project of this kind? (Opens the money and sign-off path without citing the CFO threshold. Resolves A-04.)
7. How are you measuring contact-center performance today, and which number would you want to move first?

For Marcus (minutes 25-36):

8. What does RouteLine's API expose today for shipment status and proof of delivery, and who at the vendor controls changes to it? (Resolves A-02.)
9. What are the limits: authentication, call volumes, who can approve new API consumers, any contract terms with the vendor?
10. Which parts of ServiceDesk Pro and the Outlook claims inboxes would have to stay, and which could be retired? (Resolves A-03.)
11. What does your security and architecture review look like for a new customer-facing system, and how long does it usually take?
12. What would make a new platform a bad idea from where you sit? What would make it acceptable? (Let him define the bar. Phrase it about the project, not about him.)

For both (minutes 36-43):

13. If the first release covered shipment status only, with claims filing following, would that still help you meet peak season? What is the smallest thing that would?

##### Risks and sensitivities

1. **The cost question.** Dana asked "what that would roughly cost" in writing [ET]. No pricing was supplied for this run, and scoping and pricing belong to scoping-agent. Intent: acknowledge the question, say what drives cost (which channels, which integrations, how many phases), and commit to a ranged estimate after the scoping conversation. Do not offer a number. This is the presenter's decision; see the judgment call in the chat summary.
2. **Do not repeat the contacts-sheet note about Marcus.** It characterizes an individual. Plan the second half around his ownership of the RouteLine integration, which is the fact the sheet supports.
3. **Dana's tenure and background.** The contacts sheet says she joined 8 months ago from a parcel carrier [CT]. Do not assume she owned or witnessed the earlier implementation (A-05), and do not compare Tidewater to her previous employer unless she does.
4. **Client statements are internal.** Everything Dana put on the lead form and in her email about her organization can be reflected back to her. Do not carry it to Priya, Tom, or anyone else without her say.
5. **CFO threshold.** Tom Becker's $250K signing level [CT] is internal. Do not cite it. Ask about approvals in general terms (Question 6).
6. **Who started this.** The account notes say the inquiry arrived through a lead form after a webinar; Dana's reply says "Thanks for reaching out," which reads as though we initiated contact. Do not state which happened. Open with the topic, not the origin.
7. **Product assumption.** The webinar was on Service Cloud for logistics [AN]. That shows interest; it does not show Dana wants that product. Do not pitch before Question 1 is answered.
8. **Timeline pressure.** Peak season "next fall" is roughly 10 to 11 months from today if it means fall 2027 (A-07). Do not agree it is achievable.

Response intents to Dana's two stated asks (no spoken lines; no recording of the presenter's voice was supplied, so only intents are given):

- Online tracking and claims by peak season: reflect the goal back, ask what minimum counts, state that feasibility depends on Marcus's answers and a scoping step.
- Rough cost: see Risks, item 1.

##### Facts, assumptions, and unknowns

Facts (all from supplied inputs; see Known context for sources): the company profile, the tools in use, the three pain points, Dana's two questions and her concern about phasing, who joins and when, and the four named contacts and their titles.

Assumptions (also registered in the Pursuit Brief):

| ID | Assumption | Confidence | Basis | Safe to say to client? |
|---|---|---|---|---|
| A-01 | "Tracking and filing claims online" means a customer-facing portal covering shipment status and claim submission | Medium | Dana's email wording | Yes, as a question |
| A-02 | Shipment status is the cheapest first phase because RouteLine already offers a REST API for it | Medium | Account notes list the API; nothing confirms access terms | Yes, as a hypothesis for Marcus to test |
| A-03 | Online claims filing needs a new intake and workflow, since claims live in shared Outlook inboxes today | Medium | Account notes | Yes, as a question |
| A-04 | A project of this kind may exceed $250K and need CFO approval | Low | Threshold from contacts sheet; spend unknown | No |
| A-05 | The earlier long implementation predates Dana | Low | She joined 8 months ago; nothing else | No |
| A-06 | IT will want evidence that RouteLine integration work is bounded and low-risk | Medium | Marcus owns the integration | Yes, as a question about constraints |
| A-07 | "Peak season next fall" means fall 2027 | Low | Email is undated and gives no months | Yes, as a question |

Unknowns:

- Budget, funding source, and who approves. No source.
- What the earlier implementation was, and when it happened.
- Whether other platforms are under evaluation. No competitor information supplied.
- The peak-season dates and the volume then.
- The RouteLine API terms and its coverage of claims-relevant data.
- Whether Priya's adjusters or anyone else uses a claims tool beyond Outlook.
- Time zone and format of the call.

##### Follow-up plan

- Same day: send Dana a short thank-you note with her stated goals and the phasing criteria in her words, and propose the claims-workflow session with Priya Raman and the technical session with Marcus.
- Within one day: hand the call transcript or notes to discovery-brief for ingestion and question closure.
- Within two days: update `tidewater-freight-pursuit-brief.md` with confirmed facts, closed unknowns and any change to the recommended call sequence.
- Before any cost discussion: pass the confirmed scope to scoping-agent for a ranged estimate.
