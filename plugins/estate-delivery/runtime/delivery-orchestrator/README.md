# Delivery Suite

> Orchestrates the delivery half of the Estate sell-to-deliver lifecycle, from signed SOW through hypercare closeout: the stage map (Handoff, 01 Mobilize, 02 Analyze, 03 Design, 04 Build, 05 Validate, 06 Deploy and closeout), the named human gates, which skill owns each stage's artifacts, and the per-engagement DELIVERY-STATE.md convention.

**What it does.** Orchestrates the delivery half of the Estate sell-to-deliver lifecycle from signed SOW through hypercare closeout. It owns the Handoff-through-closeout stage map and its human gates.

**Use it when.** A request concerns a live delivery engagement and the owning skill is not obvious.

**Not for.** Do not use for pre-signature work; route directly to the named sales artifact owner.

**Related.** Depends on [`manage-consulting-knowledge`](_runtime/manage-consulting-knowledge/README.md); Calls `manage-cutover-closeout`, `track-delivery`, [`evidence-core`](_runtime/evidence-core/README.md), [`review-deliverable`](_runtime/review-deliverable/README.md), `prepare-delivery-handoff`.

**Full trigger logic and boundaries:** [SKILL.md](WORKFLOW.md) · tier `situational`
