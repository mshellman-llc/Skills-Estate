# arch_check Rule Catalog

Every rule the checker enforces: what it matches, why it exists, how to fix a finding, and
when an exemption is legitimate. Severities shown are defaults; `.arch-check.json` can
override per rule (`off` / `warn` / `block`), `legacyPaths` caps matching files at warn,
and `mode: "warn"` caps the whole repo.

Exemption syntax (same line or the line above the finding):

```apex
// ARCH-EXEMPT: APX003 <reason — required>
```

---

## APX001 — SOQL/SOSL outside a Selector (block)

**Matches:** `[SELECT ...]`, `[FIND ...]`, `Database.query*/getQueryLocator*/countQuery*`,
`Search.query/find` in any class not named `*Selector` (or listed in `soqlAllowlist`).

**Why:** Centralized queries are the FLS enforcement point, the query-shape review point,
and the reuse point. Scattered SOQL is how the same object gets queried five ways with
five different field lists.

**Fix:** Move the query into the object's selector; add a method if no existing one fits.

**Legit exemptions:** Almost none in product code. Dynamic describe-driven tooling and
anonymous-script utilities occasionally qualify.

## APX002 — DML outside UnitOfWork (block)

**Matches:** statement-position `insert/update/upsert/delete/undelete/merge` and
`Database.<dml>()` in any class not in `dmlAllowlist` (default: `UnitOfWork` only).

**Why:** One commit point makes ordering, rollback, and re-entry deliberate, and makes AI
generated code mechanically reviewable — any raw DML is a structural violation, no
judgment needed.

**Fix:** Register with the transaction's UnitOfWork; let the entry point commit.

**Legit exemptions:** Immediate-mode requirements (e.g., logging that must survive
rollback via platform events — better: extend UnitOfWork), setup-object DML that can't mix
with the transaction.

## APX003 — Selector query without USER_MODE (block)

**Matches:** in `*Selector` classes, inline queries lacking `WITH USER_MODE` /
`WITH SECURITY_ENFORCED`, and `Database.query*` statements lacking `AccessLevel.USER_MODE`.

**Why:** With DTO mapping, nothing downstream enforces FLS — the query is the only
enforcement point. Default to user mode; run as system only on purpose, visibly.

**Fix:** Add `WITH USER_MODE`. Prefer it over `SECURITY_ENFORCED` (USER_MODE also enforces
sharing semantics and covers more operations).

**Legit exemptions:** Genuinely system-context work: integrations acting org-wide,
cross-user rollups, admin audit tooling. The reason string should say *why* system mode.

## APX004 — @AuraEnabled returns SObject (warn)

**Matches:** `@AuraEnabled` methods whose return type references a standard object,
`*__c/__mdt/__e/__b`, or `SObject`, including inside `List/Set/Map`.

**Why:** SObject returns couple the component to the data model and don't port (React on
Salesforce consumes Apex as plain JSON — a DTO surface is already the right shape).

**Fix:** Map to a DTO in the controller. Warn (not block) by default because pass-through
cases exist during migration; tighten to block on greenfield repos.

## APX005 — Logic in trigger body (block)

**Matches:** `.trigger` files containing more than one statement, or any
`if/for/while/switch`.

**Why:** Trigger bodies are untestable in isolation and invisible to the layer structure.
The dispatch line is the whole job.

**Fix:** `new <Object>TriggerHandler().run();` — move everything else into the handler and
services.

**Legit exemptions:** Effectively none.

## APX006 — Single-SObject public service method (warn)

**Matches:** `public/global` methods in `*Service` classes taking exactly one parameter of
an SObject type.

**Why:** Single-record services get called in loops by trigger paths eventually. Bulk-first
signatures force the shared code path to be governor-safe.

**Fix:** Take `List<T>` / `Map<Id, T>` / `Set<Id>`; the single-record caller wraps in a
list of one.

**Legit exemptions:** True singletons (e.g., "the current user's settings record").

## APX007 — Deeply nested generics (warn)

**Matches:** any type expression with three or more nested collection generics, e.g.
`Map<Id, Map<String, List<Opportunity>>>`. Two levels (`Map<Id, List<Contact>>`) is
idiomatic and never flagged. One finding per line.

**Why:** Past two levels, the structure carries meaning that nothing names — what the
keys are, what invariants hold. A named class documents the shape once, reviews once, and
gives future behavior a home. Applies to boundaries (signatures, returns, DTO fields)
without exception and to method bodies as strong preference; the same discipline applies
client-side (named factories + JSDoc typedefs), though the checker only scans Apex.

**Fix:** Extract a class that names the concept; keep at most one nesting level inside it.

**Legit exemptions:** Transient shapes consumed within a few lines where extraction adds
a class no one reads; direct passthrough of a platform API's shape.

## LWC001 — @wire on Apex import (warn)

**Matches:** `@wire(x)` where `x` was imported from `@salesforce/apex/...` in LWC JS.

**Why:** House pattern is imperative Apex: explicit call sites, explicit error handling,
explicit refresh, portable to React. LDS wires (`lightning/uiRecordApi` etc.) are *not*
flagged — LDS is still the right tool for record-centric UI.

**Fix:** Convert to `async` imperative call; if the method is `cacheable=true` the client
cache still applies. For in-editor feedback, install the ESLint version of this rule from
`assets/eslint/no-wire-of-apex.js` (PMD cannot parse modern LWC JavaScript).

**Legit exemptions:** A component intentionally built on wire reactivity that you're not
refactoring yet.

## META001 — Malformed ARCH-EXEMPT (block)

**Matches:** `ARCH-EXEMPT` comments missing a valid rule ID or a reason.

**Why:** An exemption without a reason is indistinguishable from silencing the tool. The
reason string is the audit trail — reviewers and future agents rely on it.

**Fix:** `// ARCH-EXEMPT: APX003 nightly reconciliation must see all records regardless of running user`

## META002 — PMD suppression without a reason (block)

**Matches:** `@SuppressWarnings(...)` mentioning PMD with no trailing `//` comment on the
same line, and `// NOPMD` with no text after it.

**Why:** PMD's native suppressions carry no required justification — without this rule
they're a mute button. The reason string is the audit trail reviewers and future agents
rely on, which matters doubly when AI writes most of the code.

**Fix:** `@SuppressWarnings('PMD.QueryWithoutUserMode') // org-wide rollup runs as system by design`
or `// NOPMD - transient shape consumed two lines down`.

---

## Engines

The **pmd** engine (default when a PMD 7 binary is available) runs
`assets/pmd/estate-apex.xml` — rule names map to these IDs via SoqlOutsideSelector=APX001,
DmlOutsideUnitOfWork=APX002, QueryWithoutUserMode=APX003, AuraEnabledReturnsSObject=APX004,
AvoidLogicInTrigger (PMD built-in)=APX005, NonBulkServiceMethod=APX006,
DeeplyNestedGenerics=APX007 — then applies the severity policy below. `dmlAllowlist` and
`soqlAllowlist` are injected into the ruleset as property overrides at run time, so
`.arch-check.json` stays the single source of config. PMD-native suppressions are applied
at their exact class/method scope; ARCH-EXEMPT comments are honored by the wrapper.

The **regex** engine is the dependency-free fallback. It honors ARCH-EXEMPT exactly and
PMD-native suppressions conservatively (`NOPMD` per line; `@SuppressWarnings` for the whole
file) — it may allow what PMD would flag, never the reverse. PMD rules always exempt test
classes; the regex engine's `exemptTestClasses` flag matches that default.

## Severity resolution order

0. File matches `excludePaths` → skipped entirely (reserved for vendored third-party
   framework source; never first-party code)
1. Rule default (table above)
2. `rules` override in `.arch-check.json` (`off` wins outright)
3. File matches `legacyPaths` → block downgrades to warn
4. `mode: "warn"` → all remaining blocks downgrade to warn

Exit code is 1 only when at least one finding survives at block severity — so a legacy
file full of warnings never stops a commit, and a brand-new class with one raw DML always
does (in block mode).
