---
name: delivery-suite
description: 'Orchestrates the delivery half of the Estate sell-to-deliver lifecycle from signed SOW through hypercare closeout. It owns the Handoff-through-closeout stage map and its human gates. Named skills own the artifacts and the per-engagement DELIVERY-STATE.md records their state. Use when a request concerns a live delivery engagement and the owning skill is not obvious. Do not use for pre-signature work; route directly to the named sales artifact owner.'
---


# Estate delivery suite

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [Writing Integrity review](../writing-integrity/references/detailed-review.md). Inputs, not a final pass.**

The coordinator for delivery engagements after signature. It identifies the current stage, what gate
comes next, and which skill does the work. Content decisions stay with the skill
that owns each artifact. This file stays thin on purpose: the moment it starts
describing how to build a charter or a test script, it is competing with the
owner, and instruction competition is the defect the house model exists to kill.

## Project context required

Use only the caller-confirmed engagement, source records, private output location,
and intended audience. Map reference roles such as Program Lead, CSE, Solution Lead,
and Pursuit Lead to that project's authorized owners; these labels do not impose
an employer organization chart or signing authority. The executed agreement and
accepted project plan determine gates, commercial rules, and support obligations.
Keep account history, risk assessments, credentials, and client evidence outside
portable skill sources. A cached account, attached Project, or available connector
is not authorization to read, write, or publish.

## Where the files are

`scripts/` holds `plan.py` and its selftest with fixtures. `references/` holds
`stage-map.md` (the full stage, gate, and owner table plus routing edge cases and
the known-gaps register) and `delivery-state-spec.md` (the DELIVERY-STATE.md
format). Read `stage-map.md` before routing anything unusual; the table below is
the compact form.

## The lifecycle is eight ordered steps

Handoff (pre-stage), then 01 Mobilize, 02 Analyze, 03 Design, 04 Build,
05 Validate, 06 Deploy, and the closeout loop inside 06. Each exits through a
named gate, several co-signed by the client. Gates are exit conditions held by
humans; skills draft, humans approve and sign. Preserve existing stage IDs in an engagement record. Apply the gates required
by its accepted project plan; never mark one passed without its acceptance record.

## Who owns what

Read the [stage model](references/stages.json) for the current task owners and
exit gates. The planner reads that same model. Read [the stage guide](references/stage-map.md)
for stage work and routing exceptions. Mobilization uses delivery-kickoff;
validation uses acceptance-testing. Delivery-status maintains the reporting
cadence and flags potential scope changes.

Use the project's authorized implementation workflow for Build. Keep its actual
build evidence distinct from acceptance. Apply writing-integrity to all authored
prose; use the shared brand runtime for styled artifacts. The executed agreement
and accepted changes govern commitments. This router does not approve a price.

## How to route a request

1. **Find the engagement and its state file.** `DELIVERY-STATE.md` at the
   engagement folder root. Truth hierarchy: executed SOW/quote > artifact files >
   state file > memory > chat. If the state file is missing, do not guess from
   chat: locate the hard evidence (signed SOW? accepted brief? signed charter?
   co-signed requirements?) and write the state file from it per
   `references/delivery-state-spec.md` before routing.
2. **Run the planner.** Never assemble the plan by hand.

   ```bash
   python3 scripts/plan.py path/to/DELIVERY-STATE.md
   ```

   It prints where the engagement is, the next gate and who holds it, the
   ordered remaining stages with their owning skills, and findings (out-of-order
   gates, a stage line that disagrees with the gate ledger, unparseable entries).
   Report the position and every finding; do not narrate the run. `--json` gives
   the machine contract; the text default is the one to use.
3. **State the position plainly to the user.** Stage, next gate, gate holder.
   If the user's request belongs to a different stage than the engagement is in,
   say so before routing; building ahead of an unpassed gate gets rebuilt.
4. **Hand off to the owning skill by name**, with the engagement folder, the
   state file path, and the specific artifact asked for. This suite does not
   build the artifact, review it, or restate the owner's method.
5. **Verify the state file moved.** Whichever skill closes a gate updates
   DELIVERY-STATE.md in the same session (gate status with date, artifact path,
   append-only log line). When routing next, check the update happened; a stale
   state file makes every later plan wrong.

## Durable output

This suite produces no business artifact; those belong to the specialists it
routes to. What it does leave, per `_shared/output-contract.md`, is the run's
own Markdown record: the planner output (position, next gate, remaining
stages, findings), the routing decision made, and any state-file corrections,
alongside the updated DELIVERY-STATE.md itself. Deliver or link the record;
never just say it was written.

## Gate discipline

- A gate passes when the signed or accepted artifact exists, not when the work
  feels done. The planner treats an undated pass as suspect; so should you.
- Reopening a passed gate is scope drift first: log it through
  `delivery-status` and assess the change-order candidate before any
  rework starts.
- Apply the Go-Live Acceptance mechanism in the executed agreement. Use a
  deemed-acceptance clock only when the agreement actually contains one;
  otherwise obtain its specified acceptance evidence. `cutover-closeout` owns
  that check. This suite does not close the gate without that evidence.
- A blocked gate is a finding with an owner and a resolve-by date in the state
  file's open decisions, never a reason to route around the gate.

## Check current capabilities and gaps

Inspect the caller's actual comparables library, authorized automation, and
approval records before reporting a gap. If prior-deal evidence is unavailable,
record that limit rather than inventing a comparison. Do not promise automatic
execution at signature or a stage change without its configured trigger and
execution evidence. Route pre-signature governance to its confirmed owner;
this suite starts at the signed engagement. See `references/stage-map.md`.

## What this skill does not do

- Does not build any delivery artifact; the stage skills own their artifacts.
- Does not price or author numbers. Executed commercial artifacts hold committed values. Route proposed changes to the confirmed commercial owner and `project-scoping`; `sow-quality` reviews their evidence and language but does not calculate pricing.
- Does not gate content quality; parity and visual are `brand-renderer`,
  writing review is `writing-integrity`, evidence is `evidence-core`.
- Does not touch pre-signature work. Send each request to its named sales artifact owner.
- Does not decide, approve, or sign; humans hold every gate.

## Rules

- **Never fabricate a gate status.** No signature on file means the gate is open.
- **Never build ahead of the plan.** Work started before its gate gets rebuilt.
- **Route by name.** Name the owning skill in the handoff; "the requirements
  skill" invites the wrong one.
- **Carry state in the file, not in chat.** Anything worth remembering across
  sessions goes into DELIVERY-STATE.md's ledger or log, with a date.
- **Report counts and gate names, not adjectives.** "At 02 Analyze, next gate
  requirements co-signed, 2 findings" rather than "on track".
- **Flag decisions, do not assume them.** Open decisions carry an owner, a
  resolve-by date, and the gate they block.

## Files

- `references/stages.json` · the authoritative stage IDs, gates and task owners.
- `scripts/plan.py` · the deterministic planner; it reads that stage model.
  Keep `references/stage-map.md` consistent with the model when changing it.
- `scripts/plan_selftest.py` · run it after any change to the planner or the
  state spec; it must pass before the change ships.
- `scripts/fixtures/` · state files exercising new, mid-engagement, complete,
  out-of-order, and malformed cases.
- `references/stage-map.md` · the full map, routing edge cases, known gaps.
- `references/delivery-state-spec.md` · the DELIVERY-STATE.md format and rules.
