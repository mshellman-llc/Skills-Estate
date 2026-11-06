---
skill: manage-linked-task
title: Start a ready task and create its linked working chat
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: d2aa7234b3610505200c90188ad9c60811d6eb3e8288d22b33d15856c0662193
---

## Request

Start task T-0142 from today's ready list and set up its working chat, I'm authorizing the chat creation. Config and the current bridge output are in the inputs folder.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the `manage-linked-task` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### bridge_pending.json

$ python3 "$TASK_BRIDGE" --pending
[
  {
    "task_id": "T-0142",
    "title": "Add arrears-reminder opt-out to settings page",
    "prompt": "Add a checkbox to the tenant settings page that stops arrears-reminder emails. Store the choice on the tenant profile and respect it in the reminder job. Acceptance: unit tests for the job skip logic; settings page test passes.",
    "desktop_project_id": "proj-4471",
    "note_hash": "a91f03c7",
    "existing_thread_id": null,
    "status": "ready"
  },
  {
    "task_id": "T-0150",
    "title": "Draft contractor onboarding checklist",
    "prompt": "Draft a one-page onboarding checklist for new maintenance contractors.",
    "desktop_project_id": "proj-5120",
    "note_hash": "5be2d814",
    "existing_thread_id": null,
    "status": "ready"
  }
]

#### config.md

#### Task adapter configuration (project: Tenant Portal)

- Task vault root: /Users/sam/Vaults/Tenancy
- TASK_HELPER: /Users/sam/Vaults/Tenancy/System/Tools/task_helper.py
- TASK_BRIDGE: /Users/sam/Vaults/Tenancy/System/Tools/task_bridge.py
- Notes: Today/Tasks/  Project briefs: System/Projects/
- Updater: none configured; no execution receipts exist for a scheduled run.

##### Ready Work.md (excerpt, 2026-11-04)

###### Tenant Portal
- T-0139 Fix rent-statement PDF footer — ready — chat: thread-8c21
- T-0142 Add arrears-reminder opt-out to settings page — ready — chat: none

###### Maintenance Desk
- T-0150 Draft contractor onboarding checklist — ready — chat: none

##### list_projects result (desktop)

- proj-4471  Tenant Portal   /Users/sam/Code/tenant-portal
- proj-5120  Maintenance Desk  /Users/sam/Code/maintenance-desk

## Output

T-0142 is ready to start, and nothing blocks creating its chat. I have not run anything. There is no helper, bridge or Codex app connection in this session, so below are the checks I made against your inputs and the exact steps to run, in order.

#### What I checked

| Check | Result |
|---|---|
| Script paths | Taken from your config, not inferred: `TASK_HELPER=/Users/sam/Vaults/Tenancy/System/Tools/task_helper.py`, `TASK_BRIDGE=/Users/sam/Vaults/Tenancy/System/Tools/task_bridge.py`. I could not inspect the scripts themselves, so confirm both exist at those paths before running anything. |
| Ready Work.md | T-0142 is ready under Tenant Portal and has no linked chat. |
| Bridge `--pending` output | T-0142 is listed with project `proj-4471` and note hash `a91f03c7`. `existing_thread_id` is null, so a new chat is needed. |
| Project match | `list_projects` shows `proj-4471` as Tenant Portal at `/Users/sam/Code/tenant-portal`. That matches the task's project. |
| Authorization | You asked for the chat directly, which covers creating it for T-0142 only. |

T-0139 already has `thread-8c21`, so it needs nothing. T-0150 (Maintenance Desk, `proj-5120`) is also unlinked, but you did not ask for it, so I am leaving it alone and it stays queued.

#### Steps to run for T-0142

1. Set the status:
   `python3 "$TASK_HELPER"` with its status command for T-0142 set to `in-progress`. I do not have the helper's subcommand syntax for status changes in the material provided, so check its `--help` first rather than guessing it.
2. Reserve the task so a repeated run cannot create a second chat:
   `python3 "$TASK_BRIDGE" --reserve T-0142 --expected-hash a91f03c7`
   If the hash is rejected, the note changed after the pending listing. Stop, re-run `--pending` and read the new prompt before continuing.
3. Create the chat with the Codex app's `create_thread` tool:
   - title: `Add arrears-reminder opt-out to settings page`
   - prompt: the prompt from the bridge output, unchanged (checkbox on the tenant settings page, choice stored on the tenant profile and respected by the reminder job, unit tests for the job skip logic, settings page test passing)
   - `target.type=project`, project ID `proj-4471`
   - `environment.type=local`
   - no model override, so your configured model applies
4. Link the returned `threadId`:
   `python3 "$TASK_BRIDGE" --link T-0142 <threadId> --expected-hash a91f03c7`
   If the tool returns only a `clientThreadId`, setup is still pending. Do not link it as a thread ID.
5. Run `python3 "$TASK_BRIDGE"` once with no options and read `System/Sync/Health.md`. The new chat then carries out the work. I will not repeat the same actions in this chat.

If creation or linking ends in an unclear state, keep the reservation, recover the chat ID from the tool result, and do not retry creation.

#### Expected state afterwards

- T-0142 status `in-progress`, with the new chat shown in `Today/Ready Work.md` under Tenant Portal.
- Nothing is complete. When the work finishes, record it with `python3 "$TASK_HELPER" receipt T-0142 --status complete --result '…' --verification '…'`. The verification must name what was run, for example the reminder job's skip-logic unit tests and the settings page test from the task's acceptance line. An idle chat does not close the task.

#### Gaps

- Your config lists no updater and no execution receipts, so I am not claiming that changes made between sessions are picked up automatically. Today's view only updates when the bridge runs.
- The writing checker script was not available here; I read the text over by hand instead.
