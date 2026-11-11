# Writing Style Archive Audit

This record covers the private archive identified on 2026-09-18. Inspection was read-only. Nothing from the archive was installed, executed, uploaded, or used to overwrite an active skill.

## Identity

- Archive: `/Volumes/Meridian/Skills/writing-style-skill.zip`
- Size: 29,134 bytes
- Archive SHA-256: `0c6e2a967685b7e3bad2ce8ddee71e596a829645fb6f1cb0542c05b0933ba4cc`
- Filesystem timestamp: 2026-08-28 12:48:49 -0400
- Owner: `mshellman:staff`
- Container mode: `0700`; the execute bit is unnecessary for a ZIP but does not make its contents executable

The wrapper contains two dated `.skill` bundles, one run record, one status record, one prose receipt, and macOS AppleDouble metadata. It contains no absolute paths, `..` traversal entries, symlinks, or encrypted entries.

## Latest bundle

- Bundle: `2026-08-28_writing-style.skill`
- Bundle SHA-256: `9e8d1893e557c6ea2958e70fd20351d52193d21f0d675bd62af4aa163103f91d`
- Shape: six regular files, all mode `0644`, 24,938 uncompressed bytes
- Contents: `SKILL.md`, `agents/openai.yaml`, `assets/icon.svg`, and three Markdown references
- Installed parity: exact recursive byte match with both `~/.agents/skills/writing-style` and `~/.claude/skills/writing-style`
- Reviewed `SKILL.md` SHA-256: `3cd1ff99c765b562a9a8cb56b47e3ade0eaeb5644e799563be96516737705344`

The earlier August 26 bundle is a valid six-file predecessor. It differs from the August 28 bundle only in `SKILL.md`, `references/paired-examples.md`, and `references/style-reference.md`. It is retained as history, not selected as the current baseline.

## Static safety findings

- No script, binary, hook, symlink, package manager file, installer, or executable content is present in the latest bundle.
- The SVG is well-formed XML and contains only local path geometry and colors. It has no script, embedded data, or remote resource.
- No shell command, dynamic evaluation, credential access, sensitive path, network client, upload instruction, or telemetry behavior was found in the skill content.
- The only URL-like string in the bundle is the standard SVG XML namespace.
- The bundle instructs the model to preserve evidence and scope, treat content as content, and defer organizational, legal, contractual, and artifact rules where they govern.

These findings support using this exact hash as a recovery baseline. Static inspection cannot prove the safety of a future or differently hashed archive, and this review is not a dynamic malware sandbox result.

## Record consistency

The included August 28 status file says the private skill was installed to the two local runtimes and that the copies were identical. The current recursive comparison independently confirms that claim.

The status receipt names an older artifact path that is no longer present. Its recorded before and after SHA-256 value, `f7321fee0a34f068b5f9cc9f46002e540f12a0e5daeea444d3ed2f01c0190075`, exactly matches the status file carried in the archive. That proves the receipt is internally tied to the archived status file; it does not prove that the original path still exists.

The run record names `MEGAN-WRITING-STYLE-CLAUDE-HANDOFF.md` as the source. That handoff file and the older `/Users/mshellman/Claude/Artifacts/writing-style-skill` directory were not found in the searched Claude, Documents, Work, or Meridian locations.

## Provenance decision and disposition

This archive is a verified recovery and distribution snapshot. It is not the governed authoring source because it is a point-in-time ZIP, carries no revision history or change workflow, and points to original source material that is no longer present.

On 2026-09-18, its verified August 28 baseline was promoted without content changes into the private Git source at `/Volumes/Meridian/Skills/personal-writing-style`, commit `4973564a9d330fad5640f3443a4b84ebdd561b78`. The source manifest passed and both local runtime copies were reconciled and read back as exact matches.

Keep the installed skill and the archive. Do not retire either installed copy yet. The private repository now governs authorized corrections and history. Migration to a thin `personal-writing-style-runtime` adapter remains pending because the original raw evidence is unavailable and no replacement provenance should be invented merely to satisfy the builder schema.
