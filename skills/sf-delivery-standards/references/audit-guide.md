# `/sf-delivery-standards audit`

```bash
scripts/audit.sh          # report only
scripts/audit.sh --fix    # self-heal the mechanical items (1-8)
```

Exit 0 clean, exit 1 problems found. Judgment items (9–11) never affect the exit code.

## Why this is a first-class sub-command

Every part of this stack can be silently disabled, and **none of the failures look like
failures**:

- `core.hooksPath` gets repointed by someone else's `npm install` (husky's `prepare`).
- A hook loses its exec bit, and git skips it without a word.
- The `CLAUDE.md` or `AGENTS.md` block gets edited — including by the agent it constrains.
- `~/.aleysian/` goes stale against the skill driving it, so the hooks running are not the
  hooks documented.
- A hook is named in `settings.json` but does not exist on disk.

In every case the work continues and looks fine. That is worse than a visible break, because
nobody knows to be careful. So the question this answers is not *"is it installed"* but
**"is it still armed"**.

---

## The checks

Mechanical — `--fix` heals these:

| # | Checks | If it fails |
|---|---|---|
| 1 | `aleysian.*` complete and internally coherent | `host=none` with `review=pr` means the merge gate looks for a record nothing writes. `ticket.system=jira` with no `ticket.project` means the ref pattern matches *any* project's keys, including the client's. No `orgalias` means every `sf` command in a fresh worktree hits the machine's global default org. DevOps Center without a pipeline id has only a provisional landing branch. Shared mode also requires GitHub, an integration branch, a deployment environment, and both branch patterns. |
| 2 | `core.hooksPath` → `~/.aleysian/githooks`; both hooks present, executable, shebang'd; no stale `.git/hooks/` copies | git hooks are not running, or one gate is silently skipped |
| 3 | `aleysian.chainhooks` target still exists and is executable | the **project's own** gates stopped running — our problem to notice, not theirs |
| 4 | Every stack hook is present in each configured host (`~/.claude/settings.json` and/or `~/.codex/hooks.json`); every named script exists and is executable; and NO machine-wide Claude retrieve deny rules linger | those guards are OFF. A retrieve deny rule in the user-level Claude file fires in every repo on the machine, including unrelated ones (req 1) — retrieve-blocking now lives in the gated `guard-sf-flags.sh`, scoped to managed repos, so a leftover deny rule is stale and `--fix` retracts it |
| 5 | `~/.aleysian/VERSION` vs the skill version | stale install → `init --update` |
| 6 | Each installed host instruction block (`CLAUDE.md` and/or `AGENTS.md`) is present, its hash matches config, and a stealth-owned target is not tracked | see below |
| 7 | State dir exists and is writable; `.git/info/exclude` entries present | without the state dir, no validate or deploy can be recorded — so the merge gate blocks *everything* |
| 8 | Each worktree has the selected host instruction files (stealth mode) | an agent working in that worktree has no contract in context, which is the failure this whole stack exists to prevent |

With network probes enabled, audit also resolves the first linked DevOps Center stage and fails on
a confirmed landing-branch mismatch. Shared mode additionally compares the integration branch
with the latest successful GitHub Deployment SHA. A mismatch, missing receipt, or unreadable
centralized state fails audit because none proves the shared org baseline. It also verifies that
the integration and pipeline branches exist and block deletion, preventing GitHub's automatic
head-branch cleanup from removing a permanent stage. `--no-probe` skips these remote comparisons
while still checking their configuration.

Judgment — reported only, never touched:

| # | Reports |
|---|---|
| 9 | Does `aleysian.orgalias` resolve to a real org (`sf org display`) |
| 10 | GitHub: is `gh` installed and authenticated. Jira: reported as agent-side via the Atlassian Rovo MCP (nothing to shell-check). And does the drift probe actually work for this org type |
| 11 | Client-conversation items still open, from `.git/aleysian/client-checklist` |

---

## Check 6 is not auto-fixed, even with `--fix`

The hash proves the block's content changed. It cannot tell you **whether an agent stripped a
rule or a human added a genuinely useful line.** Overwriting silently would destroy the second
case in order to fix the first.

So `audit` shows the diff — left is what is in the file, right is what the config says it
should be — and stops:

```
6. CLAUDE.md managed block
  FAIL  EDITED since generation — content no longer matches its recorded hash.
```

Three ways forward, and picking is the point:

```bash
# theirs was wrong — take the generated version
scripts/install.sh --block

# yours is right — the config changed and the block is stale. Fix the config first,
# then re-render so the two agree.
git config aleysian.pmd block && scripts/install.sh --block

# yours has something worth keeping — move it OUTSIDE the markers, then re-render.
# Content outside the fence is never touched.
```

Never resolve this by editing the hash. That re-blesses whatever is there and turns the fence
into decoration.

In `stealth` mode, a selected host-contract path that Git already tracks is also a failure.
`.git/info/exclude` does not make a tracked file untracked, so re-rendering that path would alter
the client's repository. Restore any generated edit, then either keep stealth and leave the
tracked file untouched or deliberately switch to `native` before updating and committing it.
`--fix` never changes ownership mode or untracks a file.

---

## When to run it

- **After `init`** — `install.sh` ends by telling you to.
- **At the start of work on a project you have not touched in a while** — especially one where
  someone else may have run `npm install`.
- **When a guard blocks something you believe should be allowed.** Often the answer is a config
  key that no longer matches reality (trunk renamed, sandbox branch merged away, tracker
  switched).
- **When a guard does *not* block something you expected it to.** This is the more dangerous
  direction, and audit is the only way to find it.
- **After a skill upgrade** — check 5 catches the mismatch, but only once you look.
- **When the SessionStart hook says to.** `verify-git-hooks.sh` runs a subset of these checks
  every session and repairs what it can; anything it reports as ACTION NEEDED is an audit.

A useful habit for a shared client repo: run it after every `git pull` that touched
`package.json`. That is the commit most likely to bring husky with it.
