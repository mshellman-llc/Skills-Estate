---
name: pm-spec-writing
description: "Write a feature spec, PRD, development brief, or testable acceptance criteria from supplied product context. Use for explicit specification and scoping requests; routine code edits and bug fixes do not require a separate spec."
license: MIT
metadata:
  upstream: "rampstackco/claude-skills"
  upstream-commit: "98d8cfe773f975a465f11c56d8fb2ae618307805"
  adapted: "2026-10-06"
---

# Product specifications

Write a spec that lets the next owner understand the requested behavior and verify it. Read the current brief, supplied sources, and existing decisions before drafting. Separate a confirmed requirement from a proposed choice or open decision.

Read [Spec decisions](references/spec-decisions.md) to choose the appropriate depth. A bounded change can use a compact development brief. A cross-system feature may need a fuller spec. A reproducible defect needs expected behavior and evidence of actual behavior, not a fabricated product strategy.

Use the audience's vocabulary. Describe the problem and intended outcome, the behavior in scope, and the constraints that affect implementation. Include exclusions only when they prevent a plausible misunderstanding. Give dependencies and unresolved decisions their actual owners when known.

Make acceptance criteria observable. Cover the main path and the edge cases that matter to this feature. Specify how to check the outcome at its real destination. Do not turn implementation preferences into product requirements without evidence.

Ask only for a missing decision that materially changes the spec or blocks useful work. Draft the supported portions while that decision is pending. Do not impose a fixed discovery questionnaire, require a universal “why now,” or invent a baseline, effort estimate, target, date, or owner to fill a template.

Use an existing work item when supplied. Preserve its ID and current state; drafting a spec does not close a Brain task or create a competing task system. Keep implementation and external release separate from specification unless the user requested those actions too.

Deliver the requested document at the depth its reader needs. Identify the decisions still needed to make its acceptance criteria executable. Existing source authority, claim checks, voice, brand, and completion rules govern the result.

Adapted from [RampStack's pm-spec-writing](https://github.com/rampstackco/claude-skills/tree/98d8cfe773f975a465f11c56d8fb2ae618307805/skills/pm-spec-writing). The original MIT notice is in [LICENSE](LICENSE).
