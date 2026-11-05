---
skill: ddoc
title: Scope decision deck for a multi-clinic scheduling project
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: b4190b6f05c8fe0301adfc24fb3ba516ed6550f343e0aae0a2b6319abd26799f
---

## Request

We present to Larkspur Veterinary Group on Thursday and need the scope decision deck for the clinic scheduling project, with their choice between the three quoted options. The discovery notes and the quote export are attached. Please gate the copy and tell me what still needs approval before we build.

## Inputs

Run of the built `deck-builder` task package in its "scope decision deck" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `manifest.json`.

#### discovery-notes.md

#### Larkspur Veterinary Group: discovery call, 9 Oct 2026

Attendees: Priya Venkataram (Operations Director, sponsor), Tomasz Okafor (IT Manager, technical veto), Dana Whitlock (Finance Lead). Provider side: two consultants.

##### Client statements (verbatim from transcript)

- Priya: "Reception re-types every booking from the phone log into the scheduling system, and we lose about forty minutes a day per clinic doing it."
- Priya: "We have nine clinics and each one runs its own calendar. I can't see a free surgeon across sites."
- Tomasz: "Our patient records system is fine. I do not want it touched this year."
- Dana: "Whatever we choose has to be signed off before the January budget lock, which is 15 January."
- Tomasz: "Reminder texts go out from a separate tool, and about one in ten bounces because the numbers are stale."

##### Provider observations (not stated by the client)

- Seller note: the clients probably want online booking eventually.
- Seller note: leadership seems frustrated with the current vendor.

##### Open questions

- How many staff users across the nine clinics? (Priya guessed "around 120", unconfirmed.)
- Who owns phone system admin access?

#### quote-export.txt

Quote Q-LVG-2208 (export, 2 Nov 2026). Fixed fees, USD.

Option A: Single calendar. Fee 41,500. Duration 8 weeks.
  In: one shared scheduling calendar for all nine clinics; migration of future appointments only; staff training for up to 40 users.
  Out: phone log integration; reminder text tool; past appointment history.
  Assumes: one data export from the legacy scheduler; client provides test users.

Option B: Single calendar with phone log capture. Fee 63,200. Duration 12 weeks.
  In: everything in A's calendar and migration; bookings captured from the phone log into the calendar without re-typing; training for up to 90 users.
  Out: reminder text tool; past appointment history.
  Assumes: phone system vendor grants API access; client names a phone system admin.

Option C: Single calendar, phone log capture, and reminders. Fee 84,900. Duration 16 weeks.
  In: calendar, phone log capture, and reminder texts sent from the calendar with contact numbers cleaned during migration; training for up to 120 users.
  Out: past appointment history; online booking.
  Assumes: phone system API access; client approves a one-time contact data clean-up.

Not quoted in any option: patient records system changes, online booking, payment processing.
Recommended by the delivery lead: Option B.
Phases (B): Mobilize 1 wk, Design 3 wks, Build 5 wks, Validate 2 wks, Cutover 1 wk.

## Output

I've written and hand-gated the manifest for the Larkspur deck, but the copy still needs your approval and I have not built a PPTX. The skill says not to render a client deck without a human approving the copy slide by slide.

I couldn't run `build_ddoc.js --check` or `prose_check.py` here. I applied the `--check` rules to the manifest by hand, so my counts are not tool output. Please re-run both before building.

#### What I pinned

- **Mode:** decision mode, because the quote has three options (A, B, C).
- **Recommended option:** B, the single calendar with phone log capture. The delivery lead recommends it in the quote export.
- **Audience:** Priya Venkataram (Operations Director, sponsor), Tomasz Okafor (IT Manager, technical veto) and Dana Whitlock (Finance Lead, budget).
- **Date:** 5 Nov 2026, the Thursday you named.
- **Deadline:** 15 January, the budget lock Dana gave. It anchors the decision slide.

#### Gate result (by hand)

- **Structure:** 0 failures, 0 warnings across 9 slides. All seven required decision-mode slides are present, in the reference order.
- **Options:** the three option blocks have identical sections. Their word-count spread is about 1.22x, under the 1.4x limit.
- **Figures:** all three fees tie to the quote (A $41,500, B $63,200, C $84,900), as do the durations and training numbers. Two derived figures also check out: $21,700 more for each step up, and 4 more weeks from B to C.
- **Heard slide:** all five items are `client_stated`, each with a named source. Two of your own observations are not on it: that they probably want online booking, and that leadership is frustrated with the vendor.
- **Banned characters:** 0 em dashes, 0 section symbols, 0 placeholders.

#### The copy awaiting approval

| # | Headline | Content |
| --- | --- | --- |
| 1 | Re-typing and separate calendars cost your clinics time every day | Five quotes from Priya, Tomasz and Dana, about re-typing, nine separate calendars, stale reminder numbers, the patient records system and the budget lock. |
| 2 | We recommend the single calendar with phone log capture | It ends the re-typing that costs each clinic about forty minutes a day and leaves patient records alone. Calendar alone leaves re-typing. Reminders add 4 weeks and $21,700 and need a contact data clean-up. Reminders can follow as a later phase. |
| 3 | Each option adds one capability, at a fixed fee | Table with fee, duration, in scope, staff trained, not in scope and assumptions for A, B and C. |
| 4 | Single calendar puts nine clinics on one schedule in eight weeks | A in detail: $41,500. Needs one legacy export and test users. |
| 5 | Phone log capture ends re-typing in twelve weeks | B in detail: $63,200. Needs phone system API access and a named phone system admin. |
| 6 | Reminders from the calendar reach cleaned numbers in sixteen weeks | C in detail: $84,900. Needs API access and approval of a one-time contact data clean-up. |
| 7 | Three things sit outside every option | Patient records system, past appointment history, online booking and payment processing. Each can be scoped as a separate paid phase. |
| 8 | Four things we need from you before you choose | Confirm the staff count (our ~120 is unconfirmed). Name the phone system admin owner. Say whether online booking is a priority (your hunch, now a question). Say whether a contact data clean-up is acceptable. |
| 9 | Choose an option before the 15 January budget lock | Choose an option and confirm its assumptions before 15 Jan. We send the proposal after that. Kickoff follows acceptance. |

Each option is described by what it contains, with no "everything in A plus" wording. Each exclusion routes to a paid next step.

#### Decisions for you

1. **Copy approval.** I need a reviewer to go through slides 1 to 9 one at a time. Until then, nothing is approved.
2. **Timeline slide.** I left it out. The quote has phase lengths for B (1/3/5/2/1 weeks) but no milestones, and a phase bar without milestones is a rejected pattern. If you give me gate names, I'll add it.
3. **"Can be scoped as a later phase."** This wording implies future work the quote doesn't price. Please confirm you are happy to say it.
4. **Proposal turnaround.** The decision slide says "after you choose" because you gave me no turnaround time. Give me one if you want it on the slide.
5. **Provider name and logo.** None was supplied, so the neutral brand profile applies with no logo.

#### Still to do before delivery

1. Run `node scripts/build_ddoc.js manifest.json --check` and `prose_check.py` with `house.json`. Report their counts.
2. After approval, build the PPTX, then rasterize every slide and check for overflow and figure drift. The option text on slides 5 and 6 is the most likely to overflow.
3. Complete the three release gates: writing-integrity, brand-renderer and quality-gate. None has been run, so the deck is not final.

#### Files

- `out/manifest.json`: the deck manifest, with the full copy, the quote snapshot, the figure mappings and speaker notes carrying evidence sources.
- `out/gate-report.md`: the hand-run preflight table, the figure tie-out, how the two non-client observations were handled, and the outstanding items.
- `out/answer.md`: this reply.

### File: gate-report.md

#### Gate report: Larkspur Veterinary Group, Q-LVG-2208

Method: `build_ddoc.js --check` and `prose_check.py` cannot be run here. Every rule in `preflight()` was applied by hand to `manifest.json`. These are hand counts, not tool output. Re-run both commands in a working environment before the build.

##### Phase 0 pins

| Item | Value | Basis |
| --- | --- | --- |
| Mode | Decision | Three quoted options (A, B, C) |
| Audience | Priya Venkataram (sponsor), Tomasz Okafor (technical veto), Dana Whitlock (budget) | Discovery notes |
| Source | Quote Q-LVG-2208, export of 2 Nov 2026 | `inputs/quote-export.txt` |
| Existing draft | None | Nothing supplied, so no extraction run |
| Recommended option | B | Delivery lead, per the quote export |

##### Phase 1: manifest preflight (by hand)

| Check | Result |
| --- | --- |
| Option count 2 to 3 | Pass (3) |
| Exactly one recommended | Pass (B) |
| Skeleton: heard, recommendation, comparison, option_block, outside_all, need_from_you, decision | Pass, all present |
| Order matches reference order | Pass, no warning |
| One option_block per option, unique names | Pass (3 of 3) |
| Identical section keys across blocks | Pass (In scope, Not in scope, Assumptions, Timeline) |
| Word-count parity, builder method (all authored strings in the block) | A about 74, B about 80, C about 90. Spread 1.22x, under 1.4x |
| Comparison rows: 6 rows, 3 cells each | Pass |
| Heard items all `client_stated` with source | Pass (5 of 5) |
| Figures map to `quote_snapshot` with equal values | Pass (41,500 / 63,200 / 84,900) |
| Em dash, section symbol, TBD, `[FLAG:` | 0 found |
| Title budget 78 chars | Longest 66. Pass |
| Subtitle budget 120 | One subtitle, about 116. Pass |
| Bullet budget 150, at most 7 bullets | Longest about 125. Max 3 per slide. Pass |
| Bullets end in terminal punctuation | Pass |
| Logo | Profile not resolved here. Neutral profile assumed, so no logo declared |

Hand count: 0 failures, 0 warnings, across 9 slides (10 with the cover).

##### Phase 2: figure tie-out

| Displayed figure | Quote value | Match |
| --- | --- | --- |
| $41,500, 8 weeks (A) | 41,500, 8 weeks | Yes |
| $63,200, 12 weeks (B) | 63,200, 12 weeks | Yes |
| $84,900, 16 weeks (C) | 84,900, 16 weeks | Yes |
| $21,700 more for reminders | 84,900 - 63,200 | Yes |
| 4 more weeks for reminders | 16 - 12 | Yes |
| Staff trained 40 / 90 / 120 | Quote training lines | Yes |
| "About forty minutes a day" | Priya, verbatim | Yes |

Prose gate: the scanner was not run. By-hand pass found 0 fragment bullets, 0 label headers, 0 colons on body lines, and no "Everything in A plus" constructions. Scanner counts are still required.

##### Evidence classes dropped from the slide

| Observation | Class | Handling |
| --- | --- | --- |
| Clients probably want online booking eventually | seller_asserted | Question on need_from_you |
| Leadership seems frustrated with the current vendor | seller_asserted | Dropped. No question follows from it |
| Around 120 staff | Unconfirmed estimate | Question on need_from_you, and shown as unconfirmed |

##### Outstanding before build

1. Copy approval (Phase 3) has not happened. No slide has been presented one at a time to a reviewer.
2. No timeline slide. The quote gives phases for option B (1/3/5/2/1 weeks) but no milestones, and the copy rules reject a phase bar without them. Supply gate names if you want it.
3. The "can be scoped as a later phase" wording implies future pricing the quote does not hold. Confirm you are comfortable making that statement.
4. The decision slide promises a proposal "after you choose" with no turnaround time, because none was supplied.
5. Run `--check` and `prose_check.py`, then the render, rasterize, and the three release gates.
