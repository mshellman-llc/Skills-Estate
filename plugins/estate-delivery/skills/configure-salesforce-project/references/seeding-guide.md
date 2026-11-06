# Seeding Guide — `/configure-salesforce-project seed`

Getting an existing org's metadata into an empty repo for the first time. In direct
delivery this establishes `trunk === org`. In DevOps Center it establishes production
as the canonical baseline before any pipeline branch or work item exists.

> Substitutions from the retired predecessor: `main` -> `git config estate.trunk`, and the
> escape hatch is now `ESTATE_ALLOW_RETRIEVE=1`. Everything else in this guide — the
> manifest-first sanitisation, the five exclusion reason classes, the round-trip proof —
> is unchanged, because none of it depends on the host or the tracker.
> `force-app/main/default` is a PATH and stays literal.

This runs **once per project**, and it is the only moment in this skill's entire
model where the org is upstream of the repo. Every other day of the project's
life, the repo is the source of truth and the org is downstream of it. That
inversion is why seeding gets its own guide, its own place in the setup order,
and its own way out afterwards.

**The metadata curation is delivery-tool neutral.** The activation order is not. A
DevOps Center repository must be seeded and pushed before the project is connected and
activated, or the service can create stage state against an incomplete baseline.

## DevOps Center activation order

For `estate.delivery=devops-center`, use this order:

1. Create the private repository and scaffold the Salesforce project.
2. Copy and curate `.forceignore`, then retrieve the production baseline.
3. Complete the prune and round-trip dry run in this guide.
4. Commit and push the baseline to `main`.
5. Create `staging` from that exact `main` commit and push it.
6. Refresh the Staging and `sandbox-a` sandboxes from production, so their starting
   metadata and org-bound user references derive from the same source.
7. Connect the repository, branches, environments, and project in DevOps Center.
8. Only then run `install.sh --repo --delivery devops-center ...` to arm the local
   contract and hooks, and activate the pipeline after its configuration is verified.

The machine-only skill install can happen earlier. The repo-level enforcement waits
until the seed is complete because retrieve blocking is correct after the baseline and
counterproductive during it.

---

## Where this sits in setup

| Order | Phase | Why here |
|---|---|---|
| 1 | Setup Phases 0–2d (scaffold, git, npm, PMD) | you need `sfdx-project.json` and a git repo before there is anywhere to put metadata |
| **2** | **Seed (this guide)** | **the repo is empty, so nothing can be clobbered, and the retrieve guards are not up yet** |
| 3 | Setup Phase 3 (enforcement stack) | the guards, including the retrieve block, come up over a repo that already matches the org |

**Seed before you install the enforcement stack, not after.** Phase 3 installs
`guard-sf-flags.sh`, the hook that blocks `sf project
retrieve` into the tree, because after seeding a retrieve can only do damage — it
silently reverts anything deployed but not yet pulled back, and it produces
changes with no ticket. Doing the seed first means you never have to argue with
a guard that is correct. If the stack is already installed, jump to
[Re-seeding after the guards are up](#re-seeding-after-the-guards-are-up).

If `force-app/` already has content and the org has drifted from it, this is not
a seed. That is a reconciliation, and it needs a ticket and a worktree like any
other change.

---

## The model: exclude by reason, not by list

The temptation is to copy someone's list of metadata types to skip. Lists rot,
and a list gives you nothing to reason with when you hit a type nobody wrote
down. Every exclusion below belongs to one of five classes, and the class is the
part worth learning.

| Class | Test | What it means for the repo |
|---|---|---|
| **Not authored** | a user made it by clicking, and will keep making more | tracking it turns every user's Tuesday into a diff |
| **Not portable** | it carries secrets or org-bound ids that a deploy cannot reproduce | it deploys as a broken shell, or not at all |
| **Not yours** | it belongs to an installed package | you cannot change it, and the package version already governs it |
| **Superseded** | the platform replaced it and retrieves it for compatibility | it is noise that looks like configuration |
| **Governed elsewhere** | this skill already has a mechanism for it | two mechanisms for one concern is how they disagree |

The last class is the one people get wrong, so it is worth being explicit:

**Profiles are excluded because this skill's permission model is one generated
permission set.** Not because profiles are bad. `gen-permset.py` derives object
permissions, field permissions, tabs, record types, apps and Apex class access
from the source tree, and two branches that each add fields converge the moment
it is regenerated. A retrieved `Admin.profile-meta.xml` is a second, hand-edited
answer to the same question — it conflicts on every parallel build, and it
carries FLS for fields that may not exist in the branch you are merging into.
Salesforce is also removing most profile-level permissions in Spring '26, so the
file shrinks toward irrelevance on its own. Keep the permission set generated,
leave profiles in the org, and there is nothing to reconcile. See
[tools/README.md](tools/README.md).

**External Client Apps and Connected Apps are excluded because they are not
portable.** The consumer key and secret do not come down in a retrieve, and the
OAuth policy blocks are org-scoped. What you get is a file that looks like a
Connected App, deploys without error, and produces an integration that cannot
authenticate — the worst failure shape there is, because it is silent. Create
these in the org's Setup and document their names in `CLAUDE.md`.

---

## Step 1 — Write `.forceignore` first

`.forceignore` is the durable half of this job. The manifest exclusions in Step 2
govern one retrieve; `.forceignore` governs every retrieve, every deploy, and
every `sf` command anyone runs for the rest of the project's life. Writing it
first means the guardrail exists before the thing it guards.

```bash
cp <SKILL_DIR>/references/templates/forceignore .forceignore
```

`<SKILL_DIR>` is the base directory of this skill, shown at the top of the skill
load message.

Open it and read it. Every line has a comment naming its reason class, and a few
are marked as judgment calls the project has to make (email templates and
standard object customization are the usual two). It is gitignore syntax,
relative to the project root, and it is **tracked** — like `CLAUDE.md` and the
hooks, an ignored `.forceignore` would not exist in any worktree.

One limit worth knowing: `.forceignore` filters what gets **written to disk**, not
what the org sends. A retrieve of 8,000 components still costs 8,000 components
of wait even if you keep 400 of them. That is what Step 2 is for.

## Step 2 — Generate the manifest from the org

```bash
sf project generate manifest --from-org <ORG_ALIAS> --name seed \
  --output-dir manifest \
  --excluded-metadata \
    Profile ProfilePasswordPolicy ProfileSessionSetting \
    ConnectedApp ExternalClientApplication \
    ExtlClntAppOauthSettings ExtlClntAppOauthConfigurablePolicies \
    ExtlClntAppGlobalOauthSettings ExtlClntAppOauthSecuritySettings \
    ExtlClntAppMobileSettings ExtlClntAppMobileConfigurablePolicies \
    ExtlClntAppPushSettings ExtlClntAppPushConfigurablePolicies \
    ExtlClntAppNotificationSettings ExtlClntAppCanvasSettings \
    ExtlClntAppSamlConfigurablePolicies \
    Report ReportFolder Dashboard DashboardFolder \
    Document DocumentFolder \
    Certificate SamlSsoConfig \
    InstalledPackage AppMenu FlowDefinition CleanDataService
```

Two things this command does for free, both of which used to be manual cleanup
passes:

- **Managed and unlocked package metadata is excluded by default.** That is the
  behaviour of `--from-org` without `--include-packages`. There is no
  after-the-fact namespace sweep to run, because the namespaced components were
  never in the manifest. Do not add `--include-packages` unless you have a
  specific reason and can name it.
- **The exclusions are applied at build time**, so the retrieve in Step 4 is
  smaller and faster, not just filtered on landing.

`--excluded-metadata` takes type names, never component names. If a type name
comes back rejected, it does not exist at your API version; check the spelling
against `sf org list metadata-types --json` rather than guessing.

**Deliberately not excluded here:** `EmailTemplate`, `ListView`,
`NamedCredential`, `CustomObject`, `CustomReportType`. The first two are judgment calls that depend
on whether your org authors them in Setup or in the repo. `NamedCredential`
retrieves usefully even though its secrets do not — the endpoint and auth
protocol are real configuration worth versioning, and the credential itself is
set once in the org. `CustomObject` has to come down; Step 3 is how you keep it
from bringing every standard object with it.

Reports and dashboards remain excluded initially, but custom report types stay in source.
If the company intentionally versions selected report or dashboard folders, replace the broad
folder exclusions with an explicit curated-folder policy after the baseline is stable.

## Step 3 — Prune the manifest

Open `manifest/seed.xml`. This is the sanitize step, and it is cheap precisely
because it happens here: one file with a few hundred lines, rather than several
thousand files on disk.

Read the `<types>` blocks top to bottom and apply the five classes. Then handle
the one type that always needs work:

**`CustomObject` arrives holding every standard object in the org.** Account,
Contact, Opportunity, and roughly two hundred you have never opened. Most are
untouched, and an untouched standard object in the repo is a lie about what the
project owns. The rule:

- **Keep** every member ending in `__c`.
- **Keep** standard objects you have actually customized.
- **Delete** the rest.

To find which standard objects have custom fields:

```bash
sf data query --use-tooling-api --json \
  -q "SELECT TableEnumOrId FROM CustomField" \
  | jq -r '.result.records[].TableEnumOrId' | sort -u
```

Entries that look like `Account` or `Opportunity` are standard objects with
custom fields — keep those. Entries that are 15-character ids (`01I...`) are
custom objects, already covered by the `__c` rule. Record types, validation
rules and page layouts also count as customization and will not show in that
query, so treat it as a floor rather than the whole answer, and keep anything
you are unsure about. A standard object kept unnecessarily is a Step 5 cleanup;
one dropped by mistake is a missing field.

Commit the pruned manifest. It is the record of what this project considers its
own, and the next person to ask "why isn't X in the repo?" should be able to
answer it from this file.

## Step 4 — Retrieve

```bash
sf project retrieve start --manifest manifest/seed.xml
```

Straight into `force-app/`, because the repo is empty and there is nothing to
clobber. That is the whole reason this step runs before the enforcement stack.
Expect several minutes on a mature org.

If the retrieve fails partway, it is safe to run again. Nothing is tracked yet.

## Step 5 — Prune the tree

The manifest controls which components come down. It cannot control what is
*inside* a component, and standard objects are the case where that matters:
retrieving `CustomObject: Account` brings every standard field on Account with
it. Those are platform-owned, they never change under you, and they make the
first `git add` unreadable.

**List before deleting.** Read the output; it is your last look before this
becomes tracked content.

```bash
# Standard fields inside standard objects — the deletion candidates.
find force-app -path '*/objects/*/fields/*.field-meta.xml' \
  ! -path '*/objects/*__c/*' ! -name '*__c.field-meta.xml' | sort
```

```bash
# Delete them once the list looks right.
find force-app -path '*/objects/*/fields/*.field-meta.xml' \
  ! -path '*/objects/*__c/*' ! -name '*__c.field-meta.xml' -delete
```

Then drop any standard object folder that has nothing left worth keeping — no
custom fields, no record types, no validation rules, no list views:

```bash
find force-app -path '*/objects/*' -maxdepth 4 -mindepth 1 -type d \
  ! -name '*__c' -print0 \
  | while IFS= read -r -d '' obj; do
      [ -n "$(find "$obj" -mindepth 1 -type f ! -name '*.object-meta.xml' -print -quit)" ] \
        || echo "$obj"
    done
```

Review that list, then remove the folders it names.

Two more passes worth doing by eye, because no pattern catches them reliably:

- **Managed-package fields on standard objects.** Namespaced fields look like
  `ns__Field__c` — two underscore pairs. They survive the `__c` rule above
  because they end in `__c`, but they are package-owned. `__` is reserved by the
  platform, so a name matching `*__*__c` is namespaced and not a false positive.
- **Empty files and folders.** Some types retrieve as a stub with no content.
  `find force-app -type f -empty` and `find force-app -type d -empty` find them.

## Step 6 — Review, and only then commit

This is the checkpoint. It is the one time in the project's life when a single
commit decides what the repo believes about the org, and it is worth the twenty
minutes.

```bash
git add -A
git status
git diff --cached --stat
```

Read the file list. For each top-level `objects/`, `classes/`, `flows/`,
`layouts/` group, you are answering one question: **does the project own this, or
does the org?** Anything the org owns is either an exclusion you missed in Step 3
or a `.forceignore` line you should add now. Adding it now costs one edit;
adding it in six months costs a deletion commit that reads like someone removed
working configuration.

Then prove the round trip. Direct delivery uses this as the initial `main === org`
test. DevOps Center uses it to prove that the production baseline on `main` is
deployable before any environment or pipeline is connected. A retrieve that
cannot be deployed back is a snapshot rather than a baseline:

```bash
sf project deploy start --dry-run \
  --source-dir force-app/main/default --test-level NoTestRun
```

`force-app/main/default` rather than `force-app`, because bare `force-app` is
blocked by `guard-sf-deploy.sh` once the stack is up and there is no reason to
write the command two different ways.

A clean dry run means the repo can reproduce the org. Failures here are normal
and each one is telling you something specific:

| Failure | What it means | Fix |
|---|---|---|
| references a component not in the repo | the manifest excluded a real dependency | add it to the manifest, retrieve just that type |
| references a managed-package component | the reference is real; the component belongs to the package | leave it, it resolves in the org |
| a field or object "does not exist" | Step 5 deleted something that was load-bearing | restore it from the retrieve |
| Connected App / Certificate errors | not portable, as designed | confirm it is excluded, keep it out |

Iterate until it is green or until every remaining failure is one you have
looked at and decided to accept. Write the accepted ones into `CLAUDE.md` —
"these N components live in the org and are not in the repo, for these reasons"
is exactly the note that stops the next agent from trying to fix it.

```bash
git commit -m "chore: seed force-app from <ORG_ALIAS> (baseline)"
git push
```

One commit. Not a series. This is the tree the whole project is diffed against,
and a bisect that lands in the middle of a nine-commit seed is nobody's good
afternoon.

## Step 7 — Hand off to the enforcement stack

Return to [init-guide.md](init-guide.md) Phase 3. The guards come up over a
repo that already matches the org, which is the state they are written to
preserve.

---

## Re-seeding after the guards are up

Sometimes the org has something the repo needs and nobody typed it into
`force-app/` — a flow built in the Setup UI during a demo, a field added under
deadline. That is a real situation and it deserves a real answer rather than
fighting the guard.

**It is not a second seed.** It is a change to the repo, and it goes through a
ticket and a worktree like every other change. The only difference is where the
content comes from.

A retrieve is blocked by **one** layer — `guard-sf-flags.sh`, this skill's PreToolUse hook —
and only in the **main** checkout. An earlier version also shipped a `permissions.deny` rule
in `settings.json`, but that was removed: a user-level deny fires in *every* repo on the
machine, which broke non-interference with unrelated projects. So blocking now lives only in
the gated hook, which honours the `ESTATE_/SOLO_ALLOW_RETRIEVE=1` hatch (recorded to the
hatch-log). The hatch is therefore a real bypass — use it only for the rare operation the
scratch-dir path genuinely cannot express. A retrieve run from a **linked worktree** is
allowed outright and needs no hatch: it can only clobber that branch's own files, and the PR
diff catches it before merge.

**The recommended path never needs the hatch.** Retrieve into a scratch tree,
outside `force-app/`, from a plain terminal:

```bash
# In your own terminal, not through the agent.
sf project retrieve start --metadata Flow:My_Flow --output-dir tmp-retrieve
```

`tmp-retrieve/` is already gitignored by the setup guide. Nothing in the tracked
tree can be touched by this, which is what makes it safe enough to do outside the
guards. Then, in a worktree, on a ticket, copy across the specific files you
meant to bring over, read them, and take them through the normal validate →
merge → deploy sequence in direct delivery. In DevOps Center delivery, use the
existing WI branch, validate, push, and create the DevOps Center review. DevOps
Center merges and promotes it through the configured stages.

**For the rare case the scratch-dir path cannot express**, `ESTATE_ALLOW_RETRIEVE=1`
(the `SOLO_` prefixes still work) lets one retrieve through and appends a line to
`.git/estate/hatch-log`. Like every hatch in this stack it does not block and does not
argue — it makes the override a decision on record instead of a silent one.

**Never `sf project retrieve start --source-dir force-app` in the main checkout.**
That overwrites the tracked tree with org state and silently reverts anything
deployed but not yet pulled back. There is no ticket, no diff you read on purpose,
and no way to tell afterwards what it undid. This is the command the guard exists
for. (Inside a linked worktree the same command is your own branch's to make — the
PR diff is the review it gets.)

---

## What good looks like

At the end of seeding:

- `.forceignore` is tracked, commented, and its lines match what you actually
  decided rather than what a template suggested
- `manifest/seed.xml` is tracked and readable as a statement of scope
- `force-app/` contains what the project owns and nothing the org owns
- a whole-tree dry run passes, or every failure is written down in `CLAUDE.md`
  with a reason
- there is one seed commit
- the enforcement stack is installed *after* all of the above

For direct delivery, this establishes `main === org` on day one. For DevOps Center,
it establishes an exact production baseline on `main`, with `staging` created from
that same commit before the environments and pipeline are connected.
