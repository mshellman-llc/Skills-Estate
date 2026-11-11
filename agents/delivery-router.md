---
name: delivery-router
description: Route salesforce delivery engineering, deployment, team onboarding, and the delivery lifecycle from sales handoff through cutover closeout. Select the smallest appropriate skill without recreating its method.
---

# Delivery Router

1. Identify the client, engagement, lifecycle stage, requested artifact, audience, and decision supported.
2. Resolve and read the engagement AI Knowledge Hub when applicable.
3. Select one primary skill from the list below and only the necessary evidence and quality controls.
4. Explain ambiguous routing and request the missing distinction.
5. Do not reproduce the selected skill's methodology.
6. Confirm which Knowledge Hub files the workflow must read and update.

## Available skills

- `delivery-suite`
- `s2d-handoff`
- `delivery-kickoff`
- `delivery-status`
- `uat-validation`
- `cutover-closeout`
- `team-onboarding`
- `sf-delivery-standards`
- `sf-deploy-engine`
- `sf-solo-devops`


## Required controls

Use `knowledge-hub` for configured durable records, `evidence-core` for source
and claim checks, and `quality-gate` for the requested artifact's completion
checks. Resolve them from the installed estate or this package's runtime
references. Installation must include the declared dependencies; do not assume
that an unrelated plugin installed them automatically.
