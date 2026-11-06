# Shared Writing Integrity rules

Status: design proposal accompanying the local C24 scanner implementation. No
shared rules endpoint, owner enrollment or infrastructure deployment is claimed.

Assume a personal service with a small set of authorized tools. No request rate,
latency target or storage growth measurement was supplied. Keep the existing
single local service and measure requests, snapshot size, conflict rate and
pending outbox age before adding capacity. The Mac remains a single availability
dependency; a second hosted service would require a separate operating decision.

## Reuse the existing store

`skills/review-writing/scripts/learning.py` already owns a private SQLite
store with correction events, active rules, reviews and task checkpoints. It
requires an explicit store and learning enrollment. Multiple local processes
can use the same store. Capture is duplicate-safe; promotion checks evidence,
repair/keep assessments, scope and profile budgets. Changed instructions require
the current rule revision. Imports remain candidates. Review declarations are
procedural evidence, not authentication or independent proof of quality.

The existing Knowledge Hub supplies authenticated clients, scoped access,
revision-controlled records, protected-change review and receipt-based retries.
Its generic record saves do not modify the Writing Integrity SQLite database.
Use a Hub adapter over one canonical Writing Integrity store. Do not maintain
editable active rules in both Hub Markdown records and the learning database.
Hub records may link to receipts or hold a clearly marked read-only projection.

```text
Authorized writing clients
  -> existing Hub authentication and server-side profile mapping
  -> Writing Integrity adapter
  -> one canonical learning database, catalog and operation receipts

Accepted snapshot -> compatible scanner or local context reader
Pending correction -> review -> accepted revision -> subsequent client read
```

Keep three concepts separate within that authority: maintained editorial rules,
the owner's scoped voice preferences, and unreviewed correction evidence. The
existing 12-rule/350-word profile budget serves personal context. Add a distinct
editorial catalog namespace rather than inflating
that budget or silently turning an AI repair into a personal preference.

## Interface and authority

Proposed operations are `writing_context`, `writing_capture`,
`writing_propose_rule`, `writing_review_rule`, `writing_receipt` and
`writing_scan`. They are not current Hub tools.

| Operation | Input after authentication | Result |
| --- | --- | --- |
| `writing_context` | Authorized context handle, purpose tags, supported schema/engine | Applicable accepted snapshot, revisions, digest and freshness |
| `writing_capture` | Context handle, operation key, expected profile revision, minimal evidence | Saved event ID and receipt; no automatically active rule |
| `writing_propose_rule` | Operation key, expected revisions, evidence IDs, instruction, exceptions, test results | Pending proposal ID and durable receipt |
| `writing_review_rule` | Authorized reviewer, operation key, proposal ID/revision, decision and reason | Accepted revision or retained rejection with receipt |
| `writing_receipt` | Operation key in the caller's authorized context | Completed result, pending status or unknown key; never assumed success |
| `writing_scan` | Authorized context, compatible snapshot revision, transient text | Candidates, input digest and actual engine/rule revisions |

Invalid input is rejected before a write. Missing enrollment returns an explicit
setup state. It cannot present an empty personal profile as current. Authentication
expiry requires reconnection; it does not delete stored records. A later authorized
`writing_context` call reloads the same canonical identity and accepted state.
Conflicts retain the submitted proposal for reassessment. Returning after an
ambiguous timeout first queries `writing_receipt` with the original key.

An owner-controlled server mapping binds an authenticated actor to permitted
profile, scope and operations. The caller cannot choose an arbitrary store path,
owner string, personal namespace or trusted host identity. Host provenance comes
from the connection; caller-supplied host/session labels are supplementary.
Reading rules, submitting corrections, reviewing proposals and publishing engine
changes are separate permissions. Do not grant all connected tools review power.

Capture the smallest redacted before/after pair, reason, actual source reference,
actor, session, scope and time. An observed user correction and an AI repair keep
different bases. Imported content cannot authorize policy changes. A proposal
needs a stable pattern ID, instruction, exceptions, evidence references and
positive/negative test results. Confirm authority before activating preferences;
the owner's learning enrollment may authorize routine reviewed maintenance.
Changes to facts, privacy, sharing or core policy retain the existing owner gates.

The store remains local to the service machine; do not put live SQLite on a file
share. Once service-managed, direct client CLI writes must be disabled or routed
through the adapter. Otherwise clients could bypass identity mapping and review.
The Hub adapter supplies the transport and authorization boundary. The learning
database remains the sole writable authority for rules.

## Revisions, conflict handling and retries

Before exposing the helper remotely, add a transactionally incremented profile
revision covering every mutation, immutable rule revision history and a persistent
operation receipt table. A context response includes profile/catalog revisions,
rule IDs/revisions, scope, engine/schema versions, snapshot digest and read time.
Updates carry the revision actually read, plus per-rule revisions for consolidation.
Stale edits return a conflict and leave the existing rule untouched. Review
overlapping instructions instead of silently giving the latest writer precedence.

Proposed additive tables are `profile_state(profile_id PRIMARY KEY, revision
INTEGER NOT NULL)`, `rule_versions(rule_id, revision, body_json, recorded_at)` and
`operations(actor_id, profile_id, key, payload_sha256, receipt_json)`. Their
composite primary keys are the first two and first three columns respectively. Foreign
keys bind profile/rule identities to their existing rows. Existing rows retain
their IDs; backfill a version snapshot before enabling service writes. The
catalog adds its own namespace and revision rather than reusing private profile
IDs. Migration needs a verified backup and transactional schema version. Restoring
an old schema after new writes requires data recovery in addition to binary rollback.

Each mutation has a stable operation key and canonical payload digest scoped to
the actor and profile. Commit the mutation, new revision and receipt together.
Retrying the same key and payload returns the original receipt without a second
promotion. Reusing a key for different content is an error. After a timeout,
query that receipt before retrying. A failed revision check requires rereading
and reassessing; it is not an invitation to force an overwrite.

The current helper does not yet provide these service-level guarantees. Identical
promotion requests reinforce a rule and increment its revision again; captures
deduplicate only the same event payload. There is no profile-wide revision in
`context`, no authenticated identity mapping, and retirement has no expected
revision. Do not expose the raw CLI as an authenticated service and call it done.

## Reading current rules and scanning

Adapters fetch a bounded applicable snapshot at task start and after an accepted
correction. Recheck its revision before consequential delivery; if relevant rules
changed, review the affected output against the new snapshot. Record which
snapshot and engine actually ran. A task should not silently mix rule revisions.

Use stable detector types implemented in reviewed engine code, with validated,
bounded data parameters. Do not execute code or arbitrary regular expressions
submitted as pattern records. Ordinary editorial guidance can change as data;
a new algorithm or unsupported detector type still needs an engine release.
The scanner must reject unsupported schemas instead of ignoring new checks.

For tools that can send the artifact under existing sharing authorization,
`writing_scan` can run the current central engine and return candidates, versions
and an artifact hash. Otherwise a local adapter retrieves the accepted compatible
rule snapshot and scans locally. The artifact need not be saved in the Hub.
Store rule-change evidence separately from transient drafts, with restricted
access and minimal retention. Do not upload private draft text merely to obtain
a style check.

Replace embedded active rule catalogs with a small adapter and an explicitly
versioned offline baseline. Existing embedded copies require a one-time migration;
adding a server does not update them. Enumerate all consumers, verify their actual
route in fresh sessions and record unsupported hosts. The inspected local standing
instructions prefer the primary Writing Integrity path, but this does not prove every workflow
uses it or that remote tools follow that route.

## Offline behavior and recovery

Cache only the last accepted authorized snapshot, with its scope, digest,
retrieval time, compatibility and expiry. Keep raw examples and credentials out
of portable packages. A cache is dated evidence, not proof of current rules.
When the service is unavailable, report the cached revision or use the packaged
baseline with a reading pass. Do not report current-rule compliance. Consequential
work requiring current rules waits for retrieval or an explicit owner decision.
Revoked or incompatible access must not fall back to a broader profile.

Retain authorized pending corrections in a private local outbox with their
operation keys. Reconnection reads receipts first and retries unchanged payloads;
conflicts and protected reviews remain pending. Test Mac sleep, unavailable
gateway, revoked access, timeout after commit, partial writes and restart.
The Hub's existing remote route depends on the local machine being available.

Extend the existing private backup/restore process to cover the canonical rules
database, revision history and receipts consistently. Restore into isolation,
check integrity and ownership, then verify cross-client retrieval before claiming
recovery. Do not create new credentials or broaden grants as an incidental step.

## Adoption and acceptance

First confirm the intended private store, owner and enrolled scopes; discovering
the helper is not evidence that a live store is enrolled. Test migrations and
adapter behavior with synthetic profiles. Then obtain the applicable service
change and access approvals, install the reviewed adapter, and enroll only the
named clients using existing authenticated connections where permitted.

Required evidence includes two independently authenticated clients reading the
same accepted revision, a correction proposed by one and observed by the other
only after review, rejected cross-profile access, conflicting updates, idempotent
retries after ambiguous outcomes, offline recovery, protected evidence and a
consumer inventory showing which old embedded routes remain. Test the scanner's
positive cases and counterexamples against that exact rules/engine revision.

This would remove repeated manual rule distribution for connected clients after
adoption. It cannot remove editorial review, guarantee that every tool invokes
the adapter, or eliminate engine and connector updates forever.

The main trade-off is adapter work versus duplicated state. Generic Hub records
would be faster to populate, but a second editable rule authority would create
conflicts with the existing helper. Keeping SQLite behind one adapter preserves
the current evidence model at the cost of adding authenticated service semantics.
Revisit that choice only if the helper is deliberately retired through a complete
data migration. A larger distributed service would improve availability while
adding operating cost and a new privacy boundary; no such need is established here.
