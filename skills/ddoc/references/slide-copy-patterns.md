# Slide-copy editorial patterns

These are the editorial rules for DDOC slide copy: how each slide type should read once the manifest structure is settled. The structural skeletons, the manifest schema, and the failure-mode table live in `ddoc-patterns.md`. This file governs the wording that goes in the boxes.

The rules below are slide-type specific. Apply them during the Phase 3 slide-by-slide review, alongside the scanner findings.

Two authoring registers exist under the two DDOC modes. Decision mode (the client is choosing between options) leans on the options slide and the recommendation. Confirmation mode (one option) leans on the boundary and the deliberate exclusions. The editorial rules for each slide type below apply in whichever mode the slide appears.

---

## Problem / why this matters

The purpose of this slide is to make the client feel the cost of the status quo before they see the solution. Three beats:

1. Name the specific problem. Not "visibility challenges" but "Pewag tracks chain wear in a spreadsheet that cannot send alerts."
2. Name the consequence. Not "missed revenue" but "Jim estimates missed replacement revenue at 10–20%."
3. Name what the engagement fixes, in one sentence, not a scope list.

This slide fails when it is written from Estate's perspective ("We identified an opportunity to improve..."). Write from the client's perspective.

---

## Capability hierarchy slides

The "what we're building" slide presents the scope structure, not the scope line items.

- **L1** is the section header from the quote (for example "Asset implementation," "Quoting," "Reporting"). Plain noun phrases.
- **L2** is one sentence per node: what Estate does in that area, from the client's perspective, in plain English.
  - Correct: "Salesforce tracks every chain set by customer, site, and install date."
  - Wrong: "TCS-001: Asset Object Configuration, 12 hours."
- No item codes, hour counts, or pricing on this slide. Scope detail belongs in the SOW.
- If there are more than 7–8 L2 nodes, group them under their L1 headers and use multiple slides or a collapsed view.

---

## Options / versions slide

Required when the client is choosing scope or phasing. Typical structure is three options (Foundation, then Foundation plus X, then Foundation plus X plus Y), but two or four are valid. Three is the maximum that reads as a decision rather than a catalog.

- The firm option is firm. Label it explicitly: "firm fixed-fee" or "fixed-fee investment."
- Later options are estimates. Label them explicitly: "directional estimate" or "ROM."
- Each card names what is in it specifically. Do not write "Everything in Version 1, plus history migration." Write what the card contains: "Full asset lifecycle tracking, historical chain data migrated from spreadsheets, wear alerts, and opportunity automation."
- Pricing on the options slide must tie to the scoping data and the SOW. Do not round or adjust.
- If the later options are out of scope for the current engagement (options the client may want later), say so clearly in the card footer or a slide note.

---

## Differentiators

Used on persuasive decks where there is no SOW yet and the deck is the primary artifact driving the decision. Every differentiator claim must be specific and falsifiable:

- Correct: "Estate has delivered 14 CPQ implementations on Revenue Cloud in the last 18 months."
- Wrong: "Estate brings deep CPQ expertise and a proven delivery model."

If a specific fact is not available, do not write a generic claim. Flag it for the user to supply.

---

## What we need from you

Frames client responsibilities as partnership asks, not contractual obligations:

- Use second person: "Designate a Salesforce admin with object-level field access," not "Client shall provide admin access."
- Be specific: "Provide export files for 5 years of chain history within two weeks of project kickoff," not "Provide historical data."
- 4–6 items maximum. If there are more, group them.

---

## Investment slide

Three elements only:

1. The number, clearly labeled (firm fixed-fee vs. estimate).
2. One sentence on what it covers: scope boundary and duration.
3. One sentence pointing forward to the proposal: "The proposal that follows carries the full scope, payment schedule, and change order terms." The DDOC runs before the proposal, so it points forward, never sideways to an attached SOW that does not exist yet.

Do not restate the capability list. Do not add an "includes" bullet list of deliverables. The proposal covers that; the slide references it.

---

## Timeline slide

- Phase names, duration, and key milestones only. No internal task names.
- A bar chart with phase names and no milestones tells the client nothing about what they are approving or when they see results. Put the milestones on it.
- Duration must match the SOW.

---

## Next steps

3–5 items, each with a named owner (Estate or Client) and a timeframe:

- Correct: "Client designates project sponsor and admin, by [date]."
- Correct: "Estate sends countersigned SOW, within 2 business days of signature."
- Wrong: "Schedule kickoff" (no owner, no timeframe).

---

## Anti-patterns

**The passive-voice scope recitation:** three bullets of "We will configure... We will migrate... We will build..." Reframe as what the client gets, not what Estate does.

**The hollow differentiator:** "Our team brings unmatched expertise." Remove it or replace it with a specific.

**The timeline without milestones:** a bar chart with phase names and no milestones tells the client nothing about what they are approving or when they see results.

**The agenda that is also a table of contents:** "Section 1: Background, Section 2: Approach..." Write agenda items as the questions the meeting will answer.

**The cover without a document type:** "Pewag USA, June 2026." Always include the document-type label ("Deal Decision deck," "Proposal," "Engagement overview").
