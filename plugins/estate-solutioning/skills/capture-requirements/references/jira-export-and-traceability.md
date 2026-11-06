# Jira export and source traceability

Two things the workbook does not do on its own: hand the requirements to a delivery
team in a form Jira will accept, and prove that every row came from somewhere.

Use this when the engagement has a signed SOW or a scope document behind the
requirements, or when the output is going into a Jira backlog rather than staying a
spreadsheet.

## Source traceability

The rule is that every requirement traces to a named place in a source document. Not
"the SOW", but the section of the SOW. A requirement whose origin cannot be named is
either an inference or an invention, and those are different things that must be
labelled differently.

Add a **Source** column to the Requirements tab when a source document exists. Three
values are legitimate:

| Value | Means | When to use it |
|---|---|---|
| `<doc>, <section>` | Stated in the source | The requirement is written down. Name the section, not just the file. |
| `inferred from <doc>, <section>` | Reasoned from the source | The source implies it. A reader could disagree and you would owe them the reasoning. |
| `open: <the question>` | Not in any source | The requirement is needed but unsupported. It is a question for the client, not a requirement yet. |

Never convert the third into the first because the backlog looked thin. An `open:` row
that reaches sprint planning gets asked about, which is the point. One that was quietly
promoted gets built.

The chain to keep intact runs source section, then requirement, then acceptance
criteria. When a requirement is split, both halves inherit the same source. When two
requirements collapse into one, keep both sources.

### The gap list

Everything the source does not settle goes on a gap list, delivered alongside the
workbook rather than inside it. Each gap carries the question to ask and who can
answer it. Categories worth separating, because they route to different people:
missing scope, conflicting statements between documents, unresolved integration
boundaries, undefined data ownership, and unstated security or access rules.

A gap list is not a failure of the capture. It is the most useful page in the
deliverable, because it is the part that changes what gets built.

## Jira export

Jira imports CSV. The workbook's Requirements tab already carries most of what an
import needs, so the export is a mapping rather than a rewrite.

| Jira field | Comes from | Notes |
|---|---|---|
| Summary | `Name` | Keep it short. Jira truncates in board view. |
| Issue Type | fixed | `Story` for requirement rows, `Epic` for the Epics tab. |
| Epic Link | `Epic` | Must match the epic's Jira key, not its display name. Resolve after the epics are created. |
| Description | `As A` + `I Want To` + `So That` | Rendered as the user story sentence, then any `Assumptions & Notes` below a horizontal rule. |
| Acceptance Criteria | `Acceptance Criteria` | Gherkin. Newlines inside the cell must survive as newlines, so quote the field in the CSV. |
| Priority | `Priority` | MoSCoW does not map to Jira's default scheme. Agree the mapping with the team before import and record it, rather than letting the importer guess. |
| Labels | `Capability` | Kebab-case it. Jira labels cannot contain spaces. |
| Story Points | left empty | Estimation belongs to the delivery team. A number invented during capture becomes an anchor nobody meant to set. |
| Reporter, Assignee, Sprint | left empty | Assigned during planning. |

Two orderings matter. Create the epics first and capture their keys, because Epic Link
needs the key rather than the name. Import in requirement-number order, so a failed
import can be resumed from the last successful row.

### What not to export

Do not export `open:` rows into the backlog. They are questions, and a question in a
backlog reads as work that was scoped. Deliver them on the gap list, and import them
once they have an answer and a source.

## Applying this without a SOW

Discovery notes, a transcript, or a deck work the same way. Name the artifact and the
part of it: a slide number, a timestamp, a heading. The requirement is that a second
person can find what you found. "From the discovery call" fails that test. "Discovery
call 2026-03-14, 22:10, on the approvals bottleneck" passes it.
