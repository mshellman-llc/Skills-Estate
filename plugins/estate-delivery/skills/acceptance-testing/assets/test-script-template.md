# Test script

| Field | Value |
|---|---|
| Test Script ID | TS-001 |
| Title | One sentence stating what this script proves |
| Requirement IDs | CPE-001; CPE-002 |
| Phase | SIT or UAT |
| Persona / role | From the user story's "As a" clause |
| Environment | Named sandbox from the Test Plan |
| Test data | Named dataset per the Test Plan's test data approach |
| Source | mechanical from AC / inferred from AC / authored (no AC) |
| Orphan Flag | Empty unless this script traces to no workbook requirement; then state why it exists |

## Preconditions

Derived from the Gherkin Given clauses. One numbered line per precondition.

1. Precondition from Given clause 1
2. Precondition from Given clause 2

## Steps

| Step | Action (from When) | Expected result (from Then) | Result | Defect ID |
|---|---|---|---|---|
| 1 | Action, one When clause per step where possible | Expected result that would fail if the traced requirement were broken | | |
| 2 | | | | |

For a Scenario Outline, add the Examples table below and record a result per example row.

## Execution record

| Executed by | Date | Environment | Overall result | Notes |
|---|---|---|---|---|
| | | | | |
