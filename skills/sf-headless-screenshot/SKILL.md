---
name: sf-headless-screenshot
description: "Capture Salesforce UI evidence and run authorized clickpath checks with an available authenticated browser or screenshot tool."
---

# Sf headless screenshot

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Resolve the intended organization, record/page, scenario, and expected result. Verify identity with org-preflight. Inspect the available screenshot or browser tool and its current documented interface; do not assume a private CLI is installed.

Use the user's existing supported authentication. Never print session URLs, tokens, cookies, or credentials into artifacts or command output. Keep captures scoped to the requested page and avoid unrelated personal or customer data.

For a clickpath, specify starting state, actions, expected visible results, and failure evidence. Use stable selectors grounded in the actual page. Wait for meaningful readiness rather than treating a blank frame or loading skeleton as success.

Inspect the captured image as well as assertion results. Record viewport, scenario, timestamp, target environment, and any visible error or timing problem. Distinguish automated assertions from visual judgment. A screenshot proves the captured state, not every user role or environment.
