/**
 * ExampleFeature — one file showing every layer of the house architecture working
 * together, for reference when scaffolding a real feature. In a real repo these are
 * separate files: AccountsSelector.cls, AccountService.cls, AccountPanelController.cls.
 * Delete this file after scaffolding; it exists to be read, not deployed.
 */

/* ---------------------------------------------------------------------------
 * SELECTOR — all SOQL for one object lives here. USER_MODE always (APX001/APX003).
 * ------------------------------------------------------------------------- */
// public inherited sharing class AccountsSelector {
//     public List<Account> byIds(Set<Id> ids) {
//         return [
//             SELECT Id, Name, Industry, AnnualRevenue, OwnerId
//             FROM Account
//             WHERE Id IN :ids
//             WITH USER_MODE
//         ];
//     }
//
//     public List<Account> highValueInIndustry(String industry, Decimal minRevenue) {
//         return [
//             SELECT Id, Name, AnnualRevenue
//             FROM Account
//             WHERE Industry = :industry AND AnnualRevenue >= :minRevenue
//             WITH USER_MODE
//             ORDER BY AnnualRevenue DESC
//             LIMIT 200
//         ];
//     }
// }

/* ---------------------------------------------------------------------------
 * SERVICE — business logic, bulk-first, shared by trigger + UI + API (APX006).
 * Takes collections. Registers changes with a UnitOfWork; the caller that owns
 * the transaction decides when to commit.
 * ------------------------------------------------------------------------- */
// public inherited sharing class AccountService {
//     public static void applyTierUpgrades(Set<Id> accountIds, UnitOfWork uow) {
//         for (Account acct : new AccountsSelector().byIds(accountIds)) {
//             if (acct.AnnualRevenue > 1000000 && acct.Industry != null) {
//                 uow.registerDirty(new Account(Id = acct.Id, Tier__c = 'Gold'));
//             }
//         }
//     }
// }

/* ---------------------------------------------------------------------------
 * CONTROLLER — thin @AuraEnabled boundary. Owns the transaction for UI calls,
 * maps SObjects to DTOs (APX004), translates exceptions for the client.
 * Reads are cacheable so imperative LWC calls still hit the client cache.
 * ------------------------------------------------------------------------- */
public inherited sharing class ExampleFeature {

    /** DTO — plain properties only. This is the UI contract; it ports to React as-is. */
    public class AccountSummaryDTO {
        @AuraEnabled public Id recordId;
        @AuraEnabled public String name;
        @AuraEnabled public Decimal annualRevenue;
        @AuraEnabled public String tierLabel;
    }

    // @AuraEnabled(cacheable=true)
    // public static List<AccountSummaryDTO> getHighValueAccounts(String industry) {
    //     try {
    //         List<AccountSummaryDTO> out = new List<AccountSummaryDTO>();
    //         for (Account a : new AccountsSelector().highValueInIndustry(industry, 1000000)) {
    //             AccountSummaryDTO dto = new AccountSummaryDTO();
    //             dto.recordId = a.Id;
    //             dto.name = a.Name;
    //             dto.annualRevenue = a.AnnualRevenue;
    //             dto.tierLabel = a.AnnualRevenue > 5000000 ? 'Platinum' : 'Gold';
    //             out.add(dto);
    //         }
    //         return out;
    //     } catch (Exception e) {
    //         throw new AuraHandledException(e.getMessage());
    //     }
    // }
    //
    // @AuraEnabled
    // public static void upgradeAccounts(List<Id> accountIds) {
    //     try {
    //         UnitOfWork uow = new UnitOfWork(new List<Schema.SObjectType>{ Account.SObjectType });
    //         AccountService.applyTierUpgrades(new Set<Id>(accountIds), uow);
    //         uow.commitWork();  // controller owns the UI transaction
    //     } catch (Exception e) {
    //         throw new AuraHandledException(e.getMessage());
    //     }
    // }
}

/* ---------------------------------------------------------------------------
 * LWC (companion js) — imperative calls only for Apex (LWC001). LDS wires for
 * plain record display/edit remain fine.
 *
 * import getHighValueAccounts from '@salesforce/apex/ExampleFeature.getHighValueAccounts';
 * import upgradeAccounts from '@salesforce/apex/ExampleFeature.upgradeAccounts';
 * import { notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
 *
 * async loadAccounts() {
 *     try {
 *         this.rows = await getHighValueAccounts({ industry: this.industry });
 *     } catch (e) {
 *         this.error = e.body?.message ?? 'Unable to load accounts';
 *     }
 * }
 *
 * async upgrade() {
 *     await upgradeAccounts({ accountIds: this.selectedIds });
 *     await notifyRecordUpdateAvailable(this.selectedIds.map(id => ({ recordId: id })));
 *     await this.loadAccounts();
 * }
 * ------------------------------------------------------------------------- */
