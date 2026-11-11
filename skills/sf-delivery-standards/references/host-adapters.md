# Host adapters — the merge gate per remote

`aleysian.host` decides which surface `guard-pr-merge.sh` intercepts.

The gate's job: **a change touching `force-app/` may not land on trunk until that exact
commit has passed a dry-run validate against the org.** Validate-then-merge is ordered that
way because once the squash lands, trunk *claims* to describe the org. If the code then fails
to deploy, trunk is ahead of the org and the only repairs are fix-forward or revert.
Validating first makes that state unreachable rather than recoverable.

| Host | Create / merge | Gate quality | Notes |
|---|---|---|---|
| `github` | `gh pr create` / `gh pr merge --squash` | **full** — head SHA *and* changed files | unchanged from the predecessor |
| `gitlab` | `glab mr create` / `glab mr merge --squash` | **full** on the head SHA | `glab` is mature; near drop-in |
| `azure` | `az repos pr create` / `az repos pr update --status completed` | **full** on the head SHA | squash policy is often set repo-side; the guard checks the flag when present |
| `bitbucket` | web UI only | **reduced** — becomes a *push* gate | see below |
| `none` | `aleysian-merge` | **full**, plus a recorded human approval | see below |

For the hosted flows the changed-file list is a nice-to-have. When it reads cleanly and shows
no `force-app/` paths, the gate stands aside. When it cannot be read, the gate **requires the
validate anyway** — failing closed on an unknown file list costs one dry run, and the
alternative is a silent unvalidated merge.

All of them fail **open** when the host CLI is missing or the remote is unreachable. An
offline tool should not stop work, and the deploy-side guards still protect the org.

---

## Bitbucket — honest degradation

There is no official Bitbucket CLI, so merges happen in a browser and there is nothing for a
`PreToolUse` hook to see. Rather than pretend otherwise, the gate moves one step earlier:
`guard-push.sh` requires a recorded green validate before `git push` of a branch that touches
`force-app/`. Whatever a human then merges in the UI was validated.

**This is weaker than the merge gate, in two specific ways:**

1. It cannot tell a merge from a browse. Someone can merge an old unvalidated branch that was
   pushed before this stack was installed.
2. It gates the branch head *at push time*. Push, then merge something else, and the proof
   does not follow.

The deploy-side guards are unaffected — a real deploy still requires a clean, synced trunk, so
the org is still protected. Describe this as the best available interception point on this
host, never as equivalent coverage.

Also: reaching for `gh pr merge` in a Bitbucket repo means the agent has the wrong model of
the project, so `guard-pr-merge.sh` blocks that specifically and says what the flow actually
is.

---

## `host=none` — the local review gate

For repos with no remote, and the fallback for IP-sensitive clients who will not allow one.

A pull request does four things. Three are reproducible locally:

| A PR… | `aleysian-merge` |
|---|---|
| shows a human the diff before it counts | yes |
| refuses to land unvalidated code | yes |
| produces a record of who approved what | yes — `approve-log` |
| makes a **second** person possible | **no** |

It also cannot give you off-machine backup or a review artifact that outlives the laptop. So:
**if the client will allow a private remote, use one.** This exists for when they genuinely
will not, and the alternative is no gate rather than a slightly weaker one. `init` puts
"propose a private backup remote" on the client-conversation checklist for exactly this.

### How the approval is real

The green button is the human running the command. That is the same authority model as
clicking "Merge pull request" — which is also just a person deciding after looking. Run in a
terminal it prompts for the diff and the confirmation; run through Claude Code, the human
approves the command itself, which is the same decision.

### Two layers, and neither is bypassable alone

`git merge` into trunk is intercepted by `guard-pr-merge.sh`, which requires an `approve-log`
entry for the branch head. But an agent could commit without going through the Bash tool at
all, so `pre-commit` gate 1 carries the real wall: a `force-app/` commit on trunk is allowed
**only** when all three of these hold —

1. git is mid-squash-merge (`$GIT_DIR/SQUASH_MSG` exists)
2. `aleysian-merge` staged it (`pending-approve` names the branch head)
3. that head appears in **both** `validate-log` and `approve-log`

A hand-written `git merge --squash` satisfies (1) and fails (2). That is the point:
`aleysian-merge` is the reviewed path, not a convenience wrapper around the same thing.

### What else degrades under `host=none`

- `guard-sf-deploy.sh` skips the remote-sync check. There is no origin to be behind, and
  blocking on a missing one would make local mode unusable.
- The Definition of Done's "pushed to origin" item becomes "committed to trunk".
- `post-merge-nudge.sh` reads trunk's tip locally instead of `origin/<trunk>`.

---

## Squash policy

One ticket, one commit on trunk. A merge commit or a rebase scatters the ticket refs that
`auto-label-deploy.sh` reads back out of history, and proof-of-deploy is tracked per squashed
commit.

- **native mode: hard.** The ref automation depends on it.
- **stealth mode: `aleysian.squash=prefer` is available**, because merge strategy in a client's
  repo is *their* policy and a vendor tool overriding it is out of line. `init` asks. With
  `prefer`, a non-squash merge is allowed and the guard says what it costs rather than
  blocking.

---

## Adding a host

`guard-pr-merge.sh` needs three things per host, and nothing else:

1. **a matcher** — which command constitutes a merge
2. **a squash flag** — how that CLI spells it
3. **a head-SHA read** — how to ask which commit is landing (`--json`, then `jq`)

The changed-file list is optional; omit it and the gate requires the validate unconditionally,
which is the safe direction. Add the matcher to `post-merge-nudge.sh` too, or the "trunk is now
ahead of the org" nudge will not fire after a merge on that host.
