---
name: sf-solo-devops
description: Prepare, check, and deliver changes to a single-org Salesforce project using isolated Git worktrees, generated permissions, local quality checks, and explicit org identity checks. Supports local preparation without an org. Use sf-deploy-engine for multi-environment promotion.
canon_exempt: 'engineering-doc'
canon_exempt_reason: 'setup, workflow and troubleshooting contracts an agent needs before touching a deploy'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Solo Salesforce Project DevOps

Use this workflow for a solo Salesforce project: prepare the change in a worktree, check its local outputs, validate against a confirmed org when available, merge the reviewed commit, deploy it, and verify the requested behavior. Claude Code and Codex can both use the workflow and Python tools. Claude-specific hooks only apply where installed and tested in Claude Code; their presence does not establish enforcement in Codex.

## Work without an org

No org is required to inspect the source, implement a change, generate a permission-set preview, run local checks, or prepare a reviewable PR. Do not select an existing CLI alias as a substitute for a user-confirmed test target. Do not run a deployment, dry run, retrieve, Apex test, or data query without that target.

1. Read the project requirements and inspect its SFDX package directories. Preserve current files and use a worktree for changes.
2. Run the project's installed local checks. Record missing tools and repair the local toolchain where authorized; a skipped check is not a pass.
3. Generate the permission set from source with [gen-permset.py](references/tools/gen-permset.py). `--init` creates the configuration; `--out /tmp/new-preview.xml` creates a new preview outside project trees; `--fail-on-drift` checks committed output; `--write` requires a verified worktree.
4. Review the generated XML and the changed metadata against the requested behavior. Retain the inputs, preview, local test results, and failed attempts.
5. Save a deployment handoff listing the exact commit, source files, proposed tests, and outstanding target requirement. Report **prepared locally**. Do not record a Salesforce validation or deployment success.

When an org becomes available, use [org-preflight](../org-preflight/SKILL.md) to compare its actual ID with the intended ID, then use that same explicit `--target-org` on subsequent CLI operations. Never copy a default alias into a worktree automatically. Identity verification and authorization for a write are separate requirements.

---

## Sub-commands

- **`/sf-solo-devops`** (no args) — Enforce the workflow during an implementation task. This is the default.
- **`/sf-solo-devops setup`** — Bootstrap a project with the full enforcement stack: git hooks, Claude hooks, Claude settings, and the workflow section for CLAUDE.md. See [references/setup-guide.md](references/setup-guide.md).
- **`/sf-solo-devops seed`** — Get an existing org's metadata into an empty repo for the first time: `.forceignore`, a manifest generated from the org and pruned, the retrieve, a tree prune, and a round-trip check. See [references/seeding-guide.md](references/seeding-guide.md).

If the argument contains "setup", "install", "bootstrap", or "init", follow the setup guide. If it contains "seed", "retrieve", "baseline", or "import", follow the seeding guide. Otherwise, enforce the workflow below.

Seeding is also Phase 2f *of* setup. Running it as its own sub-command is for the case where the stack is already installed and the repo was never seeded — same guide, and it will tell you what the guards change about the sequence.

---

## When This Skill Applies

Any task that will result in changes to `force-app/` (Apex, LWC, metadata, permissions, flows, objects, etc.) on a solo-developer, single-org Salesforce project. This includes:

- New feature implementation
- Bug fixes
- Metadata changes (objects, fields, permission sets, flows, flexipages)
- Refactoring existing code
- Any work that will ultimately be deployed to the org

Docs-only changes do not need deployment checks. Follow the repository’s normal branch and review rules.

**Does NOT apply to:** projects with a `pipeline.yml` or more than one environment branch. That's `sf-deploy-engine` territory — this skill has no concept of promotion, staging, or an orchestration engine.

---

## The Invariant

The desired deployment state is that the managed metadata in the org matches the recorded release commit on `main`. A Git merge or local log cannot prove that state. Preserve the deployment result and acceptance evidence; report divergence when a deployment fails or remains pending.

```
worktree → PR (squash) → main → deploy → org
```

Every implementation task follows this sequence. Each step gates the next. Do not skip steps, do not reorder.

### Step 1 — Ticket First

Before writing any code, create or identify a GitHub issue.

- Use `github-repository-work` or the available GitHub CLI to search for existing issues
- Create a new issue if none exists
- Note the issue number — every branch and commit references it

**Why:** issues are the audit trail. Without a ticket there is no record of what was done or why.

### Step 2 — Work in a Worktree

All development happens in an isolated git worktree. Never commit deployable code directly to `main`.

- Use an available managed worktree tool or `git worktree add`. A runtime-specific Agent tool is optional.
- Branch naming: `feat/N-short-description` or `fix/N-short-description` (where N is the issue number)
- Worktrees branch from `main`
- Worktrees do not inherit `.sf/` configuration. Pass the confirmed org explicitly for org operations. `ensure-worktree-config.sh` can link local Node dependencies; it does not copy or set an org.

**CRITICAL — No nested worktrees:** An agent spawned with `isolation: "worktree"` is already isolated. It works directly in that worktree — branch, change, commit — and must NEVER create another worktree inside it. Nesting is unrecoverable: when the outer worktree is removed, the Bash tool's CWD points at a deleted directory and every subsequent shell command fails permanently, including `cd /`.

**Bash inside a worktree-isolated agent is sandboxed by the harness.** It refuses anything it cannot prove stays inside the worktree — `&&`/`;` chains, `cd … && for …`, and `<<'EOF'` heredocs (read as redirects):

> `…is too complex to verify that it stays inside the worktree; break it into plain, separate commands`

That is **Claude Code, not this project's hooks** — there is nothing to find in `.claude/hooks/`, and it is **not** a stop-and-report condition. Split into plain commands, or write a script to the scratchpad and run it by path.

**If you are already in a worktree**, do NOT call `Agent` with `isolation: "worktree"` or run `git worktree add`. Just work where you are. The check — one plain command, because inside a worktree-isolated agent the harness refuses compound ones:

```bash
git rev-parse --absolute-git-dir
```
Read the answer off the path: `…/<repo>/.git` is the main checkout, `…/<repo>/.git/worktrees/<name>` is a worktree. This is the same topology the hooks use, so it cannot disagree with them.


Do not test this by looking for `.claude/worktrees/` in the path. A worktree created anywhere else (`git worktree add ../myproject-42`) is just as much a worktree, and the guards honour it.

**For rapid iteration and follow-up fixes** it is fine to leave a worktree open and continue to issue PRs. It is NOT ok to shift to editing `main` or its local files.

Read [references/workflow-steps.md](references/workflow-steps.md) for the exact command sequences.

### Step 3 — Quality Gates

#### 3a — Prettier, ESLint, PMD, Jest

When installed and configured, the reference `pre-commit` hook runs the applicable checks against staged files. Verify the hook and toolchain before relying on that enforcement. Run them early if you want faster feedback:

```bash
npm run pmd      # or: pmd check -d force-app/main/default/classes \
                 #       -R category/apex/bestpractices.xml,category/apex/security.xml,\
                 #          category/apex/design.xml,category/apex/errorprone.xml -f text
npm run lint
npm test
```

But the commit is the gate. A violation blocks it; prettier fixes and re-stages formatting for you.

#### 3b — /simplify

Use `code-simplify`, an available equivalent, or a direct code review before committing. This is the AI quality gate — it reviews for code reuse, efficiency, separation of concerns, and Salesforce best practices. Fix all issues found. Skip only for trivial metadata-only changes (single field, label update).

**This is the one quality gate no hook can enforce** — a judgment step with no mechanical signal, so it stays on you.

#### 3c — Commit

`refs #N` for in-progress commits, `fixes #N` on the final squash merge. The keyword is required, not decorative: `commit-msg` rejects a bare `#N`, because everything downstream (labelling, close permission, DoD checks) reads these refs out of commit messages, and a bare-`#N` scan picks issue numbers out of ordinary prose.

### Step 4 — Validate, Merge, Deploy (atomic sequence — do not reorder)

This sequence applies once an org is confirmed and the deployment is authorized. Without an org, complete the local preparation path above and retain the pending deployment handoff.

**From the worktree**, when the feature is ready:

1. **Jest and PMD** — retain the actual results for the changed commit. A commit alone does not prove hooks ran or checks passed.
2. **Identify Apex tests** — For each changed Apex class, include its `*Test` counterpart. For trigger/handler changes, cast a wider net. List classes explicitly.
3. **Validate against the org** (dry run — org unchanged, this is the merge gate):
   ```bash
   sf project deploy start --dry-run --target-org CONFIRMED_ORG --json \
     --source-dir force-app/main/default/classes/ChangedClass.cls \
     --source-dir force-app/main/default/classes/ChangedClassTest.cls \
     --test-level RunSpecifiedTests --tests TestA TestB TestC
   ```
   Deploy only changed files — never `--source-dir force-app` (the whole directory). This is hook-enforced.
   If validate fails, iterate in the worktree. Do not merge.

   A successful dry run is recorded against the current commit. **Commit first, then validate** — the merge gate is per-commit, so validating and then pushing another commit means re-validating.

   Use `start --dry-run` for a development-org check. For an authorized production validation and quick-deploy workflow, use the supported `validate` and `quick` commands with the required tests. See [Salesforce CLI deployment documentation](https://github.com/salesforcecli/plugin-deploy-retrieve).
4. **Create and squash merge the PR** to `main`:
   ```bash
   gh pr create --base main --title "feat: description (fixes #N)" --body "..."
   gh pr merge --squash --delete-branch
   ```
   Squash-only, and only with a recorded validate for the head commit — both hook-enforced.
5. **Deploy from `main`** (real deploy to the org):
   ```bash
   git checkout main && git pull
   sf project deploy start --target-org CONFIRMED_ORG --json \
     --source-dir force-app/main/default/classes/ChangedClass.cls \
     --source-dir force-app/main/default/classes/ChangedClassTest.cls \
     --test-level RunSpecifiedTests --tests TestA TestB TestC
   ```
   The `git pull` is not optional: the deploy guard blocks a `main` that is behind origin (you would ship an older tree than you merged), ahead of it (unpushed code reaching the org), or dirty.
6. **User tests** — hard-refresh browser, verify against acceptance criteria.
7. **Clean up worktree**: `git worktree remove <path>`

**Use the confirmed explicit `--target-org` on org operations.** Run `org-preflight` first. An alias by itself is not an identity check, and a machine default is not a confirmed project target.

**Test selection guidance:**

Choose tests from the changed behavior, its callers, the target org, and the project's release policy. `RunSpecifiedTests` can provide focused feedback; use `RunLocalTests` or `RunAllTestsInOrg` when broader coverage is required. Do not prohibit those levels to save time. Locate related Apex tests with `rg`, inspect their assertions, and retain the results.

`NoTestRun` is for supported development environments. Do not infer permission to skip production tests from a label such as “metadata-only.” Check the installed command's help and [Salesforce's test-level reference](https://github.com/salesforcecli/plugin-deploy-retrieve/blob/main/messages/deploy.metadata.md).

**If deployment fails:** preserve the result, job ID, release SHA, target ID, and actual org state. Choose fix-forward or a reviewed rollback using those facts. A Git revert does not undo an org mutation, and some metadata or data changes need a separate recovery procedure. Do not push a speculative revert or claim parity restored without verifying the subsequent result.

### Step 5 — Definition of Done (mandatory — do not skip)

For a task whose requested finish line includes deployment, completion requires all of these. For an offline preparation task, use the local handoff criteria above:

1. **Deployed to the org** — `sf project deploy start` succeeded (not just validate)
2. **In git and GitHub** — PR squash-merged to `main`, pushed to origin
3. **Acceptance criteria met** — every criterion from the GitHub issue is satisfied
4. **User gives green light** on all changes (they may want to do manual testing, etc.)
5. **Ticket updated and closed** — summary of what shipped, commit SHA or PR link, then `gh issue close N`
6. **Worktree cleaned up** — `git worktree remove <path>` and local branch deleted

**Common agent failures:** deploying but never closing the ticket. Closing the ticket but never removing the worktree. Reporting "done" after validate but before deploy. All of these are incomplete. `stop-dod-check.sh` refuses to end a turn with `main` ahead of the org or a deployed ticket still open — but items 3 and 4 are still yours to confirm.

**Keeping a worktree open across a deploy is expected, not a failure.** Same tree, same ticket, follow-up fixes as another PR — the workflow is built for it and no hook nags about it. Cleanup (item 6) is due when the **ticket** closes, not after every deploy. Two things when reusing a branch after its squash merge:

- **Sync it first:** `git merge main` after preserving and reviewing any local changes. The squash put your content on `main` under a commit the branch has never seen, so without this the next PR's diff re-shows all the original work.
- **Re-validate.** The merge gate is per-commit: a new commit needs its own dry run before `gh pr merge` will allow it.

---

## Seeding an Existing Org — the one time the org is upstream

Every rule above assumes the repo is the source of truth and the org is downstream
of it. Exactly once per project, that is backwards: an org already exists, the repo
is empty, and the metadata has to come **out** of the org to establish the baseline
the invariant is measured against.

Full procedure in [references/seeding-guide.md](references/seeding-guide.md). What
belongs in your head:

**Seed before installing the enforcement stack, not after.** The stack blocks
`sf project retrieve` at two layers, correctly, and the repo being empty is the only
window in which a retrieve cannot clobber anything. Seeding is Phase 2f of setup for
that reason.

**Sanitize at the manifest, not on disk.** `sf project generate manifest --from-org`
with `--excluded-metadata` filters before the retrieve, so the pass is one file of a
few hundred lines rather than a few thousand files. It also excludes managed and
unlocked package metadata by default, which removes the namespace sweep entirely.

**Exclude by reason class, not from a list.** Lists rot and teach nothing. Five
classes cover it: *not authored* (reports, dashboards, documents — users keep making
more), *not portable* (Connected Apps, External Client Apps, certificates — secrets
do not retrieve, so what deploys is a shell that fails silently), *not yours*
(package metadata), *superseded* (`FlowDefinition`, `CleanDataService`, `AppMenu`),
and *governed elsewhere*.

**Profiles are the "governed elsewhere" case, and the one worth understanding.** They
are excluded because this skill's permission model is one generated permission set,
not because profiles are bad. A retrieved profile is a second, hand-edited answer to
the question `gen-permset.py` already answers from the source tree — it conflicts on
every parallel build and carries FLS for fields the target branch may not have.

**`.forceignore` is the durable half.** Manifest exclusions govern one retrieve;
`.forceignore` governs every retrieve and deploy afterwards. Write it first, commit
it, and treat it like `CLAUDE.md` — a gitignored `.forceignore` does not exist in any
worktree. Template with per-line reason classes:
[references/templates/forceignore](references/templates/forceignore).

**Prove the round trip before committing.** A retrieve that cannot deploy back is a
snapshot, not a baseline:

```bash
sf project deploy start --dry-run --target-org CONFIRMED_ORG --source-dir force-app/main/default --test-level RunLocalTests
```

`force-app/main/default`, not bare `force-app` — the latter is blocked by
`guard-sf-deploy.sh` and there is no reason to learn the command two ways. Every
remaining failure gets fixed or written into `CLAUDE.md` with a reason. Then one
commit, not a series: this is the tree the whole project is diffed against.

**Afterwards, there is no second seed.** Something that exists only in the org gets a
ticket and a worktree like anything else. Retrieve it into a scratch tree from your
own terminal (`--output-dir tmp-retrieve`, gitignored, cannot touch tracked files),
copy across what you meant, and deploy it back — the deploy is what makes the two
copies the same thing again.

---

## Concurrent Deploys — Job ID Discipline

Multiple agents may be deploying to the org simultaneously. Never assume the "latest" deploy job is yours.

**NEVER use `--use-most-recent`** on any `sf project deploy` subcommand. This flag resolves to whatever deploy the org last received — which could be another agent's job.

| Dangerous | Safe equivalent |
|-----------|----------------|
| `sf project deploy report --use-most-recent` | `sf project deploy report --target-org CONFIRMED_ORG --job-id $JOB_ID` |
| `sf project deploy cancel --use-most-recent` | `sf project deploy cancel --target-org CONFIRMED_ORG --job-id $JOB_ID` |
| `sf project deploy resume --use-most-recent` | `sf project deploy resume --target-org CONFIRMED_ORG --job-id $JOB_ID` |

**Pattern — capture the job ID immediately:**
```bash
DEPLOY_RESULT=$(sf project deploy start --target-org CONFIRMED_ORG --source-dir <files> \
  --test-level RunSpecifiedTests --tests <TestClasses> --json --async)
JOB_ID=$(echo "$DEPLOY_RESULT" | jq -r '.result.id')
sf project deploy report --target-org CONFIRMED_ORG --job-id "$JOB_ID"
```

If you run a deploy/validate synchronously (without `--async`), the CLI blocks until completion — that's fine, no follow-up `report` call needed.

Note: this discipline covers *not confusing whose job is whose*. It does not by itself prevent two agents from submitting concurrent deploy/validate requests against the same org — Salesforce serializes/queues those at the platform level, and today this project relies on the workflow discipline above (worktree dry-runs, one squash-merge-and-deploy at a time from `main`) rather than an explicit lock to keep that orderly. If concurrent-agent collisions on the single org become a real problem in practice, that's worth revisiting — not a reason to avoid this skill's lighter-weight model in the meantime.

---

## Subagent Delegation — Do the Work Yourself

The main agent should do the work directly unless there is a clear, specific reason to delegate. You have full conversation context; subagents get a compressed summary and lose nuance.

**Good subagent uses:**
- Research/exploration — return findings to main agent for synthesis and ongoing work
- Parallelizable independent tasks (e.g., multiple worktrees for separate tickets)
- Long-running background tasks where the main agent continues other work

**Bad subagent uses:**
- "Go build the whole thing" — handing off implementation with a fraction of the context. This invariably fails because the subagent lacks business rules, prior decisions, and codebase understanding.

**Rule of thumb:** If you can do the task yourself in the current context, do it yourself.

---

## Fanning a Build Out — Generate Shared Metadata, Never Author It

When you *do* delegate a build to several worktree agents at once, the thing that breaks is not the
code. It is the handful of files **every** agent has to touch — the project permission set above
all, plus anything else that must list every object, field or class.

The framing to reject is "visible merge conflicts vs. invisible FLS gap". Both options are bad and
you do not have to pick one:

- Every agent edits the permission set → guaranteed conflict on the one file they all touch, every
  wave, forever.
- Agents skip it and you grant FLS later → the field deploys, nobody can see it, and it resurfaces
  as a phantom *"field does not exist"* that reads like a data-model bug and is not.

**Derive the file from the source tree instead of authoring it, and both disappear.** Two branches
that each add fields converge the moment the file is regenerated against the merged tree — nothing
to hand-merge, because the file is a pure function of what is on disk. And because you regenerate
**into the agent's worktree before merging**, the fields and their FLS land in the same PR and the
same deploy. No conflict, no invisible-field window.

[references/tools/gen-permset.py](references/tools/gen-permset.py) does this for the permission set.
Install it as `scripts/gen-permset.py`, run `--init` once to create `config/permset-gen.json`, and
add `"permset": "python3 scripts/gen-permset.py"` / `"permset:write": "… --write"` to
`package.json`.

| You are | You do |
|---|---|
| **A worktree agent** | **Never** edit the permission set. **Never** run `--write`. Run `npm run permset` (check mode) to confirm your new fields are still ungranted, and say so in your report. That's all. Sole exception: the ticket that creates the file for the first time. |
| **The orchestrator** | From the main clone, as the last step before merging: `python3 scripts/gen-permset.py --write --tree <agent worktree>` → commit into the worktree → **re-validate** (the merge gate is per-commit and you just added one) → merge → deploy. |

`--write` refuses to target the main checkout **from anywhere** — the refusal follows the *target*,
not your cwd, mirroring `guard-force-app-bash.sh`. That is what lets you resolve a generated file
from the main clone without bouncing the PR back to an agent. `--out PATH` dumps a copy for diffing
and is safe in the main clone. Check mode is the default and is safe everywhere.

The script preserves the historical field classifications: omit MasterDetail and required fields, and make formula, roll-up and AutoNumber fields read-only. Local tests verify those decisions. Validate the repaired output against the intended platform before claiming it deployed.

Read [references/tools/README.md](references/tools/README.md) for the config reference, the full
locally tested refusal cases, package handling, and retained-test workflow.

---

## Key Rules (quick reference)

| Rule | Why | Enforced by |
|------|-----|-------------|
| Verify the recorded release against the org | Git state alone does not prove deployment state | Deployment receipt and acceptance checks |
| Never deploy from a worktree | Only `main` deploys — worktrees validate only | `guard-sf-deploy.sh` |
| Never deploy a dirty or unpushed `main` | The org would hold code that is not in git / not on GitHub | `guard-sf-deploy.sh` |
| Use one explicit confirmed `--target-org` | Avoid accidental use of a machine default | `org-preflight` and `guard-sf-flags.sh` |
| Local preparation needs no org | Leave the target unset until confirmed | Explicit workflow mode |
| Deploy only changed files | Never `--source-dir force-app` | `guard-sf-deploy.sh` |
| Validate before you merge | Merging before a green dry run can strand `main` ahead of the org | `guard-pr-merge.sh` |
| Squash merges only | One ticket, one commit — the refs the automation reads stay in one place | `guard-pr-merge.sh` |
| `/simplify` before commit | AI quality gate for reuse, architecture, efficiency | **nothing — this one is on you** |
| Definition of Done = all 6 boxes | Deployed + in git + AC met + user green light + ticket closed + worktree removed | `guard-issue-close.sh`, `stop-dod-check.sh` |
| Fix forward, never reopen merged branches | New worktree + new issue off latest `main` | judgment |
| Worktrees live as long as their ticket | Reuse one across deploys for follow-up fixes; remove it when the ticket closes | `session-status.sh` reports open ones |
| Never nest worktrees | `isolation: "worktree"` agents are already in a worktree — creating another causes unrecoverable Bash failures | `guard-worktree-nesting.sh` |
| Never use `--use-most-recent` | Another agent's deploy may be the "most recent" — always use `--job-id` | `guard-sf-flags.sh` |
| Choose test scope from target and release policy | Broader tests may be required | Review and platform validation |
| Choose development dry-run or production validation deliberately | The commands support different deployment workflows | Target-specific plan |
| `RunSpecifiedTests` by default | Fast, targeted feedback — the whole point of a solo dev loop | — |
| Use `NoTestRun` only where supported | A small change does not override production requirements | Target-specific plan |
| Issue refs are keyword-anchored | A bare `#N` scan reads issue numbers out of prose and labels the wrong tickets | `commit-msg` |
| The permission set is generated, never hand-edited | It is the one file every parallel agent touches; derived from the tree, two branches converge on regeneration instead of conflicting | `gen-permset.py` refuses `--write` outside a worktree |
| Worktree agents run `npm run permset` in check mode only; the orchestrator runs `--write --tree <worktree>` before merging | Fields and their FLS land in the same PR and the same deploy — no window where a deployed field is invisible | judgment + the script's target-based refusal |
| **CLAUDE.md, `.claude/hooks/`, `.githooks/` and `.forceignore` must be committed, not gitignored** | Worktrees only ever materialize *tracked* content — anything ignored silently does not exist in any worktree, which defeats this entire skill | `verify-git-hooks.sh` reports it |
| Seed once, before the enforcement stack | The empty repo is the only window where a retrieve cannot clobber tracked content; after that the org is downstream forever | ordering in `setup-guide.md` Phase 2f |
| Sanitize at the manifest, not on disk | One file of a few hundred lines beats a few thousand files, and the retrieve is smaller too | judgment |
| Never `retrieve --source-dir force-app` | Overwrites tracked content with org state and silently reverts anything deployed but not yet pulled back — no ticket, no diff anyone read | `guard-sf-flags.sh` + deny rules |
| Prove the round trip before the seed commit | A retrieve that cannot deploy back is a snapshot, not a baseline — `main === org` would be false on day one | judgment |

---

## Enforcement Stack

The reference hooks need installation and runtime testing before their gates can be relied on. **Keep installed hook source tracked in the project repo** — `.githooks/` and `.claude/hooks/` — so a fresh clone and every new worktree get the whole stack, and the one genuinely per-clone setting arms itself.

Reference copies, install steps and the design rules are in [references/hooks/README.md](references/hooks/README.md).

### Git hooks (`.githooks/` — tracked, armed via `core.hooksPath`)

| Hook | Gate | What it does |
|------|------|-------------|
| `pre-commit` | 1 | Blocks `force-app/` commits on `main` — forces worktree usage |
| | 1b | Blocks reintroducing husky; auto-fixes the exec bit on staged hook scripts |
| | 2 | Prettier `--write` + re-stage (skips partially-staged files rather than sweeping unstaged work into the commit) |
| | 3 | ESLint on staged LWC/Aura JS — **blocks** |
| | 4 | PMD on staged Apex (step 3a) — **blocks** |
| | 5 | Jest `--findRelatedTests` on staged LWC (step 4a) — **blocks** |
| `commit-msg` | | Requires a **keyword-anchored** issue ref (`refs #N` / `fixes #N`) on commits touching `force-app/` |

All gates are scoped to staged files only, so a docs- or metadata-only commit pays almost nothing. `pre-commit` symlinks `node_modules` from the main clone so the node tools work in worktrees.

**Setup:** after reconciling existing hooks, configure `core.hooksPath=.githooks` deliberately. `verify-git-hooks.sh` inspects each session without changing settings or file permissions. Run the installed hooks with synthetic events to prove host invocation.

The reference Git stack expects `.githooks`. An existing Husky setup needs reconciliation before this stack is selected. Preserve its checks and choose one hook configuration; the session verifier reports a different path without replacing it.

### Claude Code hooks (`.claude/hooks/` — tracked, auto-applied)

Shared helpers live in `_lib.sh`: event parsing, `block()`/`note()`, worktree detection by git topology, main-clone resolution, and deploy-success verification.

**Guards — PreToolUse, exit 2 to block:**

| Hook | Matcher | Blocks |
|------|---------|--------|
| `guard-force-app.sh` | `Edit\|Write\|NotebookEdit` | Editing `force-app/` outside a worktree |
| `guard-force-app-bash.sh` | `Bash` | Shell writes to `force-app/` outside a worktree (`>`, `cp`, `mv`, `rm`, `sed -i`, `git apply`, …) |
| `guard-sf-deploy.sh` | `Bash` | whole-tree `--source-dir`; real deploys off `main`, from a dirty `main`, or from an unpushed `main` |
| `guard-sf-flags.sh` | `Bash` | missing or ambiguous explicit org target for org operations; `--use-most-recent`; routine `retrieve` |
| `guard-worktree-nesting.sh` | `Bash` | `git worktree add` from inside a worktree |
| `guard-pr-merge.sh` | `Bash` | Non-squash merges; merging a `force-app` PR whose head commit has no recorded validate |
| `guard-issue-close.sh` | `Bash` | `gh issue close N` unless a recorded deploy's history references `#N` |

**Automation — PostToolUse, never blocks:**

| Hook | What it does |
|------|-------------|
| `record-validate.sh` | Records the commit SHA of each **successful** dry run to `.claude/.validate-log` — the proof `guard-pr-merge.sh` requires |
| `auto-label-deploy.sh` | On a **successful** real deploy from `main`: records the SHA and job from structured JSON; GitHub labels/comments require explicit `SOLO_GITHUB_UPDATES=1` opt-in |
| `post-merge-nudge.sh` | After a squash merge, hands over the exact deploy command with the merged `force-app/` files already listed |

**Lifecycle:**

| Hook | Event | What it does |
|------|-------|-------------|
| `verify-git-hooks.sh` | SessionStart | Inspects the active checkout, configured hook path, local scripts and Python helpers; reports problems without changing configuration or file permissions |
| `session-status.sh` | SessionStart | Worktree-vs-main location, uncommitted `force-app/`, local deployment-log state (not a live parity check), and each open worktree's state (dirty / content already on main / not yet on main) |
| `ensure-worktree-config.sh` | PreToolUse `Bash` | Links `node_modules` for local Node tooling in a worktree. Does not call Salesforce or set an org |
| `stop-dod-check.sh` | Stop | Refuses to end the turn while `main` is ahead of the org or a deployed ticket is still open. Fingerprinted — reports each distinct state once, and honours `stop_hook_active`, so it cannot loop. Says nothing about open worktrees on purpose: keeping one for follow-up fixes is supported, so that is a preference, not a defect |

> **Never configure a `WorktreeCreate` hook in a git repo.** That event is not a post-creation notification — Claude Code delegates worktree *creation* to it and reads the path from the hook's stdout (`hook succeeded but returned no worktree path`). It exists so non-git VCS users can supply worktrees. Configuring one here overrode a native implementation that already worked, and every `isolation: "worktree"` agent died at spawn with a status line parsed as a path. Redirecting to stderr does not fix it either — then stdout is empty and the spawn fails for the opposite reason.

### Claude Code permissions (`.claude/settings.json`)

| Type | Rule | What it does |
|------|------|-------------|
| Deny | `Bash(sf project retrieve start:*)` | Blocks `sf project retrieve` — prevents accidental org-to-source pulls |
| Deny | `Bash(sf project retrieve:*)` | Same (covers both command forms) |

The routine command guard refuses retrieves. An authorized initial seed or later recovery needs a reviewed, separate scratch destination and an explicit project permission change if retrieval is denied. An environment variable does not authorize that change.

### The exit-code contract

A PreToolUse hook blocks on **exit 2** only. Exit 1 is a *non-blocking error* — the tool runs anyway, so a guard that exits 1 prints a convincing refusal and enforces nothing. Use `block()` from `_lib.sh`.

To feed guidance back to the model from PostToolUse or Stop without failing anything, use `note()` — plain stderr on exit 0 reaches the user's transcript, not the model.

### Machine-local state (all gitignored)

| File | Written by | Read by |
|------|-----------|---------|
| `.claude/.deploy-log` | `auto-label-deploy.sh` | `guard-issue-close.sh`, `stop-dod-check.sh`, `session-status.sh` |
| `.claude/.validate-log` | `record-validate.sh` | `guard-pr-merge.sh` |
| `.claude/.dod-state` | `stop-dod-check.sh` | itself (dedupe) |
| `.claude/.pending-jobs` | both recorders | both recorders — async jobs this clone started, so a `deploy report` can be told apart from a lookup |
| `.claude/.hatch-log` | every guard with a hatch, plus `record-escape-hatch.sh` | humans — every override used in this clone |

Each describes *this clone's* history against the org, so none of it is shared. Hooks resolve these paths through `--git-common-dir`, so a hook running in a worktree reads the same files as one running in the main clone.

`.deploy-log` lines are `<sha> <job-id> <utc stamp>`. Read them with `deploy_log_shas()`. Preserve the full structured result, target identity, and exact package beside the index. The recorder does not make background org calls. If the index is lost, rebuild an entry only from evidence that links that exact commit and package to the successful job; matching approximate timestamps is insufficient. Never invent an entry to unblock a close.

### Escape hatches

Deliberate, **recorded**, never silent: `SOLO_ALLOW_UNVALIDATED_MERGE=1`, `SOLO_SKIP_DOD=1`, `git commit --no-verify`, and the `docs-only` / `no-deploy` issue labels. There is **no** escape hatch on the force-app-outside-a-worktree guards — that one is a wall, not a gate.

Each hatch appends `<utc> <kind> <sha> <detail>` to `.claude/.hatch-log` and emits a `note()`. None of them block: a hatch that argues with you is one people route around. The log makes using one a decision on record.

`git commit --no-verify` bypasses every git hook by definition, so no git hook can report its own bypass — `record-escape-hatch.sh` catches it as a PreToolUse Bash hook instead. That sees commands issued **through the agent**; a `--no-verify` typed in a terminal or clicked in an IDE is invisible to it. Say "hatches are recorded when used through the agent", not "every commit is accounted for".

If you rename a hatch, rename it in the hook and in `CLAUDE.md` in the same commit — a documented override that silently does nothing reads as a broken hook.

### Enforcement Matrix

| Step | Enforced? | How |
|------|-----------|-----|
| 1. Ticket first | Yes | `commit-msg` — keyword-anchored `refs #N` required |
| 2. Worktree isolation | Yes | `pre-commit` gate 1 + `guard-force-app.sh` + `guard-force-app-bash.sh` |
| 2b. No nested worktrees | Yes | `guard-worktree-nesting.sh` |
| 2c. Explicit org identity | Workflow plus command guard | `org-preflight`; no automatic alias inheritance |
| 3a. Prettier / ESLint / PMD / Jest | Yes | `pre-commit` gates 2–5 |
| 3b. `/simplify` | **Manual** | Judgment step with no mechanical signal — the one gate that stays on the agent |
| 4a. Validate before merge | Yes | `record-validate.sh` + `guard-pr-merge.sh` |
| 4b. Squash merge | Yes | `guard-pr-merge.sh` |
| 4c. Deploy safety | Yes | `guard-sf-deploy.sh` + `guard-sf-flags.sh` |
| 4d. No retrieves | Yes | `guard-sf-flags.sh` + deny rules in `settings.json` — two independent layers; the deny rule is not env-bypassable |
| 4e. Deploy from a clean, pushed `main` | Yes | `guard-sf-deploy.sh` |
| 5. Deploy tracking | Yes | `auto-label-deploy.sh` — verifies success before recording |
| 6. Close ticket | Yes | `guard-issue-close.sh` |
| 7. Worktree cleanup | **Reported, not forced** | `session-status.sh` — reusing a worktree across deploys for follow-up fixes on the same ticket is supported |
| 8. Acceptance criteria + user green light | **Manual** | Nothing can check these for you |

Two of these are worth arguing with rather than routing around. `/simplify` is a judgment call — faking it with a marker file would be trivially gamed and would give false confidence. Acceptance criteria are the user's, not the tooling's.

---

## Express Mode

Issues labeled `express` skip user-testing wait between validate/merge/deploy — no human wait between steps, but validation and deploy still run for real.

**Mechanism:** The `auto-label-deploy.sh` hook detects `express` after a deploy and outputs a nudge to the agent confirming the ticket can be closed immediately once acceptance criteria are met, without waiting for a separate user-testing round.

**When to use:** Metadata-only changes, config tweaks, minor fields, permission sets.
**When NOT to use:** Apex logic, LWC features, flow business logic — anything needing manual verification.

---

## Related Skills

- **`github-repository-work`** — For creating and managing GitHub issues (Step 1).
- **`code-simplify`** — Code review (Step 3b).
- **`sf-deploy-engine`** — Once a project grows past one org/one branch (preprod/staging/production, an orchestration engine, promotion), that's a different skill. Don't try to bolt multi-environment concerns onto this one.

## Adapting to a New Project

This workflow assumes the project's `CLAUDE.md` (committed to the repo, not gitignored) has:
- The org alias and its mapping to `main`
- The GitHub account documented (for `gh auth switch`)
- The test class list (for `--tests`)
- The release commit, intended org ID, and deployment evidence required to establish parity
- **What lives in the org and not in the repo, and why** — Connected Apps, reports, anything the seed deliberately excluded or the round-trip check accepted as a known exception. This is the note that stops the next agent from "fixing" it.

Use `/sf-solo-devops setup` to bootstrap all of this from scratch. The setup command gathers project details via Q&A, installs hooks, configures permissions, and generates the CLAUDE.md workflow section with project-specific values filled in. If the org already has metadata, setup routes through `/sf-solo-devops seed` at Phase 2f before any of the guards go up.
