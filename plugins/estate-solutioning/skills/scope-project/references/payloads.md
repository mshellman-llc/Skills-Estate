# Payloads & Response Shapes

Historical payload contract for an optional custom pricing adapter. Confirm the current project schema before using it. The examples explain fields; they do not establish an installed tool, approved rate or authorized target.

---

## Project rate card

Load role codes and rates from the confirmed project configuration. Product and
pricebook-entry IDs belong to the current target org. No catalog rates or IDs
are embedded here. Keep cost rates private. Read quoted billing rates separately
from list rates when discounts apply.

The adapter needs productCode and the corresponding role metadata. Staffing
checks also need minHoursPerWeek and hoursPerWeekInterval. Select indirect
labor roles from the current preset rather than an inherited role list.

Re-check rates/IDs anytime:

```
salesforce_query_records:
  objectName: "PricebookEntry"
  fields: ["Id", "Product2Id", "Product2.Name", "Product2.ProductCode", "UnitPrice"]
  whereClause: "Pricebook2.Name = 'Professional Services' AND IsActive = true"
```

Per-quote values: `scoping_get_quote` with `include: ["resources", "products"]`.
`quoteResources[].productId` is the product2Id and `quotedBillRate` reflects discounts.

---

## Scope Items: Upsert

```
scoping_manage_scope_items:
  quoteId: "a3tXXX"
  operation: "upsert_items"
  scopeItems: [
    {
      "name": "Lead Assignment Rules",
      "description": "Automated lead routing for territory and round-robin assignment.\n- Configure assignment rules for territory, round-robin, and lead source criteria\n- Define fallback queue routing for leads that match no rule",
      "assumptions": "- Territory model is defined and current in Salesforce\n- Lead source values are standardized before build",
      "skillName": "Lead Management",
      "skillParentName": "Sales Cloud",
      "phase": "Phase 1",
      "tags": ["direct", "rfp-section-2"]
    }
  ]
```

- `name` is the upsert key: same name + same quote = update, not duplicate
- **Always include `skillName`**; omitting it clears the capability
- `description` and `assumptions` are auto-converted to rich-text HTML. Write a 1-3
  sentence header, then markdown bullets: specific and consistent with review-writing (see
  "Writing scope descriptions and assumptions" in SKILL.md)
- `tags` must already exist in the quote's tag catalog (create tags first)
- Deactivate: `{ "name": "...", "isActive": false, "skillName": "..." }`

Delete by external ID:

```
scoping_manage_scope_items:
  quoteId: "a3tXXX"
  operation: "delete_items"
  externalIds: ["q-000003_lead_assignment_rules"]
```

Master-detail children (scope item resources) cascade. Always read external IDs from
`scoping_get_quote`; never construct them.

## Scope Item Resources (hours)

```
scoping_manage_scope_items:
  quoteId: "a3tXXX"
  operation: "upsert_resources"
  scopeItemResources: [
    {
      "scopeItemExternalId": "q-000003_lead_assignment_rules",
      "productCode": "SA",
      "requirementsDesignHours": 4,
      "buildHours": 16,
      "validateHours": 4,
      "trainDeployHours": 2
    }
  ]
```

- Get `scopeItemExternalId` from `scoping_get_quote` after pushing items. Fractional
  hours (0.25 granularity) are valid.
- The `productCode` must already exist as a quote resource on the quote, or the call
  no-ops while reporting success; add the resource column first
  (`scoping_manage_quote_resources` `add`) and verify with `scoping_get_quote`.

## Tags

```
# Non-destructive merge: adds without disturbing existing tags
scoping_manage_tags:
  quoteId: "a3tXXX"
  operation: "merge"
  tags: [
    { "name": "direct", "color": "#2e844a" },
    { "name": "implied", "color": "#0070d2" },
    { "name": "inferred", "color": "#ff9e2c" }
  ]

# save REPLACES the entire catalog: only for a deliberate full overwrite; get first
scoping_manage_tags: { quoteId, operation: "get" }
scoping_manage_tags: { quoteId, operation: "save", tags: [ ...existing + new... ] }
```

---

# Timeline Snapshots

The contract is **derive, don't require**: express intent (who, how much, which weeks,
what phases) and the server hydrates IDs, pricing, linkage, and metadata.

## Minimal write contract

```json
{
  "timelines": [
    {
      "name": "Primary Timeline",
      "startDate": "2026-07-06",
      "weekCount": 8,
      "calendarStartWeek": 1,
      "displayOrder": 1,
      "phases": [
        { "name": "Mobilize / Analyze", "startWeek": 1, "endWeek": 1 },
        { "name": "Analyze / Design", "startWeek": 2, "endWeek": 2 },
        { "name": "Build", "startWeek": 3, "endWeek": 5 },
        { "name": "Validate", "startWeek": 6, "endWeek": 7 },
        { "name": "Deploy", "startWeek": 8, "endWeek": 8 }
      ],
      "quoteLineItems": [
        { "productCode": "SA", "titleLevel": "Principal Consultant" },
        { "productCode": "BA", "titleLevel": "Consultant" }
      ],
      "schedules": [
        { "productCode": "SA", "weeks": "1-2", "hours": 20 },
        { "productCode": "SA", "weeks": "3-8", "hours": 10 },
        { "productCode": "BA", "weeks": "1-8", "hours": 40 }
      ]
    }
  ]
}
```

Save:

```
scoping_manage_timeline:
  quoteId: "a3tXXX"
  operation: "save"
  name: "Initial Staffing Plan"
  snapshotJSON: { ...above... }
```

**Server derives:** product2Id, pricebookEntryId, unit/list/bill rates, costRate,
rowKey UUIDs, schedule↔QLI linkage, quantity, per-timeline and global metadata, and
timeline defaults (color, calendarStartWeek, displayOrder). Set `startDate`,
`weekCount`, and `name` explicitly when you know them.

**Schedule input uses week ranges.** `weeks` is a range string (`"1-8"`) or a single
week (`"3"`). Per-week `{ productCode, weekNumber, hours }` is also accepted and
collapsed into ranges on save. Quantity = Σ(hours × weeks in range), so SA at
`"1-2"`@20 + `"3-8"`@10 → quantity 100.

**Two FTE instances of one role:** two QLI entries with the same `productCode`,
distinguished by instance; check how a saved snapshot represents them and follow that.

## Preflight checklist

- [ ] `phases` are contiguous, non-overlapping, cover weeks 1..weekCount, and use
      valid phase names (list below)
- [ ] Every schedule's `productCode` has a matching `quoteLineItems` entry
- [ ] Schedules use `weeks` ranges, hours > 0 (zero-hour entries are stripped)
- [ ] Resource continuity: no week gaps between a resource's first and last week
- [ ] Hours respect each role's configured minimum and interval
- [ ] Each `productCode` exists as a quote resource on this quote
- [ ] After save: read back and surface any `validations` with ERROR severity

## Reading snapshots

Reads return compact schedules `{ rowKey, weeks, hours }`. Derive the rest:

| Need | Derivation |
|------|-----------|
| phase for a week | look up the week in `phases` (startWeek ≤ w ≤ endWeek) |
| resource name | `rowKey` → `quoteLineItems[].rowKey` → `productName` |
| scheduleDate | `timeline.startDate` + (weekNumber − 1) × 7 days |
| calendarWeek | `timeline.calendarStartWeek` + weekNumber − 1 |

A read QLI carries `productCode`, `product2Id`, `product2Name`, `product2Code`,
`resourceType`, `pricebookEntryId`, `listPrice`, `unitPrice`, `billRate`, `costRate`,
`titleLevel`, `rowKey`, `quantity`. Snapshot `totalRevenue`/`totalCost` populate once
the snapshot is activated. (Older snapshots may read back in an expanded, per-week
shape, which is fine; the derivations above still apply.)

## Multi-band

One `timelines[]` entry per band. Bands position on the calendar via `calendarStartWeek`
+ `weekCount`; `phases` and week numbers are band-relative. Resources belong to exactly
one band.

```json
{
  "timelines": [
    {
      "name": "Project Oversight",
      "startDate": "2026-07-06",
      "weekCount": 31,
      "calendarStartWeek": 1,
      "displayOrder": 1,
      "phases": [ { "name": "Support", "startWeek": 1, "endWeek": 31 } ],
      "quoteLineItems": [ { "productCode": "PM", "titleLevel": "Sr Consultant" } ],
      "schedules": [ { "productCode": "PM", "weeks": "1-31", "hours": 10 } ]
    },
    {
      "name": "Phase 1",
      "startDate": "2026-07-06",
      "weekCount": 22,
      "calendarStartWeek": 1,
      "displayOrder": 2,
      "phases": [
        { "name": "Mobilize", "startWeek": 1, "endWeek": 1 },
        { "name": "Analyze", "startWeek": 2, "endWeek": 4 },
        { "name": "Design", "startWeek": 5, "endWeek": 7 },
        { "name": "Build", "startWeek": 8, "endWeek": 15 },
        { "name": "Validate", "startWeek": 16, "endWeek": 19 },
        { "name": "Training", "startWeek": 20, "endWeek": 20 },
        { "name": "Deploy", "startWeek": 21, "endWeek": 22 }
      ],
      "quoteLineItems": [ /* productCode + titleLevel */ ],
      "schedules": [ /* productCode, weeks ranges, hours */ ]
    },
    {
      "name": "Phase 2",
      "startDate": "2026-12-07",
      "weekCount": 9,
      "calendarStartWeek": 23,
      "displayOrder": 3,
      "phases": [ /* band-relative weeks 1-9 */ ],
      "quoteLineItems": [],
      "schedules": []
    }
  ]
}
```

Later band `startDate` = global start + 7 × (calendarStartWeek − 1) days.

## Generate, Activate

```
scoping_manage_timeline: { quoteId, operation: "generate", preview: true,
                           weekCount: 12, startDate: "2026-07-06" }
scoping_manage_timeline: { quoteId, operation: "activate", snapshotId: "..." }
```

Generate notes:
- It may emit macro phase names ("Requirements & Design", "Train & Deploy") that aren't
  valid CMDT phases; re-phase with valid names (below) before saving.
- It computes duration from BU hours and may override your `weekCount`; check the
  returned value.
- It may leave continuity gaps at phase transitions; fill them.

Activation drives quote financials (revenue/cost/margin roll up to the snapshot) and
triggers async hydration of line items; always tell the user which snapshot is active,
with a link.

## Valid Phase Names

Main phases, in order: `Mobilize`, `Analyze`, `Design`, `Build`, `Validate`,
`Training`, `Deploy`, `Support`. Transition phases (single-week boundaries, never two
in a row): `Mobilize / Analyze`, `Analyze / Design`, `Design / Build`,
`Build / Validate`, `Validate / Training`, `Validate / Deploy`, `Training / Deploy`,
`Deploy / Support`.

Use the phase-group split supplied by the current project preset. Support is additive only when the scope or quote includes it. No percentage allocation is a default in this estate.

---

# Response Shapes

The response example uses fictional rates and quantities. Its placeholder IDs are not valid mutation targets. Obtain every commercial value and record ID from the current project source.

## scoping_get_quote (key fields)

```json
{
  "success": true,
  "totalBuPrice": 200,
  "timelineRevenue": 200,
  "txpotAvailable": true,
  "scopeItems": [
    {
      "id": "example-scope-item",
      "externalId": "example-import",
      "name": "Example import",
      "skillName": "Data Quality & Deduplication",
      "skillId": "example-capability",
      "phase": "Phase 1",
      "tags": "direct,data-audit",
      "isActive": true,
      "displayOrder": 10,
      "description": "<p>HTML</p>",
      "assumptions": "<p>HTML</p>",
      "buPrice": 200,
      "pot": 1,
      "txpot": 200
    }
  ],
  "scopeItemResources": [
    {
      "id": "example-allocation",
      "externalId": "example-import-role",
      "scopeItemExternalId": "example-import",
      "productCode": "SA",
      "requirementsDesignHours": 0.5,
      "buildHours": 0.75,
      "validateHours": 0.5,
      "trainDeployHours": 0.25
    }
  ],
  "quoteResources": [
    {
      "id": "example-resource",
      "productId": "example-product",
      "productCode": "SA",
      "productName": "Solution Architect",
      "titleLevel": "Principal Consultant",
      "catalogBillRate": 100,
      "quotedBillRate": 100,
      "costRate": 50,
      "totalHours": 2,
      "isPartnerResource": false,
      "displayOrder": 10
    }
  ],
  "productConfig": {
    "products": [
      {
        "id": "example-product-2",
        "productCode": "BA",
        "name": "Business Analyst",
        "billRate": 100,
        "costRate": 50,
        "minHoursPerWeek": 10,
        "hoursPerWeekInterval": 5,
        "isIndirectLabor": false,
        "defaultTitleLevel": "Consultant"
      }
    ]
  },
  "phaseComparison": {
    "available": true,
    "categories": [
      {
        "name": "Discovery",
        "buHours": 0.5,
        "timelineHours": 0.5,
        "diff": 0,
        "diffPercent": 0
      }
    ],
    "totalBuHours": 2,
    "totalTimelineHours": 2,
    "totalDiff": 0,
    "totalDiffPercent": 0
  }
}
```

Notes: `tags` is a comma-separated string. `txpot` = per-item client-facing dollar
value (BU weight × timeline revenue). `quoteResources` requires `include: ["resources"]`;
`productConfig` requires `include: ["products"]`. On quotes with many items the response
can be large; fetch only the `include` data you need. Always read external IDs from the
response; never construct them.

## scoping_manage_timeline (get)

Returns `snapshot` metadata (id, name, totalHours, totalRevenue, totalCost,
resourceCount, weeks, isApproved, isActive) plus `snapshotJSON` (compact) and a
`validations` array; surface ERROR-severity validations to the user (min-hours
violations, staffing increments, BU variance thresholds: under by 5%/15% = warn/error,
over by 20%/35% = warn/error).

## scoping_get_skills

```json
[
  {
    "id": "a3hXXX",
    "name": "Lead Management",
    "level": 3,
    "parentSkillName": "Sales Cloud",
    "grandparentSkillName": "CRM"
  }
]
```

Level 3 = leaf; scope items use level-3 names. Capabilities may carry pricing stats
(median, IQR, min/max, `pricingStatsConfidence`); use for hour calibration.

## scoping_get_team_presets

Presets carry `resources` (`productCode`, `titleLevel`, `isIndirect`), `leveragePairs`
(`seniorCode`, `juniorCode`, `rdRatio`, `buildRatio`, `validateRatio`,
`trainDeployRatio`), and `indirectRules` (`resourceTypeCode`, per-phase percents,
`calculationScope`). Pass the preset `id` as `teamPresetId` to `scoping_create_quote`
to auto-provision resources, pairs, and rules.

Leverage math (the API stores exact hours; you compute): junior phase hours = senior
phase hours × phase ratio; indirect phase hours = direct phase total × percent / 100.
Ratios are guidelines; deviations are fine.
