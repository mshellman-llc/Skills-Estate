---
skill: write-architecture-reference
title: Architecture reference for a food pantry slot-booking app
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 704962a9930c507f8002c1b4832d5947542aaf24b09f6a6c7c838028eb15b0d2
---

## Request

Please write the formal architecture reference for PantryLink, our pantry slot-booking app, from the attached brief and decisions record. I need the architecture doc and the system design as one self-contained HTML file for our board's technology committee and the two developers who will build it.

## Inputs

Run of the built `design-software-system` task package in its "formal architecture reference" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `pantrylink-architecture.html`.

#### brief.md

#### PantryLink brief

Harbourline Food Network. Rev 2026-09-12. Author: Dana Okoye, programme manager.

1. **Today.** Harbourline runs 6 pantry sites. Clients phone to book a weekly collection slot and staff keep paper sheets. Staff counted about 1 missed pickup in 5 in August 2026.
2. **What PantryLink is.** A web app. A client books or cancels one weekly collection slot at one site. A pantry coordinator sees the day's list and marks each booking collected. The network manager sees counts per site.
3. **Volume.** About 900 bookings a month across all sites, from the August 2026 phone log.
4. **Clients.** No accounts. A client books with a first name and a phone number and gets an SMS reminder the day before.
5. **Budget.** Run cost ceiling of £150 a month.
6. **People.** Build lead: Tomasz Berg, contract developer. Backup: Aisha Rahman, volunteer developer.
7. **Timing.** Go-live 2 December 2026 with 2 pilot sites.

#### decisions.md

#### PantryLink architecture decisions

Rev 2026-10-21. Accepted by the steering group. This record wins over the brief where they differ.

**D1. Hosting.** One app container and one managed Postgres database, both in a UK region. Host price list, October 2026: container £31 a month, database £19 a month.

**D2. Client identity and reminders.** Version 1 reminders go by email only. The SMS provider quote has not arrived, so SMS is deferred. Clients book with a first name and an email address, and receive a private manage link by email. No phone number is stored. This replaces brief item 4.

**D3. Staff sign-in.** Coordinators sign in with email and a one-time code. Each coordinator is assigned to exactly one site. The network manager has read-only counts and never sees client names.

**D4. Isolation.** Every table carries site_id. Postgres row-level security filters on site_id. Marking a booking collected also requires the coordinator role. A site match alone is not enough.

**D5. Booking and reminders.** Capacity is checked inside the booking transaction. Bookings are unique on slot and client email. A daily job at 16:00 sends reminders and records each one in a reminders table, unique on booking and reminder date. A rerun skips sent reminders and retries unsent ones.

**D6. Retention.** Client name and email are deleted 90 days after the slot date. Counts are kept.

**Open.**
- O1. SMS provider cost and volume terms.
- O2. Whether pantry sites have a tablet or laptop for coordinators. Not confirmed.

## Output

I've written the PantryLink reference as one self-contained HTML file. It covers both the architecture doc (what and why) and the system design (engineering how). The facts in it come from your brief and decisions record. Anything I added is labelled "Design proposal" with its trade-off.

**File:** `out/pantrylink-architecture.html` (status: design for review, rev 2026-11-04, owner Tomasz Berg)

#### Decisions for you

1. **The record overrides the brief on reminders.** Brief item 4 asks for a phone number and an SMS reminder. Decision D2 replaced that with an email address and an email reminder, so I followed D2. The document says so in its overview.
2. **The weekly limit isn't enforced anywhere.** The brief says one weekly slot per client. D5 only makes bookings unique on slot and email, so one email could book two slots in a week. I left this as open item O3 and did not invent a rule.
3. **The six-site cost can't be checked against the £150 ceiling.** The sourced running cost is £31 (container) + £19 (database) = **£50 a month**. The email service has no price, and there are no six-site figures. The document leaves those cells as "Not sourced" and doesn't say the cost fits.
4. **Coordinator devices are unconfirmed (O2).** It blocks the pilot day list at any site without a tablet or laptop.

#### What the document contains

**Part A, architecture**
- Product shape: three surfaces (client booking page, coordinator day list, manager counts), each with its identity rule.
- A systems map. It labels each relationship, marks the trust boundary and states that email leaves Harbourline's control once sent.
- Security posture, cost and ownership, a six-step stand-up with a proving check for each step, jobs to be done, growth and risks.

**Part B, system design**
- Requirements, each with a source locator. There is no latency or availability target in the sources, and the document says so rather than inventing one.
- Load arithmetic: 900 bookings a month ÷ 30 days ≈ 30 a day, so about 30 reminder emails a day. Peak rate is not measured and no peak figure is given.
- An access matrix covering action, who, checks, where enforced and what denial returns. Marking a booking collected needs the coordinator role **and** a site match, as D4 requires. Anything that can't be evaluated is denied.
- An illustrative schema with `site_id` on every table and the unique constraints from D5.
- An API table and a booking example (`201` booked, `409 slot_full`).
- A reminder job design. Reading "already sent" before sending doesn't stop two overlapping runs, so I added an atomic claim with a lease. A failed claim is handled by case: sent means skip; a live lease means leave it and don't mark it done; an expired lease means take it over.
- If the job dies, the lease expires and the next run claims the row. D5 names only one daily run, so I proposed a second run later the same afternoon. The lease length and run time are left to the build lead.
- A remaining failure window, stated plainly: the provider can accept an email and the job die before it records "sent", so a retry sends a duplicate. Delivery is at least once, not exactly once.
- A five-row trade-offs table with a revisit trigger for each choice.

#### Proposals that go beyond the record

These are marked in the document and need the steering group's agreement:
- Hashed manage-link token (forwarded links grant control, and links can't be revoked except by cancelling the booking).
- Locking the slot row inside the booking transaction.
- The claim-and-lease reminder design and the second daily run.
- A separate aggregate path for the manager's counts.
- Monitoring alerts.
- The stand-up steps.

#### Open items shown in the document

- **O1:** SMS provider terms.
- **O2:** coordinator devices.
- **O3:** weekly limit.
- **O4:** email provider, price and limits.
- **O5:** availability target, backups and people time.
- **Backup retention:** the host's backup retention isn't in the sources, and it affects D6's 90-day deletion promise.
- **Clients without email:** they can't book under D2. A decision on whether phone booking stays for them belongs to the steering group.

#### How I checked it

- **Scripts:** I could not run any scripts here, so the brand and prose checks, the receipt and the quality gate were not run. I applied the rules by hand instead.
- **Styling:** I used the neutral Baseline profile. It has no logo, uses the Baseline palette, system fonts, 1px borders and sentence-case headings, with no colored side accents. I did not render the page in a browser or run an automated contrast check. Body text uses the profile's text and muted colors on white.
- **Prose and sources:** I read all text and interface labels against the writing standard. I checked every figure and locator against `brief.md` and `decisions.md`, and no figure appears that isn't in them or derived from them in the document.
- **Not delivered:** this is HTML only, with no separate export.
