---
skill: playbook-onepager
title: Internal brief and client handout for a paid renewal review
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: d968ee8a9d28b50e4de5f049539210e999818df6af2a53c9d5a4ba6adafac605
---

## Request

I need an internal sales brief and a client handout for our new Renewal Risk Review offering, built from the notes in the inputs folder. Sales will use the internal one at pitch prep and we'll send the handout to prospects.

## Inputs

Run of the built `service-offering` task package in its "internal brief or external handout" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `spec.json`.

#### offering-notes.md

#### Renewal Risk Review: working notes (Larkfield Partners, subscription practice)

Paid, fixed-scope, one-off engagement. Sits after our free "Revenue Health Call" (play 01) and before the "Renewal Operations Build" (play 04, multi-month, quoted separately).

**Who**
- Heads of Customer Success or Revenue Operations at B2B subscription software companies, roughly 50 to 300 staff, who own the renewal number.
- They already export renewal data from a CRM and a billing system.
- Not a fit: companies with under 100 paying customers (not enough to see a pattern), or anyone wanting us to run renewals for them.
- A CS manager can sponsor, but the head of CS/RevOps must attend the readout.

**What**
- We review the last 12 months of renewals and churn for one customer segment and show which accounts in the current renewal book look at risk and why.
- It is not a forecasting model, a CRM audit or a customer survey.

**Client value**
- They walk out knowing which upcoming renewals to work first and which warning signs have actually preceded churn in their own data.

**Our reason**
- Converts to Renewal Operations Build. Also gives us a view of their data quality before we quote the build. Fee band: not set yet, finance to decide.

**Included**
- Intake call to agree the segment
- Analysis of one 12-month renewal and churn export plus usage or support data if they have it
- Risk-signal list ranked by how often each signal preceded churn
- Account watchlist for the current quarter's renewals
- 60-minute readout with the head of CS/RevOps

**Not included**
- Data cleanup or pipeline fixes (that is play 04)
- Building a scoring model inside their CRM (play 04)
- More than one segment (a second segment is a separate review)
- Outreach to customers or running save plays

**Delivery**
- Client sends exports within 5 working days of the intake call.
- One analyst, one reviewer. Analysis takes about 10 working days after data arrives (Dana Okafor, delivery lead, to confirm).
- Readout is remote. Deliverables as a PDF report and a spreadsheet.

#### sales-call-feedback.txt

Feedback from Priya Raman (sales), after two pilot conversations:

- Prospects ask "is this just a dashboard?" Say clearly that it is a one-off review of their own history, with a named list of accounts, not software.
- Both prospects wanted to know what they need to send us. Put the data list up front.
- One prospect asked if we would call their customers. We won't.
- Contact for the handout: reviews@example.com
- Do not promise a churn reduction number. We have no results data yet.

## Output

I wrote the content for both documents, but I did not produce the two PDFs. I can't run the renderer here, so the content is ready to render but the PDFs aren't built and nobody has checked page counts or layout.

The internal brief is a rich spec for the two-page layout. The client handout is the one-page layout. Both are in one file, `out/spec.json`. Rendering is one command, run from the one-pager module directory:

`python scripts/render_playbook.py --json out/spec.json --out ./pdfs --prefix "02-"`

After rendering, check that the internal brief is exactly 2 pages and the handout exactly 1. If either overflows, shorten the wording, keeping every boundary and qualifier, and render into a new folder.

#### Decisions for you to lock

1. **Fee band.** Your notes say finance hasn't set it. No price appears in either document. The handout footer reads "Ready when you are." and doesn't say the offering is free.
2. **Delivery duration.** The notes say about 10 working days of analysis after the data arrives, with Dana Okafor to confirm. The internal brief shows it marked as pending. I left it off the handout so you don't publish a time the delivery lead hasn't confirmed. The handout only states the 5-working-day data window.
3. **Play number.** Your notes name plays 01 and 04 but not this one. I used 02 as a placeholder, and the number in `--prefix` is the same placeholder. Confirm it against any other numbering, such as CRM or catalog IDs.
4. **Segment size.** The notes give "roughly 50 to 300 staff" and "under 100 paying customers" as the disqualifier. The handout uses only the 100-customer line. Say if you want the staff range there too.
5. **Churn claim.** Priya's feedback says there is no results data, so neither document states a churn reduction figure.
6. **Logo and brand.** No brand profile was supplied, so the renderer would use the neutral house profile. Point `--profile` at your brand file if you have one.

#### Internal brief (2 pages, sales prep)

- **Descriptor:** a paid, one-off review of 12 months of renewal and churn history. It ends in a ranked watchlist of at-risk renewals and a readout with the head of CS or RevOps. It leads to the Renewal Operations Build (play 04).
- **01 What it is:** a fixed-scope review of one customer segment. It is not software, a forecasting model, a CRM audit or a customer survey.
- **02 Who it's for:** heads of Customer Success or Revenue Operations at B2B subscription software companies of roughly 50 to 300 staff. A CS manager can sponsor, but the head must attend the readout.
  - **Qualifiers:** owns the renewal number, 100 or more paying customers, exports from a CRM and a billing system.
  - **Disqualifiers:** fewer than 100 paying customers, wants us to run renewals, head won't attend the readout.
- **03 Why they care:** they know which renewals to work first and which signals preceded churn in their own data.
- **Talking tracks:** Customer Success head, RevOps head, "is this just a dashboard?" (no, it's a one-off review with a named list of accounts), "will you call our customers?" (no).
- **04 Why we care:** it converts to play 04. It also shows us the state of the client's data before we quote the build.
- **05 Included:** intake call, one 12-month export analysis, ranked signal list, quarter watchlist, 60-minute readout, PDF report and spreadsheet.
- **06 Not included:**
  - Data cleanup or pipeline fixes: play 04.
  - Scoring inside their CRM: play 04.
  - A second segment: a separate review.
  - Customer outreach or save plays: not offered.
- **07 Delivery:** four steps. One analyst and one reviewer. Exports due within 5 working days of the intake call. The analysis time is marked as pending confirmation.
- **Callouts:** Positioning, and Open decisions.

#### Client handout (1 page, for prospects)

- **Headline:** Know which renewals to work first.
- **Subtitle:** See which accounts in your current renewal book look at risk, and which warning signs preceded churn in your own data.
- **Intro:** we review the last 12 months of renewals and churn for one customer segment. You receive a named list of accounts and a ranked list of signals from your own history. This is a one-off review, not software.
- **What you get:**
  - Risk-signal list, ranked by how often each signal preceded churn.
  - Account watchlist for this quarter.
  - 60-minute readout.
  - PDF report and spreadsheet.
- **Two columns:**
  - Who it's for.
  - What we need from you: a 12-month export from your CRM and billing system, plus usage or support data if you have it, sent within 5 working days of the intake call. This puts the data list up front, as the pilot calls asked.
- **Centre note:** one segment per review. A second segment is a separate review.
- **How it works:** intake call, analysis, a second-person check, and a 60-minute remote readout. We don't contact your customers, clean your data or build scoring in your CRM. Those are covered by the Renewal Operations Build.
- **Footer:** "Ready when you are." Contact reviews@example.com to begin.

The handout leaves out the internal "why we care" reasoning, the pipeline motive, the play 04 handoff logic and the disqualifier list.

#### Checks done by hand

- **Grounding:** every fact comes from the two input files. I added no price, duration, result or customer count beyond the notes.
- **Voice:** I read both documents for the house rules and found no em dashes and none of the listed sentence shapes. I did not run the prose checker, so this was a reading pass only.
- **Footer:** the offering is paid, so the footer is the neutral one, per the footer rule.
- **Not done:** no PDF render, no page-count check, no brand check, no manifest. I could not run these.

#### Files

- `out/spec.json`: the render source for both PDFs.
- `out/entry.md`: a condensed house-format record of the offering, with the five fact blocks, Tldr, Eli5 and both one-pager sections. Its internal one-pager points to `spec.json` for the longer prose. Fill those four sections from the spec if you want the catalog entry to stand alone.
- `out/answer.md`: this note.

### File: entry.md

##### 02 · Renewal Risk Review (paid)

**In scope**
- Intake call to agree one customer segment
- Analysis of one 12-month renewal and churn export, plus usage or support data if the client has it
- Ranked risk-signal list and a watchlist for the current quarter's renewals
- 60-minute remote readout with the head of CS or RevOps

**Out of scope**
- Data cleanup or pipeline fixes (Renewal Operations Build, play 04)
- Scoring model inside the client's CRM (play 04)
- More than one segment (a separate review)
- Customer outreach or save plays (not offered)

**Deliverables promised**
- PDF report
- Spreadsheet with the signal list and account watchlist

**Business value**
- Client: knows which renewals to work first and which signals preceded churn in their own data. No churn reduction figure is promised.
- Us: converts to play 04 and shows the state of the client's data before we quote it.

**Target buyer**
- Head of Customer Success or Revenue Operations at a B2B subscription software company of roughly 50 to 300 staff, with 100 or more paying customers, who owns the renewal number. A CS manager can sponsor.

###### Tldr
A paid, one-off review of 12 months of renewal history that ranks warning signs and lists at-risk renewals. It leads to the Renewal Operations Build.

###### Eli5
Think of a doctor reading your last year of check-up notes. She tells you which patterns came before past illnesses and which patients on today's list to see first. She does not treat anyone.

###### Internal one-pager
**What is it**
See `spec.json` (internal.s1).
**Who is it for**
See `spec.json` (internal.s2).
**Why should they care**
See `spec.json` (internal.s3).
**Why should we care**
See `spec.json` (internal.s4).
**What's included**
- Intake call to agree the segment
- 12-month export analysis
- Ranked risk-signal list
- Quarter watchlist
- 60-minute readout
**What's not included**
- Data cleanup or pipeline fixes (play 04)
- Scoring model in their CRM (play 04)
- More than one segment (separate review)
- Customer outreach or save plays (not offered)
Each boundary is the on-ramp to a paid next step.
**How do we deliver it**
One analyst and one reviewer. Client sends exports within 5 working days of the intake call. Analysis takes about 10 working days after data arrives (delivery lead to confirm). Remote readout. PDF report and spreadsheet.

###### External one-pager
**What is it**
A one-off review of your last 12 months of renewals and churn for one customer segment, with a named list of accounts.
**Who is it for**
Heads of Customer Success or Revenue Operations at B2B subscription software companies with 100 or more paying customers.
**Why should you care**
You see which accounts in your current renewal book look at risk. You also see which warning signs preceded churn in your own data.
**What's included**
- Ranked risk-signal list
- Quarter watchlist
- 60-minute readout
- PDF report and spreadsheet
**What's not included**
- Data cleanup or CRM scoring (Renewal Operations Build)
- A second segment (a separate review)
- Customer outreach
**How we deliver it**
Intake call, your exports within 5 working days, analysis with a second-person check, then a 60-minute remote readout.
