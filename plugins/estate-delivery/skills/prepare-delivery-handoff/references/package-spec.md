# Package spec: the manifest, the moments, the transfer

## One schema, two moments

The manifest is a JSON file that is the artifact's substrate. The rendered HTML or
Markdown is a projection of it. Both moments use the same schema; a `moment` field
tells the gate which completion standard to apply.

- `"moment": "package"`: assembled at signature. All 12 sections present and
  non-blank. Sections 11 and 12 may still be seeded with gaps (owned open
  questions), because the incoming team has not yet shaped its week one.
- `"moment": "brief"`: at delivery acceptance. Everything the package requires,
  plus section 11 filled with concrete sessions and section 12 filled with
  binary criteria. This is the strict default: an omitted `moment` field is
  treated as `brief`.

Never fork the schema. The delivery brief is produced by completing the package
manifest in place, so nothing is re-keyed, re-mapped, or lost at the seam.

## Manifest schema

```json
{
  "client": "string, required",
  "engagement": "string, required",
  "moment": "package | brief (default brief)",
  "as_of": "YYYY-MM-DD, required",
  "source_snapshot": {
    "write-statement-of-work": "identifier of the executed SOW, required",
    "quote": "Q-number, required"
  },
  "sections": {
    "01": {
      "title": "The engagement",
      "content": ["sourced statements, one per entry"],
      "sources": [{"name": "SOW section 2", "date": "2026-08-01"}],
      "gaps": [
        {
          "question": "what is unknown",
          "owner": "role or name",
          "resolve_by": "YYYY-MM-DD",
          "gate_blocked": "which gate this blocks, e.g. kickoff"
        }
      ]
    },
    "...": "sections 02 through 10 use the same shape",
    "11": {
      "title": "Discovery sessions",
      "sessions": [
        {
          "name": "session title",
          "owner": "named owner",
          "attendees": ["who must be in the room"],
          "output": "the concrete artifact or confirmation that closes the question",
          "closes": "optional: the gap or ledger claim ID this session closes"
        }
      ],
      "sources": [...], "gaps": [...]
    },
    "12": {
      "title": "What good looks like",
      "criteria": [
        {
          "criterion": "the observable behavior",
          "binary_test": "how a reviewer decides yes or no",
          "ladders_to": "optional: the section 01 outcome it supports"
        }
      ],
      "readiness": [
        {"item": "checklist item", "status": "ready | blocked | unknown", "owner": "who clears it"}
      ],
      "sources": [...], "gaps": [...]
    }
  },
  "scope": [
    {"item": "scope line", "in_or_out": "in | out", "source": "SOW clause or quote line"}
  ],
  "promises": [
    {
      "text": "what was said",
      "said_where": "transcript, thread, or email with date",
      "by": "who said it",
      "in_sow": true,
      "sow_clause": "required when in_sow is true",
      "owner": "required when in_sow is false"
    }
  ],
  "figures": [
    {"label": "total fee", "value": "as it appears in the source", "source": "executed SOW section 4 / Q-000123 field"}
  ]
}
```

Rules the gate enforces (see `scripts/check_handoff.py` for the authoritative
list):

- Sections 01 through 12 all present, no extras. A section passes by content
  (non-empty `content` plus non-empty `sources`, each source carrying name and
  date) or by gaps (each gap carrying question, owner, resolve_by, gate_blocked).
  Blank fails.
- At moment `brief`, section 11 needs at least one session with name, owner,
  attendees, and output; section 12 needs at least one criterion with a binary
  test. Gaps alone do not satisfy 11 or 12 at this moment.
- Every scope item is marked `in` or `out`. An empty scope list fails.
- Every promise names where it was said. `in_sow: true` requires the clause;
  `in_sow: false` requires an owner.
- Every figure's source must reference the SOW or the quote (the money rule).
  Figures sourced anywhere else fail.
- No em dash anywhere in the manifest.

The gate checks structure and traceability. It does not check truth; that is
evidence-core's job upstream, and the reason the manifest is built from the
ledger rather than from memory.

## The warm transfer (moment 1)

The package is not an email attachment. The SSL walks it to the Program Lead and
Solution Lead in a recorded session; the Pursuit Lead and delivery lead accept it
there. Record and transcribe the session, then ingest the transcript: answers
given in the room close gap entries (update owner and status in the manifest),
and new facts enter the ledger with the transcript as source. The handoff gate in
the sales lifecycle is not cleared by generating the package; humans clear gates.

## Seeding the delivery record

The accepted manifest seeds the engagement record the delivery side runs on:
scope maps to the scope baseline, section 09 to stakeholders, section 06 to
decisions, gap entries to open questions (owner, resolve_by, gate carried over
verbatim), maturity-gap tags to confidence tags, and the SOW's phase exit
conditions to gates. Because the package and the brief share one schema, this
seeding is a copy, not a translation; that is the point of the consolidation.

## State discipline

- Stamp every render with client, engagement, `as_of`, and the `source_snapshot`.
  Q-numbers and record IDs are not durable anchors across sandbox refreshes; the
  stamp is what lets a reader judge staleness.
- Truth hierarchy when re-opening a handoff: live SOW and quote, then the
  manifest, then memory, then chat context.
- Fix the manifest and re-render; never hand-patch a rendered brief, or the next
  regenerate drops the fix.
