---
name: capture-requirements
description: 'Capture and structure business requirements in the Estate approved format: epics, capabilities, business needs, user stories, and Gherkin acceptance criteria, delivered as a branded two-tab Excel workbook. Use to define, write, organize, or refine requirements, to extract them from an uploaded deck, PRD, brief, spec, or transcript, or to turn a Salesforce SOW into a backlog (BA mode: analyze this SOW, SOW to backlog, Salesforce BA). Triggers on capture requirements, write user stories, define epics, requirements gathering, BRD, acceptance criteria, requirements CSV. Always read the host spreadsheet skill before generating the workbook. Grading sprint readiness is refine-backlog.'
---


# Capture requirements

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [`readout-brief.md`](_runtime/writing-diagnostics/references/registers/readout-brief.md). Inputs, not a final pass.**

## Purpose

This skill guides the agent through an interactive, structured conversation to
capture business requirements as the Estate's approved delivery matrix.
The final output is a **branded Excel workbook (.xlsx)** with two tabs, ready
for client presentation and downstream use by AI agents or development teams.

## Reference files

Detailed tables live in `references/` to keep this file lean. Read the relevant
one when you reach that part of the work:

- `references/excel-workbook-format.md`: the per-column tables for both tabs,
  the styling roles, which come from the selected profile, the Epics-tab formula, and
  recalculation.
- `references/gherkin-and-questions.md`: Gherkin acceptance-criteria structure
  with a worked example, plus clarifying-question guidance.
- `references/jira-export-and-traceability.md`: the Source column and the
  three legitimate values for it, the gap list, and the workbook-to-Jira field
  mapping. Read it when the requirements come from a SOW or scope document, or
  when the output goes into a Jira backlog rather than staying a spreadsheet.
- `references/ba-mode-salesforce.md`: the BA mode rules for Salesforce
  engagements. Read it whenever BA mode is on (see below).

## Before Generating the Workbook

**Read the spreadsheet skill your host provides before writing any openpyxl code.**
Look for `xlsx`, `spreadsheets`, or the equivalent in the available skills list.
Follow its guidelines for formula construction, recalculation, error
checking, and code style. Use its `scripts/recalc.py` to recalculate
formulas after generating the workbook.

Take the workbook's colours and font from the brand profile the build card
selects: an explicitly named profile, then the project's brand file, then the
estate neutral profile. With no confirmed profile the workbook uses the neutral
profile. The reference file maps each workbook element to a profile role.

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
or another scope document, or when the backlog feeds a Salesforce build. It changes
nothing about the hierarchy, the workbook, or the phases below. It adds
discipline on top: do not start without the SOW, sweep the SOW for every
Salesforce area it commits to, trace every requirement to a named SOW section,
prefer standard platform capability before recommending custom development,
and widen Gherkin coverage to permission and negative scenarios. The full
rules are in `references/ba-mode-salesforce.md`; read that file before Phase 1
whenever this mode applies. In BA mode also read
`references/jira-export-and-traceability.md`, since that mode always needs a
Source value on every requirement and a list of gaps.

## Interactive Workflow

**This is a conversation-driven skill.** Do NOT jump straight to producing
a workbook. Follow the phases below.

### Phase 1: Intake & Understanding

1. **Gather source material.** If the user provides documents (decks, PRDs,
   briefs, specs, meeting transcripts, or verbal descriptions), read and
   digest them thoroughly. There may be multiple sources.
2. **Identify candidate Epics, Capabilities, and Business Needs.**
3. **Present the proposed hierarchy to the user.**

   Put each level on its own line and show the nesting by indentation
   alone. A collapsed paragraph hides the structure the user is checking.
   Use standard Markdown list markers (`-`) for every level. A Unicode
   bullet such as `•` is not a list marker to the chat renderer, which
   then runs the hierarchy together into one paragraph.

   ```markdown
   Proposed hierarchy

   - Business need: Enable compliant, error-free pricing for
     regulated medical devices...

     - Capability: Automated contract pricing that selects the
       correct product price tier...

       - Epic: Contract-driven pricing engine [prefix CPE]
         - Auto-apply contracted price
         - Tiered pricing logic
         - Fallback to list price
         - Audit trail for pricing decisions
         - Contract identification on quote creation
   ```

   Formatting rules:
   - Indent two spaces per level so the Markdown parser nests the lists.
   - Leave a blank line before each business need, capability and epic.
   - Write the level labels (Business need, Capability, Epic) as plain
     text. The indentation carries the hierarchy, so the labels need no bold.
   - Keep the hierarchy out of a blockquote.
   - Show the proposed prefix in brackets after the epic name.
   - Show requirement short names only, not full user stories or details.
   - Repeat the indented structure for each further business need,
     capability or epic.

4. Ask the user to confirm or adjust the hierarchy. When the host offers a
   structured question tool, such as `ask_user_input_v0` on claude.ai, use it
   for these bounded choices; otherwise ask in plain text with numbered options:
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
3. Tell the user where the file is, in the form the host supports. On a
   host with an Artifacts panel, such as claude.ai, give a direct download
   link in the reply as well as the presented file, and say the file is also
   in the Artifacts panel. In Claude Code, Codex or another host with a file
   system, give the saved path. Write the line in plain text, for example
   "Download requirements_v1.xlsx", with no emoji.
4. Ask about the following, with the host's structured question tool when it
   has one and in plain text otherwise:
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
6. When the team needs to know which stories can enter a sprint, hand the
   Requirements tab to `refine-backlog`. It grades readiness and proposes
   splits and estimates; the stories themselves change here, in this workbook,
   so Requirement Numbers and Status stay canonical. See
   `../_shared/planning-chain.md`.

### Phase 4: Final Delivery

1. Produce the final `.xlsx` workbook.
2. Present the file and say where it is, as in Phase 2: a download link
   plus a mention of the Artifacts panel where the host has one, otherwise the saved path.

3. Provide a brief summary:
   - Total number of requirements
   - Breakdown by epic
   - Number of epics and capabilities
   - Priority distribution (Must/Should/Could/Won't counts)
   - Any open items or assumptions flagged during the session

## Acceptance Criteria and Clarifying Questions

Acceptance criteria are written in Gherkin. For the scenario structure, a
worked example, and guidance on when and how to ask clarifying questions, see
`references/gherkin-and-questions.md`.

## Important Reminders

- **Say where each presented file is** in the host's own terms: a download
  link and the Artifacts panel on claude.ai, the saved path in Claude Code or
  Codex. Write it without emoji.
- **Always start with the interactive hierarchy review.** Never skip to
  workbook generation without confirming structure with the user first.
- **Offer bounded choices as options**: through a structured question tool
  if one exists, or else as a numbered list in plain text.
- **Gherkin is non-negotiable** for acceptance criteria formatting.
- **Prefix-based numbering**: auto-generate but always confirm with the user.
- **Infer priority from source material** using the signal words above.
  Use Must Have when the signal is unclear.
- **Business Need** lives only on the Epics tab. Do not include it on
  the Requirements tab.
- **Read the xlsx skill first.** The workbook code follows its rules.
- **Always recalculate** the workbook after generation using recalc.py.
- **Use the selected brand profile for colours and font.** Without a confirmed
  profile, use the neutral profile.
- When the user provides vague input, infer reasonable defaults but flag
  your assumptions and ask for confirmation.

## Release gate (required)

Before you deliver, run the gate. This step is required. Full
spec in [`release-gate.md`](_shared/release-gate.md).

1. Apply review-writing to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run `brand_check.py` on the saved workbook. It reads the fills, font
   colours, borders and fonts of the cell formats in use and checks them
   against the selected profile.
3. Run review-deliverable before you call it final.

Do not present the artifact as finished until both checks have passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
