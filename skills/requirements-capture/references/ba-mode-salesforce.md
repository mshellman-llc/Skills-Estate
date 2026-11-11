# BA mode: Salesforce engagements

This mode applies when the source material is a Salesforce Statement of Work
or scope document, or when the backlog feeds a Salesforce build. Everything in
the main skill still holds: the hierarchy, the workbook, MoSCoW, Gherkin, and
the interactive phases. This file adds the Salesforce business-analysis
discipline on top of them.

## Start from the SOW

Do not begin analysis until the SOW or the scope source is in hand. Ask for it
first. Then read the whole document before proposing a hierarchy: goals,
deliverables, assumptions, exclusions, timelines, milestones, stakeholders.
Epics proposed from a skim get restructured later at the client's expense.

## The Salesforce sweep

While reading, inventory what the SOW commits to in each of these areas. An
area the SOW is silent on becomes a recorded gap, never a blank to fill.

- Clouds in scope: Sales, Service, Experience, Revenue, Field Service, Data,
  Marketing, Agentforce, custom platform work.
- Integrations and third-party systems, including middleware.
- Data model, data migration, and data ownership.
- Security: profiles, permission sets, sharing, roles, identity, SSO.
- Reporting and dashboards.
- Automation: Flows, approval processes, assignment rules.
- AI features, only where the SOW names them.
- Non-functional ground: compliance, performance, accessibility, training,
  deployment, support.

## Traceability is the contract

Every requirement in this mode carries a Source value naming the SOW section
it came from. The Source column, its three legitimate values, the gap list,
and the Jira field mapping live in `jira-export-and-traceability.md`. Read
that file whenever this mode is on.

Never invent integrations, APIs, custom objects, reports, automations,
approval processes, Experience Cloud sites, or user roles the SOW does not
name. When the SOW implies something without stating it, the row is
`inferred from` with the section named. When the build needs something the SOW
never settles, the row is `open:` with the question, and the gap list entry
records who can answer it. Honest wording for those rows: "The SOW does not
specify" and "clarification required before implementation".

## Mapping onto the house hierarchy

There is no Feature layer in the Aleysian matrix. What a BA tool would call a
Feature is either a Capability grouping or a cluster of requirements under one
Epic. Pick whichever reads true and do not add a fourth level.

Seed candidate Epics from the Salesforce functional areas the SOW commits to.
Common ones: Case Management, Opportunity Management, Lead Management, CPQ,
Field Service, Knowledge, Omni-Channel, Experience Cloud, Reporting, Security,
Integrations, Data Migration, Agentforce. Only propose an Epic the SOW
supports.

Record the Salesforce specifics of a requirement, meaning the cloud, the
objects touched, and the integrations involved, in its Assumptions & Notes
cell, so the workbook stays the single artifact.

## Standard before custom

Think like an architect who has to maintain the org afterward. Before a
requirement implies custom development, check whether standard platform
capability covers it: standard objects, Flows, Dynamic Forms, approval
processes, Omni-Channel, assignment rules, record types, Lightning pages,
permission sets, validation rules, duplicate rules. Recommend Apex or LWC only
when standard capability falls short or the SOW requires it, and label that
recommendation as advice rather than SOW scope.

## Acceptance criteria coverage

Gherkin, as always. In this mode also cover the scenarios Salesforce builds
fail on in UAT: permission scenarios showing who cannot see or do the thing,
negative paths, error handling, validation rules, and boundary conditions
where a limit exists. A story with only the happy path is not testable in any
org that has a sharing model.

Keep stories INVEST and sprint-sized. Split a requirement that is too large,
and both halves inherit its source.

## Assumptions and risks

An assumption stays labelled an assumption in Assumptions & Notes. It never
quietly becomes a requirement. When an assumption is load-bearing, raise it as
a clarifying question instead.

Deliver a short risk list alongside the gap list: the risk, its probability,
its impact, a mitigation, and the owner to assign. Technical, data,
integration, timeline, and licensing risks are the ones a Salesforce SOW most
often hides.

## What this mode does not produce

No executive summary, no BRD narrative, no personas document, no process-flow
pack. The deliverable stays the workbook plus the gap and risk lists, with the
Jira export added when the backlog is the destination.
