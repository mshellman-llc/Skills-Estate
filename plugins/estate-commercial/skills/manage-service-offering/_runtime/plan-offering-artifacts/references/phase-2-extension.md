# Keeping phase 2 additive

Phase 2 moves execution onto an orchestration platform. Keep `plan.py` portable so that
whichever platform is chosen, nothing built in phase 1 has to be rewritten.

## The split

```
          decides WHAT and IN WHAT ORDER          decides HOW IT RUNS
          ------------------------------          -------------------
phase 1   scripts/plan.py                         a Claude skill reads the plan
                                                  and calls builder skills in turn

phase 2   scripts/plan.py   (unchanged)           a workflow engine reads the plan
                                                  and turns each step into a node
```

All ordering, dependency, requirement, and finding logic lives in `plan.py`. The executor
holds none of it. That is the whole trick: replacing the executor changes nothing about what
gets built.

## Contract for `plan.py`

Anyone changing it must preserve all of the following, or phase 2 becomes a rewrite.

1. **Pure function of the manifest.** No network, no MCP, no filesystem beyond reading the
   manifest path it was given, no clock, no randomness. Same manifest in, same plan out.
2. **JSON out on stdout, exit 0.** `--format text` is for humans only and no caller parses it.
3. **Unusable manifest exits 2** with `{"error": ...}`. Never a partial plan.
4. **Every step is independently executable** given the manifest and the plan. A step never
   depends on state the previous step held in memory. This is what allows a workflow engine
   to run steps on separate workers, retry one, or resume after a failure.
5. **Content decisions stay out.** The planner names the builder; it never says what the
   artifact should say.
6. **Additive schema changes only.** New keys are fine. Renaming or removing a key in the
   plan output breaks every executor at once.

## What phase 2 adds, and where

| Capability | Where it lands |
|---|---|
| Persistent run state | Executor. The manifest is already the durable record |
| Retry and resume | Executor, using rule 4 |
| Scheduling and triggers | Executor |
| Parallel builds across options | Executor. `blocked_by_artifacts` already expresses what may run in parallel |
| Human approval pauses | Executor. Model on the proposal-studio approval hook, which pauses writes, commits, and deploys for a yes or no |
| Notifications | Executor |

None of these require a planner change.

## What would force a rewrite, and so needs a decision first

- Making the plan depend on live quote data rather than the manifest. If pricing must be
  read at plan time rather than recorded in the manifest, rule 1 breaks. Preferred
  alternative: a separate sync step writes quote fields into the manifest, and the planner
  stays pure.
- Making steps stateful, for example a builder that must run in the same session as its
  predecessor.
- Moving gate results out of the manifest into a platform-only store, which would make the
  playbook folder no longer self-describing.

## Current invocation adapter

Each step includes `invocation.skill` and `invocation.mode` for the current catalog.
`builder` retains the legacy value so existing executors do not lose their contract.
New executors dispatch through `invocation`; migrate an existing executor explicitly.
A null skill denotes the local template-copy operation. ROM deck preparation also
names `source_workflow`; its estimate is an input to deck rendering, not permission
to invent figures. The artifact format, scope, dependencies and gate requirements
remain unchanged. An invocation route does not establish that a host has installed
or accepted the target package.
