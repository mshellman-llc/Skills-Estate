---
name: manage-consulting-knowledge
description: 'Resolve, retrieve, and safely update durable consulting knowledge across a client, its opportunities, and its engagements, and stand up or check the pursuit workspace inside the hub. Use when work needs bounded account, pursuit, delivery, evidence, transcript, outcome, or deliverable context from local files, Google Drive, or supplied files, or when a pursuit needs its workspace created, audited, repaired, or gated against the workspace standards.'
---


# Manage consulting knowledge

The Hub owns consulting record identity, retrieval, and persistence. It follows
the client relationship from account context through pursuits, delivery,
outcomes, and expansion. `evidence-core` owns source and claim quality inside the
Hub. `ingest-transcript` preserves and normalizes meeting evidence.

Use the logical records in
[`record-registry.json`](references/record-registry.json). Read only the adapter
needed for the available store: [`drive-mcp-contract.md`](references/drive-mcp-contract.md)
for Drive or `scripts/hub_runtime.py` for guarded local writes. Supplied files
remain a read or patch surface unless the host confirms a write.

## Work with the Hub

1. Confirm the client. When the task concerns a pursuit or delivery, confirm one
   opportunity or engagement. Stop if identity remains ambiguous.
2. Read the manifest and the applicable front door: `client.front_door`,
   `opportunity.front_door`, or `engagement.front_door`.
3. Select the task route or up to four named logical records. Search transcript
   and evidence indexes before opening source bodies.
4. Preserve source IDs, contradictions, current or superseded state, dates, and
   unresolved gaps. Put the current answer before history.
5. Write only to the manifest's declared primary store. Existing local files
   require the SHA-256 observed during the read. Drive writes must follow the
   connector's actual capabilities. Never create a duplicate canonical record
   to bypass a missing update operation.
6. Read back or hash the result before reporting persistence. Mirror changes run
   only after the primary write succeeds. Divergent copies stop for review.

The directory is a catalog, not a template to fill with empty files. Create a
record when it has durable content. Store a fact once and point other records to
its canonical location.

## Stores and persistence

Supported primary stores are `local`, `google-drive`, and `supplied-files`.
When more than one is available, `primaryStore` decides; availability never
changes authority.

A `local` store can be any explicitly configured writable folder. Google Drive
and a synced mount are optional. The manifest's `stores.local.root` is resolved
relative to the manifest location when it is not absolute. A sync mount remains
one local access path; its presence never changes `primaryStore` automatically.
`hub_runtime.find_synced_hub_roots` requires an explicit caller-selected `base` directory. It can discover candidate mounts there, but identity, authority and actual read/write access must still be checked. Discovery grants no write authority, including for a folder labeled My Drive.

Use the record CLI for local work. It validates registered context identities,
returns content and its observed hash together, serializes cooperating local
writers, and reads back the written bytes:

```bash
python3 scripts/hub_records.py --hub "<hub>" routes
python3 scripts/hub_records.py --hub "<hub>" --opportunity <opp-id> context proposal
python3 scripts/hub_records.py --hub "<hub>" --opportunity <opp-id> read opportunity.discovery
python3 scripts/hub_records.py --hub "<hub>" --opportunity <opp-id> write opportunity.discovery --input discovery.md --create
python3 scripts/hub_records.py --hub "<hub>" --opportunity <opp-id> write opportunity.discovery --input discovery-revised.md --expected-hash <observed-sha256>
```

Use `--create` only for an absent record. A stale hash returns `conflict-held`;
read the current record, reconcile the competing evidence, and retry with the
new observed hash. A held local writer lock requires inspecting the active
writer before recovery. The lock does not coordinate separate cloud-sync hosts.
Drive connector capabilities must be inspected in the current session; use the
[adapter contract](references/drive-mcp-contract.md) for capability checks.

Use exactly one persistence state:

- `written-and-confirmed`
- `written-primary-mirrors-pending`
- `patch-returned`
- `not-written`
- `conflict-held`

A required Hub with no readable source blocks a fully client-grounded result.
An optional Hub may be skipped when supplied evidence is enough; state what was
not checked. A denied write returns the exact logical target and a patch when
safe. Never describe a patch as an update.

## The pursuit workspace

A hub on a local filesystem is also the working environment for a pursuit or a
delivery. `scripts/hub_workspace.py` owns that layer, with the verbs from the
enforcement standard and exit codes 0, 1, 2:

```bash
python3 scripts/hub_workspace.py init --hub "<AI Knowledge Hub>" --client "<name>" \
  --opportunity <opp-id> --opportunity-name "<pursuit>"
python3 scripts/hub_workspace.py init --hub "<AI Knowledge Hub>" --engagement <eng-id> --engagement-name "<delivery>"
python3 scripts/hub_workspace.py audit --hub "<AI Knowledge Hub>"
python3 scripts/hub_workspace.py doctor --hub "<AI Knowledge Hub>"
python3 scripts/hub_workspace.py check --hub "<AI Knowledge Hub>" [paths]
```

`init` creates or repairs the hub root: `hub.yaml`, `AGENTS.md` as the index
with `CLAUDE.md` as its one-line pointer, `TODO.md`, `00-CLIENT.md`, and copies of
[`workspace-standards.md`](references/workspace-standards.md) and
[`pursuit-methodology.md`](references/pursuit-methodology.md) as `STANDARDS.md`
and `METHODOLOGY.md`. With an opportunity it adds the front door and the
working areas `inputs/`, `research/`, `synthesis/`, `evidence/`, and
`deliverables/`, then initializes Git and commits only the files it created or updated. An
engagement receives its own front door and working areas. Existing uncommitted
work is preserved; initialization reports that an explicit reviewed commit is
needed. `--no-git` supports a folder without version control, and
`--synced-filesystem` declares a configured sync mount for a new hub. It never
overwrites a file that exists; human edits are authoritative.

`audit` runs at every session start, before any work, because `AGENTS.md` says
so. It is read only and reports Drive conflict copies, lock files, a missing
pointer, dormancy, and any commit a Drive sync race dropped off the branch. The
concurrency posture is detection and repair, not prevention: `doctor` reattaches
a dropped commit under `refs/heads/recovered/` for the orchestrator to merge,
removes a `.git` conflict copy that is byte-identical to its original, and
restores missing pointer files, saying so per fix.

`check` gates working-area files before the orchestrator commits: frontmatter,
the claim-tag vocabulary, the assumptions section, absolute dates, and every
`CLM-###` resolving to a claim event. It proves the ledger at
`evidence/evidence-ledger.jsonl` is append-only against the committed copy.
Claim discipline inside that ledger belongs to `evidence-core`; run its
`ledger_events.py check` in the same gate. The standards file says what each
rule means and why; the
[design decisions](references/design-decisions.md) describe the storage, ledger, and recovery boundaries.

## Compatibility and checks

The older eight-file Drive Hub and 12-file local research folders are migration
inputs. Map them through the registry. Report mode may inspect them but may not
rename, rewrite, or move client material.

Run:

```bash
python3 scripts/hub_resolver_selftest.py
python3 scripts/hub_runtime_selftest.py
python3 scripts/migration_report_selftest.py
python3 scripts/hub_workspace_selftest.py
```

Return resolved identity, logical records used, sources, findings, attempted
writes, persistence state, pending mirrors, conflicts, and exact patches. Format
the durable run record with
[`output-contract.md`](../_shared/output-contract.md).

Legacy migration inventory accepts an explicit `--bucket-scopes FILE` JSON mapping of existing folder names to `opportunity`, `engagement` or `unclassified`. Without that mapping, folders remain unclassified; their names never establish lifecycle authority. The report proposes mappings and preserves source bytes. Actual migration requires its own authorized write and readback.
