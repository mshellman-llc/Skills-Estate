# Skills Estate release adapter

Use this adapter when the maintained source is Skills Estate. Resolve the checkout from the current project or `~/.config/skills-estate/repository`; verify its remote and read its `AGENTS.md` and README. Author in `skills/<name>/`. Shared policies belong in `policies/`; generated packages and installed copies are release outputs.

The `skill-estate-sync` workflow owns the estate's build, installation, adoption, and publication-record mechanics. This adapter supplies the commands needed when that skill is unavailable. Inspect the current tool help before relying on flags from an older release.

## Validate and package

Run from the checkout or an isolated snapshot containing the required source and build inputs:

```sh
python3 tools/estate.py validate
python3 -m unittest discover -s tests -v
python3 tools/estate.py build
python3 tools/estate.py bundle
```

Read the results before continuing. The build incorporates catalog entrypoints, shared policies, and declared runtime dependencies. Inspect `build/skills/<name>/`, `dist/<name>.zip`, and the matching entry in `dist/release.json`. Compare the ZIP's SHA-256 with that entry, then inspect the extracted files. Generated policy and runtime files belong in the comparison even when absent from the authored skill folder.

Validation and candidate builds operate across the catalog. Before rebuilding a legacy installation linked into `build/`, use `pin-installed` to preserve its existing bytes and inventory in a verified versioned directory. Builds refuse to overwrite packages still serving those links. Use an isolated snapshot when another worker is editing the source; a build rejects source changes during assembly. Use the repeatable `--skill` option on `install` or `adopt` for targeted promotion; it does not narrow candidate builds. Keep the existing catalog entries when registering a new skill.

## Install and inspect locally

Refresh candidate packages after validation and tests:

```sh
python3 tools/estate.py sync
python3 tools/estate.py status
```

`sync` builds and bundles only; it leaves installed releases unchanged. Everyday installation is a separate `install --expected-source REVIEWED_SOURCE_HASH` after the required release reviews. `rollback RELEASE_ID` restores a previously activated version after verifying its bytes and current destinations. Git commit, merge, and checkout hooks do not build or install.

Local destinations normally include `~/.agents/skills` for Codex and `~/.claude/skills` for Claude Code. Verify the current installer and resolve the actual paths. A legacy `~/.codex/skills` entry may coexist; inspect it before making another copy. Installed links should resolve to a version under `~/.local/share/skills-estate/releases/`. Compare package bytes and the source, build, and ZIP states reported by `status`; an older pinned version remains usable but is not the current candidate.

`install` refuses conflicting entries. Inspect a conflict and use `adopt` only for an authorized migration; it keeps backups and a restore receipt. `restore <receipt.json>` is conditional on the destination remaining unchanged. Avoid broad adoption to fix one skill. Preserve `synced/` and platform-managed plugin directories.

To promote a reviewed task package without changing other installed skills, use `install --skill writing-integrity --expected-source REVIEWED_SOURCE_HASH`; repeat `--skill` to select more packages. The selected workflows, their runtime dependencies and shared assembly must pass the existing release gates. Other installed links keep their exact versions. Status verifies every retained release and reports a mixed installation without claiming one shared source hash. `rollback RELEASE_ID` restores the complete inventory from the most recent activation of that release ID; use its `restore` receipt to recover originals from an adoption. A conflicting older installation still needs explicit, scoped `adopt --skill NAME --expected-source REVIEWED_SOURCE_HASH` after inspecting its files.

## Record account replacement

Use the requested account interface to upload the reviewed ZIP and inspect it as described in the main workflow. Record the matching package only after the account replacement succeeds:

```sh
python3 tools/estate.py record-publication --surface claude-account --skill SKILL_NAME --reference 'Account, observed version, date, and upload evidence'
```

Use `codex-account`, `cowork`, or `chatgpt-personal` only for the corresponding destination. Check that `dist/release.json` still identifies the uploaded hash before recording it. The command records reported upload state; retain the separate host invocation result in the release record. A changed package requires a new comparison and, where requested, a new upload.
