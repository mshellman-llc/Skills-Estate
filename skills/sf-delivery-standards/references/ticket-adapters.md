# Ticket adapters

The local loop does almost nothing to a tracker **from a hook**, on purpose. A hook is a bash
subprocess and cannot reach the session's MCP connection — there is no token or endpoint a
spawned hook could use. So any Jira network work is done by the **agent** (which can call the
Atlassian Rovo MCP), never by a hook. The only tracker capability a hook keeps is
`ticket_cli_present` in `_ticket.sh` (GitHub only — see below), which `audit` uses to degrade
honestly. Ticket-ref parsing, examples, and per-system config live in `_config.sh`
(`ticket_system`, `ticket_project`, `ticket_remote`, `ticket_example`, `ref_pattern`,
`extract_refs`, `ticket_label`).

Two things to state up front:

**Ticket closure is out of this loop's scope.** A sandbox deploy does not make a ticket "done";
tickets stay open until production, which is the configured delivery system's domain. Nothing here gates
or performs a closure. The agent closes a ticket only when the user explicitly asks — there is no
close gate, deliberately (and see the boundary at the end for why one could not exist over MCP
anyway).

**Never write to a client's tracker unasked** (`ticket.remote=client`). Automation editing a
client's project management without anyone agreeing to it first is not a feature. Refs stay
enforced so history is traceable; everything else steps back.

---

## `github`

- **Refs are keyword-anchored:** `refs #42`, never a bare `#42`. Not decorative. A bare `#N`
  scan reads issue numbers out of ordinary prose ("see the note in #3 below"), which is enough
  to cross-link tickets nobody touched.
- **Closing keywords are blocked outright** — `fixes`/`closes`/`resolves #N`. This loop never
  closes a ticket on merge (a keyword would, before the deploy has even happened), so
  `guard-closing-keywords.sh` and `commit-msg` reject them. Use `refs #N`.
- Ticket actions the agent runs use `gh` (`gh issue create` / `comment` / `view`).
  `ticket_cli_present` reports whether `gh` is installed so `audit` can say so. After a real
  deploy, the agent comments the SHA + job id on the issue — a **comment**, never a close.

## `jira`

All Jira work is done by the **agent** through the **Atlassian Rovo MCP** — a company-wide
connector authenticated interactively in the Claude client. There is no CLI to install or
authenticate, and a hook cannot reach the MCP, so `_ticket.sh` has no Jira arm.

### The Rovo MCP tools

Reference them generically and match on the tool **suffix**: the server segment is an opaque id
(and gains a `plugin_<plugin>_<server>` prefix when bundled), while the tool names are stable.

| Operation | Tool | Notes |
|---|---|---|
| create | `mcp__*__createJiraIssue` | `contentFormat: "markdown"` converts to real ADF |
| comment | `mcp__*__addCommentToJiraIssue` | markdown-aware; a `commentId` updates in place |
| read one | `mcp__*__getJiraIssue` | |
| search | `mcp__*__searchJiraIssuesUsingJql` | e.g. `project = SFO AND statusCategory != Done` |
| edit / labels / parent | `mcp__*__editJiraIssue` | `{"labels":[…]}` **replaces** the list — read-then-union to add; `{"parent":{"key":"KEY-1"}}`, `null` clears |
| links | `mcp__*__createIssueLink`, `mcp__*__getIssueLinkTypes` | |
| transition | `mcp__*__transitionJiraIssue` | only when the **user** asks — closure is out of loop scope |
| type / field metadata | `mcp__*__getJiraProjectIssueTypesMetadata`, `mcp__*__getJiraIssueTypeMetaWithFields` | for checking types/fields before a create |

**The markdown difference is not cosmetic.** The connector converts markdown to real ADF, so
`##` and `**bold**` render. A plain-text path stores them as literal characters — a migration of
119 issues once went in unreadable that way and had to be re-rendered.

### Refs

Bare work-item keys — `SFO-123` — in branch names, commit messages, and PR titles. No keyword
needed: the key is already a distinctive token, and Jira's own integrations index it directly.

Set `aleysian.ticket.project` so the pattern narrows to *this* project's keys (`SFO-[0-9]+`).
Without it the pattern falls back to a generic `[A-Z][A-Z0-9]+-[0-9]+`, which matches any
project's keys including the client's — the audit flags this.

### Referencing a GitHub PR

`guard-closing-keywords.sh` rejects **any** bare `#N` in a jira-tracked project, keyword or not.
For issue references that is exactly right: GitHub resolves `#N` against the repo the text lands
in, which is not this project's tracker, so the reference is either dead or points at — and
notifies — somebody else's issue.

GitHub **pull request** references use identical syntax and are legitimate (`supersedes #482`).
The guard has no way to tell the two apart, so it rejects both. Reference the PR by full URL:

```
supersedes https://github.com/org/repo/pull/482
```

It names the repo as well as the number, so it is unambiguous, survives being quoted into a Jira
comment where `#482` would resolve to nothing, and does not trip the guard. Make it the default
habit rather than the thing you reach for after being blocked.

### Linking commits and PRs back to Jira

**This needs a UI step, once, and then works with zero hook involvement.** Install the **GitHub
for Jira** app on the Atlassian site and connect the GitHub account or organisation that owns the
repo. After that, Jira scans branch names, commit messages, and PR titles for work-item keys and
surfaces them in the work item's **Development** panel.

- **It backfills.** Connecting indexes existing history, so earlier commits still show up.
- **The key must be in the branch name, the commit message, or the PR title.** A key only in the
  PR *body* is not indexed reliably. `commit-msg` already requires it in the message.
- **It is per-repo-connection, not per-key.** A key in a repo Jira does not know about links to
  nothing.

### Smart commits: deliberately blocked

Jira supports commands in commit messages — `SFO-1 #comment shipped #done #time 2h` — which can
transition a work item straight from a commit. `commit-msg` rejects them. An agent writing prose
can transition a ticket by accident, and afterwards an accidental transition is indistinguishable
from a deliberate one. Use the linking app for visibility (which needs no command — just the bare
key), and let the agent run explicit Rovo MCP actions when the user asks for them.

### Creating tickets: a required field can block it

Some Jira projects mark a custom field **required**, and requiredness is scoped **per work type** —
so the same project happily creates a `Bug` and rejects a `Story` with `<Field>: <Field> is
required.`

Metadata does not reliably reveal this. `getJiraIssueTypeMetaWithFields` (createmeta) reports the
fields on the **create screen**; a field that is required but *not on the screen* is both invisible
to the metadata and impossible to satisfy by supplying a value. The admin UI's `Required on` column
is the only authoritative surface. So:

- **Believe the create over any metadata.** If a create fails on a field the metadata calls
  optional, the metadata is what is wrong. A rejected create writes nothing, so it is a
  side-effect-free way to ask "does this project still enforce the field".
- **On our own projects, keep fields optional.** An agent opening a drift-reconciliation ticket
  has nothing meaningful to put in "T-Shirt Sizing", and a required field turns that into a dead
  end. Field schemes are **shared** — an automation-friendly project needs its OWN scheme, never
  an edit to a shared default, which silently removes enforcement from every other project on it.
- **On a client's project** (`ticket.remote=client`) you cannot change the configuration, so
  assume creation may be impossible and only *referencing* works. Humans open the ticket in their
  process; `commit-msg` enforces the ref, which is the part that matters. Say this out loud rather
  than letting someone discover it mid-deploy.

### The hard boundary: hooks cannot use the MCP

`pre-commit`, `commit-msg`, and every `guard-*.sh` are subprocesses invoked by git and Claude
Code. A subprocess has no channel to an MCP server. That is architecture, not preference, and it
is why all Jira work is the agent's.

It is also why there is **no close gate** — beyond the fact that closure is out of scope, one
could not be built over the MCP even if it were wanted: `transitionJiraIssue` takes
`transition: {id}` — an opaque, per-workflow id — not a status name. A subprocess cannot resolve
id → target status without another authenticated call, so it cannot tell "move to In Progress"
from "move to Done", and cannot classify a closure to gate it.

## Acceptance-criteria QA reports (`aleysian-ac-qa`)

The step-7 QA agent posts its pass/fail report the same way everything else in this loop touches
a tracker: as a **comment**, from the agent, never from a hook. It uses `gh issue comment` on
GitHub and `addCommentToJiraIssue` (`contentFormat: "markdown"`) on Jira through the Rovo MCP —
the same two paths described above, for the same reasons. It **checks `ticket.remote` first** and,
on a client tracker, withholds the comment and hands the report to a human, exactly like the
deploy-comment rule. Screenshots stay on disk under `.git/aleysian/qa/<ref>/`; the comment points
at that directory rather than embedding images (reliable upload differs per tracker and host, and
a silent partial upload is worse than a path). The verdict is drawn from the running UI, never
from the code — see the agent at `references/agents/aleysian-ac-qa.md`.

## `client` (`ticket.remote=client`)

Refs are still enforced — their key pattern, so history stays traceable. Everything else steps
back:

- No comments, no labels, no transitions unless it has been agreed. Automation editing a client's
  project management without anyone agreeing to it first is not a feature.
- `auto-label-deploy.sh` says *why* it wrote nothing, because "nothing happened" reads as a bug
  when it was a policy.

Turning any of this on is a client-conversation item, which `init` puts on the checklist.

## `pattern`

For trackers with no usable CLI or MCP. `commit-msg` enforces a regex the team chooses
(`aleysian.ticket.pattern`), and `aleysian.ticket.example` supplies a readable example for error
messages. Refs and the audit trail only — no reads, no writes.

## `none`

Refs optional. The Definition of Done's ticket item degrades to one required line in
`.git/aleysian/ship-log`: what shipped, when, why. Discourage this in `init`'s copy, but support
it — a discipline people can adopt today beats one they have to wait for.
