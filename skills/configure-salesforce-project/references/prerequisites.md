# Prerequisites

**Run `scripts/preflight.sh` first.** It reports what is missing, what is installed but
unauthenticated, and one copy-pasteable command per gap.

```bash
scripts/preflight.sh --ticket-system jira --host github    # before init
scripts/preflight.sh                                       # after init: reads the config
```

Some users will want help getting these installed and others will not need any. Read the
preflight output, offer the next command, and take the lead from them.

Two habits that save time either way: **one command at a time** (a list of six produces one
run and five skipped), and **re-run preflight to check** rather than asking whether it
worked — the script can answer that. If a command changes `PATH`, say so: the change does
not apply to the terminal window it was made in, which is the most common way a working
install looks broken.

---

## Credentials

**Every auth step is a browser or device flow. No token is ever typed, pasted, or passed as
an argument.**

Never accept a credential, and never ask anyone to paste one into a chat window — it lands
in a transcript, a scrollback buffer, and possibly a log. If offered a token, decline and
run the interactive command instead.

| Tool | Interactive auth | Flow |
|---|---|---|
| `gh` (GitHub) | `gh auth login` | GitHub.com → HTTPS → "Login with a web browser" → paste the one-time code shown |
| `sf` (Salesforce) | `sf org login web --alias <name>` | Normal Salesforce login in a browser |
| `glab` (GitLab) | `glab auth login` | Same shape as `gh` |
| `az` (Azure DevOps) | `az login` | Browser opens |

**Jira has no CLI here.** All Jira work is done by the agent through the Atlassian Rovo MCP —
a connector explicitly authorized for the project in your current client, not on the command
line. There is nothing to `brew install` and nothing for preflight to check; just confirm the
Rovo MCP is connected in your client. See [ticket-adapters.md](ticket-adapters.md).

The one-time code `gh` displays is not a credential. It is a short-lived pairing code, safe
to read aloud, and it expires in minutes.

---

## Install order

Everything after step 1 installs through step 1.

**1. Homebrew**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

It asks for the Mac password once (admin rights), takes a few minutes, and **prints two more
commands at the end** that put `brew` on the `PATH`. Those must be run, then a new terminal
window opened. A setup that "didn't work" is usually this step, three-quarters finished. Use
the installer's own closing output for the `PATH` lines rather than guessing the path.

**2. Always needed**

```bash
brew install git jq
brew install --cask sf-cli
```

- `git` — the stack is git hooks. macOS ships an old git.
- `jq` — hooks parse JSON with it, and `install.sh` **refuses** to merge
  `~/.claude/settings.json` without it. A malformed settings file disables every hook the
  user has, so guessing is not an option there.
- `sf` — the Salesforce CLI. Usually already present.

**3. Tracker**, per `estate.ticket.system`:

```bash
brew install gh && gh auth login                                          # github
```

For **jira** there is nothing to install: the agent uses the Atlassian Rovo MCP connector in
your Claude client. Confirm it is connected there — no CLI, no `brew`, no terminal auth.

**4. Host CLI**, if different from the tracker: `brew install glab` or `brew install
azure-cli`. Bitbucket has none, which is why `guard-push.sh` exists.

**5. Quality-gate tools** — optional; each gap is a real hole rather than a blocker.

```bash
brew install pmd node
npm install            # in the repo, for prettier/ESLint/Jest
```

Missing these stops nothing. `pre-commit` warns loudly and skips that gate, which is the
right degradation — but staged Apex genuinely does go in unanalysed, so do not call it fine.

---

## Org connection

The stack needs a named org alias, and `estate.orgalias` must match it. Without one, every
`sf` command in a fresh worktree falls through to the machine's **global default org** —
which is how a command meant for a sandbox reaches production.

```bash
sf org login web --alias CONFIRMED_DEV_ALIAS    # only when authorized to connect
sf org display --target-org CONFIRMED_DEV_ALIAS --json
```

Confirm the intended org ID using verify-salesforce-org before a write. Do not set a machine
default or infer project authorization from an existing alias.

`audit` checks that the alias resolves. It reports this as a judgment item, not a failure: an
unresolvable alias is detectable, a *wrong* one is not.

---

## Common failures

| Symptom | Cause |
|---|---|
| `command not found` right after a successful install | `PATH` not reloaded — new terminal window |
| `brew: command not found` after installing Homebrew | the two closing `PATH` commands were not run |
| GitHub tracker calls silently do nothing, everything looks installed | `gh` session expired — `gh auth status`, then re-auth |
| Jira actions do nothing / "no such tool" | the Rovo MCP is not connected in your Claude client |
| `install.sh` refuses to run | `jq` missing. Deliberate — it will not risk the settings file |
| Hooks do not fire at all | `core.hooksPath` was repointed — `scripts/audit.sh --fix` |
| `estate-merge: command not found` | `~/.estate/bin` not on `PATH`; `install.sh` prints the line to add |
| Works in one directory, not another | almost always the wrong org alias, not a broken install |
