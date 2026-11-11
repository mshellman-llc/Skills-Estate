# Operating the engine — auth, API, dashboard, extension

Everything here assumes `ENGINE_URL` is set from `pipeline.yml`'s `engine_url`.
`scripts/engine.sh` wraps all of it; the raw calls are documented so you can
debug when the wrapper is not the problem.

---

## Authentication

`/` and `/api/*` are behind Google Workspace SSO, default-deny. Exempt:
`/health` (open), `/webhook` (HMAC), `/internal/*` (its own machine auth, also
fail-closed).

There are three credential paths and they do not interchange:

| Caller | Credential | Where it lives |
|---|---|---|
| Browser | httpOnly session cookie | set by `/auth/callback` |
| VS Code extension | session token as `Authorization: Bearer` | `vscode.SecretStorage`, the OS keychain |
| Terminal, scripts, agents | CLI token as `Authorization: Bearer` | `~/.config/sf-deploy-engine/token` |

A bash process reaches neither the browser cookie nor the keychain, which is why
the CLI token exists. Mint it once:

```bash
open "$ENGINE_URL/auth/login?redirect=cli"     # sign in with a Workspace account
# run the command the page prints — writes ~/.config/sf-deploy-engine/token, mode 600
```

Valid 30 days. On a 401, re-run that login. `SFDE_TOKEN` overrides the file.

Revocation is coarse by design: there is no revocation list, so revoking means
rotating `SESSION_SECRET`, which invalidates every browser, VS Code and CLI
session at once. That is the same blast radius the system already had, and it is
a deliberate scope limit rather than an oversight — do not build a token
management UI without a reason.

### Reading a 401 vs a 503

- **401** — your token is missing, expired, or minted against a different
  `SESSION_SECRET`. Re-run the CLI login.
- **503 on everything but `/health`** — the service has no
  `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `SESSION_SECRET`, so
  the SSO gate is failing closed. That is a provisioning fix on the Cloud Run
  service, not something a caller can work around.
- **503 with a reason naming scale-to-zero** — a different thing entirely. See
  [provisioning.md](provisioning.md).

`AUTH_DISABLED=true` exists for local development only.

---

## Endpoint reference

### `GET /api/status`

The one to reach for first.

```json
{
  "paused": false,
  "repo": "Aleysian/64-Org-Aleysian",
  "environments": {
    "preprod": {
      "state": "SETTLED",
      "deployedTag": "a1b2c3d4",
      "inFlightJobId": null,
      "deployUrl": null,
      "freezeReason": null,
      "currentItem": null,
      "queueLength": 0,
      "queue": []
    }
  }
}
```

`state` is `SETTLED` | `DEPLOYING` | `FROZEN`. `currentItem` is the single item
in flight — a worker processes one at a time per environment, and deploys
preempt validations. `deployUrl` is a clickable Salesforce deploy-status link,
present only when `instance_url` is configured for the environment.

Read `freezeReason` before doing anything about a freeze.

### `POST /api/retry/:environment`

No body. Refuses with 400 unless the environment is `FROZEN`. Lifts the freeze
and enqueues a deploy at the branch's current HEAD, resolving the PR number from
the merge commit message on a best-effort basis.

Retry re-runs the deploy **and** the post-hooks. If the cause was bad metadata
rather than a transient failure, roll back instead — retrying walks into the same
wall and burns another test run.

### `POST /api/revalidate`

```json
{ "prNumber": 412 }
```

Re-runs validation at the PR's **live head SHA**, clears the recorded failure and
bypasses the per-PR attempt cap. A human asking is treated as explicit intent.
This replaces the old push-an-empty-commit workaround. Omitting `prNumber` asks
the engine to resolve it.

### `POST /api/rollback`

```json
{ "environment": "main", "ticket": "GH-397", "mode": "pr" }
```

Exactly one of `sha` or `ticket` — sending both, or neither, is a 400.

- **`ticket`** is resolved to the deploy that carried it in that environment, via
  the model's ticket → deploy join. Any identifier a **configured** provider
  recognises: `GH-397`, `ORG64-42`, or canonical `jira:ORG64-42`.
- **`sha`** is a merge commit on the environment's branch.
- **`mode: "pr"`** (default) opens a revert PR, so the inverse deployment is
  validated before it merges.
- **`mode: "direct"`** pushes the revert straight to the branch. Emergencies.

The revert is `git revert -m 1`, which is why merge commits are non-negotiable.
sgd turns the resulting diff into the exact inverse package: modified components
at their prior versions in `package.xml`, added components in
`destructiveChanges.xml`. It then flows through the ordinary validate → merge →
deploy loop, so a rollback is not a special path with its own bugs.

A 503 here means the delivery model could not be built, so the ticket could not
be resolved. Fall back to `sha`.

### `POST /api/release`

Selective promotion. Two accepted shapes, normalized to the same thing:

```json
{ "tickets": ["GH-397", "GH-401"], "from": "preprod", "to": "main" }
```

```json
{ "tickets": [
    { "ticket": "GH-397", "from": "stevenc2" },
    { "ticket": "ORG64-42", "from": "meg-dev" }
  ],
  "to": "preprod" }
```

`to` is optional and defaults to the target **every** selected source agrees on.
When the sources share no target the request is refused rather than one being
picked. A mixed release lands as a single cherry-pick branch, so there is exactly
one target.

The gate is tier-aware. A `tier: pipeline` source must promote along a declared
one-hop forward edge — arbitrary cross-edges would break the cherry-pick's
merge-commit ancestry assumptions. A `tier: sandbox` source may release into any
**route entry point**, which is the only thing a sandbox can reach, since
sandboxes are deliberately absent from `routes:`.

Identifiers are fail-closed: anything no configured provider recognises is a 400,
not a guess.

Two refusals to read carefully rather than retry around:

- **"No merged PR delivering X found on \<src\>"** — a release cherry-picks merge
  commits. Work pushed directly to a branch is visible on the board, which reads
  commit messages, but is not releasable until it lands as a merge.
- **Unattributed commits** — a candidate merge carries work no selected ticket
  accounts for. This check is deliberately fail-closed and resolves attribution
  per commit by text match rather than from the ledger, because a bare merge with
  no delivery ref of its own is precisely what it exists to catch.

If one PR closed several tickets, the merge is cherry-picked once and the release
reports the whole delivered set, including the ride-alongs you did not name.

The release branch is `release/<tickets>-<unique>`. The ticket refs are in the
branch name on purpose: a release merge commit's subject carries its head branch
name, which is what lets a later promotion-of-a-promotion resolve attribution
through the chain.

### `POST /api/pause` · `POST /api/resume`

No body. While paused, webhooks are acknowledged but not processed. Under an
always-on deployment without a GCS bucket the pause flag lives in memory and does
**not** survive a restart — the engine warns about this at startup.

Pause is for exactly one situation: git has to be reconciled to the org by hand.

```bash
scripts/engine.sh pause
git tag -f deployed/main <sha> && git push origin deployed/main --force
scripts/engine.sh resume
```

Tell the team. A paused engine and a quiet engine look identical from GitHub.

### `GET /api/topology`

The DAG, for anything that draws or reasons about it.

```json
{
  "repo": "owner/repo",
  "environments": [
    { "name": "preprod", "branch": "preprod", "production": false,
      "instanceUrl": null, "layer": 0, "tier": "pipeline",
      "entryLabels": [], "gatedEntry": false, "promotesTo": ["main"] }
  ],
  "routes": { "standard": { "path": ["preprod", "main"] } },
  "edges": { "forward": [{ "from": "preprod", "to": "main", "routes": ["standard"] }],
             "back": [] }
}
```

`layer` is the longest forward path from any entry point, for left-to-right
rendering. **`tier: sandbox` rows appear here but carry no route edges** — a
consumer drawing the DAG must skip them or render an orphan at layer 0. For a
sandbox, `promotesTo` is the set of route entry points, because that is where a
human releasing sandbox work can actually send it.

### `GET /api/board`

The kanban payload: tickets in environment columns, keyed on provider-aware
`TicketRef`, sourced from whichever providers `tickets.board` names. Cached
briefly; on a build failure the last good payload is served rather than an error,
so a transient Jira outage does not blank the board.

`sandboxes.title` names the Dev Sandboxes column. An older VS Code extension
against a newer engine falls back to the raw column id.

### `GET /api/history`

Query: `env`, `limit`, `before` (ISO timestamp). Returns the activity feed built
by replaying the event log, with anything still parked merged in — so the feed
and the KPI band agree with `/api/status` during an outage instead of showing an
environment frozen by a failure the feed has no record of.

### `GET /api/stats`

Query: `window` (days, clamped 1–365, default 30). KPI tiles and the activity
timeline.

### `GET /api/ticket/:ref`

Trace one ticket: where it is now, every deploy that ever carried it, and what
each of those deploys carried alongside it.

URL-encode the ref — the canonical form contains a colon
(`jira%3AORG64-42`). `GH-397`, `ORG64-42` and `github:397` all work. An
identifier no configured provider recognises is a **400, not an empty result**:
fail-closed applies to reads too, because a confident empty "never shipped" is
worse than a rejection.

### `POST /api/engine-init`

Opens a PR adding a `tier: sandbox` row to `pipeline.yml`. Server-side because it
needs the engine's git clone and GitHub App identity. **Merging that PR does not
make the sandbox live** — workers are built once at process start, so it takes
effect on the next redeploy, and the Connected App plus JWT key must be
provisioned first. Runbook: [provisioning.md](provisioning.md).

### `POST /internal/reconcile`

Outside SSO — Cloud Scheduler cannot log in — with its own machine auth (OIDC or
a shared bearer secret), fail-closed when unconfigured. Scale-to-zero's
replacement for the in-process reconciler timer.

---

## Dashboard

Served at the engine root, gated on the same SSO. Two views, deep-linkable via
`#board`.

**Pipeline** — the routes DAG, a KPI band, per-environment cards with live FSM
state and queue, and a day-grouped activity feed. Retry and rollback controls.

**Board** — engine-state-aware kanban. Cards show validating / validated /
deploying / deployed / failed, with a dashed border and pulse for in-progress
work, an `Express` badge on express-labelled issues, columns sorted active-first
and capped at 10 with expansion, DONE hidden by default.

**Dev Sandboxes column** — present when any `tier: sandbox` environment is
registered. Sits left of the pipeline's entry environment and holds tickets with
work on a sandbox branch that the pipeline has not claimed. Each card is badged
with the sandbox carrying it. Pure git visibility: read from commit messages in
the engine's clone, never from the org.

**Release builder** — click cards to select; `all` in a column header selects
everything promotable there. Selection spans columns and sandbox branches, so one
release PR can gather work from several sandboxes, and a card carried by two
sandboxes selects per badge. The promote bar offers only targets every selected
source can reach, and disables itself when they share none.

Local UI work with no engine: `node scripts/ui-preview.mjs 4599` in the engine
repo, which serves the dashboard against faked `/api/*` responses.

---

## VS Code extension

Auto-detects `pipeline.yml` and reads `engine_url` from it, or
`.vscode/settings.json`:

```json
{ "sfDeployEngine.engineUrl": "https://<SERVICE_URL>" }
```

- **Status bar** — `preprod: SETTLED | main: DEPLOYING`
- **Pipeline panel** — vertical DAG with live FSM states, gate locks and
  back-merge annotations, KPI grid, recent activity. Degrades gracefully against
  an engine predating `/api/topology`, `/api/stats` or `/api/history`
- **Environments panel** — per-env FSM state, expanding to the queue
- **Tickets panel** — engine-state-aware icons, active-first, 10 per section,
  DONE hidden. A registered sandbox gets its own group labelled from
  `/api/board`'s `sandboxes.title`
- **Notifications** — deploy success; freeze alerts with Retry and Rollback actions
- **Commands** — Refresh Status, Retry Environment, Re-validate PR, Rollback Merge
  Commit, Pause/Resume Engine, Open Dashboard, Open Engine Logs, Sign In / Sign Out

Auth mirrors the dashboard: a browser round trip to `/auth/login` with a
`vscode://` callback, token in SecretStorage.

It is not on the marketplace, so there is no auto-update. Building the `.vsix`:
[provisioning.md](provisioning.md).
