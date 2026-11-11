# Payloads & Response Shapes

Exact tool payloads and response shapes for the Aleysian Pricing System scoping tools.
If anything here disagrees with live behavior, trust live behavior and tell the user.

---

## Rate Card: Product Codes, IDs, Rates

You normally only need the **productCode**; the server derives IDs and rates. The ID
columns are here for ad-hoc SOQL. Rates shown are catalog; a quote's `quotedBillRate`
may differ when discounted.

| Code | Role | product2Id | pricebookEntryId | Bill | Cost | Min h/wk | Interval |
|------|------|------------|------------------|------|------|----------|----------|
| SA | Solution Architect | 01t3h000002SuijAAC | 01u3h000001lCpWAAU | 230 | 119 | 10 | 10 |
| SSA | Sr Solution Architect | 01tTP000002dOkTYAU | 01uTP000000RWTdYAO | 300 | 182 | 5 | 5 |
| BA | Business Analyst | 01t3h000002SuikAAC | 01u3h000001lCopAAE | 150 | 66 | 20 | 20 |
| SBA | Sr Business Analyst | 01t3h000002SuioAAC | 01u3h000001lCpaAAE | 185 | 94 | 20 | 10 |
| NBA | Business Analyst (Nearshore) | 01tTP00000Iep6HYAR | 01uTP0000043tnFYAQ | 80 | 35 | 20 | 20 |
| NSSBA | Sr Business Analyst (Nearshore) | 01tTP00000Iep1RYAR | 01uTP0000043tldYAA | 90 | 45 | 20 | 10 |
| TA | Technical Architect | 01t3h000002SuiiAAC | 01u3h000001lCpcAAE | 230 | 119 | 10 | 10 |
| STA | Sr Technical Architect | 01t3h000002SuiwAAC | 01u3h000001lCpVAAU | 300 | 182 | 5 | 5 |
| DEV | Developer | 01t3h000002SuisAAC | 01u3h000001lCosAAE | 150 | 66 | 20 | 20 |
| SD | Sr Developer | 01t3h000002SuitAAC | 01u3h000001lCpbAAE | 185 | 94 | 20 | 10 |
| NDEV | Developer (Nearshore) | 01tTP00000I8zggYAB | 01uTP000003vEPVYA2 | 80 | 40 | 20 | 20 |
| NSDEV | Sr Developer (Nearshore) | 01tTP00000I90MbYAJ | 01uTP000003vEPWYA2 | 100 | 50 | 20 | 10 |
| QA | Quality Assurance | 01tTP00000JctbeYAB | 01uTP000004KVwgYAG | 150 | 66 | 10 | 10 |
| SQA | Sr Quality Assurance | 01tTP00000JctbfYAB | 01uTP000004KVwhYAG | 230 | 119 | 10 | 10 |
| QAN | Quality Assurance (Nearshore) | 01tTP00000IO80TYAT | 01uTP000003zZNJYA2 | 70 | 30 | 10 | 10 |
| PM | Program Manager | 01t3h000002SuipAAC | 01u3h000001lCpZAAU | 185 | 94 | 10 | 10 |
| SPM | Sr Program Manager | 01tTP000002mOi1YAE | 01uTP000000UW45YAG | 230 | 119 | 5 | 5 |
| CSE | Client Services Executive | 01tTP00000I90pdYAB | 01uTP000003vEirYAE | 350 | 182 | 5 | 5 |
| DA | Data Architect | 01t3h000002SuiqAAC | 01u3h000001lCoqAAE | 185 | 94 | 5 | 5 |
| DS | Data Specialist | 01t3h000002SuinAAC | 01u3h000001lCorAAE | 150 | 66 | 10 | 10 |
| EXA | Executive Advisor | 01t3h000002SuimAAC | 01u3h000001lCpUAAU | 400 | 197.1 | 5 | 5 |
| SME | Solution SME | 01tTP00000JctbgYAB | 01uTP000004KVwiYAG | 400 | 197.1 | 5 | 5 |
| CMA | Change Management Consultant | 01tTP00000I90zJYAR | 01uTP000003vEpJYAU | 185 | 94 | 10 | 10 |
| CML | Change Management Lead | 01tTP00000JctbdYAB | 01uTP000004KVwfYAG | 230 | 119 | 10 | 10 |
| ET | Education Trainer | 01t3h000002SuiuAAC | 01u3h000001lCpSAAU | 185 | 94 | 10 | 10 |
| EDA | Education Architect | 01t3h000002SuivAAC | 01u3h000001lCpXAAU | 230 | 119 | 5 | 5 |
| ECD | Education Curriculum Developer | 01t3h000002SuirAAC | 01u3h000001lCpYAAU | 150 | 66 | 10 | 10 |

Indirect-labor roles: CSE, PM, SPM, EXA, SME, ET, EDA.

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
  sentence header, then markdown bullets: active-voiced, verb-led, no em-dashes (see
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
- [ ] Hours respect each role's min/interval (rate card above)
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

Phase-group split for estimation (standard PDT 30/40/20/10): Discovery
(Mobilize+Analyze+Design) 30% / Build 40% / Validate 20% / Finalize (Training+Deploy)
10%. Support is additive when quoted.

---

# Response Shapes

## scoping_get_quote (key fields)

```json
{
  "success": true,
  "totalBuPrice": 163273.75,
  "timelineRevenue": 87900,
  "txpotAvailable": true,
  "scopeItems": [
    {
      "id": "a3zTP000005SXPZYA4",
      "externalId": "q-000003_data_discovery__org_field_audit",
      "name": "Data Discovery & Org Field Audit",
      "skillName": "Data Quality & Deduplication",
      "skillId": "a3hTP000001NxZsYAK",
      "phase": "Phase 1",
      "tags": "direct,data-audit",
      "isActive": true,
      "displayOrder": 10,
      "description": "<p>HTML</p>",
      "assumptions": "<p>HTML</p>",
      "buPrice": 2246.25,
      "pot": 0.0137575697,
      "txpot": 1209.29
    }
  ],
  "scopeItemResources": [
    {
      "id": "a3yTP000007vcPlYAI",
      "externalId": "q-000003_gps_geolocation_capture_sa",
      "scopeItemExternalId": "q-000003_gps_geolocation_capture",
      "productCode": "SA",
      "requirementsDesignHours": 0.5,
      "buildHours": 0.75,
      "validateHours": 0.5,
      "trainDeployHours": 0.25
    }
  ],
  "quoteResources": [
    {
      "id": "a3sTP00000ogB0kYAE",
      "productId": "01t3h000002SuijAAC",
      "productCode": "SA",
      "productName": "Solution Architect",
      "titleLevel": "Principal Consultant",
      "catalogBillRate": 230,
      "quotedBillRate": 230,
      "costRate": 119,
      "totalHours": 147.5,
      "isPartnerResource": false,
      "displayOrder": 10
    }
  ],
  "productConfig": {
    "products": [
      {
        "id": "01t3h000002SuikAAC",
        "productCode": "BA",
        "name": "Business Analyst",
        "billRate": 150,
        "costRate": 66,
        "minHoursPerWeek": 20,
        "hoursPerWeekInterval": 20,
        "isIndirectLabor": false,
        "defaultTitleLevel": "Consultant"
      }
    ]
  },
  "phaseComparison": {
    "available": true,
    "categories": [
      { "name": "Discovery", "buHours": 100, "timelineHours": 130, "diff": 30, "diffPercent": 30.0 }
    ],
    "totalBuHours": 380, "totalTimelineHours": 360,
    "totalDiff": -20, "totalDiffPercent": -5.3
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
