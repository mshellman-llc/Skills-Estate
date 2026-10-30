# Scope-drift detection protocol

Scope is always an estimate; no project delivers exactly to the SOW. The job is not to pretend drift away but to see it early, with evidence, so the change-order conversation happens while it is still cheap. Silently absorbed work is the most expensive kind: it costs margin now and credibility later when the absorbed item finally surfaces.

## What this protocol produces

Change-order **CANDIDATES**. Never change orders. A candidate is a routed proposal for a human decision; the decision (in scope, absorb deliberately, or raise a Change Order) belongs to the Program Lead and CSE, and contractual review uses the contract scope and obligation review mode in `statement-of-work`; authorized humans own contractual changes. This skill supplies the evidence and stops.

## The detection pass

Run every period, even when nothing seems off. Compare two things against the SOW scope baseline (the scope body plus Exhibit A Basis of Estimate where one exists):

1. **Observed work**: what the team actually did this period, from transcripts, demos, and the artifact register.
2. **Client asks**: anything a client stakeholder requested, assumed aloud, or described as expected, whether or not anyone acted on it yet. Asks are drift leading-indicators; work is drift confirmed.

For each item, answer: does the baseline name this, qualitatively (scope body) and within footprint (Exhibit A)? Three outcomes:

- **In baseline**: normal status content.
- **Ambiguous**: the baseline neither clearly includes nor excludes it. Log it as an open question with an owner, and say so in the status report. Ambiguity flagged early is a cheap conversation; ambiguity discovered at invoice time is not.
- **Outside baseline**: raise a candidate.

## Trigger classification

Use the two-trigger taxonomy in the contract scope and obligation review mode of `statement-of-work` (read `_runtime/sow-quality/references/basis-of-estimate.md` from that package; apply it only when the selected agreement adopts it, and do not restate its mechanics in the report):

- **Soft trigger (volumetric)**: the footprint materially exceeds the Basis of Estimate. Record counts, custom-automation volume, catalog scale well past Exhibit A figures. "Materially" is doing the work: note small overages, but a candidate needs material excess.
- **Hard trigger (binary workstream addition)**: a second integration, a second org, an org split or merge, an additional migration. Any amount triggers, regardless of size. Do not treat these as negotiable by degree.

If no Exhibit A exists, say so: classification degrades to scope-body comparison only, and that gap is itself worth reporting (and worth a RAID assumption entry).

## The candidate evidence-trail format

Every candidate in the status report's scope-drift section uses this block. The gate requires at least one `Evidence:` line per candidate.

```markdown
### Candidate: {short title}

- Trigger class: hard | soft | no-baseline
- The ask or work observed: "{verbatim quote}" ({speaker}, {date}, {meeting})
- Baseline position: SOW section {n} / Exhibit A line {ref}: "{what the baseline actually says}"
- Evidence: {source 1: transcript ref with quote, timesheet line, artifact}
- Evidence: {source 2, if any}
- First observed: {date} | Periods open: {n}
- Routed to: Program Lead, CSE
- Status: raised | acknowledged | decided ({decision log ID once a human decides})
```

Rules:

- The ask is quoted verbatim and attributed. A paraphrase can be argued with; a quote cannot.
- The baseline citation quotes what the SOW actually says, not a summary of it. The reader must be able to see the gap between ask and baseline on the page.
- A candidate stays in the scope-drift section every period until a human decision lands (then it carries the decision log ID and drops off the following period). Repetition here is deliberate: an unresolved candidate that vanishes from the report has been silently absorbed.
- Never net candidates against underruns. "They asked for a second integration but the data volume came in light" is two facts, not a wash.

## When nothing drifted

The section still appears:

```markdown
## Scope drift

None observed. Compared {n} transcripts and the period's delivered work
against SOW sections {refs} and Exhibit A ({m} footprint lines).
```

Stating what was compared is the point. "None observed" after a real comparison is a finding; a missing section is an unchecked box.

## Worked example

A requirements-session transcript contains the client asking for a NetSuite integration when the SOW names a single integration (Workday). Output: a D-0NN candidate is wrong (no human decided anything); correct output is a DP or open-question entry if relevant, plus this candidate: trigger class hard, the ask quoted ("we will also need this flowing into NetSuite", B. Chen, 2026-08-05), baseline position citing the SOW integration clause verbatim, evidence lines pointing at the transcript, routed to Program Lead and CSE. The conversation is captured once, with evidence, and does not need to be reconstructed at negotiation time.
