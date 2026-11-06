---
skill: configure-salesforce-project
title: Audit Salesforce delivery hooks after a husky pull
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 1f1991ed702e190110684d81701e01a8d34f6ebb9d8e8f216b57c951eef2d69e
---

## Request

I pulled the latest develop on our Northgate Freight Salesforce repo yesterday (it touched package.json) and since then my commit with "Fixes NGF-212" went through with no complaints. Can you audit whether the delivery standards are still armed here and tell me what to fix? The state I captured is in inputs/.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `configure-salesforce-project` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### claude-md-diff.txt

Managed block in CLAUDE.md (left = file, right = rendered from config)
BEGIN estate-managed hash=4be1a07c

  line 14   - Commit messages start with an NGF-### ref.
  line 15   - Never write a closing keyword (fixes, closes, resolves) in a commit message.   <- present only on the right
  line 15   + Keep commit messages short.                                                    <- present only on the left
  line 22   - Run /simplify before every commit.
  line 23   - Run `sf project deploy start --dry-run` before opening a PR.

Body hash of file as it stands: 91d03ac2 (recorded: 4be1a07c)
Note: CLAUDE.md is tracked in the client's repo (first added in commit 0b6e2f1 by someone at the client).

#### repo-state.txt

$ cd ~/work/ngf-sfdc && git config --local --get-regexp '^(estate|core\.hooksPath)'
core.hookspath .husky/_
estate.mode stealth
estate.delivery direct
estate.trunk develop
estate.host github
estate.review pr
estate.ticket.system jira
estate.ticket.project NGF
estate.ticket.remote client
estate.format check
estate.pmd advise
estate.squash prefer
estate.sync fetch
estate.chainhooks /Users/dana/work/ngf-sfdc/.husky/_
estate.drift tracking
estate.claudemd.hash 4be1a07c
(no estate.orgalias)

$ git log -3 --format='%h %s'
c91d0e2 Fixes NGF-212 route-optimiser timeout in FreightQuoteService
a7740b3 Merge pull request #88 from ngf/NGF-198
5e12f44 NGF-198 add carrier rate Flow

$ git diff HEAD~12 HEAD --stat -- package.json
 package.json | 3 +++   (adds "husky": "^9.0.0" and "prepare": "husky")

$ ls -l ~/.estate/githooks
-rwxr-xr-x  pre-commit
-rw-r--r--  commit-msg

$ cat ~/.estate/VERSION        -> 2.3.0
$ skill version                -> 2.5.0

$ ls .git/hooks | grep -v sample   -> (empty)
$ ls -ld .git/estate .git/info/exclude -> .git/estate is missing; exclude exists, contains CLAUDE.md, AGENTS.md

$ git ls-files CLAUDE.md AGENTS.md
CLAUDE.md

$ jq -r '.hooks|to_entries[]|.key+": "+(.value[].hooks[].command)' ~/.claude/settings.json | grep estate
PreToolUse: ~/.estate/claude-hooks/guard-force-app.sh
PreToolUse: ~/.estate/claude-hooks/guard-force-app-bash.sh
PreToolUse: ~/.estate/claude-hooks/guard-closing-keywords.sh
PreToolUse: ~/.estate/claude-hooks/guard-sf-deploy.sh
PreToolUse: ~/.estate/claude-hooks/guard-sf-flags.sh
PreToolUse: ~/.estate/claude-hooks/guard-pr-merge.sh
SessionStart: ~/.estate/claude-hooks/verify-git-hooks.sh
(no guard-worktree-nesting.sh, record-validate.sh, record-escape-hatch.sh, stop-dod-check.sh)
$ ls ~/.estate/claude-hooks | wc -l -> 14 scripts present, all executable
$ jq '.permissions.deny' ~/.claude/settings.json -> ["Bash(sf project retrieve*)"]

$ git worktree list
/Users/dana/work/ngf-sfdc            c91d0e2 [develop]
/Users/dana/work/ngf-sfdc-NGF-231    3f8a1b9 [NGF-231]
$ ls /Users/dana/work/ngf-sfdc-NGF-231 | grep -E 'CLAUDE|AGENTS'  -> (none)

$ sf org display -o ngf-dev  -> Connected Status: Connected
$ gh auth status             -> github.com: The token in keyring is invalid. (X) Failed to log in

## Output

### Audit: Northgate Freight Salesforce repo

**The standards are not armed.** Your `Fixes NGF-212` commit went through because git never ran our `commit-msg` hook. The cause is the husky install that arrived with your pull, and three other things are broken as well. I read the state you captured and did not run `scripts/audit.sh`, so I applied its documented checks by hand. This is a read-only audit and nothing has been changed.

#### Why the commit slipped through

1. **`core.hooksPath` was repointed.** It is now `.husky/_`, where it should be `~/.estate/githooks`. The pull added `"prepare": "husky"` to `package.json`, and husky sets `core.hooksPath` when it runs. Git now looks only in husky's directory, so neither of our hooks runs.
2. **`commit-msg` has lost its exec bit.** It is `-rw-r--r--` in `~/.estate/githooks`. Even with `hooksPath` fixed, git would skip it silently. This is the hook that rejects closing keywords and requires an `NGF-###` ref.
3. **The Claude-side backstop has gaps.** `guard-closing-keywords.sh` is registered in `settings.json`, so a commit made through the agent should have been caught. Your capture doesn't show how `c91d0e2` was made, so I can't say whether that guard missed it or the commit came from a terminal. A terminal commit would only have been caught by `commit-msg`.

`Fixes NGF-212` is a closing keyword. In a Jira project it can be read as a smart commit. Closing tickets is outside this loop, and the ticket is the client's (`ticket.remote=client`).

#### Results by check

| # | Check | Result |
|---|---|---|
| 1 | `estate.*` complete and coherent | **FAIL.** `estate.orgalias` is unset, so `sf` commands in a fresh worktree use the machine's global default org. Everything else is coherent. Jira with project `NGF` narrows the ref pattern correctly. |
| 2 | `core.hooksPath` and git hooks | **FAIL.** Repointed to `.husky/_`. `commit-msg` is not executable. `pre-commit` is fine. No stale copies in `.git/hooks/`. |
| 3 | `chainhooks` target | **Pass, with a caution.** It points to `.husky/_`, which is correct. Once `hooksPath` is restored, our hooks run first and then call husky's. |
| 4 | Claude hook entries and scripts | **FAIL.** `guard-worktree-nesting`, `record-validate`, `record-escape-hatch` and `stop-dod-check` are missing from `settings.json`. All 14 scripts exist and are executable. A machine-wide `Bash(sf project retrieve*)` deny rule is still present. It fires in every repo on your machine, including unrelated ones, and retrieve-blocking now lives in the gated `guard-sf-flags.sh`. |
| 5 | `~/.estate/VERSION` against the skill | **FAIL.** The install is 2.3.0 and the skill is 2.5.0. |
| 6 | `CLAUDE.md` managed block | **FAIL, and not fixable by `--fix`.** See below. |
| 7 | State dir and exclude entries | **FAIL.** `.git/estate/` does not exist, so no validate or deploy can be recorded and the merge gate would block everything. The `.git/info/exclude` entries are present. |
| 8 | Contract in each worktree | **FAIL.** `ngf-sfdc-NGF-231` has no `CLAUDE.md` or `AGENTS.md`. An agent working there has no contract in context. |
| 9 | `ngf-dev` resolves | Pass. Status is Connected. |
| 10 | Tracker CLI auth | **Attention.** `gh` is installed but its token is invalid. `host=github` and `review=pr` depend on it. Jira runs agent-side through the Atlassian Rovo MCP, so there is nothing to check from a shell. |
| 11 | Client checklist | Unknown. `.git/estate/client-checklist` can't exist without the state dir. |

#### The `CLAUDE.md` problem needs your decision

Two things are wrong, and they affect each other.

- **The block was edited.** The hash on the file is `91d03ac2` and the recorded one is `4be1a07c`. The rule "never write a closing keyword" has been replaced by "Keep commit messages short." The cause is unknown. It could be an agent, a person at the client, or you. I can't tell, so I won't re-render over it, and neither will `--fix`.
- **The file is tracked by the client's repo.** `CLAUDE.md` was added in `0b6e2f1` by someone at the client. Your clone is `stealth`, which promises that nothing of ours goes into their tree. `.git/info/exclude` does not untrack a file that is already tracked. Re-rendering the block would modify the client's file, and this fails the stealth rule. `init --update` will stop here for the same reason.

You have two options:

- **Stay in stealth (my recommendation, since the client owns the repo).** Leave their `CLAUDE.md` alone and restore any local edit to it with `git checkout -- CLAUDE.md`. The contract then has no managed home in this clone. The hooks remain the enforcement layer, and the closing-keyword rule is enforced by `commit-msg` and `guard-closing-keywords.sh` whether or not the prose is there.
- **Switch to `native`.** Do this only if the client agrees to carry our tooling in-tree. You would run `git config estate.mode native`, then `scripts/install.sh --block`, and commit the contract deliberately.

If someone added a line worth keeping, move it outside the `BEGIN`/`END` markers before any re-render. Don't edit the hash.

#### Fix order

1. **Decide the ownership question above first.** It determines whether the block and the update can proceed.
2. **Run `scripts/audit.sh --fix`.** It should handle the mechanical items: restore `core.hooksPath` to `~/.estate/githooks`, restore the exec bit on `commit-msg`, add the four missing Claude hook entries, retract the stray retrieve deny rule, and create `.git/estate/`.
3. **Run `init --update`.** This brings 2.3.0 up to 2.5.0 and preserves your recorded answers. It will refuse while the tracked-contract conflict stands.
4. **Set the org alias.** Run `git config estate.orgalias ngf-dev`. I'm assuming `ngf-dev` is the org that `develop` syncs to. I couldn't confirm that from the evidence, so correct me if the alias is different.
5. **Re-authenticate GitHub.** Run `gh auth login` and use the browser flow. Never paste a token into a chat or a command.
6. **Re-run `scripts/audit.sh`.** Checks 1 to 8 should pass. Check 6 will still need the decision above.

#### Why the fix may not stick

husky's `prepare` script runs on every `npm install` and will repoint `hooksPath` again. `verify-git-hooks.sh` re-arms it at the start of each Claude session, but a terminal commit straight after an install is exposed. Run the audit after any pull that touches `package.json`. That is what happened this time.

#### The commit already made

`c91d0e2` has a closing keyword in its message. I can't see whether it was pushed. If it is still local, reword it to `NGF-212 route-optimiser timeout in FreightQuoteService` with `git commit --amend` after step 2, so `commit-msg` checks the new message. I haven't done this because it rewrites history. If the commit has been pushed or merged, leave it. Rewriting shared history would be worse. In that case, check in Jira whether NGF-212 was transitioned and reopen it if so. On a client-owned tracker, that is your call to make, not something I should do.

#### What I couldn't check

- Whether `AGENTS.md` exists. It's excluded and untracked, and your capture only listed tracked files.
- How `c91d0e2` was created.
- Whether the Jira connector is authorised in this client.
- Who edited `CLAUDE.md`.
