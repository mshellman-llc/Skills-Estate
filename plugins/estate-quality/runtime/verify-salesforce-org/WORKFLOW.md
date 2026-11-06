---
name: verify-salesforce-org
description: Check the exact intended Salesforce organization before a record write, file upload, or deployment. Use a fresh CLI or connector identity, compare its org ID and sandbox status, and refuse missing or mismatched targets.
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.



# Verify salesforce org

Use this gate before a Salesforce record mutation, file upload, metadata deployment, or scoping-app write. It compares the actual Organization ID with the intended target. An alias or the word “sandbox” alone cannot establish which organization receives a write.

## Choose the connection

Read the project's intended org ID and connection from its current configuration. If the user has not identified a target, continue local preparation and leave the write pending. Do not pick an authenticated alias merely because it exists. Read-only work and offline package preparation do not require an org.

The script supports Salesforce CLI and connector responses. Use the same connection for the identity check and subsequent authorized action. A check on one CLI alias does not establish the identity of a separate MCP connector or browser session.

## Run the check

With Salesforce CLI, query the named connection directly:

```bash
python3 scripts/preflight.py --target-org YOUR_CONFIRMED_ALIAS \
  --expect YOUR_CONFIRMED_ORG_ID --receipt attempts/preflight-001.json
```

This runs only the following read-only query through `sf data query --target-org`:

```sql
SELECT Id, Name, IsSandbox, InstanceName FROM Organization
```

With a connector, run that query through its available query tool immediately before the write. Save the complete response containing one `records` entry, then check it:

```bash
python3 scripts/preflight.py --identity-json organization-response.json \
  --expect YOUR_CONFIRMED_ORG_ID --receipt attempts/preflight-002.json
```

The JSON can be a direct query result with `records` or the CLI envelope with `status: 0` and `result.records`. The checker requires one Organization record and a boolean `IsSandbox`. Caller-supplied data is recorded as supplied evidence; the script cannot prove when a connector fetched it. If the connector uses another envelope, preserve the raw response and extract the Organization record without changing its values.

The compatibility arguments `--live-id`, `--is-sandbox true|false`, and optional `--live-name` remain available. Prefer the complete query response because it preserves more evidence. Never invent these values to obtain a pass.

## Decide whether the action can proceed

Exit 0 and `PREFLIGHT PASS` mean the supplied or freshly queried identity matches the exact intended org. Exit 2 means refusal. Refuse incomplete identity, unknown aliases, malformed responses, failed connections, ambiguous registry entries, mismatched org IDs, and registry sandbox status that disagrees with the org.

Production also requires `--allow-production`. Supply it only when the user's existing authorization covers that production action. The flag acknowledges production; it does not grant permission. A successful identity check does not authorize a deployment, prove its tests passed, or prove its result.

Keep the same connection for the write and retain its result separately. Repeat the preflight if the connection or target changes. Never reuse a receipt from a prior session as a live check.

## Configure an org registry

`scripts/orgs.json` ships with an empty `orgs` object. Keep private org IDs and aliases in a project-local registry and pass `--registry path/to/orgs.json`. Each entry is keyed by an exact 15- or 18-character Organization ID and has a unique `alias` plus `kind: sandbox|production`.

An exact ID works without a populated registry. An alias must resolve to one ID. The words `sandbox`, `production`, `sbx`, and `prod` only work if explicitly registered as aliases for one ID. Conflicting 15- and 18-character entries are rejected.

## Verify without an org

Run `python3 scripts/preflight_selftest.py` for deterministic identity decisions. Estate behavioral tests also drive a simulated CLI to exercise query arguments, failures, malformed responses, and receipts. Those tests make no Salesforce connection. Live deployment verification remains a separate step once a target is available.

Every `--receipt` path must be new. Keep failed checks as well as successful checks. Receipts contain org identity, so store them with the private project rather than in a reusable public skill package.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
