---
name: release-skill-package
description: "Package, replace, and inspect a shared skill across Codex and Claude. Use when preparing a portable release, replacing an account skill, or checking that both hosts received the intended files."
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.


# Release skill package

Release one shared skill from its maintained source and verify each requested destination. Carry its instructions, references, scripts, templates, assets, and runtime dependencies together.

Use this workflow for a release spanning local installations and account interfaces. For an estate-wide build or installation repair, use the repository's existing sync tools. Creating a new skill's behavior belongs in the skill creation workflow; changing global instructions or publishing a plugin requires its own scope.

## Identify the release

Resolve the skill name, source folder, intended change, and requested destinations from the task and current project guidance. Distinguish local Codex, local Claude Code, a Claude account, Cowork, and organization distribution. Record only the destinations the user requested. Reuse existing authorization; prepare the package before asking for any missing upload or publication approval.

Inspect the source revision and working tree, the installed paths, and any existing package. Preserve unrelated edits. Compare a downloaded or account-exported copy with the maintained source before choosing which bytes to release. A newer filename or host version does not establish source authority. For Skills Estate, read [the estate adapter](references/estate-release.md).

Before a replacement, retain the previous package or available host version and record how to recover it. Inventory the files and the capabilities they support. Explain intentional removals; resolve unexpected missing resources before proceeding.

## Build and inspect the package

Use the project's existing packager. Build from a stable source snapshot so concurrent edits cannot enter the archive unnoticed. If the build would update unrelated installed skills, stage an isolated build or use a supported targeted operation.

1. Validate the skill name, description, host metadata, and archive layout against the intended host's current requirements. Use its current interface or official documentation when a constraint is uncertain. Keep one discoverable top-level `SKILL.md`; retain supporting workflows under their intended paths.
2. Inspect the archive member list and extract it into an empty temporary directory. Check archive integrity, relative references, executable resources, and runtime dependencies. A reference to a Mac-only path needs an available host equivalent or an explicit fallback. Exclude private logs, credentials, caches, and unrelated source material.
3. Compare the extracted tree with the intended built package, including file bytes and relevant executable permissions. Record the archive's SHA-256, source revision or dirty-source snapshot, and file inventory. Do not infer equality from matching filenames or file counts.
4. Exercise a representative task using the extracted package. Check an adjacent request that should keep its existing workflow and a relevant failure case, such as a missing dependency. Inspect the actual output against the task's requirements. Report an unavailable runtime test separately from a passing file check.

Keep the source version, archive filename, archive hash, and host-assigned version in separate fields. An archive named `example-v003.zip` can become host version `v4`.

## Install or replace the requested copies

For a local installation, use the supported installer or managed link. Check an occupied destination before replacing it. Preserve divergent local edits and use a reviewed backup or adoption procedure when needed. Resolve the installed path afterward and compare its files with the package. Start a fresh host session if discovery is cached; invoke the skill there before reporting that host behavior passed.

For an account replacement, inspect the current signed-in account, skill identity, visibility, and version. Use the available connected tool or supported browser workflow. In Claude, the observed workflow was to open the existing skill, choose **Replace**, select the ZIP, and upload it. Treat those labels as navigation clues and inspect the current UI before acting. Creating a duplicate skill is not a substitute for an intended replacement.

Immediately before upload, confirm that the selected file has the reviewed hash and that the current request authorizes this account and visibility. Keep a private replacement private. A separate **Publish to org** action requires authorization for organization distribution. Do not change browser permissions or account settings merely to make automation available. If the interface cannot be controlled, provide the exact package and remaining action for the user.

After an ambiguous timeout or missing confirmation, reopen the skill and inspect its current version before retrying. If the outcome remains unknown, stop further uploads and report the unresolved state. Do not create successive versions through blind retries.

## Inspect the destination

Reopen the installed or uploaded skill and record the displayed identity, version, visibility, and update time when available. Open `SKILL.md` and the support files that the workflow actually needs: references, runtime workflows, scripts, templates, or wordlists. Compare their paths and visible content with the reviewed package. Use a downloaded copy for a full byte comparison when the host supports it. If only part of a file is visible, record the inspected portion and leave full parity unverified.

Run a small representative invocation in each requested host and inspect its output. Confirm that required resources can be read or executed there and that any documented fallback works. A file browser showing a Python script establishes its presence; successful execution needs a runtime result. Local Claude Code installation does not establish Claude account or Cowork discovery.

Record the result in the existing release record with the package hash, destination, observed version, inspected files, invocation result, and remaining action. An upload receipt records an upload; it does not establish behavior in another host. When the host cannot expose exact bytes, state the inspection limit once.

Report what changed, what was verified, which requested destinations remain pending or unchanged, and the exact next action. Use precise states such as packaged locally, installed locally, replaced in the private account, invocation verified, or published to the organization. Stop at the requested destinations.
