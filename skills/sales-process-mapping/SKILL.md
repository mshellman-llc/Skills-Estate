---
name: sales-process-mapping
description: Map sales processes from discovery files, workbooks, CRM or Jira exports and operating notes. Trace triggers, ownership, handoffs and systems of record, including territory assignment and opportunity creation when relevant.
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->

# Sales process mapping

Explain the business process first: what the customer is trying to accomplish, what starts the work, who moves it forward, and what counts as finished. Connect that explanation to the records and systems used along the way.

## Establish the source set

Start with supplied files and the project's current source authority. Inventory the available material before asking the user for more. Record each source's title, date or revision, type, and useful locator: page, section, worksheet and row, issue key, or event ID. Preserve originals.

Read the relevant content completely in bounded parts. A filename, attachment tile, HTML application shell, short Markdown pointer, or summary does not establish the underlying process. Follow an accessible referenced source; otherwise identify the missing content and proceed with the supported portion.

For CSV exports, preserve repeated headers and every comment column by position or indexed names. Handle quoted multiline cells and byte-order marks. Reconcile duplicate issue keys and revisions without discarding conflicting statements. A ticket assignee is not automatically the business owner. A ticket marked Done does not establish deployed behavior or business adoption.

If Computer History is supplied, use its skill to locate the relevant events and distinguish submitted requests, unsent drafts, user actions, and assistant explanations. Upgrade factual claims to the underlying files or connected records. Do not make Computer History a prerequisite for ordinary mapping requests.

## Find the actual processes

Identify the customer and selling model from the evidence. Distinguish buyer, contracting entity, operating site, service recipient, product or indication, and other entities where they change the workflow. Explain their relationships in ordinary language.

Treat labels such as new business, existing business, expansion, renewal, and lead conversion as candidates. Use the names and boundaries the sources support. Do not impose a generic lead-to-cash funnel or assume that every sale starts with a lead. A lead conversion, new product at an existing site, contract negotiation, onboarding, and recurring order may be separate processes with different triggers and owners.

Begin with a short business explanation and a process inventory. For each process establish its start event, entry conditions, business outcome, customer or product scope, and relationship to other processes. Show which process is being changed by the requested solution. Keep adjacent processes visible only where they supply an input or receive a handoff.

## Trace each process

Map the supported path as:

`business event → eligibility or decision → action → record change → handoff → completion`

For each meaningful step, capture:

- The business trigger, required inputs, and decision rule. Separate the business event from a database creation event, a scheduled job, or a stage transition.
- The person or role doing the work, the accountable decision owner where known, and the next recipient. Keep process owner, account owner, opportunity owner, territory member, and task assignee distinct.
- The record created or updated, its grain, and the system that owns the relevant fact. State what one record represents, such as a site/product pursuit or a contracting-entity agreement.
- The output, recipient acceptance condition, and exit criterion. A handoff is incomplete if the receiving team or required record is missing.
- Material rejection, duplicate, missing-data, reassignment, and rework paths supported by the sources. Mark an undocumented path as an open question rather than filling it with a plausible rule.

Keep current behavior, documented requirements, and proposed changes separate. Retain dates and release stages when an older rule differs from a newer one. Resolve a conflict only through an authoritative decision or direct verification; recency alone does not settle it.

## Resolve assignment and record authority

When territory or opportunity ownership matters, trace each relationship separately:

`territory definition → account coverage → opportunity territory → opportunity owner → task assignments`

Check what defines territories, which source supplies boundaries and membership, what assigns the account, what selects an opportunity's territory, and what chooses its owner. Explain tie-breaks, vacancies, multiple matches, manual overrides, staffing changes, and open versus closed records only to the extent documented. Keep record access and forecast rollup separate from ownership. A territory assignment is not evidence that an opportunity must be created.

For opportunity creation, identify the initiating person or system, qualifying business condition, required account and product context, record grain, duplicate check, and resulting owner. Separate manual and automated routes when both exist. Do not infer an opportunity from every order, activity, product interest, or account update.

Build system-of-record assignments at the entity or fact level. Distinguish where a fact originates, where users maintain it, where it is synchronized, and where it is reported. Name the synchronization direction and timing when supported. A CRM, ERP, spreadsheet, and reporting dashboard may own different facts in the same process. Do not assign all authority to the most visible application or infer an integration from two matching values.

## Deliver the map

For a full map, read [the output model and worked example](references/output-model.md). Adapt its fields to the requested scope; a focused ownership question needs only the relevant path and evidence.

Default to a concise explanation, a readable process diagram, and supporting tables. Use Mermaid for a small static map; use an editable document or interactive view when the requested scale or format warrants it. Match diagram labels and step IDs to the tables. Show customer events, decisions, roles, and handoffs in the primary view; put field names and technical details beside the relevant step or in an appendix.

Include source locators for rules and a short decision list for consequential gaps. For each gap state what is unknown, which path it affects, and who can resolve it if the evidence identifies that role. Any suggested reviewer is a proposal. Missing sources should narrow the claim, not stop all useful mapping.

## Check the result

Walk one representative case from trigger through completion and one material exception using the supplied evidence. Confirm that the diagram and tables agree about owners, sequence, record grain, and system authority. Check that every supported rule has a locator and every unresolved rule stays unresolved in both views. Ensure that a generated explanation has not become its own factual source.

Apply `writing-integrity` to the complete map and accompanying replies. Read its full pattern references, preserve the source facts and qualifications, and review manually if its scanner is unavailable. For text sent under Megan’s name, also apply her current `megan-writing-style` profile.

Read the finished map for business meaning: a reader should be able to say what happens, why it starts, who acts next, and where the result is recorded. A diagram render or schema check cannot establish those facts.

Creating a map does not authorize changes to CRM records, territory rules, Jira issues, permissions, or source files, or sending the map to another person. Report the saved location and validation performed without claiming implementation or adoption.
