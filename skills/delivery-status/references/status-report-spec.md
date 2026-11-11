# Weekly status report: section spec

The report is a projection of the governance logs and the period's evidence, in a fixed order. Sections are never dropped because they are empty or awkward; an empty section states why it is empty. Fill `assets/weekly-status-template.md`; this file explains what earns a line in each section.

## Header (required, gate-checked)

```markdown
# {Client} : {Engagement} : weekly status

Period: 2026-08-04 to 2026-08-08
Issued: 2026-08-08 | Prepared from: {n} transcripts, RAID log, decision log, {burn source}
Previous status: status-2026-08-01.md | SOW baseline: {SOW id, signed date}
```

The `Period:` line is mandatory and machine-checked (`Period: YYYY-MM-DD to YYYY-MM-DD`). "Prepared from" names the actual inputs so a reader knows what this report can and cannot know. If there is no previous status, write `Previous status: none (first status of engagement)`.

## 1. Flags (red items first, never buried)

Anything red, newly slipped, or newly drifted, at the top, before the good news. Each flag: one sentence, its stable ID or candidate title, and what decision or action it needs from whom. If there are no flags, write "No flags this period" so absence reads as a check performed.

A flag cleared this period is reported as cleared, with its source, and the body lines it touched are updated to match. A banner over a stale document body is not resolution.

## 2. Outcomes this period

What the client can now do, decide, or rely on that they could not last period. Three to six bullets, outcome-first, each with a source.

- Good: "Requirements Document co-signed 2026-08-06 (gate met; D-014)."
- Bad: "The team continued working on requirements." Activity without an outcome goes to the plan section or nowhere.

## 3. Plan position

Progress against the plan: current phase, next gate and its date, on/off track per workstream stated as a fact with a source, not a mood. Dates that moved are stated as moved, from what to what, and why, with a source. A date restated from the previous status without checking is the failure mode; reconcile every date against the previous status file.

## 4. RAID movement (counts, not adjectives)

```markdown
Risks: 4 open (1 new: R-009), 1 closed (R-003). Issues: 2 open, 0 new.
Dependencies: 3 open, 1 delivered (D-002). Assumptions: 1 invalidated (A-004).
```

Then one line each for the movers: what changed, why, source. Every ID referenced must exist in the log (gate-checked). Items open in the previous status either appear here as moved or are still open in the counts; nothing vanishes without a line.

## 5. Decisions

New decisions this period by ID, with who made them and the one-line rationale. Then "Decisions needing attention": open questions ripe for a decision, with the gate they block. This section is why the same conversation does not happen twice.

## 6. Scope drift (required, gate-checked)

Per `references/scope-drift-protocol.md`. Either "None observed" plus what was compared, or candidate blocks each with at least one `Evidence:` line. Unresolved candidates from prior periods reappear until a human decision lands.

## 7. Hours and burn (required source, gate-checked)

Burn this period, burn to date, remaining against the estimate, from a named source:

```markdown
Burn: 118 h this period, 642 h to date of 960 h estimated (66.9%).
Source: timesheet export 2026-08-08 (Q-000043 baseline).
```

If no source is available: `Named gap: burn unavailable this period; no timesheet export provided. Owner: Program Lead, resolve by next status.` Never carry last period's figure forward as if current, and never estimate. Percentages are computed from the sourced figures and shown with their inputs so the reader can recompute.

## 8. Upcoming period

The next gate, the meetings that matter, what Aleysian needs from the client (each need with an owner and a date; unowned asks evaporate).

## 9. Artifact and gate register delta

Only what moved: artifacts delivered or versioned, gates met or signed, with dates and acceptance method. Point at the register; do not reproduce it.

## Line-level rules

- Every line about scope, hours, or dates carries a source: a transcript ref, SOW clause, timesheet export, log ID, or a named gap. A confident sentence with no provenance is a live grenade in a client-facing document.
- Counts, not adjectives. "On track" is only writable next to the evidence that shows it.
- Direct client quotes are attributed by speaker and date.
- No em dashes, sentence-case headings, no meta-signposting, no significance inflation. Run the prose gate.
- The report reads top-down in two minutes: flags, outcomes, then detail. A reader who stops after section 2 has the truth, just less of it.
