# Workspace standards

The rules for every file inside an AI Knowledge Hub, and especially for the
working areas (`inputs/`, `research/`, `synthesis/`) where a pursuit or a
delivery turns thin inputs into defensible conclusions. `init` copies this file
into the hub root as `STANDARDS.md` so agents landing in the folder have the
rules in context before their first token. Human edits to the copied file are
authoritative for that hub and are never reverted by a later `init`.

These standards combine logical record identity, evidence discipline, and
pursuit working areas. [Design decisions](design-decisions.md) in the
installed skill explains the ledger and concurrency boundaries.

## Files

- Markdown only, unless a person asks for another format. Machine data is JSON
  or JSONL beside the Markdown that explains it.
- Filenames in kebab-case. No dates or version numbers in names. Update files in
  place; history lives in git and in the file's changelog section.
- One topic per file. A file that starts covering two topics gets split, and the
  index gets both.
- Every new file gets a row in `AGENTS.md`. The index is the map; an unindexed
  file does not exist.
- A file named `name (1).md` may be a sync conflict copy. Compare its contents
  and preserve unique material before removing a confirmed duplicate. `audit` reports them; one inside `.git` is blocking.

## Required frontmatter

Every Markdown file in a working area carries:

```yaml
---
title: <what the file is>
status: draft | in-review | final
owner: <person, or the agent role that wrote it>
updated: YYYY-MM-DD
sources:
  - <SRC id, or a relative link to the main input>
---
```

A file converted from another format adds provenance: `source`, `drive_id`,
`converted`, and `truncated: true|false`. A converted file never pretends to be
complete. Fetches that failed go in `inputs/failed-fetches.md` with the reason,
never silently skipped.

## Claim tags

Every substantive claim in a working-area file carries exactly one tag. The tag
is the authoring-time shorthand; the evidence ledger is the record. The mapping
is fixed:

| Tag | Meaning | Ledger status | Ledger record |
|---|---|---|---|
| `[STATED]` | The client, or the vendor in writing, said it. Cite the SRC. | Confirmed when a supporting source has authority 70 or higher, otherwise Inferred | claim event |
| `[OBSERVED]` | Found in public research. Cite a working link at the claim. | Confirmed or Inferred by the same authority rule; public sources usually land Inferred | claim event |
| `[INFERRED]` | Deduced from stated or observed facts. Name the facts it rests on. | Inferred | claim event |
| `[ASSUMED]` | A working assumption with no evidence yet. | Unknown, with owner and closure condition when load-bearing | claim event plus an assumptions register row |
| `[DECIDED]` | A working position the team chose where alternatives existed. Name who, when, what it rests on, and where the if-false consequence lives. | none: decisions are not evidence | decisions register row |

The tag records how a claim was authored; the source's authority decides what
it can bear. A `[STATED]` claim whose only source is a Slack message (authority
50) projects to Inferred, and the ledger check says so. A claim with no citation
is `[ASSUMED]` by definition. Downgrade it rather than leaving it naked. Tagging a decision as `[STATED]` or `[INFERRED]` launders
judgment into evidence; the ledger check rejects a claim event tagged `DECIDED`.

Every file that contains an `[ASSUMED]` claim ends with an
`## Assumptions to validate` section listing them, so the list can be walked with
the client. `check` fails a file that has the tag without the section.

## IDs and the citation chain

IDs are minted once, in one place, and referenced everywhere else. Never
re-paraphrase the text behind an ID.

| ID | What | Minted in |
|---|---|---|
| `REQ-<AREA>-##` | A stated requirement, verbatim | `inputs/stated-requirements.md` |
| `SYS-##` | A client system, with role and evidence | `account/technology-landscape.md` (client level, stored once) |
| `SD-###` | A candidate scope driver from the universe pass | the research file that enumerates the universe |
| `SRC-###` | A source: type, authority, dates, locator | the ledger `source` event; readable row in `evidence/source-register.md` |
| `CLM-###` | A load-bearing claim | the ledger `claim` event |
| `ASM-###` | A priced assumption with its if-false consequence | the ledger `register` event (assumptions); readable row in `solution-and-scope.md` or `risks-decisions-and-changes.md` |
| `DEC-###` | A decision, who and when | the ledger `register` event (decisions); readable row beside the ASM rows |

Hub records point down into inputs; everything else points into the hub by ID.
Only the source register and the ledger hold file paths, so a moved input breaks
one row, never fifty citations. Register `locator` fields use relative Markdown
links that any tool can follow; Obsidian wikilinks are welcome in prose for the
humans and the graph view.

The chain, drawn in the order facts come to exist:

```text
inputs/transcripts/2026-09-04-discovery-call.md   the client's words
  -> SRC-002  source event: authority 70, locator, anchor 00:41:12
  -> CLM-014  claim event: tag STATED, status Confirmed, sourceIds [SRC-002]
  -> ASM-007  register event: rests on CLM-014 and SYS-03, if false adds SD-041
  -> synthesis/requirements-theory.md cites ASM-007 and owns no facts
```

Synthesis documents trace each conclusion to REQ, SD, SYS, ASM, or CLM IDs. A
conclusion that traces to nothing is an `[ASSUMED]` claim and goes on the list.

## The evidence ledger

`evidence/evidence-ledger.jsonl` is the ledger's event log: append-only JSONL,
one JSON object per line, under git. The JSON projection supports consumers
that require a single schema-validated ledger document.

- Only load-bearing claims pay the ledger toll: figures, dates, counts, named
  capabilities, anything synthesis cites. Colour commentary gets a tag only.
- Supersession is a new `supersede` line naming the old claim and the new one.
  Nothing is edited or deleted. A restated claim is a new `claim` line with the
  same id; the latest line wins.
- The first line is a `context` event naming the client and the opportunity or
  engagement, so the ledger can be projected into the schema that
  `evidence-core` validates.
- `check` enforces append-only structurally: the committed content of the file
  must be a byte prefix of the working copy. It also resolves every `CLM-###`
  in the working areas to a claim event. `evidence-core`'s `ledger_events.py
  check` enforces the tag-to-status mapping and the claim rules;
  `ledger_events.py project` writes `evidence/evidence-ledger.json` for the
  finalization gate.
- Validation runs at every orchestrator gate commit, not only at artifact
  finalization, so a fabricated or unsourced load-bearing claim survives at most
  one gate cycle.

## Supersession and negative findings

- When a late fact reframes part of a file, put a section-precise banner at the
  top: `> Partially superseded by the 2026-09-04 pivot: sections 4B and 5
  superseded, 1 to 3 still valid. See <replacement>.` This keeps readers from
  treating superseded figures as current evidence.
- Reversed decisions stay visible: `~~decision~~ REVERSED 2026-09-04`, with the
  reversing decision logged as its own row.
- Evidence files carry a `## What was NOT discussed` section naming content that
  was invented and removed. Negative findings are findings: "searched X, found
  nothing, use Y".
- Record conflicts rather than smoothing them: when two sources disagree, log
  both and the materiality, and let the ledger carry the conflict event.

## Statelessness and changelogs

File content states current truth only. When evidence changes a claim, rewrite
the claim as if it had always been known, with the tag and citation brought
current. No inline "updated 2026-08-28" narration, no "corrected from X"
vestiges. Change history lives in one optional `## Changelog` section at the
bottom, one dated line per change. Claim tags, citations, and confidence stay
inline; they are evidence about the claim, not history about the file.

## Version control

A versioned hub is a Git repository; a local folder does not require cloud sync. `init` runs `git init` and
commits the skeleton. Git earns its place the first time a late fact reframes
the deal: the pivot is reviewed as one diff, and the superseded thesis stays
retrievable.

- The orchestrator commits; subagents never run git. Subagents write files, the
  orchestrator gates them, and a passed gate ends with a commit whose message
  names what moved and on what evidence.
- Plain commits on the default branch. No history rewriting, no force
  operations. This is a document workspace.
- Use a configured private Git remote when sharing version history across
  machines. A cloud-synced `.git` directory can develop conflicting references;
  the local lock does not prevent that cross-host race. If a hub already uses
  such a mount, `audit` detects dangling commits and `doctor` preserves them
  under `refs/heads/recovered/` for review and merging. Detection is not proof
  that the cloud service synchronized every file.
- No remote is created implicitly. Keep one writer per shared hub until the
  selected collaboration method has been exercised on the intended hosts.
- Initialization commits its own skeleton files only. When existing work is
  uncommitted, initialization leaves it for an explicit reviewed commit.

## Dates and money

- Absolute dates only. Never "last month" or "recently". `check` warns.
- Price and hour figures must link to the confirmed pricing system or a
  versioned local estimate with its inputs, formulas, and assumptions. Hub
  records reference that source; they do not become a second pricing authority.
  Client-stated figures remain attributed to their source IDs.

## The index

`AGENTS.md` at the hub root carries: a dated current-direction block, a numbered
reading order, the file index, an archive table with a why-archived column, and
the session-start instruction to run `audit`. `CLAUDE.md` holds one line,
`@AGENTS.md`. A hub untouched for 60 days gets a dormancy line naming the
outcome.
