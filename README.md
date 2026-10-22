# Skills Estate

Private source of truth for Megan's reusable skills across Claude Code and Codex. Author each skill once in `skills/`. Branding belongs in [policies/brand.md](policies/brand.md); the build includes the current policy in every portable package.

The estate contains 76 skills: 50 neutral business and delivery workflows, 21 current personal and career skills, two project adapters, and three estate foundations. [CATALOG.md](CATALOG.md) lists their entrypoints. This repository contains instructions and selected supporting tools, not private career evidence, client records, licensed brand assets, or project databases.

## Install on a Mac or Linux machine

Python 3.9 or later and Git are required. Authenticate GitHub CLI as the intended account and clone the private repository:

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git --hostname github.com
gh repo clone mshellman-llc/Skills-Estate
cd Skills-Estate
python3 tools/estate.py build
python3 tools/estate.py bundle
python3 tools/estate.py install
git config core.hooksPath .githooks
```

`install` refuses existing conflicting entries before changing any skill. Inspect those entries, then use `python3 tools/estate.py adopt` for an intended migration. Adoption moves originals into `~/.local/state/skills-estate/backup-*/` and records a restore receipt. Keep those backups until the migration is accepted.

The installer links generated packages into `~/.claude/skills` and `~/.agents/skills`. Existing matching names under `~/.codex/skills` are reconciled as legacy aliases. It also creates `~/.config/skills-estate/repository` so either assistant can find the checkout. Keep the checkout at a stable path on an available volume. Start a fresh session when a host has cached its skill list.

## Change and sync skills

Edit `skills/<name>/SKILL.md` and its supporting resources. Edit shared rules only in `policies/`. Then run:

```sh
python3 tools/estate.py validate
python3 -m unittest discover -s tests -v
python3 tools/estate.py sync
python3 tools/estate.py status
```

`sync` validates, builds, packages, and installs managed links. Builds reject changes made while packaging, and installation rejects stale or edited generated files. Both local assistants read the same generated files. Do not edit `build/`, installed links, vendor caches, or `synced/` downloads as authoring sources.

With the repository hooks enabled, commit, merge, and checkout rebuild the local installation; pre-push runs validation and tests. Hooks do not fetch or push. On another machine, pull the reviewed changes and run `sync`. GitHub Actions validates every push and pull request and publishes the generated ZIPs as a workflow artifact.

To reverse an adoption:

```sh
python3 tools/estate.py restore /absolute/path/to/backup/receipt.json
```

Restore refuses if an installed destination has changed since that receipt. It restores the recorded local entries; it does not revert Git history or account uploads.

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

Use `codex-account` for that account surface. Records are reported upload state, not runtime proof. `status` shows pending packages after content changes and inventories other skill locations that may contain duplicates. There is no unattended account uploader in this repository.

## GitHub access for both assistants

The `github-repository-work` skill uses the shared `gh` login and Git credential helper. On the configured Mac, `gh` is at `~/.local/bin/gh` if the shell has not picked it up on PATH. Credentials belong in the operating system keychain. Never put a token in this repository or in a skill.

Verify account and repository access with `gh auth status` and `gh repo view OWNER/REPO --json nameWithOwner,viewerPermission,isPrivate`. Repository access permits authorized Git operations and GitHub workflows. Deployment services still need their own connection and environment permissions. Protected branches, environment approvals, and assistant approval controls continue to apply.

## Migration scope

[MIGRATION.md](MIGRATION.md) records what was retained, rebuilt, and left in the historical source estate. Existing source folders and account-managed copies are preserved. Reusable workflows were rewritten without the former employer's identity, brand, rates, contractual language, payment details, or customer fixtures. This is not feature parity with the former employer's bespoke rendering and integration engines.

This private repository has no blanket distribution license. Preserve included third-party notices and review provenance before redistributing a skill outside the owner's accounts.

## Interactive skills map

Open [the skills map](artifacts/skills-map/index.html) in a browser to search the estate, follow suggested workflows, and inspect each skill’s instructions and connections. [Build instructions](artifacts/skills-map/README.md) cover canonical and personal snapshots.
