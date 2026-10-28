# Post-call ingestion protocol

The second half of the skill's job. The brief walked the team in; ingestion walks the answers back into the record so scope moves on evidence, not memory. Run it as soon after the session as the transcript exists, once per session.

The governing rule, inherited from the ledger: **the transcript is the only source that closes a question.** An answer nobody gave is an invention. Unanswered stays open.

## 1. Get the real transcript

- Pull the verbatim, speaker-labeled transcript through whatever the account uses: the connected meeting-notes integration, Drive, or an uploaded file. Never settle for a summary; a summary says the client has quoting problems, the transcript says one person prices multi-year commitments in a spreadsheet updated from memory, and only the second version moves scope.
- Never substitute a similarly titled note for the session that was named. Confirm the date and attendees match the calendar event before ingesting.
- If no transcript exists, say so and stop. Notes from a human attendee can be ingested, but every fact they produce enters Column A as Inferred, sourced to "attendee notes, [name], [date]", never Confirmed.

## 2. Walk Column B, question by question

For each open question in the session brief, in rank order:

- **Answered.** Move the fact to Column A: claim as stated, source "session transcript [date], [speaker]", confidence Confirmed, with the attributed verbatim quote preserved. Retire the question's id. Remove the don't-size flag from the scope line it was blocking; the line is now sizeable, though sizing itself belongs to the scoping owner.
- **Partially answered.** Record what landed as a Column A entry, then keep a narrowed replacement question open under a new id, with why_open updated to say what the session did and did not resolve.
- **Answered with a conflict.** The room said something the RFP or a workshop contradicts. Keep both in the claim text, flag the divergence, mark Inferred, and add a resolution question to Column B. Never launder two answers into one confident fact.
- **Unanswered.** Stays open, rank re-checked (an answer elsewhere in the call may have raised or lowered its scoping impact).

## 3. Extract what the questions did not anticipate

Read the transcript once more for decisions and facts outside the question list: a workflow the client described, a system nobody had named, a boundary a stakeholder asserted, a date that moved. Each becomes either a Column A entry (sourced to the transcript) or a new Column B question. New scope-relevant facts also become decision-log entries.

## 4. Log decisions

Every decision the session produced or changed gets a decision-log entry:

```json
{
  "decision": "Discount approvals move to the new platform; three tiers",
  "transcript_ref": "session 2026-08-14, 00:41, VP Finance",
  "changes": "Adds an approval-workflow scope line; supersedes the March working assumption of two tiers",
  "status": "proposed"
}
```

A decision that changes prior scope is flagged as a decision change, explicitly, so it is tracked toward the gates and scope does not silently drift. Status stays `proposed` until the scoping owner confirms; this skill never sets it to anything else.

## 5. Propose scope revisions, do not commit them

Produce a scope-revision proposal for the scoping owner: lines to add, lines whose don't-size flag cleared, lines the session moved out of scope, each with its transcript reference. Hand it to **scoping-agent** territory (the Pricing System) for creation, editing, and sizing. This skill proposes and cites; it never creates or edits a scope item, never prices a line, and never clears a gate. The SSL owns the scope.

## 6. Feed the Pursuit Brief

New findings flow forward into the rolling Pursuit Brief that call-prep maintains:

- Update the sections of the Knowledge Hub file `01-client-engagement-profile.md` this skill is allowed to touch: confirmed facts (with transcript sources), stakeholders, important unknowns, risks, and decisions needed. Update idempotently; re-ingesting the same transcript changes nothing.
- Human-authored material is protected. Never rewrite, trim, or reflow anything between `<!-- human -->` and `<!-- /human -->` markers; write around the blocks, not through them.
- When the full Pursuit Brief markdown file is in reach, verify the update before replacing it: `python3 <call-prep>/scripts/check_pursuit_brief.py --before old.md --after new.md`. Abort the update if it fails.
- The Pursuit Brief's shape and its recommended-call plan belong to call-prep; this step supplies facts, not structure.

## 7. Refresh and re-gate

- Re-rank the surviving Column B for the next session or, if discovery is complete, for the proposal. The re-ranked list is the next session's brief spine.
- Rerun `scripts/check_brief.py` on the updated ledger. The same rules apply: sources on every Column A entry, rank and unblocks on every surviving question, rank order intact.
- Stamp the updated ledger with the transcript it ingested and the date, and update the deal folder copy. Point future sessions at the file rather than restating it.

## 8. Close the loop

Report to the user: questions closed (with the one-line answer each), questions still open in rank order, decision changes flagged, and the scope-revision proposal. Then name the biggest judgment call made during ingestion (usually a partial answer treated as closed, or a conflict resolution) and argue the other side of it honestly.

## Failure modes

- Ingesting a summary and losing the verbatim quote that would have carried the value argument.
- Marking a question closed on an answer the transcript does not contain.
- Committing scope instead of proposing it.
- Losing a decision change so the next brief and the proposal quietly disagree.
- Ingesting the wrong meeting because the title matched.
