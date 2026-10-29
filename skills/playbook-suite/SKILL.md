---
name: playbook-suite
description: 'Orchestrates the full Estate playbook artifact suite. Knows what a complete playbook is, what order the artifacts get built in, which skill builds each one, and what has to pass before anything ships. Use whenever someone wants to build, complete, audit, conform, or publish an Estate playbook, or asks what is left on one. Trigger on "build the playbook", "what''s left on PB-CPQ", "conform this playbook", "playbook artifacts", "is this playbook ready", "run the playbook suite", or any PB-code paired with build, audit, gate, or ship. Do NOT trigger for a single artifact when the user named that artifact directly; call the owning skill instead.'
---


# Estate Playbook Suite

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

The coordinator for the playbook artifact suite. It decides what must exist, in what order, who builds it, and what blocks the next step. Content decisions stay with the skill that owns each artifact.

## The spec is upstream

`_shared/playbook-spec/SPEC.md` is the single authoritative definition. Read it before acting; where this file and the spec disagree, the spec wins. Both scripts pin to the spec version and raise a finding against a manifest that declares a different one.

SPEC.md is 18 KB. Read the shared sections (artifact suite, brand, voice, release gates, naming) plus the `### NN` section for the artifact in hand. Loading all ten artifact definitions to build one of them is waste.

## The suite is ten numbered slots

Nine required; the ROM deck (06) is the one conditional slot. Numbering never changes.

## Where the files are

This skill uses the standard nested layout: `scripts/` holds `plan.py` and `conformance_audit.py`, `references/` holds `conformance-procedure.md` and `phase-2-extension.md`. Every command below is written for that layout.

## How the plan is produced

Never assemble a build order by hand. Run the planner:

```bash
python3 scripts/plan.py manifest.json --format text
```

Pass `--format text`. The default `--format json` is the machine contract for a phase 2 executor and runs several times larger and slower. Step 6 below re-runs the planner after every artifact, so the compact format matters.

It reads the playbook's `manifest.json`, expands the artifact table against that playbook's options and its ROM flag, resolves dependencies, and emits an ordered plan with one action per artifact: `build`, `finish_and_gate`, `run_gates`, `fix_gate_failure`, or `complete`. It raises findings on missing Q-numbers, missing timeline snapshots, any tier below the confirmed project margin floor, and a manifest whose declared spec version is not the planner's.

The planner is deterministic and content-free. Read `phase-2-extension.md` before changing anything in `plan.py`.

## Working a playbook

1. **Locate the manifest.** `manifest.json` in the playbook folder, conforming to
   `_shared/playbook-spec/schema/manifest.schema.json`. No manifest means the playbook
   predates the spec; write one from what is on disk before building anything.
2. **Run the planner.** Report the totals and every finding. Do not narrate the run.
3. **Take the next ready step.** The plan names the builder skill. Hand off to it with the artifact number, the option if any, and the Q-number.
4. **Gate the result.** All three gates, every artifact, written disposition each. A FAIL is not shippable.
5. **Update the manifest.** Status and gate results, immediately. A manifest that lags the folder makes the next plan wrong.
6. **Re-run the planner** and continue until nothing is outstanding.

Do not build ahead of the plan. An artifact built before its dependency exists gets rebuilt.

## Who builds what

| Artifact | Skill |
|---|---|
| 01 README | this skill, from the manifest |
| 02 Overview | this skill thinks, `playbook-onepager` renders |
| 03 One-pager | `playbook-onepager` |
| 04 Talk Track and Objections | this skill thinks, `playbook-onepager` renders |
| 05 Qualifier | this skill, plus the `qualifier.json` twin |
| 06 ROM deck | `estate-brand-renderer` |
| 07 DDOC | `estate-ddoc` |
| 08 Proposal | `estate-brand-renderer` |
| 09 Pre-Engagement Stage Gate | copy the template, adapt rows |
| 10 SOW | `estate-sow` |

Gates on everything: `estate-brand-renderer` for parity, a human or model for visual, `prose-pass` for prose. Voice rewriting is `prose-pass`, applied during the build and not as a pass afterwards.

## Artifact 05 has a machine-readable twin

The Qualifier ships as a .docx for humans and a `qualifier.json` for the fit router, both generated from the same source. They must not drift. When the Qualifier changes, regenerate both in the same step, and validate the JSON against `_shared/playbook-spec/schema/qualifier.schema.json` before marking the artifact done.

## The DDOC mode is a scope fact

Decision mode when the client is choosing between options. Confirmation mode when there is one option. Both are required; a single-option playbook still gets a DDOC, because the artifact's job is putting the client on record accepting a boundary, not comparing prices. The mode follows from the option count in the manifest, so the orchestrator passes it rather than asking.

## Conformance runs

To audit an existing playbook against the spec rather than build a new one:

```bash
python3 scripts/conformance_audit.py PLAYBOOK_DIR --manifest manifest.json
```

`--infer` drafts a manifest from filenames when none exists. `--json` switches the report to JSON; the default text report is the compact one and is the one to use.

It reports what is present, what is missing, what is misnamed, what carries no gate result, and what is likely off-spec by format. It reads the filesystem and the manifest only. It does not open documents, so it cannot judge whether an artifact's contents match the spec. That judgment is the visual gate and stays with a person.

## Rules

- **Never fabricate a number.** No price, duration, margin, or count that the quote or the source does not ground. Flag it as an open decision.
- **Never mark an artifact complete without three gate dispositions.** A clean tool run is not a release authorization.
- **Never renumber artifacts.** The numbers are stable across the whole catalog.
- **Carry unchanged content verbatim.** Re-transcribing introduces drift. Copy and edit only the target section.
- **Flag decisions, do not assume them.** Collect them and surface them with the delivery.
- **Report counts, not adjectives.** "0 fail, 4 warn" rather than "clean".

## Files

- `plan.py` · the planner. Shared with the phase 2 workflow engine.
- `conformance_audit.py` · audits an existing playbook folder against the spec.
- `phase-2-extension.md` · the contract that keeps phase 2 additive.
- `conformance-procedure.md` · the six-step conformance run.

The manifest and qualifier schemas the planner cites live in `_shared/playbook-spec/schema/`.
## Commercial policy input

The package planner reads `commercial_policy` from the manifest. Supply
`margin_floor_pct` with its `source` and `verified_at` date from confirmed
project policy. No percentage is supplied by this skill. Without a verified
policy, the planner flags approval as unresolved while preserving the build
plan and known economics. An example threshold has no authority for another
engagement.
