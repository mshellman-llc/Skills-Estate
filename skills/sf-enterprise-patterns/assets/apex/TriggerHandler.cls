/**
 * TriggerHandler — base class for all trigger handlers. Triggers contain exactly
 * one line: new XxxTriggerHandler().run();  (arch_check rule APX005 enforces this)
 *
 * Provides context routing, a per-handler recursion guard, and a test/bulk bypass API.
 * Handlers override only the contexts they need and delegate real logic to services.
 *
 * Example:
 *   public inherited sharing class AccountTriggerHandler extends TriggerHandler {
 *       protected override void afterInsert() {
 *           AccountService.assignTerritories((List<Account>) Trigger.new);
 *       }
 *   }
 */
public virtual inherited sharing class TriggerHandler {

    private static Map<String, Integer> runCounts = new Map<String, Integer>();
    private static Set<String> bypassed = new Set<String>();

    /** Max re-entries per handler per transaction before short-circuiting. */
    protected Integer maxLoopCount = 5;

    public void run() {
        String name = handlerName();
        if (bypassed.contains(name)) { return; }
        Integer count = runCounts.containsKey(name) ? runCounts.get(name) : 0;
        if (count >= maxLoopCount) { return; }
        runCounts.put(name, count + 1);

        if (Trigger.isBefore && Trigger.isInsert)   { beforeInsert(); }
        else if (Trigger.isBefore && Trigger.isUpdate)  { beforeUpdate(); }
        else if (Trigger.isBefore && Trigger.isDelete)  { beforeDelete(); }
        else if (Trigger.isAfter && Trigger.isInsert)   { afterInsert(); }
        else if (Trigger.isAfter && Trigger.isUpdate)   { afterUpdate(); }
        else if (Trigger.isAfter && Trigger.isDelete)   { afterDelete(); }
        else if (Trigger.isAfter && Trigger.isUndelete) { afterUndelete(); }
    }

    // Override the contexts you need; empty defaults keep handlers small.
    protected virtual void beforeInsert() {}
    protected virtual void beforeUpdate() {}
    protected virtual void beforeDelete() {}
    protected virtual void afterInsert() {}
    protected virtual void afterUpdate() {}
    protected virtual void afterDelete() {}
    protected virtual void afterUndelete() {}

    /** Bypass a handler for the rest of the transaction (data loads, test setup). */
    public static void bypass(String handlerName) { bypassed.add(handlerName); }
    public static void clearBypass(String handlerName) { bypassed.remove(handlerName); }
    public static void clearAllBypasses() { bypassed.clear(); }

    private String handlerName() {
        return String.valueOf(this).substringBefore(':');
    }
}
