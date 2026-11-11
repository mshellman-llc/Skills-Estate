# The Aleysian House Salesforce Architecture

Full spec for the layered architecture the `sf-enterprise-patterns` skill scaffolds and
enforces. Read the section for whichever layer you're about to write.

## Why this shape

Three problems drive everything here:

1. **Divergent logic paths.** When trigger code, UI controllers, and API endpoints each
   carry their own copy of a business rule, they drift. The service layer is the single
   shared implementation; every entry point is a thin adapter onto it.
2. **Uncontrolled transactions.** Scattered DML makes ordering, partial-save behavior, and
   trigger re-entry accidental. The Unit of Work makes them deliberate: services *register*
   changes, one owner *commits* them, once.
3. **UI coupled to the data model.** Components bound to SObject shape break when the model
   changes and can't be ported off LWC. DTOs make the UI contract explicit and owned. This
   is also the React position: Salesforce Multi-Framework React apps consume Apex
   imperatively with no LDS/@wire — a DTO-based controller surface ports as-is.

## Layer responsibilities

### Triggers — dispatch only

One trigger per object, all contexts declared, body is a single dispatch:

```apex
trigger AccountTrigger on Account (
    before insert, before update, before delete,
    after insert, after update, after delete, after undelete) {
    new AccountTriggerHandler().run();
}
```

No logic, no SOQL, no DML, no conditionals — not even "just this once." (APX005)

### Trigger handlers — routing only

Extend the shipped `TriggerHandler` base. Override only needed contexts. Delegate to
services immediately; the handler's job is casting `Trigger.new`/`Trigger.oldMap` and
choosing which service method to call. Handlers own the trigger-path transaction: they
construct the UnitOfWork, pass it to services, and commit it.

```apex
public inherited sharing class AccountTriggerHandler extends TriggerHandler {
    protected override void afterUpdate() {
        UnitOfWork uow = new UnitOfWork(new List<Schema.SObjectType>{
            Opportunity.SObjectType });
        AccountService.syncOpportunityTiers(
            (Map<Id, Account>) Trigger.newMap, (Map<Id, Account>) Trigger.oldMap, uow);
        uow.commitWork();
    }
}
```

### Services — the only home for business logic

- **Bulk-first, always.** Public methods take collections (`List`, `Set<Id>`, `Map`),
  even when today's only caller has one record. A UI call is a list of one; a trigger call
  is a list of 200. One code path. (APX006)
- **No UI shaping.** Services return SObjects, domain results, or nothing — never DTOs,
  never `AuraHandledException`. Shaping belongs to the controller that called.
- **Transaction participation, not ownership by default.** Prefer signatures that accept a
  `UnitOfWork` and register changes into it. The entry point (handler, controller, API
  class) owns commit. A service may own its own transaction only when it *is* the
  boundary (e.g., a batch/queueable body) — make that explicit in the method name
  (`...AndCommit`).
- Reads go through selectors; a service never contains SOQL. (APX001)

### Selectors — the only home for SOQL

One selector per object: `AccountsSelector`, `OrdersSelector`. Every query:

- `WITH USER_MODE` (or `AccessLevel.USER_MODE` on `Database.query*`). This is the security
  backstop: FLS/CRUD enforced at the query, centrally, not left to callers. (APX003)
- System-mode queries are exceptional and must carry
  `// ARCH-EXEMPT: APX003 <why system mode is required>`.
- Selectors take filter parameters and return `List<SObject>` — no business logic, no DML,
  no formatting. If a caller needs a different field set, add a method; don't add a
  do-everything query builder.

### Unit of Work — the only home for DML

The shipped `UnitOfWork.cls` (assets/apex/) is deliberately lean: register new / dirty /
deleted, relationship stitching for parent-child inserts, ordered commit with savepoint
rollback. It is owned code — extend it in-repo when a client needs platform events,
`Database.insert` with partial success, or immediate-mode DML, rather than importing fflib.
Raw DML anywhere else fails APX002; additions to the `dmlAllowlist` in `.arch-check.json`
should be rare and reviewed.

### Controllers — thin @AuraEnabled adapters

- One controller per feature/component, not per object.
- Wrap everything in try/catch and rethrow as `AuraHandledException` with a user-safe
  message.
- Map results to DTOs; never return SObjects. (APX004) DTOs are inner classes (small
  feature) or standalone `<Feature>DTO.cls` (shared shapes) with `@AuraEnabled` plain
  properties only.
- Reads: `@AuraEnabled(cacheable=true)` when the method is genuinely side-effect-free —
  imperative LWC calls still hit the Lightning client cache for cacheable methods.
- Writes: controller constructs the UnitOfWork, calls services, commits.

### LWC — imperative Apex, LDS where LDS is better

- Apex is called imperatively: `import m from '@salesforce/apex/...'; await m(args)`.
  Never `@wire` an Apex method (LWC001) — wire hides errors in property plumbing,
  couples refresh to reactive params, and doesn't port to React.
- LDS remains the right tool for plainly record-centric UI: `lightning-record-form`,
  `lightning/uiRecordApi` wires. Don't rebuild a record edit form with DTOs.
- After an imperative write that affects records visible elsewhere on the page, call
  `notifyRecordUpdateAvailable()` so LDS-backed standard components refresh.
- Component JS holds view logic only; anything reusable across components goes in a
  shared service module or (better) the Apex service layer.

## Naming the shapes: DTO, DAO, data service, view model

"Wrapper class" and "POJO" flatten four distinct roles. Use the precise name; each has
different rules.

**DTO — the wire contract** (`*DTO`, Apex). The shape that crosses the Apex↔LWC boundary.
Screen-shaped, not table-shaped: build one per feature surface for what the component
displays, never a universal `AccountDTO` mirroring the object — that recreates the
coupling DTOs exist to break. Request and response DTOs are *different types*: writes are
command-shaped (`UpgradeTierRequest` — ids, changed fields, intent), never the read DTO
echoed back. This prevents stale-write clobbers and makes the server receive an
instruction, not a blob to diff.

**DAO — already occupied, don't rebuild it.** The DAO role on-platform is Selector (reads)
plus UnitOfWork (writes). A separate `*DAO` layer is ceremony with no job. Off-platform
callouts are the exception: one gateway class per external system plays the DAO role for
that integration.

**Data service module — the client-side gateway** (`<feature>DataService.js`, LWC). A JS
module wrapping the imperative Apex imports; components import it, never the Apex imports
directly, once two or more components share calls (single-component features may call Apex
imports directly). It centralizes error normalization (unwrap `e.body?.message` once, not
per component), `notifyRecordUpdateAvailable` after writes, and client caching. It is also
the React seam: porting a feature means reimplementing one module against the platform
SDK while components barely change.

**View model — what the template binds to** (component-local, JS). Almost never the raw
DTO: it's DTO plus presentation state — selection flags, computed CSS classes, formatted
values. Map DTO → VM at the component edge with a named transform (`toRowVm(dto)`) and
never mutate the DTO in place to hold view state. A pristine DTO is what keeps
presentational needs from leaking backward into Apex; the day `rowCssClass` appears in a
server-side DTO, the contract has stopped being an API.

The full flow: Selector/UoW (persistence) → Service (behavior) → DTO (contract) →
data service module (client gateway) → view model (binding). Each transform is where one
kind of coupling goes to die.

## Flatten deep nesting into named shapes

Generic collections nested beyond two levels (`Map<Id, Map<String, List<Opportunity>>>`)
carry no semantics — nothing says what the outer key means, what the inner key means, or
what invariants hold. Introduce a named class instead and the code self-documents:

```apex
// Hard to read, impossible to review confidently:
Map<Id, Map<String, List<Opportunity>>> pipelineByOwnerByStage;

// Says what it is, and gives invariants a home:
public class OwnerPipeline {
    public Id ownerId;
    public Map<String, List<Opportunity>> byStage; // one nesting level inside a named shape
}
List<OwnerPipeline> pipelines;
```

The rule of thumb (checker rule APX007, warn): two levels of generic nesting is the
ceiling. `Map<Id, List<Contact>>` is idiomatic Apex grouping — leave it alone. Three
levels means a concept is hiding in the structure — name it. This applies at boundaries
without exception (public method params and returns, DTO fields), and inside method bodies
as strong preference. The same rule holds client-side: deeply nested object literals in
LWC become named factory functions with a JSDoc `@typedef` (or TypeScript types where the
repo uses TS), so the shape is documented where it's built.

Named shapes also review better — human or AI: a reviewer can check `OwnerPipeline` has
the right fields once, instead of re-deriving what position three of a nested generic
means at every use site.

## Transaction ownership cheat sheet

| Entry point | Who builds UoW | Who commits |
|---|---|---|
| Trigger | Handler | Handler |
| LWC action | Controller | Controller |
| REST/API class | API class | API class |
| Batch/Queueable | The async class per scope | The async class |
| Service calling service | Passed down | The original owner |

The invariant: exactly one `commitWork()` per logical transaction, at the outermost layer
that knows the operation is complete.

## Testing conventions

- Test classes are exempt from placement rules (config `exemptTestClasses`) — test setup
  legitimately does raw DML/SOQL.
- Test services through their public bulk methods with in-memory records where possible;
  pass a UnitOfWork and assert on registered state or committed results.
- Controllers get thin tests (error translation, DTO mapping); the logic they call is
  already covered at the service level.

## Adopting on an existing codebase

Don't refactor the world on day one. Set `mode` to `block`, add the existing class
directories to `legacyPaths` (they warn instead of block), and hold the line on new files.
Refactor legacy classes opportunistically when a story touches them, then remove them from
the glob. The warn output is the standing backlog — it should shrink release over release,
and that trend is reportable to the client.
