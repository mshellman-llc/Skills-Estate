# proposal.json - the data contract

Assemble this before writing any HTML. The page renders this file. A field that is not in the
source is not on the page; note the gap and keep moving.

## Proposal mode

```json
{
  "meta": {
    "quote_number": "Q-000043",
    "client": "Example Manufacturing",
    "opportunity": "Service Cloud implementation",
    "prepared_by": "Example Delivery Team",
    "date": "2026-07-19",
    "currency": "USD",
    "validity": "Pricing valid 30 days from date above",
    "mode": "proposal"
  },
  "versions": [
    {
      "key": "A",
      "name": "Foundation",
      "tagline": "Core Service Cloud, live in 12 weeks",
      "total": 184500,
      "duration_weeks": 12,
      "scope_sections": [
        { "title": "Case Management", "items": [
          { "name": "Omni-channel routing", "description": "..." } ] }
      ],
      "team": [ { "role": "Solution Architect", "allocation": "50%" } ],
      "timeline": [ { "phase": "Discover", "weeks": "1-2" } ],
      "assumptions": [ "Volumetrics per Exhibit A basis of estimate" ],
      "not_included": [
        { "item": "CTI integration", "route": "Available as a scoped add-on" } ]
    }
  ],
  "next_steps": [ "Scope review call", "SOW signature", "Kickoff" ],
  "audit": [
    { "displayed": "184500", "source": "Q-000043 version A total" },
    { "displayed": "12 weeks", "source": "Q-000043 version A timeline" }
  ]
}
```

## Explorer mode

Same shape, four changes:

- `meta.mode` is `"explorer"`. `meta.quote_number` states the absence plainly, for example
  `"No quote on record"`. `meta.currency` is omitted.
- `meta.validity` describes what the page is, not how long a price lasts. For example:
  `"Scope explorer. No pricing appears on this page."`
- `total` and `duration_weeks` are replaced by `metric` and `metric_label`, which carry a
  computable count and its unit. For example `35` and `"of 35 requirements"`. The count must be
  reproducible by anyone holding the same source documents. Assert it in the build script.
- `team` and `timeline` are omitted. Add a single `phase_zero` block naming the paid next step
  that produces them, with its outputs.

Each scope item carries the version keys that include it and its source, so the page can render
excluded items rather than hide them:

```json
{ "name": "Selective line retention", "description": "...",
  "versions": "BC", "id": "R2", "source": "requirements" }
```

## Rules

- **versions.** Proposal mode takes them from the quote's actual versions or options. Explorer
  mode takes them from the client's own open scope decisions. Neither mode invents a
  good/better/best split, and neither uses internal low, expected, and high estimate bands.
- **total** is the quote value verbatim: no rounding for effect, no "from $X", no financing math.
- **metric** is a count from a source document, not a derived or weighted score.
- **audit.** One row per number visible on the page, plus one row for each number deliberately
  absent and why. Surface it behind a sources disclosure on the page itself so anyone can trace a
  figure in seconds. In explorer mode the audit table is the credibility of the page, so put the
  counting method in it.
- **assumptions** carry the basis-of-estimate items that protect the price. If the quote has
  Exhibit A volumetrics, surface the load-bearing ones. A prospect who saw the assumption cannot
  dispute the change order.
- **not_included** entries always carry a route. Every boundary is a doorway.
- **Scope language** is authored by the scoping process, not by this skill. Tighten grammar, never
  meaning.

## Sourcing order

1. Scoping MCP live quote. Preferred. Note the retrieval in the audit table.
2. A quote export the user provides: JSON, xlsx, or the SOW or DDOC built from the same quote.
3. No quote. You are in explorer mode. Source from the client's requirements documents and any
   source material they sent, name each document in the audit table with its modified date, and
   run no currency on the page.

A ROM or playbook-derived estimate is not a source under any of the three. It is an internal
calibration figure and it does not reach a client-facing surface.

## Tie-out, proposal mode only

Reconcile every figure on the rendered page against the quote export before shipping:

```bash
python3 ../prose-pass/scripts/rewrite_scan.py --tie-out quote_export.json page.html
```

A figure on the page that is not in the source is invention and a hard fail. A source figure
missing from the page is a warning: confirm the omission was a choice.

## Packaged builder schema

The examples above describe the source mapping. The executable schema is demonstrated by `../fixtures/proposal.json` and `../fixtures/explorer.json`. It requires source records (`id`, `title`, `reference`, `revision`), stable scope item IDs, each item's source ID, and each version's source ID. Scope sections list the included items for that version. Excluded items remain visible with a route.

`--quote` supplies a separate source export with `quote_number`, `currency`, and `versions`. Names, taglines, totals, durations, teams, timelines, scope, assumptions, and boundaries must match the source export exactly. Explorer input has no currency, price, staffing, or duration fields; its metric must match the distinct included scope IDs.

The rendered source disclosure identifies source revisions and the current option's figure fields. Additional numbers in authored descriptions still need source review; automatic field parity is not a semantic review of all prose.
