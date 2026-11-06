# Go-Live Acceptance tracker spec

Go-Live Acceptance follows the selected executed agreement. A deemed-acceptance mechanism is not universal: first confirm whether that agreement contains one. This tracker computes a deadline only for a sourced clause that uses the supported day-counting rules. Otherwise record the actual acceptance method and required human actions; do not invent a clock or claim the automatic deadline gate passed.

## The clause comes first

Before writing any date, read the executed SOW and extract the deemed-acceptance clause verbatim. Do not assume any period. The period, business or calendar day definition, and trigger event (go-live, delivery notice, or milestone) must all be extracted from the selected clause. The clause text decides all of it. If you cannot get the executed SOW, that is a named gap that blocks this tracker; do not fill it from memory of the template.

Interpretation stays shallow by design: read the period, the day type, and the trigger event off the clause. Anything beyond that (what "contests in writing" requires, whether partial acceptance is possible) is a question for the CSE and counsel, not for this skill. That boundary is why the clause is quoted rather than paraphrased.

## Required fields

The gate (`scripts/closeout_gate.py --type acceptance`) requires these labeled fields, one per line:

- `Go-live date:` YYYY-MM-DD, with the source of the date (the cutover completion step in the runbook, or the delivery notice, whichever the clause names as the trigger).
- `Acceptance period:` `<N> business days` or `<N> calendar days`, exactly as extracted from the clause.
- `SOW clause (verbatim):` the clause text quoted word for word, with SOW ID, section number, and execution date.
- `Deemed-acceptance deadline:` YYYY-MM-DD.
- `Holidays observed:` optional; ISO dates for any holidays inside the window, with the calendar they come from (client's published holiday calendar, or the contract's definition of business day if it has one). Only include holidays you can source.

## The computation, printed

Compute the deadline and show the work in the tracker itself. This synthetic arithmetic example illustrates the convention; it is not a recommended contract term:

> Go-live Friday 2026-08-14 + 10 business days = 2026-08-28 (Friday). Days counted: Aug 17-21, Aug 24-28. Weekends skipped: Aug 15-16, Aug 22-23. No holidays in window.

Day counting convention: day 1 is the first qualifying day after the trigger date. Business days skip Saturdays, Sundays, and listed holidays. The gate recomputes the deadline with the same convention and fails on any mismatch, so a typo in either field is caught before the tracker circulates. If the SOW uses a different weekend, inclusive counting, a time-of-day cutoff, or another convention this calculator cannot represent, stop the automated calculation and record the unsupported rule for a qualified manual review. Extra excluded weekdays can be supplied as sourced holidays; holidays cannot represent a different inclusive or weekend rule.

## Tracking body

Below the header fields:

- **Acceptance criteria table**: each criterion from the SOW and the Test Plan, its source, and its status (met, evidence linked / open, owner, date). Criteria come from those documents only; a criterion nobody signed up to is not one.
- **Open defect disposition**: every open defect carried out of stage 05, by its ID from validate-delivery's defect log, with the agreed disposition (fix in hypercare, accepted as known issue with client sign-off reference, deferred to change order). Keep the upstream IDs; do not renumber.
- **Status line**: one of `Clock running (N business days remain as of <date>)`, `Contested in writing on <date> (effect on clock requires contract review; escalated to authorized commercial owner)`, `Accepted by client on <date> (reference)`, or `Deemed accepted on <deadline> (uncontested; reference to the notice sent)`.
- **Surfacing log**: each time the deadline was surfaced to the Program Lead and CSE, with date and channel. The failure mode this artifact exists to prevent is a missed deadline nobody was watching; the log proves it was watched.

## Draft and decide

Humans accept. The client signs or contests; the CSE decides how to respond to a contest; deemed acceptance is a legal consequence that follows from the clause, not something this skill declares. The tracker records dates, computes the deadline, and surfaces it. It never issues acceptance, never waives a contested item, and never advises the client that the clock has run out on them.
