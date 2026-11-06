---
name: specify-implementation
description: Detailed UI, API and data-design reference used by write-feature-spec. Read for a requested implementation specification involving interfaces, persistence or interactive states. This module does not require a separate approval before an already authorized code change.
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.


# Specify implementation

Use this reference with the product specification workflow. Select the sections
needed to explain the requested feature. An API-only change does not need a UI
mockup. A request to fix a defect does not automatically require a new product
specification, an HTML file or a separate approval interview.

## Inspect the existing implementation

Read the project instructions, brief, current decisions and relevant code before
proposing changes. Follow the affected imports, callers, routes and persistence
operations far enough to identify the regression surface. Record each important
finding with its file and behavior; a filename inventory is insufficient.

Check whether a function replaces records with DELETE and INSERT, whether an
upsert preserves their IDs, and whether uniqueness or foreign keys constrain the
proposed operation. Identify required context, such as a session ID, that may be
absent in the new entry point. Inspect interactive behavior in components that
appear read-only. Identify authentication helpers and existing patterns rather
than assuming a framework or replacing them during specification.

If these findings change the proposed design, explain the correction beside
the affected behavior. Preserve unrelated defects as follow-ups unless they
block the requested result. State any relevant source that could not be read.

## Describe the feature and its states

State the user's problem, the requested outcome and the supported behavior.
Separate accepted requirements from proposed choices and open decisions. Keep
material exclusions and dependencies visible where a reader could otherwise
misunderstand the scope. Do not invent an owner, date or metric to fill a field.

For an interactive feature, describe the applicable states:

| State | What the specification explains |
| --- | --- |
| Empty or first use | Explain how the user arrives and takes the first action. Show the initial content. |
| Loading or streaming | Progress, disabled or cancellable actions and repeated submission behavior |
| Populated | Show the available data and actions. Describe the result of an action. |
| Secondary surface | Explain how a modal or panel opens and closes. Identify the context it retains. |
| Error or rejection | Give the validation message and recovery path. Explain whether input survives rejection and which permissions apply. |
| Return visit | Explain how stored state reloads and who owns the record. |

An API-only implementation may still support an interactive task. When saved records, duplicate submission or connectivity loss affect users, specify retained input, an unknown commit outcome, authorized reload on return, and record ownership even when no UI mockup is needed. Session expiry does not establish deletion or loss of persisted records; describe the actual storage lifecycle only when sourced. If both context identifiers are supplied, resolve them to the same authorized canonical context or reject the conflict. A common owner alone does not make two contexts equivalent. A retry for an existing row must retain that row's established context. Do not offer dropping one identifier as permission to move or recreate that row in another context; a transfer is a separate operation requiring explicit authorization and a specified contract.

For each relevant state, name the trigger, visible result, permitted action and
next state. Add consequential alternatives such as missing dependencies,
duplicate submissions, cancellation or concurrent edits. Mark an inapplicable
state as such only when its absence matters to the reader.

For applicable UI behavior, specify keyboard operation, focus movement and restoration, accessible names and labels, and how validation or asynchronous status is announced. State the observable acceptance checks for those behaviors using the project's accessibility requirements. A visual mockup or contrast check alone does not verify them. An API-only change can identify this as an existing caller responsibility when that boundary is supported, rather than inventing a new interface.

Use a mockup when layout or interaction needs visual explanation. Show the
existing navigation and control states. Show the actual content shape.
Mark fictional data as examples. Use the project's confirmed design
tokens or the neutral brand profile. No palette, font, navigation shell or
company identity is prescribed by this module.

A static mockup demonstrates appearance and the states it depicts. It cannot
prove dynamic behavior, latency, accessibility or production fidelity. Reuse
actual components when the project makes that practical; verify implementation
separately. Do not promise a 1:1 translation from a drawing or HTML mockup.

## Specify persistence and interfaces

For a new table, give columns, types, defaults, nullability, keys and referenced
entities. For an existing table, identify each changed field and its migration.
State the access rules and read/write actors. Include row-level security or an
equivalent mechanism when the actual platform uses one. Explain unique keys,
upsert behavior and data backfill where they affect the feature.

Prefer an additive change when it meets the requirement. Identify a destructive
migration explicitly. Identify affected records and explain compatibility with
existing callers. Describe the recovery procedure.
Specification does not authorize executing it.

For each new endpoint, specify its method and path. Define authentication and
authorization. Give the request schema with successful and error responses.
Cover invalid inputs and missing resources. Explain what happens when a
dependency is unavailable. Describe idempotency,
ordering or retry behavior when the operation needs it.

For a changed endpoint, name the changed contract and the behavior it preserves.
For example, an optional conversation ID may be added alongside an existing
session ID. Explain how callers select the context and how an older caller
continues to work. Keep field names and required literals exact.

## Bound the implementation work

When implementation planning is requested, provide a file manifest with the
operation and actual path. Describe the proposed change and why it is needed:

| Operation | Meaning |
| --- | --- |
| CREATE | A new file and its responsibility |
| UPDATE | The exact behavior changed in an existing file |
| DELETE | Identify what replaces the removed file and which consumers change. |
| READ | A source used for design that needs no implementation change |
| MIGRATION | A schema or data transition and its recovery conditions |
| CONFIG | A dependency, environment variable or service setting |

Include affected importers and callers when they need changes or regression
checks. A preliminary manifest is a plan, not a guarantee that investigation
cannot reveal another necessary file. Update it when the implementation scope
changes and surface a material decision. Preserve the user's existing approval
and release boundaries; a file count creates no additional approval gate.

## Persistence completion check

Before delivering a specification that saves records, explicitly state how a later authorized read reloads the durable record and how record ownership and context access are checked. Cover a fresh visit as well as recovery immediately after a timeout. If the existing read path or lifecycle is unknown, name it as an uninspected dependency and specify the observable readback requirement; do not invent a new endpoint or deletion policy as established behavior. Include an acceptance case for that later read, stable identity and denied access. This requirement describes data behavior and does not require a UI mockup.

## Make acceptance executable

For each criterion, name the initiating action and observable result. Specify
the exact verification method. State the expected behavior for the main path and material
failures. A screenshot can prove a rendered state; persistence needs a record
readback or an equivalent test. A schema check cannot prove a complete user task.

Select test and build commands from the current repository's documentation and
package scripts. Do not prescribe npm, TypeScript, Vitest or Next.js when the
project does not use them. Keep a planned verification distinct from a command
that actually ran and a result inspected at the intended destination.

Before delivering, check the specification against the supplied request and
the inspected code. Verify that states, interfaces, data changes, file scope
and criteria agree. Identify a material unresolved decision beside the section
it affects. Ask only for a decision that blocks useful work; continue the
supported portions. Never invent an approval or imply the specification was
implemented.

## Deliver in the requested form

Use the project's existing document or work-item format. A self-contained HTML
specification can embed its styles and assets with rendered mockups. A Markdown,
editable document or issue may suit the task better. Do not introduce a font
CDN or another network dependency into an otherwise self-contained artifact.

Retain supporting notes and evidence when needed for recovery or the user's
verification requirements. Run the applicable shared release checks, including
writing review and visual inspection for a designed document. Implementation
can proceed within the authorization already granted; request a remaining
approval only when the actual project or action requires one.
