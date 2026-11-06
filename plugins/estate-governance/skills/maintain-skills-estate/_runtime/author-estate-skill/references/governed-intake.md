# Governed skill intake

Use this intake when a local sketch is ready to become a repository draft. The author answers the
judgment questions once. The scaffolder writes the repetitive records into `skill.yaml`,
`fixtures/governance.yaml`, and `SKILL.md`.

## The ten answers

1. **What user job does it own?** Name the user, situation, requested outcome, and completion
   condition.
2. **Why is it separate?** Name the closest skills and explain why this is not a mode, component,
   reference, adapter, alias, or merge candidate.
3. **What goes in and comes out?** List required evidence and inputs, then name the artifact,
   decision, state change, verdict, or refusal.
4. **Which prompts select it?** Record positive prompts, adjacent prompts owned by another skill,
   and negative prompts.
5. **Which skills does it need?** Separate required components, optional helpers, controls,
   upstream routers, and downstream consumers.
6. **Which capabilities does it need?** Describe the logical capability, its implementation on
   each claimed host, and the safe behavior when it is absent.
7. **What can it change or damage?** Name persistent writes, required authorization, failure
   behavior, privacy risks, and rollback.
8. **How much does it cost?** Record standing context, loaded resources, execution tokens, calls,
   time, external charges, and human intervention from a dated receipt.
9. **How efficient and useful is it?** Compare accepted results on the same fixture, host, and
   model. Count first-pass acceptance and corrections, not tokens alone.
10. **Who keeps it current?** Name the steward, maintainers, lifecycle approver, review date,
    stale external facts, and retirement path.

No receipt means `unknown`. Do not substitute an estimate. A cheaper rejected result is not an
efficiency improvement.

## Sketch, draft, and candidate

A local sketch stays outside canonical `skills/` and needs no paperwork. Use it to test an idea or
discard it. The governed path starts when the author wants the idea in the repository.

The scaffolder creates a `draft`. Drafts may retain explicit `TODO`, empty, and `unknown` values in
`fixtures/governance.yaml`.
Before promotion to `candidate`, complete the ten answers and record the collision disposition.
The disposition must be one of:

- `separate`: a distinct user job or completion condition;
- `mode`: the same job with a legitimate operating variant;
- `component`: shared construction used by more than one public entry;
- `reference`: supporting knowledge with no public trigger;
- `adapter`: one method with a host-specific implementation;
- `alias`: a temporary compatibility name with a removal condition;
- `merge`: the same job and output belongs in an existing skill.

A similarity score only opens a finding. A reviewer records the disposition. Automation never
merges, renames, deprecates, or retires a skill.

## Capability fallback

Name capabilities such as web research, repository read, document creation, browser control, or
CRM write before naming tools. For each supported host, state how the capability is supplied. If a
required capability is missing, choose one tested behavior:

- use a tested substitute;
- produce a reduced result and name what is absent;
- request one human action;
- pause without changing state;
- refuse without claiming completion.

Remove a host support claim when none of these paths is safe.

## Validation scope

Use the smallest scope that can catch the change:

| Scope | Use it for | Checks |
| --- | --- | --- |
| Changed skill | Internal prose, scripts, references, fixtures, repairs | Skill self-test and direct dependents |
| Overlap group | Job, trigger, output, role, dependency, capability, or lifecycle behavior | Changed checks plus nearest skills and routing boundaries |
| Full estate | Schema, shared policy, generators, installers, bundle machinery, scheduled audit, release candidate | All estate checks |

The first audit records existing debt. An unrelated repair does not inherit that debt as a new
failure. The repair cannot add a finding or increase an existing finding's severity.
