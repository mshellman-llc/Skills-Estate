# Optional custom CRM scoping adapter

Use this adapter only when the current project exposes these custom tools.
Their names do not establish an installed integration or a live connection.
The portable scope-project workflow owns scope reasoning and estimates.
Use its local model when the integration is absent.

Confirm the target org and its current quote schema before mutation. Derive
links from the actual instance URL or returned record URL; this estate supplies
no production domain or record IDs. Keep rate cards and endpoint configuration
in the private project, outside this reusable module.

Only write within the user's requested action. A draft scope does not require
creating a CRM record. Team membership changes and timeline activation each
need authorization for the actual operation. Read back every accepted change.

## Tools

MCP scoping tools (prefix `scoping_`) plus generic Salesforce tools (prefix `salesforce_`),
all on the same connector:

| Tool | Purpose |
|------|---------|
| `scoping_get_quote` | Fetch scope items, resources, products, tags |
| `scoping_get_skills` | Capability taxonomy + pricing stats |
| `scoping_get_team_presets` | Team presets with leverage/indirect rules |
| `scoping_get_sow_data` | Pre-assembled SOW payload |
| `scoping_create_quote` | Create quote with optional team preset |
| `scoping_manage_scope_items` | CRUD scope items + hour allocations |
| `scoping_manage_tags` | Tag catalog management |
| `scoping_manage_timeline` | Timeline snapshots (list/get/save/generate/activate/clone) |
| `scoping_manage_quote_resources` | Quote resource columns (add/list/delete/swap) |
| `scoping_join_team` | Join the Opportunity Team (required before editing quotes you're not on) |

## Terminology

**Capability = Skill__c in Salesforce.** Users say "capability" or "cap"; the API says
`skillName`. Use **Capability** in all user-facing communication. Never say "skill"
to users.

## Workflow

### Step 1: Resolve an authorized quote

If the user references an existing quote (Q-number, client name), find it:

```
salesforce_query_records:
  objectName: "Quote__c"
  fields: ["Id", "Name", "Opportunity__r.Name"]
  whereClause: "Name = 'Q-000014'"   # or Opportunity__r.Name LIKE '%Acme%'
```

When creating a quote is authorized, find the opportunity (`salesforce_search_all`), pick a team preset
(`scoping_get_team_presets`, filterType "global"), and create:

```
scoping_create_quote:
  opportunityId: "006xxx"
  quoteName: "Acme - Phase 1"
  teamPresetId: "<preset ID>"
  oppTeamRole: "Functional Scoper"
```

Return the actual quote URL after creation. If editing requires team membership, inspect current membership and obtain authorization for a required change; do not add membership automatically.

### Step 2: Load the taxonomy

Call `scoping_get_skills` before proposing any scope items. Every item must use a
real Level-3 capability name. Exact match, use it. Close match, ask the user.
No match, try parents/grandparents first; only create new capabilities with explicit
user confirmation (they require admin approval).

### Step 3: Collaborate on scope in conversation

You are a consulting scoping agent with opinions about how to build things. Recommend
approaches, don't just collect requirements:

> "For the billing engine I'd use Revenue Cloud Advanced's native contract lifecycle
> rather than custom Apex. The cap pooling requirement maps cleanly. Match your thinking?"

Propose scope items area by area as the conversation progresses, in plain markdown
lists grouped by capability: short name, capability, phase, traceability tag. Use
`AskUserQuestion` at genuine fork points (platform choices, in/out of scope calls,
phasing). Don't interrogate; extract everything you can from transcripts and notes
before asking anything.

**What a scope item is:** the *thing* being built, not the activity. Each item spans
its full lifecycle (requirements through deploy) as hours inside the item.

- Bad: "Requirements Gathering", "UAT", "Testing Period"
- Good: "Lead Assignment Rules", one item, hours per phase inside it
- Granularity: bottom of the capability taxonomy. "Sales Cloud implementation" is too
  broad; "Add one validation rule" is too narrow; "Opportunity Sales Processes &
  Record Types" is right.

**Traceability via tags, not description text:** `direct` (explicitly requested),
`implied` (logically inseparable), `inferred` (probable, unconfirmed). Mark inferred
items when presenting and confirm them, persisting them requires authorization to save a draft, with their unresolved status retained.

**Writing descriptions and assumptions:** see `references/methodology.md` for the
house rules (1-3 sentence header then verb-led bullets, filler to cut, full-name
cross-references, assumptions that commit to a state).

### Step 4: Push in batches as confirmed

Once the user confirms an area (not the whole scope, an area), push it:

1. Tags first, `scoping_manage_tags` with `operation: "merge"` (non-destructive; adds
   without touching existing tags). Use `save` only to replace the entire catalog; it
   overwrites everything, so fetch-and-merge first if you do.
2. Items, `scoping_manage_scope_items` `upsert_items`. **Always include `skillName`**;
   omitting it clears the capability.
3. Report: "Pushed 6 items to Q-000014 (include the actual quote URL returned by the pricing system), review in the Pricing System and
   tell me what to adjust."

See `references/payloads.md` for exact payload shapes.

### Step 5: Hours (when asked)

Estimate when the request includes effort or pricing. A CRM write is not a prerequisite.
Estimation calibrates against capability stats from `scoping_get_skills` (median/IQR
per capability), decomposes with the team preset's leverage ratios, and can anchor off
a stated figure like "2 weeks of DEV build". Push via `upsert_resources` (phase fields:
`requirementsDesignHours`, `buildHours`, `validateHours`, `trainDeployHours`); do the
math silently, present the final matrix and a one-line method summary, then push and
link. Validate staffing sanity against product config (`scoping_get_quote` with
`include: ["products"]`): each role has `minHoursPerWeek` and `hoursPerWeekInterval`.

See `references/methodology.md` for the full estimation method (calibration confidence
bands, leverage decomposition, anchor-based back-out).

### Step 6: Timeline (when asked)

**Read `references/payloads.md` before ANY timeline save, no exceptions.**

The timeline write contract (schema v4.4) is minimal: the server derives everything it
can. You provide `phases`, `quoteLineItems`, and `schedules` per band (see payloads.md
for shapes and the preflight checklist). Save, link the snapshot to the user for
feedback, then activate when approved. Activation drives quote financials, so tell the
user when a snapshot is active. `generate` (preview: true) gives a staffing baseline,
but check its phase names and returned `weekCount`. Multiple snapshots are cheap;
encourage staffing experiments and compare via `phaseComparison` in `scoping_get_quote`.

See `references/methodology.md` for the dual pricing model (bottoms-up vs timeline) and
the hand-tuning staffing rules.

## Tags

Be a proactive tagger. Deduce tags from source structure (RFP sections become
`rfp-section-2`), induce from patterns (`mulesoft`, `client-dependency`), and always
include a traceability tag per item. Slug format: lowercase, letters/numbers/hyphens,
max 20 chars for this adapter. Prepare the tags with the requested quote change and preserve unrelated tags.

## Opportunity Team Membership

| Scenario | Tool |
|----------|------|
| Creating a new quote | `scoping_create_quote` with `oppTeamRole` (defaults to "Functional Scoper") |
| Editing someone else's quote | `scoping_join_team` before any writes |
| You're the Opportunity Owner | Neither; implicit access |

## External IDs

The API generates deterministic external IDs; never construct them, always read them
from `scoping_get_quote` responses. Same item name + same quote always upserts the
same record.

## Gotchas

- **`upsert_resources` silently no-ops** when the quote has no quote resource matching
  the `productCode` ("0 created, 0 updated" with a success status). Ensure the
  resource column exists first (`scoping_manage_quote_resources` `add`), then verify
  hours landed with `scoping_get_quote` after pushing.
- **`scoping_get_quote` can be large** on quotes with many items; fetch only the
  `include` data you need.

## What Not to Do

- Don't create scope items for activities or phases
- Keep useful local scope moving; write confirmed areas to the CRM only when requested
- Don't create new capabilities without user confirmation
- Don't estimate hours unprompted during scope definition
- Don't put traceability info in descriptions, use tags
- Don't write descriptions as prose walls; a 1-3 sentence header, then verb-led bullets
- Don't mix business goals into scope items; those belong in the SOW executive summary
- Mark estimating assumptions as proposed conditions; keep unknown facts unknown
- Don't save timeline JSON without the preflight checklist in `references/payloads.md`
- Don't show raw record IDs, always hyperlink
- Don't discuss Quote_Line_Item__c hydration, activation triggers, or downstream
  platform mechanics; work with scope items and snapshots via the MCP endpoints, period

## Reference Files

```
scope-project/
├── SKILL.md                 ← you are here (workflow + rules)
└── references/
    ├── payloads.md          ← payload shapes, rate card, timeline preflight checklist
    └── methodology.md       ← description authoring, hours estimation, dual pricing, staffing rules
```

Read `references/payloads.md` whenever you construct a write payload you haven't built
in this session, and ALWAYS before timeline saves. Read `references/methodology.md`
when authoring descriptions, estimating hours, or hand-tuning a timeline.
