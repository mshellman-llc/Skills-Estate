---
name: prioritize-work
description: "Rank competing customer problems, jobs, desired outcomes, roadmap candidates or backlog items with one named scoring method (RICE, ICE, WSJF, ODI, Opportunity Score or a weighted decision matrix), write out each candidate's arithmetic and audit the source behind every input. Returns a ranked proposal for a named decision owner. Use when someone asks which scoring method fits, which outcomes are under-served, for RICE, ICE or WSJF scores, what to work on next, or to prioritize or rank a list. Roadmap layout belongs to build-roadmap, sprint commitment to plan-sprint, setting or editing MoSCoW classes on captured requirements to capture-requirements, and job-led discussion with no scoring to frame-jobs-to-be-done."
---

# Prioritize work

> **Before writing: read [the build card](../_shared/build-card.md) and [the planning chain](../_shared/planning-chain.md).** Both are inputs to this work, so read them before choosing a method instead of saving them for a final check. The build card governs how the proposal is produced and checked; the planning chain names who owns each ID, field and log the ranking touches.

This skill puts competing work in order. The candidates may be backlog items, roadmap candidates, desired outcomes, or the customer problems and jobs behind them. It scores them with a single named method, writes out the arithmetic behind every score and audits where each input came from. What it returns is a proposal. The final order is the named decision owner's call.

Stay inside the product, engagement or portfolio the caller has confirmed, and use only the candidates and the evidence that came with them. Each input carries its origin: a user study, an analytics export, a ticket count, an engineer's sizing or a named participant in the working session. Any input without a traceable origin is marked as an estimate.

Publishing a ranking does not make it a decision. On a client engagement, once a person decides, `track-delivery` writes a `DEC-###` entry in the decision log.

## When to use it

Typical requests: "what method should we score these with?", "where are our customers under-served?", "give these candidates RICE scores" (or ICE, or WSJF), "what should we build next?", "prioritize this list" and "rank these items".

Some nearby requests belong to other skills:

| Request | Skill |
| --- | --- |
| Laying out a roadmap and placing items in its horizons | `build-roadmap` |
| Committing items to a sprint | `plan-sprint` |
| Assigning or changing a requirement's MoSCoW class | `capture-requirements` |
| Discussing jobs to be done without scoring them | `frame-jobs-to-be-done` |

## Inputs

- The candidates, each with a traceable `id`: a Requirement Number such as `ABC-012`, an epic prefix, a job ID or a roadmap card ID.
- The values the chosen method needs for every candidate, each with its source.
- The name of the person who will decide the order.
- Python 3 for the scorer. The `evidence-core` runtime supplies the evidence rule this skill follows: a score input either cites where it came from or is labeled a hypothesis.

## Procedure

### 1. Classify the list

State what is being ranked: problems, jobs and desired outcomes, or solutions such as features and initiatives. Problems and jobs are ranked ahead of solutions, because scoring solutions first commits the team to one answer before anyone has checked what solving the underlying problem is worth. For each solution that states no problem, ask what problem it addresses, or detour through `frame-jobs-to-be-done`, which has a reference on prioritizing by job. The scorer flags any item that has neither a `job` nor a `problem` field.

### 2. Choose one method and give the reason

Pick a single method with [the method selection guide](references/choosing-a-method.md) and write one sentence in the proposal saying why it suits this list. If the session ends up mixing methods, record why. The scorer computes six methods, chosen with `--framework`: `ice`, `odi`, `opportunity`, `rice`, `weighted` and `wsjf`. The Eisenhower matrix, Kano, risk versus reward and the impact/effort 2x2 are discussion methods. MoSCoW is also outside the scorer, and its values belong to `capture-requirements`. Formulas, scales and caveats for every method are in [scoring methods](references/scoring-methods.md).

### 3. Gather the inputs and their sources

Collect the method's fields for each candidate, with a source for every value. Record sources in the item's `sources` object under `confidence`, `effort` (this key also covers WSJF job size) and `importance` (customer importance for ODI and Opportunity Score). Effort and job size come from engineering and from nobody else. When nobody can source a value, leave its `sources` entry empty and mark the value as an estimate in the proposal. The scorer flags unsourced effort, job size and customer importance, and it caps unsourced confidence above 50%. Write everything to one candidate JSON file in the shape [the candidate file contract](references/candidate-file.md) defines.

### 4. Run the scorer and work through every flag

Run it from this skill's folder:

```bash
python3 scripts/priority_score.py candidates.json --framework rice
```

Add `--format json` for a machine-readable report, or `--output PATH` to save the report to a file. Exit code 0 means every item was scored. Exit code 1 means the report lists at least one rejected item. Exit code 2 means nothing could be scored or the report could not be written; stderr gives the reason after `error:`.

Handle each flag before presenting. Either remove its cause and rerun (obtain the written source, have engineering size the item, ask what problem a solution addresses) or carry the flag into the proposal where the decision owner can see it. Never raise or lower a value to make a flag disappear. Fix rejected items and rerun, or list them as rejected.

### 5. Present the proposal

The proposal states:

- the method and the reason it was chosen;
- the ranked table with each item's formula and flags;
- the provenance audit, giving the origin of every input and marking each estimate;
- the ties the scorer listed, each left for the decision meeting to break with an explicit tiebreaker (closer strategic fit, less effort or another stated rule);
- the decision owner's name and the exact decision asked of them.

## After the ranking

The owner decides the order. This skill never edits the MoSCoW field that `capture-requirements` owns, and it never moves anything on the roadmap. Each change the owner approves is recorded by the skill that owns that record.

- On an engagement where the new order would change committed scope, raise a scope question through `track-delivery` first, before anyone acts on the order.
- Ranked requirements feed the Product Owner's backlog order; `refine-backlog` and `plan-sprint` then work in that order.
- Ranked jobs and outcomes become Now, Next and Later candidates for `build-roadmap`. Where each one lands stays with the owner.

## Out of scope

- Estimating effort, which is engineering's job.
- Drawing the roadmap, which `build-roadmap` does.
- Making the decision.
- Jobs-to-be-done research and job statements, which belong to `frame-jobs-to-be-done`.
- Assigning or editing MoSCoW values, which `capture-requirements` does after the client or Product Owner confirms them.

## Deliverables

Deliver or link these for every run, following [the output contract](../_shared/output-contract.md):

- the candidate JSON file;
- the scorer's report, in Markdown or JSON;
- the open decision and who owns it.

## Release gate

Apply [the release gate](../_shared/release-gate.md) before delivery. Run `review-writing` over the proposal text, then run `review-deliverable` before anyone calls the proposal final. Until both have passed, it is not final.

## Files in this skill

| Path | Contents |
| --- | --- |
| `SKILL.md` | This procedure |
| `references/choosing-a-method.md` | Problems before solutions, the situation-to-method table, failure patterns and remedies |
| `references/scoring-methods.md` | Facts about each method (formula, scales, caveats), the evidence rules and the originators |
| `references/candidate-file.md` | Input contract for the candidate JSON, with every rejection, flag, note and exit code |
| `scripts/priority_score.py` | Scorer |
| `scripts/priority_score_selftest.py` | Selftest that runs the scorer on the fixtures |
| `scripts/fixtures/*.json` | Synthetic candidate files for an invented ferry booking app |
