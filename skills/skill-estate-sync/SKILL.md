---
name: skill-estate-sync
description: 'Keeps house-skills the single source of truth. Governs six mirror surfaces: Claude Code, Codex, Claude.ai, Cowork, ChatGPT, OpenAI API. Use when a skill changes and has to reach them, when a skill behaves differently between hosts, or to check whether mounted copies match source. Reports local drift, missing shared dependencies, unwired artifact-producing skills, declared canon exemptions, and pending cloud publications. Gates on selftests and builds uploadable .skill bundles. Fixes the failure where working scripts live in a repo but a surface mounts a SKILL.md-only stub.'
---

# skill-estate-sync

The estate drifts because there is no single publish path. Working implementations live in
house-skills; a surface mounts a stripped copy; nobody knows which surface has what. This makes
house-skills the source and every surface a checked mirror of it.

## The six governed surfaces

| Surface | Reached by | Checked how |
|---|---|---|
| Claude Code | `install.sh --platform claude` into `~/.claude/skills` | file by file |
| Codex | `install.sh --platform codex` into `~/.agents/skills` | file by file |
| Claude.ai | a human uploads `dist/*.skill` through org settings | publication record |
| Cowork | a human uploads the same bundles | publication record |
| ChatGPT | a human uploads the same bundles | publication record |
| OpenAI API | whoever owns the deployment attaches the bundles | publication record |

Two mount locally. The diff reads their files and reports a stub or a drift. The other four sit
behind a web UI or an upload endpoint that this toolchain holds no credential for. A ledger row for
one of those records what a person said they published. Nothing here reads the tier back. No row
is independent verification, and every run prints that. A pending publication leaves the exit code
at 0. It is a human step, not a broken build.

## When to use

- A skill in house-skills changed and needs to reach the six surfaces above.
- A skill runs differently depending on which host mounts it (a drift symptom).
- Before trusting any skill on a surface you did not just publish to.

## How it works

It discovers skills by **scanning** `skills/`. A new skill folder is covered with no edit to any
list. Surfaces are declared in `surfaces.json`; adding one is a single line.

1. **Diff.** `python3 scripts/estate_diff.py` classifies every skill on every surface as identical,
   resource-drift, drift, stub, or missing, and lists surface-only skills. Exit 1 on any stub or
   drift. The stub case is the dangerous one: a surface mounting a SKILL.md with the scripts stripped.
   The same pass resolves every `_shared/` reference against source and exits 1 on one that is
   absent. `_shared/` carries no SKILL.md. The mirror scan skips it on that basis; without this check a
   skill can cite a shared file that is not in the repo while the diff still reports green.
2. **Gate + bundle.** `python3 scripts/build_bundles.py` runs each skill's `*_selftest.py` and
   **refuses to bundle a skill that fails its own test, or that ships no test at all**, then zips
   each passing skill to `dist/<name>.skill`. This is the publish artifact and the quality gate in
   one. Absence counts as failure on purpose: an empty test list used to return pass, so untested
   skills bundled clean and the estate reported green over code nothing had ever exercised.
   A skill that cites `_shared/` files gets them vendored into its bundle, since a bundle mounts
   alone.
3. **Publish.** Claude Code and Codex install from source via the repo's `install.sh`; the same
   open `SKILL.md` packages work in ChatGPT skill surfaces. The `.skill` bundles
   are uploaded to the claude.ai organization and to Cowork through a web UI. Nothing in this
   toolchain can read or write those tiers. A human uploads instead, then records it with
   `python3 scripts/record_publish.py --surface <name>`. `estate_diff.py` compares the current
   bundle hashes against that ledger and reports the pending count. The report labels every such
   row as a claim. Before, the cloud tiers were simply omitted. The diff printed "all mirrored"
   while four of six surfaces went unchecked. Never silently overwrite a diverged surface; surface
   the diff and confirm first.

## What the report carries

`--json` and the printed table answer from the same values. The machine report holds:

- `missing_shared`: `_shared/` paths a skill cites that are not in the repo.
- `unwired_content_skills`: artifact-producing skills whose `SKILL.md` never loads
  `_shared/build-card.md`. These fail the audit, exit 1, in both modes. `--json` used to skip the
  check entirely: the report was serialized before it ran. An automated caller then read a green
  estate that the same command printed in capitals.
- `canon_exemptions`: who claims the `engineering-doc` carve-out from STANDARD.md, and why. Counting
  it is the point of declaring it: a reviewer can see whether it is still three skills or twelve.
- `local_surface_drift`: which skills are a stub or a drift on which local mount.
- `cloud_publications`: the last recorded date and the pending bundle count for each cloud tier.
  Its `verified` field reads `false`. No code path in this repo sets it to anything else.

A skill whose entire output is a verdict, a package, code, or captured evidence is exempt from the
build-card requirement. `NO_PROSE_SKILLS` in `estate_diff.py` carries each name with its reason,
because an exclusion nobody can read grows back into the list it replaced.

## Making it run and grow

- **Runs on triggers, not memory.** Wire the git pre-commit hook (`references/pre-commit.sh`).
  It rebuilds bundles on every commit and fails the commit on a failed selftest. A `schedule` task
  runs `estate_diff.py` weekly to report surface drift.
- **Grows by scanning.** Both scripts glob `skills/`; new skills need no registration.
- **Stays honest by gating.** The house standard requires a selftest per skill. The bundler
  enforces it. Nothing untested ships.

## Standard for a shippable skill

Lean SKILL.md (detail in `references/`, loaded on demand), a `*_selftest.py` beside the scripts,
stdlib-only unless a `requirements.txt` says otherwise, no references to retired skills, no
hardcoded `/mnt/skills` paths. `estate_diff.py` plus the bundler enforce the parts a machine can.

## Configuration

`surfaces.json`: `source` is the skills root. `surfaces` holds the local mounts to check and
`cloud_surfaces` the tiers tracked by ledger. See the file for the shape and an optional
claude.ai-offline surface for diffing a cloud tier against an export.
