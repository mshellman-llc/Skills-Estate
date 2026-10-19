---
name: spec-writer
description: "Write an implementation-ready feature specification with user flows, UI states, affected files, data changes, and testable acceptance criteria. Use for explicit feature specification work."
---

# Spec writer

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Read the existing product, relevant code, design decisions, and requested change. Identify the audience, problem, expected behavior, scope boundaries, and constraints. Preserve existing behavior outside the change.

Describe the main flow and relevant empty, loading, error, permission, validation, success, cancellation, and recovery states. Specify data contracts, state transitions, accessibility behavior, and migration needs. Use rendered mockups when they resolve an actual interface decision.

List affected files or components with create, update, delete, read, or migration intent. Verify paths before presenting them as existing. For each acceptance criterion, define an observable result and the conditions under which it applies. Separate proposed design from current implementation.

Resolve material product choices with the user; make reversible implementation assumptions explicit. Deliver the requested editable spec and any mockups. A saved spec does not authorize implementation, destructive migrations, publication, or production deployment beyond the user's request.
