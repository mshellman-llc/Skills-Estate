---
name: org-preflight
description: "Verify the Salesforce organization and environment before a write, DML operation, deployment, or metadata change."
---

# Org preflight

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Resolve the intended organization from the user's request and current project configuration. Read the connected session or CLI identity using available read-only commands. Compare organization ID, instance, username or principal, and sandbox/production status with the intended target.

A tool label, alias, browser title, or previously used login does not establish the target. If the IDs disagree or the environment cannot be verified, stop the write and state the mismatch. Do not switch credentials or environments silently.

Check that the requested operation and its scope are authorized. Reuse existing authorization for that operation; ask only when the proposed write changes the agreed target or impact. Confirm the relevant records or metadata and the recovery path before executing.

Return the verified target identity and operation scope without credentials or tokens. After the write, verify the result in that same organization. A sandbox success does not prove production deployment.
