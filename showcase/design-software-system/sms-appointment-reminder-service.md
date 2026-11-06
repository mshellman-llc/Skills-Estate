---
skill: design-software-system
title: Design for an SMS appointment reminder and reply service
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: a85c9e72b9cd4db699a8d758270748b7a18cdd8f08a26ddb03cb99b75e639b56
---

## Request

We want to replace our nightly appointment-reminder script with a proper service that sends SMS reminders and lets patients confirm or cancel by replying. My notes and the current setup are in the inputs folder; can you design it and tell me what you'd recommend and what the trade-offs are?

## Inputs

Run of the built `design-software-system` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### current-script.txt

Current setup (written by Tomas Ibarra, from memory of the script; the script itself is not attached)

- A Python script runs from cron at 17:00 each weekday on VM-1.
- It reads tomorrow's appointments from the SchedBook read-only reporting view (columns: appt_id, patient_id, clinic_id, start_time, mobile, status).
- For each row it calls the Northgate send API one at a time and writes a line to a log file. No database record is kept of what was sent.
- Twice last year the script was re-run by hand after a crash partway through; some patients received two texts. Nobody counted how many.
- Replies arrive in a Northgate inbox. A front-desk person reads them and updates SchedBook by hand.
- SchedBook exposes a REST endpoint to cancel an appointment (POST /appointments/{id}/cancel, requires an API key). We have not tested it. Whether repeating the call is harmless is unknown.
- STOP replies are not tracked anywhere except Northgate's own opt-out list.

#### requirements-notes.md

#### Reminder service: notes from planning meeting (Priya Raman, ops lead)

Harbourline Community Health runs 6 clinics. Appointments live in the scheduling system (vendor product "SchedBook"), which we cannot modify.

##### What we want
- SMS reminder 48 hours and 4 hours before each appointment.
- Patient replies C to confirm, X to cancel. A cancel must free the slot in SchedBook so the front desk can rebook it.
- Front-desk staff see reminder status (sent, delivered, confirmed, cancelled, failed) on a per-clinic screen. Staff should see only their own clinic's patients.
- Patients who reply STOP must never be texted again.

##### Numbers we have
- About 1,400 appointments per weekday across all clinics; clinics closed weekends.
- Last quarter, no-show rate was 14%. Goal is under 10%. (Target is ours, not a promise.)
- SMS provider is Northgate Messaging (example.com account). Their API returns a message ID and sends delivery receipts by webhook. Rate limit: 20 messages per second.

##### Constraints
- One developer (Tomas Ibarra) plus part-time help from IT. Go-live target is the end of January.
- Existing stack is a single Postgres 15 database and two small VMs on a cloud provider. Team knows Postgres and Python; no one has run a message broker.
- Message text must not include diagnosis or clinic service type, only date, time, clinic name and a call-back number. Compliance has asked for this.
- Budget: no figure given.

##### Not decided
- Whether reminders go out in the patient's language (we hold a language field, about 70% filled).

## Output

#### Recommendation

Build one small Python service on your existing Postgres 15 database, with no message broker. Run two processes from the same code: a **web** process (Northgate webhooks and the staff screen) and a **worker** process (sync from SchedBook, send, cancel). Both can run on VM-1 and VM-2 because workers claim rows with `FOR UPDATE SKIP LOCKED`.

The duplicate texts came from the old script keeping no record of what it sent. A unique reminder row per appointment and kind, written before each send, fixes that. Volume is small (about 0.14 webhook calls per second), nobody on the team has run a broker, and Tomas Ibarra can build this with skills already in the team.

**What I inspected:** Priya Raman's planning notes and Tomas's description of the current script. **Not available:** the script itself, SchedBook and Northgate API documentation, and any count of past duplicates. The design marks what depends on those.

#### Design

```
 SchedBook view ──poll 5 min──▶ worker (sync, send, cancel) ──▶ Northgate send API
 SchedBook cancel API ◀──────── worker
                                   │ claim / update
 Northgate webhooks ─▶ web ─────▶ Postgres 15 ◀───── web ◀── staff browser
```

- **Sync:** every 5 minutes, upsert appointments from the reporting view and create a 48h and a 4h reminder row each. A cancelled or rescheduled appointment cancels unsent reminders.
- **Sender:** claims a due row, re-checks appointment status and the opt-out list, sends, stores the Northgate message ID.
- **Webhook:** verifies the signature, stores the event in `inbound_event` (unique on provider event ID), then answers 200. That stored row is the durable hand-off; Northgate redelivers if it gets no 200.
- **Replies:** STOP writes to a local `opt_out` table and skips pending reminders. C marks the reminder confirmed. X creates one `cancel_request` per appointment; the cancel worker reads the appointment status from SchedBook first, calls the cancel endpoint, retries four times, then shows the failure to staff for a manual cancel.

**Tables:** `appointment`, `reminder` (UNIQUE on appointment and kind; state, claim owner, claim expiry, provider message ID, attempts), `inbound_event`, `cancel_request`, `opt_out`, `staff_clinic_grant`.

**Authorization:**

| Principal | Allowed | Denied when |
| --- | --- | --- |
| Northgate | Post events | Signature invalid |
| Patient | Confirm or cancel an appointment whose mobile on file matches the sender | Number does not match |
| Front-desk staff | View reminders for clinics in their grant | No grant, or grant lookup unavailable |

A clinic filter alone does not give permission; staff need a login and a grant row. The staff screen is read-only in version 1.

#### Failure handling

A worker that dies after Northgate accepted a message but before the ID was stored leaves the row `sending` with an expired claim. The service cannot tell whether the text went out. If Northgate can look up a message by client reference (unknown), the sweeper checks. If not, it marks the row `unknown`, does not resend, and shows it on the staff screen. That accepts a missed reminder in a rare crash instead of a duplicate. An unexpired claim means another worker owns the row, so the sweeper leaves it. Every worker runs the sweeper, so the surviving worker restarts the dead one's work.

Timeouts and 5xx responses retry at 30 s, 2 min and 10 min, then `failed`. A 429 waits and is not counted as an attempt.

#### Scale

- Outbound: 1,400 × 2 = 2,800 messages per weekday. One burst at 20 per second takes 2,800 / 20 = 140 seconds; in practice they spread across the day.
- Inbound (assumed 40% reply rate): 0.4 × 2,800 = 1,120 replies, plus 2,800 delivery receipts, about 3,920 webhook calls per day.
- Storage: 2,800 × 260 weekdays = 728,000 reminder rows a year.

One Postgres instance carries this. Add workers to scale. Postgres is the single point of failure; no backup arrangements were supplied, so confirm a nightly backup before go-live.

**First alerts:** pending reminders more than 10 minutes overdue; any `unknown` or `failed` reminder; sync lag over 15 minutes; cancel requests not done after 15 minutes; webhook errors and signature failures.

#### Trade-offs

| Decision | Alternative | Why it lost | When it wins |
| --- | --- | --- | --- |
| Postgres as the queue | RabbitMQ or SQS | Nobody has run one; volume is low | Other services need the events, or volume grows about 100× |
| No resend on `unknown` | Resend | Avoids repeating the duplicate problem | Northgate lookup exists, or missed reminders cost more than duplicates |
| Poll SchedBook | SchedBook notifications | Vendor product cannot be changed | SchedBook adds change notifications |
| Cancel on one X | Second confirming reply | Fewer steps for patients | A family sharing a number causes a wrong cancellation |
| Read-only staff screen | Staff can resend or cancel | Smaller permission surface | Front desk asks and an audit trail exists |

#### Assumptions to confirm

- **A1/A2:** Sends fall between 08:00 and 20:00 clinic time, which puts the 48-hour reminder for a Monday appointment on Saturday morning. Please confirm weekend texts are acceptable.
- **A3:** 40% reply rate is a sizing guess; your notes give none.
- **A4:** SchedBook's reporting view is current within a few minutes.
- **A5:** Northgate supports a client reference and lookup.
- **Budget:** none given; the design adds no paid component.
- **Language:** version 1 sends English only, since the language field is about 70% filled. This was undecided in your notes.

#### Test before building

1. Is SchedBook's cancel call safe to repeat, and is the reporting view's status current? Test in a non-production account. The retry logic reads status first until this is known.
2. Does Northgate support client references and lookup?

#### Revisit as it grows

| Revisit | Earliest signal |
| --- | --- |
| Add a broker | Webhook backlog or lock waits in the slow-query log |
| Two-step cancel | First wrongly cancelled appointment on a shared number |
| Translated templates | Front desk reports patients unable to read English text |
| Postgres failover | Any outage delaying reminders by more than an hour |
| Staff actions on screen | Repeated requests for manual resend |

The 14% to under 10% no-show goal is yours; this design does not predict that outcome. Measure it after go-live.

#### Release check

I could not run the bundled prose checker, receipt tool or review-deliverable scripts here. I checked the wording by hand and recomputed every figure above. There is no scanner result or receipt, so a scripted quality record would show the prose and receipt checks as blocked. This is a working design in Markdown, so the brand check does not apply. Nothing has been built, sent or tested against SchedBook or Northgate.

#### File

- `out/reminder-service-design.md` — the full design: requirements, authorization table, data model, interfaces, claim query, failure handling, scale arithmetic, observability and trade-offs.

### File: reminder-service-design.md

#### Appointment reminder service: design

##### Recommendation

Build one small Python service on the existing Postgres 15 database, with no message broker. Postgres holds the appointments, the reminder queue, the inbound replies and the opt-out list. Two processes run from the same code: a web process (Northgate webhooks and the staff screen) and a worker process (sync, send, cancel). Both can run on VM-1 and VM-2 at the same time because workers claim rows with `FOR UPDATE SKIP LOCKED`.

The main reason for this shape is the duplicate texts from the old script. They happened because nothing recorded what had been sent. A unique row per appointment and reminder kind, written before the send, fixes that without new infrastructure. Nobody on the team has run a broker, and the volume does not need one.

##### Inspected and not available

Inspected: the planning notes and Tomas Ibarra's description of the current script. Not available: the script itself, the SchedBook API documentation, the Northgate API documentation, and any count of past duplicates. Everything below that depends on those is marked as an assumption or an open question.

##### 1. Requirements

Functional (from the notes):
- Send an SMS 48 hours and 4 hours before each appointment.
- Reply C confirms; reply X cancels the appointment in SchedBook.
- Reply STOP permanently stops texts to that number.
- A per-clinic screen shows sent, delivered, confirmed, cancelled and failed. Staff see only their own clinic.
- Message text contains only date, time, clinic name and a call-back number.

Non-functional:
- About 1,400 weekday appointments (given). Target no-show rate under 10% against 14% last quarter (the clinic's goal; this design does not predict it will be reached).
- Northgate allows 20 messages per second (given).
- One developer, go-live end of January, Postgres and Python skills only (given).

Assumptions (marked A):
- A1: Reminders send between 08:00 and 20:00 clinic time. A reminder due outside that window goes out at 20:00 the previous evening or 08:00, whichever is nearer inside the window. Confirm with Priya Raman.
- A2: Weekend appointments do not exist, but 48-hour reminders for Monday morning fall on Saturday. A1 moves them to Saturday 08:00. Confirm whether weekend texts are acceptable.
- A3: About 40% of patients reply. The notes give no reply rate; this is a sizing guess.
- A4: SchedBook's reporting view is refreshed within a few minutes. Unknown.
- A5: Northgate can attach a client reference to a send, and can look a message up by it. Unknown; the design works without it.
- A6: Budget is unstated, so cost is judged only as "no new paid components".

##### 2. High-level design

```
 SchedBook reporting view ──poll 5 min──▶ ┌──────────────┐
                                          │  worker      │──send──▶ Northgate API
 SchedBook cancel API ◀──cancel───────────│  (sync, send,│
                                          │   cancel)    │
                                          └──────┬───────┘
                                                 │ claim / update
                                          ┌──────▼───────┐
 Northgate webhooks ──▶ ┌──────────┐      │  Postgres 15 │
 (delivery, inbound)    │  web     │─────▶│              │
 Staff browser ────────▶│  process │◀─────│              │
                        └──────────┘      └──────────────┘
```

Components:
- **Sync (worker):** every 5 minutes reads appointments from the reporting view and upserts them. New rows create two reminder rows. A cancelled or rescheduled appointment cancels unsent reminders and creates new ones.
- **Sender (worker):** claims due reminders, re-checks the appointment and opt-out status, sends through Northgate, records the message ID.
- **Webhook handler (web):** verifies the Northgate signature, writes the event to `inbound_event`, then answers 200. It does no other work.
- **Inbound processor (worker):** reads `inbound_event` rows, applies STOP, C and X.
- **Staff screen (web):** read-only list of reminders for the user's clinic.

###### Identity and authorization

| Principal | Allowed | Enforced | Denial |
| --- | --- | --- | --- |
| Northgate (webhook) | Post delivery and inbound events | Signature check in the web process | 401, event not stored |
| Patient (SMS reply) | Confirm or cancel an appointment whose number on file matches the sender | Inbound processor | Reply ignored and logged |
| Front-desk staff | View reminders for clinics they are granted | Web process, per request | 403 |
| Worker | Call the SchedBook cancel API with the service key | Key held only on worker hosts | Task goes to failed state |

Clinic filtering alone does not give permission to act. Staff access needs both a valid login and a row in `staff_clinic_grant`. If the grant lookup or the login provider is unavailable, the screen denies. The service never lets staff cancel or edit through the screen in this version, so no write permission is needed there.

A reply cancels only when the sender number equals the mobile on the appointment and the appointment has at least one reminder sent to that number. A number shared by a family could cancel another member's appointment; the reply text names the date and time and allows a "reply Y to confirm cancellation" step (see trade-offs).

##### 3. Deep dive

###### Data model

| Table | Key columns | Notes |
| --- | --- | --- |
| `appointment` | `appt_id` (PK), `patient_id`, `clinic_id`, `start_time`, `mobile`, `status`, `synced_at` | Mirror of the view |
| `reminder` | `id`, `appt_id`, `kind` (48h/4h), `due_at`, `state`, `claim_owner`, `claim_expires_at`, `provider_msg_id`, `attempts`; UNIQUE (`appt_id`, `kind`) | The queue and the audit record |
| `inbound_event` | `provider_event_id` (UNIQUE), `kind` (reply/delivery), `payload`, `received_at`, `processed_at` | Webhook landing table |
| `cancel_request` | `id`, `appt_id` (UNIQUE), `state`, `claim_owner`, `claim_expires_at`, `attempts` | One cancel per appointment |
| `opt_out` | `mobile` (PK), `at` | Checked before every send |
| `staff_clinic_grant` | `staff_id`, `clinic_id` | Staff screen authorization |

Reminder states: `pending → sending → sent → delivered`, plus `confirmed`, `failed`, `skipped` (opted out, cancelled or past), and `unknown` (see failure handling). Access patterns: due reminders by `due_at` where state is `pending`, reminders by clinic and date for the screen, events by `processed_at IS NULL`.

###### Interfaces

- `POST /hooks/northgate` — Northgate calls it. Idempotent through `provider_event_id`.
- `GET /clinics/{clinic_id}/reminders?date=` — staff screen data. Checks the grant.
- Outbound: Northgate send, SchedBook `POST /appointments/{id}/cancel`.

No other endpoints. A cancel in SchedBook is not known to be safe to repeat (open question 1).

###### Sending and failure handling

1. The sender claims a row: `UPDATE reminder SET state='sending', claim_owner=:w, claim_expires_at=now()+2 min WHERE id = (SELECT id FROM reminder WHERE state='pending' AND due_at<=now() FOR UPDATE SKIP LOCKED LIMIT 1)`. The unique key on (`appt_id`, `kind`) means a re-run of the sync cannot create a second row.
2. It re-reads the appointment and the opt-out list. If the appointment is cancelled, in the past or opted out, state becomes `skipped`.
3. It calls Northgate, with a client reference of the reminder id if A5 holds, then stores `provider_msg_id` and sets `sent`.
4. Timeouts and 5xx responses set the row back to `pending` with a backoff of 30 s, 2 min, 10 min; after 4 attempts the state is `failed`. A 429 waits for the 20 per second limit and does not count as an attempt.


[trimmed: the rest of this file, about 715 more words, is not shown]
