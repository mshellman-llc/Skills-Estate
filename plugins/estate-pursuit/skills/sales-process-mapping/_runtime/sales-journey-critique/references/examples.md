# Critique examples

These are hypothetical examples, not client facts or mandatory output templates.

## A polished journey with no task behavior

Artifact: A demo has expandable cards labeled Qualify, Propose, and Close. Its proposed-behavior link opens another paragraph. It names a CRM but provides no screens, current process, or measures.

Useful critique: Preserve the stage navigation. The Propose card explains an internal sales activity, but the buyer's review and response are missing. Show who receives the proposal, where they review it, how they request a revision, and how the seller receives that request. Pair that task with the evidenced current process. Treat the current screens as a discovery gap until they are supplied. A link that opens descriptive text establishes navigation, not a working proposal flow.

Acceptance: A reviewer can trace the buyer's action through the seller handoff and see what changes between the two states. A proposed measure could be time from proposal delivery to the first buyer response, with event definitions, a data source, and an owner; no baseline or target is supplied here.

## A complete slice of a larger sales cycle

Artifact: An excerpt covers only proposal revision. It provides buyer and seller swimlanes, evidenced current screenshots, proposed screens, data ownership, a rejection path, and a defined response-time measure. It does not cover lead qualification or fulfillment.

Useful critique: Review proposal revision within its stated scope. Credit the supported path and measurement definition. Do not demand unrelated stages or invent missing defects. If a prototype was not opened, describe what the screenshots establish and leave runtime behavior untested.

## A metric and identifier problem

Artifact: A screen says “REQ-42 / SOL-8: customer experience improves 40%,” with no definition, baseline, or supporting result.

Useful critique: Give the behavior a descriptive label and retain the IDs as references. The improvement claim cannot be assessed from this screen. Ask which experience measure the percentage describes, how it was calculated, and which evidence supports it. If the number is an approved target, label it as a target; otherwise remove the unsupported number from proposed replacement copy. Do not substitute a fabricated baseline.

## Repairing formulaic critique prose

Hypothetical draft with writing defects:

> This isn't just a sales process. It's a customer experience transformation. The result? A seamless, scalable, customer-centric journey. The real opportunity: unlock value.

Evidence available for the rewrite: The proposal screen lets a buyer request a revision, but the artifact does not identify who receives the request or how the buyer learns that it was received.

Revised critique: The proposal screen lets the buyer request a revision. Show who receives the request and what confirmation the buyer sees. A reviewer should be able to trace the request from submission to the seller's response.

The revision removes the staged contrast, scripted reveal, unsupported benefit claims, and slogan. It retains the observed behavior and supplies a concrete repair without inventing a response time or business result. Apply this structural review to the whole critique, including its opening and closing sentences.

## Repairing abstraction and unsupported consequences

Evidence: The proposed design requires a seller to approve a revision before the buyer sees a new proposal. No customer research or conversion results are supplied.

Hypothetical flawed draft:

> The implementation of revision approval facilitates customer confidence, driving increased conversion. By prioritizing a customer-centric revision experience, the journey can become more customer-centric.

Revised critique: The proposed design requires the seller to approve a revision before the buyer sees the new proposal. Show the seller's approval action and the buyer's waiting state. Test whether buyers understand when the revised proposal will arrive.

The rewrite preserves the approval dependency and proposed status. It removes the unsupported conversion claim and replaces circular advice with screen behavior to show and a research question to test. It does not invent timing, customer sentiment, or a result.

## Checking the diagnosis before agreeing

Hypothetical request: “This doesn't show the current process anywhere. Critique it.”

Evidence: Page 2 pairs the current emailed request with a proposed portal request. Both identify the buyer and seller. The proposed path ends at Submit; no acknowledgement or retry behavior is shown. No runtime test is supplied.

Useful critique: Page 2 shows the current email process alongside the proposed portal request. The missing detail is what happens after the buyer selects Submit. Show the acknowledgement and the retry path, including what happens to the buyer's input if submission fails. A reviewer should be able to trace both outcomes from that screen.

This critique corrects the diagnosis using the supplied page, identifies the actual gap, and gives an acceptance check in one paragraph. It does not claim the portal works or prescribe new stages outside the request.

## Keeping language that already works

Hypothetical source: “Show who owns the request—and what the buyer sees while waiting.” The scenario establishes an unassigned request and an absent waiting state.

Keep the sentence. Its dash joins two related requirements; both are grounded in the scenario. Do not replace it with a generic statement about transparency, force it into a table, or remove the buyer's waiting state for brevity.
