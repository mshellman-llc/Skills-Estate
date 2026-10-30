# CPQ migration scope boundaries

Resolve these dimensions from the confirmed engagement quote, architecture and contract. This reference supplies questions to ask, not exclusions or a standard tier policy. Do not copy a prior engagement's caps or commercial commitments.

| Dimension | Decision required from the current source |
| --- | --- |
| Integrations | Identify included endpoints and whether work covers mapping, remediation, replacement or a new integration. |
| Revenue capabilities | Confirm which quoting, pricing, contract, order, invoicing and revenue processes are included. |
| Asset lifecycle | Confirm co-term, ramp, consumption and amendment scenarios individually. |
| Custom code | Identify the Apex, quote-calculator and external logic to preserve, refactor or replace; verify target-platform support. |
| Data footprint | Name source systems, objects, history, quality responsibilities and reconciliation conditions. |
| Platform changes | Confirm org consolidation, licensing, provisioning and unrelated configuration boundaries. |
| Cutover | Confirm parallel running, rollback, legacy access and decommissioning responsibility. |
| Enablement and support | Confirm audiences, training format, support period and responsibilities. |
| External systems | State what the provider may change and what remains with another system owner. |
| Unverified features | Treat beta features and unresolved platform limits as decisions requiring current evidence. |

Render only the source-supported exclusions in `model.exclusions`. The generator appends the actual contract profile's catch-all clause. Missing scope authority remains an open item; this checklist creates no contractual exclusion, change-order right or follow-on service commitment.
