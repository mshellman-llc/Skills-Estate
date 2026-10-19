---
name: sf-enterprise-patterns
description: "Apply a project's Salesforce service, selector, unit-of-work, and controller conventions when designing or reviewing Apex and LWC code."
---

# Sf enterprise patterns

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Read the repository's architecture and supported libraries before changing code. Use these patterns where they fit the established project; do not impose an unrelated framework or rewrite a working architecture as a side effect.

Keep trigger, UI, and API entry points thin. Put shared business behavior in services, query behavior in selectors where the project uses them, and DML coordination in its unit-of-work mechanism. Make sharing, CRUD, field-level access, and execution mode explicit. Return deliberate DTO shapes across controller boundaries.

Review bulk behavior, governor limits, transaction boundaries, recursion, failure handling, and data access. For LWC, choose imperative or reactive data access according to the use case and project convention. Do not make one access style a universal requirement.

Run the repository's actual static checks and meaningful Apex/LWC tests. When adding enforcement, preserve existing hooks and test both accepted and rejected fixtures. Report any exception with its reason and scope. Static conformance does not prove organization deployment or runtime behavior.
