# Knowledge Hub design decisions

## Records and working areas

Account facts live once under `account/`. Each opportunity and engagement has a
stable ID, front door, and its own working areas. Create substantive records
when content exists. Initialization creates identity and navigation scaffolding;
it does not imply discovery, approval, delivery, or acceptance occurred.

`AGENTS.md` indexes the hub and `CLAUDE.md` points to it. A separate deal folder
can link to the hub without duplicating canonical records. A synchronized
symlink is not required by the local runtime.

## Claims and ledger

Inline tags express how a statement was authored. Load-bearing claims, sources,
assumptions, and decisions also have durable IDs. Append-only JSONL events form
the ledger; `evidence-core/scripts/ledger_events.py project` produces the JSON
view consumed by downstream validation.

`hub_workspace.py check` detects edits to committed ledger bytes and resolves
claim references. The evidence validator checks authority, status, and source
relationships. Both checks are needed: an unchanged event can still describe
an unsupported claim. The operator coordinating the work mints claim IDs and
reviews proposed claims before appending events.

A project can explicitly choose a directly authored JSON ledger instead. That
choice preserves IDs, sources, and validation but does not provide the JSONL
append-only history check. Record the choice in the project's standards.

## Storage and concurrency

The manifest declares one primary store. Local folders work without Drive or a
company-specific connector. Availability never silently changes authority.
Read operations return a content hash. An update must supply that hash; a stale
version is held for reconciliation. Cooperating local writers take an exclusive
record lock before checking and replacing content. The result is read back.

The lock coordinates writers on the same filesystem. It does not coordinate
independent cloud-sync hosts or external editors that ignore the lock. A synced
Git directory can lose branch references during a race. `audit` reports
unreachable commits; `doctor` attaches them to recovered branches without
merging them. The deterministic recovery drill tests those local operations.
A live multi-host sync claim requires a separate test on those hosts.

Use a configured private Git remote for shared version history when available.
Never create a remote or transfer private hub content implicitly. Initialization
stages only its own files and leaves existing uncommitted changes for review.

## Connector adaptation

Resolve capabilities from the tools actually available in the session. Search,
read, create, metadata update, and content replacement are distinct. The legacy
Drive planner returns planned calls; it does not execute them or prove that a
cloud service accepted them. A supported content updater must retain the
canonical file identity and verify the result. Otherwise use an explicitly
configured local primary, or return an exact patch without claiming a write.

## Extensions that are not implemented by this skill

Cross-user vault sharing, cross-agent signal deduplication, and a shared scope
catalog require separate implementations. Source hashes can support future
deduplication, but recording a hash does not establish those services.
