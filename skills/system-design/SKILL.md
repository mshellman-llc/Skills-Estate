---
name: system-design
description: "Explore a working design for a service, API, data platform, or product, including requirements, components, capacity, reliability, and trade-offs."
---

# System design

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Clarify the problem, users, constraints, and required outcomes. Use supplied scale and reliability targets; label estimates and avoid invented precision. Inspect the existing system when the design extends one.

Sketch components and flows, then examine the load-bearing boundaries: data ownership, API contracts, identity, authorization, state changes, storage, caching, queues, and consistency. Describe errors, timeouts, retries, idempotency, and recovery where they matter.

Estimate capacity from explicit inputs and show the calculation. Separate launch needs from hypothetical future scale. Explain the main alternative and why the recommended design fits the constraints, including its cost and operational burden.

Return a readable working design with diagrams when useful, unresolved decisions, and testable next steps. Formal source-controlled architecture belongs in architecture-doc. Design approval is not implementation, and a design example does not establish production performance.
