# Hooks reference

> **Inherited from the retired predecessor.** The design rules, the exit-code contract, and each
> hook's reasoning are unchanged and worth reading. What moved:
>
> | Then | Now |
> |---|---|
> | `.githooks/` tracked in the repo, armed by npm `prepare` | `~/.estate/githooks`, armed by `core.hooksPath`, re-armed every session |
> | `.claude/hooks/` tracked + repo `settings.json` | `~/.estate/claude-hooks/` + **user-level** `~/.claude/settings.json`, absolute paths |
> | `.claude/.deploy-log`, `.validate-log`, `.hatch-log` | `.git/estate/deploy-log`, `validate-log`, `hatch-log`, plus `approve-log`, `drift-log`, `ship-log`, `dod-state`, `client-checklist` |
> | hardcoded `main` | `trunk()` from `estate.trunk` |
> | hardcoded `gh` | the ticket adapter (`_ticket.sh`) |
> | `SOLO_*` escape hatches | `ALEY_*` (the `SOLO_`/`SW_` names still work) |
>
> **New in this skill:** `_config.sh` (config + the master mode gate), `_ticket.sh` (tracker
> adapter), `_block.sh` (the CLAUDE.md hash fence), `guard-closing-keywords.sh`,
> `guard-local-merge.sh`, `guard-push.sh`, `guard-devops-shared.sh`, `bin/estate-merge`,
> `bin/estate-devops-shared-status`, `bin/estate-devops-branch-status`, and
> `bin/estate-devops-package`.
>
> **The one structural change to understand:** sourcing `_lib.sh` now calls `sfds_gate()`,
> which **exits 0 immediately in any repo with no `estate.mode`**. That is why these hooks
> can live at user level and fire in every repo on the machine without affecting any of them.
> Set `HOOK_NO_GATE=1` before sourcing to opt out — only `install.sh` and `audit.sh` do.

---

Working copies of the whole stack. Everything is **tracked in the project repo**,
so a fresh clone and every new worktree get it automatically. The one genuinely
per-clone setting (`core.hooksPath`) arms itself.

```
githooks/                     -> <repo>/.githooks/       pre-commit, commit-msg
claude-hooks/                 -> <repo>/.claude/hooks/   _lib.sh + guards + automation + lifecycle
claude-settings-template.json -> <repo>/.claude/settings.json
```

## Install

```bash
cd <repo>
mkdir -p .githooks .claude/hooks
cp ~/.claude/skills/sf-delivery-standards/references/hooks/githooks/*        .githooks/
cp ~/.claude/skills/sf-delivery-standards/references/hooks/claude-hooks/*.sh .claude/hooks/
chmod +x .githooks/* .claude/hooks/*.sh
git config core.hooksPath .githooks
```

Merge `claude-settings-template.json` into `.claude/settings.json` (keep whatever
permissions the project already has), then add to `package.json`:

```json
"scripts": {
  "prepare": "git config core.hooksPath .githooks || true",
  "hooks:verify": "bash .claude/hooks/verify-git-hooks.sh"
}
```

and to `.gitignore`:

```
.claude/worktrees/
.claude/settings.local.json
.claude/.deploy-log
.claude/.validate-log
.claude/.dod-state
.claude/.pending-jobs
.claude/.hatch-log
```

Commit all of it. **Do not gitignore `.claude/hooks/`, `.claude/settings.json`
or `CLAUDE.md`.** `git worktree add` materialises tracked content only, so an
ignored file does not exist in any worktree — which is where all development
happens.

## Verify

```bash
npm run hooks:verify          # arms core.hooksPath, reports anything not enforced
git config core.hooksPath     # -> .githooks
```

Then start a Claude Code session. `verify-git-hooks.sh` and `session-status.sh`
run at SessionStart: silence from the first means everything is armed; the second
always prints where you are and whether `main === org`.

## The exit-code contract — read this before writing a guard

| Exit | PreToolUse behaviour |
|------|----------------------|
| 0 | allow; stdout goes to the transcript |
| **2** | **BLOCK**; stderr is fed back to Claude |
| 1, or anything else | non-blocking error — **the tool runs anyway** |

A guard that exits 1 prints a convincing refusal and then lets the action
through. Use `block()` from `_lib.sh`.

To feed guidance back to the model without failing anything, use `note()`. Plain
stderr on exit 0 reaches the user's transcript, not the model. Set `HOOK_EVENT`
to the firing event — `note()` stamps it, and a mismatched event name is dropped.

## What each file does

**`githooks/pre-commit`** — six gates, cheapest first, scoped to staged files
so a docs-only commit pays almost nothing: force-app-on-main; husky refusal plus
hook exec-bit repair; prettier (auto-fixes and re-stages, skipping
partially-staged files); ESLint; PMD; Jest. Symlinks `node_modules` from the main
clone so the node tools work inside a worktree.

During a DevOps Center WI-branch merge from a configured protected stage tip, the
effective staged set is `git diff --cached MERGE_HEAD`. This gates the net WI
delta instead of every file imported from the stage. A lint-staged-only chained
hook is run with the same diff base. More complex client hooks receive
`ALEY_MERGE_DIFF_BASE` and otherwise run unchanged.

**`githooks/commit-msg`** — force-app commits need a keyword-anchored issue ref
(`refs #N`, `fixes #N`). Keyword-anchored because a bare `#N` scan reads issue
numbers out of ordinary prose, and every downstream automation reads these refs
to decide what to label and what may be closed.

In DevOps Center delivery, the branch must be an exact `WI-*` branch and the
commit message must contain that same work-item id. The branch, commit, and
review are the association seam; there is no separate local association command.

**`claude-hooks/_lib.sh`** — sourced by all the others: event parsing (jq with a
python3 fallback), `block()` / `note()`, worktree detection by git topology,
main-clone resolution, heredoc-stripped command text, issue-ref extraction,
`deploy_log_shas()`, `record_hatch()`, and `sf_deploy_verdict()`.

**Guards (PreToolUse):**

| File | Blocks |
|---|---|
| `guard-force-app.sh` | editing `force-app/` outside a worktree |
| `guard-force-app-bash.sh` | shell writes to `force-app/` outside a worktree |
| `guard-sf-deploy.sh` | `deploy validate`; org-wide test levels; whole-tree deploys; unsafe direct-mode deploys; in isolated DevOps Center delivery, real deploys outside a clean linked `WI-*` worktree; in shared mode, every local real deploy |
| `guard-sf-flags.sh` | project-local `--target-org`/`-o`; `--use-most-recent`; `retrieve` into the **main** checkout; DevOps Center control commands without the configured explicit control-org alias and `--json` |
| `guard-worktree-nesting.sh` | `git worktree add` from inside a worktree |
| `guard-pr-merge.sh` | merges into an `estate.protected` branch; merges that disagree with `estate.squash` (`require`/`prefer` want `--squash`, `merge` refuses it); merging a deployable PR with no recorded validate |
| `guard-devops-handoff.sh` | a DevOps Center review handoff from the wrong branch, the main checkout, a dirty deployable tree, an unvalidated HEAD, or a `gh pr create` without the configured staging base |
| `guard-devops-shared.sh` | shared `dev/WI-*` creation from any base except the deployed integration ref; sensitive work while the centralized receipt is missing or mismatched; merging the accumulated integration branch into a WI package |
| `guard-closing-keywords.sh` | a closing keyword (`fixes`/`closes`/`resolves #N`) or Jira smart commit — this loop never closes a ticket on merge |

**Automation (never blocks):** `record-validate.sh` (logs successful dry runs —
the merge gate's proof), `auto-label-deploy.sh` (logs successful deploys to the
deploy-log and, in a note, asks the agent to comment the SHA + job id on the
ticket — it does not touch the tracker itself, and never closes anything),
`record-escape-hatch.sh` (logs overrides), `post-merge-nudge.sh` (hands over the
deploy command with the merged files listed).

Both recorders are registered under **PostToolUse and TaskCompleted**. The harness
auto-backgrounds Bash commands that exceed its timeout; when that happens,
PostToolUse fires with an incomplete result (the command is still running), so
the verdict cannot be read and the recording does not happen. TaskCompleted fires
when the backgrounded command actually finishes, carrying the real output, so the
recording happens then. The same scripts handle both events — they derive
`HOOK_EVENT` from the input JSON's `hook_event_name` field. Without the
TaskCompleted registration, a validate that takes longer than the Bash timeout
silently drops its proof, and the merge gate blocks a commit the org already
accepted.

In DevOps Center delivery, `auto-label-deploy.sh`, `post-merge-nudge.sh`, and
`stop-dod-check.sh` are intentionally inert. A successful deploy to the
development sandbox is local feedback, not evidence that a stage branch was
promoted. DevOps Center owns that lifecycle and its promotion evidence.

Shared DevOps Center delivery uses GitHub Deployments for the cross-clone receipt.
`estate-devops-shared-status` refreshes the integration ref and requires its SHA to equal the
latest successful deployment for the configured environment. `estate-devops-package` verifies
that each owned file still matches the accepted development head, applies that exact patch to the
generated WI branch, and writes `.estate/work-items/WI-######.json`. The handoff guard recomputes
the file set and blob identities from that ledger. `estate-devops-branch-status` proves each
permanent branch exists on GitHub and has deletion blocked before handoff. The repository's
centralized coordinator owns the actual shared-org merge, deployment, authentication, tests, and
post-deploy verification.

**Lifecycle:** `verify-git-hooks.sh` and `session-status.sh` (SessionStart),
`ensure-worktree-config.sh` (PreToolUse — sets `target-org` and links
`node_modules` on first use inside a worktree), `stop-dod-check.sh` (Stop —
refuses to end the turn while `main` is ahead of the org; fingerprinted so it
reports each state once). It does not nag about ticket closure (out of scope) or
open worktrees (reusing one across deploys for follow-up fixes is supported).

**Machine-local state** (all gitignored, all plain text in `.claude/`):

| File | Format | Purpose |
|---|---|---|
| `.deploy-log` | `<sha> <job-id> <utc>` | proof a commit reached the org |
| `.validate-log` | `<sha> <branch> <utc>` | proof a commit passed a dry run |
| `.pending-jobs` | `<job-id> <sha> <kind>` | async jobs this clone started |
| `.hatch-log` | `<utc> <kind> <sha> <detail>` | overrides used |
| `.dod-state` | one sha1 | Stop-hook dedupe |

Read `.deploy-log` through `deploy_log_shas()`; a consumer that treats a whole
line as a SHA stops matching and blocks every close.

If `.deploy-log` is lost, rebuild it from the org rather than hand-writing
entries: query `DeployRequest` where `CheckOnly = false AND Status = 'Succeeded'`
and match each timestamp to `git reflog`. Re-deriving a verified fact is fine;
inventing one defeats the gate.

## Design rules

**The org is the authority, not the console text.** `sf_deploy_verdict()`
resolves the deploy id — from the *command* first, since `deploy report --job-id
X` names the job and does not always echo it back — and asks the org for `status`
and `checkOnly`. Text is a fallback only. `"Status: Succeeded"` cannot tell a dry
run from a real deploy, and that distinction is the whole basis of the
proof-of-deploy gate.

- Verify `.result.id` equals the id you asked about. `deploy report` answers from
  a local cache when it can, so a mismatched id is *no answer*, not a verdict.
- Never `--use-most-recent` — in a multi-agent org it resolves to somebody else's
  deploy.

**`UNKNOWN` is not `FAILED`.** `FAILED` means `main` may be ahead of the org and
needs a fix-forward or revert. `UNKNOWN` usually means an `--async` deploy is
still in flight.

**Know that an event is yours before recording it.** `deploy report --job-id X`
serves both "collect the async job I started" and "look up an old job", and they
are identical from the command text. Registering in-flight jobs in
`.pending-jobs` and matching on job id separates them. Generally: widening what a
hook reacts to widens what can trigger it by accident, and for anything writing
an audit record, "it looked like it" is not enough.

**Recording is idempotent, and so is everything it triggers.** `auto-label-deploy.sh`
posts a GitHub comment; gate the side effects on the same check as the log write,
or a repeated `deploy report` posts a duplicate.

**Prose is not a command.** Guards match with heredoc *bodies* stripped and match
paths on token boundaries, so writing a commit message that explains a rule does
not trip it. Inside a command, a redirect's target is the **one token** after
`>`, not "anything up to a path I recognise" — Salesforce metadata is XML, so
`grep -rn "<fullName>" force-app/...` is routine work and must not read as a
write.

**Judge the target path, not the shell's cwd.** Any hook calling
`git rev-parse HEAD` is asserting its cwd is the subject of the command. For
anything taking a path argument that is wrong by default: resolve the tree from
the argument (`source_tree_root()`), and fall back to cwd only when there is no
path to read.

**Test against a throwaway clone with `gh` and `sf` stubbed on `PATH`. Never the
live repo.** `auto-label-deploy.sh` *executes* `gh issue edit` and `gh issue
comment`, and a clone's `origin` still resolves to the real project — a harness
without stubs posts to live tickets, and one that tidies up after itself deletes
real state. Assert at the end that the live repo's status fingerprint is
unchanged. A harness that mutates the system under observation cannot be trusted
about it.

> **Never configure a `WorktreeCreate` hook in a git repo.** That event is not a
> post-creation notification — Claude Code delegates worktree *creation* to it and
> reads the path from the hook's stdout. It exists so non-git VCS users can supply
> worktrees. Configuring one makes every `isolation: "worktree"` agent fail at
> spawn.

## Ticket closure is out of scope — no close gate

There is deliberately no close gate. A sandbox deploy does not make a ticket
"done"; tickets stay open until production, which is the `sf-deploy-engine`'s
domain, not this local loop's. So nothing here gates or performs a closure, and
the agent closes a ticket only when the user explicitly asks.

What remains is preventing an *accidental* close on merge: `guard-closing-keywords.sh`
blocks `fixes #N` / `closes #N` (and Jira smart commits) in commit messages and PR
titles/bodies, so a merge cannot silently close a ticket the loop meant to leave
open. `commit-msg` carries the same check for terminal-authored commits. Use
`refs #N` everywhere.

Jira work — including any transition the user does ask for — is the agent's, via the
Atlassian Rovo MCP; a hook cannot reach the MCP, so none of it lives in a hook.

## Project-specific bits to check after installing

Nothing needs editing for a standard project, but confirm:

- **Branch roles.** Direct delivery uses `estate.trunk` as the org-synced
  branch. DevOps Center delivery uses `estate.trunk` as the topology-derived
  first landing branch, protects both that branch and `main`, and permits local
  source deploys only from branches matching `estate.devops.branchpattern`.
  The development environment has no branch of its own.
- **Org alias.** `ensure-worktree-config.sh` reads it from the main clone's
  `.sf/config.json` — set that first (`sf config set target-org=<alias>`) or
  export `SOLO_ORG_ALIAS`.
- **Source root.** The guards assume `force-app/`.
- **Toolchain.** The prettier / ESLint / PMD / Jest gates skip with a warning when
  the binaries are absent, so a project without them still commits.
- **PMD ruleset.** `pre-commit` prefers `config/pmd-ruleset.xml` and falls back to
  the built-in categories. Point `npm run pmd` at the same `-R` so the hook and
  the manual command cannot disagree.

## Escape hatches

Deliberate, recorded, never silent. Each appends to `.claude/.hatch-log` and
emits a `note()`. **None of them block** — a hatch that argues with you is one
people route around; the log only makes using one a decision on record.

| Hatch | Effect |
|---|---|
| `SOLO_ALLOW_UNVALIDATED_MERGE=1` | skip the validate-before-merge gate |
| `SOLO_SKIP_DOD=1` | skip the Stop-hook Definition-of-Done check |
| `SOLO_ALLOW_RETRIEVE=1` | allow a retrieve into the **main** checkout — recorded, see below (a linked worktree needs no key) |
| `git commit --no-verify` | skip every pre-commit gate |
| `docs-only` / `no-deploy` issue label | close a ticket that produced no deploy |

All three env vars also answer to an `SW_`-prefixed alias. If you rename a hatch,
rename it in the hook and in `CLAUDE.md` together — a documented override that
silently does nothing reads as a broken hook.

There is deliberately **no** escape hatch on the force-app-outside-a-worktree
guards. That one is a wall, not a gate.

For a DevOps Center stage-sync commit, `--no-verify` is limited to a chained hook
that cannot safely honor the merge-aware comparison. Record the reason and keep
independent evidence for the net WI file list, focused gates, full suite, and
exact-commit Salesforce dry run.

**Retrieve-blocking lives in `guard-sf-flags.sh`, and only there.** Earlier
versions also carried a `permissions.deny` rule in `settings.json`, but a deny
rule in the user-level file fires in EVERY repo on the machine — it blocked
legitimate retrieves in unrelated Salesforce projects that never went through
init (requirement 1), and it could not be scoped to one project. It is gone;
`install.sh` retracts it from already-armed machines on re-arm. The guard is
gated, so it blocks retrieve-into-tree only in a managed repo — the correct
scope. And within a managed repo it blocks only the **main** checkout: a retrieve
run from a linked worktree is allowed, because it can only clobber that branch's
own files and the PR diff catches it before merge. `SOLO_ALLOW_RETRIEVE=1`
relaxes the main-checkout block, and the hatch records the override instead of
leaving it silent — for an operation that should happen about once a year.

The intended path in the main checkout needs neither key: retrieve into a scratch tree
(`--output-dir tmp-retrieve`, gitignored, cannot touch tracked files) from a
plain terminal, then bring the specific files across in a worktree on a ticket
and deploy them back. Initial seeding needs neither key either, because it runs
before this stack is installed. Both are covered in
[../seeding-guide.md](../seeding-guide.md).

**`git commit --no-verify` needs its own hook.** It bypasses every git hook by
definition, so no git hook can report its own bypass; `record-escape-hatch.sh`
catches it as a PreToolUse hook instead. That sees commands issued **through the
agent** — a `--no-verify` typed in a terminal or clicked in an IDE is invisible.
Claim "hatches used through the agent are recorded", not "every commit is
accounted for".

**Anchor hatch detection to a command position** — start of line or after a
separator, allowing leading `VAR=value` assignments. Otherwise writing *about* a
hatch records one, and a log with false entries gets ignored.
