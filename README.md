# Skills Estate

Private source of truth for Megan's reusable skills across Claude Code and Codex. Author each skill once in `skills/`. Branding belongs in [policies/brand.md](policies/brand.md); the build includes the current policy in every portable package.

The restoration candidate contains 90 source modules and 62 proposed task entrypoints. [CATALOG.md](CATALOG.md) records both inventories. Capability review and host verification remain open; this branch is not an accepted release. Private project records and credentials stay outside the repository.


<!-- SKILL-GROUPS:BEGIN -->
## Browse by work

| Group | Source workflows | Task packages |
| --- | ---: | ---: |
| [Pursuit and discovery](browse/pursuit-and-discovery/README.md) | 7 | 5 |
| [Scope and proposals](browse/scope-and-proposals/README.md) | 14 | 9 |
| [Delivery and Salesforce](browse/delivery-and-salesforce/README.md) | 23 | 18 |
| [Product and experience](browse/product-and-experience/README.md) | 13 | 12 |
| [Knowledge and context](browse/knowledge-and-context/README.md) | 9 | 6 |
| [Writing and presentation](browse/writing-and-presentation/README.md) | 9 | 5 |
| [Career and personal](browse/career-and-personal/README.md) | 8 | 6 |
| [Estate and engineering controls](browse/estate-and-engineering-controls/README.md) | 7 | 3 |
<!-- SKILL-GROUPS:END -->

## Use the skills

The skills reach every app as plugins from this repository's marketplace. After a change reaches `main` and passes automated verification, GitHub rebuilds the plugin folders under `plugins/`, which `.claude-plugin/marketplace.json` lists, and attaches the plugin ZIPs to the [Plugins (latest)](https://github.com/mshellman-llc/Skills-Estate/releases/tag/plugins-latest) release. Publication starts when that verification finishes, and a daily run retries anything an event missed. It refuses to publish stale or failing source. Do not edit `plugins/`; it is generated.

- Cowork and claude.ai: Customize, Plugins, Add, Add marketplace, `mshellman-llc/Skills-Estate`, with automatic sync on.
- Claude Code: `/plugin marketplace add mshellman-llc/Skills-Estate`, install the eight `estate-` domain plugins (add `estate-personal` for the career and personal workflows), and turn on auto-update for the marketplace in `/plugin`.
- Codex on the Mac: run `python3 tools/estate.py update` from this folder. It pulls `main`, links every public skill for Codex, and moves other copies of those skills out of `~/.claude/skills` into a dated backup under `~/.local/state/skills-estate/`.

Merged pull request branches are deleted automatically.

## Change skills

Edit `skills/<name>/SKILL.md` and its supporting resources. Edit shared rules only in `policies/`. Before opening a pull request, run:

```sh
python3 tools/verify.py --refresh
python3 tools/estate.py sync
```

`tools/verify.py` runs CI's checks in CI's order with CI's Node settings: browse pages, validation, the plugin version record and the test suite. `--refresh` first rebuilds the skills map, the reuse review and the browse pages. A failed step prints its output and the next command to run. Every `skills/*/scripts/*_selftest.py` runs as part of the suite without a hand-written test.

`build/`, `dist/` and `.local/` are generated and ignored by Git. Do not edit them, installed links, or `synced/` account downloads as sources.

The runner lists deferred browser, loopback, generated-map and skill-toolchain checks explicitly. The skill-toolchain checks need `jq` and `python-pptx`. CI runs `--all-integrations`; a local pass with deferred checks is not full release acceptance. Use a supported browser environment and preserve the browser launch guards.

Before generating changed plugins, increase `version` in `config/plugin-bundles.json`, then run `python3 tools/plugin_version.py --record 'Describe the changes'` and `python3 tools/plugins.py --candidate`. The version history binds source, dependencies, routing, and assembly to one version and refuses stale builds or reuse of a version for changed content. Follow the [existing add/update/release workflow](skills/skill-estate-sync/references/release-workflow.md) for review and publication. Candidate creation does not install or publish.

Supply personal profiles, client facts, contract policies, accounts, and learning stores as explicit external inputs. The portable workflows do not select a personal context store automatically. `config/retired-entrypoints.json` prevents the 15 removed predecessors and standalone Prose Pass from returning through normal builds and activation. Their required internal methods remain with their successors; Explorer remains available under the later keep decision.

## If something breaks

- A plugin did not update: run the "Publish plugin marketplace" workflow from the Actions tab, or wait for the daily run.
- The app cannot add the marketplace: download the ZIPs from the Plugins (latest) release and use Customize, Plugins, Add, Upload plugin.
- A local install needs undoing: `python3 tools/estate.py rollback RELEASE_ID` restores an earlier version, and `python3 tools/estate.py restore RECEIPT` returns originals moved during an adoption. Release IDs and receipts are under `~/.local/state/skills-estate/`. `python3 tools/estate.py --help` lists the remaining maintenance commands.

## Select a brand once

Use the profile the user explicitly names, otherwise the current project's `brand.md`, otherwise the neutral profile in `policies/brand.md`. Project profiles use the documented JSON structure. They stay with their project. The neutral profile uses system fonts and has no logo. `tools/brand.py` validates a profile and can produce CSS variables; a renderer still needs to apply those values and the result needs visual review.

No skill needs its own color palette, logo, or font list. The build includes a snapshot at `references/estate/brand.md` for hosts that cannot read another skill's files. A policy change therefore changes package hashes and marks earlier account uploads pending.

## GitHub access for both assistants

The `github-repository-work` skill uses the shared `gh` login and Git credential helper. On the configured Mac, `gh` is at `~/.local/bin/gh` if the shell has not picked it up on PATH. Credentials belong in the operating system keychain. Never put a token in this repository or in a skill.

Verify account and repository access with `gh auth status` and `gh repo view OWNER/REPO --json nameWithOwner,viewerPermission,isPrivate`. Repository access permits authorized Git operations and GitHub workflows. Deployment services still need their own connection and environment permissions. Protected branches, environment approvals, and assistant approval controls continue to apply.

## Migration scope

[MIGRATION.md](MIGRATION.md) records what was retained, rebuilt, and left in the historical source estate. Existing source folders and account-managed copies are preserved. Reusable workflows were rewritten without the former employer's identity, brand, rates, contractual language, payment details, or customer fixtures. The restoration preserves implementation resources for capability review; parity has not yet been accepted.

This private repository has no blanket distribution license. Preserve included third-party notices and review provenance before redistributing a skill outside the owner's accounts.

## Interactive skills map

Open the [Skills Estate site](https://megan-skills-estate.livelaughcod-8893.chatgpt.site) to browse workflows, sort by name, and copy group links. Ask Codex to refresh the site from GitHub when needed. The [browse pages](browse/README.md) use the same eight groups; GitHub also builds their shareable collections.
