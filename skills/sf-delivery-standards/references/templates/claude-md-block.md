## Salesforce delivery contract

**Invariant: `{{TRUNK}}` === the org (`{{ORG_ALIAS}}`).** Every deployable change goes:
ticket → worktree → commit gates → validate (dry run) → review → `{{TRUNK}}` → deploy.
Each step gates the next. Small changes do not get a shorter path; there isn't one.

Does NOT apply to docs-only changes (`docs/`, `*.md`, non-deployable files) — commit those directly.

**Work intake (before step 1).** A ticket worth implementing states a user story and Gherkin
acceptance criteria (`Given/When/Then`) with the **persona named** and preconditions concrete
enough to reproduce — shape it with `requirements-capture`. Those AC are what step 7 verifies.

For a supplied ticket, inspect its current state before implementing: matching worktrees and
branches, commits on `{{TRUNK}}`, PR status, and validation or deployment evidence. Missing
clone-local receipts mean **unknown**, not "not run"; a later deployed trunk SHA may contain the
ticket. Do not duplicate work that has already landed.

1. **Ticket first.** Every branch and commit references one: `{{TICKET_EXAMPLE}}` (tracker:
   {{TICKET_SYSTEM}}). **Never** write a closing keyword (`fixes`/`closes`/`resolves #N`) or a Jira
   smart-commit command — this loop never closes a ticket on merge (a keyword would, before the
   deploy has even happened). {{TICKET_ACTIONS}}
{{TICKET_NOTES}}

2. **Worktree always.** Never edit `force-app/` outside one; never nest them. An agent spawned
   with `isolation: "worktree"` is _already_ in one — it branches and commits where it stands.
   Start the agent with the repo root or ticket worktree as its project folder. A parent folder
   that merely contains repos is unmanaged, so the machine-wide hooks intentionally do nothing.
   Check with one plain command: `git rev-parse --absolute-git-dir` — a path ending
   `/.git/worktrees/<name>` means you are in a worktree, plain `/.git` means the main checkout.
   Leaving a worktree open across deploys for follow-up fixes on the same ticket is expected.

3. **Gates run at commit** (prettier: {{FORMAT_POLICY}}; PMD: {{PMD_POLICY}}; ESLint; Jest —
   all scoped to staged files). Run `/simplify` before committing: it is the one quality gate no
   hook can enforce, so it stays on you. Skip it only for trivial metadata (one field, a label).

4. **Validate = `sf project deploy start --dry-run`**, from the worktree, with explicit
   `--source-dir` per changed file and `--test-level RunSpecifiedTests --tests <list>`
   (`NoTestRun` is correct whenever nothing in the change can affect Apex results).
   **Commit first, then validate** — the record is per-commit.
   Never: `deploy validate` (rejects NoTestRun), `RunLocalTests`, `--source-dir force-app`,
   `--target-org`, `--use-most-recent`, or `retrieve` into the **main** checkout. (A
   retrieve inside your worktree is allowed — your own files, caught by the PR diff — but
   prefer authoring in `force-app/` and deploying.)

5. **{{MERGE_INSTRUCTIONS}}**
   Squash policy: {{SQUASH_POLICY}} — one ticket, one commit on `{{TRUNK}}`.

6. **Deploy only from a clean `{{TRUNK}}`** in the main checkout, same files, same tests.
   If it fails: fix forward if under five minutes, otherwise `git revert` and debug in a worktree.
   Never leave `{{TRUNK}}` ahead of the org. After a real deploy, record it on the ticket with a
   COMMENT (the deployed SHA + job id) — never a transition or a close.

7. **Done = all five:** deployed for real{{PUSH_CLAUSE}} + merged + acceptance criteria met +
   user green light + worktree removed. After deploying, point the user at the change in the org
   and **offer** acceptance QA (`aleysian-ac-qa` checks each AC against the **running UI**, not the
   code, and comments a pass/fail report) — run it on their go-ahead, or automatically if
   `aleysian.qa=auto`, never silently. Rework stays on THIS ticket; an AC change or new scope is a
   decision to raise and write into the AC. The ticket stays OPEN — closing is engine scope.

**Never use `--target-org`.** The org is configured project-locally; naming one by hand is how a
command meant for one org reaches another.

**Escape hatches exist, and every use is recorded** — never silent: {{HATCH_LIST}}.
If a guard blocks you, it is right until proven otherwise: read its message rather than routing
around it. The guards live in `~/.aleysian/`, outside this repo, so a branch cannot disarm them.

Deep reference in the installed `sf-delivery-standards` skill: `references/workflow-steps.md`
(exact command sequences and existing-ticket intake), `troubleshooting.md`, `seeding-guide.md`
(org → empty repo, once per project), `drift-reconcile.md` (capturing a Setup change),
`ticket-adapters.md`, `host-adapters.md`. Run `/sf-delivery-standards audit` if anything here looks
wrong or out of date.
