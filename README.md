# Skills Estate

Reusable workflows for Claude Code and Codex. Author each skill once in `skills/`. Branding belongs in [policies/brand.md](policies/brand.md); the build includes the current policy in every portable package.

The catalog contains 91 source modules and 63 task entrypoints. It separates task entrypoints from supporting runtime modules. [CATALOG.md](CATALOG.md) lists their current names and relationships. Supply private project records and credentials through the configured task inputs.


<!-- SKILL-GROUPS:BEGIN -->
## Browse by work

| Group | Source workflows | Task packages |
| --- | ---: | ---: |
| [Pursuit and discovery](browse/pursuit-and-discovery/README.md) | 7 | 5 |
| [Scope and proposals](browse/scope-and-proposals/README.md) | 14 | 9 |
| [Delivery and project work](browse/delivery-and-salesforce/README.md) | 15 | 13 |
| [Salesforce development](browse/salesforce-development/README.md) | 8 | 5 |
| [Product and experience](browse/product-and-experience/README.md) | 14 | 13 |
| [Knowledge and context](browse/knowledge-and-context/README.md) | 9 | 6 |
| [Writing and presentation](browse/writing-and-presentation/README.md) | 9 | 5 |
| [Career and applications](browse/career-and-personal/README.md) | 5 | 3 |
| [Personal and creative](browse/personal-and-creative/README.md) | 3 | 3 |
| [Estate and engineering controls](browse/estate-and-engineering-controls/README.md) | 7 | 3 |
<!-- SKILL-GROUPS:END -->

## Use the skills

The skills reach every app as plugins from this repository's marketplace. After a change reaches `main` and passes automated verification, GitHub rebuilds the plugin folders under `plugins/`, which `.claude-plugin/marketplace.json` lists, and attaches the plugin ZIPs to the [Plugins (latest)](https://github.com/mshellman-llc/Skills-Estate/releases/tag/plugins-latest) release. Publication starts when that verification finishes, and a daily run retries anything an event missed. It refuses to publish stale or failing source. Do not edit `plugins/`; it is generated.

- Cowork and claude.ai: Customize, Plugins, Add, Add marketplace, `mshellman-llc/Skills-Estate`, with automatic sync on.
- Claude Code: `/plugin marketplace add mshellman-llc/Skills-Estate`, install the `estate-` plugins you need. Salesforce development is `estate-salesforce`; career and applications are `estate-career`; stickers and game planning are `estate-personal`. Turn on auto-update for the marketplace in `/plugin`.
- Codex on the Mac: run `python3 ~/.agents/skills/maintain-skills-estate/scripts/manage_estate.py update` from this folder. It fetches GitHub `main` into a clean temporary checkout, requires that exact revision to pass GitHub verification, runs the existing local checks, and builds with the fetched tooling. It then updates Codex through the versioned release store and backs up duplicate local Claude skills in the same recoverable transaction. Your open branch, staged edits and untracked files stay in place. Claude continues to use its marketplace plugins; this command does not rewrite Claude’s plugin cache.

Update receipts under `~/.local/state/skills-estate/update-*/` identify the fetched commit, verified Actions run, local tests, previous release and restore receipt. A failed preparation leaves installations unchanged. A failed activation restores its prior state; a detected concurrent edit is preserved with its recovery journal. The repository pointer always names the durable authoring checkout.

To run a merged updater repair without changing an older authoring branch, use `python3 /path/to/clean-checkout/tools/estate.py update --repository /path/to/canonical-checkout`. The clean checkout supplies the updater code; releases and the repository pointer retain the canonical identity.

For local development, run `python3 tools/estate.py test-local`. It checks the working tree and builds committed `HEAD` candidates without installing. Commit reviewed source and the version record before building. Ordinary `update` always selects GitHub main.

Merged pull request branches are deleted automatically.

## Change skills

Edit `skills/<name>/SKILL.md` and its supporting resources. Edit shared rules only in `policies/`. Before opening a pull request, run:

```sh
python3 tools/verify.py --refresh
python3 tools/estate.py sync
```

`tools/verify.py` runs CI's checks in CI's order with CI's Node settings: browse pages, validation, the plugin version record and the test suite. `--refresh` first rebuilds the skills map, the reuse review and the browse pages. A failed step prints its output and the next command to run. Every `skills/*/scripts/*_selftest.py` runs as part of the suite without a hand-written test.

Builds and plugin candidates read a clean snapshot of `HEAD`. Commit the reviewed source, version record and generated source pages before running `sync` or creating plugin candidates. Local edits, staged changes, ignored files and untracked folders are excluded without being moved or inspected. Manifests record the commit and content hash. Packaging code must match the commit; commit tooling edits before generating packages. `validate` and the test runner still check working files during development.

`build/`, `dist/` and `.local/` are generated and ignored by Git. Do not edit them, installed links, or `synced/` account downloads as sources.

The runner lists deferred browser, loopback, generated-map and skill-toolchain checks explicitly. The skill-toolchain checks need `jq` and `python-pptx`. CI runs `--all-integrations`; a local pass with deferred checks is not full release acceptance. Use a supported browser environment and preserve the browser launch guards.

Before generating changed plugins, increase `version` in `config/plugin-bundles.json`, then run `python3 tools/plugin_version.py --record 'Describe the changes'` and `python3 tools/plugins.py --candidate`. The version history binds source, dependencies, routing, and assembly to one version and refuses stale builds or reuse of a version for changed content. Follow the [existing add/update/release workflow](skills/maintain-skills-estate/references/release-workflow.md) for review and publication. Candidate creation does not install or publish.

Supply personal profiles, client facts, contract policies, accounts, and learning stores as explicit external inputs. The portable workflows do not select a personal context store automatically. `config/retired-entrypoints.json` prevents the 15 internal workflow modes and writing diagnostics from returning through normal builds and activation. Their resources are bundled with the public workflows that own them.

## If something breaks

- A plugin did not update: run the "Publish plugin marketplace" workflow from the Actions tab, or wait for the daily run.
- The app cannot add the marketplace: download the ZIPs from the Plugins (latest) release and use Customize, Plugins, Add, Upload plugin.
- A local install needs undoing: `python3 tools/estate.py rollback RELEASE_ID` restores an earlier version, and `python3 tools/estate.py restore RECEIPT` returns originals moved during an adoption. Release IDs and receipts are under `~/.local/state/skills-estate/`. `python3 tools/estate.py --help` lists the remaining maintenance commands.

## Select a brand once

Use the profile the user explicitly names, otherwise the current project's `brand.md`, otherwise the neutral profile in `policies/brand.md`. Project profiles use the documented JSON structure. They stay with their project. The neutral profile uses system fonts and has no logo. `tools/brand.py` validates a profile and can produce CSS variables; a renderer still needs to apply those values and the result needs visual review.

No skill needs its own color palette, logo, or font list. The build includes a snapshot at `references/estate/brand.md` for hosts that cannot read another skill's files. A policy change therefore changes package hashes and marks earlier account uploads pending.

## GitHub access for both assistants

The `work-in-github-repository` skill uses the shared `gh` login and Git credential helper. On the configured Mac, `gh` is at `~/.local/bin/gh` if the shell has not picked it up on PATH. Credentials belong in the operating system keychain. Never put a token in this repository or in a skill.

Verify account and repository access with `gh auth status` and `gh repo view OWNER/REPO --json nameWithOwner,viewerPermission,isPrivate`. Repository access permits authorized Git operations and GitHub workflows. Deployment services still need their own connection and environment permissions. Protected branches, environment approvals, and assistant approval controls continue to apply.

## Source and notices

Author skills and supporting resources here. Keep client data, account configuration and private working records outside the repository. Preserve bundled licenses and notices when copying a workflow. This private repository has no blanket distribution license.

## Interactive skills map

The [portable explorer](artifacts/skills-map/README.md) includes inline skill details, a local show/hide manager, separate Skills Estate and portfolio exports, and a reusable browser component. The [integration guide](artifacts/skills-map/INTEGRATION.md) explains how to add it to a future site without choosing a framework now.

Open the [Skills Estate site](https://megan-skills-estate.livelaughcod-8893.chatgpt.site) to browse workflows, sort by name, and copy group links. Ask Codex to refresh the site from GitHub when needed. The [browse pages](browse/README.md) use the same ten groups; GitHub also builds their shareable collections.
