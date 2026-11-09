#!/usr/bin/env python3
"""Generate a project's permission set from what is actually on disk.

    python3 scripts/gen-permset.py                       # CHECK ONLY -- reports drift, writes nothing
    python3 scripts/gen-permset.py --write               # actually write (worktrees only)
    python3 scripts/gen-permset.py --write --tree PATH   # write into another checkout
    python3 scripts/gen-permset.py --out /tmp/next.xml   # new preview outside SFDX projects
    python3 scripts/gen-permset.py --init                # write a starter config and exit

WHY THIS EXISTS -- read before deciding you do not need it.

A single project-wide permission set is the one file every parallel agent touches. Hand-authored,
it is a guaranteed merge conflict the moment two worktrees each add a field, and the usual
"fix" -- let each agent skip it and grant FLS later -- trades a visible conflict for an invisible
gap: the field deploys, nobody can see it, and the failure surfaces in a later wave as a phantom
"field does not exist" that reads like a data-model bug and is not.

Deriving the file from the source tree dissolves both. Two branches that each add fields converge
the moment the file is regenerated against the merged tree -- there is nothing to hand-merge,
because the file is a pure function of what is on disk. And because the coordinator regenerates
into the agent's worktree *before* merging, the fields and their FLS land in the same PR and the
same deploy. No conflict, no window where a deployed field is invisible.

THE CONTRACT (this is the part agents get wrong):

  You are               You do
  --------------------  ------------------------------------------------------------------
  A worktree agent      NEVER edit the permission set. NEVER run --write. Run check mode
                        (`npm run permset`) to confirm your new fields are still ungranted,
                        and say so in your report. That is all.
  The coordinator       From the main clone, as the last step before merging:
                        `--write --tree <agent worktree>`, commit it into the worktree,
                        RE-VALIDATE (the merge gate is per-commit and you just added one),
                        then merge and deploy.

Check mode is the default on purpose. Writing needs --write, and the tree being written must be a
git worktree: the source directory is never authored in the main checkout, and
`guard-force-app-bash.sh` enforces that. This script refuses it too, so neither you nor the guard
has to be the only line of defence.

`--tree PATH` retargets both the reads and the write. That is how a coordinator standing in the
main clone regenerates into a worktree without bouncing the PR back to an agent. **The refusal
follows the target, not your cwd** -- `--tree <a worktree>` is allowed from anywhere, and
`--tree <the main clone>` is refused from anywhere, including from inside a worktree. That mirrors
`guard-force-app-bash.sh`, which has always judged the target path rather than the working
directory. Without it the script would be stricter than the policy it exists to enforce, and every
generated-file conflict would have to bounce back to an agent.

NEVER HAND-EDIT THE OUTPUT. A real project has hundreds of field entries; a hand edit invites
exactly the silent omission this script exists to prevent.

Run it after adding ANY object, field, record type, tab, app, page or Apex class. Everything is
derived from the tree, so new metadata is picked up automatically. The only things needing human
maintenance live in the config file (see --init): the no-delete list, the read-only allow-list,
and any explicit standard-object / standard-tab grants.

If the project formats XML at commit time (Prettier with @prettier/plugin-xml), a regeneration
with no metadata change produces a whitespace-only diff. That is expected; check mode compares on
content, not bytes, so it does not report that as drift.

CLASSIFICATION RULES -- preserved from the historical implementation. Offline tests verify
these classifications; this repaired version has not been deployed to an org:

  * MasterDetail relationship fields are omitted entirely -- the platform REJECTS FLS on them.
  * Universally-required fields (<required>true</required>) are omitted entirely: "You cannot
    deploy to a required field: <name>". A required field is unconditionally visible and editable
    to anyone holding object access, so nothing is lost.
  * <formula>, <summaryOperation> and type=AutoNumber are read-only by nature. Emitting
    editable=true on one is a DEPLOY ERROR, not a warning.
  * Other supported fields get readable=true, editable=true, unless the config's read_only list
    names it.

The remaining classifications (platform events, big objects, external objects, custom metadata
types, custom settings) are conservative platform-shape defaults rather than empirical findings
from one org: where a metadata type's support for FLS or CRUD is partial or uncertain, this script
SKIPS and REPORTS rather than guessing. A skip is visible in the summary; a wrong guess is a
deploy error. Every one of them is overridable in the config.

A permission set only ever GRANTS. It cannot revoke what a Profile already allows, so a withheld
delete does nothing for a System Administrator. That is correct design intent and correct for a
minimum-access user -- it is not a demonstrable guarantee in an org you are running as admin. Say
so rather than claiming delete-immunity.
"""
import os
import re
import sys
import json
import glob
import fnmatch
import subprocess
import argparse
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

CONFIG_DEFAULT = os.path.join("config", "permset-gen.json")

# Order matters: the Metadata API's PermissionSet type is an alphabetically-ordered sequence, and
# the deploy rejects elements out of order. Anything added here goes in its alphabetical slot.
EXAMPLE_CONFIG = {
    "api_name": "My_Project_Admin",
    "label": "My Project Admin",
    "description": "Single permission set for this project. Generated from source by scripts/gen-permset.py -- do not hand-edit.",
    "standard_object_access": [],
    "standard_tabs": [],
    "no_delete": [],
    "read_only": [],
    "exclude_objects": [],
    "exclude_fields": [],
    "exclude_tabs": [],
    "exclude_apex_classes": [],
    "user_permissions": [],
    "extra_custom_permissions": [],
    "derive": {
        "applications": True,
        "apex_classes": True,
        "apex_pages": True,
        "custom_metadata_types": True,
        "custom_permissions": True,
        "record_types": True,
        "tabs": True,
        "flows": False,
    },
}

CONFIG_HELP = """\
Config reference (JSON; globs allowed everywhere marked *):

  api_name                 REQUIRED. Permission set API name -> <api_name>.permissionset-meta.xml
  label                    REQUIRED. Display label.
  description              Optional, max 255 chars (platform cap). Say "generated" in it.
  license                  Optional permission set license.
  output                   Optional explicit output path, relative to the tree root.

  standard_object_access*  Standard objects needing object-level CRUD, not just FLS.
                           FLS WITHOUT OBJECT ACCESS IS INERT -- it only looks correct because
                           your admin profile is supplying the CRUD. Omitting an object here is
                           a real decision (e.g. keeping Opportunity out of ops hands); write
                           down why in the config, or someone will "fix" it.
  standard_tabs*           e.g. "standard-Contact". Custom tabs are derived from tabs/.

  no_delete*               Objects that get allowCreate/Edit/Read but NOT allowDelete.
                           Append-only semantics a validation rule cannot enforce, because
                           validation rules DO NOT FIRE ON DELETE. List BOTH halves of a
                           master-detail pair: a cascade delete of the master takes its details
                           regardless of the child's permissions.
  read_only*               "Object__c.Field__c" entries that get readable=true, editable=false.
                           For plain fields that are conceptually derived but could not be a real
                           formula or roll-up. Prefer making it a real roll-up/formula where you
                           can -- the platform then enforces it and no entry is needed here.

  exclude_objects*         Objects to omit from objectPermissions entirely.
  exclude_fields*          "Object__c.Field__c" entries to omit from fieldPermissions entirely.
  exclude_tabs*            Derived tabs to omit.
  exclude_apex_classes*    Derived Apex classes to omit.

  user_permissions*        Literal user permission names (e.g. "ViewSetup"). Not derivable.
  extra_custom_permissions Custom permissions beyond those found in customPermissions/.

  derive.<thing>           Toggle each derived section. Defaults are the proven set;
                           `flows` is OFF by default -- see the note in derive_flows().
  field_permissions_for    Object kinds that get fieldPermissions. Default ["standard","custom"];
                           the others ("custom_setting", "platform_event", "big_object",
                           "external_object", "custom_metadata") are skipped and REPORTED.
  custom_settings          "skip" (default) or "object" -- whether custom-setting objects get
                           objectPermissions. If you switch this to "object", add
                           "custom_setting" to field_permissions_for as well: FLS without object
                           access is inert, and object access without FLS shows empty fields.
"""


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------- tree resolution

def find_tree_root(start):
    """Walk up for sfdx-project.json.

    The sentinel is sfdx-project.json, NOT the source directory. Git does not track empty
    directories, so a worktree taken from a branch that has no metadata yet legitimately has no
    force-app/ -- checking for it rejects a perfectly valid fresh-repo worktree. sfdx-project.json
    is tracked and always present.
    """
    cur = os.path.realpath(start)
    while True:
        if os.path.isfile(os.path.join(cur, "sfdx-project.json")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def resolve_repo(argv):
    """--tree wins; otherwise the tree you are standing in; otherwise the script's own repo.

    CWD before script location on purpose: an agent in a worktree may invoke the main clone's copy
    of this script by absolute path, and the tree it means is the one it is standing in.
    """
    if "--tree" in argv:
        try:
            target = os.path.realpath(os.path.expanduser(argv[argv.index("--tree") + 1]))
        except IndexError:
            refuse("--tree needs a path argument.")
        if not os.path.isfile(os.path.join(target, "sfdx-project.json")):
            refuse("--tree %s has no sfdx-project.json -- not a checkout of an SFDX project." % target)
        return target
    return (find_tree_root(os.getcwd())
            or find_tree_root(os.path.dirname(os.path.abspath(__file__)))
            or refuse("no sfdx-project.json found above %s -- run from inside the project, "
                      "or pass --tree PATH." % os.getcwd()))


def metadata_roots(repo):
    """Every packageDirectories path, resolved to where the metadata folders actually live.

    Handles both the standard force-app/main/default layout and a flat package directory.
    Returns [(root, is_default)], default first.
    """
    try:
        with open(os.path.join(repo, "sfdx-project.json")) as fh:
            project = json.load(fh)
            if not isinstance(project, dict):
                refuse("sfdx-project.json must contain an object")
            pkg_dirs = project.get("packageDirectories") or []
    except (ValueError, OSError) as exc:
        refuse("could not read sfdx-project.json: %s" % exc)
    if not pkg_dirs:
        pkg_dirs = [{"path": "force-app", "default": True}]

    # Recognisable metadata folder names, used only to tell a flat package directory from a
    # standard one that has no metadata yet. A worktree off a fresh branch has NEITHER layout on
    # disk (git tracks no empty directories), and guessing "flat" there would write the permission
    # set to force-app/permissionsets/ — a path the standard scaffold never uses again.
    MD_FOLDERS = ("objects", "classes", "lwc", "aura", "tabs", "applications", "flows",
                  "permissionsets", "triggers", "pages", "staticresources", "flexipages")

    roots = []
    if not isinstance(pkg_dirs, list):
        refuse("packageDirectories must be an array")
    for entry in pkg_dirs:
        if not isinstance(entry, dict):
            refuse("each packageDirectories entry must be an object")
        base = checked_path(repo, entry.get("path", "force-app"))
        nested = os.path.join(base, "main", "default")
        flat = any(os.path.isdir(os.path.join(base, d)) for d in MD_FOLDERS)
        if not contained(repo, nested):
            refuse("metadata root escapes the selected project")
        roots.append((base if (flat and not os.path.isdir(nested)) else nested,
                      bool(entry.get("default"))))
    roots.sort(key=lambda r: not r[1])          # default package directory first
    return roots


def in_main_checkout(repo):
    """True in the main clone, False in a worktree. Same git topology the hooks use, so it cannot
    disagree with them."""
    try:
        gd = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=repo,
                            capture_output=True, text=True, check=True).stdout.strip()
        cd = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=repo,
                            capture_output=True, text=True, check=True).stdout.strip()
        return os.path.realpath(os.path.join(repo, gd)) == os.path.realpath(os.path.join(repo, cd))
    except (OSError, subprocess.SubprocessError):
        refuse("--write requires a verified Git worktree; Git topology could not be read.")


# ---------------------------------------------------------------------------- small helpers

def contained(root, path):
    return os.path.commonpath([os.path.realpath(root), os.path.realpath(path)]) == os.path.realpath(root)


def checked_path(repo, relative):
    if not isinstance(relative, str) or not relative or os.path.isabs(relative):
        refuse("project paths must be nonempty relative paths")
    target = os.path.join(repo, relative)
    if not contained(repo, target) or os.path.realpath(target) == os.path.realpath(repo):
        refuse("path escapes the selected project: %s" % relative)
    return target


def xml_root(txt):
    try:
        return ET.fromstring(txt)
    except ET.ParseError as exc:
        refuse("malformed metadata XML: %s" % exc)


def tag(txt, name):
    if not txt:
        return None
    root = xml_root(txt)
    for child in root:
        if child.tag.rsplit("}", 1)[-1] == name:
            return (child.text or "").strip()
    return None


def read(path, optional=False):
    try:
        with open(path, encoding="utf-8") as fh:
            txt = fh.read()
        if path.endswith("-meta.xml"):
            xml_root(txt)
        return txt
    except FileNotFoundError:
        if optional:
            return ""
        refuse("metadata file is missing: %s" % path)
    except (OSError, UnicodeError) as exc:
        refuse("could not read %s: %s" % (path, exc))


def object_metadata(roots, name):
    paths = collect(roots, "objects", name, name + ".object-meta.xml")
    return read(paths[0]) if paths else ""


def matches(value, patterns):
    return any(fnmatch.fnmatchcase(value, p) for p in patterns)


def squash_ws(s):
    """Compare on content, ignoring whitespace an XML formatter rewrites at commit time.

    Prettier wraps long lines as `<description\n  >text</description>`, so a naive comparison
    reports drift on a file that is byte-for-byte correct in substance.
    """
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s+>", ">", s)                 # `<description >` -> `<description>`
    s = re.sub(r">\s+<", "><", s)
    return s.strip()


def collect(roots, *parts):
    """Glob a metadata folder across every package directory, de-duplicated, sorted.

    De-duplication is on the path RELATIVE TO THE METADATA ROOT, never the basename: two objects
    can legitimately own a record type of the same name (Account.Fleet and Job__c.Fleet), and a
    basename key silently drops one of them. Same relative path in two package directories is the
    same component, which is the case this needs to collapse.
    """
    hits = {}
    for root, _ in roots:
        for path in glob.glob(os.path.join(root, *parts)):
            if not contained(root, path):
                refuse("metadata symlink escapes its package: %s" % path)
            if os.path.isfile(path) and path.endswith("-meta.xml"):
                read(path)
            key = os.path.relpath(path, root)
            previous = hits.get(key)
            if previous and os.path.isfile(path):
                if read(previous) != read(path):
                    refuse("conflicting metadata component in multiple packages: %s" % key)
            else:
                hits[key] = path
    return [hits[k] for k in sorted(hits)]


def object_kind(name, meta_txt, cfg):
    if name.endswith("__mdt"):
        return "custom_metadata"
    if name.endswith("__e"):
        return "platform_event"
    if name.endswith("__b"):
        return "big_object"
    if name.endswith("__x"):
        return "external_object"
    if name.endswith("__c"):
        return "custom_setting" if tag(meta_txt, "customSettingsType") is not None else "custom"
    return "standard"


# CRUD shape per object kind. Emitting a permission the type does not support is a deploy error,
# so anything partial is expressed here once rather than special-cased at the call site.
#            create  edit   delete-allowed
CRUD = {
    "custom":          (True,  True,  True),
    "custom_setting":  (True,  True,  True),
    "standard":        (True,  True,  True),
    "platform_event":  (True,  False, False),   # publish + subscribe; no update or delete
    "big_object":      (True,  False, False),   # insert + query only
    "external_object": (False, False, False),   # read-only by nature
}


# ---------------------------------------------------------------------------- derivation

def derive_objects(roots, cfg, report):
    """Object directories -> (object permissions, custom metadata type accesses)."""
    obj_dirs = collect(roots, "objects", "*")
    obj_perms, cmdt, skipped = [], [], []
    std_allow = cfg["standard_object_access"]

    for path in obj_dirs:
        name = os.path.basename(path.rstrip(os.sep))
        kind = object_kind(name, object_metadata(roots, name), cfg)

        if matches(name, cfg["exclude_objects"]):
            skipped.append("%s (excluded)" % name)
            continue
        if kind == "custom_metadata":
            if cfg["derive"].get("custom_metadata_types", True):
                cmdt.append(name)
            continue
        if kind == "custom_setting" and cfg["custom_settings"] != "object":
            skipped.append("%s (custom setting)" % name)
            continue
        if kind == "standard" and not matches(name, std_allow):
            continue

        create, edit, deletable = CRUD[kind]
        obj_perms.append({
            "object": name,
            "create": create,
            "edit": edit,
            "delete": deletable and not matches(name, cfg["no_delete"]),
        })

    # Standard objects listed for access that have no directory on disk still need the grant --
    # a standard object needs no local metadata to exist in the org.
    have = {p["object"] for p in obj_perms}
    for name in std_allow:
        if not any(c in name for c in "*?[") and name not in have and not matches(name, cfg["exclude_objects"]):
            obj_perms.append({"object": name, "create": True, "edit": True,
                              "delete": not matches(name, cfg["no_delete"])})

    obj_perms.sort(key=lambda p: (p["object"] not in std_allow, p["object"]))
    report["objects_skipped"] = skipped
    return obj_perms, sorted(cmdt)


def derive_fields(roots, cfg, report):
    """Field files -> FLS entries. This is where the four empirical rules live."""
    perms, md, required, unsupported, excluded = [], [], [], [], []
    kinds_with_fls = cfg["field_permissions_for"]

    for obj_path in collect(roots, "objects", "*"):
        obj = os.path.basename(obj_path.rstrip(os.sep))
        kind = object_kind(obj, object_metadata(roots, obj), cfg)
        field_files = collect(roots, "objects", obj, "fields", "*.field-meta.xml")
        if kind not in kinds_with_fls:
            unsupported.extend("%s.%s" % (obj, os.path.basename(p).replace(".field-meta.xml", ""))
                               for p in field_files)
            continue

        for path in field_files:
            txt = read(path)
            name = tag(txt, "fullName") or os.path.basename(path).replace(".field-meta.xml", "")
            api = "%s.%s" % (obj, name)
            ftype = tag(txt, "type")

            # The platform rejects FLS on master-detail fields outright.
            if ftype == "MasterDetail":
                md.append(api)
                continue
            # "You cannot deploy to a required field" -- and a required field is unconditionally
            # visible and editable to anyone with object access, so nothing is lost.
            if tag(txt, "required") == "true":
                required.append(api)
                continue
            if matches(api, cfg["exclude_fields"]):
                excluded.append(api)
                continue

            # Derived by nature: editable=true on one of these is a DEPLOY ERROR.
            derived = (tag(txt, "formula") is not None) or (tag(txt, "summaryOperation") is not None) or ftype == "AutoNumber"
            perms.append((api, not (derived or matches(api, cfg["read_only"]))))

    report.update(fields_master_detail=md, fields_required=required,
                  fields_unsupported_kind=unsupported, fields_excluded=excluded)
    return perms


def derive_flows(roots, cfg):
    """Screen and autolaunched flows only.

    OFF by default. A record-triggered flow runs in system context and needs no flowAccesses
    grant, and the shape of what the platform accepts here varies more than the object/field
    rules do -- so this is opt-in, and filtered to flows a user actually invokes. Turn it on once
    you have confirmed it deploys in your org, not before.
    """
    out = []
    for path in collect(roots, "flows", "*.flow-meta.xml"):
        txt = read(path)
        if tag(txt, "processType") not in ("Flow", "AutoLaunchedFlow"):
            continue
        if tag(txt, "triggerType") is not None:              # record-triggered: system context, no grant needed
            continue
        out.append(os.path.basename(path).replace(".flow-meta.xml", ""))
    return sorted(out)


def basenames(paths, suffix):
    return sorted(os.path.basename(p).replace(suffix, "") for p in paths)


# ---------------------------------------------------------------------------- rendering

def render(cfg, parts):
    def xml_values(value):
        if isinstance(value, str):
            return escape(value)
        if isinstance(value, dict):
            return {k: xml_values(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [xml_values(v) for v in value]
        return value
    cfg, parts = xml_values(cfg), xml_values(parts)
    L = []
    a = L.append
    a('<?xml version="1.0" encoding="UTF-8" ?>')
    a('<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">')

    for app in parts["applications"]:
        a("    <applicationVisibilities>")
        a("        <application>%s</application>" % app)
        a("        <visible>true</visible>")
        a("    </applicationVisibilities>")

    # A class missing here throws an unhelpful "insufficient access" at RUNTIME rather than at
    # deploy time, which is the worst possible place to find out.
    for cls in parts["apex_classes"]:
        a("    <classAccesses>")
        a("        <apexClass>%s</apexClass>" % cls)
        a("        <enabled>true</enabled>")
        a("    </classAccesses>")

    for mdt in parts["custom_metadata_types"]:
        a("    <customMetadataTypeAccesses>")
        a("        <enabled>true</enabled>")
        a("        <name>%s</name>" % mdt)
        a("    </customMetadataTypeAccesses>")

    for cp in parts["custom_permissions"]:
        a("    <customPermissions>")
        a("        <enabled>true</enabled>")
        a("        <name>%s</name>" % cp)
        a("    </customPermissions>")

    if cfg.get("description"):
        a("    <description>%s</description>" % cfg["description"])

    for field, editable in parts["fields"]:
        a("    <fieldPermissions>")
        a("        <editable>%s</editable>" % ("true" if editable else "false"))
        a("        <field>%s</field>" % field)
        a("        <readable>true</readable>")
        a("    </fieldPermissions>")

    for flow in parts["flows"]:
        a("    <flowAccesses>")
        a("        <enabled>true</enabled>")
        a("        <flow>%s</flow>" % flow)
        a("    </flowAccesses>")

    a("    <hasActivationRequired>false</hasActivationRequired>")
    a("    <label>%s</label>" % cfg["label"])
    if cfg.get("license"):
        a("    <license>%s</license>" % cfg["license"])

    for p in parts["objects"]:
        a("    <objectPermissions>")
        a("        <allowCreate>%s</allowCreate>" % str(p["create"]).lower())
        a("        <allowDelete>%s</allowDelete>" % str(p["delete"]).lower())
        a("        <allowEdit>%s</allowEdit>" % str(p["edit"]).lower())
        a("        <allowRead>true</allowRead>")
        a("        <modifyAllRecords>false</modifyAllRecords>")
        a("        <object>%s</object>" % p["object"])
        a("        <viewAllRecords>false</viewAllRecords>")
        a("    </objectPermissions>")

    for page in parts["apex_pages"]:
        a("    <pageAccesses>")
        a("        <apexPage>%s</apexPage>" % page)
        a("        <enabled>true</enabled>")
        a("    </pageAccesses>")

    for rt in parts["record_types"]:
        a("    <recordTypeVisibilities>")
        a("        <recordType>%s</recordType>" % rt)
        a("        <visible>true</visible>")
        a("    </recordTypeVisibilities>")

    for t in parts["tabs"]:
        a("    <tabSettings>")
        a("        <tab>%s</tab>" % t)
        a("        <visibility>Visible</visibility>")
        a("    </tabSettings>")

    for up in parts["user_permissions"]:
        a("    <userPermissions>")
        a("        <enabled>true</enabled>")
        a("        <name>%s</name>" % up)
        a("    </userPermissions>")

    a("</PermissionSet>")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------- config

def load_config(repo, argv):
    path = argv[argv.index("--config") + 1] if "--config" in argv else CONFIG_DEFAULT
    full = path if os.path.isabs(path) else os.path.join(repo, path)

    if "--init" in argv:
        if not contained(repo, full):
            refuse("--init config must be inside the selected project")
        if os.path.lexists(full):
            refuse("%s already exists -- edit it rather than re-initialising." % path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "x", encoding="utf-8") as fh:
            json.dump(EXAMPLE_CONFIG, fh, indent=2)
            fh.write("\n")
        print("wrote %s -- fill in api_name/label, then run check mode.\n" % path)
        print(CONFIG_HELP)
        sys.exit(0)

    if not os.path.exists(full):
        sys.stderr.write("No config at %s. Run with --init to create a starter.\n\n%s"
                         % (path, CONFIG_HELP))
        sys.exit(2)

    try:
        with open(full) as fh:
            cfg = json.load(fh)
    except (ValueError, OSError) as exc:
        refuse("%s is not readable JSON: %s" % (path, exc))
    if not isinstance(cfg, dict):
        refuse("config must be a JSON object")

    for key in ("api_name", "label"):
        if not isinstance(cfg.get(key), str) or not cfg[key].strip():
            refuse("%s is missing required key '%s'." % (path, key))

    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", cfg["api_name"]):
        refuse("api_name must be an API identifier, not a path")
    for key in ("description", "license", "output"):
        if key in cfg and not isinstance(cfg[key], str):
            refuse("%s must be a string" % key)
    for key in (*EXAMPLE_CONFIG.keys(), "field_permissions_for"):
        if isinstance(EXAMPLE_CONFIG.get(key), list) or key == "field_permissions_for":
            if key in cfg and (not isinstance(cfg[key], list) or
                               any(not isinstance(v, str) or not v.strip() for v in cfg[key])):
                refuse("%s must be a list of nonempty strings" % key)
    if cfg.get("custom_settings", "skip") not in ("skip", "object"):
        refuse("custom_settings must be skip or object")
    if "derive" in cfg and (not isinstance(cfg["derive"], dict) or
                            any(k not in EXAMPLE_CONFIG["derive"] or type(v) is not bool
                                for k, v in cfg["derive"].items())):
        refuse("derive requires known section names and boolean values")
    desc = cfg.get("description") or ""
    if len(desc) > 255:
        refuse("description is %d chars; the platform cap is 255." % len(desc))

    cfg.setdefault("standard_object_access", [])
    cfg.setdefault("standard_tabs", [])
    cfg.setdefault("no_delete", [])
    cfg.setdefault("read_only", [])
    for k in ("exclude_objects", "exclude_fields", "exclude_tabs", "exclude_apex_classes",
              "user_permissions", "extra_custom_permissions"):
        cfg.setdefault(k, [])
    cfg.setdefault("field_permissions_for", ["standard", "custom"])
    cfg.setdefault("custom_settings", "skip")
    derive = dict(EXAMPLE_CONFIG["derive"])
    derive.update(cfg.get("derive") or {})
    cfg["derive"] = derive
    cfg["_config_path"] = path
    return cfg


# ---------------------------------------------------------------------------- main

def main():
    argv = sys.argv[1:]
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        print(CONFIG_HELP)
        return

    parser = argparse.ArgumentParser(description="Generate permission-set XML from local metadata")
    parser.add_argument("--tree")
    parser.add_argument("--config")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--out")
    actions.add_argument("--write", action="store_true")
    actions.add_argument("--init", action="store_true")
    parser.add_argument("--fail-on-drift", action="store_true")
    parsed = parser.parse_args(argv)
    # Normalize --option=value syntax for the legacy helper signatures.
    argv = []
    for key, value in vars(parsed).items():
        if value:
            argv.append("--" + key.replace("_", "-"))
            if isinstance(value, str):
                argv.append(value)
    repo = resolve_repo(argv)
    cfg = load_config(repo, argv)
    roots = metadata_roots(repo)
    default_root = roots[0][0]
    report = {}

    out_rel = cfg.get("output") or os.path.join(
        os.path.relpath(default_root, repo), "permissionsets",
        "%s.permissionset-meta.xml" % cfg["api_name"])
    out_path = checked_path(repo, out_rel)
    if not out_path.endswith(".permissionset-meta.xml") or os.path.islink(out_path):
        refuse("output must be a permission-set metadata file, not a symlink")

    d = cfg["derive"]
    obj_perms, cmdt = derive_objects(roots, cfg, report)
    apex = basenames(collect(roots, "classes", "*.cls"), ".cls") if d["apex_classes"] else []
    tabs = basenames(collect(roots, "tabs", "*.tab-meta.xml"), ".tab-meta.xml") if d["tabs"] else []
    custom_perms = (basenames(collect(roots, "customPermissions", "*.customPermission-meta.xml"),
                              ".customPermission-meta.xml") if d["custom_permissions"] else [])

    record_types = []
    if d["record_types"]:
        for path in collect(roots, "objects", "*", "recordTypes", "*.recordType-meta.xml"):
            record_types.append("%s.%s" % (path.split(os.sep)[-3],
                                           os.path.basename(path).replace(".recordType-meta.xml", "")))
        record_types.sort()

    parts = {
        "applications": basenames(collect(roots, "applications", "*.app-meta.xml"),
                                  ".app-meta.xml") if d["applications"] else [],
        "apex_classes": [c for c in apex if not matches(c, cfg["exclude_apex_classes"])],
        "apex_pages": basenames(collect(roots, "pages", "*.page"), ".page") if d["apex_pages"] else [],
        "custom_metadata_types": cmdt,
        "custom_permissions": sorted(set(custom_perms) | set(cfg["extra_custom_permissions"])),
        "fields": derive_fields(roots, cfg, report),
        "flows": derive_flows(roots, cfg) if d["flows"] else [],
        "objects": obj_perms,
        "record_types": record_types,
        "tabs": [t for t in tabs if not matches(t, cfg["exclude_tabs"])] + cfg["standard_tabs"],
        "user_permissions": sorted(cfg["user_permissions"]),
    }

    generated = render(cfg, parts)
    xml_root(generated)

    # --out never targets the source tree, so it is safe in the main checkout. This is how you
    # inspect a proposed change without authoring one.
    if "--out" in argv:
        dest = argv[argv.index("--out") + 1]
        if contained(repo, dest) or find_tree_root(os.path.dirname(os.path.abspath(dest))):
            refuse("--out must be outside SFDX project trees; use --write for a worktree")
        if os.path.lexists(dest):
            refuse("--out requires a new file; existing output is preserved")
        with open(dest, "x", encoding="utf-8") as fh:
            fh.write(generated)
        print("wrote %s (diff target, not the repo file)" % dest)
        return

    write = "--write" in argv
    if write and in_main_checkout(repo):
        refuse(
            "--write targets the main checkout (%s).\n"
            "  The source tree is authored in a worktree only.\n"
            "  Agent tool with isolation: \"worktree\", or: git worktree add ../<repo>-N -b feat/N-desc\n"
            "  To regenerate into an existing worktree from here: --write --tree <worktree path>"
            % repo)

    if write:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as fh:
            fh.write(generated)
        print("wrote %s" % out_rel)
        drift = False
    else:
        existing = read(out_path) if os.path.exists(out_path) else ""
        drift = squash_ws(existing) != squash_ws(generated)
        print("CHECK ONLY (pass --write inside a worktree to update)")
        print("  %s: %s" % (out_rel, "OUT OF DATE -- regenerate" if drift else "up to date"))

    md, req = report["fields_master_detail"], report["fields_required"]
    unsupported, excluded = report["fields_unsupported_kind"], report["fields_excluded"]
    total_fields = len(parts["fields"]) + len(md) + len(req) + len(unsupported) + len(excluded)
    read_only_count = sum(1 for _, editable in parts["fields"] if not editable)

    print("  config:                  %s" % cfg["_config_path"])
    print("  applications:            %d" % len(parts["applications"]))
    print("  apex classes:            %d" % len(parts["apex_classes"]))
    print("  apex pages:              %d" % len(parts["apex_pages"]))
    print("  custom metadata types:   %d" % len(parts["custom_metadata_types"]))
    print("  custom permissions:      %d" % len(parts["custom_permissions"]))
    print("  objectPermissions:       %d" % len(parts["objects"]))
    if cfg["no_delete"]:
        # Only what the CONFIG withheld. Platform events and big objects have no delete to give
        # up, and reporting those as policy decisions would misread the shape as an intention.
        withheld = [p["object"] for p in parts["objects"] if matches(p["object"], cfg["no_delete"])]
        print("    delete withheld on %d:  %s" % (len(withheld), ", ".join(withheld)))
    if report["objects_skipped"]:
        print("    objects skipped:       %s" % ", ".join(report["objects_skipped"]))
    print("  field files on disk:     %d" % total_fields)
    print("    master-detail omitted: %d" % len(md))
    print("    required omitted:      %d" % len(req))
    if unsupported:
        print("    unsupported kind:      %d  (see field_permissions_for)" % len(unsupported))
    if excluded:
        print("    excluded by config:    %d" % len(excluded))
    print("  fieldPermissions:        %d" % len(parts["fields"]))
    print("    read-only:             %d" % read_only_count)
    print("  flowAccesses:            %d%s"
          % (len(parts["flows"]), "" if cfg["derive"]["flows"] else "  (derive.flows is off)"))
    print("  recordTypeVisibilities:  %d" % len(parts["record_types"]))
    print("  tabSettings:             %d  (%d derived + %d standard)"
          % (len(parts["tabs"]), len(parts["tabs"]) - len(cfg["standard_tabs"]),
             len(cfg["standard_tabs"])))
    print("  userPermissions:         %d" % len(parts["user_permissions"]))

    if drift and "--fail-on-drift" in argv:
        sys.exit(3)


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        refuse(str(exc))
