---
name: sf-apex-patterns
description: 'Apply the estate''s Salesforce architecture (a service layer shared by trigger, UI and API entry points, a Unit of Work for all DML, selectors for all SOQL in USER_MODE, DTO returns from @AuraEnabled, imperative Apex from LWC) when the project uses it. Use for a new Apex class, trigger or LWC component, adding a service, selector or unit of work, running arch checks or pre-commit, or fixing architecture violations.'
metadata:
  canon_exempt: 'engineering-doc'
  canon_exempt_reason: 'Enforcement-stack reference an agent must hold in full: rule IDs, exit codes, suppression contract, and engine semantics, punctuation included.'
---


# Salesforce Enterprise Patterns (Estate House Architecture)

This skill does two things: it tells you **how to structure Salesforce code** the house way,
and it ships **scripted checks** (`scripts/arch_check.py`) that verify the structure
mechanically — runnable ad hoc, in CI, or as a git pre-commit hook with warn/block modes.

Why this architecture exists (short version): business logic in one place (services) so
trigger, UI, and API paths never diverge; DML in one place (Unit of Work) so transaction
ordering and partial-save behavior are deliberate; SOQL in one place (selectors) so
field-level security is enforced by default and query shape is reviewable; DTOs at the UI
boundary so the LWC/React view layer is decoupled from the data model. The full spec with
code examples is in `references/architecture.md` — read it before writing code in an
unfamiliar layer. The rule catalog with rationale per check is in `references/rules.md`.

## Project adoption

This is a reusable reference architecture, not an employer or platform mandate. Read the project's architecture decisions and existing framework before applying it. Preserve a confirmed project convention unless the user authorizes migration. If adoption is undecided, present compatibility findings and leave enforcement uninstalled. The bundled rule severities are defaults for this named pattern, not policies inferred for a new client.

## The layers at a glance

| Layer | Naming | Owns | Never contains |
|---|---|---|---|
| Trigger | `<Object>.trigger` | One dispatch line to its handler | Logic, SOQL, DML, loops, ifs |
| Trigger handler | `<Object>TriggerHandler.cls` | Context routing, recursion guard | SOQL, DML (delegates to services) |
| Service | `<Domain>Service.cls` | Business logic, bulk-first, transaction boundaries | UI shaping, direct SOQL |
| Selector | `<Object>sSelector.cls` | ALL SOQL for its object, `WITH USER_MODE` | DML, business logic |
| Unit of Work | `UnitOfWork.cls` (shipped) | ALL DML, ordered commit | Queries, logic |
| Controller | `<Feature>Controller.cls` | `@AuraEnabled` entry points, DTO mapping, error translation | Business logic, SOQL, DML |
| DTO | `<Feature>DTO.cls` or inner classes | `@AuraEnabled` plain properties | SObject fields, logic |
| LWC | `<feature>/` | View logic, **imperative** Apex calls | `@wire` to Apex (LDS ui*Api wires are fine) |

A UI request flows: LWC → imperative call → Controller → Service → Selector (reads) /
UnitOfWork (writes) → Controller maps result to DTO → LWC. A trigger flows: Trigger →
Handler → the same Service. That shared middle is the entire point.

**Handler-layer variant:** the trigger dispatch layer is swappable. The default is the
shipped `TriggerHandler.cls`; orgs with meaningful Flow + Apex automation mix (or
multi-team automation on shared objects) should use the Trigger Actions Framework instead —
read `references/taf.md` before scaffolding trigger work in a repo that uses TAF (you'll
see `MetadataTriggerHandler` in triggers and `Trigger_Action__mdt` metadata). All other
layers and all checker rules are identical under both.

## Scaffolding a new feature

1. Copy the base classes from `assets/apex/` into the target repo if not already present:
   `UnitOfWork.cls`, `TriggerHandler.cls` (plus their `-meta.xml` files — generate matching
   the repo's existing API version). These are lean and owned — do not substitute fflib.
2. Create the selector before the service. Every SOQL statement it contains uses
   `WITH USER_MODE` (or `AccessLevel.USER_MODE` for `Database.query*`). System-mode queries
   require an inline `// ARCH-EXEMPT: APX003 <reason>` and a real reason.
3. Write the service bulk-first: every public method takes collections, even if today's only
   caller passes one record. Services receive or construct a `UnitOfWork`, register changes,
   and either commit it or hand it back to the caller who owns the transaction.
4. Controllers are thin: try/catch translating exceptions to `AuraHandledException`, calls
   into the service, maps SObjects to DTOs. Mark read methods `@AuraEnabled(cacheable=true)`
   when semantics allow — imperative calls still hit the client cache.
5. LWC calls Apex imperatively (`import method from '@salesforce/apex/...'` then `await`).
   If an imperative write touches records shown elsewhere on a Lightning page, call
   `notifyRecordUpdateAvailable()` so standard components don't go stale. LDS wire adapters
   (`lightning/uiRecordApi` etc.) and record forms remain the right tool for plainly
   record-centric display/edit — don't force the DTO ceremony onto those.
6. Follow the code examples in `references/architecture.md` for each file you create.

## Running the checks

```bash
python3 scripts/arch_check.py --paths force-app/           # whole tree
python3 scripts/arch_check.py --staged                     # staged files only (hook mode)
python3 scripts/arch_check.py --paths force-app/ --json    # machine-readable
```

Exit code 0 = clean or warnings only; 1 = at least one blocking violation; 2 = usage/config
error. Run the checker after writing or modifying Apex/LWC and fix (or consciously exempt)
findings before presenting work as done.

### Engines: PMD-first, regex fallback

arch_check is an orchestrator with two engines. The **pmd** engine runs the custom PMD 7
ruleset at `assets/pmd/estate-apex.xml` (AST-accurate, and the same rules a dev's IDE
and CI see via the org's PMD standards), then applies the policy PMD can't express:
warn/block modes, legacy-path downgrades, exclude paths, and suppression governance. The
**regex** engine is the self-contained fallback for environments without PMD — no
dependencies, same rule IDs, slightly less precise. Default `--engine auto` picks pmd when
a PMD binary is found (config `pmdPath`, `$PMD_BIN`, or `pmd` on PATH). The LWC rule
(LWC001) always runs in the wrapper; for in-editor feedback there's also an ESLint version
at `assets/eslint/no-wire-of-apex.js` (PMD cannot parse modern LWC JavaScript).

Suppression policy, in order of preference: (1) `@SuppressWarnings('PMD.RuleName')` with a
trailing `// reason` comment — silences PMD everywhere including the IDE; (2) `// NOPMD -
reason` for one line; (3) `// ARCH-EXEMPT: APX003 reason` — wrapper-level, works under
both engines. A suppression without a reason is itself a blocking violation (META001 for
ARCH-EXEMPT, META002 for the PMD forms): for AI-generated code the reason string is the
audit trail, and an agent that adds one must tell the user it did and why.

### Configuration: `.arch-check.json` at the repo root

Copy `assets/arch-check.json` as a starting point:

```json
{
  "mode": "block",
  "legacyPaths": ["force-app/main/default/classes/legacy/**"],
  "rules": { "APX004": "warn", "LWC001": "warn" },
  "dmlAllowlist": ["UnitOfWork"],
  "exemptTestClasses": true
}
```

- `mode`: repo-wide default — `block` (violations fail the commit) or `warn` (report only).
  New engagements start at `block`; use `warn` when adopting the pattern on an existing
  codebase you haven't refactored yet.
- `legacyPaths`: globs for old code. Findings in matching files are downgraded to warn no
  matter what — new work stays blocked, old work stays visible without stopping commits.
  As legacy code gets refactored, shrink these globs.
- `rules`: per-rule override — `"off"`, `"warn"`, or `"block"`. Rule IDs are in
  `references/rules.md`.
- `dmlAllowlist`: class names (without `.cls`) allowed to perform raw DML besides
  `UnitOfWork`. Keep it short; every entry is a hole in the transaction story.
- `excludePaths`: globs skipped entirely — for vendored third-party framework source
  (e.g. a vendored Trigger Actions Framework). First-party code never goes here.
- `exemptTestClasses`: `@IsTest` files skip placement rules (they still shouldn't rot, but
  test setup legitimately does raw DML and SOQL).

### Inline exemptions

Any finding can be suppressed on a specific line with a trailing or preceding comment:

```apex
List<User> admins = [SELECT Id FROM User WITH SYSTEM_MODE]; // ARCH-EXEMPT: APX003 admin audit runs as system by design
```

An exemption without a reason after the rule ID is itself a violation (`META001`). Exemptions
are for genuine exceptions, not for finishing faster — when you add one while working on a
task, tell the user you did and why.

### Enforcement: two installation paths

**Repo already running the Estate delivery-standards stack** (sf-delivery-standards;
you'll see `git config core.hooksPath` pointing at `~/.estate/githooks`): do NOT install
a `.git/hooks` hook — it would never fire. That stack's pre-commit gate 4 runs PMD against
`config/pmd-ruleset.xml`, so integration is one file: copy
`assets/pmd/estate-apex.xml` to `config/estate-apex.xml` and
`assets/pmd/pmd-ruleset-project.xml` to `config/pmd-ruleset.xml` (or merge the
architecture rule refs into an existing project ruleset). The architecture rules are then
blocking under `git config estate.pmd block`, advisory under `advise` — that knob is the
delivery stack's warn/block equivalent. Add the ESLint rule to the repo's eslint config so
gate 3 covers LWC001, and run `arch_check.py` in CI (or an npm script) for what PMD can't
express: legacy-path downgrades and suppression-reason governance.
`scripts/install_hooks.py` detects this stack and prints these steps instead of writing an
inert hook.

**Standalone repo** (no delivery-standards stack):

```bash
python3 scripts/install_hooks.py            # writes .git/hooks/pre-commit + copies ruleset
python3 scripts/install_hooks.py --print    # just print the hook (for husky users)
```

The hook runs `arch_check.py --staged` against staged file *content* (not the working
tree), so partially-staged files are checked as they'll actually be committed. Bypass in an
emergency with `git commit --no-verify` — but treat that as a flag to raise, not a habit.

## Rules the checker enforces

| ID | Default | Checks |
|---|---|---|
| APX001 | block | SOQL/SOSL outside `*Selector` classes |
| APX002 | block | DML outside `UnitOfWork` (+ configured allowlist) |
| APX003 | block | Selector SOQL missing `USER_MODE`/`SECURITY_ENFORCED` |
| APX004 | warn | `@AuraEnabled` method returns SObject types instead of DTOs |
| APX005 | block | Logic in trigger bodies (anything beyond handler dispatch) |
| APX006 | warn | Public service methods taking a single SObject (bulk-first smell) |
| APX007 | warn | Generic collections nested 3+ levels (extract a named class) |
| LWC001 | warn | `@wire` on an `@salesforce/apex` import (should be imperative) |
| META001 | block | `ARCH-EXEMPT` without a rule ID and reason |
| META002 | block | `@SuppressWarnings`/`NOPMD` without a reason comment |

Full rationale, examples, and remediation per rule: `references/rules.md`. When a finding is
a false positive you can't restructure around, exempt it inline with a reason — never
disable a whole rule to silence one line.

## Reviewing existing code

When asked to review code against this architecture (not just write it), run the checker
first for the mechanical findings, then read `references/architecture.md` and look for what
scripts can't see: services that shape UI responses, transaction ownership ambiguity (who
commits the UoW?), selectors leaking query building into callers, controllers with business
logic that happens to contain no SOQL/DML. Report scripted findings and judgment findings
separately.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
