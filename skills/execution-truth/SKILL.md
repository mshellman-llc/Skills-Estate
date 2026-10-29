---
name: execution-truth
description: Establish and verify the actual completion state of work that changes repositories, files, cloud documents, deployments, client data, publications, installations, or automations. Use before material implementation and at handoff. Do not use for ordinary questions, explanations, or read-only analysis with no produced artifact or state change.
---


# Execution truth

Prevent a local draft, commit, successful command, or API response from being
reported as a later state.

At the start, identify the requested outcome, authoritative source, finish line,
affected systems, and prohibited actions. Keep one independently reviewable
objective in scope. Record adjacent findings as follow-ups unless they block the
finish line.

Read only the adapter for the current work:

- Repository or code change: [`references/git.md`](references/git.md)
- Local artifact or filesystem change: [`references/local-files.md`](references/local-files.md)
- Google Drive or another cloud document: [`references/cloud-documents.md`](references/cloud-documents.md)
- Environment or application deployment: [`references/deployments.md`](references/deployments.md)
- Client records or migration: [`references/client-data.md`](references/client-data.md)
- Website, bundle, or marketplace publication: [`references/publishing.md`](references/publishing.md)
- Scheduled or recurring work: [`references/automations.md`](references/automations.md)

Use `scripts/work_truth.py` for a bounded Git, file, or generic receipt when the
runtime can execute it. A runtime without the script performs the adapter's
read-only checks and labels unavailable proof instead of assuming success.

Use these states precisely: `proposed`, `built-locally`, `committed-locally`,
`pr-open`, `merged`, `published`, `installed`, and `verified-live`. A task may
need a more specific adapter state, but it may never promote itself without
evidence from the destination system.

Finish with four facts: **changed now**, **verified**, **still unchanged**, and
the **exact next action**. Name any approval required for that next action.
