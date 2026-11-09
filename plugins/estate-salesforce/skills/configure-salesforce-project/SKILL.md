---
name: configure-salesforce-project
description: 'Install, audit or repair a Salesforce repo''s delivery standards: git and Claude Code or Codex hooks, the CLAUDE.md or AGENTS.md contract, tracker and trunk settings, the DevOps Center local loop, initial retrieve and org-drift baseline. Use for set up delivery standards, install hooks, hooks not running, guard blocked me, switch tracker or trunk, first org commit or org drift. Not for ordinary implementation, deploys, promotion, releases or rollback (operate-salesforce-pipeline).'
metadata:
  canon_exempt: 'engineering-doc'
  canon_exempt_reason: 'install, audit and troubleshooting contracts an agent needs before touching a deploy'
---


# Configure salesforce project

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [`general.md`](_runtime/writing-diagnostics/references/registers/general.md). Inputs, not a final pass.**

This skill puts Estate's delivery discipline onto a project and proves it is still
there later. It is **not** the thing you read while implementing a feature — that
contract lives in the project's `CLAUDE.md` (Claude) or `AGENTS.md` (Codex), where it is in context every session
without anything having to trigger.

The direct-delivery invariant is **`trunk === the org`**. In DevOps Center mode the
invariant becomes **DevOps Center owns stage branches and promotion**, while the local
loop owns WI worktrees, scoped org capture, quality, validation, and review handoff.

> **Successor to the retired solo workflow.** Same invariant, same worktree/validate/merge/
> deploy discipline, re-architected for four realities the solo skill never faced:
> the repo may belong to the client or not exist remotely at all; tickets may live in
> Jira; the person using it is probably not the person who wrote it; and the skill is
> not the delivery mechanism for the rules — `CLAUDE.md` is.
>
> **Not this skill:** multi-environment promotion, pipelines, org-to-org sync. Those are
> owned by `operate-salesforce-pipeline` or Salesforce DevOps Center. On an engine repo
> with a `pipeline.yml`, this skill still owns the local loop, with `trunk` set to the
> dev sandbox branch, `squash=merge`, and the environment branches in `protected`.
> See [references/init-guide.md](references/init-guide.md). On a DevOps Center repo,
> use [references/devops-center.md](references/devops-center.md); the managed
> `dx-devops-*` skills own work-item lifecycle, pipeline setup, and promotion.

---

## Sub-commands

| Command | Does |
|---|---|
| `/configure-salesforce-project init` | Detect → ask what cannot be inferred → write config → install hooks → seed the host instruction block → audit → emit the client-conversation checklist. Idempotent. Use `--platform claude`, `codex`, or `both` (default). [references/init-guide.md](references/init-guide.md) |
| `/configure-salesforce-project init --update` | Re-render everything after a skill upgrade, preserving the answers already recorded. |
| `/configure-salesforce-project audit` | Verify every installed piece is still armed. Read-only. `--fix` self-heals the mechanical items. [references/audit-guide.md](references/audit-guide.md) |
| `estate-ticket-status <TICKET>` | Read-only intake for an existing ticket. Reports matching Git work, the trunk landing commit, and clone-local validation/deploy evidence without treating absent local receipts as proof that work did not happen. [references/workflow-steps.md](references/workflow-steps.md) |
| `/configure-salesforce-project probe` | Find out what this project's tracker actually permits — types available, what automation can create, which required fields block it — and record it. Runs during init. [references/ticket-adapters.md](references/ticket-adapters.md) |
| `/configure-salesforce-project preflight` | Report which prerequisites are missing or unauthenticated, and walk the user through them one command at a time. Runs as phase 0 of init. [references/prerequisites.md](references/prerequisites.md) |
| `/configure-salesforce-project seed` | Org → empty repo, the one time the org is upstream. [references/seeding-guide.md](references/seeding-guide.md) |
| `/configure-salesforce-project uninstall` | The inverse of init: retract the Claude and Codex settings entries, remove `~/.estate`, clear the `estate.*` config and `core.hooksPath`, strip the exclude entries and managed instruction blocks, delete `.git/estate`. Removes only what init wrote; user-authored prose survives. `--machine-only` / `--repo` scope it. `scripts/uninstall.sh` |

Route on the argument: *setup / install / bootstrap / init / onboard* → init.
*audit / check / verify / armed / drift* → audit. *seed / baseline / retrieve /
forceignore / first commit* → seeding. *prerequisites / not installed / not authenticated /
command not found* → preflight. *uninstall / remove / rip out / tear down / deactivate* →
uninstall. Nothing else should reach this skill.

Seeding is also a phase **of** init. Running it standalone is for a repo that has the
stack but was never seeded — same guide, and it explains what the guards change about
the order.

---

## Before anything: prerequisites and the credentials rule

**Run `scripts/preflight.sh` before init.** It reports what is missing versus installed-but-
unauthenticated, with one command per gap. Some users will want help working through those
and others will not need any — read the output, offer the next command, take the lead from
them. Details: [references/prerequisites.md](references/prerequisites.md).

**Every auth step here is a browser or device flow. No token is ever typed, pasted, or
passed as an argument.** `gh auth login`, `sf org login web`. This is not a preference: never
accept a credential from a user, and never teach one to paste a secret into a chat window,
where it lands in a transcript. If a user offers you a token, decline and point at the
interactive command.

**Jira has no CLI in this stack.** All Jira work is done by the agent through the Atlassian
Rovo MCP — a connector explicitly authorized for the project in the current client, not on the command
line. A hook is a bash subprocess and cannot reach the session's MCP, so no hook does any Jira
network work; the agent does. See [references/ticket-adapters.md](references/ticket-adapters.md).

A corollary for the GitHub tracker CLI: **installed is not authenticated.** An expired OAuth
session leaves `gh` on `PATH` and every call failing, which looks exactly like a working
install. `preflight.sh` and `audit` report the auth state as its own thing.

---

## The three-layer model

The reason this skill is an installer rather than a workflow enforcer:

| Layer | Lives in | Job | Why it holds |
|---|---|---|---|
| **Contract** | `CLAUDE.md` and/or `AGENTS.md` managed block (~60 lines) | The invariant, the step order, the rules | In context every session. No trigger to miss. |
| **Enforcement** | `~/.estate/` hooks + selected host settings | Walls and gates | Deterministic. Does not depend on any model reading anything. |
| **Reference** | this skill's `references/` | Setup, seeding, adapters, troubleshooting | Loaded rarely, on demand, by explicit path. |

Skill auto-triggering is probabilistic; a hook and a host instruction file are not. So the
hot path belongs to `CLAUDE.md`/`AGENTS.md` and the walls belong to hooks. Putting the *whole*
skill in either file would be the anti-pattern — a 500-line instruction file degrades
adherence to everything in it, including the parts you were trying to make reliable.
Three guardrails keep the block from becoming that:

- **Size budget.** ~60 lines. Anything wanting more room goes in `references/` with a
  pointer from the block.
- **Hash fence.** The `BEGIN` marker carries a hash of the block's own body. A
  hand-edit inside the fence changes the body and not the hash.
- **Session-start self-check.** `verify-git-hooks.sh` re-hashes the block every
  session and reports a mismatch to the model. This is what makes *"an agent edited
  its own CLAUDE.md and deleted the enforcement rules"* self-announcing within one
  session instead of silently permanent.

Hooks are themselves a reliable context channel: `additionalContext` from a
SessionStart hook reaches the model deterministically, which no skill description can
promise.

---

## Two ownership modes

`estate.mode` is the master switch, and also the reason these hooks can be installed
machine-wide without affecting unrelated repos: **every hook exits 0 immediately in a
repo that has no `estate.mode`.**

| | `native` | `stealth` |
|---|---|---|
| Repo owner | Estate, or the client is fine with our tooling in-tree | The client. Nothing of ours gets committed. |
| Hooks | `~/.estate/`, armed via `core.hooksPath` | same |
| Host contract (`CLAUDE.md`, `AGENTS.md`, or both) | **committed** | untracked, in `.git/info/exclude`, symlinked into each worktree |
| Their husky / hooks | blocked (gate 1b) | **chained** — ours runs, then theirs |
| Prettier | their config, `--write` | `--check` only when they have no config |
| State/logs | `.git/estate/` | same |

The stealth rule of thumb, worth stating out loud to whoever is using this:
**govern your own behaviour silently; change their artifacts or their process only out loud.**
If a selected host contract is already tracked, `init` and `init --update` stop before
making any changes. Do not package the generated diff while the clone still declares
`stealth`; either leave the client's tracked file untouched or switch to `native`
deliberately before updating and committing the contract. Audit reports a tracked
managed-contract target in stealth as a failure.

---

## Configuration surface

Every per-repo decision is one `git config estate.*` key. Local git config is
invisible to the client (never tracked), shared automatically by every worktree of the
clone, readable from any hook in one call, and diffable by `audit`.

| Key | Values | Drives |
|---|---|---|
| `mode` | `native` \| `stealth` | artifact policy; **and the master gate** |
| `delivery` | `direct` \| `engine` \| `devops-center` | chooses the delivery invariant, managed contract, and hook behavior |
| `trunk` | branch name | direct/engine: org-synced branch; DevOps Center: topology-derived first landing branch |
| `host` | `github` \| `gitlab` \| `bitbucket` \| `azure` \| `none` | which merge surface the gate intercepts — [references/host-adapters.md](references/host-adapters.md) |
| `review` | `pr` \| `local` | hosted PR vs. the local review gate. `host=none` forces `local` |
| `ticket.system` | `github` \| `jira` \| `pattern` \| `none` | [references/ticket-adapters.md](references/ticket-adapters.md) |
| `ticket.project` | e.g. `SFO` | Jira project key — also narrows the ref pattern to *this* project's keys |
| `ticket.remote` | `ours` \| `client` | `client` turns **all** write automation off by default |
| `ticket.pattern` | regex | what `commit-msg` requires; defaults per system |
| `format` | `client` \| `check` \| `off` | prettier policy |
| `pmd` | `block` \| `advise` | PMD gate severity |
| `squash` | `require` \| `prefer` \| `merge` | hard in native; advisory in stealth when their repo policy differs. `merge` **inverts** it — merge commits required, `--squash`/`--rebase` refused — for a repo whose promotion model cherry-picks merge commits (`-m 1`) and reverts them (`-m 1`) |
| `protected` | space-separated branches | branches this clone may never merge **into**. Empty by default. Checked before the validate hatch, because "skip the dry run" is not "merge anywhere" |
| `sync` | `fetch` \| `off` | `fetch` (default) refreshes `origin/<trunk>` at session start and before every deploy, so a shared org + shared branch surfaces "you are behind" instead of a stale deploy. `off` = local-only, no session-start network. Never pulls/merges into the tree |
| `chainhooks` | path | the project's own hook dir, exec'd after ours |
| `drift` | `tracking` \| `off` | declares a source-tracked org; reconcile is reactive ([drift-reconcile.md](references/drift-reconcile.md)) |
| `qa` | `auto` \| `ask` \| `off` | acceptance-criteria QA at step 7: `ask` (offer, default), `auto` (run once deployed), `off`. The `estate-ac-qa` agent |
| `orgalias` | sf alias | local development org; only direct/engine require it to equal `trunk` |
| `devops.orgalias` | sf alias | the DevOps Center control org; required explicitly on `sf devops` commands |
| `devops.projectid` | record id | the connected DevOps Center project, rendered into the contract |
| `devops.pipelineid` | record id | pipeline whose linked stage topology owns the landing branch |
| `devops.branchpattern` | regex | WI branch shape; defaults to `^WI-[0-9]+$` |
| `devops.workmodel` | `isolated` \| `shared` | isolated uses the WI branch directly; shared adds a serialized development-integration branch |
| `devops.integrationbranch` | branch name | shared-org Git baseline; required only for `devops.workmodel=shared` |
| `devops.environment` | GitHub environment name | centralized successful-deployment receipt for the shared development org |
| `devops.developmentbranchpattern` | regex | shared development refs, with `^dev/WI-[0-9]+$` as the default |

---

## DevOps Center mode

Set `estate.delivery=devops-center` only in a repository dedicated to DevOps Center.
Do not combine it with a Deploy Engine `pipeline.yml` or its merge-tag assumptions.

Isolated development environments do not own Git branches. DevOps Center compares a development
environment to the first pipeline stage and gives each In Progress WI its own feature branch.
Init derives `trunk` from the unique first stage in the pipeline's `nextStageId` chain; a
pre-pipeline value is provisional and cannot pass a full audit.

The hot path is: DevOps Center WI -> In Progress -> existing `WI-######` branch -> linked
worktree -> scoped retrieve/build -> quality + dry run -> commit/push -> DevOps Center
review -> Ready to Promote. The agent does not merge the review or deploy a stage branch.
Use `manage-salesforce-devops` for WI state/review, `promote-salesforce-changes` for selective
promotion, and `dx-devops-pipeline-manage` for setup. Before promotion, inspect the installed
DevOps Center plugin version and the exact required commands and flags. Stop on missing or
obsolete capabilities. Full boundary, conflict recovery, and human/DX Inspector path:
[references/devops-center.md](references/devops-center.md).

Local hooks cannot observe a Salesforce or GitHub web UI action. Put company-required
quality gates in DevOps Testing or repository checks as well as local hooks.

For a deliberately shared, persistent development org, set `devops.workmodel=shared` and read the
shared development-org loop in [references/devops-center.md](references/devops-center.md). That
mode separates `dev/WI-######` development from the generated `WI-######` package, requires a
successful GitHub Deployment SHA as the cross-clone receipt, blocks local real deploys, and gates
the package against a durable scope ledger. A centralized receipt is required for safety, so the
current implementation supports GitHub only. The repository still owns the serialized landing
coordinator, its Salesforce authentication, test policy, branch protection, and verification.

---

## What is installed, and where

```
~/.estate/                       # once per machine; refreshed by init --update
  VERSION                          # audit compares this to the skill
  githooks/pre-commit, commit-msg  # armed per-clone via core.hooksPath
  claude-hooks/*.sh                # absolute paths in USER-level settings.json
  bin/estate-merge               # the local review gate (host=none)
  bin/estate-ticket-status       # read-only existing-ticket intake
  templates/                       # host instruction block, hook fragments, PMD ruleset, .forceignore

~/.claude/agents/estate-ac-qa.md # the acceptance-criteria QA agent (a capability, not a wall)
~/.claude/settings.json            # hook entries, jq-merged (no machine-wide deny rules)
~/.codex/hooks.json                # parallel Codex hook entries, jq-merged
<repo>/.git/estate/              # deploy-log, validate-log, hatch-log, approve-log,
                                   # drift-log, dod-state, pending-jobs
<repo>/.git/info/exclude           # per-clone gitignore (nothing added to theirs)
```

Three of these placements are load-bearing and worth understanding before changing:

**State inside `.git/`.** The predecessor kept logs at `<root>/.claude/.deploy-log`
and gitignored them. In a client repo that means either committing our bookkeeping to
their tree or editing their `.gitignore`. `$(git rev-parse --git-common-dir)/estate/`
is untracked *by construction* — not in any working tree — while still being per-clone
(correct: these logs describe this clone's history against the org) and common across
worktrees (correct: a worktree's dry run must be visible to the merge gate).

**Hooks at user level, not in the repo.** A worktree agent can edit `.claude/hooks/` in
its own branch. It cannot edit `~/.estate/`. *"The repo must not disarm itself"*
becomes *"the repo cannot"*.

**`.git/info/exclude`, not `.gitignore`.** Same effect, but not a tracked file, so
stealth mode adds nothing to anything they will ever see.

---

## Key rules this stack enforces

| Rule | Why | Enforced by |
|---|---|---|
| Direct/engine: `trunk === org`; DevOps Center: service owns stage branches | prevents orphaned deploys and local pipeline bypass | delivery-specific contract + hooks |
| Shared DevOps Center: integration branch equals the latest successful development-org deployment SHA | prevents parallel agents from branching or validating against a Git baseline that is not true in Salesforce | `estate-devops-shared-status`, `guard-devops-shared.sh`, audit |
| Ticket first, in the project's own ref format | without it there is no path from an org change back to the reason for it | `commit-msg` |
| **Never a closing keyword or smart commit** | `fixes #42` closes the ticket at *merge* time, and this loop never closes a ticket on merge (tickets stay open — closure is prod/engine scope). In a client's repo it closes *their* #42 | `guard-closing-keywords.sh` + `commit-msg` |
| `force-app/` is worktree-only | editing it on trunk breaks the invariant before any deploy | `guard-force-app.sh`, `guard-force-app-bash.sh`, `pre-commit` gate 1 |
| Never nest worktrees | removing the outer one deletes the inner one's cwd; every later Bash call fails, including `cd /` | `guard-worktree-nesting.sh` |
| Validate before direct merge or DevOps review handoff | prevents unvalidated source from reaching its landing mechanism | `record-validate.sh`, `guard-pr-merge.sh`, `guard-devops-handoff.sh` |
| A human reviewed the diff | that is what a PR *is*; with no remote, `estate-merge` records it | `guard-pr-merge.sh` + `pre-commit` gate 1 carve-out |
| Deploy from clean trunk in direct mode; from a clean WI worktree in isolated DevOps Center; only through the central coordinator in shared mode | otherwise the target org holds source that cannot be identified and serialized in Git | `guard-sf-deploy.sh` |
| Shared DevOps Center packages contain exactly one accepted WI delta | prevents accumulated sandbox or overlapping component state from leaking into a later promotion | `estate-devops-package`, scope ledger, `guard-devops-handoff.sh` |
| Deploy only changed files; `RunSpecifiedTests` | whole-tree deploys hide what the ticket actually shipped | `guard-sf-deploy.sh` |
| `start --dry-run`, never `deploy validate` | `validate` is the prod quick-deploy path and rejects `NoTestRun` | `guard-sf-deploy.sh` |
| Never `--target-org` on local project commands; require the configured control org on `sf devops` | separates the development org from the DevOps Center API org | `guard-sf-flags.sh` |
| Never retrieve into the **main** tree | silently reverts anything deployed but not pulled back, with no diff anyone read; a linked worktree is allowed — its PR diff catches it | `guard-sf-flags.sh` (gated to managed repos; no machine-wide deny rule) |
| Ticket closure is out of the local loop | a sandbox deploy is not "done"; tickets stay open until production (the delivery system's domain). Close only if the user asks | the contract (no gate; deliberately removed) |
| Never write to a client's tracker unasked | automation editing their project management is not a feature | the contract + `auto-label-deploy.sh` note (`ticket.remote=client`) |
| Never fight the project's own hooks | re-arming ours while dropping theirs is the same sin, aimed at a client | `chainhooks` + `verify-git-hooks.sh` |
| Stage-sync commits gate the net WI delta relative to `MERGE_HEAD` | imported stage files are already promoted content, not new WI scope | merge-aware `pre-commit`; compatible chained lint-staged hooks receive the same diff base |
| `/simplify` before commit | AI quality gate for reuse, architecture, efficiency | **nothing — this one is on you** |
| Acceptance criteria met, judged against the UI | the code is not its own oracle — verifying behaviour from the source rationalises whatever the source does | judgment, aided by `estate-ac-qa` |
| User green light | nothing can check this for you | judgment |

These are deliberately unenforced. `/simplify` is a judgment call with no mechanical
signal — faking it with a marker file would be trivially gamed and would give false
confidence. "Acceptance criteria met" is the same shape: a gate on the *existence* of a
QA artifact would be satisfied by a rubber-stamp comment, so the QA pass is a **capability**
(`estate-ac-qa` — drives the org, screenshots each criterion, comments evidence to the
ticket), not a wall. It judges the AC from the running UI, never from the implementation.
Acceptance criteria are the user's, not the tooling's.

Full hook-by-hook detail, the exit-code contract, and the design rules:
[references/hooks/README.md](references/hooks/README.md).

---

## Escape hatches

Deliberate, **recorded**, never silent. Each appends `<utc> <kind> <sha> <detail>` to
`.git/estate/hatch-log` and emits a note.

`ESTATE_ALLOW_UNVALIDATED_MERGE=1` · `ESTATE_SKIP_DOD=1` · `ESTATE_ALLOW_RETRIEVE=1` ·
`ESTATE_ALLOW_UNVALIDATED_PUSH=1` (bitbucket only) · `git commit --no-verify` · the
`docs-only` / `no-deploy` ticket labels. The `SOLO_` prefixes from
the predecessor still work — a documented override that silently does nothing looks
like a broken gate, and gates that look broken get removed.

There is **no** hatch on the force-app-outside-a-worktree guards, and none on
`guard-closing-keywords.sh`. Those are walls, not gates.

None of them block. A hatch that argues with you is one people route around; the log is
what makes using one a decision on record.

**Scope, stated honestly:** `record-escape-hatch.sh` sees commands issued *through the
agent*. A `--no-verify` typed in a terminal or clicked in an IDE is invisible to it. Say
"hatches used through the agent are recorded", not "every commit is accounted for".

For a DevOps Center stage-sync merge, `--no-verify` is a last resort only when a chained
repository hook cannot safely consume the merge-aware diff base. Record the reason and retain
independent evidence for the net WI delta: file list against `MERGE_HEAD`, focused gates, the full
repository suite, and an exact-commit Salesforce dry run. See
[references/devops-center.md](references/devops-center.md).

---

## Org drift (`estate.drift`)

Reframes the Setup-click problem from prohibition to capture: **clicking in Setup is not
forbidden; unrecorded clicking is.**

The user's report is the primary trigger. The ticket-owning agent treats the named components as
candidates, verifies them through `SourceMember`, subtracts newer git and deploy activity, and
captures only the confirmed remainder into `tmp-retrieve` in the ticket worktree. A broad
SourceMember query is the fallback when the user cannot remember the component names.

This is reactive by design. There is no poller, scheduled job, cursor store, org-change inbox, or
automatic git writer. `SourceMember` identifies metadata; it does not prove author or intent.
Added and modified metadata are retrieved narrowly. An `IsNameObsolete` deletion is confirmed and
removed deliberately from source because a deleted component cannot be retrieved. The full path
lives in [references/drift-reconcile.md](references/drift-reconcile.md).

- **`tracking`** — the org is source-tracked (Dev/Dev Pro/scratch). Declares that the
  reconcile playbook applies here.
- **`off`** — default.

`audittrail` is **retired**. Building directly in a non-source-tracked org (partial/full copy,
production) is out of scope for this local loop. Pipeline-environment drift remains an
`operate-salesforce-pipeline` or DevOps Center concern. The local handoff begins once the reviewed change is
in source and ready for that delivery system.

---

## Related skills

- **`/simplify`** — the AI quality gate (step 3 of the contract).
- **`estate-ac-qa`** — the acceptance-criteria QA capability shipped with this stack
  (step 7). Verifies AC against the running UI, blind to the implementation; delegates
  browser mechanics to `capture-salesforce-screens` and posts its report as a ticket
  comment (GitHub via `gh`, Jira via the Rovo MCP with inline-image evidence),
  respecting `ticket.remote`. Claude installs it to `~/.claude/agents/`; Codex uses
  the shipped `references/agents/estate-ac-qa.md` as the delegated QA prompt.
- **`capture-requirements`** — how work is intaked: user story + Gherkin AC with a
  named persona. Those AC are what `estate-ac-qa` and step 7 measure against.
- **`capture-salesforce-screens`** — the headless browser driver `estate-ac-qa` calls
  to screenshot and assert against the org. The single source of truth for
  Salesforce UI waits and selectors. Wraps the `sfqa` CLI.
- **`github-issue-manager`** — creating and managing GitHub issues, when
  `ticket.system=github`.
- **`operate-salesforce-pipeline`** — everything from the PR into an environment branch upward:
  promotion, releases, rollback, freeze recovery. Do not bolt multi-environment
  concerns onto this skill; the invariant here stays one branch and one org, and on
  an engine-managed repo that branch is the dev sandbox. Run its `scripts/init.sh`
  to set `protected` from `pipeline.yml` rather than typing the branch list.
- **`manage-salesforce-devops`**: DevOps Center work-item state, generated WI branch,
  commit/push guidance, and review creation.
- **`promote-salesforce-changes`**: validate, prepare, selectively promote, and complete DevOps
  Center work-item promotion.
- **`dx-devops-pipeline-manage`**: pipeline, stage, environment, project, and activation
  management for the dedicated DevOps Center repository.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
