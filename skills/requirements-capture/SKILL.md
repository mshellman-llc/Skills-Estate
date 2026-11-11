---
name: requirements-capture
description: 'Capture and structure business requirements in the Aleysian approved format: epics, capabilities, business needs, user stories, and Gherkin acceptance criteria, delivered as a branded two-tab Excel workbook. Use to define, write, organize, or refine requirements, to extract them from an uploaded deck, PRD, brief, spec, or transcript, or to turn a Salesforce SOW into a backlog (BA mode: analyze this SOW, SOW to backlog, Salesforce BA). Triggers on capture requirements, write user stories, define epics, requirements gathering, BRD, acceptance criteria, requirements CSV. Always read the host spreadsheet skill before generating the workbook.'
---

# Aleysian Requirements Capture

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

## Purpose

This skill guides the agent through an interactive, structured conversation to
capture business requirements in the Aleysian approved delivery matrix format.
The final output is a **branded Excel workbook (.xlsx)** with two tabs, ready
for client presentation and downstream use by AI agents or development teams.

## Reference files

Detailed tables live in `references/` to keep this file lean. Read the relevant
one when you reach that part of the work:

- `references/excel-workbook-format.md`: the per-column tables for both tabs,
  the default blue/white styling theme, the Epics-tab formula, and recalculation.
- `references/gherkin-and-questions.md`: Gherkin acceptance-criteria structure
  with a worked example, plus clarifying-question guidance.
- `references/jira-export-and-traceability.md`: the Source column and the
  three legitimate values for it, the gap list, and the workbook-to-Jira field
  mapping. Read it when the requirements come from a SOW or scope document, or
  when the output goes into a Jira backlog rather than staying a spreadsheet.
- `references/ba-mode-salesforce.md`: the BA mode rules for Salesforce
  engagements. Read it whenever BA mode is on (see below).

## Before Generating the Workbook

**Always read the host spreadsheet skill before writing any openpyxl code.**
Look for `xlsx`, `spreadsheets`, or the equivalent in the available skills list.
Follow its guidelines for formula construction, recalculation, error
checking, and code style. Use its `scripts/recalc.py` to recalculate
formulas after generating the workbook.

If an **Aleysian brand guidelines skill** exists (check available skills),
read it and use the official brand colors instead of the default blue/white
theme in the reference file.

## Delivery Matrix: Key Definitions

These definitions form the hierarchy used to organize every requirement:

| Level | Definition |
|---|---|
| **Business Need** | Clearly defined problem, opportunity, or objective that drives the creation of a capability or project. *(attribute on Epic)* |
| **Capability** | A broad, enduring business function or outcome. *(attribute on Epic)* |
| **Epic** | A major business deliverable/process spanning multiple requirements. |
| **Requirement** | A specific rule or condition the system must satisfy. |
| **User Story** | A user-centered statement of action for a requirement. *(attribute on Requirement)* |
| **Acceptance Criteria** | Measurable success conditions for a user story, written in **Gherkin** format. *(attribute on Requirement)* |

### Hierarchy

```
Business Need
 └─ Capability
     └─ Epic
         └─ Requirement
             ├─ User Story (As a / I want to / So that)
             └─ Acceptance Criteria (Gherkin: Given / When / Then)
```

## Output Format: Excel Workbook (.xlsx)

The deliverable is a single `.xlsx` workbook with **two tabs**: an "Epics"
summary tab and a "Requirements" detail tab. For the full per-column layout of
each tab, the styling theme, the Epics-tab COUNTIF formula, and recalculation,
see `references/excel-workbook-format.md`. Business Need lives exclusively on
the Epics tab and is not repeated on individual requirement rows.

## Canonical Values: Priority (MoSCoW)

Use **exactly** these values. No variations, abbreviations, or synonyms.

| Value | When to use |
|---|---|
| **Must Have** | Non-negotiable for the release. System won't work or be compliant without it. Default when priority is unclear. |
| **Should Have** | Important but not critical for launch. Can be deferred to fast-follow if necessary. |
| **Could Have** | Desirable nice-to-have. Minimal impact if omitted. |
| **Won't Have** | Explicitly out of scope for this release. Captured for future consideration. |

**Inference guidance:** When working from source material (documents, meeting
transcripts, chat messages, etc.), look for priority signals:

- "must", "critical", "required", "compliance", "regulatory", "blocking"
  → **Must Have**
- "important", "should", "expected", "high value" → **Should Have**
- "nice to have", "if time permits", "ideally", "bonus", "enhancement"
  → **Could Have**
- "out of scope", "not now", "future", "phase 2", "parking lot", "deferred"
  → **Won't Have**

If no signal is present, default to **Must Have**.

## Canonical Values: Status

| Value | When to use |
|---|---|
| **Draft** | Initial capture. Not yet reviewed. Default for all new requirements. |
| **Reviewed** | Reviewed by stakeholders but not formally signed off. |
| **Approved** | Formally approved and baselined. |

## BA Mode: Salesforce Engagements

BA mode turns on when the source material is a Salesforce Statement of Work
or scope document, or when the backlog feeds a Salesforce build. It changes
nothing about the hierarchy, the workbook, or the phases below. It adds
discipline on top: do not start without the SOW, sweep the SOW for every
Salesforce area it commits to, trace every requirement to a named SOW section,
prefer standard platform capability before recommending custom development,
and widen Gherkin coverage to permission and negative scenarios. The full
rules are in `references/ba-mode-salesforce.md`; read that file before Phase 1
whenever this mode applies. In BA mode also read
`references/jira-export-and-traceability.md`, since the Source column and the
gap list are mandatory there rather than situational.

## Interactive Workflow

**This is a conversation-driven skill.** Do NOT jump straight to producing
a workbook. Follow the phases below.

### Phase 1: Intake & Understanding

1. **Gather source material.** If the user provides documents (decks, PRDs,
   briefs, specs, meeting transcripts, or verbal descriptions), read and
   digest them thoroughly. There may be multiple sources.
2. **Identify candidate Epics, Capabilities, and Business Needs.**
3. **Present the proposed hierarchy to the user.**

   **MUST** use the exact indentation format shown below. Each level MUST
   be on its own line with proper indentation. Do NOT collapse the hierarchy
   into a single paragraph or run items together on one line.

   **CRITICAL FORMATTING RULE:** Use ONLY standard markdown list characters
   (`-` or `*`) for ALL hierarchy levels. Do NOT use Unicode bullet
   characters (`•`, `◦`, `▪`, etc.). The chat renderer does not recognize
   these as list markers and will collapse the hierarchy into a single
   paragraph. This is the #1 formatting failure mode for this skill.

   **Required format (follow this structure exactly):**

   ```markdown
   **Proposed Hierarchy:**

   - **Business Need:** Enable compliant, error-free pricing for
     FDA-regulated medical devices...

     - **Capability:** Automated contract pricing that selects the
       correct product price tier...

       - **Epic:** Contract-Driven Pricing Engine [Prefix: **CPE**]
         - Auto-Apply Contracted Price
         - Tiered Pricing Logic
         - Fallback to List Price
         - Audit Trail for Pricing Decisions
         - Contract Identification on Quote Creation
   ```

   Formatting rules:
   - Use standard markdown `-` for ALL hierarchy levels (Business Need,
     Capability, Epic, and requirement names). NEVER use `•` or other
     Unicode bullet characters.
   - Use **2-space indentation** per nesting level so the markdown parser
     recognizes sub-lists.
   - Insert a **blank line** before each Business Need, Capability, and
     Epic item to ensure line-break separation in the rendered output.
   - Do NOT wrap the hierarchy in a blockquote (`>`). Output it as a
     top-level markdown list.
   - **Every item on its own line.** Never concatenated into a paragraph.
   - Bold the labels: **Business Need:**, **Capability:**, **Epic:**.
   - Show the proposed prefix in brackets after the epic name.
   - Show requirement short names only, not full user stories or details.
   - If there are multiple business needs, capabilities, or epics, repeat
     the full indented structure for each.

4. **Use `ask_user_input_v0`** to confirm or adjust:
   - Are these the right epics?
   - Are any missing or should any be merged/split?
   - Is the capability grouping correct?
   - Are the epic prefixes OK?

5. Iterate until the user approves the hierarchy.

### Phase 2: Detailed Requirements Drafting

Once hierarchy is confirmed:

1. **Generate the first version of the .xlsx workbook** with both tabs
   fully populated: Gherkin acceptance criteria, inferred priorities,
   default statuses, formulas, and styling.
2. **Save and present** the workbook to the user for review.
3. **MUST include a direct download link** to the file in your response
   text (not just via `present_files`). After presenting the file, add a
   line like:

   > 📎 **[Download requirements_v1.xlsx]**. If you don't see the file,
   > open the **Artifacts panel** (top-right corner).

   This is important because users may not notice the artifacts panel,
   especially if it's minimized.
4. **Use `ask_user_input_v0`** to ask about:
   - Personas: Are the "As A" roles correct?
   - Acceptance criteria: Are the Gherkin scenarios complete?
   - Missing requirements: Anything to add?
   - Priority: Do the inferred MoSCoW values look right?
   - Assumptions: Any constraints or dependencies to note?

### Phase 3: Iteration & Refinement

1. The user may respond with:
   - Verbal edits ("change X to Y", "add a requirement for Z")
   - An edited .xlsx file they re-upload
2. Apply edits and produce a new version.
3. **If the host provides a durable shared-file editor** (for example Cowork or a
   connected ChatGPT spreadsheet), co-author within the shared file directly.
4. **Otherwise**, create versioned files (e.g.,
   `requirements_v1.xlsx`, `requirements_v2.xlsx`) for a clear revision
   trail.
5. Continue iterating until the user is satisfied.

### Phase 4: Final Delivery

1. Produce the final `.xlsx` workbook.
2. **Present the file and include a direct download link in your response.**
   Always remind the user:

   > 📎 **[Download requirements_final.xlsx]**. Open the **Artifacts
   > panel** (top-right corner) if you don't see the file.

3. Provide a brief summary:
   - Total number of requirements
   - Breakdown by epic
   - Number of epics and capabilities
   - Priority distribution (Must/Should/Could/Won't counts)
   - Any open items or assumptions flagged during the session

## Acceptance Criteria and Clarifying Questions

Acceptance criteria are written in Gherkin. For the scenario structure, a
worked example, and guidance on when and how to ask clarifying questions with
`ask_user_input_v0`, see `references/gherkin-and-questions.md`.

## Important Reminders

- **Always include a download link and artifacts panel reminder** when
  presenting files. Users often miss the artifacts panel. Every time you
  present a file, add: "📎 **[Download filename.xlsx]**. Open the
  **Artifacts panel** (top-right) if you don't see the file."
- **Always start with the interactive hierarchy review.** Never skip to
  workbook generation without confirming structure with the user first.
- **Use `ask_user_input_v0`** to present options as clickable choices whenever
  the question has bounded answers.
- **Gherkin is non-negotiable** for acceptance criteria formatting.
- **Prefix-based numbering**: auto-generate but always confirm with the user.
- **Infer priority from source material** using the signal words above.
  Default to Must Have when uncertain.
- **Business Need** lives only on the Epics tab. Do not include it on
  the Requirements tab.
- **Always read the xlsx skill** before generating the workbook.
- **Always recalculate** the workbook after generation using recalc.py.
- **Check for brand guidelines skill.** If it exists, use official Aleysian
  colors instead of the default blue/white theme.
- When the user provides vague input, infer reasonable defaults but flag
  your assumptions and ask for confirmation.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion. Full
spec in [`release-gate.md`](../_shared/release-gate.md).

1. Run prose-pass on the prose. It rewrites AI patterns and gates the result. For
   a final artifact it emits a receipt the quality gate requires.
2. Run quality-gate before you call it final.

Do not present the artifact as finished until both checks have passed.
