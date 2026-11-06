---
skill: review-deliverable
title: Source check of a board decision memo before release
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 854448520c20383707e16bddd027fed13a2196e75b083918a894e4f0398b9e1b
---

## Request

Can you check my catalogue-system decision memo against the vendor quote and the meeting notes before I send it to the board on Friday? I need to know if it's safe to send as is.

## Inputs

Run of the built `review-deliverable` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `quality-record.json`.

#### meeting-notes.md

#### Finance committee notes, 14 October 2026

Attendees: Priya Raman, Tomas Aguilar (treasurer), Dana Whitfield (chair), Ines Okafor.

- The committee reviewed two vendors, Linden Software and one other. Verbal pricing only for Linden at that point; the written quote came later.
- Committee voted 3 to 1 to recommend Linden to the Board. Ines Okafor against, citing the migration risk.
- Capital line for systems is $50,000 for FY2027. Tomas to confirm whether sales tax counts against it.
- The Board votes on the recommendation and budget at its meeting on 18 November 2026.
- Priya noted roughly 6,000 member records have duplicate entries and need cleaning before any extract.
- Target go-live is "after the February school holidays", to be confirmed once the order is signed.

#### memo.md

#### Decision memo: replacing the library catalogue system

To: Board of Trustees, Tidewater Library Cooperative
From: Priya Raman, Operations Manager
Date: 6 November 2026

##### Recommendation

Go. We recommend signing with Linden Software to replace our catalogue system, with go-live on 2 February 2027.

##### Cost

The first-year cost is $47,300, including licence, implementation, data migration and staff training. This is within the $50,000 capital line.

##### Approval

The Board approved the budget on 14 October, so no further spending approval is needed. The finance committee has also signed off on the vendor.

##### Timing

The quote is valid until 30 November 2026. Delivering on 2 February 2027 is fully achievable and carries no material risk, since the migration is straightforward.

##### Why this matters

Our current system is a critical part of our mission and we are excited to embrace a transformative new chapter. It is not just a catalogue; it is a gateway to our community. Moving now will ensure seamless, best-in-class service for every member.

#### vendor-quote.txt

Linden Software - Quote LQ-2209
Prepared for: Tidewater Library Cooperative
Issued: 20 October 2026. Valid until: 30 November 2026.

Subscription licence, hosted: $2,400 per month, billed monthly (12 months = $28,800)
Implementation and configuration: $12,500 fixed
Data migration: 40 hours at $150 per hour (estimate; billed on actual hours)
Staff training: $2,200 (two half-day sessions)

Notes:
- Migration hours assume the member records are de-duplicated before the extract. Records that need cleaning are billed at the same hourly rate.
- Standard implementation lead time is 14 weeks from signed order.
- Prices in USD, excluding sales tax.

## Output

### Quality record: catalogue-system decision memo

**Verdict: not safe to send. Release is withheld.** Three of the memo's four high-risk claims do not match your sources, and the fourth is unsupported. The fixes are small, and I list them below.

**Artifact:** `inputs/memo.md`, a decision memo to the Board of Trustees dated 6 November 2026. It supports a go/no-go on signing with Linden Software.
**Sources read:** `inputs/vendor-quote.txt` (quote LQ-2209) and `inputs/meeting-notes.md` (finance committee, 14 October 2026).
**Layer reached:** reviewed locally. Nothing was sent or changed, and I edited no file.

#### Checks

| Control | Verdict | Evidence |
|---|---|---|
| Source reconciliation | **fail** | Details below |
| Prose review (`writing-diagnostics`) | **blocked** | I read the memo and found defects (below). I cannot run the receipt tool here, so no receipt exists. |
| Brand renderer | not applicable | The memo is plain Markdown, not a styled file. No preflight report or `brand_check.py` result exists, and none is needed. |

#### Assertions against sources

| # | Memo claim | Source says | Result |
|---|---|---|---|
| A1 | First-year cost is $47,300 "including licence, implementation, data migration and staff training" | Licence $28,800 (12 × $2,400) + implementation $12,500 + migration $6,000 (40 h × $150, an estimate) + training $2,200 = **$49,500**. The memo's figure is exactly $2,200 low, so it leaves out training despite saying it includes it. | **Fail** |
| A1b | "Within the $50,000 capital line" | $49,500 leaves $500 of headroom. The quote excludes sales tax, and the notes say Tomas Aguilar still has to confirm whether tax counts against the line. Migration is billed on actual hours, and about 6,000 member records need de-duplication first, billed at the same $150 rate. The claim is not supportable as stated. | **Blocked** |
| A2 | "The Board approved the budget on 14 October" | 14 October was the finance committee meeting. It voted 3 to 1 to *recommend* Linden. The Board votes on 18 November 2026. | **Fail** |
| A3 | "The finance committee has also signed off on the vendor" | The committee recommended Linden on verbal pricing only. The written quote arrived later. One member, Ines Okafor, voted against because of migration risk. | **Fail** |
| A4 | Go-live 2 February 2027 is "fully achievable" with "no material risk" | The quote gives a standard lead time of 14 weeks from signed order. The Board cannot approve before 18 November, so an order signed on 19 November would reach about 25 February 2027. The notes only say "after the February school holidays, to be confirmed". Ines Okafor's migration concern and the duplicate-record cleanup contradict "no material risk". | **Fail** |
| A5 | Quote valid until 30 November 2026 | Matches the quote. | Pass |

I recomputed every total by hand. Because the figures and approvals are high-risk claims (financial figure, approval status, go/no-go), none can be released on an unsupported source.

#### Prose findings

I read the whole memo. `writing_check.py` and `prose_receipt.py` need a shell, so I could not run them and did not substitute a clean scan. This is a manual reading pass only.

- **"Why this matters"** is filler and should be replaced. "Critical part of our mission", "transformative new chapter", "not just a catalogue; it is a gateway" and "seamless, best-in-class" add no fact. The section also never says what is wrong with the current system. Replace it with the actual reason for the change, which the sources do not state, so you need to supply it.
- **"Fully achievable"** and **"straightforward"** in Timing are unsupported confidence words. They should go with the A4 rewrite.
- The Cost, Approval and Timing sections are otherwise plain and short.

#### Blockers and remediation

1. **Correct the cost to $49,500.** State the components. Say the migration line ($6,000) is an estimate billed on actual hours.
2. **Qualify the capital-line claim.** Say the total is $500 under the $50,000 line before sales tax and before any extra de-duplication billing. Get Tomas Aguilar's answer on tax before you write "within".
3. **Rewrite Approval.** Say the finance committee recommended Linden on 14 October (3 to 1) and the Board votes on 18 November. Remove "approved" and "no further spending approval is needed". Remove "signed off on the vendor". Consider stating the dissent, since the Board will see it in the minutes.
4. **Rewrite Timing.** Give the 14-week lead time and the resulting date (late February 2027 if signed after the 18 November vote). Replace "no material risk" with the duplicate-record cleanup, which affects migration cost and timing. Confirm the go-live date with Linden before the memo states one.
5. **Replace "Why this matters"** with the real reason for replacing the system.
6. **Rerun the prose check** (`writing_check.py`, then `prose_receipt.py emit` and `validate`) once the memo is revised, and record the receipt path.

#### Quality record (as saved)

Saved as `out/quality-record.json`. I filled it in by hand and did not run `quality_gate.py`, so its structure is unvalidated.

- `artifact`: `inputs/memo.md`, `brand_render: false`, `narrative_final: false`
- `controls_selected`: source-reconciliation, writing-diagnostics, brand-renderer
- `checks`: source-reconciliation **fail**; writing-diagnostics **blocked**; brand-renderer **not_applicable**
- `assertions`: A1 financial_figure, A2 and A3 approval_status, A4 go_no_go, each tied to the source-reconciliation check, which failed
- `release.released`: **false**
- `hub_update.status`: not_applicable

When I applied the validator's documented rules by hand, the record fails closed. Each of the four high-risk assertions lacks a passing cited check, so the validator would report blockers, and `released: false` is consistent with them. It would treat the record as valid but unreleased.

#### Files

- `out/quality-record.json`: the record summarised above
- `out/answer.md`: this review
