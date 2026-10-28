<!-- Maintenance note: no README generator exists in this repository. This file is maintained by hand and must be kept consistent with skill.yaml and SKILL.md when either changes. -->
# ROM

> Builds a sourced rough-order-of-magnitude effort or cost range and its basis of estimate from a supplied scope, comparables or quote, and gates quote-anchored figures when a quote exists.

**What it does.** Builds a sourced effort or cost range and the basis of estimate the client validates before deep scoping. A quote is not required; a missing rate leaves cost unresolved. When a quote is supplied, the figure gate checks its tie-out. Buyer-facing or deal-desk-facing.

**Use it when.** Asked for a ROM, rough order of magnitude, early pricing range, investment range, ballpark or basis of estimate, when a quote reference is paired with a range, sizing, or early-pricing request, or when a playbook tier needs its ROM artifact.

**Not for.** Do NOT use for scoping or quote creation (that is project-scoping), the SOW (sow), or the firm proposal (interactive-proposal).

**Related.** Optionally uses [`knowledge-hub`](../knowledge-hub/README.md) when an authorized project destination exists; Calls [`evidence-core`](../evidence-core/README.md), [`quality-gate`](../quality-gate/README.md).

**Full trigger logic and boundaries:** [SKILL.md](SKILL.md) · tier `core`
