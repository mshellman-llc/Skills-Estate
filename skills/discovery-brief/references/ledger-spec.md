# The two-column ledger: field spec and formats

The ledger is the substrate. The brief is a projection of it. Build and gate the ledger before writing prose; `scripts/check_brief.py` validates both representations below and blocks on any violation.

## Column A: what we know

Every fact the brief will assert.

| Field | Holds | Rules |
| --- | --- | --- |
| claim | The fact, number, system, or person. | Concrete and specific. No "the platform", "various requirements". |
| source | Named source with a date. | "RFP §2.4, 2026-05-02", "SF Opportunity competitors, pulled 2026-08-10", "workshop transcript 2026-03-18". Multiple sources comma-separated. Never empty. A claim with no source does not enter Column A. |
| confidence | Confirmed or Inferred. | Confirmed: an authoritative source (RFP, system-of-record field, signed document) or two corroborating sources. Inferred: single-source or reasoned; the brief states it as inference with its basis. Unknown is not a Column A value; a searched-for fact not found becomes a Column B entry. Contested (sources disagree) keeps both values in the claim text with the divergence flagged, and stays Inferred until resolved. |
| as_of | Date of the most recent source. | Staleness is visible, not hidden. |

## Column B: the open questions

The spine. Rank order is call order.

| Field | Holds | Rules |
| --- | --- | --- |
| id | Q-01, Q-02, ... zero-padded. | Stable across sessions; a closed question's id is retired, not reused. |
| question | The thing to ask, phrased as it would be asked. | Short, direct, answerable in the room. |
| why_open | What was searched and not found. | Proof the record was checked before the room gets asked. |
| unblocks | The scope line or capability code the answer shapes. | Never empty. This is the cut test in field form: no scope line, no question. |
| rank | High, Medium, or Low scoping impact. | High: blocks a workstream from being sized, swings a wide cost band, or gates a phase. Medium: changes effort within a sizeable workstream. Low: refines at the margins. |

Set rank deliberately: trace the question to its scope line and ask "if this answer flips, how much does the number move?" Ties break by what gates other work. Entries must appear in rank order, High before Medium before Low; the gate enforces the ordering.

## JSON representation

The working format. One file per session brief.

```json
{
  "meta": {
    "client": "Acme Industrial",
    "opportunity": "Acme CPQ remediation",
    "call": "Scoping session 2, 2026-08-14",
    "as_of": "2026-08-11"
  },
  "known": [
    {
      "claim": "Twelve NOW-priority requirements in the RFP; nine map to the core pattern, three are net-new",
      "source": "RFP §3, 2026-05-02; capability-response sheet, 2026-06-20",
      "confidence": "Confirmed",
      "as_of": "2026-06-20"
    },
    {
      "claim": "The billing integration looks reusable from the prior phase",
      "source": "workshop transcript 2026-03-18",
      "confidence": "Inferred",
      "as_of": "2026-03-18"
    }
  ],
  "open": [
    {
      "id": "Q-01",
      "question": "Does order management stay on the incumbent OMS or move to the new platform?",
      "why_open": "RFP names both systems without a disposition; March workshop deferred to the technical session",
      "unblocks": "ORD workstream scope lines",
      "rank": "High"
    },
    {
      "id": "Q-02",
      "question": "How many discount approval tiers exist today, and who owns each?",
      "why_open": "Scoring sheet marks approvals partially capable; tier count appears nowhere in the record",
      "unblocks": "CPQ approval-workflow line",
      "rank": "Medium"
    }
  ]
}
```

Required keys: `known` (list, may be empty for a greenfield deal) and `open` (list, normally non-empty). A completed JSON discovery record may use `open: []` only with the Boolean `discovery_complete: true`; strings such as `"true"` do not grant completion. Preserve answered questions, retired IDs and their evidence in the record history. Do not set completion merely to bypass missing answers or evidence. `meta` is recommended and carries the stamp.

## Markdown representation

The projected brief embeds the ledger in two gated blocks. The gate finds each by heading text and parses the first table under it.

**Column A**: a heading containing "column a" or "what we know" (case-insensitive), followed by a table whose header row includes `Claim`, `Source`, and `Confidence` (an `As-of` column is recommended). Every data row needs a non-empty source cell and a confidence of Confirmed or Inferred.

**Column B**: a heading containing "column b", "open questions", or "ranked unknowns", followed by a table whose header row includes `Question`, `Rank`, and `Unblocks` (`ID` and `Why open` columns are recommended). Every data row needs a valid rank and a non-empty unblocks cell, and rows must run High before Medium before Low.

```markdown
## Column A: what we know

| Claim | Source | Confidence | As-of |
| --- | --- | --- | --- |
| Twelve NOW requirements; nine core, three net-new | RFP §3, 2026-05-02; scoring sheet 2026-06-20 | Confirmed | 2026-06-20 |

## Column B: ranked unknowns

| ID | Question | Rank | Unblocks | Why open |
| --- | --- | --- | --- | --- |
| Q-01 | OMS stays or moves? | High | ORD workstream | RFP names both, workshop deferred |
```

The full brief renders each Column B row as a question block in section 02, with the rank, the scope lever ("don't size the ORD lines until Q-01 is answered"), and the why-open reasoning. The table is the gated record; the blocks are its projection.

## What the gate checks

1. Every Column A entry has a non-empty source.
2. No Column A entry carries confidence Unknown, and every confidence is Confirmed or Inferred.
3. Column B is non-empty unless a JSON record explicitly declares `discovery_complete: true`. The Markdown projection has no equivalent completion switch.
4. Every Column B entry has a non-empty question, a rank of High, Medium, or Low, and a non-empty unblocks value.
5. Column B entries appear in rank order.
6. JSON rows are objects and required text fields contain strings. Punctuation alone does not fail this evidence gate; exact source quotations retain their punctuation.

A structural gate failure blocks release. Correct the ledger and re-project. Passing the script does not establish source authority, factual accuracy, scope approval or completion of unanswered work; those require evidence review.
