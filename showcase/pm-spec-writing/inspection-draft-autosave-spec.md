---
skill: pm-spec-writing
title: Spec for autosaving and resuming inspection drafts on poor signal
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 6adc8ca7812b4ae14a7b5278ba1d03d8ef4f3af2dd79bf65db3d67b9345b4259
---

## Request

Can you write the feature spec for autosaving and resuming site inspection drafts in our inspector web app? My brief and the engineer's notes on the current API are in the inputs folder; the main thing is that inspectors on poor signal stop losing their work.

## Inputs

Run of the built `feature-spec` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### api-notes.md

#### Current API notes (from Kofi Adeyemi, backend engineer)

Written from memory; I have not re-read the code this week.

- `POST /api/inspections/submit` takes `{ session_id, site_id, items: [{ item_id, answer, note }] }`. Auth is the `requireInspector()` helper, which returns the inspector's user ID.
- `session_id` is the login session, not the visit. It changes when the inspector logs in again.
- Submit writes to `inspections` (one row) and `inspection_items`. I believe the items save does DELETE then INSERT for the inspection, so item row IDs change on every save.
- `inspection_items` has a unique key on (inspection_id, item_id) and a foreign key to `inspections`.
- Nothing reads a half-finished inspection today. I do not know of any GET endpoint for inspections an inspector owns; the supervisor list reads submitted rows only.
- Answers are `pass`, `fail`, `na`. A `fail` requires a note of at least 10 characters (validated client-side only).
- I have not checked whether `inspections` has a status column.

#### brief.md

#### Brief: inspection drafts (Tallow Row Facilities)

Author: Priya Nandakumar, product manager. Contact: priya@example.com

##### Problem
Inspectors complete a 40-to-60 item checklist on a phone, often in plant rooms and basements with weak signal. Today nothing is saved until they tap Submit. If the page reloads, the phone locks for long enough to drop the session, or Submit fails on a bad connection, the whole checklist is gone. Support logged 14 "lost inspection" tickets in October 2026.

##### Wanted
- The checklist saves automatically as the inspector works, without them tapping anything.
- If the connection drops, they keep working; changes are sent when the connection returns.
- Reopening the inspection later (same phone or another device) restores answers and notes.
- Submit still works as it does now and turns the draft into the final inspection.

##### Rules I am sure of
- Only the inspector who started an inspection can open or edit its draft. Supervisors can see submitted inspections only (existing behaviour).
- One draft per inspector per site visit.
- Photos are out of scope for this release; they upload separately and already work.

##### Not decided
- How long an abandoned draft is kept. Ask Operations (Tomasz Berg).
- Whether a supervisor may take over a draft when an inspector is off sick.
- Launch date.

##### Success
Fewer lost-inspection tickets. I have not agreed a target with support.

## Output

I've written the spec for inspection draft autosave and resume. It's ready for review, but not for implementation yet. Four decisions are open, and the first one changes how a draft is identified.

**File:** `out/inspection-draft-spec.md` (Markdown, feature-spec depth with API, data and states)

#### What the spec says

**Outcome.** Answers and notes are saved on the server as the inspector works. Edits made offline queue on the phone and send when signal returns. The inspector can reopen the draft on any device after a reload or re-login. Submit keeps working and turns the draft into the final inspection. Support logged 14 lost-inspection tickets in October 2026, and that is the only baseline in your material.

**Design points that come from Kofi's notes**
- `session_id` is the login session and changes on every login, so it can't identify a draft. The client creates an `inspection_id` (UUID) when the checklist opens. A resume list for the site lets a second device find it.
- Kofi believes the item save does DELETE then INSERT. Autosave must upsert on the existing (`inspection_id`, `item_id`) key and write only the changed items. Otherwise each save would replace item row IDs, and a partial request could wipe answers it didn't mention.
- No read path exists for unsubmitted inspections. The spec proposes three endpoints:
  - `PUT /api/inspections/{inspection_id}/draft` takes changed items and a `base_revision`. It returns the new `revision`, or 409 when the revision is stale.
  - `GET /api/inspections/{inspection_id}/draft` returns the owner's draft.
  - `GET /api/inspections/drafts?site_id=` lists the caller's own drafts.
- A draft owned by another inspector returns 404, so its existence isn't disclosed.
- `POST /api/inspections/submit` gains an optional `inspection_id`, so older app versions keep working. If a request carries both `session_id` and `inspection_id`, both must belong to the caller, or it is rejected with 409 and nothing is written. A submit can't move an existing inspection to another site or session. A repeated submit writes nothing new.
- After a timeout, a lost response is retried safely. A 409 on retry triggers a read-back. If the server already holds the pending edits, the save counts as done. Otherwise the inspector sees a conflict dialog.
- The 10-character rule for a `fail` note is client-side only today. Drafts accept short notes, and the rule moves server-side at Submit. Kofi should review that change.

**Interface states.** The spec covers New, Resume available, Saving, Saved, Offline, Conflict, Rejected and Submitting. Each has a trigger, what the inspector sees, and the next state. It also covers a polite live-region save indicator, focus handling for the two dialogs, and keyboard-only use.

**Data.** The changes are additive. `inspections` gets a `status` (default `'submitted'`, so existing rows are untouched), a `revision` and an `updated_at`. `inspection_items` needs no schema change. Supervisor queries must filter to submitted rows, and every query that reads `inspections` needs checking for that.

**Acceptance.** There are 15 criteria, each with an action, an observable result and a check method. They include:
- offline edits reaching the server
- resume after re-login
- the same item row ID after repeated saves
- a lost-response retry
- a two-device conflict
- denied access for another inspector
- supervisors not seeing drafts
- the old client still submitting
- screen-reader and keyboard checks

#### Decisions still open

| # | Decision | Owner | What it blocks |
| --- | --- | --- | --- |
| 1 | What counts as one "site visit" | Priya | Draft identity. I assumed site plus the inspector's local calendar date, and marked it as an assumption. |
| 2 | How long an abandoned draft is kept | Tomasz Berg | Cleanup rule. The spec specifies no deletion. Discard marks a draft as discarded. |
| 3 | Whether a supervisor can take over a draft | Priya | Until decided, only the owner has access. |
| 4 | Whether `inspections` already has a status column | Kofi | Whether to reuse it or add one. |
| 5 | Launch date | Priya | Nothing in the behaviour. |

#### Gaps and limits
- I had no code access. Everything about current behaviour (DELETE then INSERT, no read path, client-only validation, the session ID's lifecycle) is Kofi's recollection from his notes. The spec lists what to read before building: the submit handler, `requireInspector()`, the `inspections` schema and the supervisor query.
- No success target is set. The spec proposes tracking lost-inspection tickets against October's 14, with a target and window agreed by you and support before launch.
- Nothing was implemented, migrated or run. The acceptance checks are planned, not executed.
- I couldn't run the bundled writing checker (`writing_check.py`). I did a manual read of the text instead, so no scanner result stands behind it.

### File: inspection-draft-spec.md

#### Inspection drafts: autosave and resume

Status: ready for review. Not ready for implementation until decisions 1 to 4 below are settled.
Source: Priya Nandakumar's brief and Kofi Adeyemi's API notes. No code was read, so every statement about current behaviour is Kofi's recollection and is marked as such.

##### Problem and outcome

Inspectors fill in a 40-to-60 item checklist on a phone, often with weak signal. Nothing is stored until they tap Submit, so a reload, a dropped login session or a failed Submit loses the whole checklist. Support logged 14 lost-inspection tickets in October 2026.

Outcome: answers and notes are stored on the server while the inspector works, work continues through a connection drop, and the inspector can reopen the draft later on any device and finish it. Submit keeps working and turns the draft into the final inspection.

No ticket-reduction target exists. Measurement work is proposed in the last section; this spec sets no target.

##### Confirmed requirements (from the brief)

- Autosave without an inspector action.
- Changes made offline are sent when the connection returns.
- A draft reopens on the same or another device with answers and notes restored.
- Only the inspector who started the draft can read or edit it. Supervisors see submitted inspections only.
- One draft per inspector per site visit.
- Photos are out of scope.

##### Open decisions

| # | Decision | Owner | Effect |
| --- | --- | --- | --- |
| 1 | What counts as one "site visit" | Priya Nandakumar | Sets the draft's identity. This spec assumes site plus the inspector's local calendar date. |
| 2 | Retention of an abandoned draft | Tomasz Berg (Operations) | Sets the cleanup rule and the resume list. No deletion is specified here. |
| 3 | Supervisor takeover of a draft | Priya Nandakumar | Until decided, only the owner has access. |
| 4 | Whether `inspections` has a status column | Kofi Adeyemi to check | Decides between reusing it and adding one (see Data). |
| 5 | Launch date | Priya Nandakumar | Does not block the behaviour below. |

##### Current behaviour (unverified, from Kofi's notes)

- `POST /api/inspections/submit` takes `{ session_id, site_id, items: [{ item_id, answer, note }] }`. Authentication is `requireInspector()`, which returns the user ID.
- `session_id` identifies the login session and changes on every new login. It cannot identify a visit.
- Items are probably saved by DELETE then INSERT, so `inspection_items` row IDs change on each save. The table has a unique key on (`inspection_id`, `item_id`) and a foreign key to `inspections`.
- No endpoint reads an unsubmitted inspection. The supervisor list reads submitted rows.
- The rule that a `fail` needs a note of 10 or more characters runs in the client only.

Consequence for the design: autosave must update items in place on (`inspection_id`, `item_id`), so repeated saves keep row IDs and never delete answers the request did not mention. The login `session_id` cannot key a draft, because the inspector would lose it on re-login.

##### Behaviour

###### Identity

The client creates an `inspection_id` (UUID) when the inspector opens a checklist for a site and stores it locally. The server accepts it only if it is new or already owned by the caller. A second device finds the draft through the resume list (below), which returns the existing `inspection_id`.

###### States

| State | Trigger | What the inspector sees | Next state |
| --- | --- | --- | --- |
| New | Opens a checklist for a site with no draft today | Empty checklist, indicator "Not saved yet" | Saving on first answer |
| Resume available | Opens a site where the caller has a draft for the same visit | Prompt: "Continue your draft from 09:42?" with Continue and Discard. Continue loads the draft. | Populated |
| Saving | Answer or note changes | Indicator "Saving…". Inputs stay enabled. Changes are batched, at most one request in flight. | Saved, Offline or Rejected |
| Saved | Server acknowledges | Indicator "Saved 09:44" | Saving on next edit |
| Offline | Request fails or no connectivity | Indicator "Offline. Changes kept on this phone." Inputs stay enabled and edits queue locally. | Saving when connection returns |
| Conflict | Server reports a newer revision | Dialog: "This draft was changed on another device." Actions: Load latest, which discards queued local edits for the items that differ, or Keep mine, which resends them on top of the latest revision. | Saved |
| Rejected | Server returns 4xx other than 409 | Indicator "Could not save" with the reason; local edits stay on screen. | Saving on retry |
| Submitting | Tap Submit | Submit disabled until the response. | Submitted, or back to Saved with errors |

Discard in the resume prompt asks for confirmation and then marks the draft as discarded. It is not a hard delete until decision 2 is made.

###### Accessibility

- The save indicator is a text element in a polite live region. Changes between Saving, Saved and Offline are announced; "Saving…" is not announced on every keystroke, only when it has lasted over 2 seconds.
- The conflict dialog and resume prompt take focus on open, trap it, and return focus to the control that opened them (or to the first checklist item for the resume prompt) on close.
- Both dialogs work with the keyboard alone, and every button has a text name.
- Failed-item validation messages at Submit are linked to their fields.

##### API (proposed)

All endpoints use `requireInspector()`. The caller must own the `inspection_id`; a draft owned by someone else returns 404, not 403, so its existence is not disclosed.

###### PUT /api/inspections/{inspection_id}/draft

Request:

```json
{
  "site_id": "string",
  "base_revision": 0,
  "items": [{ "item_id": "string", "answer": "pass|fail|na|null", "note": "string|null" }]
}
```

- `items` holds only changed items. Each is upserted on (`inspection_id`, `item_id`). Items not listed are untouched.
- `base_revision` is the last revision the client received; 0 for a new draft.
- Notes shorter than 10 characters on a `fail` are accepted in a draft.
- 200: `{ "inspection_id", "revision", "saved_at" }`. Revision increases by 1 per accepted request.
- 400: unknown `item_id`, answer outside the allowed set, or missing `site_id`.
- 409: `base_revision` is behind the server. Response carries the current `revision` and the items changed since.
- 409 with code `already_submitted`: the inspection is final; drafts cannot be edited.
- 403: `inspection_id` exists with a different `site_id` for the caller. Site never changes after creation.
- 503 or timeout: dependency unavailable; the client treats it as Offline.
- Retry safety: item upserts are idempotent. If the first attempt committed but the response was lost, the retry returns 409. The client then reads the draft, and if the server's items equal its pending items it treats the save as done; otherwise it shows the Conflict state.

###### GET /api/inspections/{inspection_id}/draft

Returns `{ inspection_id, site_id, revision, saved_at, items: [...] }` for the owner. 404 if missing, discarded, submitted or owned by another user.

###### GET /api/inspections/drafts?site_id={site_id}

Returns the caller's own drafts, newest first, with `inspection_id`, `site_id`, `saved_at`. Empty list when none.

###### POST /api/inspections/submit (changed)

- Adds optional `inspection_id`. A caller that omits it behaves as today, so older app versions keep working.
- When both `session_id` and `inspection_id` are given, the session must belong to the caller and the draft must be owned by the caller; otherwise the request is rejected with 409 and no write occurs. An existing inspection keeps its original context; the request cannot move it to another site or session.
- Items from the request are upserted by (`inspection_id`, `item_id`) and the status moves to submitted in one transaction. Server-side validation of the 10-character `fail` note applies at submit (a change from client-only, flagged for Kofi's review). Failures return per-item errors and leave the draft as it was.
- Repeating a submit for an inspection that is already submitted returns the existing result and writes nothing.

##### Data (proposed, additive)

- `inspections`: if a status column exists, add `draft` and `discarded` values and check that existing rows read as submitted. If not, add `status` text not null default `'submitted'`, `revision` integer not null default 0, `updated_at` timestamptz. Existing rows need no backfill beyond the defaults. Adding columns is non-destructive; rollback is dropping the added columns before any draft rows exist.
- `inspection_items`: no schema change. Writes switch from DELETE and INSERT to upsert on the existing unique key.
- A uniqueness rule for decision 1: unique on (owner user ID, `site_id`, visit date) for rows with status `draft`. Final wording waits for decision 1.
- Access: draft rows are readable and writable by the owning user only. Supervisor queries must filter to `status = 'submitted'`; this needs a check in every query that reads `inspections`.

##### Read-back and ownership


[trimmed: the rest of this file, about 654 more words, is not shown]
