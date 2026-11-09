#!/usr/bin/env python3
"""Selftest for references/tools/gen-permset.py. Stdlib only, fully offline.

Builds throwaway SFDX fixtures in a temp directory and asserts the behaviour that is easy to
break by accident and expensive to discover in an org:

  * the four EMPIRICAL classification rules (MasterDetail, required, derived-field read-only)
  * the write-refusal matrix, which must follow the TARGET tree rather than the shell's cwd
  * the fresh-worktree case: a branch with no source directory is still a valid target
  * record types with the same basename on two objects both survive de-duplication
  * output is well-formed XML whose elements are in the Metadata API's alphabetical sequence
  * regeneration is idempotent, and check mode reports drift honestly

Run directly, or via the repo's verify.sh.
"""
import os
import re
import sys
import json
import shutil
import tempfile
import subprocess
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.join(os.path.dirname(HERE), "references", "tools", "gen-permset.py")

FAILURES = []
CHECKS = [0]


def check(label, condition, detail=""):
    CHECKS[0] += 1
    if condition:
        print("  ok   %s" % label)
    else:
        print("  FAIL %s%s" % (label, ("  <- " + detail) if detail else ""))
        FAILURES.append(label)


def run(*args, cwd=None):
    proc = subprocess.run([sys.executable, TOOL] + list(args), cwd=cwd,
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def git(*args, cwd):
    return subprocess.run(["git"] + list(args), cwd=cwd, capture_output=True, text=True)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


FIELD = ('<?xml version="1.0" encoding="UTF-8"?>\n'
         '<CustomField xmlns="http://soap.sforce.com/2006/04/metadata">\n'
         '<fullName>%s</fullName>\n%s</CustomField>\n')
RECTYPE = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<RecordType xmlns="http://soap.sforce.com/2006/04/metadata">'
           '<fullName>Standard</fullName></RecordType>\n')


def build_fixture(root, layout="standard"):
    """An SFDX project exercising every classification branch, committed to a git repo."""
    os.makedirs(root, exist_ok=True)
    pkg = "force-app"
    write(os.path.join(root, "sfdx-project.json"), json.dumps({
        "packageDirectories": [{"path": pkg, "default": True}],
        "name": "fixture", "namespace": "", "sourceApiVersion": "66.0"}) + "\n")
    d = os.path.join(root, pkg) if layout == "flat" else os.path.join(root, pkg, "main", "default")

    fields = {
        # Widget__c covers all four empirical rules plus a plain field and a config read-only.
        "Widget__c/XID__c": "<type>Text</type><length>64</length><externalId>true</externalId>",
        "Widget__c/Total__c": "<type>Summary</type><summaryOperation>sum</summaryOperation>",
        "Widget__c/Calc__c": "<type>Text</type><formula>1</formula>",
        "Widget__c/Seq__c": "<type>AutoNumber</type>",
        "Widget__c/Parent__c": "<type>MasterDetail</type>",
        "Widget__c/Needed__c": "<type>Text</type><required>true</required>",
        "Widget__c/Stamp__c": "<type>Text</type>",
        "Gadget__c/Note__c": "<type>Text</type>",
        "Account/Region__c": "<type>Text</type>",
        "Setting__c/Val__c": "<type>Text</type>",
        "Cfg__mdt/Key__c": "<type>Text</type>",
        "Ping__e/Payload__c": "<type>Text</type>",
    }
    for key, body in fields.items():
        obj, name = key.split("/")
        write(os.path.join(d, "objects", obj, "fields", name + ".field-meta.xml"),
              FIELD % (name, body))

    write(os.path.join(d, "objects", "Setting__c", "Setting__c.object-meta.xml"),
          '<?xml version="1.0" encoding="UTF-8"?>\n<CustomObject '
          'xmlns="http://soap.sforce.com/2006/04/metadata">'
          '<customSettingsType>List</customSettingsType></CustomObject>\n')

    # Same record type NAME on two objects: a basename-keyed de-dup silently drops one.
    for obj in ("Widget__c", "Gadget__c"):
        write(os.path.join(d, "objects", obj, "recordTypes", "Standard.recordType-meta.xml"),
              RECTYPE)

    write(os.path.join(d, "classes", "Svc.cls"), "public class Svc {}\n")
    write(os.path.join(d, "classes", "SvcTest.cls"), "public class SvcTest {}\n")
    write(os.path.join(d, "tabs", "Widget__c.tab-meta.xml"), "<CustomTab/>\n")
    write(os.path.join(d, "applications", "Fix_App.app-meta.xml"), "<CustomApplication/>\n")
    write(os.path.join(d, "pages", "Legacy.page"), "<apex:page/>\n")
    write(os.path.join(d, "customPermissions", "Do_Thing.customPermission-meta.xml"),
          "<CustomPermission/>\n")

    write(os.path.join(root, "config", "permset-gen.json"), json.dumps({
        "api_name": "Fixture_Admin",
        "label": "Fixture Admin",
        "description": "Generated from source. Do not hand-edit.",
        "standard_object_access": ["Account"],
        "standard_tabs": ["standard-Contact"],
        "no_delete": ["Gadget__c"],
        "read_only": ["Widget__c.Stamp__c"],
        "user_permissions": ["ViewSetup"],
    }, indent=2) + "\n")

    git("init", "-q", ".", cwd=root)
    git("config", "user.email", "selftest@example.invalid", cwd=root)
    git("config", "user.name", "selftest", cwd=root)
    git("add", "-A", cwd=root)
    git("commit", "-qm", "fixture", cwd=root)
    return d


def field_entries(xml_text):
    """{api name: editable} from the rendered permission set."""
    out = {}
    for block in re.findall(r"<fieldPermissions>(.*?)</fieldPermissions>", xml_text, re.S):
        name = re.search(r"<field>(.*?)</field>", block).group(1)
        out[name] = re.search(r"<editable>(.*?)</editable>", block).group(1) == "true"
    return out


def test_classification(tmp):
    print("classification rules (empirical -- a deploy fails if these regress)")
    root = os.path.join(tmp, "cls")
    build_fixture(root)
    code, out = run("--out", os.path.join(tmp, "cls.xml"), cwd=root)
    check("exit 0 for --out in the main checkout", code == 0, out.strip())
    xml_text = open(os.path.join(tmp, "cls.xml")).read()
    f = field_entries(xml_text)

    check("MasterDetail field omitted", "Widget__c.Parent__c" not in f)
    check("required=true field omitted", "Widget__c.Needed__c" not in f)
    check("roll-up summary is read-only", f.get("Widget__c.Total__c") is False)
    check("formula field is read-only", f.get("Widget__c.Calc__c") is False)
    check("AutoNumber field is read-only", f.get("Widget__c.Seq__c") is False)
    check("config read_only honoured", f.get("Widget__c.Stamp__c") is False)
    check("plain field is editable", f.get("Widget__c.XID__c") is True)
    check("standard-object field still gets FLS", f.get("Account.Region__c") is True)
    check("custom metadata field skipped", "Cfg__mdt.Key__c" not in f)
    check("platform event field skipped", "Ping__e.Payload__c" not in f)

    objs = re.findall(r"<object>(.*?)</object>", xml_text)
    check("listed standard object gets CRUD", "Account" in objs)
    check("unlisted standard object gets none", "Opportunity" not in objs)
    check("custom setting skipped from objectPermissions", "Setting__c" not in objs)
    check("custom metadata type not in objectPermissions", "Cfg__mdt" not in objs)
    check("customMetadataTypeAccesses emitted", "<name>Cfg__mdt</name>" in xml_text)

    gadget = re.search(r"<objectPermissions>(?:(?!</objectPermissions>).)*?"
                       r"<object>Gadget__c</object>.*?</objectPermissions>", xml_text, re.S)
    check("no_delete withholds delete", gadget and "<allowDelete>false</allowDelete>" in gadget.group(0))
    ping = re.search(r"<objectPermissions>(?:(?!</objectPermissions>).)*?"
                     r"<object>Ping__e</object>.*?</objectPermissions>", xml_text, re.S)
    check("platform event gets no edit", ping and "<allowEdit>false</allowEdit>" in ping.group(0))

    rts = re.findall(r"<recordType>(.*?)</recordType>", xml_text)
    check("same-named record types on two objects both kept",
          "Widget__c.Standard" in rts and "Gadget__c.Standard" in rts, str(rts))

    check("derived tabs plus configured standard tab",
          "<tab>Widget__c</tab>" in xml_text and "<tab>standard-Contact</tab>" in xml_text)
    check("apex class access derived", "<apexClass>SvcTest</apexClass>" in xml_text)
    check("visualforce page access derived", "<apexPage>Legacy</apexPage>" in xml_text)
    check("custom permission derived", "<name>Do_Thing</name>" in xml_text)
    check("user permission passed through", "<name>ViewSetup</name>" in xml_text)
    check("flowAccesses off by default", "<flowAccesses>" not in xml_text)
    return xml_text


def test_xml_shape(xml_text):
    print("output shape")
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        check("well-formed XML", False, str(exc))
        return
    check("well-formed XML", True)
    tags, seen = [], None
    for child in root:
        name = re.sub(r"\{.*\}", "", child.tag)
        if name != seen:
            tags.append(name)
            seen = name
    check("elements in the Metadata API's alphabetical sequence", tags == sorted(tags), str(tags))


def test_refusals(tmp):
    """The refusal follows the TARGET tree, never the shell's cwd."""
    print("write-refusal matrix")
    if not shutil.which("git"):
        print("  SKIP no git on PATH")
        return
    root = os.path.join(tmp, "ref")
    build_fixture(root)
    wt = os.path.join(tmp, "ref-wt")
    res = git("worktree", "add", "-q", wt, "-b", "feat/1-x", cwd=root)
    if res.returncode != 0:
        check("git worktree add", False, res.stderr.strip())
        return

    code, out = run("--write", cwd=root)
    check("--write from the main clone is refused", code == 2 and "REFUSED" in out, out.strip())

    code, out = run("--write", "--tree", root, cwd=wt)
    check("--write --tree <main clone> refused from inside a worktree",
          code == 2 and "REFUSED" in out, out.strip())

    cfg = os.path.join(root, "config", "permset-gen.json")
    code, out = run("--write", "--tree", wt, "--config", cfg, cwd=root)
    written = os.path.join(wt, "force-app", "main", "default", "permissionsets",
                           "Fixture_Admin.permissionset-meta.xml")
    check("--write --tree <worktree> from the main clone succeeds", code == 0, out.strip())
    check("the worktree received the file", os.path.isfile(written))
    check("the main clone was not touched",
          not os.path.exists(os.path.join(root, "force-app", "main", "default", "permissionsets")))

    code, out = run("--config", cfg, cwd=wt)
    check("check mode reports up to date after a write",
          code == 0 and "up to date" in out, out.strip())

    before = open(written).read()
    code, _ = run("--write", "--config", cfg, cwd=wt)
    check("regeneration is idempotent", code == 0 and open(written).read() == before)

    shutil.copy2(written, written + ".before-drift-test")
    os.remove(written)
    code, out = run("--config", cfg, "--fail-on-drift", cwd=wt)
    check("--fail-on-drift exits 3 when stale", code == 3, "exit %d" % code)

    shutil.copytree(wt, wt + "-evidence", symlinks=True)
    git("worktree", "remove", "--force", wt, cwd=root)


def test_layouts(tmp):
    """Where the file lands must not depend on whether metadata exists on disk yet."""
    print("package-directory layouts")
    if not shutil.which("git"):
        print("  SKIP no git on PATH")
        return

    root = os.path.join(tmp, "fresh")
    os.makedirs(root)
    write(os.path.join(root, "sfdx-project.json"), json.dumps({
        "packageDirectories": [{"path": "force-app", "default": True}],
        "name": "fresh", "namespace": "", "sourceApiVersion": "66.0"}) + "\n")
    write(os.path.join(root, "config", "permset-gen.json"),
          json.dumps({"api_name": "Fresh_Admin", "label": "Fresh Admin"}) + "\n")
    git("init", "-q", ".", cwd=root)
    git("config", "user.email", "selftest@example.invalid", cwd=root)
    git("config", "user.name", "selftest", cwd=root)
    git("add", "-A", cwd=root)
    git("commit", "-qm", "no metadata yet", cwd=root)
    wt = os.path.join(tmp, "fresh-wt")
    git("worktree", "add", "-q", wt, "-b", "feat/1-first", cwd=root)

    check("a worktree with no source directory has none on disk",
          not os.path.exists(os.path.join(wt, "force-app")))
    code, out = run("--write", "--tree", wt,
                    "--config", os.path.join(root, "config", "permset-gen.json"), cwd=root)
    check("the fresh worktree is a valid target (sentinel is sfdx-project.json)",
          code == 0, out.strip())
    check("it lands on the standard path, not a flat one",
          os.path.isfile(os.path.join(wt, "force-app", "main", "default", "permissionsets",
                                      "Fresh_Admin.permissionset-meta.xml")))
    shutil.copytree(wt, wt + "-evidence", symlinks=True)
    git("worktree", "remove", "--force", wt, cwd=root)

    flat = os.path.join(tmp, "flat")
    build_fixture(flat, layout="flat")
    code, out = run("--out", os.path.join(tmp, "flat.xml"), cwd=flat)
    check("a genuinely flat package directory still resolves", code == 0, out.strip())
    code, out = run(cwd=flat)
    check("flat output path has no main/default", "force-app/permissionsets/" in out, out.strip())


def test_config_errors(tmp):
    print("config handling")
    root = os.path.join(tmp, "cfg")
    build_fixture(root)
    cfg = os.path.join(root, "config", "permset-gen.json")

    with open(cfg) as fh:
        good = json.load(fh)
    bad = dict(good)
    bad.pop("api_name")
    write(cfg, json.dumps(bad))
    code, out = run(cwd=root)
    check("a config missing api_name is refused", code == 2 and "api_name" in out, out.strip())

    bad = dict(good)
    bad["description"] = "x" * 256
    write(cfg, json.dumps(bad))
    code, out = run(cwd=root)
    check("an over-long description is refused before the platform sees it",
          code == 2 and "255" in out, out.strip())

    write(cfg, "{not json")
    code, out = run(cwd=root)
    check("invalid JSON is refused with the path named", code == 2 and "JSON" in out, out.strip())

    os.remove(cfg)
    code, out = run(cwd=root)
    check("a missing config points at --init", code == 2 and "--init" in out, out.strip())
    code, out = run("--init", cwd=root)
    check("--init writes a starter config", code == 0 and os.path.isfile(cfg), out.strip())
    code, out = run("--init", cwd=root)
    check("--init refuses to clobber an existing config", code == 2, out.strip())


def main():
    print("gen-permset selftest")
    if not os.path.isfile(TOOL):
        print("  FAIL tool not found at %s" % TOOL)
        return 1

    temporary = tempfile.TemporaryDirectory(prefix="gen-permset-selftest-")
    tmp = temporary.name
    try:
        xml_text = test_classification(tmp)
        test_xml_shape(xml_text)
        test_refusals(tmp)
        test_layouts(tmp)
        test_config_errors(tmp)
    finally:
        temporary.cleanup()

    print()
    if FAILURES:
        print("FAILED %d of %d checks:" % (len(FAILURES), CHECKS[0]))
        for f in FAILURES:
            print("  - %s" % f)
        return 1
    print("PASSED %d checks" % CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
