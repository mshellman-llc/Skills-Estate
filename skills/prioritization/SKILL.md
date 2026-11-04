---
name: prioritization
description: 'Rank problems, jobs, roadmap candidates or backlog items with a named framework (ODI, Opportunity Score, RICE, ICE, WSJF, weighted matrix) and check the evidence behind every score, so the ranking is a sourced proposal for the person who decides. Use for "prioritize these", "RICE score", "rank the backlog", "what should we build next", "which outcomes are under-served", "WSJF", or choosing a framework. Do NOT use for MoSCoW values on captured requirements (requirements-capture), job-led debate without scoring (jtbd-framing), roadmap layout (roadmap-artifacts), or sprint commitment (sprint-planning).'
---

# Prioritization

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [the planning chain](../_shared/planning-chain.md). Inputs, not a final pass.**

This skill turns a candidate list into a ranked proposal with the formula and the evidence for each score visible. The person who owns the decision sets the order. A ranking is not a decision until that person makes it, and delivery-status records it as a DEC entry on an engagement.

## Project context required

Use only the caller-confirmed product, engagement or portfolio and the candidates and evidence supplied for it. Score inputs come from named sources: research, analytics, support records, engineering sizing, or the people in the session. An input with no source is labelled an estimate.

## Workflow

1. **Name what is being ranked.** Problems and jobs come before solutions. If the list is features with no problem named, ask which problem each addresses, or apply jtbd-framing's prioritization reference first. The tool flags items without a `job` or `problem`.
2. **Choose one framework** with [the framework reference](references/frameworks.md). State the choice and the reason.
3. **Collect inputs with sources.** For each item record the framework fields and a `sources` entry for confidence, effort and customer importance. Effort comes from engineering. Write the candidate file described in [candidate format](references/candidate-format.md).
4. **Score and read the flags.** Run the tool. Resolve each flag or carry it into the proposal; do not raise a number to clear a flag.
5. **Present the proposal.** Show the ranked table, the formula for each item, the flags and any ties. Name the decision owner and the decision needed. Do not change requirements-capture's MoSCoW values or the roadmap; the owner decides and the owning skill records the change.

## Tool

```bash
python3 scripts/priority_score.py candidates.json --framework rice
python3 scripts/priority_score.py outcomes.json --framework odi --format json --output ranking.json
```

Frameworks: `rice`, `ice`, `opportunity`, `odi`, `wsjf`, `weighted`. The tool caps unsourced confidence above 50%, flags unsourced effort and customer ratings, notes ties and uniform impact, and exits 1 when an item is missing a required field or repeats an ID. Report the counts and flags it prints.

`scripts/priority_score_selftest.py` checks the formulas against the upstream demo scores and the evidence rules against failing fixtures. Run it after any change.

## How rankings feed the chain

- Ranked jobs and outcomes give roadmap-artifacts its Now, Next and Later candidates; the owner places them.
- Ranked requirements inform the Product Owner's backlog order, which backlog-refinement and sprint-planning follow.
- On an engagement, a re-ordering that moves committed scope is a scope question; route it through delivery-status before anyone acts on it.

## Durable output

Each run leaves the candidate file, the ranking report (Markdown or JSON) and the decision still needed, per `_shared/output-contract.md`. Deliver or link them.

## Boundaries

- Does not decide. The named owner does.
- Does not set or rewrite MoSCoW values; requirements-capture records them after the client or Product Owner confirms.
- Does not run JTBD research or write job statements. That is `jtbd-framing`.
- Does not draw the roadmap. That is `roadmap-artifacts`.
- Does not estimate effort. Engineering does.

## Files

- `references/frameworks.md`: framework selection, formulas, scales, evidence rules and common failures.
- `references/candidate-format.md`: the candidate JSON the tool reads.
- `scripts/priority_score.py`: the scorer, which uses the standard library only.
- `scripts/priority_score_selftest.py` and `scripts/fixtures/`: formula parity and evidence-rule cases.
- `UPSTREAM.md` and `LICENSE-UPSTREAM`: the source this skill adapts and its license.

## Release gate (required)

Before you deliver, run the gate. Full spec in [`release-gate.md`](../_shared/release-gate.md).

1. Apply writing-integrity to the proposal prose.
2. Run quality-gate before you call it final.

Do not present the ranking as final until both checks have passed.
