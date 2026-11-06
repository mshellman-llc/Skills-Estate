# Gherkin Acceptance Criteria and Clarifying Questions

## Gherkin Acceptance Criteria Guidelines

Each requirement's acceptance criteria should follow this structure:

```gherkin
Scenario: <Short descriptive title>
  Given <precondition>
  When <action or trigger>
  Then <expected outcome>
  And <additional outcome> (optional)
```

**Best practices:**

- Write **multiple scenarios** per requirement when there are distinct paths
  (happy path, edge cases, error handling, fallback logic).
- Keep each scenario focused on one behavior.
- Use concrete, testable language. Avoid vague terms like "appropriate" or
  "correct" without defining what that means.
- Reference specific data, roles, or system states where possible.
- Always include a **Scenario:** title line before each Given/When/Then block.
- Write `Given` preconditions concrete and reproducible enough to be stood up as
  test data, and make the acting persona (the user story's **As A** / the scenario
  actor) a real, testable role — so the criteria can be validated against a running
  system by a person or an automated QA agent, not just read.

**Example:**

```gherkin
Scenario: Contract price applied for active contract
  Given the account "Metro General Hospital" has an active contract
    for "CardioTrack X200 Monitoring Kit"
  And the contract specifies Tier 2 pricing (501–1,500 units)
  When a sales specialist creates a new quote
  Then the system must automatically apply the Tier 2 contracted price
  And the quote line item must display the Contract ID, Tier Applied,
    and Effective Date

Scenario: Fallback to list price when no contract exists
  Given the account "Sunrise Clinic" has no active contract
    for "CardioTrack X200 Monitoring Kit"
  When a sales specialist creates a new quote
  Then the system must apply the standard list price
  And no contract reference fields should be populated
```

## Clarifying Question Guidelines

Throughout the conversation, use `ask_user_input_v0` to ask focused questions.
Good times to ask:

- **Ambiguous scope**: "Should this epic also cover [related area]?"
- **Missing personas**: "Who are the primary users?"
- **Edge cases**: "What should happen when [edge case]?"
- **Priority disputes**: "The transcript says 'nice to have' but it seems
  compliance-related. Which priority fits?"
- **Integration boundaries**: "Is the integration in-scope or a separate epic?"

Keep questions concise. Prefer single-select or multi-select options when
the choices are bounded. Use open-ended follow-up only when truly needed.
