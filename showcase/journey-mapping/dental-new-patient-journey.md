---
skill: journey-mapping
title: New-patient journey and service blueprint for a dental group
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 044a9b62cc4632caf267af2a4a70a412e71a3889783548063ee340997d0cac63
---

## Request

Build a new-patient journey map and service blueprint for Brightwell Dental Partners from the research notes in ./inputs/, with the opportunities it shows. Make it something the ops director can review.

## Inputs

Run of the built `journey-mapping` task package. All inputs below are invented. The run had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### research-notes.md

#### Brightwell Dental Partners — new-patient journey research (fictional)

Sources: 6 front-desk staff interviews (2 offices), 8 new-patient phone interviews, call-log sample of 200 new-patient calls, and the current paper intake packet.

Findings:
- Patients find Brightwell through insurance directory (45% of interviewees) or Google Maps (40%).
- Booking is phone only. Call log: 31% of new-patient calls go to voicemail at lunch or after 5pm; 1 in 3 voicemails is never returned the same day.
- Front desk asks for insurance details on the phone; staff say 25% of patients don't have the card handy.
- Patients receive a 6-page paper packet at check-in. Interviewees: "I filled in my medications twice." Average 18 minutes to complete in the waiting room (front-desk estimate).
- Front desk re-keys the packet into DentaCore; staff report 10–15 minutes per new patient and frequent illegible handwriting.
- Insurance verification happens the morning of the appointment; 12% of new patients have a coverage problem discovered at check-in (staff estimate).
- After the first visit, the treatment plan and cost estimate is printed; 3 of 8 patients said they did not understand what insurance would pay.
- Patients who had a good front-desk interaction mentioned the person's name.

## Output

### Brightwell new-patient journey map: ready for the ops director's review

I built a Markdown journey map, service blueprint and opportunity map for a new patient who books by phone, from searching for a dentist to receiving the printed treatment plan and cost estimate. It is a current-state map, version 0.1. The full document is `out/brightwell-new-patient-journey-map.md`.

#### What the research shows

The losses sit before the patient reaches the chair:

- **Booking:** 31% of the 200 sampled new-patient calls go to voicemail at lunch or after 5pm, and 1 in 3 voicemails is not returned the same day.
- **Insurance:** staff say 25% of patients don't have the card handy on the phone. Verification runs the morning of the appointment, and staff estimate 12% of new patients have a coverage problem found at check-in.
- **Check-in:** patients fill in a 6-page paper packet in the waiting room (about 18 minutes, front-desk estimate), then staff re-key it into DentaCore (10–15 minutes, staff report). One patient said, "I filled in my medications twice."
- **After the visit:** 3 of 8 patients did not understand what insurance would pay.
- **Keep:** patients who had a good front-desk interaction remembered the person's name.

#### Journey phases

| Phase | Reported or observed | Feeling captured |
|---|---|---|
| P1 Find (directory 45%, Google Maps 40%) | Directory and Maps listings | Not captured |
| P2 Book (phone only, voicemail, insurance on the call) | Call log, staff | Not captured |
| P3 Before the visit (verification the morning of) | Staff | Not captured |
| P4 Check-in (paper packet, re-keying, coverage surprise) | Patient quote, staff | Repetition, not a named feeling |
| P5 First visit | Not captured | Not captured |
| P6 Plan and cost | Patient interviews | Confusion about insurance payment (3 of 8) |

The notes carry almost no feelings, so there is no emotional curve and no invented scores.

#### Blueprint finding

The notes don't say what patients can see of staff work. Voicemail callbacks, the morning verification, re-keying and estimate preparation therefore sit in a "visibility not captured" row and not in back-stage. No back-stage action is established from the evidence. Confirming where these fall is the first validation task.

#### Opportunities (effort and impact are labels; owners and outcomes are proposals)

| # | Opportunity | How it changes the step | Measure | Effort / impact |
|---|---|---|---|---|
| O1 | Named person per office clears voicemail at midday and close; same-business-day callback | Acts after the voicemail is left, so it recovers calls and does not reduce voicemails | Share of new-patient voicemails with an outbound call the same business day (voicemail timestamp to first outbound call), baselined from the call log | S / H |
| O2 | Verify insurance on the day of booking; ask patients to have the card ready; follow up with those who don't | Acts days before check-in, while the patient can still be reached | Share of new patients whose coverage problem is first found at check-in; count from records, since 12% is an estimate | M / H |
| O3a | Audit the packet and remove repeated questions | Changes content, not when it is filled in | Pages and fields before and after | S / M |
| O3b | Intake before the visit that writes into DentaCore | Moves completion off the waiting room and removes re-keying, if DentaCore can accept it (not captured) | Timed arrival-to-check-in minutes; staff minutes per new patient | L / H |
| O4 | Estimate shows insurance payment and patient balance separately, with a staff walk-through | Acts after the plan is printed, on understanding, not on cost | Patient can state what insurance pays and what they owe at handoff | M / M |
| O5 | Keep named, personal front-desk contact in any change | Protects a reported strength | None proposed | none |

Quick wins are O1 and O3a. O3b is the one strategic bet. I did not propose online booking: the notes record no patient demand for it.

#### Limits to know

- The 18 minutes, 10–15 minutes, 25% and 12% are staff estimates, not measurements.
- The discovery shares of 45% and 40% don't divide evenly into 8 interviews, and the notes don't give the base.
- The packet's contents were not supplied, so which pages repeat the medication question is unknown.
- The first visit, patient goals and most thoughts and feelings are not captured. The document lists seven validation questions with whom to ask.

#### Checks

Done by hand: claim-to-source reconciliation, feeling and quote parity, blueprint visibility classification and measure timing against each action. Not run: the bundled build and self-test scripts (no script execution here), the writing checker, quality gate and brand rendering. No HTML board was built. Evidence-core does not apply, because this is a standalone research map with no engagement ledger.

#### Files

- `out/brightwell-new-patient-journey-map.md`: full journey map, blueprint, opportunity map, source ledger and validation questions
- `out/answer.md`: this summary

### File: brightwell-new-patient-journey-map.md

#### Brightwell Dental Partners: new-patient journey map, service blueprint and opportunities

Version 0.1 · 2026-11-04 · Current state · For review by the operations director

##### Recommendation

Fix the front end of the journey first. The notes show three losses before the patient reaches the chair: voicemails that go unreturned (booking), insurance problems found only at check-in (before the visit and check-in), and a paper packet that patients complete in the waiting room and staff then re-key (check-in). The after-visit cost estimate is the fourth problem, and the one patients said they did not understand.

Proposed order, each a proposal to validate:

1. Set a same-day callback rule for voicemails, with lunch and after-5pm coverage. Small effort.
2. Move insurance verification from the morning of the visit to the day of booking, and ask for the card ahead of the call. Medium effort.
3. Audit the packet for repeated questions, then move intake before the visit. The audit is small. Pre-visit intake is a larger bet, because it depends on what DentaCore can accept, and the notes do not say.
4. Rework the cost estimate so it shows what insurance pays and what the patient owes. Medium effort, after finding out how estimates are built.

##### Scope

**Actor:** a new adult patient who books by phone at one of the Brightwell offices.
**Journey:** from searching for a dentist to receiving the printed treatment plan and cost estimate after the first visit.
**State:** current. Nothing here shows a changed process.
**Offices in the research:** 2 (not named in the notes).

##### Evidence basis

| Source | Size | Type | Used for |
|---|---|---|---|
| Front-desk staff interviews | 6 staff, 2 offices | Reported (staff) | Insurance, re-keying, coverage problems |
| New-patient phone interviews | 8 patients | Reported (patients) | Discovery channel, packet, estimate, front-desk moments |
| Call-log sample | 200 new-patient calls | Observed | Voicemail share and callback timing |
| Paper intake packet | 1 packet, 6 pages | Observed | Packet length. Its contents were not supplied. |

Three limits to know before reviewing:

- The 18-minute completion time, the 10–15 minutes of re-keying, the 25% without a card and the 12% coverage-problem rate are staff estimates. None is measured.
- Discovery shares of 45% and 40% do not divide evenly into 8 interviews. The notes do not say what the percentage is of; treat them as approximate until the base is confirmed.
- No emotion scores were supplied, so there is no emotional curve. Feelings appear only where the notes carry them. Goals are the evident purpose of each step, not something patients reported.

##### Phases

| ID | Phase | Starts | Ends |
|---|---|---|---|
| P1 | Find | Patient looks for a dentist | Patient has a number to call |
| P2 | Book | Patient calls | Appointment made and insurance details given (or not) |
| P3 | Before the visit | Appointment booked | Morning of the appointment |
| P4 | Check-in | Patient arrives | Packet completed and entered |
| P5 | First visit | Patient seen | Visit ends. Not captured in the research. |
| P6 | Plan and cost | Treatment plan printed | Patient understands what insurance will pay |

##### 1. Journey map (the patient's view)

| Phase / step | Touchpoint | Goal | Thoughts | Emotion | Pain points | Opportunity |
|---|---|---|---|---|---|---|
| P1.1 Search | Insurance directory (45% of interviewees) or Google Maps (40%) | Find an in-network, nearby dentist | Not captured | Not captured | None reported | Not an opportunity from this evidence. Why patients choose Brightwell from the list is not captured. |
| P2.1 Call to book | Phone to the office | Get an appointment | Not captured | Not captured | Booking is phone only. 31% of new-patient calls reach voicemail at lunch or after 5pm; 1 in 3 voicemails is not returned the same day. | O1 |
| P2.2 Give insurance details | Same phone call, front desk asks | Book without a hold-up | Not captured | Not captured | Staff say 25% of patients do not have the card handy. | O2 |
| P3.1 Wait for the visit | Not captured whether the patient hears anything | Not captured | Not captured | Not captured | Not captured | O2 |
| P4.1 Fill in the packet | 6-page paper packet in the waiting room | Get checked in | "I filled in my medications twice." (patient interview) | Repetition is the reported complaint. The feeling is not named. | About 18 minutes to complete (front-desk estimate). Medications asked twice. | O3 |
| P4.2 Coverage surfaces | Front desk at check-in | Be seen on time | Not captured | Not captured | 12% of new patients have a coverage problem found here (staff estimate). | O2 |
| P5.1 Visit | Chair side | Not captured | Not captured | Not captured | Not captured | None |
| P6.1 Receive plan and estimate | Printed treatment plan and cost estimate | Know what to pay | Not captured | Confusion about insurance payment: 3 of 8 patients did not understand what insurance would pay. | Same 3 of 8. | O4 |

Positive moment to keep: patients who had a good front-desk interaction mentioned the person's name. The notes do not say at which step. Treat it as a strength at P2 to P4 until validated, and keep named, personal contact when changing those steps.

##### 2. Service blueprint

The notes establish what the patient does and what staff do on the patient's behalf, but they do not say what the patient can see of the internal work. Most internal actions therefore sit in the visibility-not-captured row, not in back-stage.

| Phase | Front-stage (in the patient's view) | Back-stage (established out of view) | Visibility not captured | Supporting systems |
|---|---|---|---|---|
| P1 | Patient reads the directory or Google Maps listing | None established | Who maintains the listings | Insurance directory, Google Maps (owner not captured) |
| P2 | Patient calls. Front desk asks for insurance details. Voicemail greeting when no one answers. | None established | Voicemail review and callbacks, including who owns them and when | Phone and voicemail system (name not captured); call log |
| P3 | Not captured | None established | Insurance verification on the morning of the appointment (staff-reported timing) | Payer verification route (not captured); DentaCore |
| P4 | Patient completes the 6-page paper packet. Front desk handles check-in. | None established | Re-keying the packet into DentaCore (10–15 minutes per patient, staff report). Handwriting that staff cannot read. | Paper packet, DentaCore |
| P5 | Not captured | Not captured | Not captured | Not captured |
| P6 | Patient receives the printed plan and estimate | None established | How the estimate is built, and from which benefit data | DentaCore (assumed source, not stated) |

**Line of visibility.** Lies between the front-stage column and the other two. Placement of the verification, re-keying and callback work across it is the open question for validation.
**Line of internal interaction.** Between staff work and supporting systems. Only DentaCore is named, and only as the place the packet is re-keyed.

**Symptom and cause pairs the evidence supports:**

| Patient symptom | Cause the notes support | Cause not yet known |
|---|---|---|
| No callback after a voicemail | 31% of calls hit voicemail at lunch or after 5pm | Why 1 in 3 is not returned same day (ownership, workload, no queue) |
| Coverage problem at check-in | Verification runs the morning of the appointment | Whether details taken by phone are complete. 25% lack the card. |
| Medications asked twice | Paper packet design | Which pages repeat the question. Packet contents were not supplied. |
| Does not understand what insurance pays | Estimate printed after the visit | How the estimate is built and explained |

##### 3. Opportunity map

Effort and impact are labels, not prices. Owners and outcomes are proposals. "Reported severity" is how often or how plainly the notes raise it; the order is my prioritization.

| # | Friction (phase) | Evidence | Recommended action and when it acts | Expected outcome | Measure | Effort / impact | Proposed owner |
|---|---|---|---|---|---|---|---|
| O1 | Unreturned voicemails (P2.1) | Call log, 200 calls: 31% to voicemail; 1 in 3 not returned same day | Name a person per office to clear voicemail at midday and at close, and return calls the same business day. Acts after the voicemail is left, so it cannot reduce the number of calls that reach voicemail. | More booking calls recovered | Share of new-patient voicemails with an outbound call the same business day. Start: voicemail timestamp. End: first outbound call. Baseline from the same call-log extract, since the source did not define these events. | S / H | Front-desk lead (proposed) |
| O2 | Coverage found at check-in (P2.2, P3.1, P4.2) | Staff estimate 12% of new patients; 25% without the card on the phone | Verify insurance on the day of booking, not the morning of the visit. Ask the patient to have the card ready when they book, with a follow-up for those who do not. Acts days before check-in, so the patient can be contacted while there is time to resolve it. | Fewer surprises at the desk | Share of new patients with a coverage problem first found at check-in. Baseline is the 12% staff estimate, so count from records first. | M / H | Operations with the insurance coordinator (proposed) |
| O3a | Repeated questions (P4.1) | Quote: medications filled in twice | Audit the 6-page packet and remove duplicated questions. This changes the packet's content, not when it is completed. | Shorter packet | Pages and fields before and after; patient-reported time on a short follow-up | S / M | Operations (proposed) |
| O3b | Waiting-room completion and re-keying (P4.1, P4.2) | 18 minutes in the waiting room; 10–15 minutes re-keying per patient; illegible handwriting (all staff estimates) | Offer intake before the visit that writes to DentaCore, or at minimum a typed form that staff can import. Acts before arrival, so it can cut waiting-room time and re-keying. Whether DentaCore can accept it is not captured. | Less time at the desk and fewer transcription errors | Minutes from arrival to completed check-in (timed, not estimated); staff minutes per new patient | L / H | Operations with IT (proposed) |
| O4 | Estimate not understood (P6.1) | 3 of 8 patients did not understand what insurance would pay | Show insurance payment and patient balance as separate lines, and have staff walk through it at handoff. Acts after the plan is printed, so it addresses understanding and not the cost itself. First learn how the estimate is built. | Patients can say what they will owe | Short check at handoff: can the patient state what insurance pays and what they owe | M / M | Practice manager with billing (proposed) |
| O5 | Keep: named front-desk contact (P2–P4) | Patients named the staff member after a good interaction | Preserve personal contact in any change, such as a named callback or named check-in contact | Keeps a reported strength | Not proposed as a change | none | Front-desk lead |

**Quick wins:** O1 and O3a. Both are rule or content changes with no system build.
**Strategic bet:** O3b. It depends on DentaCore and on the answer to how patients prefer to complete intake, which the notes do not cover.
**Cross-team:** O2 involves front desk, insurance and billing; its timing depends on how verification is run today (not captured).
**Not proposed:** online booking. The notes show booking is phone only but record no patient demand for online booking. Ask first.

##### Source and confidence ledger

| Claim | Phase | Source | Confidence |
|---|---|---|---|
| Directory 45%, Google Maps 40% | P1 | Patient interviews (8); base unclear | Medium |
| Booking is phone only | P2 | Research notes | High |
| 31% of new-patient calls go to voicemail at lunch or after 5pm | P2 | Call-log sample, 200 calls | High (sample) |
| 1 in 3 voicemails not returned same day | P2 | Call-log sample | High (sample) |
| 25% without insurance card at hand | P2.2 | Staff interviews | Medium (estimate) |
| 6-page packet; medications entered twice | P4.1 | Packet; patient quote | High (packet), Low (one quote) |
| 18 minutes to complete | P4.1 | Front-desk estimate | Medium |
| Re-keying 10–15 minutes; illegible handwriting | P4 | Staff interviews | Medium |
| Verification on the morning of the appointment | P3 | Staff interviews | Medium |
| 12% coverage problems at check-in | P4.2 | Staff estimate | Medium |
| 3 of 8 did not understand insurance payment | P6.1 | Patient interviews | Medium (small sample) |
| Named front-desk person remembered | P2–P4 | Patient interviews | Low (step unknown) |
| Emotion scores, goals, thoughts other than one quote | all | Not captured | Not captured |

##### Validation questions

| What to settle | Ask whom | Confirms or overturns |
|---|---|---|
| Whether the 12% and the 25% hold in records | Front-desk lead; pull a month of new-patient records | O2 size |
| Who clears voicemail now, and what stops same-day callbacks | Front-desk staff at both offices | O1 cause |
| Which packet pages repeat questions | Review the packet with 3 recent new patients | O3a |
| Whether DentaCore accepts electronic intake | DentaCore administrator | O3b feasibility |
| How the estimate is built and what patients are told | Billing and treatment coordinators | O4 cause |
| Whether the patient hears anything between booking and arrival | Patients; front-desk staff | Blueprint P3 |
| Why patients pick Brightwell from a listing, and what they feel at each step | A second round of patient interviews, with feelings asked at each step | Empty emotion cells |

##### Checks run and not run

- Done by hand: reconciliation of every claim to the notes, parity of feelings and quotes with the journey, blueprint visibility classification, measure timing against each action.
- Not run: the bundled map-builder and self-test scripts (no script execution in this session), the writing checker, the quality gate and brand rendering. No HTML board was built; this is the Markdown version with all three views inline. Evidence-core does not apply: this is a standalone research map with no engagement ledger.
