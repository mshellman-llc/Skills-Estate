# `/configure-salesforce-project init`

Five phases: **preflight** (are the tools even there), **detect** (ask nothing), **ask**
(only what cannot be inferred), **do** (one script), **emit** (the client-conversation
checklist).

Idempotent. Re-running changes only the keys whose answers changed. `init --update`
re-renders after a skill upgrade and asks nothing.

Before repo initialization or block rendering, the installer checks ownership of the selected
`CLAUDE.md` and `AGENTS.md` targets. In `stealth` mode it refuses a tracked target before the
machine or clone half writes anything. Refresh machine hooks separately with
`scripts/install.sh --machine-only --platform <claude|codex|both>`, then resolve repository
policy explicitly: leave the client's tracked contract untouched, or switch to `native` before
updating and committing it.

---

## Phase 0 — Preflight

```bash
scripts/preflight.sh --ticket-system <answer-from-phase-2> --host <detected>
```

Do this **before** the Q&A when the tracker is obvious, or between ask and do when it is
not. Two reasons it comes first rather than being a footnote:

1. `install.sh` **refuses to run without `jq`** — it will not risk a malformed
   `~/.claude/settings.json`, because that disables every hook the user has. Finding that out
   after the Q&A wastes the answers.
2. Discovering three missing tools one failure at a time is a bad first run.

Work the gaps one command at a time and re-run preflight after each. Note when a command
changes `PATH`, since that does not apply to the window it was run in. Some users will want
help with this and others will not need any — see [prerequisites.md](prerequisites.md).

**Auth is always the interactive flow.** `gh auth login`, `sf org login web --alias <name>`.
Never accept a token from the user and never ask for one. Jira needs no CLI auth here — it is
handled agent-side through the Atlassian Rovo MCP connector in the Claude client.

Optional gaps (`pmd`, `node`, `node_modules`) do not block init. Say what each costs — "PMD
isn't installed, so staged Apex will go in unanalysed; the gate warns instead of blocking" —
and move on. Do not present an optional gap as a blocker, and do not present it as fine.

### Are you running the current skill? (best-effort, non-blocking)

The installed skill is a plain copy, not a git checkout — it does not update itself, and
`init`/`audit` never pull from the repo. So on a re-run it is worth a one-shot check that the
local copy is not stale before you install from it. Compare the local version to `main`:

```bash
LOCAL=$(grep -m1 BLOCK_VERSION "$SKILL_DIR/references/hooks/claude-hooks/_block.sh" | cut -d'"' -f2)
REMOTE=$(gh api repos/Estate/AI-Skills/contents/house-skills/skills/configure-salesforce-project/references/hooks/claude-hooks/_block.sh \
           --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -m1 BLOCK_VERSION | cut -d'"' -f2)
```

If `REMOTE` is set and higher than `LOCAL`, tell the user once: *"your configure-salesforce-project is
behind `main` (local vX, main vY) — refresh it via your estate sync before I install from it."*
This is **best-effort and never blocks**: it needs network + access to the (private) Estate
repo, so it silently does nothing on a client machine or offline — do not treat a failed or empty
`REMOTE` as a problem. `audit` stays fully offline and does not do this. (Maintainers keep `main`
shippable and bump `BLOCK_VERSION`/`VERSION` on every shippable change, which is what makes the
comparison meaningful.)

---

## Phase 1 — Detect

Run these before asking anything. Every question you can answer from the repo is a
question a non-technical user does not have to understand.

```bash
git rev-parse --show-toplevel                       # is this even a repo
git remote get-url origin 2>/dev/null               # host + ownership
git branch --show-current; git branch -r            # candidate trunks
ls sfdx-project.json pipeline.yml 2>/dev/null       # SF project? engine project?
ls .husky 2>/dev/null; git config core.hooksPath    # whose hooks are armed
ls .prettierrc* prettier.config.js 2>/dev/null      # do they format
ls config/pmd-ruleset.xml eslint.config.js 2>/dev/null
ls CLAUDE.md .claude/CLAUDE.md 2>/dev/null
git config --get-regexp '^estate\.'               # a previous init
sf config get target-org 2>/dev/null                # org alias
```

**If `pipeline.yml` exists, this repo has a deploy engine above it.** That does not
stop the install — the two stacks compose, and they divide cleanly:

| | Owns |
|---|---|
| this skill | the local loop: ticket, worktree, dry run, deploy to **one** org |
| `operate-salesforce-pipeline` | everything from the PR into an environment branch upward |

Three answers change, and they are not optional:

- **`trunk` is the dev sandbox branch**, not `main`. The invariant `trunk === org`
  then reads "my sandbox branch equals my sandbox org", which is true and useful.
  Pointing `trunk` at an environment branch would claim this clone deploys
  production, and every deploy guard would enforce that claim.
- **`squash=merge`.** The engine cherry-picks merge commits (`-m 1`) to promote and
  reverts them (`-m 1`) to roll back. Squashing removes the structure both run on,
  silently, and the damage only surfaces the day someone needs a rollback.
- **`protected`** lists the environment branches, so nothing here merges into one.
  `operate-salesforce-pipeline`'s `scripts/init.sh` reads them out of `pipeline.yml` and sets
  the key; run it rather than typing the list, because `pipeline.yml` is the
  authority on what the environments are.

Only one stack may own `core.hooksPath`, and it is this one. `operate-salesforce-pipeline`
installs no git hooks — it has no local loop to guard.

**A DevOps Center repo is a separate delivery mode, not engine coexistence.** Set
`estate.delivery=devops-center`, keep it free of `pipeline.yml`, and use the branch and
project facts returned by `dx-devops-pipeline-manage`. The intended shape is:

- production branch `main`;
- first landing branch derived from the pipeline's linked `nextStageId` topology, expected to be
  the configured landing branch for this project and recorded as `estate.trunk` only because it is the WI review target;
- development org `sandbox-a`, recorded as `estate.orgalias` and project-locally in `.sf`;
- protected branches `staging main`;
- squash required;
- `ticket.system=pattern`, with the DevOps Center WI pattern;
- DevOps Center control-org alias, project id, and pipeline id under `estate.devops.*`.

In the default `devops.workmodel=isolated`, the development org has no Git branch. The pipeline
stages do, and each In Progress WI gets a feature branch based on the first linked stage. After
the pipeline exists, resolve rather than guess the landing branch:

```bash
scripts/resolve-devops-landing.sh \
  --pipeline-id <pipeline-id> --project-id <project-id> \
  --target-org <control-org-alias>
```

The resolver finds the unique stage not referenced by any other stage's `nextStageId` and returns
its `branchName`. Before the pipeline exists, an explicit `--trunk staging` is allowed only as a
provisional bootstrap value. Audit reports the stack incomplete until init is rerun with the
pipeline id, and a confirmed topology mismatch fails audit.

In this mode `trunk === org` does not apply. The contract says DevOps Center owns stage
branches and promotion. Read [devops-center.md](devops-center.md) before initialization.

If several agents deliberately share one persistent development org, ask whether the repository
already has a centralized landing coordinator and a GitHub Deployment environment that records
each successful shared-org deployment. Without both, keep the isolated model or stop. Do not
install shared mode as prose-only policy.

Shared mode additionally records:

- `devops.workmodel=shared`;
- `devops.integrationbranch`, such as `integration-dev`;
- `devops.environment`, such as `ExampleDevelopment`;
- `devops.developmentbranchpattern=^dev/WI-[0-9]+$`.

The installer adds the integration branch to `estate.protected`. Audit requires the branch to
resolve and, unless `--no-probe` is used, requires its HEAD to equal the latest successful GitHub
Deployment SHA for the configured environment. Audit also verifies that the integration branch,
first DevOps Center stage, and `main` exist on GitHub and have deletion disabled through classic
branch protection or an active ruleset. Repository-level automatic head-branch deletion is safe
only when those permanent branches cannot be deleted.

What each detection settles:

| Detected | Infer |
|---|---|
| remote host is `github.com` / `gitlab.com` / `dev.azure.com` / `bitbucket.org` | `host` |
| no remote at all | `host=none`, `review=local` |
| remote org is an Estate org | `mode=native` (otherwise ask) |
| a prettier config exists | `format=client` |
| `.husky/` or a foreign `core.hooksPath` | `chainhooks`, and `mode=stealth` is likely |
| `sf project retrieve preview` succeeds | `drift=tracking` is available |
| existing `estate.*` keys | this is a re-run; every one of them is a default |
| user selected a dedicated DevOps Center repository | `delivery=devops-center`; do not infer this from branch names alone |

---

## Phase 2 — Ask

One `AskUserQuestion` round, and only for what detection could not settle. Phrase each
in terms of the *situation*, never the config key — the person answering may not know
what a trunk is, and does not need to.

| Ask when | Question, in their terms |
|---|---|
| remote ownership ambiguous | "Is this repo Estate's, or the client's? If it's theirs, nothing of ours gets committed to it." → `mode` |
| direct or engine delivery has more than one plausible trunk, or a shared client repo | "Which branch matches the org you deploy to? On a shared repo where each person has their own sandbox, that's your sandbox branch, not `main`." → `trunk` |
| always | "Where do tickets live for this project?" → `ticket.system` (+ project key for Jira) |
| `ticket.system` is Jira or the client's | "Is that tracker ours or the client's? If it's theirs, nothing automated will write to it." → `ticket.remote` |
| no prettier config found | "This project has no code formatter configured. Check formatting without changing anything, or leave it alone?" → `format` (`check` / `off`) |
| always, if the codebase is not ours | "Should static analysis block a commit, or just report? Blocking is right eventually; on an unfamiliar codebase it can be unusable on day one." → `pmd` |
| org is a Dev/Dev Pro sandbox | "Watch for changes made by clicking in Setup that never made it into the repo?" → `drift` |
| stealth mode | "Does this project's repo allow squash merges?" → `squash` |

Do not ask about `review` — it follows from `host`, and `install.sh` forces
`review=local` when `host=none`.

Do not ask for a DevOps Center landing branch after the pipeline exists. Resolve it from the
pipeline topology. The development sandbox is not evidence for any branch because it has none.

For DevOps Center, ask whether each developer has an isolated environment or several agents share
one persistent org. Select shared mode only when the GitHub coordinator, protected integration
branch, and successful deployment receipt already exist or are in the approved implementation
scope.

---

## Phase 2b — Check what the tracker will let you do, and write it down

**A tracker's configuration decides whether automation can work at all, and none of it is
visible until something breaks.** Observed on a real site: a Jira field configuration marked
one custom field required, which makes a `Story` create fail *for that issue type only* — the
same project created `Bug` fine. And a project created from `projectTypeKey: software` with no
template has only `Task` and `Sub-task`, so any mapping that assumes `Story` exists fails.

For a **Jira** project, this is now an agent step, not a shell script. With the Atlassian Rovo
MCP, introspect the project up front — `mcp__*__getJiraProjectIssueTypesMetadata` and
`mcp__*__getJiraIssueTypeMetaWithFields` for the types and their fields — and, because metadata
reports only *screen* fields (a required-but-off-screen field is invisible to it), confirm by
attempting a real create per type and believing the error. A rejected create writes nothing, so
it is side-effect-free. See [ticket-adapters.md](ticket-adapters.md). For **GitHub** there is
nothing to probe.

Record what you learn as git config, then re-render the contract so it carries the findings:

```bash
git config estate.ticket.types    "Task,Bug"          # what the project has
git config estate.ticket.cancreate "Task"             # what automation can actually create
git config estate.ticket.blocked  "Story:User Story"  # Type:Field pairs that block a create
scripts/install.sh --block
```

| Recorded | Used for |
|---|---|
| `ticket.types` | what the project has, so nothing assumes `Story` exists |
| `ticket.cancreate` | which types automation can actually create |
| `ticket.blocked` | `Type:Field` pairs that cannot be created, and why |

`install.sh --block` renders these into the `CLAUDE.md` contract, which is the point: an agent
that knows *"Story is blocked by a required field on this project"* asks the human to open the
ticket. One that doesn't, retries the create and burns a turn.

**If a blocked type is on a project we own, fix the project** — make the field optional. An
agent opening a drift-reconciliation ticket has nothing honest to put in an estimate field.
**If it's the client's, we cannot fix it**: assume humans create tickets in their process and we
only reference them. `commit-msg` still enforces the ref, which is the part the audit trail
needs. Either way it goes on the client-conversation checklist.

Note what this cannot tell you: whether a field is required *site-wide* or only on this project.
Both produce the same error; the distinction is a Jira admin-UI lookup.

---

## Phase 3 — Do

```bash
scripts/install.sh --repo \
  --mode stealth --delivery direct --trunk CONFIRMED_DEV_BRANCH --host github \
  --ticket-system jira --ticket-project CONFIRMED_PROJECT_KEY --ticket-remote ours \
  --format check --pmd advise --drift tracking --org-alias CONFIRMED_DEV_ALIAS --squash prefer
```

For the confirmed DevOps Center repository, after the production seed and stage
branches exist:

```bash
scripts/install.sh --repo --platform both \
  --mode native --delivery devops-center --host github \
  --ticket-system pattern --ticket-pattern '(^|[^[:alnum:]])WI-[0-9]+([^[:alnum:]]|$)' \
  --ticket-remote ours --format client --pmd block --drift tracking \
  --org-alias sandbox-a --squash require --protected 'staging main' \
  --devops-org-alias <control-org-alias> --devops-project-id <project-id> \
  --devops-pipeline-id <pipeline-id>
```

`install.sh` derives the landing branch from that pipeline and refuses a supplied `--trunk` when
it disagrees. If the pipeline does not exist yet, omit `--devops-pipeline-id` and pass an explicit
provisional `--trunk`; rerun init after pipeline creation.

For the shared-org variant, add:

```bash
  --devops-work-model shared \
  --devops-integration-branch integration-dev \
  --devops-environment ExampleDevelopment
```

The command refuses shared mode on non-GitHub hosts or without both centralized names. It does not
invent or install the repository's deployment coordinator because Salesforce authentication,
test selection, approvals, and verification are repository-owned security decisions.

The script deliberately prompts for nothing. A script that asks questions cannot be
re-run by an agent, and this one must be — after an upgrade, after a config change,
after `audit --fix`.

In order, it: installs `~/.estate/` → **backs up and jq-merges** the hook and deny
entries into `~/.claude/settings.json` → writes the `estate.*` keys → arms
`core.hooksPath`, recording whatever it displaced as `chainhooks` → writes
`.git/info/exclude` → creates the state dir → renders and inserts the `CLAUDE.md` block.

Two things to watch:

**The settings merge is the one genuinely destructive step available.** The user's
`~/.claude/settings.json` almost certainly has hooks from other projects. It is backed
up first, merged by appending per event, and de-duplicated by command — so re-running is
a no-op and nothing of theirs is dropped. If `jq` is missing the script refuses rather
than trying; a malformed `settings.json` disables every hook the user has.

**Native mode: commit `CLAUDE.md`.** A worktree materialises *tracked* content only, so
an uncommitted or gitignored `CLAUDE.md` silently does not exist in any worktree — which
defeats the entire contract. Stealth mode solves this differently (excluded, and
symlinked in by `ensure-worktree-config.sh`), which is why the mode has to be right.

### If there is no repo yet

Init does not stop at "you need a repo" — it walks the user through creating one, and
the repo is **private** by default. Creation is a real, externally-visible action and
needs the user's own authenticated CLI, so — like every auth and dependency step —
guide it one command at a time and let the user run it; never create it silently or
from a token. Per host:

```bash
gh repo create <org>/<name> --private --source . --remote origin   # GitHub
glab repo create <group>/<name> --private                          # GitLab
az repos create --name <name> --project <project>                  # Azure (private by org policy)
# Bitbucket / host=none: create the private repo in the UI, then `git remote add origin <url>`
```

Default to private and say why: a client's Salesforce metadata is theirs, and a public
mirror of it is a disclosure nobody asked for. Only a deliberate, recorded decision
makes it public. Once the remote exists, continue into seeding below.

### If the org has metadata and the repo is empty

Route through [seeding-guide.md](seeding-guide.md) **before** the guards go up. The
stack blocks `sf project retrieve` at two independent layers, correctly, and an empty
repo is the only window in which a retrieve cannot clobber anything.

Order: (create the private repo, if none) → config + hooks install → **seed** → then
the block and the audit.

### Verify

```bash
scripts/audit.sh
```

Expect the org-alias and tracker-CLI lines to be the only complaints on a fresh
install. Anything in section 2 or 4 failing means the stack is not actually armed —
fix it before telling the user init succeeded.

---

## Phase 4 — Emit the client-conversation checklist

Anything the answers imply needs someone's consent. Write it to
`.git/estate/client-checklist` (so `audit` keeps surfacing it until it is resolved)
**and** hand it to the user as something they can paste to their lead.

Include an item only when the answers actually raise it:

- `format=check` → *"This project has no code formatter. Introducing one is a one-time
  noisy diff and then permanently less review friction. Worth proposing?"*
- `pmd=block` on a codebase we did not write → *"Static analysis will block commits on
  shared code. Confirm the team wants that bar."*
- `squash=prefer` → *"We prefer one commit per ticket on the deploy branch. If your
  policy is merge commits we'll follow it, with the tradeoff that ticket references end
  up spread across commits."*
- `ticket.remote=client` → *"Nothing automated will touch your tickets. If you'd like
  deploys to comment on them automatically, that's a switch we can flip."*
- `host=none` → *"Local-only means no second reviewer, no off-machine backup, and no
  durable review record. A private remote is strictly better if you can allow one."*
- `mode=stealth` + `chainhooks` set → nothing to ask; say it out loud anyway: *"Your
  existing git hooks still run. Ours run first and only look at our own changes."*

The framing to keep: **govern your own behaviour silently; change their artifacts or
their process only out loud.**

---

## Re-running, and changing one answer later

Every key is independently settable, and the hooks read config live — so nothing needs
reinstalling to change behaviour:

```bash
git config estate.pmd block            # ratchet up once the codebase is clean
git config estate.trunk main           # sandbox branch merged; back to main
git config estate.ticket.system jira
git config estate.ticket.project SFO
scripts/install.sh --block               # re-render the CLAUDE.md block to match
scripts/audit.sh                          # confirm the pair is still coherent
```

The last two matter: the block is a *snapshot* of config, so changing a key without
re-rendering leaves `CLAUDE.md` telling the user something the hooks no longer do. The
audit catches that as a hash mismatch, but only at the next session start.
