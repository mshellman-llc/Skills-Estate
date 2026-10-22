# Test script format and Gherkin mapping

The test script is the unit of traceability. Every script declares the requirement IDs it
covers, using the IDs exactly as they appear in the requirements workbook from
estate-requirements-capture (prefix plus number, for example `CPE-001`). Never invent an
ID and never paraphrase one; the gate script matches strings, not intentions.

## Script fields

Every script carries all of these. A field you cannot fill is a known unknown with an owner,
not a dropped row.

| Field | Rule |
|---|---|
| Test Script ID | Stable, never reused. `TS-###`, numbered in creation order. If a script is retired, its ID retires with it. |
| Title | What the script proves, in one sentence. "Tier boundary applies the correct price at exactly 100 units", not "Test pricing". |
| Requirement IDs | One or more workbook requirement IDs, semicolon separated in CSV. This is the traceability field the gate reads. |
| Phase | `SIT` or `UAT`. SIT scripts prove the system holds together; UAT scripts prove a business user can do their job. The same requirement often needs one of each. |
| Persona / role | Who executes, as a role from the user story's "As a" clause, not a person's name. |
| Environment | The named sandbox or environment from the Test Plan. |
| Preconditions | System state and data that must exist before step 1. Derived from the Gherkin Given. |
| Test data | What records the script needs and where they come from, per the Test Plan's test data approach. Name the dataset; "some accounts" is not test data. |
| Steps | Numbered rows of Action and Expected Result. See the mapping below. |
| Status | `Not started`, `In progress`, `Passed`, `Failed`, `Blocked`. Lives in the UAT tracker; the script document points at the tracker rather than duplicating it. |
| Source | Where the steps came from: `mechanical from AC`, `inferred from AC`, or `authored (no AC)`. See below. |
| Orphan Flag | Empty for a traced script. For a script that traces to no requirement in the workbook, a short note saying why it exists. See orphans. |

## Mapping Gherkin acceptance criteria to steps

The requirements workbook carries acceptance criteria in Gherkin. Where the Gherkin is
complete, the conversion is mechanical, and mechanical is the goal: a step a model authored
freely is a step a reviewer has to re-derive, while a step lifted from a co-signed AC
inherits its authority.

| Gherkin clause | Becomes |
|---|---|
| `Given` | Preconditions and test data setup. Each Given clause is a numbered precondition. |
| `When` | Action steps, in clause order. One When clause per step where possible. |
| `Then` (and `And` after Then) | Expected results, attached to the step that triggers them. |
| `Scenario` | One test script, or one step group within a script when scenarios are trivially small. Record which scenarios each script covers. |
| `Scenario Outline` + Examples | One script with a data table: the steps run once per example row, and the tracker records a result per row. |

Mark the script's Source field `mechanical from AC` only when every step traces to a clause.
When you had to fill in what the AC left unsaid (navigation, record names, boundary values),
mark it `inferred from AC` and flag the inferred steps inline with `[INFERRED: basis]`. When
a requirement has no usable AC, author the script, mark it `authored (no AC)`, and raise the
missing AC as an open question routed back through estate-requirements-capture; do not
quietly fix the requirement inside a test script.

## Coverage rules

- Every requirement gets at least one script. Must Have requirements get at least one UAT
  script executed by the client persona; SIT-only coverage of a Must Have is itself a
  finding to surface.
- A requirement whose scripts cannot be written yet (feature lands in a later sprint,
  environment not provisioned) goes on the named gap list with an owner, a reason, and a
  resolve-by date. That is the only acceptable form of non-coverage.
- One script may cover several requirements when they are exercised by one flow. That is
  fine; list every ID. What is not fine is one vague script "covering" ten requirements it
  never actually asserts on. Each traced requirement must have at least one expected result
  that would fail if that requirement were broken.

## Orphan scripts

A script that traces to no workbook requirement, or to an ID the workbook does not contain,
is an orphan. Orphans are usually one of: scope drift (someone built and is now testing
something never captured), a regression script inherited from the client, or a typo in the
ID. Fix typos. Keep legitimate orphans, but flag them in the Orphan Flag field with the
reason, and route the scope-drift ones to estate-delivery-status so the drift is visible
in status reporting, not buried in a test asset. The gate fails on any unflagged orphan.

## Test data approach

The Test Plan owns the test data approach; the scripts consume it. Summarize it once (data
sources, masking rules, refresh cadence, who provisions) and have each script name its
dataset. If the Test Plan has no test data section, that is a named gap against the Design
phase, owned by the Solution Lead, blocking SIT start.
