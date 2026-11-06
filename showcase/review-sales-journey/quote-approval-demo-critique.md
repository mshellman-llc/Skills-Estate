---
skill: review-sales-journey
title: Critique of a quote-approval demo against discovery notes
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: b3017491fc634e10d3e701a494df80578b65d168147fbdc4e4563724a5c46dd2
---

## Request

I'm presenting this quote-approval demo to Brightwater's operations leadership on Thursday. Can you critique the demo outline against our discovery notes and tell me what to fix first?

## Inputs

Run of the built `map-sales-process` task package in its "review a sales journey or demo" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### demo-outline.md

#### Quote Approval Demo, v3 (draft for Thursday)

Audience: Brightwater Packaging operations leadership (COO, head of customer service, finance manager).
Presenter: Dana Okafor, solutions consultant, Kestrel Quote.

##### Stage 1: Request
Customer service rep enters a quote request in Kestrel. Slide: "Seamless intake, all in one place."

##### Stage 2: Price
Kestrel pulls list price and applies discount rules. Screenshot: pricing screen with a 12% discount field.

##### Stage 3: Approve
Quotes over the threshold route to an approver. Slide: "Faster approvals drive faster revenue." Click "Approve" button in the prototype; the status changes to Approved.

##### Stage 4: Send
Quote PDF is emailed to the buyer. Slide shows the email template.

##### Stage 5: Win
Buyer accepts. Order is created in the ERP.

##### Proposed-behavior links
Each stage has a "See proposed behavior" link that opens a one-paragraph description.

##### Systems
Kestrel Quote (new), ERP (existing), email.

##### Success
"Approval cycle time falls 35%."

#### discovery-notes.txt

Discovery call notes, Brightwater Packaging, 14 Oct 2026
Attendees: Priya Nair (head of customer service), Tom Elkins (finance manager), Dana Okafor.

Today: Reps build quotes in a spreadsheet, using prices from the ERP price list export. Any quote with a discount above 8% goes to a regional sales manager by email. Managers reply "ok" or "no" when they find time; Priya says reps often chase by phone. Finance (Tom) sees the quote only after the buyer accepts, and has twice reversed a discount that nobody had approved properly.

Approver is the regional sales manager. If the manager is on leave, nobody covers; quotes wait. No one tracks how long. Priya's guess: "a day or two, sometimes a week". Not measured.

Rejections: the manager says no, rep re-quotes at a lower discount and emails again. No record of why.

Buyers get a PDF by email from the rep's own mailbox. Buyers reply by email to accept; rep keys the order into the ERP by hand.

Tom wants: approved discount and approver name visible on the order in the ERP. Priya wants: reps stop chasing.
No agreed target for approval time. Tom asked for a baseline before any target is set.

## Output

**Fix the Approve stage first.** The outline is built around the right problem, but Stage 3 is the only stage where Brightwater's pain is concentrated, and the demo treats it as a button that flips a status. Rebuild that stage as a paired current-versus-proposed walk-through of one quote with a 12% discount, including a rejection. Then replace the "35%" success line with a measurement definition. Both changes can be made from what you already have.

I reviewed `demo-outline.md` (v3) against `discovery-notes.txt` (14 Oct 2026). I read the outline as text only. I did not see the prototype, so I can't say whether the Approve button does more than change the status label.

#### Who the demo is about

Two different people are in this journey. Brightwater's customer service reps and regional sales managers are the software users. Brightwater's own buyers receive the quote, and Priya Nair, Tom Elkins and the COO are judging the internal workflow. The outline never says which of these people each stage serves. Stage 4 ("Send") and Stage 5 ("Win") involve the buyer, but nothing shows what the buyer sees or does.

#### What to keep

- The five-stage navigation fits the discovery material. Request, price, approve, send and accept match the process Priya and Tom described.
- The 12% discount on the pricing screen is a good choice. The notes put the approval threshold at 8%, so that quote triggers routing in Brightwater's own terms. Say so aloud: "above your 8% line."
- The systems list names the right three, Kestrel, the ERP and email.

#### Findings, in priority order

| # | Location | What the outline shows or omits | Repair | Acceptance check |
|---|---|---|---|---|
| 1 | Stage 3, Approve button and "See proposed behavior" link | The click changes a status to Approved. It doesn't show who the approver is, how they are told, what they see, or what the rep sees meanwhile. The link opens a paragraph, so it shows navigation, not task behavior. The notes list four current problems: email approval, phone chasing, no cover when a manager is on leave, and no record of rejection reasons. None appears. | Walk one quote end to end. The rep submits a 12% quote. The regional manager is notified and opens it. The manager approves, or rejects with a reason. The rep sees the outcome. Then show what happens when the manager is on leave. Pair this with today's step: the manager replies "ok" or "no" by email, and the rep chases by phone. | A reviewer can trace one quote from submission to decision, see the rejection and re-quote path, and see who acts if the manager is away. If Kestrel has no cover rule, say that as a stated limit. Don't leave the gap unmentioned. |
| 2 | Success line, "Approval cycle time falls 35%" | No definition, baseline or source for 35%. The notes say approval time is not measured ("a day or two, sometimes a week" is Priya's guess) and that no target exists. Tom asked for a baseline before any target. | Remove the 35% from the deck unless it is an agreed target, and label it a target if so. Define the measure instead: start event is the rep submitting the quote for approval, end event is the approver's recorded decision, window is the pilot period, source is Kestrel timestamps. Propose a baseline step: sample recent emailed approvals for a few weeks before go-live. Add a rework count (quotes re-quoted after rejection) and the number of unapproved discounts found after acceptance. | The success slide gives start and end events, data source and owner. It states plainly that no baseline exists yet. A reviewer can tell the 35% is not a result. |
| 3 | Stage 5, Win, and Tom's request | The outline says "Order is created in the ERP" but not how. The notes say reps now key accepted orders in by hand, and Tom's need is the approved discount and approver name on the ERP order. He twice reversed discounts that were not properly approved. | Show the ERP order after acceptance, with the approved discount and the approver's name in view. State whether Kestrel writes the order or whether a rep still keys it. If that integration is not confirmed, say it is unconfirmed. | Tom can see on one screen which fact reached the ERP, who approved it, and which system wrote it. |
| 4 | Stage 4, Send | The email template is shown. The notes say quotes now go from the rep's own mailbox and buyers accept by replying. The outline doesn't show where the buyer's acceptance is captured. | Show the buyer's side of acceptance: what the buyer clicks or sends, and where the rep sees it. If acceptance is still an email reply, name that. | The path from sent quote to recorded acceptance is traceable, with the offline step labeled. |
| 5 | Slides at Stages 1, 3 | "Seamless intake, all in one place" and "Faster approvals drive faster revenue" assert benefits with no support. The second links approval speed to revenue with no evidence. | Replace with the observed task. For example: "Reps enter requests in Kestrel; today they build quotes in a spreadsheet using an ERP price export." Drop the revenue claim. | Each slide states something a viewer can check against the demo or the notes. |
| 6 | Stage 1, Request and Stage 2, Price | The outline doesn't pair these with today's spreadsheet and ERP price-list export. Whether Kestrel reads prices live from the ERP is not stated. | Add a one-line current-state note per stage, and state the price source. If live price sync is not confirmed, list it as an open question. | The change at each stage is visible, and the price system of record is named. |

#### Coverage and limits

The five checks apply as follows. Customer flow is thin: the rep and manager appear only as labels, and the buyer is missing at Stage 4. Current versus future is missing in every stage. Systems are named, but data ownership is not. Click paths exist only for the Approve button. Measures are the weakest part, as finding 2 shows.

Not established by the material: the prototype's actual behavior, who the approver is for quotes below the threshold, what the threshold is in Kestrel's configuration, and whether the ERP integration exists. I treated each as an open question and did not assume an answer.

#### Illustrative corrected path for Stage 3

This uses only the facts from the notes and the 12% example from your outline. The steps for Kestrel are proposed behavior and need confirming against the prototype.

1. Today: a rep builds a 12% quote in a spreadsheet and emails the regional manager. The manager replies "ok" or "no" when free. The rep phones to chase. Finance sees the quote only after acceptance.
2. Proposed: the rep submits the quote. Kestrel flags the 12% discount as above the 8% line and routes it to the regional manager.
3. The manager sees the quote and approves, or rejects with a reason. The rep sees the outcome on the quote.
4. Exception: the manager is on leave. Show who receives the quote, or show that Kestrel leaves it waiting and say that is a gap to settle with Priya.
5. Result: the ERP order carries the discount and the approver's name, which is what Tom asked to see.

#### Decision before Thursday

You need to decide whether Kestrel can name a backup approver. If it can, show it in the exception step. If it can't, tell Brightwater now. That is the one question in the notes with no current answer on either side.

A note on method: I couldn't run the bundled writing scanner here, so I read this critique by hand against the sentence-pattern and paragraph checks and found no flagged patterns I left in place.

**Files:** none saved; this answer is the deliverable.
