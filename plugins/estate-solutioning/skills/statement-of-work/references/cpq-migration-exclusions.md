# CPQ → RCA Migration, Section 2.3 exclusion examples (per tier)

Detailed reference examples for CPQ-to-RCA migration scopes. The confirmed engagement quote owns its actual exclusions; these examples do not establish current platform capabilities or a signed commitment.

**How this is used.** The `sow` generator renders `model.exclusions` (an array of strings) into Section 2.3, then appends the selected catch-all clause. It does **not** hardcode exclusions, these are playbook content. When building the model for a CPQ-migration tier, copy that tier's list below into `model.exclusions`. Leave the catch-all to the generator (it always appends `CATCH_ALL_EXCLUSION`).

Do not paste the catch-all sentence ("Any services not explicitly set forth…") into this list; the generator owns it.

---

## Tier 1, Lift & Shift

- A second integration, a net-new integration build, an undocumented integration, a move to new middleware, or a tax-engine or payment integration.
- Contract Lifecycle Management (CLM), Dynamic Revenue Orchestrator (DRO), and Invoice Management (billing).
- Co-term, ramp, and consumption-based asset lifecycle logic.
- Pricing logic redesign or optimization beyond the 1:1 migration.
- Apex remediation or refactoring of source CPQ classes; custom Apex beyond ETL scripts, CML constraint rules, and quote template rendering.
- Modifications to non-CPQ Salesforce configuration.
- Multi-org consolidation or active platform migrations in flight.
- A parallel-run period beyond the cutover.
- Legacy CPQ decommissioning beyond cutover-runbook documentation. The legacy CPQ org remains client-owned and read-only after cutover; decommissioning is the Client's responsibility.
- Salesforce platform license procurement, upgrades, or org provisioning.
- Refactoring an existing Quote Calculator Plugin (QCP) into the RCA pricing procedure. QCP logic that requires re-architecture is out of scope for a functional-parity migration.
- Integration covers field mapping and endpoint re-routing only: the delivery team makes no logic changes within the integration and does not configure, customize, or advise on the external system itself.

## Tier 2, Remediate & Migrate

- Dynamic Revenue Orchestration.
- CLM redlining or advanced contract negotiation workflows.
- Revenue Cloud Billing and Invoice Management.
- Net-new platform engineering for a changed revenue model.
- Payment gateway or payment processing.
- Change management programs or training delivery beyond the agreed train-the-trainer sessions.
- Additional integrations beyond those identified herein.
- Managed services or ongoing support after the Support window.
- Refactoring of pre-existing Client Apex to reach Salesforce deployment coverage requirements; the Client's existing code must compile and meet coverage in the source org.
- Salesforce platform license procurement, upgrades, or org provisioning.

## Tier 3, Re-Architect & Migrate

- Revenue Cloud Billing, including invoicing and revenue recognition. Available under a separate engagement.
- A fourth integration or beyond. This engagement covers up to three rebuilt connectors.
- Data migration beyond the two-source-system footprint in Exhibit A.
- Payment gateway or payment processing.
- A full organizational change management program. Role-based train-the-trainer enablement is included.
- Net-new business capability not present in the current revenue process and not named in Section 2.2.
- Modifications to non-CPQ Salesforce configuration outside the defined revenue scope.
- Revenue Cloud features in beta or behind a feature flag at engagement start, unless documented in an addendum.
- Managed services or ongoing support after the Support window. Available under a separate managed services engagement.
- Reverse-engineering of an undocumented pricing engine, which is addressed through Change Control if encountered.
