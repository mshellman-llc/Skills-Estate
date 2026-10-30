# Provisioning a new engine instance

One-time-per-client infrastructure. If a project already has a live Cloud Run
service, an installed GitHub App and a `pipeline.yml`, you are not here — you are
in [the SKILL.md](../SKILL.md) operating an existing pipeline.

**One instance per client.** Production JWT credentials are never
multi-tenanted, and the whole reliability argument rests on exactly one writer
existing per environment.

The full walkthrough with console screenshots lives in the engine repo's README
under *Setting Up a New Instance*. This file carries the checklist, the decisions
that are easy to get wrong, and the parts the README does not frame as decisions.

---

## Prerequisites

- `gcloud` authenticated, with billing access on the target org
- `gh` authenticated
- `openssl`
- The client's SFDX repo on GitHub, with the environment branches already existing
- System administrator on every target Salesforce org

---

## Checklist

- [ ] **GCP project** — `gcloud projects create <id>`, link billing, enable `run`, `secretmanager`, `artifactregistry`, `cloudbuild`
- [ ] **Artifact Registry** — `gcloud artifacts repositories create <id> --repository-format=docker --location=us-central1`
- [ ] **JWT key pair** — `openssl req -x509 -sha256 -nodes -days 3650 -newkey rsa:2048 -keyout server.key -out server.crt`
- [ ] **Salesforce Connected Apps** — one per environment. Upload `server.crt`, enable the JWT Bearer flow, and assign the deploy user's profile under Policies. Missing the Policies step is the classic silent failure: auth appears configured and every deploy fails at login.
- [ ] **GitHub App** — permissions Checks, Contents, Issues, Pull requests (read/write), Metadata (read). Subscribe to Push, Pull request, Check run. Generate a private key.
- [ ] **Install the App on the target repository only**
- [ ] **Secrets in Secret Manager** — `github-app-id`, `github-app-installation-id`, `github-app-private-key`, `github-webhook-secret` (`openssl rand -hex 32`), and per environment `sf-client-id-<env>` (the Connected App's Consumer Key) and `sf-jwt-key-<env>` (`server.key`)
- [ ] **Grant secret access** to the Cloud Run service account (`roles/secretmanager.secretAccessor`)
- [ ] **Build and deploy** — see topology below
- [ ] **Configure Google Workspace SSO** — without it the service answers nothing but `/health`
- [ ] **Allow unauthenticated network access** — `--member=allUsers --role=roles/run.invoker`
- [ ] **`pipeline.yml`** in the repo root, including `engine_url` — see [pipeline-config.md](pipeline-config.md)
- [ ] **Bootstrap tags** — `git tag deployed/<branch> <sha>` at the commit matching each org's *current* state, and push them
- [ ] **Verify the webhook** — GitHub App settings → Advanced → Recent Deliveries shows a `ping` with 200
- [ ] **Test PR** — a check run appears
- [ ] **Test merge** — the deploy runs and the tag advances
- [ ] **Hand off** — run `scripts/doctor.sh`, then `sf-delivery-standards init` on the repo for the local loop

Bootstrapping the tags wrong is the one step with no error message. A tag set at
the wrong SHA makes the engine's first delta either enormous or empty, and both
look like the engine working.

---

## Deployment topology

`EXECUTION_MODE` selects it. **Anything other than the exact string
`scale-to-zero` is always-on**, deliberately: a typo must land on the mode that
works.

| | Always-on (default) | Scale-to-zero (opt-in) |
|---|---|---|
| Shape | one container, HTTP + workers | thin service + per-env Cloud Run Job + Cloud Scheduler |
| Cost | Estimate from the selected region and current resource pricing | Estimate from the selected region, job frequency and current resource pricing |
| Single-writer safety | `min-instances=1`, assumed | GCS lease + fencing tokens, enforced |
| Background timers | in-process | none — Cloud Scheduler hits `/internal/reconcile` |
| Dashboard | works | **503s** |
| Acceptance evidence | Require current evidence for the selected engine version and target | Require current evidence, including failure-path tests |

### Always-on

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/<PROJECT_ID>/<PROJECT_ID>/engine:latest .

gcloud run deploy sf-deploy-engine \
  --image=us-central1-docker.pkg.dev/<PROJECT_ID>/<PROJECT_ID>/engine:latest \
  --region=us-central1 --min-instances=1 --no-cpu-throttling --cpu=1 --memory=1Gi \
  --set-secrets="GITHUB_APP_ID=github-app-id:latest,\
GITHUB_APP_PRIVATE_KEY=github-app-private-key:latest,\
GITHUB_APP_INSTALLATION_ID=github-app-installation-id:latest,\
GITHUB_WEBHOOK_SECRET=github-webhook-secret:latest,\
SF_CLIENT_ID_PREPROD=sf-client-id-preprod:latest,\
SF_CLIENT_ID_PROD=sf-client-id-prod:latest,\
SF_JWT_KEY_PREPROD=sf-jwt-key-preprod:latest,\
SF_JWT_KEY_PROD=sf-jwt-key-prod:latest"
```

Setting `ENGINE_STATE_BUCKET` is optional here and worth doing: it is what makes
a pause and the re-validation attempt cap survive a restart. Without it both live
in memory, and the engine warns at startup.

### Then SSO, or nothing works

`/` and every `/api/*` route are gated on a verified Google identity in an allowed
Workspace domain. Unset, the gate **fails closed**, which is correct and also
means a deploy that stops at the step above yields a service answering only
`/health`.

Create an OAuth 2.0 Web application client under **APIs & Services → Credentials**
with redirect URI `https://<SERVICE_URL>/auth/callback`, then:

```bash
echo -n "<OAUTH_CLIENT_ID>"     | gcloud secrets create google-oauth-client-id --data-file=-
echo -n "<OAUTH_CLIENT_SECRET>" | gcloud secrets create google-oauth-client-secret --data-file=-
openssl rand -hex 32 | tr -d '\n' | gcloud secrets create session-secret --data-file=-

gcloud run services update sf-deploy-engine --region=us-central1 \
  --update-env-vars="ALLOWED_HD=<workspace-domain>,ENGINE_PUBLIC_URL=https://<SERVICE_URL>" \
  --update-secrets="GOOGLE_OAUTH_CLIENT_ID=google-oauth-client-id:latest,\
GOOGLE_OAUTH_CLIENT_SECRET=google-oauth-client-secret:latest,\
SESSION_SECRET=session-secret:latest"
```

Set `ALLOWED_HD` explicitly to the authorized Workspace domain. Inspect the selected engine version for any inherited default and reject deployment until it is replaced; never infer a domain from this reusable guide. `AUTH_DISABLED=true`
is local dev only and logs a loud warning; never set it on a deployed service.

Then open the network layer, since Cloud Run IAM can express neither Workspace
SSO nor webhook HMAC:

```bash
gcloud run services add-iam-policy-binding sf-deploy-engine \
  --region=us-central1 --member="allUsers" --role="roles/run.invoker"
```

Verify: `curl https://<SERVICE_URL>/health` returns `{"status":"healthy"}`. An
unauthenticated `curl /` returning 503 means SSO is unconfigured; a redirect to
Google means it is working.

If Jira is a board source, mount the token here too:
`--update-secrets="JIRA_API_TOKEN=jira-api-token:latest"`.

### Scale-to-zero — read this before enabling it

Implemented, unit-tested, and **never run against a real org**. That is the whole
of its provenance. Seven known risks, none of them speculative:

1. **Never exercised in production.** Every timing constant — lease TTL versus
   renewal interval versus GCS round-trip latency — is reasoned, not observed.
   The first real deploy in this mode is the experiment.
2. **The dashboard does not work.** `/api/board`, `/api/stats`, `/api/history`,
   `/api/topology`, `/api/ticket/:ref`, `/api/retry`, `/api/rollback`,
   `/api/release` and `/api/revalidate` all return **503 with a reason** — the
   thin service never clones the repo and has no worker. Closing this needs a
   published read-model: the Job writes a GCS snapshot after each run, the
   service serves it. Scoped, not built. **Do not patch this endpoint by
   endpoint** — that reintroduces the repo dependency the split removed.
3. **A no-op Job still clones.** The Job builds the whole engine before it can
   discover it has nothing to do, and the service wakes *every* environment on
   every delivery, so a push to `preprod` cold-starts `main` too. A pre-build
   exit was considered and rejected: skipping the build also skips the reconcile.
4. **~6 GCS round-trips per queue item.** Folding `dequeue()`'s read and
   compare-and-swap into one `take()` is ~33% fewer, and was deliberately not
   done — this is the correctness core and the current form is the tested one.
   Budget for it if GCS latency in your region is poor.
5. **Event-log pushes bypass `onAuthFailure`.** Reactive token refresh lives on
   the git runner; the log backend shells out to `git` directly. A deploy that
   outlives its installation token parks its log write and retries rather than
   refreshing. Not a correctness hole — the parked queue is durable and the
   reconciler drains it — but expect the noise.
6. **`--depth=1` on the log branch marks the whole clone shallow.** Measured
   harmless today. Set `shallow: false` in the log backend config if anything
   later needs deep history in the main repo.
7. **Image sizes are estimated, not measured.**

Webhook delivery is safe regardless: verified and durably parked before the 202,
so nothing is lost even with every worker down.

---

## Adding an environment to a live instance

1. Provision a Connected App and JWT key pair for the new org.
2. Add `sf-client-id-<env>` and `sf-jwt-key-<env>` to Secret Manager, grant access.
3. Add the environment block to `pipeline.yml`.
4. Add it to `routes:` — as a new step on an existing route's `path`, or as its
   own route. An environment absent from every route deploys fine but has no
   promotion edges.
5. Bootstrap its `deployed/<branch>` tag at the SHA matching the org's current state.
6. Redeploy the service so the new secret refs are wired and the worker is built.
7. Add the branch to `estate.protected` on every clone (`scripts/init.sh` does this).
8. Verify with a test PR.

Step 6 is not optional. Workers are constructed once, at process start.

---

## Onboarding a sandbox (`engine init`)

Adds a `tier: sandbox` row so the sandbox shows on the board and can be a release
source. It does **not** make the sandbox engine-deployed — see
[pipeline-config.md](pipeline-config.md).

```bash
scripts/engine-init <env-name> <org-name> <branch> <username> [--test-level LEVEL]
```

That script is a thin wrapper over `POST /api/engine-init`, and it is server-side
because building the diff needs the engine's git clone and GitHub App identity.
It only opens a PR against `pipeline.yml`. Before merging, provision the
Connected App and JWT key pair and wire `SF_CLIENT_ID_<ENV>` / `SF_JWT_KEY_<ENV>`.
After merging, redeploy.

**Known limitation:** under scale-to-zero, `WORKER_ENVIRONMENTS` is not dynamic,
so a new environment needs the Scheduler and Job wiring updated by hand.

---

## Rotating JWT keys

1. Generate a new pair, upload `server.crt` to the Connected App as an additional
   certificate.
2. Add a new version to `sf-jwt-key-<env>`.
3. Redeploy so the service picks up `:latest`.
4. Confirm a deploy succeeds, then remove the old certificate.

Do the redeploy while the environment is `SETTLED`. Rotating mid-deploy leaves an
in-flight job authenticated against a key the next attempt will not have.

---

## Building the VS Code extension

Not on the marketplace, so there is no auto-update.

```bash
cd packages/vscode
npm install && npm run build
npx @vscode/vsce package
code --install-extension sf-deploy-engine-<version>.vsix
```

Take the version from `packages/vscode/package.json` rather than copying a number
out of any doc. The `code` CLI must be on PATH — in VS Code, `Cmd+Shift+P` →
*Shell Command: Install 'code' command in PATH*.

Rebuild whenever `packages/vscode/src/` changes and developers need the update.
Once more than a couple of people depend on it, treat the absence of auto-update
as a real gap rather than a nice-to-have.

---

## Handoff

Provisioning is done when:

1. A test PR against every environment branch has validated and deployed.
2. `deployed/<branch>` exists and matches actual org state for every environment.
3. `pipeline.yml` is committed with the right `engine_url`.
4. The GitHub App is installed and its recent deliveries are 200s.
5. `scripts/doctor.sh` exits 0.

Then run `scripts/init.sh` to wire the repo, and `sf-delivery-standards init` for
the local loop. Keep provisioning detail — GCP project ids, secret names,
Connected App setup — **out** of the client repo's `CLAUDE.md`. Keep it in the authorized private project record, outside this reusable skill and its distributions.
