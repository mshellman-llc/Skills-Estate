---
name: skill-estate-sync
description: "Maintain a Skills Estate checkout: author or repair a workflow, validate and package it, install a reviewed release, or replace a skill in another host or account. Select only the requested operation."
---

## Choose the requested task

Use the primary workflow below unless the request matches a mode in this table. For a matching mode, read its complete linked workflow and required references, then produce that mode's output. Preserve its calculations, failure handling and acceptance checks. One request does not require every mode.

| Requested mode | Complete workflow |
| --- | --- |
| create or repair an estate skill | [skill-creation-walkthrough](_runtime/skill-creation-walkthrough/WORKFLOW.md) |
| release to another host or account | [cross-platform-skill-release](_runtime/cross-platform-skill-release/WORKFLOW.md) |



# Skill estate sync

Keep one canonical Git checkout. Edit its `skills/`, `policies/`, and declared runtime dependencies; build complete portable packages from those sources. Claude Code and Codex use the same accepted versioned packages locally. Candidate builds and ZIPs remain separate from installed releases. A package includes the workflow, scripts, references, templates, and shared policies it needs.

Read [the skill standard](references/estate/skill-standard.md) before deciding whether a change is ready to install. A successful build checks packaging. It does not prove that a skill can perform its task.

## Choose the maintenance operation

- For an estate addition or behavioral repair, read [estate authoring](_runtime/skill-creation-walkthrough/WORKFLOW.md). It carries the governed intake and scaffolder; use the host's general authoring tools when available.
- For build, package, local installation, drift or rollback, follow the procedures below.
- For another host or account, read [cross-platform release](_runtime/cross-platform-skill-release/WORKFLOW.md). It preserves archive inspection, private-account replacement, ambiguous-upload recovery and destination invocation checks. Its generic method also supports sources outside this estate; do not require an estate checkout for that branch.

Read only the requested mode. A creation request does not authorize installation or account publication.

## Select the estate

Use the checkout already identified by the user or the installation's repository pointer. The bundled bridge resolves an explicit `--repo`, otherwise `~/.config/skills-estate/repository`. It refuses a missing pointer or a checkout without the expected tooling. It does not clone a repository, change accounts, or guess from the current directory.

Run from this skill's directory, replacing the example repository with the confirmed checkout:

```sh
python3 scripts/manage_estate.py --repo /path/to/Skills-Estate validate
python3 scripts/manage_estate.py --repo /path/to/Skills-Estate build
python3 scripts/manage_estate.py --repo /path/to/Skills-Estate bundle
python3 scripts/manage_estate.py --repo /path/to/Skills-Estate status
```

From the canonical checkout, the equivalent command is `python3 tools/estate.py <command>`. The bridge invokes that exact tool; it does not maintain a second packaging implementation. Python 3 and a writable canonical checkout are required. Status creates a local lock file and reads the build; it does not contact host services.

If no checkout is available, report the missing prerequisite and identify the user's existing repository. An isolated upload of this maintainer skill can inspect its own resources but cannot synchronize an estate that is absent from the host.

## Repair and verify before installing

1. Run `validate`. Fix malformed entry metadata, broken local links, missing declared runtime dependencies, or dependency cycles in source. Preserve working implementations when repairing instructions.
2. Run the changed skill's behavioral tests with representative inputs. Save the actual outputs, failures, and command receipts. Check generated prose and figures against the inputs, and inspect rendered artifacts. Use the checkout's `tools/run_preserved_test.py` for Python tests that create temporary files.
3. Run the estate's packaging and installation tests after changing shared policies, runtime assembly, or synchronization code. Shared changes can affect every dependent package.
4. Run `build`, then `bundle`. The builder copies the selected shared policies and transitive runtimes, preserves executable modes, and records source/package hashes. It rejects a source change during assembly. Bundle output is in `dist/`; use the release manifest's filenames instead of assuming an extension.
5. Confirm that the reviewed output belongs to the current source hash. Do not infer task quality from hashes, file counts, ZIP creation, or a structural selftest. A host invocation is separate evidence from local file installation.

The current canonical CLI does not automatically run every behavioral test before building. The agent must complete the applicable tests and content review before treating a build as ready. Preserve a skill's failed attempt and fix the capability; do not replace the workflow with a general description to make validation pass.

## Install and keep local hosts consistent

Before rebuilding a legacy checkout whose installed links point into `build/`, run `pin-installed`. It preserves only the existing managed inventory and exact bytes in a versioned directory; it does not promote new source or change vendor installations.

After the requested repairs, independent review, and release checks pass, use the exact reviewed source hash:

```sh
python3 scripts/manage_estate.py --repo /path/to/Skills-Estate install --expected-source REVIEWED_SOURCE_HASH
python3 scripts/manage_estate.py --repo /path/to/Skills-Estate status
```

Installation copies packages into a verified version under `~/.local/share/skills-estate/releases/` and links that version into `~/.claude/skills` and `~/.agents/skills`. Existing matching legacy entries in `~/.codex/skills` are reconciled as well. Unrelated installed skills remain separate. The repository pointer lets this skill find the same checkout from either host.

An existing divergent file, directory, or link is a conflict. Inspect its unique work first. If replacement is authorized, `adopt` backs it up and records a restore receipt before linking. A failed install rolls back its changes. Never discard a divergent installation to force a green status.

`restore /absolute/path/to/receipt.json` reverses a recorded install only if its destinations still match what the installer wrote. It refuses to overwrite a subsequent user change.

`sync` runs build and bundle only. It refreshes candidates without changing installed versions. Git commit, checkout, and merge hooks never install or rebuild. Everyday promotion requires the reviewed source hash and completed release gates. `rollback RELEASE_ID` can reactivate a previously installed version after checking its integrity and the current destinations. For a test run, put `--home /absolute/path/to/test-home` before the command. This changes the install destination and repository pointer; build output still belongs to the selected checkout.

Status inspects the current source, build, ZIP hashes, installed release, local links, and reported account uploads. It continues to inspect ZIPs when the build is stale. Local states include `linked-current`, `pinned-older`, `legacy-mutable`, drift, missing, and broken entries. Overall success requires current build and ZIPs plus matching managed installations. An older pinned installation remains usable but is not the current candidate. A copied package remains outside managed release ownership. Open the updated skill in a fresh host session when discovery requires a reload, then run a representative task there and retain its output. Do not claim Claude Code execution based on a Codex run, or the reverse.

To promote a reviewed task package without changing other installed skills, use `install --skill writing-integrity --expected-source REVIEWED_SOURCE_HASH`; repeat `--skill` to select more packages. The selected workflows, their runtime dependencies and shared assembly must pass the existing release gates. Other installed links keep their exact versions. Status verifies every retained release and reports a mixed installation without claiming one shared source hash. `rollback RELEASE_ID` restores the complete inventory from the most recent activation of that release ID; use its `restore` receipt to recover originals from an adoption. A conflicting older installation still needs explicit, scoped `adopt --skill NAME --expected-source REVIEWED_SOURCE_HASH` after inspecting its files.

## Shared brand and dependency changes

Edit the canonical brand policy/profile once. Rebuild dependent packages so their vendored policy copies and runtime assets match. Do not edit generated `build/`, `dist/`, or installed package files. Compare a neutral-profile output and an explicitly selected alternate profile when the change affects branding. Missing declared assets must produce an actionable failure rather than silently restoring former company branding.

Runtime relationships belong in `config/runtime-dependencies.json`. A router must carry the scripts and references needed by its declared dependencies when used alone. Test the assembled package away from sibling source directories to reveal accidental source-tree dependencies.

## Account uploads and other surfaces

Local installation does not upload to Claude's account, a Codex account, Cowork, ChatGPT, or an API deployment. Check the destination's current supported format and available authorized upload method. Do not assume every surface accepts the same ZIP or provides a skill registry.

After an actual authorized account upload, record the specific skill and destination reference:

```sh
python3 scripts/manage_estate.py --repo /path/to/Skills-Estate record-publication \
  --surface claude-account --skill knowledge-hub --reference 'account and upload record'
```

The canonical ledger accepts `claude-account`, `codex-account`, `cowork`, and `chatgpt-personal`. A ledger row remains `verified_live: false`: it records the reported upload hash, not a readback or execution. Retain a separate receipt for a destination readback or task invocation. For another destination, retain its actual receipt and extend the adapter explicitly before claiming managed synchronization.

## Retained standalone audit tools

The earlier flat-estate tools remain bundled for explicit compatibility work. They are not the canonical release path:

- `scripts/estate_diff.py --source DIR --config FILE --json` compares a flat skills tree to configured local directories. It distinguishes missing skills, SKILL-only stubs, entrypoint drift, and resource drift; each fails the comparison. It also checks the older `_shared/build-card.md` contract, shared references, and declared prose exemptions. Use it on a tree following that contract, not as a substitute for canonical status.
- `scripts/build_bundles.py --source DIR --out DIR` gates flat-tree bundles on each skill's `*_selftest.py`, carries transitive shared resources, and preserves the original runtime-vendoring mechanism. Its optional release classification filters drafts. `--no-gate` is a diagnostic bypass and is not release evidence. It does not use the canonical dependency graph or manifests.
- `scripts/record_publish.py` retains the flat-tree publication-ledger format. The bundled ledger starts empty; old organization uploads are not evidence for this estate. Its configuration must match the intended standalone checkout before writing a record.
- `scripts/sync_build_card.py --skills-root DIR --check` checks the older shared-card/runtime references without generating brand literals.
- `scripts/estate_sync_selftest.py` exercises those compatibility functions with synthetic fixtures. It does not connect to a host or cloud account.

Use [the optional pre-commit hook](references/pre-commit.sh) only after inspecting existing hooks. It validates the canonical source without staging generated files. A hook is not installed or a recurring check scheduled merely because this file describes one.

## Completion record

State which source revision changed, which tasks produced usable outputs, which packages were built, and which destinations were actually updated. Link the outputs and installation or publication receipts. Name any remaining capability or host test and its next action. A missing service does not justify labeling that service's behavior verified; provide a working local path when the task supports one.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
