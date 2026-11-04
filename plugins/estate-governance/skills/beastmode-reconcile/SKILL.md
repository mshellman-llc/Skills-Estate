---
name: beastmode-reconcile
description: Compare a named knowledge folder with current authorities, preserve unique evidence, and archive verified duplicates reversibly. Use for new intake or continued cleanup. Do not trigger for simple retrieval, or equate similar filenames, age, or inactivity with obsolescence.
metadata:
  version: "2026.09.30.2"
---


# Reconcile a bounded set of files

## Host access

Resolve the hub endpoint, router, local roots and permitted account from explicit task or project configuration. No personal drive, owner profile, schedule or account is a default. Confirm that the selected adapter implements the named operations; if it does not, use its supported equivalent and preserve the same revision, authorization and acceptance checks.

Use only tools and files actually available in this session. In Claude Code invoke `/beastmode-reconcile`; in Codex use `$beastmode-reconcile`; in Claude chat/Cowork ask to use `beastmode-reconcile`. Mac paths identify local authorities; in Cowork resolve them only through a folder already shared with this session. Cloud chat cannot read a Mac path or localhost merely because this skill names it. When hub access or a required foundation is unavailable, report that gap and continue only work supported by accessible evidence. Use named companion skills when available; otherwise apply the safeguards below and identify any required review gate you cannot complete. Do not install dependencies or broaden permissions automatically.

1. Read the current configured hub router and call the permitted hub's `get_context`. Resolve the current reconciliation record and disposition map from the configured project or explicit caller-supplied location; select the latest applicable evidence, not a date alone. Identify the named folder, comparison roots, authority questions, and authorized action. Both comparison roots are sources; neither outranks the other by location.
2. Check mounts and actual source paths before using old manifests. Read relevant folder/repository guidance. Inspect dirty work, tracked paths, vault structure, links, symlinks, hard links, and active consumers before proposing moves. Reuse existing validated inventory and hash results when unchanged. Hash only changed or missing candidates; escalate to content comparison only for meaningful differences. Do not rescan all configured roots for a one-folder request.
3. Classify each candidate as exact duplicate, divergent version, complementary evidence, unique material, or unresolved. Exact duplicates require matching complete file hashes and a verified retained copy; archive safety also depends on the file's role. Matching bytes alone do not authorize breaking a repository, app, vault, or active route. Treat credentials and recovery material as excluded: do not read, copy, or ingest their contents.
4. For divergent material, compare relevant claims and intended use. Preserve source authorship, dates, and evidence. Newer edits are not necessarily newer facts. Keep distinct assessment versions and related-but-different programs separate. Do not promote an unsupported metric from a historical résumé, borrowed example, or AI summary. Extract unique material into a cited comparison or proposed synthesis without silently replacing originals.
5. Prepare a concrete move manifest in the private reconciliation area: source, retained canonical/peer path, archive destination, hashes, classification, reason, consumer repairs, and inverse move. Record why an authority was selected. Reuse the existing map format and rollback mechanism rather than creating a second ledger. Keep unresolved authority decisions visible while completing independent safe work.
6. If the user requested cleanup/archiving, perform reversible moves within that scope once verification and the manifest are ready; do not ask again for an already-authorized action. If the user requested comparison only, stop at the reviewed plan. Never permanently delete. Before each move, recheck source and peer hashes and refuse occupied destinations. Use staged copy-and-verify before source removal for cross-filesystem moves; retain complete recovery evidence. Prefer archiving verified individual files over moving a mixed folder with unique content.
7. Verify every disposition on disk, retained content, repaired links/consumers, and rollback instructions. Preserve historical submissions and repository history. A missing drive or read error is incomplete coverage, not a duplicate or successful archive. Record completed, preserved, excluded, and unresolved items explicitly.
8. Refresh affected hub routes through supported version-checked proposals or the existing authorized bridge workflow. Do not overwrite synchronized knowledge Markdown or open a second writer against the live SQLite store. Verify ingestion/retrieval separately from the filesystem move. A source-change flag is not proof that dependent prose was corrected.

Use `execution-truth`. Finish with changed now, verified, still unchanged, exact next action, and the disposition/rollback record. Use semantic scope such as “this assessment folder,” not total file counts, to explain coverage. Leave unrelated projects and libraries alone unless requested.

Example: `$beastmode-reconcile Compare this folder with the current career sources, preserve unique material, and archive verified duplicates.`

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
