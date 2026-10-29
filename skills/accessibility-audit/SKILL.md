---
name: accessibility-audit
description: "Audit a specified interface against WCAG or verify requested accessibility fixes. Use for explicit accessibility reviews and remediation checks; routine QA and copy edits do not require this audit. Default target is WCAG 2.2 AA."
license: MIT
metadata:
  upstream: "rampstackco/claude-skills"
  upstream-commit: "98d8cfe773f975a465f11c56d8fb2ae618307805"
  adapted: "2026-10-06"
---


# Accessibility audit

Assess the specified interface against the user's target. If none is supplied, use WCAG 2.2 AA. State the version and conformance level. Record the sampled pages or states and the environment, with the methods actually used. Read [Audit coverage](references/audit-coverage.md) before selecting checks.

Combine available automated checks with manual interaction. Inspect the rendered states needed for the user journey. Include errors and dynamic content. Choose tools already available in the session; do not claim a tool ran because its name appears in a plan.

Record each observed barrier with the affected page or component, reproduction steps, user impact, criterion, evidence, and proposed repair. Cite the relevant W3C criterion when the finding depends on its requirement or exceptions. Prioritize the effect on completing the task, rather than an automated score alone.

Distinguish observed failures from suspected issues and untested criteria. Static code or a screenshot may support a specific finding but cannot prove keyboard behavior, screen-reader output, or conformance of a complete process. If a required environment is unavailable, complete the supported checks and state the remaining coverage.

WCAG 2.2 AA includes applicable A and AA criteria. Include the six new A and AA criteria listed in the reference. Read the current criterion and exceptions before judging a failure. AAA criteria are outside the default target.

Do not declare legal compliance, certification, or full conformance from an automated scan or a bounded audit. Retesting a fix verifies only the behavior tested in the recorded environment. A conformance claim requires the scope and requirements in the standard to be met.

An audit request authorizes inspection and recommendations. Apply fixes when the user requested remediation too, using the existing implementation and verification workflow. Preserve the governing source, privacy, brand, and completion rules.

Adapted from [RampStack's accessibility-audit](https://github.com/rampstackco/claude-skills/tree/98d8cfe773f975a465f11c56d8fb2ae618307805/skills/accessibility-audit). The original MIT notice is in [LICENSE](LICENSE).
