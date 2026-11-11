---
name: sf-deploy-engine
description: 'Operate an sf-deploy-engine Salesforce CI/CD pipeline: engine-managed validation and deploy to pipeline environments (preprod, staging, production), selective and multi-source releases, rollback by ticket or SHA, re-validation, freeze recovery, pause/resume, route topology and hotfix entry gates, smart test skip, pre/post-deploy Apex hooks, GitHub or Jira ticket providers, and provisioning a new engine instance. Use whenever the repo has a pipeline.yml. Trigger on: ''deploy to prod'', ''promote'', ''release'', ''cut a release'', ''what needs to ship'', ''rollback'', ''revert ticket'', ''retry'', ''engine status'', ''validation failed'', ''environment frozen'', ''pause the engine'', ''revalidate'', pipeline.yml, deploy engine, deploy_hooks, back_merge, entry_requires_label, smart_tests, provision the engine, engine init. Also when a PR targets an environment branch. Do NOT trigger for the local loop against your own dev sandbox — worktrees, feature branches, local deploys, git hooks — that is sf-delivery-standards.'
metadata:
  canon_exempt: 'engineering-doc'
  canon_exempt_reason: 'auth contract, API payloads and the refusal matrix must be in hand before the agent acts on an org'
---

# sf-deploy-engine — operating the pipeline

The engine is an always-on orchestrator that owns Salesforce deployments to
**pipeline environments** through GitHub webhooks, one single-threaded FSM worker
per environment, and strict git-to-org synchronization. It takes over at the
first environment branch and owns everything upward.

**This skill starts at the PR into an environment branch.** Everything before
that — the ticket, the worktree, the local dry run, the deploy to your own dev
sandbox, the git and agent lifecycle hooks that enforce it — is `sf-delivery-standards`,
and that skill works the same whether or not an engine sits above it. Do not
duplicate its rules here and do not answer local-loop questions from this skill.

**This is a layer, not a fork.** The engine ships its own two guards
(`scripts/init.sh` installs them), which read `pipeline.yml` and nothing else.
They add refusals on top of the local-loop stack, read none of its config, and
write none of its files. **An agent working the local loop needs to know nothing
about this layer and change nothing to accommodate it.** If you find yourself
about to edit `sf-delivery-standards` to make something here work, stop — that
is the seam being crossed, and the answer is a rule in this skill's own hooks.

**What the guards bind, stated precisely.** A Claude or Codex hook fires on a tool
call the *model* makes. A command a human types in a terminal or runs from an IDE
never passes through the harness. So the true claim is *"an agent cannot deploy
to a pipeline org through this session"* — **not** *"the pipeline orgs are
protected."* The controls that bind a human are branch protection and the org's
own permissions. Do not let anyone read more into a green `doctor.sh` than that.

---

## Sub-commands

| Command | Does |
|---|---|
| `/sf-deploy-engine` (no args) | Operate the pipeline. The default: status, promote, release, rollback, retry, revalidate. |
| `/sf-deploy-engine doctor` | Is this pipeline actually healthy? Read-only. `scripts/doctor.sh` |
| `/sf-deploy-engine init` | Point an existing repo at an already-running engine. `scripts/init.sh` |
| `/sf-deploy-engine provision` | Stand up a **new** engine instance: GCP, GitHub App, secrets, SSO. [references/provisioning.md](references/provisioning.md) |

Route on the argument: *status / promote / release / rollback / retry / frozen /
revalidate / what needs to ship* → operate. *doctor / audit / health / is the
engine ok / drift* → doctor. *init / onboard this repo / point at the engine* →
init. *provision / new instance / new client / GCP / GitHub App / rotate keys /
add an environment / build the vsix* → provisioning.

Provisioning is rare and one-time-per-client. It lives in a reference so it never
loads during a deploy.

---

## The boundary — get this right before anything else

| Where | Who deploys | How |
|---|---|---|
| Your dev sandbox | **You**, directly | `sf project deploy start`, governed by `sf-delivery-standards` |
| Any environment in `pipeline.yml` | **The engine**, exclusively | PR → engine validates → merge → engine deploys |

**Never run `sf project deploy` against a pipeline environment's org, for any
reason, including to fix something.** A manual deploy desyncs `deployed/<branch>`
from the org and the engine has no way to detect it. The recovery is Pause →
reconcile git and the tag by hand → Resume, and it is worse than whatever you
were trying to shortcut.

The two exceptions the schema allows are both narrow. `tier: sandbox` rows are
registered for **visibility only** — they produce the Dev Sandboxes board column
and are a legal `/api/release` source into a route entry point, but get no
worker, no `deployed/<branch>` tag and no engine-driven deploy. And `freeze:
advisory` relaxes the freeze gate for low-stakes tiers. Neither makes a sandbox
engine-managed. See `docs/decisions/sandboxes-are-environments.md` in the engine
repo before proposing otherwise.

---

## Core model

| Ref | Means | Moved by |
|---|---|---|
| Branch HEAD (`preprod`) | **Desired** org state | Merged PRs |
| Tag `deployed/<branch>` | **Actual** org state | The engine only |

Deltas are computed `deployed/<branch>` → SHA with sfdx-git-delta. A failed
deploy leaves the tag unmoved, so git still describes the org *at the tag* and
the gap stays queryable.

```
SETTLED → DEPLOYING → SETTLED (tag advanced)
             ↓ failure
          FROZEN → retry → DEPLOYING
             ↓ rollback (the revert lands as a push)
          DEPLOYING → SETTLED
```

Quick deploy (skip the 15-minute test run on merge) is eligible only when all
three hold: the validation ran on the same SHA, the org state is unchanged (the
tag has not moved), and the validation is under 10 days old. Any miss falls back
to a full deploy — that fallback is the design, not a bug.

**Fail-closed by construction:** engine down → required checks never go green →
nothing merges → nothing breaks.

---

## Authentication — do this first, once

`/` and `/api/*` are locked to Google Workspace SSO. **A bare `curl` against
`/api/*` returns 401 or 503, and older runbooks that show unauthenticated curl
are wrong.** Browser cookies do not reach a bash process and the VS Code token
lives in the OS keychain, so terminal callers mint their own:

1. Open `$ENGINE_URL/auth/login?redirect=cli` in a browser and sign in.
2. Run the command the page prints. It writes `~/.config/sf-deploy-engine/token`, mode 600.
3. Re-run that login when a call reports 401. The token lasts 30 days.

`scripts/engine.sh` reads that file (or `SFDE_TOKEN`) and sends
`Authorization: Bearer`. Use it rather than hand-rolled curl — the release and
rollback payloads are the fiddly part.

```bash
export ENGINE_URL=$(grep '^engine_url:' pipeline.yml | awk '{print $2}')
scripts/engine.sh status
```

**Everything 503s but `/health`?** In always-on that is the SSO gate failing
*closed* because `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` /
`SESSION_SECRET` are unset on the service. That is a provisioning fix, not an
auth fix. Under `EXECUTION_MODE=scale-to-zero` a different set of endpoints 503s
by design — see [references/provisioning.md](references/provisioning.md).

---

## Daily operations

Full payloads, response shapes and every endpoint:
[references/operations.md](references/operations.md).

### Where does everything stand

```bash
scripts/engine.sh status          # FSM state, in-flight item and queue per env
scripts/doctor.sh                 # the same, plus tag drift, config drift, auth, webhook health
```

`SETTLED` idle · `DEPLOYING` in progress · `FROZEN` failed, waiting on a human.

### What is ready to ship

```bash
scripts/doctor.sh --ready         # unpromoted merge commits per promotion edge
```

Promotions are cherry-picks, so a promoted merge gets a new SHA downstream and
`git log main..preprod` reports it as pending forever. This compares by
**patch-equivalence** of each merge's first-parent diff, which is what actually
drops shipped work off the list.

### Promote

Bulk, everything on the upstream branch:

```bash
gh pr create --base main --head preprod --title "RELEASE: preprod -> main ($(date +%F))"
```

Merge commit, never squash. Never delete the upstream branch.

Selective, specific tickets — this is what the dashboard's release builder does:

```bash
scripts/engine.sh release --from preprod GH-397 GH-401 ORG64-42
```

Ticket identifiers are provider-aware: `GH-397`, a Jira key like `ORG64-42`, the
canonical `jira:ORG64-42`, or a bare issue number. An identifier no **configured**
provider recognises is rejected rather than guessed at.

One release can span several sources — different dev sandboxes, or a sandbox and
preprod together. `--from` applies to every ticket after it, until the next one:

```bash
scripts/engine.sh release --to preprod --from stevenc2 GH-397 --from meg-dev GH-401
```

**`--from` is required** — there is no default source, and the API rejects a flat
ticket list without one. `--to` *is* optional: it defaults to the target every
selected source agrees on, and with no shared target the request is refused
rather than one being picked.

Two refusals worth recognising, both deliberate:

- *"No merged PR delivering GH-397 found on \<src\>"* — a release cherry-picks
  merge commits. Work pushed straight to a branch shows on the board (which reads
  commit messages) but is not releasable until it lands as a merge.
- An **unattributed commit** check fails the release when a candidate merge
  carries work no selected ticket accounts for. That is the ride-along guard;
  read what it names before overriding.

### Roll back

```bash
scripts/engine.sh rollback --env main --ticket GH-397        # resolves the deploy that carried it
scripts/engine.sh rollback --env main --sha <merge-commit>   # or name the merge yourself
```

`--mode pr` (default) opens a revert PR so the inverse deployment is validated
first. `--mode direct` pushes the revert straight to the branch — emergencies
only. `git revert -m 1` produces a diff sgd turns into the exact inverse package:
modified components at prior versions in `package.xml`, added components in
`destructiveChanges.xml`.

**Re-land pattern:** never reuse the original branch. New branch, `git revert
<revert-sha>`, add the fix, new PR.

### Re-validate a PR

```bash
scripts/engine.sh revalidate --pr 412
```

Re-runs validation at the PR's live head SHA, clears the recorded failure and
bypasses the attempt cap — a human asking is explicit intent. This replaces the
old empty-commit workaround.

### Recover a freeze

```bash
scripts/engine.sh status                  # read freezeReason first
scripts/engine.sh retry preprod           # re-enqueue the deploy at branch HEAD
```

Retry only works on a `FROZEN` environment. If the cause is bad metadata rather
than a transient failure, roll back instead of retrying into the same wall.

### Pause for maintenance

Only when git has to be reconciled to the org by hand:

```bash
scripts/engine.sh pause
git tag -f deployed/main <sha> && git push origin deployed/main --force
scripts/engine.sh resume
```

Webhooks are acknowledged but not processed while paused. Tell the team — a
paused engine looks exactly like a quiet one.

---

## What the engine reacts to

| GitHub event | Engine reaction |
|---|---|
| `pull_request` opened/synchronize → env branch | Enqueue validation |
| `push` to env branch | Enqueue deploy |
| `pull_request` closed unmerged | Cancel queued validations; abandon an in-flight one, discarding its result |
| `pull_request` reopened | Re-enqueue validation |
| Issue label `express` | Auto-merge after validation, auto-promote after deploy |
| Label `qa:passed` / `qa:failed` | Update board state |
| Label `destructive-approved` | Satisfies the destructive gate |
| Label `run-tests` | Forces tests even when smart-test skip would apply |
| Route entry label | Permits a direct PR into a gated entry point |

**Labels the engine writes are write-only.** `env:*`, `deploy:failed` and
`rolled-back` exist so a human browsing GitHub can see where things are; the
engine never reads them back as truth. Delivery state comes from the event log.
The labels above that express **human intent** are read, and should be.

### Test level per tier

- **Pipeline environments** — the configured `test_level`, usually
  `RunLocalTests`, downgraded to `NoTestRun` only when `smart_tests` proves the
  whole delta is safe metadata. No partial trust: provably safe, or the full suite.
- **Production** — Salesforce forbids `NoTestRun` outright. Batch promotions into
  releases so N tickets cost one 15-minute run instead of N of them.

`smart_tests` never applies to a `production: true` environment, and any unsafe
type in the delta (ApexClass, CustomObject, Flow, LWC) means full tests. Config
and the safe-type list: [references/pipeline-config.md](references/pipeline-config.md).

---

## Route topology

`routes:` replaced `promotions:`. A config with only `promotions:` still loads —
it is translated into a synthetic `standard` route and warns — but it cannot
express hotfix entry points or back-merge, so migrate it.

- A **forward edge** is a consecutive pair on any route's `path`. Promote-only,
  by cherry-pick or PR. The union of all forward edges must be acyclic.
- **`entry_requires_label`** gates direct PRs into a route's entry point. Engine-owned
  head branches (`release/`, `express/`, `backmerge/`, `revert/`) and bulk
  promotion from an upstream env's branch are exempt — the gate only catches a
  fresh direct entry, which is exactly the hotfix case it exists for.
- **`back_merge`** targets fire after a successful deploy to a route's terminal
  env and must be strictly upstream, so a back-merge can never introduce a
  forward promotion path.

Full semantics and worked configs:
[references/pipeline-config.md](references/pipeline-config.md).

---

## Pre/post-deploy Apex hooks

Repo-versioned anonymous Apex the engine runs **around** a deploy, for imperative
org actions metadata cannot express. Off unless `deploy_hooks.enabled`.

```
deploy-hooks/
  pre/   01-disable-automation.apex
  post/  123-delete-orphan-flow-versions.apex
```

Scripts live outside `force-app/` so sgd never treats them as metadata. They are
**delta-driven and run-once**: discovered from the same `deployed/<branch>` → SHA
window as metadata, so a script appears in exactly one deploy's window. Add it in
the same PR as the change it supports.

```
compute delta → gates → [PRE] → sf deploy → [POST] → advance tag
```

The tag advances **last** — it means "org fully reconciled, hooks included." A
pre-hook failure freezes with nothing deployed. A post-hook failure freezes with
the tag **not** advanced, so Retry re-runs deploy + post: **write hooks
idempotently.** Hooks never run during validation — anonymous Apex has no
`checkOnly`, so a hooks-only PR validates trivially green and then runs its
scripts on merge with no metadata deploy at all.

---

## Ticket providers

Absent `tickets:` means GitHub only, exactly as before providers existed.

- `extract` — regexes over commit and PR text. Free, read-only. Once a tracker
  has ever been used, leave it on permanently: commits written in that period
  name its tickets forever.
- `board` — the kanban's card source, and a **credentialed** read when it
  includes `jira`. Validated at config load; the engine refuses to start without
  `base_url`, `email` and `projects`, because the failure it prevents is a board
  rendering with every Jira card silently missing, which reads as "nothing to
  ship."

`projects` is load-bearing: the Jira key regex is built from the allowlist, never
from the general key shape, because `/[A-Z][A-Z0-9]+-\d+/` also matches `UTF-8`
and `ISO-8601`. No allowlist, no Jira extraction. The token never appears in
`pipeline.yml` — mount `JIRA_API_TOKEN` from Secret Manager.

---

## Key rules

| Rule | Why |
|---|---|
| Pipeline environments are the engine's, exclusively | A manual deploy desyncs `deployed/<branch>` with no way for the engine to detect it |
| Merge commits everywhere, never squash | `git revert -m 1` and `git cherry-pick -m 1` both need real merge commits |
| Never move `deployed/<branch>` unless paused | The tag is the engine's statement about the org |
| A `pipeline.yml` change is not live until the engine restarts | Config is read once at bootstrap; merging it is necessary, not sufficient |
| Mint a CLI token; never expect bare curl to work | `/api/*` is behind Workspace SSO |
| Release by ticket, not by SHA, when you can | The ticket → deploy join is what the model exists for, and it catches ride-alongs |
| Batch production promotions | `NoTestRun` is illegal in production, so every promotion costs a full test run |
| Never `--use-most-recent` on any `sf` command | Another deploy — yours, another agent's, or the engine's — may be the most recent |
| Deploy hooks must be idempotent | A Retry re-runs them; a post-hook freeze re-runs the whole deploy + post |
| Loosen quick-deploy eligibility only with a false-positive argument | A false negative costs 30 minutes; a false positive ships untested metadata |
| Engine down = frozen line, and that is correct | Required checks never go green, so nothing merges |

---

## Known gaps

Verify against the engine repo's issue list rather than trusting this section to
be current.

- **Failure-path drills have never been run** (engine repo #4): freeze, rollback,
  sequencing, re-land and kill. The paths are implemented and unit-tested; they
  have not been exercised against a real org under failure.
- **Scale-to-zero has never run against a real org.** Every timing constant is
  reasoned, not observed. Read the known-risk list before enabling it.
- **`Deploy.contentHash` exists and nothing populates it** — quick deploy is
  still SHA-based.

---

## Troubleshooting

[references/troubleshooting.md](references/troubleshooting.md) — symptom to
action, including the two different families of 503, a board that renders empty,
config that appears not to apply, and webhook silence.

## Related skills

- **`sf-delivery-standards`** — everything below the environment branch: the
  ticket, the worktree, the local dry run, the sandbox deploy, the hooks. Run its
  `init` on an engine-managed repo with `trunk` set to the dev sandbox branch;
  nothing else about it needs to change for the engine.

  There is exactly **one** point of contact, and it is a value in this repo's git
  config using that skill's own documented key: its merge gate defaults to
  `aleysian.squash=require`, which would refuse the merge commits promotion and
  rollback depend on, so `scripts/init.sh` sets it to the existing `prefer` value
  and lets the engine's own guard enforce merge-commits-only. No code in that
  skill changes, and nobody working the local loop has to do anything.
- **`/simplify`** — the AI quality gate, before any commit.
