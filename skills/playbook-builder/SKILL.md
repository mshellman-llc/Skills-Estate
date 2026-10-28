---
name: playbook-builder
description: "Define, compare, or maintain productized offerings and service playbooks in a coherent catalog."
---

# Playbook builder

Read [shared workflow](references/estate/workflow.md). For rendered artifacts, read [brand policy](references/estate/brand.md).

Locate the authored catalog source, existing offerings, intended buyer, and commercial objective. If the catalog is generated, edit the authored source and regenerate its views.

Define who the offering serves and disqualifies, what it is, the client's desired outcome, the provider's objective and next step, included activities and deliverables, scope boundaries, and delivery mechanics. Make effort, staffing, duration, dependencies, and price sources explicit.

Before adding an offering, compare its buyer, problem, scope, and position in the catalog with existing entries. Merge or replace a duplicate only within the authorized change, preserving useful content and identifiers. Distinct adjacent offerings need a clear boundary and transition.

Create internal and external descriptions appropriate to their audiences. Keep internal economics out of client copy. Verify catalog links, numbering, dependencies, and consistent scope across changed views. An authored offering is not a sold or delivered service.

## Preserve untouched catalog entries

For a targeted catalog edit, preserve a before copy. Run `python3 scripts/verify_corpus.py --source BEFORE.md --edited AFTER.md --changed "01 Offering name"` using the full level-two heading text for each intended change. Include `preamble` only when intentionally changing the introduction. The checker rejects undeclared edits and duplicate headings and ignores only documented trailing separator/blank-line differences. Read its command help before using it with a different catalog shape. Run `python3 scripts/verify_corpus.py --selftest` after changing the checker.

This check protects unchanged offerings; it does not establish that an edited offering is commercially sound or approved. Review the declared changes against the request and source. Use descriptive offering names in the deliverable and retain machine traceability separately.
