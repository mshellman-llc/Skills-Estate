---
name: skill-estate-sync
description: Validate, build, package, install, and audit the canonical Skills Estate across Claude Code and Codex. Use for skill changes, local drift, release bundles, and account upload tracking.
---

# Skill estate sync

The canonical repository is `mshellman-llc/Skills-Estate`. Locate the checkout from the current project or `~/.config/skills-estate/repository`. Verify that location and its remote before running commands. A hosted session without the checkout can prepare a change but cannot claim a local installation.

Author in `skills/`; shared branding lives in `policies/brand.md`. Run commands from the checkout:

```sh
python3 tools/estate.py validate
python3 -m unittest discover -s tests -v
python3 tools/estate.py sync
```

The build vendors the current shared policies into each package. Local installs link the generated packages into `~/.claude/skills` and `~/.agents/skills`. `sync` rebuilds, packages, and installs missing managed links. It does not fetch, push, upload, or overwrite a conflicting skill.

Run `status` to inspect current local bytes and pending account packages. Existing conflicts need inspection. `adopt` moves existing entries to a timestamped backup before linking; use it only for an authorized, reviewed migration. `restore <receipt.json>` restores the recorded entries and refuses if a destination changed since installation. Never edit `synced/`, vendor plugin caches, or unrelated skills.

For GitHub updates, inspect the diff, commit, push through the authenticated GitHub CLI, and verify the remote commit and CI. Repository hooks rebuild local packages after commit, checkout, and merge. Another machine needs its own authenticated clone and installation.

Claude account uploads and Codex account/plugin distribution are separate from local installation. `dist/` contains individual ZIP packages and `release.json` with their hashes. Use the actual account interface to upload and test a package; record an upload only after it occurred:

```sh
python3 tools/estate.py record-publication --surface claude-account --skill NAME --reference 'account and upload record'
```

A publication record is reported state, never independent verification. A changed package returns to pending. Account-enabled Claude skills reach Cowork according to the host's sync behavior; local Claude Code folders do not establish Cowork installation. Do not claim all surfaces are current while any required account or runtime check remains pending.
