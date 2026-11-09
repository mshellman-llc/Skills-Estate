# Handler-Layer Variant: Trigger Actions Framework (TAF)

The house architecture's trigger layer has two supported dispatchers. This file covers the
second one: Mitch Spano's Trigger Actions Framework
(github.com/mitchspano/apex-trigger-actions-framework). TAF replaces **only** the
handler/dispatch layer — services, selectors, UnitOfWork, controllers, DTOs, and LWC rules
are unchanged, and the arch_check rules apply identically.

## Choosing the dispatcher

| Situation | Use |
|---|---|
| Apex-dominant automation, small team, simple org | Shipped `TriggerHandler.cls` (default) — fewest moving parts to hand off |
| Meaningful record-triggered **Flow + Apex mix** on the same objects | TAF — deterministic interleaved ordering is its killer feature |
| Multiple teams/admins contributing automation to shared objects | TAF — metadata-driven ordering and bypass without deploys |
| Client explicitly standardized on TAF already | TAF — don't fight it |

Don't mix dispatchers on the same object. Pick per-org (or per-object during migration)
and record the choice in the repo README.

## How TAF maps onto the house layers

- **Trigger:** still one line — `new MetadataTriggerHandler().run();` — which passes
  APX005 as-is.
- **Trigger handler → trigger actions:** instead of one `<Object>TriggerHandler` class,
  each unit of automation is a class implementing a `TriggerAction` interface
  (`TriggerAction.BeforeInsert`, `TriggerAction.AfterUpdate`, ...), registered and ordered
  via `Trigger_Action__mdt` custom metadata (plus one `sObject_Trigger_Setting__mdt` per
  object). Flows are registered the same way, so Flow and Apex actions interleave in an
  explicit, admin-visible order.
- **House rule, unchanged:** action classes are thin adapters. They cast trigger context,
  call services, and nothing else. APX001/APX002 enforce this mechanically — an action
  class with SOQL or raw DML fails the same checks a fat handler would.
- **Bypass:** TAF provides metadata- and permission-based bypass per action plus a static
  bypass API — use those instead of the shipped `TriggerHandler.bypass()`.

Naming: `<Object><Context><What>TA`, e.g. `OpportunityAfterUpdateSyncTiersTA`. One
action = one business behavior; resist the ten-line-class sprawl by keeping behavior in
services and actions as pure delegation.

## Unit of Work ownership under TAF

With the owned TriggerHandler, the handler builds and commits the UoW. TAF splits the
trigger path across independent action classes, so decide explicitly:

**Option A (default): each action owns its own UoW.** Build, register, commit inside the
action. Simple, isolated, no shared state — at the cost of multiple commits per trigger
context. Start here.

**Option B (advanced, NEEDS SPIKE before house adoption): finalizer-owned commit.**
TAF ships DML Finalizers — classes implementing `TriggerAction.DmlFinalizer`, configured
and ordered via `DML_Finalizer__mdt`, executed by `TriggerBase` when the trigger context
stack empties and its DML row accounting drains (with `waitToFinalize()`/`nowFinalize()`
for manual control). Architecturally this is the "outermost layer that knows the operation
is complete" — the natural single commit point: actions register into a
transaction-scoped UoW, one finalizer commits it. Before standardizing on this, spike:
(1) re-entrancy — the finalizer's commit fires triggers again; confirm row accounting and
recursion behavior; (2) the framework's rules about performing DML inside finalizers;
(3) interaction with interleaved Flows, which do their own DML outside the UoW regardless.
Record spike results here.

Note the honest limit: once Flows interleave, "all DML through UoW" governs the **Apex**
path only. Flow DML is outside it by nature. That's acceptable — the UoW invariant was
never going to bind declarative automation — but say so in design docs rather than
implying total coverage.

## Repo and checker configuration

Prefer installing TAF as its unlocked package so framework classes never enter the repo.
If the client vendors the source instead, exclude it from checking — it's third-party code
with its own conventions:

```json
{
  "excludePaths": ["force-app/main/default/classes/trigger-actions-framework/**"],
  "dmlAllowlist": ["UnitOfWork"]
}
```

Everything else in `.arch-check.json` stays the same. Action classes are first-party code
and get no exclusions.

Deployment note: `Trigger_Action__mdt` / `sObject_Trigger_Setting__mdt` (and
`DML_Finalizer__mdt` if used) records are part of the feature — ship them in the same
package/changeset as the action classes, and review them in the same PR. An action class
with no metadata record silently never runs; treat missing metadata as a review blocker.

## Scaffolding checklist (TAF repos)

1. Trigger exists per object, one line, all contexts declared.
2. `sObject_Trigger_Setting__mdt` record for the object.
3. Action class implementing the right `TriggerAction` interface, delegating to a service.
4. `Trigger_Action__mdt` record with explicit `Order__c` — check existing records (and
   registered Flows) for that object/context and choose the order deliberately.
5. Run `arch_check.py` — same rules as everywhere else.
