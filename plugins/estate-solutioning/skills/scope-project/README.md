<!-- Maintenance note: no README generator exists in this repository. This file is maintained by hand and must be kept consistent with skill.yaml and SKILL.md when either changes. -->
# Scoping Agent

> Develop project scope and effort estimates from the user's brief, supplied models or a configured pricing system, with or without a CRM.

**What it does.** Develops scope and sourced effort estimates from the brief, a supplied export or the local calculator. A rough estimate does not require an existing quote or a CRM connection. Use to scope, size, estimate, or price work for a client or prospect, from scratch or by refining draft scope, reviewing transcripts, or revising existing scope. A project pricing adapter is used only when the project supplies and authorizes one.

**Not for.** Do NOT use for the SOW (sow), a static scope reference or option comparison (compare-scope-options), or project delivery. A rough order of magnitude range and its basis use the rom mode.

**Related.** Optionally uses [`manage-consulting-knowledge`](_runtime/manage-consulting-knowledge/README.md) when an authorized project destination exists; Calls [`evidence-core`](_runtime/evidence-core/README.md), [`review-deliverable`](_runtime/review-deliverable/README.md).

**Full trigger logic and boundaries:** [SKILL.md](SKILL.md) · tier `core`
