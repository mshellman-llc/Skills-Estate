---
name: design-process
description: 'Work with a business or operational process in two modes: document it as an SOP, or optimize it. Use Document mode to formalize a process into an SOP with purpose, scope, a RACI matrix, process flow, step detail, exceptions, and metrics for a handoff, audit, onboarding, or to standardize inconsistent work. Use Optimize mode to make a process, workflow, pipeline, or hand-off faster, cheaper, or more reliable. Triggers on write an SOP, document this process, build a RACI, this process is slow, too many steps or approvals, streamline this, remove the bottleneck, cut cycle time, reduce hand-offs. Not for one-off project plans, org charts, product requirements, incident runbooks, or code and query performance tuning.'
---


# Design process

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [`readout-brief.md`](_runtime/writing-diagnostics/references/registers/readout-brief.md). Inputs, not a final pass.**

Two modes over one subject. Document a process as a repeatable SOP, or analyze an
existing process and recommend improvements. Pick the mode from the request: a
formalize, standardize, or write-it-down ask is Document; a make-it-faster,
cheaper, or more-reliable ask is Optimize. When both are wanted, document the
current state first, then optimize from it.

## Conventions both modes hold

- Do not invent owners, names, dates, metrics, targets, durations, or cadence. If
  a field is not supplied, write `not captured`. If a section has no content,
  write `none`.
- Surface unresolved decisions rather than papering over them. Where an owner, a
  trigger, or a rule is unsettled, write `open: <the question>` instead of a
  fabricated answer.
- Distinguish the current state you were told from any redesign you propose. Never
  present a recommendation as if it were observed fact.
- Work with whatever tools are connected, and never assume a specific product is
  present. Fall back to the user's description and say so.

---

## Mode: Document (the SOP)

Turn a business process into a complete, repeatable standard operating procedure.

Take whatever the user has: a process name, a rough description, pasted docs, or
meeting notes. If the description is thin, ask targeted questions first, the
trigger, owner, the steps in order, who does each, what each step produces, the
exceptions, and how success is measured. Do not stall on missing detail; capture
what exists and mark the rest.

Two rules carry this mode:

- **The exceptions are the point.** "Usually X, but sometimes Y" is the most
  valuable content in the document. Capture it explicitly, do not smooth it into
  the happy path.
- **RACI integrity: exactly one Accountable per step.** If two names are given as
  accountable, flag it as `open: single accountable owner unresolved`.

Produce the SOP in this structure. Keep placeholder brackets only where the user
supplied a value; otherwise apply the conventions above.

```markdown
## Process Document: [Process Name]
**Owner:** [Person/Team] | **Last Updated:** [Date] | **Review Cadence:** [Quarterly / Annually / not captured]

### Purpose
[Why this process exists and what it accomplishes]

### Scope
[What is included and what is explicitly excluded]

### RACI Matrix
| Step | Responsible | Accountable | Consulted | Informed |
|------|-------------|-------------|-----------|----------|
| [Step] | [Who does the work] | [Single owner] | [Who to ask] | [Who to tell] |

### Process Flow
[Step-by-step sequence, or an ASCII flowchart if branching matters]

### Detailed Steps

#### Step 1: [Name]
- **Who:** [Role]
- **When:** [Trigger or timing]
- **How:** [Instructions specific enough to follow without asking]
- **Output:** [What this step produces]

#### Step 2: [Name]
[Same format]

### Exceptions and Edge Cases
| Scenario | What to Do |
|----------|------------|
| [Exception] | [How to handle it] |

### Metrics
| Metric | Target | How to Measure |
|--------|--------|----------------|
| [Metric] | [Target] | [Method] |

### Related Documents
- [Related process or policy, or `none`]
```

---

## Mode: Optimize

Analyze an existing process and recommend improvements. Lead with the answer: the
biggest constraint and what to change, then the supporting map.

One rule carries this mode: **impact estimates must trace to supplied numbers.**
Step times, volumes, error rates, and costs come only from what the user gives you
or from records they point to. If cycle time or cost is not captured, state the
direction of the change, faster or fewer hand-offs, and mark the magnitude `not
captured` rather than fabricating a percentage. A plausible-looking made-up
duration or cost is a defect.

### 1. Map the current state
- List every step, decision point, and hand-off in order.
- For each step capture owner, trigger, duration, and whether it is manual,
  automated, or an approval. Use `not captured` for anything unknown.
- Mark queue and wait time between steps separately from work time.

### 2. Find the waste
- Waiting: time in queues or waiting for approvals.
- Rework: steps that fail and get redone; note the failure trigger.
- Hand-offs: each one is a delay and failure point; count them.
- Over-processing: steps that add no value to the outcome.
- Manual work: tasks a rule or integration could do instead.

Name the single largest constraint. Everything else is secondary until it is fixed.

### 3. Design the future state
- Eliminate steps that add no value.
- Automate manual steps where a clear rule exists.
- Reduce hand-offs; merge steps under one owner where possible.
- Parallelize independent steps.
- Add checkpoints, not gates: verify without blocking flow.

### 4. Quantify the impact
- Time saved per cycle, from captured durations, else `not captured`.
- Error or rework rate change.
- Cost change and load on the people involved.
- State the assumptions behind each figure in one line.

Return, in chat by default: the headline constraint and top recommendation; a
before/after step comparison with hand-off and step counts for each; prioritized
recommendations, each with expected impact and effort; open questions and figures
marked `not captured`; and an implementation order, quick wins first.

---

## Delivery

Default to returning the result inline in the conversation as Markdown. Only write
a file if the user asks and a writable working directory is available; on a hosted
or read-only surface where a write fails, fall back to inline output without
stopping. Never make the deliverable depend on a file write succeeding.

## If tools are connected

Optional, only when the capability is actually available, never block on it. A
connected knowledge base: search first for an existing version to update rather
than duplicate, then offer to publish. A connected task tracker: link related
work and, if the user wants, open tasks for `open:` items and improvement actions.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion. Full
spec in [`release-gate.md`](_shared/release-gate.md).

1. Apply review-writing to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run review-deliverable before you call it final.

Do not present the artifact as finished until both checks have passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
