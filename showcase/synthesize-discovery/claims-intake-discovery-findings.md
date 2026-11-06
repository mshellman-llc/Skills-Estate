---
skill: synthesize-discovery
title: Insurance claims intake: findings from two discovery calls
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 53a74977869d0e0946aefa1977d7a0ebf5826d6f86a327eb045599245b8510b2
---

## Request

I've attached notes from two discovery calls with Fernbrook Mutual's claims team for our intake-redesign project. Can you synthesise them into findings for the steering readout on Friday? Keep any quotes exactly as spoken.

## Inputs

Run of the built `synthesize-discovery` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### call-1-claims-ops.md

#### Call 1: Claims operations lead (2026-10-20, 45 min, transcript excerpts)

Attendees: Priya Raman (Head of Claims Operations, Fernbrook Mutual); Dana Whitlock (consultant lead); Leo Marsh (consultant analyst).

[02:10] Dana: Walk us through what happens when a claim comes in.
[02:40] Priya: "Claims arrive by phone, the web form and email, and each one lands in a different queue. Somebody has to retype the email ones by hand."
[06:15] Priya: "We miss our own five-day first-contact target on about a third of claims. I'd have to pull the exact figure, but it's a third, give or take." (Priya's estimate; no report supplied.)
[11:30] Dana: What stops you fixing it?
[11:50] Priya: "The policy system is the blocker. Anything that touches it needs a change request, and the queue for those is months long."
[19:05] Priya: "I don't need a fancy portal. I need the adjusters to stop chasing missing photos."
[27:20] Priya: "Our fraud team would hate anything that auto-approves small claims. I'd want them in the room before we talk about it."
[38:00] Leo: Would a status page for customers help?
[38:20] Priya: "Maybe. Honestly the phone volume is the thing my director watches."

#### call-2-adjuster.md

#### Call 2: Senior adjuster (2026-10-22, 30 min, transcript excerpts)

Attendees: Tomas Okafor (Senior Claims Adjuster, Fernbrook Mutual); Leo Marsh (consultant analyst).

[01:45] Tomas: "Half my morning is emailing people for photos they already sent to a different address."
[05:10] Leo: How often do you have to re-request?
[05:25] Tomas: "Most water-damage claims. Maybe seven in ten. I haven't counted."
[09:40] Tomas: "The web form lets people submit with no photos at all. I raised it with IT last spring and was told it's tied to the policy system."
[14:00] Tomas: "I'd actually be fine with auto-approving the small ones. Under five hundred, the fraud rate is tiny." (Tomas's view; no fraud data supplied.)
[21:30] Tomas: "Customers ring me directly because the main line has no answers for them."
[26:00] Leo: Is there a shared view of claim status?
[26:10] Tomas: "No. I keep my own spreadsheet."

## Output

I've synthesised both calls into findings for Friday's steering readout. Pain points 1 and 2 are the strongest, because both people raised them. Every figure is a spoken estimate with no report behind it, so don't present them as measured.

**Assumptions:** the audience is the steering group. The inputs are transcript excerpts, so I treated anything outside them as unknown. Granola and Fathom were not used.

#### TL;DR

Claims arrive by phone, web form and email, and each channel feeds a separate queue. The web form accepts claims without photos, so adjusters spend their time asking for photos, and customers phone adjusters because the main line has no status to give. Priya Raman (Head of Claims Operations) says the policy system blocks changes. Tomas Okafor (Senior Claims Adjuster) was told the same about the web form. They disagree on auto-approving small claims.

#### Pain points

| # | Pain point | Severity | Frequency | Evidence | Speaker |
|---|---|---|---|---|---|
| 1 | Adjusters chase missing or misrouted photos | High | Daily; about 7 in 10 water-damage claims (Tomas's estimate, not counted) | [19:05] call 1; [01:45], [05:25] call 2 | Ops lead and adjuster |
| 2 | Policy-system changes wait in a months-long queue | High | Ongoing | [11:50] call 1; [09:40] call 2 | Ops lead and adjuster |
| 3 | Three channels, separate queues, email claims retyped | Medium | Not stated | [02:40] call 1 | Ops lead |
| 4 | About a third of claims miss the five-day first-contact target | Medium | Priya's estimate; exact figure not pulled | [06:15] call 1 | Ops lead |
| 5 | No shared claim status; customers phone adjusters | Medium | Not stated | [21:30], [26:10] call 2 | Adjuster |

Reasons: 1 and 2 are high because two people raised them independently and the policy system is called a blocker. 3 is a stated frustration, not a block. 4 is an unverified estimate from one person. 5 comes from one speaker.

#### Job statement

Only one is supported by the sources: When a claim arrives without the photos needed to assess it, I want the missing items identified before an adjuster opens the file, so I can start assessment without a round of email requests. (Operations lead and adjuster, [19:05] call 1, [01:45] call 2.) No customer job is written, since no customer was interviewed.

#### Opportunity areas (proposed, not client requests)

1. Require photos at web-form submission for claim types that need them (pain point 1). Feasibility is unconfirmed because of the policy-system tie.
2. Route email and phone claims into one intake queue (pain point 3).
3. Give customers and the main line a claim status view (pain point 5). Priya was lukewarm, so it needs a link to phone volume.
4. Establish whether items 1 to 3 can avoid the policy system (pain point 2).

#### Verbatims

- "Claims arrive by phone, the web form and email, and each one lands in a different queue. Somebody has to retype the email ones by hand." Priya Raman, [02:40] call 1
- "We miss our own five-day first-contact target on about a third of claims. I'd have to pull the exact figure, but it's a third, give or take." Priya Raman, [06:15] call 1
- "The policy system is the blocker. Anything that touches it needs a change request, and the queue for those is months long." Priya Raman, [11:50] call 1
- "I don't need a fancy portal. I need the adjusters to stop chasing missing photos." Priya Raman, [19:05] call 1
- "Half my morning is emailing people for photos they already sent to a different address." Tomas Okafor, [01:45] call 2
- "The web form lets people submit with no photos at all. I raised it with IT last spring and was told it's tied to the policy system." Tomas Okafor, [09:40] call 2
- "Customers ring me directly because the main line has no answers for them." Tomas Okafor, [21:30] call 2

#### Speaker insights

**Priya Raman.** Priority is less adjuster rework, not a portal. She sees the policy system as the constraint, wants the fraud team involved before auto-approval is discussed, and says her director watches phone volume ([38:20]).

**Tomas Okafor.** Concerned with daily rework and direct customer calls. He keeps his own status spreadsheet ([26:10]) and has already tried to get the form changed through IT. He is open to auto-approving small claims.

#### Where they differ

Priya: "Our fraud team would hate anything that auto-approves small claims. I'd want them in the room before we talk about it." [27:20]. Tomas: "I'd actually be fine with auto-approving the small ones. Under five hundred, the fraud rate is tiny." [14:00]. His fraud-rate claim is a view without data. Her claim about the fraud team is an expectation, since that team wasn't interviewed.

#### Open questions and next steps

| Question | Follow-up | Owner |
|---|---|---|
| Real first-contact miss rate? | Request the first-contact report | Open |
| Photo re-request rate by claim type? | Sample claim files or email logs | Open |
| Can the web form change without a policy-system change? | Ask IT what ties them and the queue length | Open |
| Fraud team view and fraud rate under 500? | Interview the fraud team before presenting options | Open |
| What does Priya's director measure? | Ask Priya for phone-volume figures and target | Priya Raman, if she agrees |

No project owners are named in the sources, so ownership is open. If you keep a pursuit ledger, I can pass these questions to the maintain-discovery-record workflow.

#### Gaps

- Both sources are excerpts; other speakers and unquoted moments are unknown.
- No customer, IT or fraud voices. Findings 2 and 5 rest on one or two internal speakers.
- "About a third" and "seven in ten" are spoken estimates.
- "Under five hundred" has no currency stated.

#### Checks and limits

I could not run the bundled scripts (brand preflight, prose and writing checks, quality gate). I did a manual reading pass for the writing standard and checked each quote against the source text. No receipt exists, so treat this as a draft for your review, not a gate-passed final. I used no brand profile and saved a Markdown file only; there is no Word version.

#### Files

- `out/synthesize-discovery.md`: the full synthesis above, with the fuller wording of the speaker insights and gaps.
- `out/answer.md`: this reply.

### File: synthesize-discovery.md

#### Fernbrook Mutual claims intake: discovery synthesis

Sources: call 1 with Priya Raman, Head of Claims Operations (2026-10-20), and call 2 with Tomas Okafor, Senior Claims Adjuster (2026-10-22). Both are transcript excerpts, not full transcripts. Timestamps are in brackets. Consultant attendees were Dana Whitlock and Leo Marsh.

##### TL;DR

Claims reach Fernbrook Mutual through three channels that feed separate queues, and the web form accepts claims without photos. Adjusters then spend their time asking customers for photos, and customers phone adjusters because the main line has no status to give. Both interviewees describe the missing-photo chase as a daily burden. Priya says the policy system blocks changes, and Tomas was given the same reason for the form. The two disagree on auto-approving small claims. Both sets of figures are spoken estimates, and no reports were supplied.

##### Pain points

| # | Pain point | Severity | Frequency | Evidence | Speaker |
|---|---|---|---|---|---|
| 1 | Adjusters chase missing or misrouted photos | High | Daily; about 7 in 10 water-damage claims (Tomas's estimate, not counted) | [19:05] call 1; [01:45], [05:25] call 2 | Operations lead and adjuster |
| 2 | Changes touching the policy system wait in a months-long queue | High | Ongoing | [11:50] call 1; [09:40] call 2 | Operations lead and adjuster |
| 3 | Three channels land in separate queues; email claims are retyped by hand | Medium | Not stated | [02:40] call 1 | Operations lead |
| 4 | About one third of claims miss the five-day first-contact target | Medium | About a third (Priya's estimate; exact figure not pulled) | [06:15] call 1 | Operations lead |
| 5 | No shared view of claim status; customers phone adjusters directly | Medium | Not stated | [21:30], [26:10] call 2 | Adjuster |

Severity reasons:
- Pain points 1 and 2 are high because two people independently raised them, and the policy-system constraint is described as a blocker.
- Pain point 3 is medium because it is a stated frustration with manual work, not a block.
- Pain point 4 is medium because the target is internal and the figure is an unverified estimate from one person.
- Pain point 5 is medium because it comes from one speaker, though the status-page exchange at [38:20] offers partial support.

##### Job statements

Only one job is supported well enough to state.

- When a claim arrives without the photos needed to assess it, I want the missing items identified before an adjuster opens the file, so I can start assessment without a round of email requests. Signal: [19:05] call 1 and [01:45] call 2. Speaker roles: operations lead and adjuster.

The source does not show the outcome customers want, so no customer job statement is written.

##### Opportunity areas (proposed)

These are the team's inferences, not client requests.

1. **Require photos at web-form submission for claim types that need them.** Rests on pain point 1 and the [09:40] account of the form. Tomas was told the form is tied to the policy system, so feasibility is unconfirmed.
2. **Route email and phone claims into one intake queue.** Rests on pain point 3.
3. **Give customers and the main line a claim status view.** Rests on pain point 5. Priya was lukewarm at [38:20], so the case would need to connect to the phone volume her director watches.
4. **Work around the policy-system change queue.** Rests on pain point 2. Whether any of 1 to 3 can avoid that system is the first thing to establish.

##### Verbatims

Quotes are exact. Parenthetical notes in the source are labelled as notes.

- "Claims arrive by phone, the web form and email, and each one lands in a different queue. Somebody has to retype the email ones by hand." Priya Raman, [02:40] call 1.
- "We miss our own five-day first-contact target on about a third of claims. I'd have to pull the exact figure, but it's a third, give or take." Priya Raman, [06:15] call 1.
- "The policy system is the blocker. Anything that touches it needs a change request, and the queue for those is months long." Priya Raman, [11:50] call 1.
- "I don't need a fancy portal. I need the adjusters to stop chasing missing photos." Priya Raman, [19:05] call 1.
- "Half my morning is emailing people for photos they already sent to a different address." Tomas Okafor, [01:45] call 2.
- "The web form lets people submit with no photos at all. I raised it with IT last spring and was told it's tied to the policy system." Tomas Okafor, [09:40] call 2.
- "Customers ring me directly because the main line has no answers for them." Tomas Okafor, [21:30] call 2.

##### Speaker-attributed insights

**Priya Raman, Head of Claims Operations.** Her stated priority is less adjuster rework, and she downplays a portal ([19:05]). She is wary of the policy system as a constraint ([11:50]) and of the fraud team's reaction to auto-approval ([27:20]), which suggests she wants stakeholders involved before options are proposed. She names her director as the audience for phone volume ([38:20]), which signals who her measures of success answer to.

**Tomas Okafor, Senior Claims Adjuster.** He is concerned with daily rework and with customers calling him directly. He keeps his own status spreadsheet ([26:10]) and has already tried to get the form changed through IT. He is open to auto-approval of small claims ([14:00]) and speaks for adjusters only, not for fraud.

##### Where the speakers differ

Auto-approval of small claims is contested. Priya: "Our fraud team would hate anything that auto-approves small claims. I'd want them in the room before we talk about it." [27:20]. Tomas: "I'd actually be fine with auto-approving the small ones. Under five hundred, the fraud rate is tiny." [14:00]. Tomas's claim about the fraud rate is his view, and no fraud data was supplied. Priya's claim about the fraud team is her expectation, since the fraud team was not interviewed.

##### Open questions and next steps

| Question | Follow-up | Owner |
|---|---|---|
| What is the real first-contact miss rate? | Request the first-contact report Priya mentioned | Open |
| How often are photos re-requested, by claim type? | Request a sample of claim files or email logs to check the "seven in ten" estimate | Open |
| Can the web form change without a policy-system change? | Ask IT what ties the form to the policy system and what the current queue length is | Open |
| What does the fraud team think about small-claim auto-approval, and what is the fraud rate under 500? | Interview the fraud team before any option is presented | Open |
| What does Priya's director measure? | Ask Priya for the phone-volume figures and target | Priya Raman, if she agrees |

The source names no project owners, so ownership is left open.

##### Gaps and assumptions

- Both sources are excerpts. Anything not in the excerpts is unknown, including other speakers and what was said between timestamps.
- No customer, IT or fraud-team voices are included. Findings 2 and 5 rest on one or two internal speakers.
- Every figure is a spoken estimate: "about a third" and "seven in ten". None has a report behind it. Do not show them in the readout as measured.
- The meaning of "small claims" is Tomas's "under five hundred", with no currency given.
- Assumed: the readout audience is the project steering group, and plain headings are acceptable.
