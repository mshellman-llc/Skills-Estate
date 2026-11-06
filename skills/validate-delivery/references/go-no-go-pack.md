# Go/no-go pack and cutover readiness checklist

The pack is the evidence set the humans sign against at the Validate exit gate. Its job is
completeness and neutrality: every number recomputes from the underlying files, every
acceptance criterion is answered, and nothing in the framing implies the decision. The skill
recommends; the CSE, Program Lead, and client sponsor decide and co-sign. A pack that reads
like a sales case for "go" has failed even if the project should go.

## Authority

The SOW and the co-signed Test Plan own what "accepted" means: the UAT gates, the acceptance
criteria, and any deemed-acceptance language. Reference them by document and section
("per SOW section 6.2"), quote a criterion verbatim when the pack must state it, and never
restate or summarize contractual acceptance clauses in your own words. A paraphrase of a
contract clause is a new clause nobody agreed to. If the SOW and Test Plan disagree, show
both, flag the conflict to the CSE, and do not pick.

## Required sections, in order

Every section is always present. A section with nothing to report says so explicitly
("No open severity 1 or 2 defects as of the stamp date"); a section you cannot fill is a
known unknown with an owner and never a silent omission.

1. **Stamp and sources.** As-of date and time, engagement name, SOW ID, and the exact files
   the pack was computed from (requirements workbook version, tracker file, defect log,
   gaps list), each with its own as-of date. The pack is a snapshot; an unstamped pack is
   unusable the day after it is written.
2. **Decision requested.** What is being decided (go/no-go for cutover on date X), who
   decides, and when the decision is needed. One paragraph, no argument.
3. **Coverage summary.** The trace_check.py counts, printed as computed: total requirements,
   requirements with coverage, named gaps, total scripts, flagged orphans. Then requirement
   pass rate and execution progress per the tracker spec, cut by MoSCoW priority. Include
   the gate result line ("trace_check.py: GATE PASSED, 0 findings"). A pack whose counts do
   not recompute is not a pack; run the gate with --gonogo before shipping.
4. **Named gaps.** Every requirement without coverage: ID, reason, owner, resolve-by, and
   what the gap means for go-live. Gaps block go/no-go in the sense that they must be in
   front of the deciders; they do not mean the answer is no. That call is human.
5. **Open defects by severity.** Full table of open and deferred defects: ID, title,
   severity, triage decision, owner, affected requirement IDs. Sev 1 and 2 individually
   narrated (impact, workaround, plan); sev 3 and 4 may be summarized with counts plus the
   list. Deferred defects appear here with their deferral target; deferral does not remove
   a defect from the pack.
6. **Acceptance criteria status.** Each criterion from the SOW / Test Plan, cited by
   section, with a Met / Not met / Cannot assess status and the evidence pointer. Cannot
   assess is a legitimate status and a finding; do not squint it into Met.
7. **Cutover readiness checklist.** See below, with per-item status and owner.
8. **Risks carried into deploy.** Test-surfaced risks and issues, already routed to the
   RAID log, that survive into cutover: open defects going to hypercare, data quality
   findings, training gaps. This is what manage-cutover-closeout inherits; name it here
   so the handoff is a file, not a hallway conversation.
9. **Recommendation and decision block.** The skill's recommendation, stated once, with the
   two or three facts that drive it, followed by the honest case for the other answer.
   Then the signature block: decision, date, names, roles, both sides. The block ships
   empty. The skill never fills it, never marks the gate met in the engagement record, and
   never schedules cutover.

## Cutover readiness checklist

Seed from the Test Plan and deployment plan; this is the default item set when they are
silent. Each item: status (Ready / Not ready / N/A with reason), owner (role), evidence.

- Deployment runbook exists, is dry-run tested, with timings and a named runner per step
- Rollback plan exists and the rollback trigger conditions are written down
- Production environment access confirmed for every person in the runbook
- Data migration final pass planned: source freeze, load window, reconciliation counts
- Integration cutover steps sequenced with the owning external teams confirmed
- UAT sign-off obtained or scheduled (reference the SOW's acceptance mechanism, do not restate it)
- Training delivered; attendance and outstanding cohorts listed
- Hypercare model staffed: window, roster, severity routing, per SOW
- Open defect handoff list agreed with the client (which known issues go live)
- Communications plan: go-live announcement, freeze notices, support channel
- Go/no-go meeting scheduled with the deciders named

Executing this checklist (the cutover itself, hypercare) is manage-cutover-closeout's
job. This skill establishes readiness and hands the checklist over.

## Neutrality rules

- Counts before adjectives. "3 open sev 2 defects" precedes any characterization of them.
- No significance inflation and no minimizing: "only 3 defects" and "3 critical blockers"
  are both editorials; "3 open sev 2 defects, workarounds documented for 2" is evidence.
- The recommendation lives in section 9 and nowhere else. Sections 1 through 8 contain no
  recommending language.
- Present the same facts you would present if the recommendation were the opposite.
