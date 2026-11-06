# Lessons-learned and reusable-asset harvest spec

Closeout is where the firm's biggest knowledge loss happens: lessons and account history get buried in a project folder and never reach the next team. The harvest is the step that closes the loop, and it is first-class work, not a wrap-up chore. A strong harvest makes the next handoff faster and the next estimate better; skipping it is the single biggest source of repeated effort on the next project.

Ask for or reuse an explicitly confirmed private engagement destination and its authorized audience. Prepare the harvest there only when writing is authorized; otherwise return a draft and exact proposed destination. An attached Project, cached knowledge store, or unrelated account is not an implicit destination. Keep client-specific and relationship information in that private record. A separate reusable asset needs rights, confidentiality review, and approval before crossing into a shared library.

## 1. Actuals vs estimate

The table that turns this engagement into a comparable for future deals. It lives in the Hypercare Closeout Report and is checked by the gate.

| Workstream | Estimated hours | Actual hours | Variance | Source |

- **Estimated hours** come from the quote (the Q-number via the scoping system) or the SOW exhibit. Never from memory.
- **Actual hours** come from timesheets or the time-tracking export, named with an as-of date.
- **Source** names both, per row. Where a number cannot be sourced (timesheets miscoded, quote superseded mid-engagement), the cell reads `GAP:` plus what is missing, who owns getting it, and by when. A gap is a finding; a filled-in plausible number is a fabrication and a hard fail.
- Add one prose paragraph per workstream whose variance exceeds the project's documented review threshold (if none is set, report all variances and ask the owner to prioritize review): what drove it, in terms the next estimator can act on ("client data quality" is weak; "the source system had no stable key for contacts, adding a matching workstream nobody scoped" is usable).
- Money rule: this table carries hours and variance, not rates, fees, or margin. Pricing analysis belongs to the Pricing System; this feeds it comparables.

State explicitly in the harvest that this table feeds future deal comparables. That sentence is what makes the next Sales Solution Lead go looking for it.

## 2. What broke and why

For every Sev 1 and Sev 2, and any lower-severity issue with a systemic cause: what happened, the cause chain (technical and process), the earliest point in the lifecycle it could have been caught, and what would catch it next time. Causes, not blame; roles, not names, unless the lesson is about a staffing pattern. If the same cause appears twice in the engagement, say so; repetition is the lesson.

## 3. What worked

Two to five things worth repeating deliberately, each concrete enough to repeat: a demo cadence that kept a difficult sponsor engaged, a migration reconciliation script, a cutover sequencing choice. "Good communication" harvests nothing.

## 4. Reusable assets

Each candidate asset gets: name, what it does, where it lives (repository path, Drive file ID, or knowledge-base location; a real pointer, not "in the project folder"), the capability and playbook it maps to, the effort it saved or would save, and its generalization state (client-specific as-is / needs scrubbing / already generic).

Candidates are nominated here, not promoted. A human (the Solution Lead or the practice owner) confirms quality before an asset is promoted for reuse; record who confirmed and when, or record the nomination as pending with an owner. An unreviewed asset promoted into the knowledge base is worse than no asset, because the next team will trust it.

## 5. Account history

The paragraph the next pursuit team reads first: how the relationship ended the engagement, who the real decision-makers turned out to be versus who the org chart said, sensitivities and commitments made, open change-order candidates (the warm pipeline), and the client's stated next steps. Source each claim (transcript, log entry, decision record). This section is restricted to the confirmed account audience. Include only relevant, authorized information and keep it out of portable skill or plugin sources and general reusable libraries.

## 6. Confidence-tag reconciliation

If the supplied project risk profile carried evidence-backed capability-gap tags, state per tag whether the delivery experience confirmed the gap, narrowed it, or surfaced a new one, with the evidence. This is how the firm's confidence tiers stay honest.

## Format and landing

One markdown document plus the actuals table already in the closeout report. Every claim sourced (log entry, timesheet export, quote field, transcript). Apply review-writing to it; the harvest gets read by people who were not there, so it must survive without the delivery team in the room. Save only to the confirmed authorized private destination, link it from the authorized engagement record, and report the actual persistence state. If permission or destination is missing, return the draft and the precise pending action.
