---
skill: write-portfolio-case-study
title: Portfolio case study for a three-way invoice matching tool
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: e78a68ff01fee091589db827b094754fe95b5f7ca303e7779a81a94da3bcd750
---

## Request

Can you turn my Harbourline invoice-matching project into a portfolio case study for my site? My notes, the figures ledger and the client's permission email are attached. I want a working copy and a publish copy.

## Inputs

Run of the built `write-portfolio-case-study` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### figures-ledger-and-permission.md

#### Figures ledger

| Figure | Source | Status |
|---|---|---|
| ~4,000 invoices/month | Harbourline AP volume report, May 2026 | checked against report |
| Auto-approve rate 71.4% | Pilot run log, June batch (3,962 invoices, 2,829 auto-approved) | computed from log |
| 11 duplicates caught, Jun–Jul | Hold-queue export | in export |
| Matching time 3 days → under 1 day at close | Dana's verbal comment, not measured | reported |
| "Pays for itself in a quarter" | Verbal, tone unclear | not usable |
| Estimated annual duplicate-payment exposure avoided: 38,000 | My model: 11 caught x avg invoice 3,450, extrapolated over 12 months | modeled |

#### Permission email (from Dana Okoye, 14 Oct 2026, dana.okoye@example.com)

"Happy for you to write up the matching tool as a case study. Please don't use our name or logo, and please keep supplier names, our invoice volumes by supplier and your fees out of it. Describing us as a regional food distributor is fine. You own the code you wrote; just keep our data out of any demo."

#### project-notes.md

#### Harbourline Foods – invoice matching (my notes)

Client: Harbourline Foods, regional food distributor, about 220 staff. Accounts payable team of 6 handled roughly 4,000 supplier invoices a month. Contact was Dana Okoye, finance controller.

Problem: AP clerks matched each supplier invoice against the purchase order and the goods-received note by hand in spreadsheets. Mismatches (price, quantity, missing receipt) surfaced late, often after the payment run was scheduled, and caused duplicate-payment risk and supplier disputes.

What I did (Mar–Jun 2026, solo, 14 weeks, billed at my day rate of 640 per day): built a three-way matching tool in Python and SQLite. It reads the ERP export of POs, the receiving log CSV and the invoice batch. Rules: exact PO number match first, then fuzzy match on supplier + amount + date window of 10 days when the PO number is missing or mistyped. Price tolerance of 2% or 15 currency units, whichever is lower. Each invoice lands in one of three queues: auto-approve, review (with the reason code), hold (no receipt or duplicate suspected). Duplicate check hashes supplier ID + invoice number + amount. Clerks work only the review and hold queues through a simple web page I wrote with Flask. Two AP clerks helped me write the reason codes; Dana signed off on tolerances.

Results as I remember: clerks used to spend about 3 days per month-end close on matching, now under 1 day. Auto-approve rate about 70% in the pilot. Caught 11 duplicate invoices in the first two months. Dana said it paid for itself in a quarter, I think? Might have been a joke.

The tool is running in production for the monthly batch since June. The email-alert feature for holds is built but they haven't switched it on yet.

Reusable: I have since turned the matching rules into a generic template I can reuse (own code, no Harbourline data).

## Output

I've written the case study with a working copy and a publish copy. It isn't ready to post yet. It needs your OK on two items below, and I couldn't run the voice check.

**File:** `./out/invoice-matching-case-study.md`. It holds the metadata block, the working copy with evidence labels, the publish copy, and a short checks record.

#### What the publish copy says
- **Client:** a regional food distributor with roughly 200 staff. There is no name, logo or contact. The permission email allowed "regional food distributor" and nothing identifying.
- **Problem:** six AP clerks matched about 4,000 invoices a month by hand in spreadsheets. Mismatches surfaced after the payment run was scheduled.
- **How it works:**
  - The tool is built in Python, SQLite and Flask.
  - It does an exact PO match first. If that fails, it does a fuzzy match on supplier, amount and a 10-day window.
  - The price tolerance is 2% or 15 currency units, whichever is lower.
  - Invoices land in an auto-approve, review or hold queue. Duplicates are caught by hashing supplier ID, invoice number and amount.
  - A hold alert by email is built into the tool. I described it without saying whether it is switched on.
- **Outcome:** in the June batch, 2,829 of 3,962 invoices (71.4%) were auto-approved. The tool caught 11 duplicates in June and July, and has run the monthly batch since June.
- **Your role and what it becomes:** you were the sole developer. The matching rules are now a generic template you reuse.

#### What I left out, and why
- **Fees and day rate:** the client asked for these to be kept out.
- **Supplier names, per-supplier volumes and the average invoice value (3,450):** the client asked for supplier names and per-supplier volumes to be kept out. I treated invoice value as client financial data.
- **Controller's name:** I used the role only.
- **"3 days to under 1 day" at month-end close:** this was a verbal comment from the client and was never measured. You weren't sure of it in your notes, so I labelled it [reported] and cut it. If you would say it plainly as your own observation, I can restore it.
- **"Pays for itself in a quarter":** tone unclear, so I excluded it.
- **38,000 estimated annual exposure avoided:** I cut it from the publish copy, for these reasons:
  - The ledger says this is 11 caught duplicates × 3,450 average, extrapolated over 12 months. But 11 × 3,450 is 37,950, which is the two-month total with no extrapolation. A 12-month extrapolation would be about 227,700.
  - No currency is given.
  - Caught duplicates may never have been paid, so "exposure avoided" may overstate it.
  - Tell me which calculation you meant and I can restore it as "an estimated …".

#### Needs your confirmation
1. **Tolerance figures (2% / 15 units).** Your controller signed these off, but the permission email doesn't mention them. They show how the tool works, so I included them. Say if you'd rather keep them generic.
2. **Invoice volume (about 4,000 a month).** The client barred per-supplier volumes, not total volume. I read that as allowed. Please confirm.
3. **"In use since June."** This comes from your notes only, and I labelled it [reported]. Confirm it is still accurate.
4. **Size band.** Your notes say about 220 staff. I wrote "roughly 200".

#### Gaps in my checks
- **Publish gate, voice:** no confirmed apply-author-style profile was supplied, so gate 5 is open. The metadata marks the study "Publish-ready: no".
- **`writing_check.py`:** I can't run scripts here. I did the banned-phrase scan and the read-through by hand and found nothing. Please run the real checker before you publish.
- **Arithmetic:** I checked 2,829 / 3,962 = 71.4%.
- **Layer reached:** the files are prepared locally. Nothing has been posted to your site.

#### Files
- `./out/invoice-matching-case-study.md`
- `./out/answer.md`

### File: invoice-matching-case-study.md

```
Study:            Three-way invoice matching for a regional food distributor
Maps to offer:    Finance-operations automation (matching and exception-queue builds)
Evidence status:  verified (reported and estimated figures held back from the publish copy)
Sanitization:     done
Ownership check:  clear (own code; client permission email of 14 Oct 2026; client data excluded)
Publish-ready:    no — blocked on: confirmed apply-author-style profile (gate 5); candidate OK on the tolerance figures
```

#### WORKING COPY

##### Title
Three-way invoice matching for a regional food distributor

##### Client (sanitized)
Regional food distributor, roughly 200 staff. Accounts payable team of six. [verified: ~220 staff in notes; banded]

##### Problem
Clerks matched every supplier invoice to its purchase order and goods-received note by hand in spreadsheets. About 4,000 invoices a month [verified: AP volume report, May 2026]. Mismatches in price, quantity or receipt surfaced after the payment run was scheduled, which created duplicate-payment risk and supplier disputes.

##### What I did
Solo build, March to June 2026 (14 weeks). A three-way matching tool in Python and SQLite, plus a small Flask page for the clerks. Two AP clerks helped write the reason codes. The client's finance controller signed off the tolerances.

##### How it works
- Inputs: ERP export of purchase orders, receiving log CSV, invoice batch.
- Pass 1: exact match on PO number.
- Pass 2 (PO number missing or mistyped): fuzzy match on supplier + amount + a 10-day date window.
- Price tolerance: 2% or 15 currency units, whichever is lower. [reported: from notes; confirm OK to publish]
- Three queues: auto-approve, review (with reason code), hold (no receipt or suspected duplicate).
- Duplicate check: hash of supplier ID + invoice number + amount.
- Clerks work only the review and hold queues.
- Email alert for holds: built, not switched on by the client. [in progress]

##### Outcome
- June batch: 2,829 of 3,962 invoices auto-approved, 71.4%. [verified: pilot run log, computed]
- 11 duplicate invoices caught, June–July. [verified: hold-queue export]
- In use for the monthly batch since June. [reported: candidate's notes]
- Month-end matching time fell from about 3 days to under 1 day. [reported: client's verbal comment, never measured] — held back from the publish copy; see chat.
- Estimated annual duplicate exposure avoided: 38,000. [estimated] — held back; see chat.
- "Pays for itself in a quarter." Not usable (tone unclear). Excluded.

##### My role
Sole developer and designer: requirements, rules, code, queue page, rollout to the monthly batch. Clerks contributed reason codes; the controller approved tolerances.

##### What it becomes
The matching rules are now a generic template in my own code with no client data. Offer: three-way matching and exception-queue builds for AP teams.

##### Excluded on purpose
Client name and logo, controller's name, day rate and any fee figure, supplier names, per-supplier volumes, average invoice value (client financial data).

---

#### PUBLISH COPY

#### Three-way invoice matching for a regional food distributor

**Client:** A regional food distributor with roughly 200 staff.

##### Problem
The accounts payable team of six matched about 4,000 supplier invoices a month against purchase orders and goods-received notes by hand, in spreadsheets. Price, quantity and missing-receipt mismatches showed up after the payment run was scheduled. That meant duplicate-payment risk and disputes with suppliers.

##### What I did
Between March and June 2026 I built a three-way matching tool in Python and SQLite, with a Flask page for the clerks. I worked with two AP clerks to write the reason codes, and the finance controller approved the tolerances.

##### How it works
The tool reads the ERP purchase-order export, the receiving log and the invoice batch. It first matches on exact PO number. When the number is missing or mistyped, it falls back to a fuzzy match on supplier, amount and a 10-day date window. Price differences pass within 2% or 15 currency units, whichever is lower.

Every invoice lands in one of three queues. Auto-approve needs no attention. Review carries a reason code that tells the clerk what to check. Hold collects invoices with no receipt or a suspected duplicate, found by hashing supplier ID, invoice number and amount. Clerks work the review and hold queues only. A hold alert by email is built into the tool.

##### Outcome
In the June batch, 2,829 of 3,962 invoices, 71.4%, went through auto-approve. The tool caught 11 duplicate invoices in June and July. It has run the monthly batch since June.

##### My role
I was the only developer. I gathered the requirements, designed the matching rules, wrote the code and the queue page, and moved it onto the monthly batch. The clerks shaped the reason codes and the controller set the tolerances.

##### What it becomes
I have rebuilt the matching rules as a generic template with no client data. I use it for three-way matching and exception-queue projects in accounts payable.

---

#### CHECKS (working record)
- Banned-phrase scan of the publish copy by hand ("not verified", "unverified", "not claimed", "directional", "does not prove", "Where it stood", etc.): none found. `writing_check.py` could not be run here; I did a manual read for X-not-Y constructions, filler and closing restatement and found none.
- Arithmetic: 2,829 / 3,962 = 71.4%.
- Gate: 1 sanitized ✔; 2 owned ✔ (no rate card or margin); 3 sourced ✔; 4 separation ✔; 5 voice — pending a confirmed author profile; 6 two versions ✔.
