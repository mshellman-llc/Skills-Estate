# Planning chain

Product and delivery planning skills pass work to each other through shared IDs and files. This contract names who owns each artifact and field so a later skill reads an earlier one instead of rebuilding it. When a skill's own instructions are more specific, follow them; when two skills disagree about an ID or a field owner, this file decides.

## Order of work

| Step | Skill | Produces | Next skill reads |
|---|---|---|---|
| Jobs and opportunities | `frame-jobs-to-be-done` (workshop mode when a team runs a JTBD session) | Job statements, struggling moments, hire and fire criteria, opportunity statements with evidence numbers | Problem and job names for prioritization; outcomes for roadmap cards |
| Ranking | `prioritize-work` | A ranked proposal with formulas and evidence flags | The decision owner's order; roadmap horizon placement |
| Roadmap | `build-roadmap` (outcome mode for outcome roadmaps) | `plan.json` and the rendered roadmap | Now items become epics and requirements |
| Requirements | `capture-requirements` | Epics and the Requirements tab: Requirement Number, user story, Gherkin acceptance criteria, MoSCoW priority, status | Rows for refinement |
| Refinement | `refine-backlog` | `readiness.json` and a readiness report per Requirement Number | Sprint planning reads only READY items |
| Sprint | `plan-sprint` | `sprint-NN-plan.md` and its gate report | Status reporting and the next sprint |
| Status and logs | `track-delivery` | Weekly status, RAID log, decision log, scope-drift candidates | Every other step reads the logs |

On a client engagement, `delivery-orchestrator` decides which stage the work belongs to and `start-delivery` seeds the logs and the first backlog. A product team without an engagement record can enter the chain at any step; the skill names what it expected to receive and what it used instead.

## Shared IDs

| ID | Format | Created by | Rule |
|---|---|---|---|
| Requirement Number | `PREFIX-###`, such as `CPE-004` | capture-requirements | Permanent. Refinement, sprint plans and roadmap citations use it unchanged. A split creates new numbers and records the parent in Assumptions & Notes. |
| Kickoff epic | `E-###` | start-delivery | Maps to a capture-requirements epic prefix in the epic's notes. |
| RAID entries | `R-###`, `A-###`, `I-###`, `D-###` (D is a dependency) | start-delivery seeds, track-delivery appends | Append-only. Other skills cite them and propose new entries; only track-delivery writes the log. |
| Decision | `DEC-###` | track-delivery | Records a decision a named person made. A ranking or a gate result is not a decision. |
| Roadmap item | the card `id` in `plan.json` | build-roadmap | Cards cite the Requirement Numbers or epic prefixes they deliver. |

## Field ownership

| Field | Owner | Other skills |
|---|---|---|
| MoSCoW priority | capture-requirements, confirmed by the client or Product Owner | prioritization proposes an order; it never rewrites the MoSCoW value |
| Estimate | the delivery team, recorded during refine-backlog | capture-requirements leaves it empty; plan-sprint reads it |
| Readiness verdict | refine-backlog | plan-sprint commits only READY items |
| Commit or stretch | the team, recorded in the sprint plan | status reports it; nobody else changes it |
| Dependency owner and date | the RAID log | refinement and sprint plans cite D-### IDs |
| Confidence and effort in a score | the named source in the candidate file | an unsourced confidence above 50% is capped; unsourced effort is flagged |

## Evidence

Every skill in the chain follows `evidence-core`: a job, a score input, an estimate, a dependency date or a status line names its source or is labelled a hypothesis. A tool's verdict reports what the tool checked. A READY verdict means the row passed the readiness checks; it does not mean the requirement is correct or approved.

## Files on disk

Keep chain artifacts together in the engagement or team folder so the next skill can find them by name:

```
requirements/requirements_vN.xlsx      capture-requirements
requirements/requirements_vN.csv       Requirements tab export for refinement
refinement/readiness-YYYY-MM-DD.json   refine-backlog
sprints/sprint-NN-plan.json            plan-sprint input
sprints/sprint-NN-plan.md              plan-sprint output
roadmap/plan.json                      build-roadmap
RAID.md, DECISIONS.md, status-*.md     start-delivery and track-delivery
```

A project can use other paths; record them in the engagement's DELIVERY-STATE.md or the team's README so every skill reads the same files.
