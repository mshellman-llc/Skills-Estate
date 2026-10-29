# Skills Estate

Private source of truth for Megan's reusable skills across Claude Code and Codex. Author each skill once in `skills/`. Branding belongs in [policies/brand.md](policies/brand.md); the build includes the current policy in every portable package.

The restoration candidate contains 80 source modules and 52 proposed task entrypoints. [CATALOG.md](CATALOG.md) records both inventories. Capability review and host verification remain open; this branch is not an accepted release. Private project records and credentials stay outside the repository.


<!-- SKILL-GROUPS:BEGIN -->
## Browse by work

| Group | Source workflows | Task packages |
| --- | ---: | ---: |
| [Pursuit and discovery](browse/pursuit-and-discovery/README.md) | 7 | 4 |
| [Scope and proposals](browse/scope-and-proposals/README.md) | 14 | 9 |
| [Delivery and Salesforce](browse/delivery-and-salesforce/README.md) | 16 | 12 |
| [Product and experience](browse/product-and-experience/README.md) | 11 | 10 |
| [Knowledge and context](browse/knowledge-and-context/README.md) | 9 | 6 |
| [Writing and presentation](browse/writing-and-presentation/README.md) | 8 | 4 |
| [Career and personal](browse/career-and-personal/README.md) | 8 | 6 |
| [Estate and engineering controls](browse/estate-and-engineering-controls/README.md) | 7 | 3 |
<!-- SKILL-GROUPS:END -->

## Prepare and install on a Mac or Linux machine

Python 3.9 or later and Git are required. Authenticate GitHub CLI as the intended account and clone the private repository:

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
gh repo clone mshellman-llc/Skills-Estate
cd Skills-Estate
python3 tools/estate.py build
python3 tools/estate.py bundle
python3 tools/estate.py --home /absolute/path/to/isolated-home install
git config core.hooksPath .githooks
```

The example installs a candidate into an isolated home. Everyday installation requires completed release gates and `install --expected-source REVIEWED_SOURCE_HASH`, where the hash comes from the reviewed build manifest. This restoration candidate has open review gates.

`install` refuses existing conflicting entries before changing any skill. Inspect those entries, then use `python3 tools/estate.py adopt` for an intended migration. Adoption moves originals into `~/.local/state/skills-estate/backup-*/` and records a restore receipt. Keep those backups until the migration is accepted.

The installer copies packages into a verified, versioned directory under `~/.local/share/skills-estate/releases/` and links that version into `~/.claude/skills` and `~/.agents/skills`. Existing matching names under `~/.codex/skills` are reconciled as legacy aliases. It also creates `~/.config/skills-estate/repository` so either assistant can find the checkout. Installed files remain available when the source volume is unavailable. Keep the repository pointer valid for maintenance. Start a fresh session when a host has cached its skill list.

To promote a reviewed task package without changing other installed skills, use `install --skill writing-integrity --expected-source REVIEWED_SOURCE_HASH`; repeat `--skill` to select more packages. The selected workflows, their runtime dependencies and shared assembly must pass the existing release gates. Other installed links keep their exact versions. Status verifies every retained release and reports a mixed installation without claiming one shared source hash. `rollback RELEASE_ID` restores the complete inventory from the most recent activation of that release ID; use its `restore` receipt to recover originals from an adoption. A conflicting older installation still needs explicit, scoped `adopt --skill NAME --expected-source REVIEWED_SOURCE_HASH` after inspecting its files.

## Change and sync skills

Edit `skills/<name>/SKILL.md` and its supporting resources. Edit shared rules only in `policies/`. Then run:

```sh
python3 tools/estate.py validate
python3 -m unittest discover -s tests -v
python3 tools/estate.py sync
python3 tools/estate.py status
```

`sync` validates, builds, and packages candidates; it leaves installed releases unchanged. Builds reject source changes during assembly. Installation rejects stale or edited generated files. Both local assistants link to the same verified version of each promoted package. `status` reports source, build, ZIP, and installed drift separately, even when the build is stale. A green build does not establish a current ZIP or installation. Do not edit `build/`, installed links, vendor caches, or `synced/` downloads as authoring sources.

Commit, merge, and checkout hooks do not build or install. Pre-push runs validation and tests. On another machine, pull the reviewed changes and run `sync`, review the resulting source hash, then explicitly install the accepted release. GitHub Actions validates every push and pull request and publishes the generated ZIPs as a workflow artifact.

For an existing installation linked into `build/`, first run `python3 tools/estate.py pin-installed`. This preserves its current inventory and bytes in a versioned directory, without accepting new source. Builds refuse to overwrite a directory still serving everyday host links. Vendor and account-managed installations are excluded.

To return to a previously activated version, run `python3 tools/estate.py rollback RELEASE_ID`. Release IDs and backup receipts are under `~/.local/state/skills-estate/`. No automatic retention deletes the only rollback copy. Review obsolete releases before removing them.

To reverse an adoption:

```sh
python3 tools/estate.py restore /absolute/path/to/backup/receipt.json
```

Restore refuses if an installed destination has changed since that receipt. A migration receipt also refuses to restore legacy links after their mutable build has changed; keep the pinned version instead. Interrupted activation plans remain beside the backup originals for recovery; an unfinished plan is not an activated release. It restores the recorded local entries; it does not revert Git history or account uploads.

## Select a brand once

Use the profile the user explicitly names, otherwise the current project's `brand.md`, otherwise the neutral profile in `policies/brand.md`. Project profiles use the documented JSON structure. They stay with their project. The neutral profile uses system fonts and has no logo. `tools/brand.py` validates a profile and can produce CSS variables; a renderer still needs to apply those values and the result needs visual review.

No skill needs its own color palette, logo, or font list. The build includes a snapshot at `references/estate/brand.md` for hosts that cannot read another skill's files. A policy change therefore changes package hashes and marks earlier account uploads pending.

## Account and web skills

Local installation covers Claude Code and Codex on this machine. Claude account uploads, Cowork discovery, Codex account skills, and hosted execution are separate surfaces. Local symlinks do not verify any of those surfaces.

`dist/` contains one self-contained ZIP per skill and `release.json` with package hashes. Upload the chosen ZIPs through the account's supported skill interface. Inspect existing names before replacing them. Test discovery and an actual invocation in that host. Claude account downloads and platform-managed plugins remain outside this installer's ownership.

After an upload actually succeeds, record its evidence:

```sh
python3 tools/estate.py record-publication --surface claude-account --skill client-brand --reference 'Account, date, and upload result'
```

The other ledger destinations are `codex-account`, `cowork`, and `chatgpt-personal`. Records are reported upload state, not runtime proof. `status` shows pending packages after content changes and inventories other skill locations that may contain duplicates. There is no unattended account uploader in this repository.

## GitHub access for both assistants

The `github-repository-work` skill uses the shared `gh` login and Git credential helper. On the configured Mac, `gh` is at `~/.local/bin/gh` if the shell has not picked it up on PATH. Credentials belong in the operating system keychain. Never put a token in this repository or in a skill.

Verify account and repository access with `gh auth status` and `gh repo view OWNER/REPO --json nameWithOwner,viewerPermission,isPrivate`. Repository access permits authorized Git operations and GitHub workflows. Deployment services still need their own connection and environment permissions. Protected branches, environment approvals, and assistant approval controls continue to apply.

## Migration scope

[MIGRATION.md](MIGRATION.md) records what was retained, rebuilt, and left in the historical source estate. Existing source folders and account-managed copies are preserved. Reusable workflows were rewritten without the former employer's identity, brand, rates, contractual language, payment details, or customer fixtures. The restoration preserves implementation resources for capability review; parity has not yet been accepted.

This private repository has no blanket distribution license. Preserve included third-party notices and review provenance before redistributing a skill outside the owner's accounts.

## Interactive skills map

Open the [Skills Estate site](https://megan-skills-estate.livelaughcod-8893.chatgpt.site) to browse workflows, sort by name, and copy group links. Ask Codex to refresh the site from GitHub when needed. The [browse pages](browse/README.md) use the same eight groups; GitHub also builds their shareable collections.
