# Workflow steps — full command sequences

Annotated commands for each phase. Placeholders use `<ANGLE_BRACKETS>`.

If `git config estate.delivery` returns `devops-center`, do not use the merge/deploy
sequence below. Use [devops-center.md](devops-center.md): the local loop ends with a pushed,
validated WI branch and an open DevOps Center review. DevOps Center owns the merge and stage
deployment.

Two substitutions run through everything below:

- **`<TRUNK>`** — `git config estate.trunk`. Often `main`; on a shared client repo where
  each consultant owns a sandbox, it is `sandbox/<alias>`. Never assume the literal string.
- **`<TICKET>`** — the ref in your tracker's format. `refs #42` under GitHub, `SFO-42`
  under Jira. `git config estate.ticket.pattern` is what `commit-msg` actually requires.

```bash
git config estate.trunk; git config estate.ticket.system; git config estate.host
```

Run the agent from the repo root or the ticket worktree, not from a parent directory that happens
to contain clones and worktrees. The user-level hooks intentionally exit without action outside a
configured repo. Confirm the project folder before relying on them:

```bash
git rev-parse --show-toplevel
```

> **Changed from the retired predecessor, and it will block you if you don't know:** `fixes #N` is
> **rejected** by `guard-closing-keywords.sh` and by `commit-msg`. Use `refs #N` everywhere.
> This local loop does not close tickets at all — closure is production/engine scope, and a
> ticket stays open until then. Close one only if the user explicitly asks.

---

## Step 1 — Create or find a ticket

### Existing-ticket intake

A supplied ticket is not proof that implementation is still needed. Establish its state before
creating a branch or editing metadata:

```bash
estate-ticket-status <TICKET>
git worktree list
git branch --all --list "*<TICKET>*"
git log --all --regexp-ignore-case --grep='<TICKET>' --oneline
```

Then inspect the tracker and host for the ticket, matching pull request, and deployment comment.
The helper reports facts available in this clone. Git branches and commits are shared after a
fetch. `.git/estate/validate-log` and `deploy-log` are deliberately clone-local, so no matching
entry means **unknown**, not "validation did not happen" or "deployment did not happen."

For deployment ancestry, use the commit that landed on `<TRUNK>`, not the feature head. A merge or
squash creates a different trunk commit. A later deploy receipt proves the ticket deployed when
the landed commit is its ancestor. On another machine, the tracker deployment comment or the
Salesforce deployment record is shared evidence when this clone has no receipt.

If the ticket is already delivered, report that result and stop. If work exists only on an open
branch or worktree, continue it instead of opening a duplicate. If evidence conflicts, state what
is confirmed and what remains unknown before changing anything.

**GitHub** (`ticket.system=github`):
```bash
gh issue list --search "keyword"
gh issue create --title "feat: description" --body "Details"
```

**Jira** (`ticket.system=jira`): use the Atlassian Rovo MCP from the agent — there is no CLI.
Search with `mcp__*__searchJiraIssuesUsingJql` (`project = <KEY> AND statusCategory != Done`)
and create with `mcp__*__createJiraIssue`. The `mcp__*__` prefix is matched on the tool suffix
because the server segment is an opaque id. A hook cannot reach the MCP, so these are the
agent's to call directly.

Note the ref. It goes in the branch name and every commit.

---

## Step 2 — Create a worktree

With `Agent` + `isolation: "worktree"` this is already done — that agent is *in* a worktree
and must not create another. By hand, **from the main checkout**:

```bash
git worktree add ../project-42 -b feat/42-short-description
cd ../project-42
```

Branch naming: `feat/<ref>-description` or `fix/<ref>-description`.

`ensure-worktree-config.sh` does the rest on the first `sf`/`npm` command in the worktree.
Shown so you know what it is doing and why:

```bash
sf config set target-org=<ORG_ALIAS>              # .sf/ is gitignored, so a fresh worktree
                                                  # has none and sf falls through to the
                                                  # machine's GLOBAL default org
ln -s <main-clone>/node_modules node_modules      # gitignored too; prettier/eslint/jest
                                                  # resolve plugins relative to the tree
# stealth mode only: CLAUDE.md and .forceignore are untracked, so a worktree gets neither
ln -s <main-clone>/CLAUDE.md CLAUDE.md
```

Am I in a worktree? One plain command — inside a worktree-isolated agent the harness
refuses compound ones:

```bash
git rev-parse --absolute-git-dir
```

`…/<repo>/.git` is the main checkout. `…/<repo>/.git/worktrees/<name>` is a worktree. Do
**not** test by looking for `.claude/worktrees/` in the path: a worktree created anywhere
else is just as much a worktree, and the guards honour it.

---

## Step 3 — Quality gates

### 3a — Prettier, ESLint, PMD, Jest

All four run in `pre-commit` on staged files, so **the commit is the gate**. Run them early
only for faster feedback:

```bash
npm run lint
npm test
pmd check --file-list <(git diff <TRUNK> --name-only -- '*.cls' '*.trigger') \
  -R config/pmd-ruleset.xml -f text        # or ~/.estate/templates/pmd-ruleset.xml
```

Prettier's behaviour depends on `estate.format`: `client` rewrites and re-stages using
*their* config; `check` reports and never writes; `off` skips. PMD blocks or advises per
`estate.pmd`.

### 3b — /simplify

Run the `/simplify` skill: reuse, architecture, efficiency, Salesforce patterns. Fix what it
finds. Skip only for trivial metadata (one field, a label).

**This is the one quality gate no hook can enforce** — a judgment step with no mechanical
signal, so it stays on you. Do not fake it with a marker file.

### 3c — Commit

```bash
git add -A
git commit -m "feat: description (refs #42)"     # GitHub
git commit -m "feat: description (SFO-42)"        # Jira
```

`refs #N` on **every** commit including the final squash. Never `fixes`/`closes`/`resolves`,
and never a Jira smart-commit command (`#done`, `#comment`, `#time`) — both are blocked, and
[ticket-adapters.md](ticket-adapters.md) explains why.

---

## Step 4 — Validate, merge, deploy (atomic — do not reorder)

The delivery engine serializes integration and later environments. The local invariant still
applies at the sandbox boundary: before landing a ticket, confirm the current trunk has a recorded
successful deploy. If another developer has just merged, wait for that deploy to finish before
merging the next ticket. Salesforce serializes deploy jobs, but it does not serialize Git merges.
An intentional batch is the exception: validate each ticket, merge the planned batch, then deploy
the union of changed files and tests once, as described below.

### 4a — Pick the tests

For each changed Apex class, include its `*Test` counterpart. For triggers and handlers,
cast wider — include tests that do DML on the affected SObject.

```bash
git diff <TRUNK> --name-only -- force-app/
grep -rl "FooService" force-app --include="*Test.cls"
```

`NoTestRun` is valid whenever the change cannot affect Apex results: metadata-only, CSS/HTML
LWC, labels, permissions, layouts, static resources — even an Apex comment edit.

### 4b — Validate against the org, from the worktree

```bash
sf project deploy start --dry-run \
  --source-dir force-app/main/default/classes/ChangedClass.cls \
  --source-dir force-app/main/default/classes/ChangedClassTest.cls \
  --source-dir force-app/main/default/objects/MyObj__c/fields/NewField__c.field-meta.xml \
  --test-level RunSpecifiedTests --tests TestA TestB
```

This **is** the merge gate. If it fails, iterate here. Do not merge.

- **Only changed files.** `--source-dir force-app` is blocked: whole-tree deploys are slow,
  surface unrelated failures, and make it impossible to tell what the org received for this
  ticket.
- **`start --dry-run`, never `deploy validate`.** `validate` is the production quick-deploy
  path and rejects `NoTestRun`.
- **Commit first, then validate.** The record is per-commit, and the merge gate checks the
  head commit. Commit again afterwards and you re-validate.
- **Never `--target-org`.** The org is configured project-locally.

### 4c — Land it on trunk

The command depends on `estate.host`. All of them are squash-by-default: one ticket, one
commit on trunk, so the refs the automation reads stay in one place.

**github**
```bash
gh pr create --base <TRUNK> --title "feat: description (refs #42)" --body "..."
gh pr merge --squash --delete-branch
```

**gitlab**
```bash
glab mr create --target-branch <TRUNK> --title "feat: description (SFO-42)" --description "..."
glab mr merge --squash --remove-source-branch
```

**azure**
```bash
az repos pr create --target-branch <TRUNK> --title "feat: description (SFO-42)"
az repos pr update --id <N> --squash true --status completed
```

**bitbucket** — no CLI merge surface exists, so the gate moves one step earlier: the **push**
requires a recorded validate, and then a human merges in the browser.
```bash
git push -u origin HEAD          # guard-push.sh checks the validate here
# then open and merge the PR in Bitbucket
```

**none** — no remote, so `estate-merge` stands in for the PR. It shows you the diff,
verifies the dry run, squashes with the right ticket ref, and records the approval.
```bash
git checkout <TRUNK>
estate-merge feat/42-short-description
```
A hand-written `git merge --squash` is blocked, deliberately: the gate is what records that a
human read the diff, and with no PR there is nothing else doing that job.

### 4d — Deploy from trunk

Same files, same tests as the validate.

```bash
git checkout <TRUNK> && git pull      # omit `git pull` when host=none
sf project deploy start \
  --source-dir force-app/main/default/classes/ChangedClass.cls \
  --source-dir force-app/main/default/classes/ChangedClassTest.cls \
  --test-level RunSpecifiedTests --tests TestA TestB
```

The `git pull` is not optional. The deploy guard blocks a trunk that is behind the remote
(you would ship an older tree than you merged), ahead of it (unpushed code reaching the org),
or carrying uncommitted `force-app/` changes.

**Async, for multi-agent orgs** — capture the job id immediately and never use
`--use-most-recent`, which resolves to whatever the org saw last, possibly another agent's
deploy:
```bash
JOB_ID=$(sf project deploy start --source-dir <files> \
  --test-level RunSpecifiedTests --tests TestA --json --async | jq -r '.result.id')
sf project deploy report --job-id "$JOB_ID"
```

### 4e — If the deploy fails

Restore the invariant first, debug second.

- **Fixable in under five minutes?** Fix forward: new worktree, fix, validate, merge, deploy.
- **Needs investigation?** Revert, then debug:
  ```bash
  git revert HEAD --no-edit && git push
  sf project deploy start --source-dir <same files> \
    --test-level RunSpecifiedTests --tests <same list>
  ```
  This restores `<TRUNK> === org` immediately. Then rebase the worktree and debug there.

---

## Step 5 — Record the deploy on the ticket

After a real deploy, record it on the ticket with a **comment** — never a transition or a
close. This is the loop's only ticket write, and the **agent** does it (a hook cannot reach
the MCP).

```bash
# GitHub
gh issue comment 42 --body "Deployed in $(git rev-parse --short HEAD) (deploy <job-id>)."

# Jira — via the Atlassian Rovo MCP, not a CLI:
#   mcp__*__addCommentToJiraIssue
#   body: Deployed in <short sha> (deploy <job-id>).
```

`auto-label-deploy.sh` records the deploy in the deploy-log and, in a note, asks you to post
this comment. It does **not** touch the tracker itself, and it never labels, transitions, or
closes.

**The ticket stays open.** A sandbox deploy is not "done" — closure is production/engine scope
(the `sf-deploy-engine`'s domain), so nothing in this local loop closes a ticket. Close one
only if the user explicitly asks: `gh issue close N`, or `mcp__*__transitionJiraIssue` for Jira.

If the tracker is the client's (`ticket.remote=client`), do not write to it automatically —
follow their process if commenting has been agreed.

---

## Step 6 — Clean up

```bash
git worktree remove ../project-42
git branch -d feat/42-short-description
```

Due when the ticket's work is finished, not after every deploy. Keeping a worktree open across
deploys for follow-up fixes on the same ticket is supported and no hook nags about it.

Two things when reusing a branch after its squash merge:

```bash
git merge <TRUNK>                       # or: git fetch && git reset --hard origin/<TRUNK>
```
The squash put your content on trunk under a commit the branch has never seen. Without this,
the next PR's diff re-shows all the original work. Then **re-validate** — the merge gate is
per-commit, and you just added one.

---

## Quick reference — the whole sequence

```
1. ticket        gh issue create            | Rovo MCP createJiraIssue
2. worktree      Agent isolation: "worktree" | git worktree add ../p-N -b feat/N-desc
3. implement  →  /simplify  →  commit "…(refs #N)"      # 4 gates run in pre-commit
4. validate      sf project deploy start --dry-run --source-dir <changed> --test-level RunSpecifiedTests --tests …
5. land          gh pr merge --squash  | glab mr merge --squash | estate-merge <branch>
6. deploy        git checkout <TRUNK> && git pull && sf project deploy start <same files, same tests>
7. record        comment the SHA + job on the ticket   (gh issue comment | Rovo MCP addCommentToJiraIssue)
8. verify        acceptance criteria + user green light
9. clean up      git worktree remove <path>
```

The loop ends at deploy: the ticket stays open (closure is production/engine scope), so there
is no close step. Steps 3–9 are enforced in both directions where a gate applies: the guards
block the wrong thing, and the Stop hook refuses to end a turn with trunk ahead of the org.
The two things nothing can check for you are `/simplify` and whether the feature does what the
ticket actually asked for.

---

## Orchestrating a batch of related tickets

A common pattern: hand an orchestrator several related tickets, have it build them in parallel
worktrees (often with per-subagent model choices — a cheaper model for the simple ones), then
land and QA them together. This composes with the loop above; the guards already support it. The
invariant is unchanged, so only two things need care that a single-ticket run never faced:

1. **Parallel dev + parallel validate — fine.** Each ticket develops in its own worktree and
   validates there (validate is per-branch). Nothing serializes until the landing.

2. **Batch-merge and batch-deploy are ONE move — never leave trunk merged-but-undeployed.** The
   invariant is `trunk === org`; if you merge the batch and stop, trunk is ahead of the org and
   `stop-dod-check` will (correctly) nag. So merge the batch, then immediately deploy it as one
   deploy — the **union of the changed files + union of the `RunSpecifiedTests`**, never
   `--source-dir force-app`. The deploy record/comment references all the ticket refs.

3. **If trunk moved during the hold, rebase + re-validate before merging.** A long hold lets
   trunk advance underneath the branches (an earlier ticket in the batch, or a teammate). A
   rebase makes new commits, and the validate record is **per-commit** — so a rebased branch is
   no longer validated until you re-run the dry run on the new commits.

4. **QA the deployed suite together, then one sign-off.** Interactions between related tickets
   only surface with all of them in the org, so run `estate-ac-qa` across the batch after the
   batch deploys, fix-forward any FAIL while it is cheap, then take the single acceptance
   sign-off. This is a case where batch QA is *better* than per-ticket, not just faster.

The `fetch_trunk` refresh (session start and pre-deploy) makes a concurrent landing safer, but
the orchestrator should still sequence the merge+deploy of each ticket rather than fire them at
once — there is one trunk and one org, and the deploy step is single-writer.
