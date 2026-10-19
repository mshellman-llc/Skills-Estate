---
name: skill-creation-walkthrough
description: "Create or improve a focused cross-platform skill with clear triggers, progressive references, useful resources, and observable validation."
---

# Skill creation walkthrough

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Define the repeated user task, likely inputs, expected result, and boundaries with neighboring skills. Inspect the current estate before adding a duplicate capability. Keep the description concise enough to support correct selection.

Author the skill in this repository's skills directory with YAML name and description. Include only guidance that changes the agent's decisions. Put lengthy procedures and schemas in referenced files. Add scripts when deterministic work would otherwise be repeatedly rewritten, and document actual dependencies.

Use the shared brand and workflow policies through the estate build; do not copy brand values into the skill. Preserve the user's scope and existing authorization. Do not add mandatory interviews, universal approval steps, or broad triggers unrelated to the task.

Run structural validation and realistic positive and negative scenarios. Verify reference resolution in the standalone bundle and local install. A parser check does not prove behavioral quality. Build, install, and check status through skill-estate-sync, then record the actual destinations reached.
