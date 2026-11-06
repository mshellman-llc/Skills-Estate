#!/usr/bin/env python3
"""Selftest for arch_check.py (apply-salesforce-patterns).

Builds a fixture repo in a temp dir, runs the checker, and asserts the findings.
Stdlib only. The regex engine is always tested; the PMD engine is tested too when
a PMD 7 binary is discoverable ($PMD_BIN or `pmd` on PATH), and skipped with a
notice otherwise so verify.sh passes on machines without PMD.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ARCH_CHECK = os.path.join(HERE, "arch_check.py")

FIXTURES = {
    "force-app/classes/BadController.cls": """
public with sharing class BadController {
    @AuraEnabled(cacheable=true)
    public static List<Account> getAccounts() {
        return [SELECT Id, Name FROM Account WITH USER_MODE LIMIT 5];
    }
    @AuraEnabled
    public static void saveIt(Id acctId) {
        update new Account(Id = acctId, Name = 'x');
    }
    // ARCH-EXEMPT
    public static void badExemption() {}
}
""",
    "force-app/classes/AccountsSelector.cls": """
public inherited sharing class AccountsSelector {
    public List<Account> good(Set<Id> ids) {
        return [SELECT Id FROM Account WHERE Id IN :ids WITH USER_MODE];
    }
    public List<Account> bad() {
        return [SELECT Id FROM Account LIMIT 10];
    }
    public List<Account> exempted() {
        return [SELECT Id FROM Account]; // ARCH-EXEMPT: APX003 rollup runs as system by design
    }
}
""",
    "force-app/classes/AccountService.cls": """
public inherited sharing class AccountService {
    public static void one(Account a) { System.debug(a); }
    public static void many(List<Account> accts) { System.debug(accts); }
}
""",
    "force-app/classes/NestedShapes.cls": """
public class NestedShapes {
    public static Map<Id, Map<String, List<Opportunity>>> deep() { return null; }
    public static Map<Id, List<Contact>> shallow() { return null; }
    public static void ops(Boolean f) { if (f && 1 < 2) { System.debug('strings with insert and [SELECT Id FROM Case]'); } }
}
""",
    "force-app/classes/legacy/OldUtil.cls": """
public class OldUtil {
    public static void doStuff() {
        List<Contact> cs = [SELECT Id FROM Contact LIMIT 1];
        delete cs;
    }
}
""",
    "force-app/classes/vendored/FrameworkGuts.cls": """
public class FrameworkGuts {
    public void run() { insert new Account(Name = 'excluded path'); }
}
""",
    "force-app/classes/SomethingTest.cls": """
@IsTest
private class SomethingTest {
    @IsTest static void t() {
        insert new Account(Name = 'T');
        System.assertEquals(1, [SELECT COUNT() FROM Account]);
    }
}
""",
    "force-app/classes/NakedSelector.cls": """
public class NakedSelector {
    @SuppressWarnings('PMD.QueryWithoutUserMode')
    public void a() {}
    public void b() {
        System.debug('x'); // NOPMD
    }
}
""",
    "force-app/classes/UnitOfWork.cls": """
public class UnitOfWork {
    public void commitWork(List<SObject> recs) { insert recs; }
}
""",
    "force-app/triggers/GoodTrigger.trigger": """
trigger GoodTrigger on Account (before insert, after update) {
    new AccountTriggerHandler().run();
}
""",
    "force-app/triggers/TafTrigger.trigger": """
trigger TafTrigger on Case (after insert) {
    new MetadataTriggerHandler().run();
}
""",
    "force-app/triggers/BadTrigger.trigger": """
trigger BadTrigger on Contact (after insert) {
    for (Contact c : Trigger.new) {
        insert new Task(WhoId = c.Id);
    }
}
""",
    "force-app/lwc/myCmp/myCmp.js": """
import { LightningElement, wire } from 'lwc';
import rows from '@salesforce/apex/Ctl.rows';
import { getRecord } from 'lightning/uiRecordApi';
export default class MyCmp extends LightningElement {
    @wire(rows) wired;
    @wire(getRecord, { recordId: '$id', fields: [] }) rec;
}
""",
}

CONFIG = {
    "mode": "block",
    "legacyPaths": ["force-app/classes/legacy/**"],
    "excludePaths": ["force-app/classes/vendored/**"],
    "rules": {},
    "dmlAllowlist": ["UnitOfWork"],
}

# (rule, file basename, severity) triples that MUST be present, per engine.
EXPECTED_COMMON = {
    ("APX001", "BadController.cls", "block"),
    ("APX002", "BadController.cls", "block"),
    ("APX004", "BadController.cls", "warn"),
    ("META001", "BadController.cls", "block"),
    ("APX003", "AccountsSelector.cls", "block"),
    ("APX006", "AccountService.cls", "warn"),
    ("APX007", "NestedShapes.cls", "warn"),
    ("APX001", "OldUtil.cls", "warn"),      # legacy path: downgraded
    ("APX002", "OldUtil.cls", "warn"),
    ("APX005", "BadTrigger.trigger", "block"),
    ("APX002", "BadTrigger.trigger", "block"),
    ("LWC001", "myCmp.js", "warn"),
    ("META002", "NakedSelector.cls", "block"),
}

# Files that must produce NO findings under any engine.
CLEAN_FILES = {"GoodTrigger.trigger", "TafTrigger.trigger", "UnitOfWork.cls",
               "SomethingTest.cls", "FrameworkGuts.cls"}

failures = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok    {label}")
    else:
        failures.append(label)
        print(f"  FAIL  {label}  {detail}")


def run_engine(root, engine):
    proc = subprocess.run(
        [sys.executable, ARCH_CHECK, "--paths", "force-app", "--engine", engine, "--json"],
        cwd=root, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        check(f"{engine}: checker ran", False, proc.stderr[-500:])
        return None
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        check(f"{engine}: JSON output parses", False, proc.stdout[:200])
        return None
    report["exit"] = proc.returncode
    return report


def assert_engine(report, engine):
    got = {(f["rule"], os.path.basename(f["file"]), f["severity"])
           for f in report["findings"]}
    for triple in sorted(EXPECTED_COMMON):
        check(f"{engine}: finds {triple}", triple in got)
    flagged_files = {os.path.basename(f["file"]) for f in report["findings"]}
    for clean in sorted(CLEAN_FILES):
        check(f"{engine}: {clean} stays clean", clean not in flagged_files)
    exempt_hits = [f for f in report["findings"]
                   if os.path.basename(f["file"]) == "AccountsSelector.cls"
                   and f["rule"] == "APX003"]
    check(f"{engine}: ARCH-EXEMPT honored (1 APX003, not 2)", len(exempt_hits) == 1,
          f"got {len(exempt_hits)}")
    shallow_ok = not any(f["rule"] == "APX007" and f["line"] >= 3
                         for f in report["findings"]
                         if os.path.basename(f["file"]) == "NestedShapes.cls")
    check(f"{engine}: 2-level nesting not flagged", shallow_ok)
    check(f"{engine}: blocking exit code", report["exit"] == 1)


def main():
    with tempfile.TemporaryDirectory(prefix="arch_selftest_") as root:
        for rel, content in FIXTURES.items():
            dest = os.path.join(root, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(content.lstrip("\n"))
        with open(os.path.join(root, ".arch-check.json"), "w", encoding="utf-8") as f:
            json.dump(CONFIG, f)

        print("== regex engine ==")
        report = run_engine(root, "regex")
        if report:
            assert_engine(report, "regex")

        pmd = os.environ.get("PMD_BIN") or shutil.which("pmd")
        if pmd:
            print("== pmd engine ==")
            report = run_engine(root, "pmd")
            if report:
                assert_engine(report, "pmd")
        else:
            print("== pmd engine == SKIPPED (no PMD binary; regex engine covered above)")

    if failures:
        print(f"\nSELFTEST FAILED: {len(failures)} assertion(s)")
        return 1
    print("\nSELFTEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
