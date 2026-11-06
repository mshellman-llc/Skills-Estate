---
skill: review-writing
title: Condensing a two-option proposal into a decision email
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: d803e6989ebbf6222af21a788033f43c48fba6f5d425a5d51312defa8de22fcc
---

## Request

Can you turn my draft proposal into a short email to Priya Anand, the finance director at Kestrel Valley Council? She needs to pick an option by 20 November, and my draft reads like a brochure. Keep the prices and conditions accurate.

## Inputs

Run of the built `review-writing` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### draft-proposal.md

#### Invoice Intake Automation: Proposal for Kestrel Valley Council

We are thrilled to present a transformative, game-changing solution that will revolutionise how Kestrel Valley Council handles supplier invoices. Our robust, seamless platform leverages cutting-edge OCR to empower your accounts payable team.

##### Option A: Core Intake

Core Intake reads PDF and emailed invoices, matches them to purchase orders in the council's ledger, and routes mismatches to a review queue. It is not just a scanner, it is a complete intake pipeline.

- Fixed price: £18,400 excluding VAT
- Estimate: 120 consultant hours over 6 weeks
- Assumes the ledger exports purchase orders as CSV nightly (the council's IT team confirmed this on 14 October)
- Excludes paper invoice scanning and staff training

##### Option B: Core Intake plus Approvals

Everything in Option A, plus a workflow that sends matched invoices to budget holders for approval and posts approved invoices back to the ledger.

- Fixed price: £27,900 excluding VAT
- Estimate: 190 consultant hours over 9 weeks
- Assumes the ledger offers a write API. This is not yet confirmed. If it does not, posting stays manual and we would reprice the posting step.
- Excludes paper invoice scanning and staff training

##### Optional add-on

Staff training, two half-day sessions: £2,100 excluding VAT, available with either option.

##### Timing

Work can start on 11 January 2027 if we have a decision by 20 November 2026. Our rates are held until that date.

#### notes.txt

Notes from me (Dan Okafor, Fernlight Consulting):
- Priya met us once, on 2 October. She is not technical.
- Her IT lead, Marcus Webb, is checking the ledger write API; he said he'd know by the end of next week.
- Neither option has been approved. Council procurement needs a signed purchase order before we start.
- I recommend B if the API exists, otherwise A.
- Keep it friendly but short. Reply goes to priya.anand@example.com.

## Output

I've rewritten the proposal as an email to Priya. It asks her to pick Option A or B by 20 November and keeps every price, estimate, assumption and exclusion from your draft. It's ready to paste, and I haven't sent it.

**To:** priya.anand@example.com
**Subject:** Invoice intake: please choose Option A or B by 20 November

Hello Priya,

Could you choose between two options for automating invoice intake by 20 November? Our rates are held until then, and that date lets us start on 11 January 2027. I recommend Option B if the council's ledger can accept postings from outside, and Option A if it can't.

**Option A, Core Intake: £18,400 excluding VAT, fixed price.**
The system reads PDF and emailed invoices, matches them to purchase orders in your ledger, and sends mismatches to a review queue. We estimate 120 consultant hours over 6 weeks. It relies on the ledger exporting purchase orders as a nightly CSV file, which Marcus Webb's team confirmed on 14 October.

**Option B, Core Intake plus Approvals: £27,900 excluding VAT, fixed price.**
This adds a step that sends matched invoices to budget holders for approval and posts approved ones back to the ledger. We estimate 190 consultant hours over 9 weeks. It depends on the ledger having a write API, which isn't confirmed yet. Marcus is checking and told me he'd know by the end of next week. If the API doesn't exist, posting stays manual and we would reprice that step.

Neither option includes scanning paper invoices or staff training. Training is a separate add-on at £2,100 excluding VAT for two half-day sessions, and you can add it to either option.

Nothing is approved yet. Council procurement will need to issue a signed purchase order before we begin.

If it helps, I can talk through the options with you and Marcus before the 20th.

Best wishes,
Dan Okafor
Fernlight Consulting

---

**What I changed**

- Cut the opening paragraph and the "not just a scanner" line. They claimed benefits without a fact behind them. The email now opens with the decision and the date, since that's what Priya has to act on.
- Described the options in plain terms because Priya isn't technical. "OCR", "pipeline" and "write API" became what each does for her team, and the write API is explained as the ledger accepting postings.
- Put your recommendation in the first paragraph, using your condition: B if the API exists, A if not.
- Kept the approval state and the procurement requirement, so "proposed" doesn't read as agreed.

**Things to check before sending**

- **Marcus's timing.** I kept "by the end of next week" from your notes. If that was said some time ago, swap in a calendar date. If it falls after 20 November, say so, because Priya may need to decide before the API question is settled.
- **Hours.** I labelled the hours as estimates beside fixed prices, as in your draft. Delete them if you'd rather not show them to a finance reader.
- **Totals with training**, in case she asks: Option A plus training is £20,500 and Option B plus training is £30,000, both excluding VAT. I left these out of the email.
- **Closing offer.** The last line before the sign-off offers a call. I kept it because Marcus's answer may change the choice. Cut it if you don't want to offer.

**How I checked it**

I used the skill's core rules with no saved profile, because no profile store was set, so nothing was loaded or saved. I couldn't run the bundled prose checker, so I did the check by hand. I compared each figure, date and condition in the email against the draft and your notes, then read the email for stock phrases, staged contrasts and unsupported importance claims. A hand read doesn't amount to a scanner pass.

**Files:** none saved other than this answer. The email text above is the full deliverable.
