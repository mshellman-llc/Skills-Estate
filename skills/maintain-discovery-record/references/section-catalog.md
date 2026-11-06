# Section catalog

This catalog does double duty: it is the ledger's retrieval checklist (work it top to bottom while building Column A and B) and the projection target (the sections the brief renders). Derive the section set from the ledger, never from an example: the three load-bearing sections are always present; the flex sections appear only where the ledger holds the substance.

Open each rendered section with one line stating the bar it is held to.

Alignment note: this catalog satisfies the `discovery_brief` contract in the evidence-core artifact registry. Its required domains map as follows: known facts and source coverage live in Column A and section 01; ranked unknowns are section 02; scope at stake is section 03; decision owners and call outcome are required subelements of section 01. Its hard fails (generic questionnaire, re-asking confirmed facts, unknown presented as fact, unranked questions, template substitution) are the ledger rules in field form.

## 01 Situation (always)

- **Answers:** who the client is, what they are buying, the shape of the deal, how the call is set up to run, who in the room owns which decision, and the outcome the call must produce.
- **Bar:** a teammate who has never seen the account can state, in two minutes, the deal, the call format, the decision owners, and what the call must not end without. Every line sourced, none guessed.
- **Required subelements:** the decision owners (who on the client side can answer or commit on each High-rank question; who is absent that matters, Finance or IT not attending is itself a finding) and the call outcome (the one or two resolutions the session exists to produce, drawn from the top of Column B).
- **Retrieve from:** Salesforce (account, opportunity, products, competitors, contact roles), the RFP, workshop notes, the AE's call prep for format and attendees.
- **Prevents:** a team that walks in cold, or worse, re-asks what the record answers.

## 02 Ranked unknowns (always; the spine)

- **Answers:** the open questions that change the proposal, in the order the call should work them.
- **Bar:** every question names the scope line it unblocks, earns its place by moving the estimate, and sits in rank order. The top questions block a workstream from being sized at all.
- **Retrieve from:** Column B, built by working every other section and writing a question for each unknown.
- **Render:** numbered blocks in rank order, each with the rank, the why-open reasoning, and the scope lever line ("don't size the ORD lines until Q-01 is answered"). Close on the single gate that must clear before design.
- **Prevents:** a call that burns time on low-leverage curiosity, and a proposal that prices an open item.

## 03 Scope at stake (always)

- **Answers:** the candidate scope lines the answers will shape, mapped to capability codes and phases.
- **Bar:** every line carries its capability code and phase; pattern-derived lines are visibly separated from RFP-derived ones; every un-sizeable line is flagged in place with the question that blocks it.
- **Retrieve from:** the firm's pattern and capability catalog (core lines), the RFP (client-specific NOW items), the capability-response sheet. Cross-reference every Column B question to the line it sits under.
- **Prevents:** pricing an open item by accident, and losing RFP-specific items inside the generic pattern.

## 04 Competition (flex)

- **Include when** competitors are named on the opportunity. **Drop when** sole-source or pure expansion.
- **Bar:** each alternative carries a threat level and a one-paragraph position in the client's own terms, not a feature list. Include the status-quo "do nothing" option; it is always the cheapest competitor.
- **Retrieve from:** the SF opportunity, Slack and Gmail for live intel (treat single-channel intel as Inferred), the workshop for the do-nothing baseline.

## 05 Value arguments (flex)

- **Include when** the value is contested or needs asserting. **Drop when** the call is pure technical scoping.
- **Bar:** each argument leads with the business outcome, ties to a pain the client stated in their own words, and is specific enough to say aloud without hedging. No cold claims.
- **Retrieve from:** workshop transcripts (verbatim pains, attributed), prior comparable engagements, the RFP's stated goals.

## 06 What to listen for (flex)

- **Include when** the call is exploratory or a reverse demo. **Drop when** tightly scripted.
- **Bar:** each cue is something a listener can catch in the moment, paired with the concrete scope move it triggers. Not "listen for pain points".
- **Retrieve from:** Column B (many unknowns have an audible tell), the workshop's partial signals, the AE's political read.
- **Prevents:** the answer to Q-03 leaking out in an aside and nobody catching it.

## 07 Build complexity (flex)

- **Include when** a capability-response scoring exists and something scored partial. **Drop otherwise.**
- **Bar:** each partially-capable item is a named line with the reason it is custom, its dependency, and where it sits in the plan. Never folded into a "customization" bucket; an unnamed custom line is where fixed-fee margin leaks.
- **Retrieve from:** the capability-response sheet, cross-referenced to the Column B questions each item depends on.

## 08 Decisions, risks, and assumptions (post-call)

- **Include when** at least one ingestion has run. This is where the post-call record's decision, risk, and assumption domains render.
- **Answers:** what the sessions decided (with who decided and where in the transcript), what threatens the deal or the delivery, and which load-bearing claims are still Inferred rather than Confirmed.
- **Bar:** every decision carries a transcript reference and a status (proposed until the scoping owner confirms); every risk names its trigger; every assumption is labeled as one with its basis. A decision that changes prior scope is flagged as a decision change.
- **Retrieve from:** the decision log built during ingestion, the Inferred rows of Column A, and any conflict flags in the ledger.
- **Prevents:** decision changes lost in an aside, and an assumption hardening into a fact nobody sourced.

## 09 Next discovery actions (post-call)

- **Include when** Column B still holds open questions after an ingestion.
- **Answers:** what discovery should happen next: the sessions to schedule, the documents to request, the retrievals to run, each tied to the Column B question it would close.
- **Bar:** every action names its question and an owner. Recommendations for calls to schedule flow to prepare-sales-pursuit's Pursuit Brief; this section states the discovery need, not the call plan.
- **Retrieve from:** the re-ranked Column B and the why-open fields.
- **Prevents:** discovery drifting into a standing meeting with no closure path.

## Post-call record domains

The post-call discovery record covers ten domains. Each maps onto the ledger and this catalog rather than getting its own artifact: business problem and current state (01, Column A), stakeholders and users (01), desired outcomes (01, 05), requirements and constraints (03, 07), decisions (08), risks (08), assumptions (08, from Column A's Inferred rows), open questions (02, Column B), evidence references (the source and date every Column A row carries), and recommended next discovery actions (09).

## Scaling and renaming

A thin deal yields the load-bearing three, folded tight. A rich RFP earns every section and a long Column B. Fit section titles to the deal's language ("Scope at stake" can become "Capabilities in play"); keep the section's job, change the label. The question count in 02 always equals the count of real scope-moving unknowns in Column B; padding to look thorough is a defect the gate cannot catch, so hold the line yourself.
