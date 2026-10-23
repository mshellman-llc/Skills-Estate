---
name: brain-work-item
description: Start, continue, or close Megan's Brain-linked Codex work item. Use when a Brain task ID or daily ready item is the work source, or when finishing a linked task.
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Brain work item

The current task authority is `/Volumes/BeastMode/Personal/Brain`. Read the named note under `Today/Tasks/` and its project brief under `System/Projects/`. Preserve the task ID, evidence, and status history. The task bridge resolves Brain from its current installation; `MEGAN_BRAIN_PATH` can override that location.

## Start or continue work

When Megan starts a ready item, set its status to `in-progress` with the Brain task helper. If the current chat is already linked, continue here. Otherwise create its working chat through the Codex app:

1. Run `/usr/bin/python3 '/Volumes/BeastMode/Projects/MeganOS/megan-os/bin/task_bridge.py' --pending`. It returns each unlinked active task's title, prompt, desktop project ID, and note hash.
2. Use `list_projects` to confirm the returned project ID and folder. Reserve the selected task with the bridge's `--reserve TASK_ID --expected-hash HASH` command. A reservation stops repeated runs from creating another chat.
3. If the plan has `existing_thread_id`, reuse that chat. Otherwise call the Codex app's `create_thread` tool with the returned title and prompt, `target.type=project`, the verified desktop project ID, and `environment.type=local`. Keep the user's configured model. The standing Brain sync plan authorizes this task-specific chat creation.
4. Link the returned `threadId` using the bridge's `--link TASK_ID THREAD_ID --expected-hash HASH` command. It saves the returned ID locally, checks desktop membership and working folder, and links the Brain note only if the note still matches. A `clientThreadId` is pending setup, not a thread ID.
5. Run the bridge once without options and read `System/Sync/Health.md`. The working chat carries out the next action; do not execute that same action in both chats.

If creation or linking has an uncertain outcome, retain the reservation and recover the returned chat ID from the tool result. Do not retry creation blindly. A changed Brain note, unavailable folder, or wrong project stays visible as a queued item or conflict. An existing linked chat is reused.

The daily view at `Today/Ready Work.md` shows every ready item grouped by project and includes each linked chat. The daily 9 a.m. updater recovers changes missed between work sessions.

## Record a work boundary

Use the project's current source folder and guidance. At a real work boundary, record the actual result in Brain:

```sh
/usr/bin/python3 '/Volumes/BeastMode/Projects/MeganOS/megan-os/bin/brain_tasks.py' receipt TASK_ID --status complete --result 'What changed' --verification 'What was checked'
```

Use `blocked` or `in-progress` when that is the actual state. A completion receipt needs specific verification. An idle or archived chat does not close a task. After recording a receipt, run the bridge once so it refreshes the daily view and archives a chat only for an explicit Brain closure.

If Brain is unavailable, retain the result in the chat and report that Brain has not been updated. Keep local preparation, employer submission, publication, deployment, and verified results in their exact states. Preserve Megan's existing authorizations; do not infer new external actions from chat creation.

Former-employer actions marked `closed-no-longer-owned` stay historical. Create a new independent task for continuing work.
