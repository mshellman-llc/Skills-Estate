---
name: sf-delivery-standards
description: "Set up, audit, or repair a Salesforce project's delivery checks and operating instructions. Use for delivery tooling setup and hook troubleshooting rather than an ordinary deployment."
---

# Sf delivery standards

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Inspect the repository's current branch, dirty files, tracker, environment model, Git hooks path, lifecycle hooks, CI, and project instructions. Read actual installed tool versions and available commands. Do not copy an employer-specific enforcement stack into a new project.

Choose the project's supported path: direct sandbox development, an existing deployment engine, or DevOps Center. Define ticket linkage, isolation, review, validation, test scope, and production authorization in the project contract. Preserve current rules unless the requested repair changes them.

For hooks, record what exists, show the intended change, preserve backups, and avoid replacing unrelated hooks. A hook must call a tool that exists and fail with a useful explanation. Do not disable a failing control to make delivery appear successful.

Test a meaningful pass and failure case in an isolated fixture before installing. Verify the actual configured hook path and CI behavior afterward. Report local enforcement separately from hosted CI and org behavior. Credentials remain in the user's supported authentication store.

## Working contracts and validation

Read [restored workflow and checks](references/restored-workflow.md) when preparing this artifact or running its deterministic checks. Preserve the current instructions above; the adapter contract states its supported format and limits.
