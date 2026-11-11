/**
 * UnitOfWork — lean, owned transaction manager. The ONLY class that performs DML.
 * (Aleysian house architecture; arch_check rule APX002 enforces this.)
 *
 * Register changes from services, commit once at the transaction boundary.
 * DML executes in type registration order for inserts/updates, reverse for deletes,
 * so register parents before children.
 *
 * Usage:
 *   UnitOfWork uow = new UnitOfWork(new List<Schema.SObjectType>{
 *       Account.SObjectType, Contact.SObjectType });
 *   uow.registerNew(acct);
 *   uow.registerRelationship(con, Contact.AccountId, acct); // resolves Id at commit
 *   uow.registerNew(con);
 *   uow.registerDirty(existingOpp);
 *   uow.registerDeleted(staleTask);
 *   uow.commitWork();
 */
public inherited sharing class UnitOfWork {

    private List<Schema.SObjectType> order;
    private Map<String, List<SObject>> newByType = new Map<String, List<SObject>>();
    private Map<String, Map<Id, SObject>> dirtyByType = new Map<String, Map<Id, SObject>>();
    private Map<String, Map<Id, SObject>> deletedByType = new Map<String, Map<Id, SObject>>();
    private List<Relationship> relationships = new List<Relationship>();
    private Boolean committed = false;

    public UnitOfWork(List<Schema.SObjectType> typeOrder) {
        this.order = typeOrder;
        for (Schema.SObjectType t : typeOrder) {
            String key = String.valueOf(t);
            newByType.put(key, new List<SObject>());
            dirtyByType.put(key, new Map<Id, SObject>());
            deletedByType.put(key, new Map<Id, SObject>());
        }
    }

    public void registerNew(SObject record) {
        assertOpen();
        if (record.Id != null) {
            throw new UnitOfWorkException('registerNew called with an existing record; use registerDirty');
        }
        listFor(newByType, record).add(record);
    }

    public void registerNew(List<SObject> records) {
        for (SObject r : records) { registerNew(r); }
    }

    public void registerDirty(SObject record) {
        assertOpen();
        if (record.Id == null) {
            throw new UnitOfWorkException('registerDirty called with a new record; use registerNew');
        }
        mapFor(dirtyByType, record).put(record.Id, record);
    }

    public void registerDirty(List<SObject> records) {
        for (SObject r : records) { registerDirty(r); }
    }

    public void registerDeleted(SObject record) {
        assertOpen();
        mapFor(deletedByType, record).put(record.Id, record);
    }

    public void registerDeleted(List<SObject> records) {
        for (SObject r : records) { registerDeleted(r); }
    }

    /** Point child.field at a parent that may not have an Id yet; resolved at commit. */
    public void registerRelationship(SObject child, Schema.SObjectField field, SObject parent) {
        assertOpen();
        relationships.add(new Relationship(child, field, parent));
    }

    /** Single commit point. Inserts in type order, updates in type order, deletes reversed. */
    public void commitWork() {
        assertOpen();
        committed = true;
        Savepoint sp = Database.setSavepoint();
        try {
            for (Schema.SObjectType t : order) {
                resolveRelationships();
                List<SObject> toInsert = newByType.get(String.valueOf(t));
                if (!toInsert.isEmpty()) { insert toInsert; }
            }
            resolveRelationships();
            for (Schema.SObjectType t : order) {
                Map<Id, SObject> toUpdate = dirtyByType.get(String.valueOf(t));
                if (!toUpdate.isEmpty()) { update toUpdate.values(); }
            }
            for (Integer i = order.size() - 1; i >= 0; i--) {
                Map<Id, SObject> toDelete = deletedByType.get(String.valueOf(order[i]));
                if (!toDelete.isEmpty()) { delete toDelete.values(); }
            }
        } catch (Exception e) {
            Database.rollback(sp);
            throw e;
        }
    }

    private void resolveRelationships() {
        for (Relationship rel : relationships) {
            if (rel.parent.Id != null) {
                rel.child.put(rel.field, rel.parent.Id);
            }
        }
    }

    private List<SObject> listFor(Map<String, List<SObject>> store, SObject record) {
        String key = String.valueOf(record.getSObjectType());
        if (!store.containsKey(key)) {
            throw new UnitOfWorkException(key + ' was not registered in the UnitOfWork type order');
        }
        return store.get(key);
    }

    private Map<Id, SObject> mapFor(Map<String, Map<Id, SObject>> store, SObject record) {
        String key = String.valueOf(record.getSObjectType());
        if (!store.containsKey(key)) {
            throw new UnitOfWorkException(key + ' was not registered in the UnitOfWork type order');
        }
        return store.get(key);
    }

    private void assertOpen() {
        if (committed) {
            throw new UnitOfWorkException('UnitOfWork already committed; create a new one per transaction');
        }
    }

    private class Relationship {
        SObject child; Schema.SObjectField field; SObject parent;
        Relationship(SObject c, Schema.SObjectField f, SObject p) { child = c; field = f; parent = p; }
    }

    public class UnitOfWorkException extends Exception {}
}
