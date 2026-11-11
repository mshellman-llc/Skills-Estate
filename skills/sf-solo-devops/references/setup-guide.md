# Setup Guide — `/sf-solo-devops setup`

This guide is triggered when the user runs `/sf-solo-devops setup` (or any args containing "setup", "install", "bootstrap", or "init").

The setup command bootstraps a solo-developer, single-org Salesforce project with the full enforcement stack: SFDX scaffold, dev toolchain, git hooks, Claude hooks, Claude Code settings, and the workflow section embedded directly in the project's CLAUDE.md.

Setup can finish locally without an org. Record the target as unconfigured and skip org discovery, seeding, validation, and deployment until the user identifies a target. Existing CLI aliases are not implied authorization.

This skill handles both fresh projects (no repo yet) and existing projects (add enforcement to what's already there) — for exactly one org, one branch (`main`).

**If the project needs more than one org/environment** (dev + staging + prod, or any real promotion pipeline), stop here and use `/sf-deploy-engine setup` instead. This skill has no concept of promotion, staging, or an orchestration engine, and deliberately doesn't — that complexity belongs to the engine skill, not bolted onto the solo workflow.

---

## Phase 0 — Detect Project State

Before asking questions, auto-detect what already exists:

```bash
# Project structure
test -f sfdx-project.json && echo "SFDX: exists" || echo "SFDX: missing"
test -d force-app && echo "force-app: exists" || echo "force-app: missing"
test -d .git && echo "git: exists" || echo "git: missing"
test -f package.json && echo "package.json: exists" || echo "package.json: missing"

# Seeding state — has the org's metadata ever been pulled in?
find force-app -name '*-meta.xml' 2>/dev/null | wc -l    # 0 = unseeded
test -f .forceignore && echo ".forceignore: exists" || echo ".forceignore: MISSING (Phase 2f)"
ls manifest/*.xml 2>/dev/null

# Is this actually a multi-env / engine project in disguise?
test -f pipeline.yml && echo "pipeline.yml found — this is sf-deploy-engine territory, not sf-solo-devops"

# Org
# Read the project's documented intended target; do not select from cached aliases.
# With no confirmed target, continue local setup and skip org commands.

# GitHub
gh auth status 2>&1
git remote -v 2>/dev/null

# Toolchain
which pmd 2>/dev/null && pmd --version 2>/dev/null || echo "PMD: not found"
test -f node_modules/@salesforce/sfdx-lwc-jest/bin/sfdx-lwc-jest && echo "Jest: installed" || echo "Jest: not installed"

# Existing hooks
ls -la .githooks/ 2>/dev/null
git config core.hooksPath 2>/dev/null || echo "core.hooksPath: unset (git hooks NOT armed)"
ls -la .git/hooks/pre-commit .git/hooks/commit-msg 2>/dev/null   # legacy untracked install
ls -la .claude/hooks/*.sh 2>/dev/null

# husky would silently disable every git hook
test -d .husky && echo "husky present — MUST be removed"
grep -q '"husky"' package.json 2>/dev/null && echo "husky in package.json — MUST be removed"
test -f .claude/settings.json && echo "Claude settings: exists" || echo "Claude settings: missing"
test -f .claude/CLAUDE.md && echo "CLAUDE.md: exists" || echo "CLAUDE.md: missing"

# Test classes
ls force-app/main/default/classes/*Test*.cls 2>/dev/null | xargs -I {} basename {} .cls | sort | tr '\n' ' '
```

If `pipeline.yml` exists, stop and redirect to `sf-deploy-engine`. Otherwise use these results to pre-fill Q&A defaults and skip phases that are already done.

**Read the seeding state before anything else.** An empty `force-app/` against an
org that has metadata is the one combination that changes the shape of setup: it
means Phase 2f runs, and it means Phase 3 must wait for it. A `force-app/` that
already has content is *not* a seeding candidate — pulling the org over it is the
exact operation the enforcement stack exists to prevent, whether or not the stack
is installed yet.

---

## Phase 1 — Gather Project Details (Q&A)

Use the host's available question tool or a concise question to gather material missing details. Do not repeat questions already answered. Present as a single conversational block with auto-detected defaults filled in. Don't ask one question at a time — give the user a clear picture of what you found and what you need.

### Required

1. **Project name and purpose** — What is this project? One sentence. (Used for the CLAUDE.md header and context.)

2. **Org target, when available** — Record the user-confirmed connection and exact intended org ID.
   - An org is optional for local setup. Use `unconfigured` when none is available.
   - Before an org operation, run `org-preflight` on the same explicit connection.

3. **GitHub account** — Which GitHub account owns this repo?
   - Auto-detect from `gh auth status` and offer as default.
   - If the user has multiple accounts (e.g., personal + work), ask which is the project account and which is the default to switch back to.

If the user describes more than one org/environment during this Q&A, stop and point them at `sf-deploy-engine` instead of trying to accommodate it here.

### Optional (offer but don't block on)

4. **Business context** — Brief description of what this system does, who uses it, key domain concepts. (Embedded in CLAUDE.md for agent context.) Example: "Pricing system for consulting engagements. Dual pricing approach — bottoms-up scope items + tops-down timeline."

5. **High-level goals** — 2-4 sentences about the business problem, who it serves, and what success looks like. Example: "Replace FSL-based field data capture ($650/user/mo) with metadata-driven forms ($25/user/mo). Support offline data entry."

6. **Architectural context** — Any known constraints, data model decisions, key objects, security model, or guardrails. These become additional CLAUDE.md sections.

7. **MCP servers to avoid** — Any connected MCP tools that should NOT be used (e.g., production-only org tools). List them as deny patterns.

---

## Phase 2 — Scaffold (skip if project already exists)

Only run this phase if `sfdx-project.json` doesn't exist.

### 2a — SFDX Project

```bash
sf project generate project --name PROJECT_NAME --template standard
cd PROJECT_NAME
```

Update `sourceApiVersion` in `sfdx-project.json` to the version supported by the intended project and toolchain. Do not insert an assumed current version.

### 2b — Git + GitHub

```bash
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Salesforce
.sf/
.sfdx/
.localdevserver/
deploy-options.json
**/lwc/jsconfig.json

# Dependencies
node_modules/

# Coverage
coverage/

# Logs
*.log
npm-debug.log*

# PMD
.pmdCache

# ESLint
.eslintcache

# OS
.DS_Store
Thumbs.db

# Environment
.env

# Temporary
tmp-retrieve/
tmp-destructive/
EOF

# Initial commit — CLAUDE.md is added in Phase 4 and gets committed here too, deliberately.
git add -A
git commit -m "chore: initialize SFDX project"
```

**Do not add `CLAUDE.md` to `.gitignore`.** `git worktree add` only ever materializes tracked content from the branch — an untracked or gitignored `CLAUDE.md` silently never exists in any worktree an agent creates for itself, which means every worktree-isolated task runs with zero project instructions. If there's genuinely personal content that shouldn't be shared, split it into a separate untracked file and keep the workflow rules committed.

If no remote exists, create the GitHub repo:
```bash
gh auth switch --user <PROJECT_GITHUB_ACCOUNT>
gh repo create <ACCOUNT>/<PROJECT_NAME> --private --source=. --push --description "<PROJECT_DESCRIPTION>"
gh auth switch --user <DEFAULT_GITHUB_ACCOUNT>
```

### 2c — Dev Toolchain (npm)

```bash
npm init -y
npm install --save-dev \
  @salesforce/sfdx-lwc-jest \
  @lwc/eslint-plugin-lwc \
  @salesforce/eslint-config-lwc \
  eslint \
  prettier \
  @prettier/plugin-xml
```

Update `package.json` scripts:
```json
{
  "scripts": {
    "test": "sfdx-lwc-jest",
    "test:watch": "sfdx-lwc-jest --watch",
    "test:coverage": "sfdx-lwc-jest --coverage",
    "lint": "eslint **/lwc/**/*.js",
    "prettier": "prettier --write \"**/*.{cls,css,html,js,json,md,xml,yaml,yml}\"",
    "prettier:verify": "prettier --check \"**/*.{cls,css,html,js,json,md,xml,yaml,yml}\""
  }
}
```

Create `jest.config.js`:
```js
const { jestConfig } = require("@salesforce/sfdx-lwc-jest/config");
module.exports = {
  ...jestConfig,
  modulePathIgnorePatterns: ["<rootDir>/.localdevserver"],
};
```

### 2d — PMD Verification

PMD is used for Apex static analysis in Step 3a of the workflow.

```bash
which pmd 2>/dev/null && pmd --version 2>/dev/null
```

If PMD is not installed, inform the user:
```
PMD is not installed. It's needed for Apex static analysis (Step 3a).

Install via Homebrew:
  brew install pmd

Or download from https://pmd.github.io/

Local setup can continue, but Apex static analysis remains pending until the tool is available. Do not report PMD passed or claim the entire quality gate is ready.
```

Do not block setup on PMD installation. Note its absence in the summary.

### 2e — Org connection, when available

Skip this phase when no target is confirmed. Keep the project's local preparation usable without setting a default org. When a target is available, run `org-preflight` against the exact intended org ID and retain its private receipt. Use that explicit connection on every subsequent org command; do not copy a machine default into a worktree.

### 2f — Baseline Seed (existing orgs only)

**Skip if there is no confirmed org, the org is empty, or the user is starting from scratch.** Go to Phase 3.

If the org has metadata that should become the repo's baseline, read
[seeding-guide.md](seeding-guide.md) and work through it now. Do not improvise a
`sf project retrieve start --source-dir force-app` here — that pulls every
standard object, every user-authored report, every managed-package component and
every unportable Connected App into the first commit, and each one of those is a
thing somebody has to delete later while wondering whether it was load-bearing.

The guide covers, in order: `.forceignore` first, a manifest generated from the
org with exclusions applied at build time, a manifest prune, the retrieve, a
tree prune for standard-object noise, a review-and-round-trip checkpoint, and one
commit.

**The ordering is load-bearing, not stylistic.** Seeding happens here, before
Phase 3, for two reasons:

- Phase 3 installs `guard-sf-flags.sh` and the `permissions.deny` rules that
  block `sf project retrieve` outright. Seeding first means never arguing with a
  guard that is correct.
- The repo is empty, so a retrieve cannot clobber anything. That stops being
  true the moment there is a first commit.

Budget real time for it. On a mature org the retrieve alone runs several minutes
and the review checkpoint is worth twenty. This is the commit the whole project
is diffed against.

When the guide hands back, continue to Phase 3.

---

## Phase 3 — Install Enforcement Stack

Everything here is **tracked in the repo**. Nothing lands in `.git/hooks/`, because that directory is not tracked and would have to be reinstalled per clone — the exact silent-failure mode this stack is designed to avoid.

`<SKILL_DIR>` below is the base directory of this skill (shown at the top of the skill load message).

### 3a — Copy the hooks in

```bash
# From the project root
mkdir -p .githooks .claude/hooks
cp <SKILL_DIR>/references/hooks/githooks/*        .githooks/
cp <SKILL_DIR>/references/hooks/claude-hooks/*    .claude/hooks/
chmod +x .githooks/* .claude/hooks/*.sh
git config core.hooksPath .githooks
```

Inspect existing hooks and preserve their behavior before changing `core.hooksPath`. Back up the prior configuration and reconcile any custom checks; do not delete legacy hooks automatically.

### 3b — Make the arming survive a fresh clone

`core.hooksPath` is local config and does not clone. Two mechanisms cover it, and you want both:

```json
"scripts": {
  "prepare": "git config core.hooksPath .githooks || true",
  "hooks:verify": "bash .claude/hooks/verify-git-hooks.sh",
  "pmd": "pmd check -d force-app/main/default/classes -R config/pmd-ruleset.xml -f text",
  "permset": "python3 scripts/gen-permset.py",
  "permset:write": "python3 scripts/gen-permset.py --write"
}
```

`prepare` runs on `npm install`; `verify-git-hooks.sh` re-checks and repairs at every Claude Code session start.

**Point `npm run pmd` and the pre-commit PMD gate at the same `-R`.** The hook prefers `config/pmd-ruleset.xml` and falls back to the built-in categories with a warning if it is absent, so this works either way — but if the two disagree about thresholds, an agent gets a clean manual run and a blocked commit, and reasonably concludes the hook is broken.

A project ruleset is worth adding once PMD's class-level aggregate rules (cyclomatic complexity, class size) start firing on ordinary Apex: those are tuned for whole classes, and **retune them rather than suppressing the categories**, or the security and error-prone rules go with them.

The reference hooks expect `.githooks/` to be the hook path. If a hook manager is already installed, reconcile its checks and choose one deliberate configuration before enabling this stack. Preserve the existing setup until the replacement has been tested.

### 3c — gitignore the machine-local state (and nothing else)

```
.claude/worktrees/
.claude/settings.local.json
.claude/.deploy-log
.claude/.validate-log
.claude/.dod-state
.claude/.pending-jobs
.claude/.hatch-log
```

Everything else under `.claude/` stays tracked. `git worktree add` materialises tracked content only, so an ignored hook or CLAUDE.md simply does not exist in any worktree.

### 3d — Claude Code Settings

Read the existing `.claude/settings.json` (or create one). Merge in from `claude-settings-template.json`:

- `permissions.deny` — the `sf project retrieve` deny rules
- `hooks.SessionStart`, `hooks.PreToolUse`, `hooks.PostToolUse`, `hooks.Stop`

Do **not** add a `WorktreeCreate` entry. See the warning in [hooks/README.md](hooks/README.md).
- Preserve the user's existing permission choices. The template does not grant blanket Bash access.

**Do NOT overwrite** existing permissions, hooks, or other settings. Merge additively.

### 3e — Check the project-specific assumptions

The hooks are generic, but confirm:

- **Branch name.** `guard-sf-deploy.sh` and `stop-dod-check.sh` assume `main`.
- **Org identity.** Org operations require an explicit confirmed target and `org-preflight`. `ensure-worktree-config.sh` only handles local Node dependencies.
- **Source root.** The guards assume `force-app/`.

### 3f — Verify installation

Run synthetic hook events against the installed copies. Include both allowed local preparation and refused missing-target cases. A path or settings entry does not prove host-level enforcement. GitHub comments remain off unless the user explicitly authorizes them and the project sets `SOLO_GITHUB_UPDATES=1`.

```bash
npm run hooks:verify          # arms core.hooksPath, reports anything not enforced
git config core.hooksPath     # -> .githooks
ls -l .githooks .claude/hooks # all executable
```

`verify-git-hooks.sh` checks that every hook named in `settings.json` exists, is executable and has a shebang, so a silently-skipped guard is reported rather than assumed working. Report the results to the user.

### 3g — Generated permission set

Install this if the project will ever have more than one agent building at a time. The project
permission set is the one file every parallel worktree touches, and generating it from the source
tree removes both failure modes at once — the merge conflict *and* the deployed-but-invisible field.
See [tools/README.md](tools/README.md) for the reasoning.

```bash
mkdir -p scripts
cp <SKILL_DIR>/references/tools/gen-permset.py scripts/gen-permset.py
python3 scripts/gen-permset.py --init          # writes config/permset-gen.json, prints the config reference
```

Fill in `api_name` and `label` (one permission set, carrying everything — object perms, every
field, tabs, record types, apps, Apex classes). Then confirm it runs:

```bash
npm run permset                                # check mode — safe in the main clone, writes nothing
```

The npm scripts went into `package.json` in 3b. Both `scripts/gen-permset.py` and
`config/permset-gen.json` are tracked, like everything else here — a worktree only materializes
tracked content.

**Do not create the permission set by hand first.** The first ticket that needs it runs `--write`
inside its own worktree; from then on the file is generated and never edited.

---

## Phase 4 — Generate CLAUDE.md Workflow Section

Read [claude-md-template.md](claude-md-template.md). Fill in all `{{PLACEHOLDER}}` values with the answers from Phase 1. Two come from elsewhere:

- `{{PERMSET_API_NAME}}` from `config/permset-gen.json` (Phase 3g).
- `{{ORG_ONLY_METADATA}}` from Phase 2f — the exclusions actually applied, plus any round-trip failure you accepted as a known exception. Write the reason next to each, not just the name. If there is no org, say `Unconfigured; no org metadata inspected.` If seeding was skipped because the confirmed org was empty, say so: `Nothing — this project started from an empty org and the repo has been the source of truth from the first commit.`

Then:

- If `.claude/CLAUDE.md` (or the project's `CLAUDE.md`) doesn't exist, create it with the filled template.
- If it already exists, read it and check if it already has a workflow section (look for `## Workflow` or `main === org`). If so, ask the user whether to replace or skip. If no existing workflow section, append the filled template.
- **Confirm it is not listed in `.gitignore`.** If it is, remove that entry and tell the user why (see Phase 2b note above).

**Key principle:** The workflow rules live IN the CLAUDE.md, not as a reference to the skill. CLAUDE.md is always loaded into context; skills are loaded on demand. Critical workflow rules must be in CLAUDE.md for reliable enforcement — and it must be committed, or worktrees never see it.

The test class list is auto-detected in Phase 0. If tests exist, include the full `--test-level RunSpecifiedTests --tests ...` block. If no tests exist yet, include a placeholder noting they should be added as Apex classes are created.

---

## Phase 5 — Final Commit + Summary

If any files were created or modified (hooks, settings, CLAUDE.md), commit them:

```bash
gh auth switch --user <PROJECT_GITHUB_ACCOUNT>
git add -A
git commit -m "chore: add devops enforcement stack (hooks, settings, CLAUDE.md)"
git push
gh auth switch --user <DEFAULT_GITHUB_ACCOUNT>
```

Print a summary of everything installed:

```
Setup complete for PROJECT_NAME:

  Project scaffold:
    sfdx-project.json         — SFDX source project (API vXX.0)
    package.json              — Jest, ESLint, Prettier
    jest.config.js            — LWC Jest configuration

  Quality gate tools:
    PMD                       — installed (vX.X) / NOT INSTALLED (install via: brew install pmd)
    Jest                      — installed (npm test)

  Git hooks (tracked, armed via core.hooksPath=.githooks):
    .githooks/pre-commit      — force-app-on-main, husky refusal, hook exec bits,
                                prettier, eslint, PMD, jest (staged files only)
    .githooks/commit-msg      — keyword-anchored issue ref (refs #N / fixes #N)

  Claude hooks (tracked):
    _lib.sh                     — shared helpers; block() exits 2, the only code that blocks
    guard-force-app.sh          — Edit/Write on force-app/ outside a worktree
    guard-force-app-bash.sh     — shell writes to force-app/ outside a worktree
    guard-sf-deploy.sh          — reviewed source boundaries,
                                  deploys off main / from a dirty or unpushed main
    guard-sf-flags.sh + .py     — explicit target, recorded job ID, retrieve boundary
    deploy-verdict.py          — structured result interpretation, no org query
    guard-worktree-nesting.sh   — worktree inside a worktree
    guard-pr-merge.sh           — squash-only, no merge without a recorded validate
    guard-issue-close.sh        — no close without a recorded deploy
    record-validate.sh          — logs successful dry runs
    auto-label-deploy.sh        — logs structured deployment results; GitHub updates opt-in
    post-merge-nudge.sh         — hands over the deploy command after a merge
    verify-git-hooks.sh         — arms and audits the stack at session start
    session-status.sh           — location, dirty force-app, main-vs-org drift
    ensure-worktree-config.sh   — local node_modules link; no org configuration
    stop-dod-check.sh           — blocks the turn while the DoD is incomplete

  Claude settings:
    .claude/settings.json     — deny rules for sf project retrieve + hook config

  Baseline (existing orgs only):
    .forceignore              — what this project does NOT track, by reason class
    manifest/seed.xml         — the pruned manifest the baseline was retrieved with
    force-app/                — N components, round-trip verified / N exceptions noted

  Generated metadata:
    scripts/gen-permset.py    — permission set derived from the source tree
    config/permset-gen.json   — no_delete / read_only / standard-object grants
    npm run permset           — check mode (agents); permset:write is worktree-only

  Arming:
    package.json "prepare"    — git config core.hooksPath .githooks on npm install
    npm run hooks:verify      — manual re-check

  CLAUDE.md:
    CLAUDE.md                 — workflow section with project-specific values, committed (not gitignored)

  Confirmed org: ORG_ALIAS / unconfigured; no live validation performed
  GitHub account: GITHUB_ACCOUNT
  Test classes: N detected / none yet

  Next: create your first GitHub issue and start building.
```

---

## Idempotency

Running setup again on an already-configured project should be safe:
- Phase 0 detects what exists and skips what's already done
- Phase 2 (scaffold) skips entirely if `sfdx-project.json` exists
- **Phase 2f (seed) is the one phase that is NOT idempotent, and must never re-run
  against a non-empty `force-app/`.** Re-seeding would pull org state over tracked
  content and silently revert anything deployed but not yet retrieved. Phase 0's
  component count is the gate: non-zero means skip, no exceptions. Bringing one
  thing across from the org later is a ticket, not a re-run — see
  [seeding-guide.md](seeding-guide.md) § Re-seeding after the guards are up.
- `.forceignore` is treated like the hooks: overwritten from the template only if
  the user asks, since its JUDGMENT lines are project decisions by design
- Diff installed hooks against the reference copies, back up the prior version, merge intended updates, then rerun the synthetic and host invocation checks. Preserve project-specific behavior.
- `git config core.hooksPath` is idempotent
- Settings.json is merged additively (no overwrites)
- CLAUDE.md prompts before overwriting the workflow section

If a project has diverged from the reference copies deliberately, diff before overwriting:

```bash
diff -ru <SKILL_DIR>/references/hooks/claude-hooks .claude/hooks
diff -ru <SKILL_DIR>/references/hooks/githooks .githooks
```
