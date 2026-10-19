---
name: beastmode-capture
description: Save a BeastMode decision, discovery, or factual correction with evidence and review state. Use when Megan says remember this, correct the hub, or capture a decision. Do not treat brainstorming as confirmed fact or claim a proposal is accepted.
metadata:
  version: "2026.09.30.2"
---

# Capture a decision or correction

## Host access

Use only tools and files actually available in this session. In Claude Code invoke `/beastmode-capture`; in Codex use `$beastmode-capture`; in Claude chat/Cowork ask to use `beastmode-capture`. Mac paths identify local authorities; in Cowork resolve them only through a folder already shared with this session. Cloud chat cannot read a Mac path or localhost merely because this skill names it. When hub access or a required foundation is unavailable, report that gap and continue only work supported by accessible evidence. Use named companion skills when available; otherwise apply the safeguards below and identify any required review gate you cannot complete. Do not install dependencies or broaden permissions automatically.

Use the existing hub update workflow. Do not write a second memory database or edit an assistant's separate memory unless Megan explicitly requests that separate destination.

1. Read the current BeastMode router when available and call the permitted hub's `get_context`. Establish exactly what Megan wants retained, where it belongs, and its existing sharing boundary. Default private personal capture to a permitted local destination; never infer approval to upload it to hosted or shared spaces.
2. Search for the existing subject record. Fully fetch the relevant record and sources in bounded parts, pinned to exact revisions. A correction belongs with its subject and provenance, not in a competing rulebook. If several authorities disagree, keep the conflict visible; neither drive, the newest timestamp, nor an AI synthesis wins automatically.
3. Preserve the user's wording where it expresses a decision. Classify each statement as confirmed, user-reported, observed, proposed, estimated, or creative canon as supported by the contract. Record the source and when the statement applied separately from when it was captured. A user report is attributable evidence, not independent verification. Ask only for an ambiguity that materially changes the decision, authority, or sharing scope.
4. Inspect the actual proposal schema in the available tool/service before constructing input; do not invent required fields or a new-record revision sentinel. Submit `propose_update` against the exact record and contract revisions read. Contract, confirmed-fact, and sharing changes follow the service's owner-review rules. On revision conflict, refetch and compare; preserve both edits and do not force an overwrite.
5. If the connector lacks write access, use an already-authorized local hub workflow only when the current task permits it. Never elevate a shared/cloud actor by borrowing local owner credentials. If no permitted write path exists, save a clearly marked private pending proposal under the current local intake route, including target, base revisions, evidence, and reason it is pending. If even that destination is unavailable, return the draft without claiming it was saved.
6. Verify the service response and fetch the resulting state. Distinguish draft, saved pending, proposal submitted, accepted, and dependent review needed. Acceptance requires an acceptance receipt or current accepted revision; creating a proposal is insufficient. After an accepted correction, identify registered dependents, request the supported refresh, and verify what changed. Unregistered documents may still be stale. Preserve submitted résumés, published historical artifacts, and archived evidence; create corrected successors where appropriate.

Return what was captured, its source, destination, exact state, and what remains for review. A saved proposal is not an automatic change to every AI tool. For material changes use `execution-truth` and report changed now, verified, still unchanged, and exact next action.

Examples: `$beastmode-capture Hold the sales-pursuit number until we have supporting evidence.` / `$beastmode-capture Save this as a proposed product idea, not a committed plan.`
