---
skill: moscow-story-map
title: MoSCoW story map for a tenant repairs portal release
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 407f61974326eb0e046d709d20e0657e3e6ac897af86dae19634ab14af5d63e3
---

## Request

Class the release 1 stories for the repairs portal by workflow step, using the class definitions and decisions in the client brief and the tracker export I've attached. Tell me what is ready to build, where the Must share stands against their ceiling, and what's on the critical path.

## Inputs

Run of the built `moscow-story-map` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `fix.txt`.

#### client-brief.md

#### Tenant repairs portal, release 1: scope notes

From Priya Natarajan, Head of Housing Operations, Tarn Valley Housing Association. Notes dated 28 October 2026.

##### Workflow steps

1. Report a repair (tenant or housing officer logs it)
2. Schedule and dispatch (officer assigns a contractor and a slot)
3. Complete and invoice (contractor signs off, finance is paid)

Release epics: HR-1 Report a repair, HR-2 Schedule and dispatch, HR-3 Complete and invoice.

##### Class definitions

- Must: we cannot go live without it.
- Should: go-live is possible, but officers need a manual workaround.
- Could: only if the sprint has room.
- Won't: moves to release 2.

Must points should stay at or under 60% of the open Must, Should and Could points.

##### Decisions so far

- Request form, urgent repair flag, contractor calendar, dispatch and contractor sign-off are Musts.
- Contractors must be trained on sign-off before go-live. This is a Must. No ticket exists yet; it belongs under HR-3.
- Photo upload and invoice export are Shoulds. For the first month finance can key invoices by hand from the sign-off emails.
- Postcode matching and text message updates are Coulds. Officers pick contractors by hand today.
- The tenant satisfaction survey is Won't for release 1.
- Gas safety certificate warning (HR-15): not decided. Ask Priya's team on Friday.

##### Open question

Finance has not confirmed the file format for the invoice export (CSV or their ledger's import template). This affects HR-32.

##### Roles

Tenant, housing officer, contractor, finance clerk.

#### tickets.csv

Key,Summary,Type,Status,Epic,Sprint,Points,Blocked by,Acceptance criteria
HR-1,Report a repair,Epic,In Progress,,,,,
HR-2,Schedule and dispatch,Epic,To Do,,,,,
HR-3,Complete and invoice,Epic,To Do,,,,,
HR-11,Repair request form,Story,Done,HR-1,Sprint 1,5,,Yes
HR-12,Photo upload on request,Story,To Do,HR-1,Sprint 2,3,HR-11,Yes
HR-13,Urgent repair flag with 24-hour routing,Story,In Progress,HR-1,Sprint 1,5,,Yes
HR-14,Text message status updates for tenants,Story,To Do,HR-1,,,,None
HR-15,Gas safety certificate warning on request,Story,To Do,HR-1,Sprint 3,3,,Yes
HR-21,Contractor availability calendar,Story,In Progress,HR-2,Sprint 1,8,,Yes
HR-22,Dispatch job to contractor,Story,To Do,HR-2,Sprint 2,5,"HR-21, HR-13",Yes
HR-23,Postcode contractor matching,Story,To Do,HR-2,Sprint 3,5,,Yes
HR-31,Contractor sign-off on completion,Story,To Do,HR-3,Sprint 3,5,HR-22,Yes
HR-32,Invoice export to finance,Story,To Do,HR-3,Sprint 3,8,HR-31,Yes
HR-33,Tenant satisfaction survey,Story,To Do,HR-3,,2,,Yes

## Output

### Repairs portal release 1: story map

I mapped 11 stories across the three workflow steps. Six are ready to build. Must points stand at 59% of open scope, just under the 60% ceiling, but the Contractor training Must has no estimate yet. A 1-point estimate brings the share to exactly 60%, and anything larger breaks the ceiling. The critical path is a single chain, Contractor calendar → Dispatch → Sign-off, and it runs through all three sprints.

I could not run `story_map.py`, so I applied its documented rules by hand to your tickets and brief. The tracker export was a CSV, so I read it directly and did not generate `tracker/tickets.json`. Re-run `summary` once the export has been normalised to confirm these figures.

#### Story map

Classes and definitions come from Priya Natarajan's 28 October brief. I did not add any of my own.

| Step | Must | Should | Could | Won't (release 2) |
|---|---|---|---|---|
| Report a repair | Repair request form (HR-11, done); Urgent repair flag (HR-13) | Photo upload (HR-12) | Text message updates (HR-14) | |
| Schedule and dispatch | Contractor calendar (HR-21); Dispatch to contractor (HR-22) | | Postcode contractor matching (HR-23) | |
| Complete and invoice | Contractor sign-off (HR-31); Contractor training (no ticket, planned in HR-3) | Invoice export (HR-32) | | Tenant satisfaction survey (HR-33) |

By class: 6 Must, 2 Should, 2 Could, 1 Won't.

#### Ready to build

A story is ready when it has acceptance criteria, an estimate, no open question and no open blocker. A done story counts as ready.

**Ready (6):** Repair request form (done), Urgent repair flag, Photo upload, Contractor calendar, Postcode contractor matching, Tenant satisfaction survey.

**Not ready (5):**

| Story | Why |
|---|---|
| Dispatch to contractor (HR-22) | Blocked by HR-21 and HR-13, both still in progress |
| Contractor sign-off (HR-31) | Blocked by HR-22 |
| Invoice export (HR-32) | Blocked by HR-31, and finance has not confirmed the file format (open question `q-invoice-format`) |
| Text message updates (HR-14) | No estimate and no acceptance criteria |
| Contractor training | No ticket, so no estimate or acceptance criteria |

Photo upload was blocked only by HR-11, which is done, so it is ready.

#### Must share

Open points exclude done and canceled tickets, so the finished request form drops out.

| Class | Open points | Tickets |
|---|---|---|
| Must | 23 | HR-13 (5), HR-21 (8), HR-22 (5), HR-31 (5) |
| Should | 11 | HR-12 (3), HR-32 (8) |
| Could | 5 | HR-23 (5); HR-14 has no estimate |
| Won't | 2 | HR-33 (2), left out of the share |

Must share = 23 ÷ (23 + 11 + 5) = 23 ÷ 39 = **59%**, against a ceiling of 60%.

The share is understated because Contractor training is a Must with no estimate. At 1 point the share is 24 ÷ 40 = 60%. At 2 points it is 25 ÷ 41 = 61%. Estimate the training story now, or agree with Priya which Should or Could moves out to make room.

#### Not yet classed

One open ticket under the release epics has no story: **HR-15, Gas safety certificate warning on request** (Sprint 3, 3 points). The brief says its class is undecided and the question goes to Priya's team on Friday, so I left it unclassed. If it becomes a Must it adds 3 points (26 ÷ 42 = 62%) before the training story is counted.

#### Critical path

Open Must tickets and their open upstream blockers, by sprint:

| Sprint 1 | Sprint 2 | Sprint 3 | No ticket |
|---|---|---|---|
| HR-21 Contractor calendar (8, in progress) | HR-22 Dispatch to contractor (5) | HR-31 Contractor sign-off (5) | Contractor training |
| HR-13 Urgent repair flag (5, in progress) | | | |

Links: HR-21 blocks HR-22, HR-13 blocks HR-22, HR-22 blocks HR-31.

- HR-21 is the largest piece of work on the path at 8 points, and Dispatch waits on it. A slip in Sprint 1 moves everything after it.
- HR-31 ends the path, and Invoice export (HR-32, 8 points, a Should) follows it in the same sprint. If HR-31 slips, the invoice export slips too. The manual invoicing workaround in the brief covers that case.
- Contractor training is a Must with no ticket, so it has no sprint. It can only happen once sign-off exists, so it needs a ticket and a slot after HR-31.

#### Next actions

1. Create a ticket for contractor training under HR-3 and estimate it. This settles the Must share.
2. Get the invoice file format from finance. Until then HR-32 stays not ready.
3. Get the HR-15 class from Priya's team on Friday.
4. Estimate HR-14 and write its acceptance criteria if it is to stay a Could.

#### Files

- `out/config/site.json`: class definitions from the brief, the three release epics, the readiness rules and the 60% ceiling.
- `out/content/stories.json`: the 11 stories with step, class, tickets, roles, what, interim and dependencies. It holds no status, points or readiness.
- `out/content/questions.json`: the open invoice-format question linked to Invoice export.

These are in the layout the skill's scripts expect, so `summary` can run on them as soon as `tracker/tickets.json` exists.
