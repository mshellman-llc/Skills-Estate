---
name: delivery-router
description: Route salesforce delivery engineering, deployment, team onboarding, backlog refinement, sprint planning, release review sites, and the delivery lifecycle from sales handoff through cutover closeout. Select the smallest appropriate skill without recreating its method.
---

# Delivery Router

1. Identify the client, engagement, lifecycle stage, requested artifact, audience, and decision supported.
2. Resolve and read the engagement AI Knowledge Hub when applicable.
3. Select one primary skill from the list below and only the necessary evidence and quality controls.
4. Explain ambiguous routing and request the missing distinction.
5. Do not reproduce the selected skill's methodology.
6. Confirm which Knowledge Hub files the workflow must read and update.

## Planning chain distinctions

Requirements and backlog requests follow the shared planning chain that each of these skills cites. Writing or changing a requirement is `requirements-capture`. Deciding whether existing requirements are ready for a sprint, estimating them or splitting them is `backlog-refinement`. Committing a sprint against capacity, or diagnosing a missed sprint, is `sprint-planning`. Writing RAID entries, decisions or a status report is `delivery-status`; the other skills propose RAID entries and `delivery-status` records them.

## Release review distinctions

Turning a new tracker export into canonical tickets and a delta is `tracker-intake`. Classifying release stories with MoSCoW, readiness and the critical path is `moscow-story-map`; INVEST grading for a sprint stays with `backlog-refinement`. Keeping refinement questions, owners and answers is `decision-register`; RAID decisions on a signed engagement stay with `delivery-status`. Building or refreshing the multi-page review site, publishing it and answering its comments is `review-site`, which calls the other three.

## Available skills

- `delivery-suite`
- `s2d-handoff`
- `delivery-kickoff`
- `delivery-status`
- `backlog-refinement`
- `sprint-planning`
- `uat-validation`
- `cutover-closeout`
- `team-onboarding`
- `sf-delivery-standards`
- `sf-deploy-engine`
- `sf-solo-devops`
- `tracker-intake`
- `moscow-story-map`
- `decision-register`
- `review-site`


## Required controls

Use `knowledge-hub` for configured durable records, `evidence-core` for source
and claim checks, and `quality-gate` for the requested artifact's completion
checks. Resolve them from the installed estate or this package's runtime
references. Installation must include the declared dependencies; do not assume
that an unrelated plugin installed them automatically.
