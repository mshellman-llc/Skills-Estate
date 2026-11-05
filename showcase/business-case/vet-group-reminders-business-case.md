---
skill: business-case
title: Business case for appointment reminders and online booking across six clinics
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 044b11756dbf2e052006fb336c4a0b800d001cdea716fadc9220bb5c060ab74d
---

## Request

Ines Okafor, our finance director, takes the appointment reminder and online booking project to the finance committee on 2026-11-18. Can you write the business case for her using the quote and my discovery notes? She has said she will push on price, so I want the honest version.

## Inputs

Run of the built `business-case` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `fix.txt`, `ledger.json`.

#### discovery-notes.md

#### Discovery notes, Calder Valley Veterinary Group (as of 2026-11-02)

Sources: call with Dev Marchetti (practice operations manager) 2026-10-20; email
from Ines Okafor (finance director) 2026-10-29; finance committee calendar.

##### What the clinics told us
- Six clinics, about 6,400 appointments a month across the group (Dev, 2026-10-20).
- Two agency part-timers make reminder calls all day. Agency cost is $2,600 a
  month. They do nothing else (Dev; Ines confirmed the cost, 2026-10-29).
- The agency agreement auto-renews on 2027-02-28 for 12 months. Notice of
  non-renewal must be written and received by 2027-02-14 (Ines, 2026-10-29).
- No-show rate is 13% at Main Street. Main Street ran SMS reminders by hand-built
  script for 8 weeks in spring 2026 and no-shows fell to 9% (Dev; his own tally,
  no other clinic tested).
- Average appointment is worth $95 in billed revenue (Ines, 2026-10-29).
- Clients cannot book online. Calls go unanswered at peak, and Dev says voicemail
  booking requests are the main complaint in client feedback (no count kept).

##### Pushback already heard
- Ines: "ClinicBook sells a reminder add-on at $240 per clinic per month. Why
  not that?" Dev: the add-on does reminders only, no online booking, and ClinicBook
  is installed at four of the six clinics.
- Ines: the agency saving only counts as cash if we actually end the contract.
- Dr Hannah Voss (clinical lead): worried the pilot gain was Main Street's
  engaged front desk, not the SMS.

##### Calendar
- Finance committee meets 2026-11-18, then next on 2027-02-17.
- Quote Q-CVV-0417 expires 2026-12-15.

#### quote-Q-CVV-0417.md

#### Quote Q-CVV-0417 (issued 2026-10-27, valid to 2026-12-15)

Client: Calder Valley Veterinary Group, six clinics.
Scope: automated SMS and email appointment reminders, online booking, and a
two-way confirm/cancel flow, connected to the practice management system (PMS)
"ClinicBook" at four clinics. Fixed fee. Ten weeks from signed approval to go-live.

Priced:
- Fixed fee for build, configuration, staff training and 12 months of licence: $54,000
- Licence from month 13: $890 per month

Not priced in this quote:
- SMS carrier charges (volume-based; vendor estimate requested, not received)
- Connecting the two clinics on the older "VetDesk 6" system (Pike Street and
  Alder Lane). VetDesk 6 has no API. Options are a nightly file export or
  migrating those clinics to ClinicBook. Neither is scoped.
- Clinic staff time for training, about two hours per person (not charged)

## Output

### Business case for Ines Okafor: reminders and online booking

The business case is drafted for the 2026-11-18 finance committee. It recommends approving quote Q-CVV-0417, a $54,000 fixed fee that includes 12 months of licence, with three conditions closed before the first payment. The numbers in it come only from your quote and your discovery notes.

#### What carries the case

1. **The agency notice date.** The agency agreement for the two reminder-call staff costs $2,600 a month. It auto-renews on 2027-02-28 for 12 months, and written notice must be received by 2027-02-14. The next committee is 2027-02-17, three days late. Approving on 2026-11-18 gives a go-live on 2027-01-27, 18 days before the deadline.
2. **The cost of missing it.** Waiting locks in $2,600 x 12 = $31,200. Even if the renewal is not counted, the three months between the two possible go-live dates cost $2,600 x 3 = $7,800. The two figures overlap and are not added.
3. **The case against, conceded.** The ClinicBook reminder add-on costs 4 x $240 = $960 a month for the four clinics it covers. That is $34,560 over three years, against $75,360 for this project ($54,000 plus 24 months at $890). The add-on is $40,800 cheaper, and more once unpriced items are added to ours. The case holds only because the add-on has no online booking, does not reach Pike Street and Alder Lane, and does not change the agency date.

#### Landmines

- **The agency saving is cash only if notice is given.** Ines said this herself. The case makes notice an owned decision, to be taken only after two weeks of clean running (check on 2027-02-10).
- **Two items are not in the $54,000.** SMS carrier charges have no estimate yet. The two VetDesk 6 clinics have no connection route and no price, because that system has no API. Both appear as named gaps in section 08, not in the headline.
- **The no-show upside rests on one clinic.** Main Street went from 13% to 9% on Dev's own tally. The 4-point extrapolation is $24,320 a month of billed revenue, and I labeled it an inference and did not use it. The case uses a one-point gain, 64 x $95 = $6,080 a month, which is revenue and not margin.
- **The quote expires 2026-12-15.**

#### The judgment call

I led with the date and not with the no-show benefit. The argument for the other order: committees respond to revenue upside, and a $6,080 or $24,320 monthly figure is more vivid than a contract clause. I chose the date because it is the only figure that comes entirely from sourced inputs, and because Ines has said she will push on price. The risk is that it makes the project look like a way to avoid a cost and not a way to create value. If she thinks so, section 04 could reorder, but the inference would then need to be presented first with its low confidence stated.

A second call: I conceded the add-on comparison in full and did not reframe the cost. Argued the other way, the add-on does not remove the agency staff, so its true cost includes the continued $2,600 a month. That reasoning is fair but it depends on whether the add-on alone could justify ending the agency contract. Dev should confirm that before Ines uses the argument.

#### What I could not do

- **Evidence gate.** I did not run `evidence_core.py` because I cannot execute scripts here. I built the ledger by hand (`out/ledger.json`) and applied the documented rules. Result: 8 required domains, none Insufficient. Benefits and approval conditions are Conditional, because the value figure is an inference and two costs are unpriced. The full case proceeds with those gaps shown.
- **Structure gate.** I did not run `case_gate.py`. I applied its rules by hand and by search (log in `out/fix.txt`). The first pass found four figure lines without a source token; I fixed them. After the fixes, every figure line has a token, all 11 shown products recompute, there are no em dashes, and the five load-bearing sections each have content.
- **Prose check and brand render.** The prose checker and brand renderer did not run. I read the text once for filler and repeated constructions. The file is a Markdown draft and has not been rendered. The for/against split, the timeline and the decision tracker would come from the renderer.
- **Depth tests.** All ten pass on reading. Every benefit traces to a pain in the notes. Every risk has a severity and an action. The clone test passes because the dates, the add-on rebuttal and the VetDesk 6 gap come from these two input files and could not belong to another client.
- **Not delivered.** This is a draft for Ines. It has not been sent, committed, or put into any client folder.

#### Open items before the meeting

| Item | Owner | Due |
| --- | --- | --- |
| SMS carrier estimate | Quote author | 2026-11-13 |
| VetDesk 6 route (export or migrate) | Dev Marchetti | 2026-12-04 |
| Three months of no-show data, all clinics | Dev Marchetti | 2026-12-18 |
| Agency notice decision | Ines Okafor | 2027-02-10 |

#### Files

- `out/case.md`: the business case, sections 01 to 08 plus an assumptions register and a source stamp.
- `out/ledger.json`: the hand-built evidence ledger, 15 claims, snapshot 2026-11-02.
- `out/fix.txt`: the manual gate log.

Key content of `out/case.md`:

- **Recommendation:** approve Q-CVV-0417 on 2026-11-18, $54,000 fixed fee including 12 months licence, $890 a month from month 13.
- **Why now:** notice deadline 2027-02-14, next committee 2027-02-17, renewal lock $31,200.
- **Benefits:** reminder calls replaced (cash only if notice is given), fewer no-shows (one-point case $6,080 a month, labeled inference), online booking (qualitative, no count exists).
- **Case against:** ClinicBook add-on (conceded, $40,800 cheaper over three years), agency saving not real without notice (conceded), pilot gain may be the front desk (partly conceded), do nothing (answered).
- **Risks:** five, with severity from high to low and an action each.
- **Ask:** approve the quote; unpriced SMS charges and VetDesk 6 connection named as gaps; three owned open decisions with dates.

### File: case.md

#### Calder Valley Veterinary Group: appointment reminders and online booking

Prepared for the finance committee, 2026-11-18. Presenter: Ines Okafor, finance director.

##### 01 Executive frame

*Bar: a reader of this section alone knows what is being funded, why it beats the alternatives including doing nothing, and what the strongest objection is.*

**Recommendation.** Approve the fixed-fee build under quote Q-CVV-0417 at the 2026-11-18 meeting, with three conditions closed before the first payment (section 08).

The fee is $54,000 and includes 12 months of licence [quote: Q-CVV-0417].

**Why it wins.** The deciding factor is a date. The agency agreement that pays two people to phone clients renews on 2027-02-28 and can only be ended by written notice received by 2027-02-14 [src: Ines Okafor email, 2026-10-29]. The next committee after this one meets on 2027-02-17, three days too late. Approving now gives a go-live on 2027-01-27, 18 days before the notice deadline. Approving in February locks in the next 12 months of agency cost.

That lock is $2,600 x 12 = $31,200 [computed: inputs C6, C4].

**Strongest argument for.** Main Street clinic cut no-shows from 13% to 9% in 8 weeks using SMS reminders alone [src: Dev Marchetti call, 2026-10-20]. Clients also get a way to book that does not depend on someone answering the phone.

**Strongest argument against.** The practice management system vendor sells a reminder add-on at $240 per clinic per month [src: Ines Okafor email, 2026-10-29]. For the four clinics it supports, that costs less over three years than this project. We concede that in section 05. The case holds because the add-on has no online booking, does not reach two of the six clinics, and does not by itself change the agency contract date.

**What is not settled.** The 4-point no-show gain is one clinic's own tally, so the revenue upside is a labeled inference and is not used in the headline. Two cost items are not priced yet (section 08).

##### 02 The client and the gap

*Bar: an approver new to the account understands the business problem in two minutes.*

Calder Valley runs six veterinary clinics handling about 6,400 appointments a month [src: Dev Marchetti call, 2026-10-20].

Reminders are phone calls. Two agency part-timers do nothing else, and they cost $2,600 a month [src: Dev Marchetti call 2026-10-20, confirmed by Ines Okafor email 2026-10-29].

Clients cannot book online. Calls go unanswered at peak hours, and voicemail booking requests are the main complaint in client feedback. No complaint count is kept, so that is Dev's judgment and not a measured figure.

##### 03 Why this moment

*Bar: the urgency rests on dated events from the client's own calendar.*

- 2026-11-18: finance committee meeting.
- 2026-12-15: quote Q-CVV-0417 expires.
- 2027-01-27: go-live if approved on 2026-11-18 (10 weeks from approval).
- 2027-02-14: last day for written notice ending the agency agreement.
- 2027-02-17: next finance committee meeting.
- 2027-02-28: agency agreement auto-renews for 12 months.
- 2027-04-28: go-live if approved on 2027-02-17.

A February approval therefore goes live two months after the renewal has already locked.

##### 04 Economics

*Bar: each benefit closes a pain the client named; the cost of waiting is printed arithmetic tied to the dated events above.*

**Benefit 1: reminder calls replaced by automatic SMS and email.** Closes the pain of two people phoning clients all day.

The agency line is $2,600 a month [src: Ines Okafor email, 2026-10-29].

This is cash only if the agreement is ended, which is a condition in section 08.

**Benefit 2: fewer missed appointments.** Closes the pain of empty slots. Main Street's no-show rate fell from 13% to 9% [src: Dev Marchetti call, 2026-10-20].

That is one clinic, eight weeks, and Dev's own tally. The group-wide no-show rate is not measured [gap: 3 months of PMS no-show data, owner Dev Marchetti].

Each appointment is worth $95 in billed revenue [src: Ines Okafor email, 2026-10-29].

Applying the full 4-point gain to every clinic gives an illustrative upside:

- 6,400 x 0.04 = 256 appointments recovered per month [computed: inputs C3, C9]
- 256 x $95 = $24,320 per month of billed revenue [inferred: I1, low, extrapolates one clinic's pilot to six]

Dr Voss doubts the gain came from SMS. A one-point gain tests that doubt:

- 6,400 x 0.01 = 64 appointments recovered per month [computed: inputs C3, I1]
- 64 x $95 = $6,080 per month of billed revenue [inferred: I1, low, one-quarter of the pilot gain]

This is revenue, not margin, and a recovered slot only counts if it is not left empty. The first figure, $24,320, is not safe to quote as a forecast [inferred: I1, low, see assumptions register]. The second, $6,080, is the one to use in the room, labeled as an inference [inferred: I1, low, see assumptions register].

**Benefit 3: clients can book online.** Closes the pain of unanswered calls and voicemail booking requests. The benefit is stated qualitatively because no complaint or lost-booking count exists [gap: booking complaint count, owner Dev Marchetti].

**Cost of waiting.** Two computations, both from the agency agreement. They overlap, so they are not added together.

Computation 1, the renewal lock if approval waits for 2027-02-17 (notice deadline 2027-02-14):

- $2,600 x 12 = $31,200 committed for months the project would have covered [computed: inputs C6, C4]

Computation 2, the minimum cost of the three-month gap between the two go-live dates (2027-01-27 and 2027-04-28):

- $2,600 x 3 = $7,800 of agency cost paid after the system could have replaced it [computed: inputs C6, C5]

The no-show upside forgone in that gap would be $6,080 x 3 = $18,240 at the one-point case [computed: inputs I1, C3].

**Investment for comparison.** $54,000 fixed fee [quote: Q-CVV-0417]. At the one-point case, $6,080 a month over 12 months is $6,080 x 12 = $72,960 of billed revenue [computed: inputs I1]. That is a revenue figure on an inference, so it supports the case without carrying it.

##### 05 The case against

*Bar: the cheapest alternative first, each objection at full strength, each answered with evidence or conceded.*

**1. "Buy the ClinicBook add-on instead."** Ines raised this before the meeting. The add-on is $240 per clinic per month and the vendor already supplies the PMS [src: Ines Okafor email, 2026-10-29].

It covers four clinics, because ClinicBook is installed at four of six [src: Dev Marchetti call, 2026-10-20].

- 4 x $240 = $960 per month [computed: inputs C11]
- $960 x 36 = $34,560 over three years [computed: inputs C11]

Our option over the same three years is a fee of $54,000 for year one plus 24 months of licence from month 13 [quote: Q-CVV-0417]:

- $890 x 24 = $21,360 [computed: inputs C10]
- $54,000 + $21,360 = $75,360 over three years, before SMS charges and the VetDesk 6 connection, which are unpriced [quote: Q-CVV-0417]

The add-on is cheaper by $75,360 - $34,560 = $40,800 over three years, and it is cheaper by more once unpriced items are added to ours [computed: inputs C10, C11].

We concede this. The case for the project does not rest on being cheaper than the add-on. It rests on three things the add-on does not do: online booking, reminders at Pike Street and Alder Lane, and a go-live early enough to give notice on the agency agreement. If the committee does not value online booking, the add-on is the better purchase for four clinics, and the agency agreement question stays open.

**2. "The agency saving is not real unless we end the contract."** Ines made this point directly [src: Ines Okafor email, 2026-10-29]. Conceded. The $2,600 a month only becomes savings if written notice is given by 2027-02-14 [src: Ines Okafor email, 2026-10-29]. Section 08 makes that a named decision with an owner, and the notice should follow two weeks of stable running (section 06).

**3. "The Main Street result was the front desk, not the SMS."** Dr Hannah Voss raised this [src: Dr Voss, relayed in Ines Okafor email, 2026-10-29]. Partly conceded. We have one clinic, one tally, no control. The answer is in the economics: the case uses a one-point gain, one quarter of the pilot, and is built to hold on the agency date and online booking if the no-show gain turns out to be small.

**4. "Do nothing."** Cheapest in cash this quarter. It leaves two people phoning clients, no online booking, and the agency agreement renewing for 12 months at $2,600 a month, which is $31,200 [computed: inputs C6, C4].

##### 06 Risk

*Bar: each risk comes from friction in the sources, carries a severity, and has a mitigation that is an action.*

1. **VetDesk 6 clinics cannot be connected (Pike Street, Alder Lane).** Severity: high. Source: quote exclusions. Mitigation: Dev Marchetti chooses between a nightly file export and migrating the two clinics to ClinicBook by 2026-12-04, and the vendor prices the choice before the first payment. If neither is chosen, go-live is limited to four clinics and the committee is told so.
2. **Agency staff are needed until the system is proven, so notice on 2027-02-14 may come too early.** Severity: medium. Source: renewal date and go-live date. Mitigation: go-live 2027-01-27 leaves 18 days. Set a check on 2027-02-10; give notice only if reminders have run cleanly for two weeks, otherwise the committee takes the 12-month lock knowingly.

[trimmed: the rest of this file, about 544 more words, is not shown]
