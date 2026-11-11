# `pipeline.yml` — the whole schema

One file in the client repo root. The engine parses it with Zod at **bootstrap
only**, so every change here needs an engine restart or redeploy before it is
live. Merging the config is necessary and not sufficient — this is the single
most common "I changed it and nothing happened."

Authoritative source: `src/config.ts` in the engine repo. When this file and that
file disagree, that file wins.

---

## Minimum viable config

```yaml
engine_url: https://sf-deploy-engine-<hash>.us-central1.run.app

environments:
  preprod:
    org_name: 64_Staging
    branch: preprod
    secret_ref: projects/aleysian/secrets/sf-jwt-preprod
    username: someone@example.com.staging
    test_level: RunLocalTests
    freeze: strict
    destructive_requires_label: false
    production: false
  main:
    org_name: 64_Prod
    branch: main
    secret_ref: projects/aleysian/secrets/sf-jwt-prod
    username: someone@example.com
    test_level: RunLocalTests
    freeze: strict
    destructive_requires_label: true
    production: true

routes:
  standard:
    path: [preprod, main]
```

`engine_url` is read by the VS Code extension and by this skill's scripts. It is
not part of the Zod schema, so a typo there fails at call time rather than at
boot.

---

## `environments:`

A map of environment name → config. The name is the key used everywhere else
(routes, `/api/retry/:environment`, release sources).

| Field | Type | Required | Notes |
|---|---|---|---|
| `org_name` | string | yes | Descriptive only. Shown in the dashboard and the VS Code panel. |
| `branch` | string | yes | The git branch this environment deploys from. Environment name and branch are independent; do not assume they match. |
| `secret_ref` | string | yes | Secret Manager resource path for the JWT key. |
| `username` | string | yes | Salesforce login username the JWT authenticates as. |
| `test_level` | enum | yes | `RunLocalTests` \| `RunSpecifiedTests` \| `NoTestRun`. |
| `freeze` | enum | no, default `strict` | `strict` parks the worker on failure until a human retries. `advisory` records and surfaces the failure but keeps draining the queue. |
| `destructive_requires_label` | bool | yes for `tier: pipeline` | When true, a delta carrying a `destructiveChanges` manifest is blocked unless the PR has `destructive-approved`. |
| `production` | bool | no, default `false` | Disables smart-test skip unconditionally. Salesforce forbids `NoTestRun` in production anyway. |
| `instance_url` | string | no | Used to build a clickable Salesforce deploy-status link on board cards and PR comments. |
| `tier` | enum | no, default `pipeline` | `pipeline` \| `sandbox`. See below. |

### `tier: sandbox`

A registered sandbox is **visibility infrastructure, not a managed environment**.
It gets:

- a Dev Sandboxes column on the kanban, holding tickets with work on that branch
  that the pipeline has not claimed yet, badged with the sandbox carrying them
- standing as a legal `/api/release` **source** into a route entry point

It does **not** get a worker, a `deployed/<branch>` tag, or any engine-driven
deploy. The board column is read out of the engine's git clone by parsing commit
messages; the engine never touches the sandbox org. A ticket leaves the column
the moment the pipeline claims it.

`destructive_requires_label` may be omitted for a sandbox row and defaults to
`false`. For `tier: pipeline` it stays mandatory, and omitting it throws at boot
with the environment named.

This was tried the other way — full engine-managed sandboxes, v7 Parts 3 and 4 —
and revised back on 2026-08-03. Read
`docs/decisions/sandboxes-are-environments.md` before re-proposing it.

### `freeze: advisory`

Relaxes the FROZEN block-until-human gate in `src/worker/loop.ts`'s run loop: the
failure is still logged and still surfaced on the dashboard and via the
`deploy:failed` label, but the loop keeps draining its queue instead of parking.
Intended for low-stakes tiers. A consecutive-failure circuit breaker still trips
it after N failures, so an advisory environment cannot fail silently forever.

---

## `routes:` — the promotion DAG

```yaml
routes:
  standard:
    path: [preprod, staging, main]
    back_merge: [preprod]
  hotfix:
    path: [main]
    entry_requires_label: hotfix
```

| Field | Notes |
|---|---|
| `path` | Ordered list of environments, at least one. Consecutive pairs are **forward edges**. |
| `entry_requires_label` | Label required on a PR entering this route's entry point (`path[0]`) directly. |
| `back_merge` | Environments to merge back into after a successful deploy to this route's **terminal** env. |

### Edge semantics

- **Forward edges** are promote-only, by cherry-pick or PR. The union of every
  route's forward edges must be **acyclic** — a cycle throws at config load with
  the offending edges named.
- **Back-merge** targets fire after a successful deploy to the route's terminal
  environment, and are constrained to be strictly **upstream** of it. That
  constraint is what stops a back-merge from quietly creating a forward promotion
  path.
- Referencing an environment that is not in `environments:` throws at load.

### The entry gate

`entry_requires_label` exists for the hotfix case: a route whose entry point is
production, which must not be enterable by anyone opening a PR against `main`.
Exemptions are evaluated in this order:

1. **Engine-owned head branches** — `release/`, `express/`, `backmerge/`,
   `revert/`. The engine constructs these names in exactly one place, so the
   gate's prefix list and the construction sites cannot drift apart.
2. **Bulk promotion** — the PR's head *is* an upstream environment's branch
   (`preprod` → `main`).
3. **Direct entry with the label** — the PR carries one of the route's entry labels.

Anything else is a direct entry missing its label, and is blocked with a message
naming both the label and the promotion path it should have used instead.

An entry point is only gated when **every** route entering it is gated. If one
ungated route enters an environment, that ungated route is the standard way in
and direct PRs need no label.

### Migrating from `promotions:`

```yaml
promotions:
  - from: preprod
    to: main
```

Still loads. It is translated into a synthetic `standard` route and logs a
deprecation warning. Setting both `routes:` and `promotions:` uses `routes:` and
ignores `promotions:` with a warning. Neither is valid too, and yields an empty
topology — the engine still deploys, it just has no promotion targets, so
`/api/release` refuses everything with "No promotion route configured from X."

Migrate: the legacy shape cannot express hotfix entry points or back-merge.

---

## `tickets:` — GitHub, Jira, or both

Optional. **Absent means GitHub only** — byte-for-byte the behaviour from before
providers existed, which is why a config written before this block existed
normalizes to exactly the same object it always did.

```yaml
tickets:
  extract: [github, jira]
  board:   [github, jira]
  jira:
    base_url: https://<site>.atlassian.net
    email: <the account the API token belongs to>
    projects: [ORG64]
    deployments: true
```

| Field | Default | Notes |
|---|---|---|
| `extract` | `[github]` | Which providers' identifiers are recognised in commit and PR text. Free, read-only, regex only. |
| `board` | `[github]` | Which providers supply kanban cards. A credentialed API read when it includes `jira`. |
| `jira.base_url` | — | Required when Jira is used. |
| `jira.email` | — | The account the API token belongs to. Required for `board: [jira]`. |
| `jira.projects` | `[]` | Uppercase project keys. The extraction regex is **built from this list**. |
| `jira.deployments` | `false` | Emit GitHub Deployments so Jira renders its native deployments panel. |
| `jira.secret_ref` | — | Documentation only. The engine never resolves it. |

**The two lists are separate on purpose.** `extract` costs nothing and should
stay on permanently once a tracker has ever been used, because commits written
during that period name its tickets forever. `board` is the one that changes what
you see; reverting is `board: [github]` plus a redeploy, with no data migration.

**`projects` is load-bearing, not a convenience.** The Jira key regex is built
from the allowlist and never from the general key shape, because
`/[A-Z][A-Z0-9]+-\d+/` also matches `UTF-8`, `SLDS-2` and `ISO-8601`. No
allowlist, no Jira extraction — and the engine says so at load rather than
silently extracting nothing.

**`board: [jira]` is validated at config load and refuses to start** without
`base_url`, `email` and `projects`. The failure being prevented is a board that
renders with every Jira card missing, which reads as "nothing to ship" rather
than as a broken integration.

**The token is never in this file.** Mount `JIRA_API_TOKEN` from Secret Manager
with `--set-secrets`, alongside the Salesforce keys.

Lowercase project keys are rejected rather than coerced, because a lowercase key
would build a regex matching nothing and the operator would see "Jira extraction
quietly does nothing" instead of an error.

---

## `smart_tests:`

```yaml
smart_tests:
  enabled: true
  label: run-tests
  # safe_types: [...]   # optional; replaces the built-in list entirely
```

After computing the delta, the engine reads the `<types>` out of the generated
`package.xml`. If **every** type is on the safe list, the test level is
downgraded to `NoTestRun`.

Three gates, any of which restores the configured level:

- `production: true` on the environment — always, unconditionally
- the `run-tests` label on a linked issue — the per-issue override
- any unsafe type in the delta

The built-in safe list is 43 types, all of which are incapable of breaking an
Apex test: `ActionLinkGroupTemplate`, `AnalyticSnapshot`, `AppMenu`, `Audience`,
`Bot`, `BotVersion`, `BrandingSet`, `ContentAsset`, `CustomApplication`,
`CustomApplicationComponent`, `CustomFeedFilter`, `CustomHelpMenuSection`,
`CustomLabel`, `CustomObjectTranslation`, `CustomPageWebLink`, `CustomSite`,
`CustomTab`, `CustomValueSetTranslation`, `Dashboard`, `DashboardFolder`,
`Document`, `EmailTemplate`, `ExperienceBundle`, `FlexiPage`,
`GlobalValueSetTranslation`, `HomePageComponent`, `HomePageLayout`, `Layout`,
`Letterhead`, `LightningExperienceTheme`, `LightningMessageChannel`, `ListView`,
`NavigationMenu`, `PathAssistant`, `QuickAction`, `Report`, `ReportFolder`,
`ReportType`, `SiteDotCom`, `StandardValueSetTranslation`, `StaticResource`,
`Translations`, `WebLink`.

Notably absent, and deliberately: `ApexClass`, `ApexTrigger`, `CustomObject`,
`CustomField`, `Flow`, `LightningComponentBundle`, `AuraDefinitionBundle`,
`PermissionSet`, `Profile`.

`safe_types` **replaces** the built-in list rather than extending it. Adding a
type to it is a claim that the type cannot break any Apex test in this org. Make
that claim with an argument, not a hunch: a false negative costs one full test
run, a false positive ships untested metadata.

A permission set in the delta is an unsafe type, so permission-set changes always
carry the full suite. Batch them rather than promoting one at a time.

---

## `express:`

```yaml
express:
  enabled: true
  label: express
```

Automates validate → merge → deploy → promote with no human wait between steps.
Validation still runs and tests are never skipped — express removes waiting, not
checking.

- **ALL** linked issues on the PR must carry the label. A mixed PR falls back to
  the normal flow; there is no partial express.
- The flag is checked at **action** time, not enqueue time, so adding or removing
  the label changes behaviour live.
- Each promotion is an isolated cherry-pick PR on an `express/` head branch, and
  is independently revertible.
- Audit events: `express_merged`, `express_promoted`.

---

## `deploy_hooks:`

```yaml
deploy_hooks:
  enabled: true
  # path: deploy-hooks          # default
  # require_ticket_ref: false   # true = every changed hook file must name a ticket
```

Anonymous Apex run around a deploy. Layout, ordering, failure semantics and the
idempotency requirement are in [the SKILL.md](../SKILL.md#prepost-deploy-apex-hooks).

`require_ticket_ref: true` fails validation, at review time, for a hook file with
no parseable ticket reference. Name a hook after its issue with a leading numeric
prefix (`123-cleanup.apex`, which also sets run order) or `GH-123` / `#123`
anywhere in the filename. The linked issue then picks up the deploy's normal
`env:*` labelling, so hook execution shows up in that ticket's board and activity
view with no separate tracker.

---

## `normalize:`

```yaml
normalize:
  script: scripts/normalize-metadata.js   # this is the default
```

Runs the **repo's own** checked-in normalizer at PR head and fails validation on
drift. The repo's script is the source of truth for what "normalized" means; the
engine just runs it.

Scoped to the files the PR actually changed. The repo's normalizer scans the
whole tree, so an unscoped check would fail a PR for drift a teammate introduced
elsewhere — a file is only reported iff the repo's normalizer named it in its
output. No script in the repo means nothing to enforce.
