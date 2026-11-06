# Troubleshooting

Run `scripts/doctor.sh` first. Most of what follows is something it already
names, and it distinguishes failures that look identical from the outside.

---

## The service is not answering

| Symptom | Cause | Action |
|---|---|---|
| Everything 503s but `/health`, always-on mode | The Workspace SSO gate failing **closed** because `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `SESSION_SECRET` are unset on the service | Configure SSO — [provisioning.md](provisioning.md) § "Then SSO, or nothing works". Not a code problem. |
| A specific set of `/api/*` routes 503 with a written reason, everything else works | `EXECUTION_MODE=scale-to-zero`. The thin service never clones the repo, so anything needing the log or a worker cannot answer | Expected. The fix is a published read-model, which is scoped and unbuilt. Do not patch it route by route. |
| 401 on every API call | Token missing, expired past 30 days, or minted against a rotated `SESSION_SECRET` | Re-run `$ENGINE_URL/auth/login?redirect=cli` |
| `curl /` returns 503 but the browser works | Correct behaviour. `/` serves dashboard HTML to a signed-in browser and is not a useful curl target | Use `/health` for liveness |
| Nothing at all, including `/health` | The service is down or the image failed to start | Cloud Run logs. A config-load throw (bad route topology, `board: [jira]` without credentials) kills the process at boot with the reason named. |

---

## The engine is not reacting

| Symptom | Action |
|---|---|
| No check runs appear on a PR | Verify the GitHub App is installed and not suspended, then check webhook deliveries in the App's settings → Advanced → Recent Deliveries. Non-200s there are the whole story. |
| Webhook deliveries are 200 but nothing happens | Check whether the engine is paused — `scripts/engine.sh status`, field `paused`. A paused engine acknowledges deliveries and processes nothing, and looks exactly like a quiet one from GitHub. |
| Changed `pipeline.yml` and the new behaviour is not live | The engine reads config **once, at bootstrap**. Redeploy or restart the service. This is the single most common one. |
| Added a new environment and it has no worker | Same cause. Workers are built once at process start. |
| Enabled `deploy_hooks` but hooks never run | Restart first. Then confirm the scripts are under `deploy-hooks/pre\|post/`, end in `.apex`, and actually landed inside the deploy's delta window — hooks are delta-driven and run exactly once, in the deploy that first carries them. |
| Check run stuck "in progress" for a long time | Validation runs the full suite, so ~15 minutes is normal. Beyond that, check Cloud Run logs and `scripts/engine.sh status` for the in-flight job. |

---

## An environment is FROZEN

Read `freezeReason` before acting — `scripts/engine.sh status`.

| Reason resembles | What happened | Action |
|---|---|---|
| A Salesforce deploy error | Metadata failed against the org | Fix forward in a new PR, or roll back. Retrying identical metadata walks into the same wall and costs another test run. |
| A transient failure — auth, network, git | Nothing is wrong with the metadata | `scripts/engine.sh retry <env>` |
| `pre-hook … failed` | A pre-deploy Apex script threw. **Nothing deployed.** | Fix the script or the org state it assumes, then retry |
| `post-hook … failed` | Metadata deployed, the tag did **not** advance | Retry re-runs deploy **and** post-hooks, so the hook must be idempotent. The unmoved tag is deliberate: it keeps the deployed-versus-actual gap queryable. |
| A destructive-changes block | The delta deletes metadata and the environment sets `destructive_requires_label` | Review what is being deleted, then add `destructive-approved` to the PR. Read the destructive manifest first — this gate exists because deletions are the one irreversible class. |
| An entry-gate block | A direct PR into a gated route entry point | Add the route's entry label, or promote through the upstream environment instead. The message names both. |

Retry refuses with 400 on an environment that is not FROZEN. That is the guard
working.

---

## Deploys and validations

| Symptom | Explanation |
|---|---|
| Validation passed but the merge ran a full deploy, not a quick one | Quick deploy needs all three: same SHA validated, org state unchanged (the tag has not moved), validation under 10 days old. Any miss falls back to a full deploy. That fallback is the design. A false-positive quick deploy would ship untested metadata; a false negative costs 30 minutes. |
| Validation is running tests you expected to be skipped | `smart_tests` downgrades to `NoTestRun` only when **every** type in the delta is safe. A `production: true` environment never downgrades, the `run-tests` label forces tests, and permission sets, Apex, objects, fields, flows and LWC are all unsafe types. |
| A `NoTestRun` / test-level error from the CLI on a non-prod org | This was engine issue #14 and is **fixed** — the engine uses `sf project deploy start --dry-run` rather than the `validate` subcommand, which rejects `NoTestRun` and `RunSpecifiedTests` on non-prod orgs. If you are seeing it now, something is invoking `validate` directly. |
| A deploy is running that nobody started | Check `/api/history` and the reconciler. In-flight deploys survive restarts by re-attaching via `sf project deploy resume`, so a restart can look like a spontaneous deploy. |
| The delta is enormous or empty on the first deploy after setup | `deployed/<branch>` was bootstrapped at the wrong SHA. This step has no error message. Pause, set the tag at the commit that actually matches the org, resume. |

---

## Releases and promotion

| Symptom | Explanation |
|---|---|
| "No merged PR delivering X found on \<src\>" | A release cherry-picks merge commits. Work pushed straight to a branch is visible on the board — which reads commit messages — but is not releasable until it lands as a merge. |
| The release is refused for unattributed commits | A candidate merge carries work no selected ticket accounts for. Read what it names. This is the ride-along guard and it is deliberately fail-closed. |
| "No promotion target is shared by all selected sources" | A mixed release lands as a single cherry-pick branch, so there is exactly one target. Either narrow the selection or name `--to` explicitly, if a legal shared target exists. |
| "X → Y is not a promotion edge on any configured route" | Promotion follows declared one-hop forward edges. Arbitrary cross-edges break the cherry-pick's merge-commit ancestry assumptions. |
| "\<src\> is a dev sandbox — work can only be released into a route entry point" | Correct. Sandboxes are absent from `routes:` by design, so the only thing they can reach is the way *into* the pipeline. |
| Already-promoted work still shows as pending in `git log` | Promotions are cherry-picks, so the downstream commit has a new SHA. Use `scripts/doctor.sh --ready`, which compares by patch-equivalence of each merge's first-parent diff. |
| An identifier is rejected as unrecognised | Fail-closed by design. Only providers listed in `tickets.extract` are recognised, and a Jira key must be in `tickets.jira.projects`. |

---

## Board and tickets

| Symptom | Explanation |
|---|---|
| The board renders with no Jira cards | Almost always `JIRA_API_TOKEN` unmounted or expired. The engine refuses to *start* without `base_url` / `email` / `projects`, so a running engine with an empty board is a credential problem, not a config one. This failure is the reason that config validation exists — an empty board reads as "nothing to ship". |
| Jira references are never extracted | `tickets.jira.projects` is empty. The regex is built from the allowlist, never from the general key shape. The engine warns about this at load. |
| A lowercase Jira project key is rejected at boot | Deliberate. A lowercase key would build a regex matching nothing, and silence is worse than a boot error. |
| The Dev Sandboxes column is missing | No `tier: sandbox` environment is registered in `pipeline.yml`, or the engine has not restarted since one was added. |
| A ticket sits in a column it already left | The board is engine-state-aware but caches briefly, and on a build failure serves the last good payload rather than erroring. Give it a refresh cycle. |
| `env:*` labels on GitHub disagree with the board | The board is right. Engine-written labels are **write-only** decoration for humans; delivery state comes from the event log. Never read them back as truth. |

---

## Git and tags

| Symptom | Action |
|---|---|
| Someone deployed manually to an environment org | `deployed/<branch>` now lies. Pause → land the deployed content as commits on the branch → move the tag to match → resume. Do not skip the commits: the point of the tag is that git at the tag describes the org. |
| `deployed/<branch>` is behind the branch HEAD and nothing is queued | A deploy failed or was lost. Check `freezeReason` and `/api/history`. If the environment is SETTLED and the tag is behind, that is a genuine anomaly — `doctor.sh` flags it. |
| A rollback needs re-landing | New branch, `git revert <revert-sha>`, add the fix, new PR. Never reuse the original branch. |
| Someone squash-merged | `git revert -m 1` and `git cherry-pick -m 1` both need real merge commits, so that work is now hard to roll back or promote selectively. Disable squash and rebase at the repo level: `gh api repos/<owner>/<repo> -X PATCH -f allow_squash_merge=false -f allow_rebase_merge=false`. |

---

## When to stop and ask

Two situations where the right move is to stop rather than act:

- **A destructive gate blocked something and you are not sure what is being
  deleted.** Read the destructive manifest. Approving it is the one irreversible
  class of action in the pipeline.
- **The engine's state and the org's state disagree and you cannot explain why.**
  Every repair from here involves moving a tag or force-pushing, and a wrong
  guess makes the gap invisible instead of fixing it.
