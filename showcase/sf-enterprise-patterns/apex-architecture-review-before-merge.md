---
skill: sf-enterprise-patterns
title: Pre-merge Apex review against the service, selector and Unit of Work pattern
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: f02a3a9fec328a1b42e89fae6a157071d3fc4ed59452e0c9b0a38ec463cbffff
---

## Request

We're about to merge the contract renewal work for the Orders org. Can you review RenewalController, RenewalService and ContractsSelector against our Apex architecture and tell me what has to change before merge? Our ADR and .arch-check.json are included.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `sf-apex-patterns` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### project-config.md

#### ADR-007: Apex architecture (accepted 2026-02-12)

Orders org (Kestrel Freight) uses the service layer + UnitOfWork + selectors
pattern for all new Apex. Shipped `UnitOfWork.cls` and `TriggerHandler.cls`
are already in `force-app/main/default/classes/`. Default trigger handler,
no Trigger Actions Framework. Classes in `classes/legacy/` predate the ADR.

#### .arch-check.json

```json
{
  "mode": "block",
  "legacyPaths": ["force-app/main/default/classes/legacy/**"],
  "rules": { "APX004": "warn" },
  "dmlAllowlist": ["UnitOfWork"],
  "exemptTestClasses": true
}
```

PMD is not installed on the CI runner or the reviewer's machine.

#### renewal-classes.txt

=== force-app/main/default/classes/RenewalController.cls ===
1  public with sharing class RenewalController {
2      @AuraEnabled(cacheable=true)
3      public static List<Contract__c> getExpiring(Integer days) {
4          Date cutoff = Date.today().addDays(days);
5          return [SELECT Id, Name, EndDate__c FROM Contract__c WHERE EndDate__c <= :cutoff];
6      }
7      @AuraEnabled
8      public static void extend(Id contractId, Integer months) {
9          Contract__c c = [SELECT Id, EndDate__c FROM Contract__c WHERE Id = :contractId WITH USER_MODE];
10         c.EndDate__c = c.EndDate__c.addMonths(months);
11         update c;
12     }
13 }

=== force-app/main/default/classes/RenewalService.cls ===
1  public with sharing class RenewalService {
2      public static void applyUplift(Contract__c c) {
3          c.Value__c = c.Value__c * 1.04;
4      }
5      public static Map<Id, Map<String, List<Contract__c>>> groupByOwnerAndBand(List<Contract__c> rows) {
6          return new Map<Id, Map<String, List<Contract__c>>>(); // grouping omitted
7      }
8  }

=== force-app/main/default/classes/ContractsSelector.cls ===
1  public with sharing class ContractsSelector {
2      public static List<Contract__c> byIds(Set<Id> ids) {
3          return [SELECT Id, EndDate__c FROM Contract__c WHERE Id IN :ids];
4      }
5      public static List<Contract__c> allActive() {
6          // ARCH-EXEMPT: APX003
7          return [SELECT Id, OwnerId FROM Contract__c WHERE Status__c = 'Active' WITH SYSTEM_MODE];
8      }
9  }

## Output

**The branch is not ready to merge.** Run in block mode, `arch_check` would exit 1 with 6 blocking findings and 3 warnings. The ADR confirms the pattern is adopted and none of the three files is under `classes/legacy/`, so nothing is downgraded.

I could not run `scripts/arch_check.py` here, and PMD is not installed on your runner. I applied the regex engine's documented rules by hand to the line-numbered listings you supplied. Run the real command before merging to confirm: `python3 scripts/arch_check.py --paths force-app/`.

#### Scripted findings

| File:line | Rule | Severity | Finding |
|---|---|---|---|
| RenewalController.cls:5 | APX001 | block | SOQL in a controller |
| RenewalController.cls:9 | APX001 | block | SOQL in a controller (it does use `WITH USER_MODE`, but the query still belongs in a selector) |
| RenewalController.cls:11 | APX002 | block | Raw `update`; only `UnitOfWork` may do DML |
| ContractsSelector.cls:3 | APX003 | block | `byIds` has no `WITH USER_MODE` |
| ContractsSelector.cls:6 | META001 | block | `ARCH-EXEMPT: APX003` has no reason |
| ContractsSelector.cls:7 | APX003 | block | `WITH SYSTEM_MODE` query. The exemption above it is malformed, so it does not suppress this line |
| RenewalController.cls:3 | APX004 | warn | `@AuraEnabled` returns `List<Contract__c>` instead of a DTO |
| RenewalService.cls:2 | APX006 | warn | Public service method takes a single `Contract__c` |
| RenewalService.cls:5 | APX007 | warn | `Map<Id, Map<String, List<Contract__c>>>` nests three levels (the return type; line 6 repeats it in the body) |

`dmlAllowlist` holds only `UnitOfWork`, so there is no allowance for the controller's `update`.

#### Judgment findings (the script cannot see these)

- **Business logic in the controller.** `extend` computes the new end date (line 10). That rule belongs in `RenewalService`, or the trigger path and the UI path will drift.
- **No error translation.** Neither controller method has a try/catch that rethrows `AuraHandledException`.
- **Transaction ownership is unstated.** The controller must build the `UnitOfWork`, pass it to the service and call `commitWork()` once. Today nothing owns the transaction.
- **The 1.04 uplift** in `applyUplift` is a hard-coded business constant. Confirm with the business owner where it should live (custom metadata is the usual place). I have not assumed a source for it.
- **`allActive()` needs a decision.** If this is an org-wide rollup that must see every record regardless of the running user, system mode may be legitimate, but the reason has to say so. If it feeds a user-facing screen, switch it to `WITH USER_MODE`. I can't tell which from the code.

#### What to change

1. `ContractsSelector.byIds`: add `WITH USER_MODE`.
2. `ContractsSelector.allActive`: either `WITH USER_MODE`, or keep system mode and write the reason, for example `// ARCH-EXEMPT: APX003 <why this caller must see all contracts regardless of running user>`. The reason must come from the owner of that requirement.
3. Add `ContractsSelector.expiringBefore(Date cutoff)` (user mode) and use `byIds` for the lookup in `extend`.
4. `RenewalService`: change to bulk signatures, add a `UnitOfWork` parameter, and add the extension logic:

```apex
public with sharing class RenewalService {
    public static void extendContracts(
            List<Contract__c> contracts, Integer months, UnitOfWork uow) {
        for (Contract__c c : contracts) {
            c.EndDate__c = c.EndDate__c.addMonths(months);
        }
        uow.registerDirty(contracts);
    }

    public class OwnerBands {
        public Id ownerId;
        public Map<String, List<Contract__c>> byBand;
    }
    public static List<OwnerBands> groupByOwnerAndBand(List<Contract__c> rows) { /* ... */ }
}
```

   Check the registration method name against the shipped `UnitOfWork.cls` in your repo; I wrote `registerDirty` from the architecture spec without seeing your copy. `applyUplift` becomes `applyUplift(List<Contract__c>, UnitOfWork)` the same way.
5. `RenewalController`: return a `RenewalRowDTO` inner class (`@AuraEnabled` plain properties: id, name, endDate) from `getExpiring`; make `extend` take a list or wrap the single id, call selector, service and `uow.commitWork()`, all inside try/catch that rethrows `AuraHandledException` with a user-safe message.

#### Next step

After those edits, rerun `arch_check`; the expected result is exit 0 with no warnings. No `.arch-check.json` change is needed, and I would not add a rule override or allowlist entry to get a pass. Since PMD is absent, the regex engine is the only check running in CI; installing PMD 7 would give you the AST-accurate rules.

Nothing was installed, committed or changed in your repository. This review is a read-through only.
