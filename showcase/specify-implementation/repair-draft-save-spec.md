---
skill: specify-implementation
title: UI and API spec for saving a repair request as a draft
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 7ae4353bc1c856ed2de2a49fef14ef204b420d9e2d46541462c9e6ef750ea61f
---

## Request

Can you write the detailed UI and API spec for the "save repair request as draft" feature described in inputs/brief.md? The code excerpt in inputs/current-code.md is everything I can share from the repo right now.

## Inputs

Run of the built `write-feature-spec` task package in its "detailed UI and API specification" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### brief.md

#### Brief: save repair request as draft (Larchmont Homes resident portal)

Residents report repairs through a four-field form in the portal: category, room, description, preferred access window. Residents on mobile lose the form when the connection drops or the session times out (30 minutes idle). Support logged 41 complaints about this in September (fictional figure, from the support queue).

##### Requested outcome
- A "Save draft" button on the repair form. Saving keeps what the resident typed.
- When the resident comes back (new login, another device), the portal shows "You have a saved repair request" with Resume and Discard.
- Resume refills the form. Submitting the form turns the draft into a normal repair request.
- A resident has at most one draft per tenancy. Residents with two tenancies (e.g. a flat and a garage) can have one draft each.
- Only the resident who wrote the draft, and joint tenants on the same tenancy, may see it. Housing officers must not see drafts.

##### Decisions
- Confirmed: one draft per tenancy; officers cannot see drafts.
- Open: how long drafts are kept. Product owner (Priya Raman) to decide; not yet decided.
- Open: whether joint tenants can both edit at once. No decision.

##### Out of scope
- Photo attachments (separate project).
- Changing how submitted requests are triaged.

##### Note
The new mobile app will call the save endpoint using `tenancy_id` only. The web portal currently identifies the form by `portal_session_id`.

#### current-code.md

#### Code excerpt (Python / FastAPI, Postgres)

```python
# routes/forms.py
@router.post("/api/form-state")
async def save_form_state(body: FormStateIn, user=Depends(current_resident)):
    # body: portal_session_id (str, required), fields (dict)
    session = await sessions.get(body.portal_session_id)
    if session is None or session.resident_id != user.id:
        raise HTTPException(404)
    await db.execute("DELETE FROM form_state WHERE portal_session_id=$1", body.portal_session_id)
    await db.execute(
        "INSERT INTO form_state (id, portal_session_id, fields, updated_at) VALUES (gen_random_uuid(), $1, $2, now())",
        body.portal_session_id, json.dumps(body.fields))
    return {"ok": True}
```

```sql
-- form_state: id uuid pk, portal_session_id text not null, fields jsonb, updated_at timestamptz
-- repair_request: id uuid pk, tenancy_id uuid not null references tenancy(id), resident_id uuid, category text, room text, description text, access_window text, status text, created_at timestamptz
-- tenancy_member: tenancy_id uuid, resident_id uuid, primary key (tenancy_id, resident_id)
-- A cleanup job deletes sessions idle > 30 min; form_state has no FK to sessions.
```

Not supplied: the repair submit route, the current_resident helper, the front-end component, any test setup, and any existing read endpoint for form_state.

## Output

I wrote the specification for saving a repair request as a draft. It is ready for review but not ready to implement. Two decisions are open, and some files weren't supplied. Nothing has been implemented or run.

#### What the code excerpt changed

- **The existing save route can't hold drafts.** `POST /api/form-state` deletes the row and inserts a new one with a new id on every save. It is also keyed by `portal_session_id` with no foreign key, and the session cleanup job removes idle sessions. A draft stored there would become unreachable after the 30-minute timeout, which is the loss the feature must fix. The spec leaves that route untouched and adds a `repair_draft` table keyed by tenancy.
- **The mobile app and the web portal use different identifiers.** The app sends `tenancy_id` only, and the web form sends `portal_session_id`. The new routes take `tenancy_id` as the only context, so the web form must send the tenancy it is showing. A draft can't be moved to another tenancy.
- **Access follows the existing pattern.** A caller who isn't a `tenancy_member` gets 404, as `routes/forms.py` already does. This covers housing officers, who have no membership.

#### Open decisions

| Decision | Owner | Effect |
| --- | --- | --- |
| How long drafts are kept | Priya Raman | The spec sets no expiry and no cleanup job. Retention criteria are left out. |
| Whether joint tenants can edit at the same time | Not assigned | The spec proposes an optional `base_revision` check that returns 409 on a stale write. Without a decision, the last write wins. |

#### Gaps in what I could read

The repair submit route, the `current_resident` helper, the front-end component, test setup and any row-level security setup were not supplied. The submit change is therefore specified as behavior only. Submit must create the request and delete the draft in one transaction, and its request contract is left until that route is read. Two file paths in the manifest are marked unknown. I proposed a 2,000-character limit per field; the brief gave none.

#### Key content

**Endpoints** (all need an authenticated tenancy member):

| Method and path | Result |
| --- | --- |
| `PUT /api/tenancies/{tenancy_id}/repair-draft` | 201 on first save, 200 on replace with the same `id` and `revision` +1. 409 on stale `base_revision`, 422 on invalid input, 404 for a non-member, 503 if the database is down. A repeated identical request is safe. |
| `GET /api/tenancies/{tenancy_id}/repair-draft` | 200 with the draft, or `{"draft": null}`. This is the readback for return visits and for an unknown save outcome. |
| `DELETE /api/tenancies/{tenancy_id}/repair-draft` | 204 whether or not a draft existed. |

**Table** (additive): `repair_draft(id, tenancy_id NOT NULL REFERENCES tenancy, author_resident_id, fields jsonb, revision, created_at, updated_at)` with `UNIQUE (tenancy_id)`. Save is an upsert on `tenancy_id`, so the id survives. Rollback is dropping the table, which deletes unsubmitted drafts.

**UI states:** first use, saving, saved, return visit (banner with Resume and Discard), resume, discard confirmation, network failure, validation rejection, expired session and stale draft. After a timeout the UI says "We could not confirm the save. Your text is still here." and keeps the input. Retrying is safe. Status messages go in live regions, the Discard dialog traps focus and returns it to the Discard button, and field errors are tied to their fields.

**Acceptance criteria** (16 in the file). Examples:

- Saving twice gives one row and the same `id`.
- A draft saved before the idle timeout appears on another device after a fresh login, and Resume refills all four fields.
- A non-member and an officer both get 404, and the stored draft is unchanged.
- A resident with two tenancies holds two independent drafts.
- Submitting a resumed form creates the request, and the draft readback then returns null.
- A failed submit leaves the draft in place.
- A keyboard and screen-reader pass covers the save status and the discard dialog.

Retention checks are left out until the owner decides.

#### File

- `out/repair-draft-spec.md` is the full specification. It has the problem and confirmed requirements, code findings, UI states with a wireframe, API contracts, data definition, file manifest, acceptance table and assumptions.

### File: repair-draft-spec.md

#### Save repair request as draft: UI and API specification

Status: ready for review. Not ready to implement until the two open decisions below are settled and the uninspected routes are read.

##### 1. Problem and outcome

Residents filling in the repair form on mobile lose their input when the connection drops or the 30-minute idle session expires. Support logged 41 such complaints in September (figure from the brief, support queue).

Outcome: a resident can save the form, leave, and later resume it from any device, then submit it as a normal repair request.

###### Confirmed requirements (brief)

- A "Save draft" button on the repair form keeps the four fields: category, room, description, access window.
- On return, the portal offers Resume and Discard.
- Submitting a resumed form creates a normal repair request.
- One draft per tenancy. A resident with two tenancies can hold one draft in each.
- Visible only to the author and joint tenants of that tenancy. Housing officers cannot see drafts.

###### Open decisions

| Decision | Owner | Effect on this spec |
| --- | --- | --- |
| How long drafts are kept | Priya Raman (product owner) | Section 5 states no expiry and no cleanup job. Retention criteria stay blank until decided. |
| Whether two joint tenants may edit at the same time | Not assigned | Section 4 proposes a stale-write check. Treat it as a proposal. |

###### Out of scope

Photo attachments, and changes to how submitted requests are triaged.

##### 2. What the supplied code shows

| Finding | Consequence for the design |
| --- | --- |
| `POST /api/form-state` in `routes/forms.py` deletes the row for the session and inserts a new one with a new `gen_random_uuid()` id on every save. | A draft's id would change on each save, and a failure between the two statements loses the draft. The new feature uses an upsert on a unique key so the id is stable. |
| `form_state` is keyed by `portal_session_id` with no foreign key to sessions. The cleanup job deletes idle sessions. | A draft stored there would be unreachable once its session is gone, which is the exact loss the feature must fix. Drafts need a tenancy key. |
| The route checks `session.resident_id == user.id` and returns 404 otherwise. | The new routes follow this pattern: 404 for a tenancy the caller does not belong to, so existence is not revealed. |
| `tenancy_member (tenancy_id, resident_id)` has a composite primary key. | It is the membership check for author and joint tenants. |
| The mobile app sends `tenancy_id` only. The web portal sends `portal_session_id`. | The draft endpoints take `tenancy_id` as their only context. The web form must send the tenancy it is editing. |

Not supplied and therefore not inspected: the repair submit route, the `current_resident` helper, the front-end form component, test setup, any read path for `form_state`, and whether the database uses row-level security. Each is named where it matters. The existing `/api/form-state` route stays unchanged.

##### 3. UI behavior

Example wording below is illustrative.

###### Wireframe: repair form with a saved draft

```
Report a repair                         Tenancy: Flat 4, 12 Example Row
+--------------------------------------------------------------+
| You have a saved repair request (saved 3 Nov, 18:42)         |
| [Resume]  [Discard]                                          |
+--------------------------------------------------------------+
Category      [ Heating            v ]
Room          [ Kitchen              ]
Description   [ Radiator will not warm up...                   ]
Access window [ Weekday mornings     ]
              [Save draft]   [Submit request]
```

###### States

| State | Trigger | Visible result | Permitted actions | Next state |
| --- | --- | --- | --- | --- |
| First use | Resident opens the form with no draft | Empty form, Save draft enabled once any field has content | Type, Save draft, Submit | Saving, or Submitting |
| Saving | Select Save draft | Button shows "Saving..." and is disabled. Typed input stays editable. | None on the button until the response | Saved, or Save failed |
| Saved | 200 or 201 response | Status line "Draft saved at 18:42", announced politely | Keep editing, Save again, Submit | Populated |
| Return visit | Resident opens the form on any device with a draft for that tenancy | Banner above the form with saved time, Resume, Discard. Form is empty until Resume. | Resume, Discard, or ignore | Populated, or First use |
| Resume | Select Resume | Fields filled from the draft, banner removed, focus moves to the first field | Edit, Save, Submit | Populated |
| Discard | Select Discard | Confirmation dialog "Discard this saved request?" with Discard and Keep. On confirm the draft is deleted and the banner disappears. | Confirm, Keep | First use |
| Save failed (network) | Timeout or no connection | Message "We could not confirm the save. Your text is still here. Try again." Form content stays. | Save draft (retry), Submit | Saving |
| Save rejected | 422 | Field-level messages below the offending fields | Fix and retry | Saving |
| Session expired | 401 | Sign-in prompt that returns to the form. Typed text is kept in the page until sign-in finishes. | Sign in, then Save | Saving |
| Stale draft (proposed) | 409 | Message "This draft was changed by someone else on your tenancy." with Load latest and Keep mine | Choose one | Populated |

Double activation of Save draft while Saving does nothing. If the connection fails after the request left the device, the outcome is unknown. The UI must not claim success or failure; it shows the "could not confirm" message, and a retry is safe because the save is idempotent (section 4). A later page load shows the true state through the return-visit banner.

###### Accessibility

- Save draft, Resume and Discard are native buttons, reachable by Tab in reading order, operable with Enter and Space.
- The saved and failed messages sit in a live region (`role="status"` for saved, `role="alert"` for failed or rejected).
- Field errors are linked to their fields with `aria-describedby`, and focus moves to the first invalid field after a 422.
- The Discard dialog traps focus, closes on Escape, starts focus on Keep, and returns focus to the Discard button on close. After a confirmed discard, focus moves to the Category field.
- The banner has the accessible name "Saved repair request".

The project's own accessibility standard was not supplied; the checks in section 7 apply until it is.

##### 4. API

All routes require an authenticated resident (existing `current_resident` helper, uninspected). Authorization for each: a `tenancy_member` row for (`tenancy_id`, caller). Otherwise 404. Officers hold no membership through their role, so they get 404.

###### `PUT /api/tenancies/{tenancy_id}/repair-draft`

Creates or replaces the draft for the tenancy. Repeating the same request gives the same result.

Request:

```json
{
  "fields": {
    "category": "Heating",
    "room": "Kitchen",
    "description": "Radiator will not warm up",
    "access_window": "Weekday mornings"
  },
  "base_revision": 3
}
```

- `fields`: required object. Each key is optional, string or null. At least one value must be non-empty. Unknown keys are rejected. Maximum length per value: 2,000 characters (proposed; no limit was supplied).
- `base_revision`: optional integer (proposed, covers the open concurrency decision). Omitted means last write wins. If present and not equal to the stored revision, respond 409.

| Status | Body | When |
| --- | --- | --- |
| 201 | draft object | First save for this tenancy |
| 200 | draft object | Replaced an existing draft. `id` unchanged, `revision` +1 |
| 401 | `{"error":"unauthenticated"}` | No valid session |
| 404 | `{"error":"not_found"}` | Caller is not a member of the tenancy, or the tenancy does not exist |
| 409 | `{"error":"stale_revision","current":<draft object>}` | `base_revision` mismatch |
| 422 | `{"error":"invalid","fields":{"description":"too_long"}}` | Empty, unknown key, or over length |
| 503 | `{"error":"unavailable"}` | Database unavailable. Nothing is partly written. |

Draft object: `{"id","tenancy_id","author_resident_id","fields","revision","updated_at"}`.

###### `GET /api/tenancies/{tenancy_id}/repair-draft`

200 with the draft object, or 200 with `{"draft": null}` when none exists. 401 and 404 as above. This is the readback used on every return visit and after an unknown save outcome.

###### `DELETE /api/tenancies/{tenancy_id}/repair-draft`

204 whether or not a draft existed. 401 and 404 as above.

###### Submit


[trimmed: the rest of this file, about 845 more words, is not shown]
