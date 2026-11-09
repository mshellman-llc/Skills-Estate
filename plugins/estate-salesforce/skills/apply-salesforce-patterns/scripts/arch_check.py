#!/usr/bin/env python3
"""
arch_check.py — Estate Salesforce house-architecture checker / orchestrator.

Checks Apex classes, triggers, and LWC JavaScript against the house architecture
(service layer / unit of work / selector / DTO / imperative LWC). Two engines:

  pmd    — runs the estate-apex.xml PMD ruleset (AST-accurate; same rules the IDE
           and CI see) and post-processes results: severity policy, legacy paths,
           suppression governance. Requires a PMD 7 binary.
  regex  — self-contained fallback with no dependencies (the original implementation).

Default is --engine auto: pmd when a PMD binary is found, else regex with a notice.
LWC checks and suppression governance always run in the wrapper (PMD covers neither).

Usage:
  python3 arch_check.py --paths force-app/                # scan a tree
  python3 arch_check.py --staged                          # scan staged content (hook mode)
  python3 arch_check.py --paths force-app/ --json         # machine-readable output
  python3 arch_check.py --paths force-app/ --engine regex # force an engine

Exit codes: 0 = clean or warnings only; 1 = blocking violations; 2 = usage/config error.

Stdlib only. PMD is discovered via config "pmdPath", $PMD_BIN, or `pmd` on PATH;
the ruleset via config "pmdRuleset" or pmd/estate-apex.xml next to this script.
"""

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# Rule registry: id -> (default severity, short description)
# ---------------------------------------------------------------------------
RULES = {
    "APX001": ("block", "SOQL/SOSL outside a *Selector class"),
    "APX002": ("block", "DML outside UnitOfWork (or configured allowlist)"),
    "APX003": ("block", "Selector query missing USER_MODE / SECURITY_ENFORCED"),
    "APX004": ("warn",  "@AuraEnabled method returns SObject type instead of a DTO"),
    "APX005": ("block", "Logic in trigger body (anything beyond handler dispatch)"),
    "APX006": ("warn",  "Public service method takes a single SObject (bulk-first smell)"),
    "APX007": ("warn",  "Generic collection nested 3+ levels — introduce a named class"),
    "LWC001": ("warn",  "@wire on an @salesforce/apex import (call imperatively instead)"),
    "META001": ("block", "ARCH-EXEMPT comment missing rule ID or reason"),
    "META002": ("block", "PMD suppression (@SuppressWarnings / NOPMD) without a reason"),
}

# PMD rule name -> arch_check rule ID (rules in assets/pmd/estate-apex.xml)
PMD_RULE_MAP = {
    "SoqlOutsideSelector": "APX001",
    "DmlOutsideUnitOfWork": "APX002",
    "QueryWithoutUserMode": "APX003",
    "AuraEnabledReturnsSObject": "APX004",
    "AvoidLogicInTrigger": "APX005",
    "NonBulkServiceMethod": "APX006",
    "DeeplyNestedGenerics": "APX007",
}

DEFAULT_CONFIG = {
    "mode": "block",              # "block" | "warn"  (repo-wide cap)
    "legacyPaths": [],            # globs; findings in matching files are capped at warn
    "excludePaths": [],           # globs; matching files are skipped entirely
                                  # (vendored frameworks, e.g. trigger-actions-framework)
    "rules": {},                  # per-rule override: "off" | "warn" | "block"
    "dmlAllowlist": ["UnitOfWork"],
    "soqlAllowlist": [],          # extra classes allowed to hold SOQL besides *Selector
    "exemptTestClasses": True,    # regex engine only; PMD rules always exempt test classes
    "engine": "auto",             # "auto" | "pmd" | "regex"
    "pmdPath": None,              # path to pmd binary (else $PMD_BIN, else PATH)
    "pmdRuleset": None,           # path to estate-apex.xml (else pmd/ next to this script)
}

STANDARD_SOBJECTS = {
    "account", "contact", "lead", "opportunity", "case", "user", "task", "event",
    "campaign", "campaignmember", "product2", "pricebook2", "pricebookentry",
    "order", "orderitem", "contract", "asset", "quote", "quotelineitem",
    "opportunitylineitem", "recordtype", "group", "groupmember", "contentversion",
    "contentdocument", "contentdocumentlink", "emailmessage", "attachment", "note",
    "sobject", "opportunitycontactrole", "accountcontactrelation", "individual",
}

EXEMPT_RE = re.compile(r"ARCH-EXEMPT\s*:?\s*([A-Z]{3,4}\d{3})?\s*(.*)", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Source sanitizing: blank out comments and string literals, preserving
# line structure, so keyword matching doesn't fire inside strings/comments.
# ---------------------------------------------------------------------------
def sanitize(src):
    out = []
    i, n = 0, len(src)
    mode = None  # None | 'line' | 'block' | 'sq' | 'dq' | 'tick'
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if mode is None:
            if c == "/" and nxt == "/":
                mode = "line"; out.append("  "); i += 2; continue
            if c == "/" and nxt == "*":
                mode = "block"; out.append("  "); i += 2; continue
            if c == "'":
                mode = "sq"; out.append("'"); i += 1; continue
            if c == '"':
                mode = "dq"; out.append('"'); i += 1; continue
            if c == "`":
                mode = "tick"; out.append("`"); i += 1; continue
            out.append(c); i += 1; continue
        if mode == "line":
            if c == "\n":
                mode = None; out.append("\n")
            else:
                out.append(" ")
            i += 1; continue
        if mode == "block":
            if c == "*" and nxt == "/":
                mode = None; out.append("  "); i += 2; continue
            out.append("\n" if c == "\n" else " "); i += 1; continue
        # string modes
        if c == "\\":
            out.append("  "); i += 2; continue
        if (mode == "sq" and c == "'") or (mode == "dq" and c == '"') or (mode == "tick" and c == "`"):
            out.append(c); mode = None; i += 1; continue
        out.append("\n" if c == "\n" else " "); i += 1
    return "".join(out)


def line_of(text, index):
    return text.count("\n", 0, index) + 1


# ---------------------------------------------------------------------------
# Exemption handling
# ---------------------------------------------------------------------------
def collect_exemptions(raw_lines):
    """Return ({line_no: rule_id_or_'*'}, [meta_findings]).
    An exemption applies to its own line and the immediately following line."""
    exempt = {}
    meta = []
    for idx, line in enumerate(raw_lines, start=1):
        if "ARCH-EXEMPT" not in line.upper():
            continue
        m = EXEMPT_RE.search(line)
        rule_id = (m.group(1) or "").upper() if m else ""
        reason = (m.group(2) or "").strip() if m else ""
        if not rule_id or not reason or rule_id not in RULES:
            meta.append((idx, "META001",
                         "ARCH-EXEMPT must name a valid rule ID and give a reason, "
                         "e.g. // ARCH-EXEMPT: APX003 nightly batch runs as system by design"))
            continue
        for ln in (idx, idx + 1):
            exempt.setdefault(ln, set()).add(rule_id)
    return exempt, meta


def is_exempt(exemptions, line_no, rule_id):
    return rule_id in exemptions.get(line_no, set())


# ---------------------------------------------------------------------------
# Apex checks
# ---------------------------------------------------------------------------
SOQL_OPEN_RE = re.compile(r"\[\s*(select|find)\b", re.IGNORECASE)
DB_QUERY_RE = re.compile(r"\bDatabase\s*\.\s*(query|queryWithBinds|getQueryLocator|getQueryLocatorWithBinds|countQuery|countQueryWithBinds)\s*\(", re.IGNORECASE)
SEARCH_QUERY_RE = re.compile(r"\bSearch\s*\.\s*(query|find)\s*\(", re.IGNORECASE)
DML_STMT_RE = re.compile(r"(?m)(?:^|[;{}])\s*(insert|update|upsert|delete|undelete|merge)\s+(?!\()", re.IGNORECASE)
DB_DML_RE = re.compile(r"\bDatabase\s*\.\s*(insert|update|upsert|delete|undelete|merge)\s*\(", re.IGNORECASE)
AURA_RE = re.compile(r"@AuraEnabled\b[^\n]*", re.IGNORECASE)
METHOD_SIG_RE = re.compile(
    r"(?:global|public|protected|private)\s+(?:static\s+)?([\w.<>,\s\[\]]+?)\s+(\w+)\s*\(",
)
IS_TEST_RE = re.compile(r"@IsTest\b", re.IGNORECASE)
# Three collection generics opened without a closing '>' between them = nesting depth >= 3.
# Comparison operators can't false-positive: each '<' must directly follow List/Set/Map/Iterable.
NESTED_GENERIC_RE = re.compile(
    r"\b(?:List|Set|Map|Iterable)\s*<[^<>;{}]*\b(?:List|Set|Map|Iterable)\s*<[^<>;{}]*"
    r"\b(?:List|Set|Map|Iterable)\s*<",
    re.IGNORECASE,
)
SERVICE_SINGLE_SOBJ_RE = re.compile(
    r"(?m)^\s*(?:global|public)\s+(?:static\s+)?[\w.<>,\s]+?\s+\w+\s*\(\s*([A-Za-z_]\w*(?:__c|__mdt|__e|__b)?)\s+\w+\s*\)"
)


def find_matching_bracket(text, open_idx):
    """open_idx points at '['. Return index of matching ']' or -1."""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                return i
    return -1


def sobjecty(type_str):
    """Heuristic: does an Apex type string reference an SObject type?"""
    t = type_str.strip()
    # unwrap collections recursively
    inner = re.findall(r"[\w]+(?:__c|__mdt|__e|__b)?", t)
    for token in inner:
        tl = token.lower()
        if tl in ("list", "set", "map", "id", "string", "integer", "decimal", "boolean",
                  "double", "long", "date", "datetime", "time", "object", "void", "blob"):
            continue
        if tl.endswith(("__c", "__mdt", "__e", "__b")) or tl in STANDARD_SOBJECTS:
            return token
    return None


def check_apex(path, raw, cfg):
    findings = []
    lines = raw.splitlines()
    exemptions, meta = collect_exemptions(lines)
    for ln, rid, msg in meta:
        findings.append((rid, ln, msg))

    clean = sanitize(raw)
    cls_name = os.path.splitext(os.path.basename(path))[0]
    is_test = bool(IS_TEST_RE.search(clean))
    if is_test and cfg.get("exemptTestClasses", True):
        return findings  # META001 still applies to tests; placement rules don't

    is_selector = cls_name.endswith("Selector") or cls_name in cfg.get("soqlAllowlist", [])
    dml_ok = cls_name in cfg.get("dmlAllowlist", ["UnitOfWork"])
    is_trigger = path.endswith(".trigger")

    # --- SOQL / SOSL placement + USER_MODE ---
    for m in SOQL_OPEN_RE.finditer(clean):
        ln = line_of(clean, m.start())
        end = find_matching_bracket(clean, m.start())
        body = clean[m.start(): end + 1] if end != -1 else clean[m.start(): m.start() + 400]
        if not is_selector:
            if not is_exempt(exemptions, ln, "APX001"):
                findings.append(("APX001", ln,
                                 f"Inline {'SOSL' if m.group(1).lower()=='find' else 'SOQL'} in "
                                 f"{cls_name} — move it into a *Selector class"))
        else:
            if not re.search(r"\bWITH\s+(USER_MODE|SECURITY_ENFORCED)\b", body, re.IGNORECASE):
                if not is_exempt(exemptions, ln, "APX003"):
                    findings.append(("APX003", ln,
                                     "Selector query missing WITH USER_MODE (or SECURITY_ENFORCED)"))
    for m in list(DB_QUERY_RE.finditer(clean)) + list(SEARCH_QUERY_RE.finditer(clean)):
        ln = line_of(clean, m.start())
        if not is_selector:
            if not is_exempt(exemptions, ln, "APX001"):
                findings.append(("APX001", ln,
                                 f"Dynamic query in {cls_name} — move it into a *Selector class"))
        else:
            stmt_end = clean.find(";", m.start())
            stmt = clean[m.start(): stmt_end if stmt_end != -1 else m.start() + 400]
            if "USER_MODE" not in stmt.upper():
                if not is_exempt(exemptions, ln, "APX003"):
                    findings.append(("APX003", ln,
                                     "Dynamic query missing AccessLevel.USER_MODE"))

    # --- DML placement ---
    if not dml_ok:
        for m in DML_STMT_RE.finditer(clean):
            ln = line_of(clean, m.start(1))
            if not is_exempt(exemptions, ln, "APX002"):
                findings.append(("APX002", ln,
                                 f"Raw '{m.group(1).lower()}' DML in {cls_name} — register with "
                                 f"UnitOfWork instead"))
        for m in DB_DML_RE.finditer(clean):
            ln = line_of(clean, m.start())
            if not is_exempt(exemptions, ln, "APX002"):
                findings.append(("APX002", ln,
                                 f"Database.{m.group(1)}() in {cls_name} — register with "
                                 f"UnitOfWork instead"))

    # --- Trigger bodies: dispatch only ---
    if is_trigger:
        brace = clean.find("{")
        body = clean[brace + 1: clean.rfind("}")] if brace != -1 else clean
        statements = [s.strip() for s in body.split(";") if s.strip()]
        control = re.search(r"\b(if|for|while|switch)\s*[\(o]", body)
        if len(statements) > 1 or control:
            ln = line_of(clean, brace + 1 if brace != -1 else 0)
            if not is_exempt(exemptions, ln, "APX005"):
                findings.append(("APX005", ln,
                                 "Trigger contains logic — reduce to a single handler dispatch, "
                                 "e.g. new AccountTriggerHandler().run();"))

    # --- @AuraEnabled returning SObjects ---
    for m in AURA_RE.finditer(clean):
        sig = METHOD_SIG_RE.search(clean, m.end(), m.end() + 500)
        if not sig:
            continue
        offender = sobjecty(sig.group(1))
        if offender:
            ln = line_of(clean, sig.start())
            if not is_exempt(exemptions, ln, "APX004"):
                findings.append(("APX004", ln,
                                 f"@AuraEnabled method '{sig.group(2)}' returns SObject type "
                                 f"'{offender}' — return a DTO so the UI is decoupled from the "
                                 f"data model"))

    # --- Deeply nested generics ---
    seen_nest_lines = set()
    for m in NESTED_GENERIC_RE.finditer(clean):
        ln = line_of(clean, m.start())
        if ln in seen_nest_lines:
            continue
        seen_nest_lines.add(ln)
        if not is_exempt(exemptions, ln, "APX007"):
            findings.append(("APX007", ln,
                             "Generic collection nested 3+ levels deep — extract a named "
                             "class so the shape documents itself (see architecture.md, "
                             "'Flatten deep nesting')"))

    # --- Bulk-first services ---
    if cls_name.endswith("Service"):
        for m in SERVICE_SINGLE_SOBJ_RE.finditer(clean):
            if sobjecty(m.group(1)):
                ln = line_of(clean, m.start())
                if not is_exempt(exemptions, ln, "APX006"):
                    findings.append(("APX006", ln,
                                     f"Service method takes a single {m.group(1)} — take a "
                                     f"collection so trigger and UI paths share one code path"))
    return findings


# ---------------------------------------------------------------------------
# LWC checks
# ---------------------------------------------------------------------------
APEX_IMPORT_RE = re.compile(r"import\s+(\w+)\s+from\s+['\"]@salesforce/apex/[^'\"]+['\"]")
WIRE_RE = re.compile(r"@wire\s*\(\s*(\w+)")


def check_lwc(path, raw, cfg):
    findings = []
    lines = raw.splitlines()
    exemptions, meta = collect_exemptions(lines)
    for ln, rid, msg in meta:
        findings.append((rid, ln, msg))
    clean = sanitize(raw)
    # Imports are matched against raw source: the sanitizer blanks string literals,
    # which would erase the '@salesforce/apex/...' module path.
    apex_imports = set(m.group(1) for m in APEX_IMPORT_RE.finditer(raw))
    if not apex_imports:
        return findings
    for m in WIRE_RE.finditer(clean):
        if m.group(1) in apex_imports:
            ln = line_of(clean, m.start())
            if not is_exempt(exemptions, ln, "LWC001"):
                findings.append(("LWC001", ln,
                                 f"@wire({m.group(1)}) wires an Apex method — call it "
                                 f"imperatively (await {m.group(1)}(...)) per house pattern; "
                                 f"LDS wires (lightning/ui*Api) are fine"))
    return findings


# ---------------------------------------------------------------------------
# PMD engine
# ---------------------------------------------------------------------------
def find_pmd(cfg):
    for cand in (cfg.get("pmdPath"), os.environ.get("PMD_BIN"), "pmd"):
        if not cand:
            continue
        if os.path.sep in cand and os.path.isfile(cand):
            return cand
        resolved = shutil.which(cand)
        if resolved:
            return resolved
    return None


def find_ruleset(cfg):
    explicit = cfg.get("pmdRuleset")
    if explicit:
        if os.path.isfile(explicit):
            return os.path.abspath(explicit)
        print(f"arch_check: pmdRuleset not found: {explicit}", file=sys.stderr)
        sys.exit(2)
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, "pmd", "estate-apex.xml"),
              os.path.join(here, "..", "assets", "pmd", "estate-apex.xml")):
        if os.path.isfile(p):
            return os.path.abspath(p)
    return None


def build_effective_ruleset(cfg, base, tmpdir):
    """Inject .arch-check.json allowlists into the ruleset as property overrides.
    When the allowlists match the defaults the base ruleset is used untouched."""
    dml = cfg.get("dmlAllowlist", ["UnitOfWork"])
    soql = cfg.get("soqlAllowlist", [])
    if dml == ["UnitOfWork"] and not soql:
        return base

    def alt(names):
        return "^(" + "|".join(re.escape(n) for n in names) + ")$" if names else "^$"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ruleset name="estate-effective"
         xmlns="http://pmd.sourceforge.net/ruleset/2.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://pmd.sourceforge.net/ruleset/2.0.0 https://pmd.sourceforge.io/ruleset_2_0_0.xsd">
  <description>Generated by arch_check from .arch-check.json — do not edit.</description>
  <rule ref="{base}/SoqlOutsideSelector">
    <properties><property name="allowedClassPattern" value="{alt(soql)}"/></properties>
  </rule>
  <rule ref="{base}/DmlOutsideUnitOfWork">
    <properties><property name="dmlAllowlistPattern" value="{alt(dml)}"/></properties>
  </rule>
  <rule ref="{base}/QueryWithoutUserMode"/>
  <rule ref="{base}/AuraEnabledReturnsSObject"/>
  <rule ref="{base}/NonBulkServiceMethod"/>
  <rule ref="{base}/DeeplyNestedGenerics"/>
  <rule ref="category/apex/bestpractices.xml/AvoidLogicInTrigger"/>
</ruleset>
"""
    path = os.path.join(tmpdir, "effective-ruleset.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    return path


def run_pmd_engine(apex_files, cfg, pmd_bin, tmpdir):
    """apex_files: list of (display_path, content). Content is materialized into a temp
    tree so staged content (not the working tree) is what PMD checks. Returns
    [(display_path, rule_id, line, message)] with ARCH-EXEMPT honored and META001
    hygiene findings included."""
    src_root = os.path.join(tmpdir, "src")
    display_by_rel = {}
    for path, content in apex_files:
        rel = path.replace("\\", "/").lstrip("./")
        display_by_rel[rel] = path
        dest = os.path.join(src_root, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

    ruleset = build_effective_ruleset(cfg, find_ruleset(cfg), tmpdir)
    cmd = [pmd_bin, "check", "-R", ruleset, "-d", src_root,
           "--format", "json", "--no-cache", "--no-progress"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0, 4):  # 4 = violations found
        print(f"arch_check: PMD failed (exit {proc.returncode}):\n{proc.stderr[-2000:]}",
              file=sys.stderr)
        sys.exit(2)
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("arch_check: could not parse PMD JSON output", file=sys.stderr)
        sys.exit(2)

    content_by_display = dict(apex_files)
    exempt_by_path, findings = {}, []
    for rel, display in display_by_rel.items():
        content = content_by_display[display]
        exemptions, meta = collect_exemptions(content.splitlines())
        exempt_by_path[rel] = exemptions
        for ln, rid, msg in meta:
            findings.append((display, rid, ln, msg))

    for entry in report.get("files", []):
        rel = os.path.relpath(entry.get("filename", ""), src_root).replace("\\", "/")
        display = display_by_rel.get(rel, rel)
        for v in entry.get("violations", []):
            rule = v.get("rule", "")
            rule_id = PMD_RULE_MAP.get(rule, rule)
            line = v.get("beginline", 1)
            if rule_id in RULES and is_exempt(exempt_by_path.get(rel, {}), line, rule_id):
                continue  # ARCH-EXEMPT honored in PMD mode too
            findings.append((display, rule_id, line, v.get("description", rule)))
    return findings


# ---------------------------------------------------------------------------
# Suppression governance (META002) — runs under every engine
# ---------------------------------------------------------------------------
NOPMD_RE = re.compile(r"//\s*NOPMD\b[\s:–—-]*(.*)", re.IGNORECASE)
SUPPRESS_RE = re.compile(r"@SuppressWarnings\s*\(", re.IGNORECASE)
SUPPRESS_NAMES_RE = re.compile(r"@SuppressWarnings\s*\(\s*'([^']*)'", re.IGNORECASE)


def pmd_suppressions(raw):
    """PMD-native suppressions, honored by the regex engine so both engines agree.
    Returns (rule_ids_suppressed_for_whole_file, line_numbers_suppressed_for_all_rules).
    File-level scope for @SuppressWarnings is deliberately conservative — the PMD engine
    applies the exact class/method scope; this fallback only needs to not contradict it."""
    file_rules, lines = set(), set()
    for m in SUPPRESS_NAMES_RE.finditer(raw):
        for token in m.group(1).split(","):
            token = token.strip()
            if token.upper() == "PMD":
                file_rules.update(PMD_RULE_MAP.values())
            elif token.upper().startswith("PMD."):
                mapped = PMD_RULE_MAP.get(token[4:])
                if mapped:
                    file_rules.add(mapped)
    for idx, line in enumerate(raw.splitlines(), start=1):
        if NOPMD_RE.search(line):
            lines.add(idx)
    return file_rules, lines


def check_suppression_reasons(path, raw):
    """A PMD suppression without a reason is a mute button, not an audit trail.
    NOPMD needs trailing text; @SuppressWarnings needs a trailing // comment."""
    findings = []
    for idx, line in enumerate(raw.splitlines(), start=1):
        m = NOPMD_RE.search(line)
        if m and not re.search(r"\w", m.group(1)):
            findings.append((path, "META002", idx,
                             "NOPMD without a reason — write '// NOPMD - <why this is exempt>'"))
        if SUPPRESS_RE.search(line) and "PMD" in line.upper():
            comment = line.split("//", 1)
            if len(comment) < 2 or not re.search(r"\w", comment[1]):
                findings.append((path, "META002", idx,
                                 "@SuppressWarnings without a reason — add a trailing "
                                 "'// <why this is exempt>' on the same line"))
    return findings


# ---------------------------------------------------------------------------
# Severity resolution
# ---------------------------------------------------------------------------
def glob_to_regex(pattern):
    pattern = pattern.replace("\\", "/")
    out, i = "", 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            if pattern[i:i + 3] == "**/":
                out += r"(?:.*/)?"; i += 3; continue
            if pattern[i:i + 2] == "**":
                out += r".*"; i += 2; continue
            out += r"[^/]*"; i += 1; continue
        if c == "?":
            out += r"[^/]"; i += 1; continue
        out += re.escape(c); i += 1
    return re.compile(r"^" + out + r"$")


def matches_any(path, patterns):
    norm = path.replace("\\", "/").lstrip("./")
    for pat in patterns:
        if glob_to_regex(pat).match(norm) or fnmatch.fnmatch(norm, pat):
            return True
    return False


def is_legacy(path, cfg):
    return matches_any(path, cfg.get("legacyPaths", []))


def is_excluded(path, cfg):
    return matches_any(path, cfg.get("excludePaths", []))


def resolve_severity(rule_id, path, cfg):
    sev = RULES[rule_id][0] if rule_id in RULES else "warn"  # unmapped custom PMD rules
    override = cfg.get("rules", {}).get(rule_id)
    if override in ("off", "warn", "block"):
        sev = override
    if sev == "off":
        return "off"
    if is_legacy(path, cfg) and sev == "block":
        sev = "warn"
    if cfg.get("mode", "block") == "warn" and sev == "block":
        sev = "warn"
    return sev


# ---------------------------------------------------------------------------
# File discovery / staged content
# ---------------------------------------------------------------------------
def is_lwc_js(path):
    p = path.replace("\\", "/")
    return ("/lwc/" in p and p.endswith(".js")
            and not p.endswith(".test.js") and "/__tests__/" not in p)


def relevant(path):
    return path.endswith((".cls", ".trigger")) or is_lwc_js(path)


def iter_tree(paths):
    for root in paths:
        if os.path.isfile(root):
            if relevant(root):
                yield root, open(root, encoding="utf-8", errors="replace").read()
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".sfdx", ".sf")]
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                if relevant(full):
                    yield full, open(full, encoding="utf-8", errors="replace").read()


def iter_staged():
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"arch_check: cannot read staged files ({e})", file=sys.stderr)
        sys.exit(2)
    for path in out.splitlines():
        if not relevant(path):
            continue
        show = subprocess.run(["git", "show", f":{path}"], capture_output=True, text=True)
        if show.returncode == 0:
            yield path, show.stdout


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def load_config(explicit_path):
    path = explicit_path or ".arch-check.json"
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                cfg.update(json.load(f))
        except (json.JSONDecodeError, OSError) as e:
            print(f"arch_check: bad config {path}: {e}", file=sys.stderr)
            sys.exit(2)
    elif explicit_path:
        print(f"arch_check: config not found: {explicit_path}", file=sys.stderr)
        sys.exit(2)
    return cfg


def main():
    ap = argparse.ArgumentParser(description="Estate Salesforce architecture checker")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--paths", nargs="+", help="files or directories to scan")
    src.add_argument("--staged", action="store_true", help="scan git staged content (hook mode)")
    ap.add_argument("--config", help="path to .arch-check.json (default: repo root)")
    ap.add_argument("--json", action="store_true", help="emit findings as JSON")
    ap.add_argument("--engine", choices=["auto", "pmd", "regex"],
                    help="override the analysis engine (default: config, then auto)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    files = [(p, c) for p, c in (iter_staged() if args.staged else iter_tree(args.paths))
             if not is_excluded(p, cfg)]
    apex_files = [(p, c) for p, c in files if p.endswith((".cls", ".trigger"))]
    lwc_files = [(p, c) for p, c in files if is_lwc_js(p)]

    engine = args.engine or cfg.get("engine", "auto")
    pmd_bin = find_pmd(cfg)
    if engine == "auto":
        engine = "pmd" if (pmd_bin and find_ruleset(cfg)) else "regex"
    if engine == "pmd":
        if not pmd_bin:
            print("arch_check: engine=pmd but no PMD binary found "
                  "(set pmdPath in .arch-check.json, $PMD_BIN, or add pmd to PATH)",
                  file=sys.stderr)
            sys.exit(2)
        if not find_ruleset(cfg):
            print("arch_check: engine=pmd but estate-apex.xml ruleset not found "
                  "(set pmdRuleset in .arch-check.json)", file=sys.stderr)
            sys.exit(2)

    # (path, rule_id, line, message)
    raw = []
    if apex_files:
        if engine == "pmd":
            with tempfile.TemporaryDirectory(prefix="arch_check_") as tmpdir:
                raw.extend(run_pmd_engine(apex_files, cfg, pmd_bin, tmpdir))
        else:
            for path, content in apex_files:
                sup_rules, sup_lines = pmd_suppressions(content)
                raw.extend((path, r, l, m) for r, l, m in check_apex(path, content, cfg)
                           if r not in sup_rules and l not in sup_lines)
    for path, content in lwc_files:
        raw.extend((path, r, l, m) for r, l, m in check_lwc(path, content, cfg))
    for path, content in apex_files:
        raw.extend(check_suppression_reasons(path, content))

    results = []
    scanned = len(apex_files) + len(lwc_files)
    for path, rule_id, line, msg in raw:
        sev = resolve_severity(rule_id, path, cfg)
        if sev == "off":
            continue
        results.append({"file": path, "line": line, "rule": rule_id,
                        "severity": sev, "message": msg,
                        "legacy": is_legacy(path, cfg)})

    results.sort(key=lambda r: (r["file"], r["line"]))
    blocks = [r for r in results if r["severity"] == "block"]
    warns = [r for r in results if r["severity"] == "warn"]

    if args.json:
        print(json.dumps({"engine": engine, "scanned": scanned, "blocks": len(blocks),
                          "warnings": len(warns), "findings": results}, indent=2))
    else:
        use_color = sys.stdout.isatty()
        RED, YEL, DIM, END = ("\033[31m", "\033[33m", "\033[2m", "\033[0m") if use_color else ("",) * 4
        cur = None
        for r in results:
            if r["file"] != cur:
                cur = r["file"]
                tag = f" {DIM}(legacy — warn only){END}" if r["legacy"] else ""
                print(f"\n{cur}{tag}")
            color = RED if r["severity"] == "block" else YEL
            print(f"  {color}{r['severity'].upper():5}{END} L{r['line']:<4} {r['rule']}  {r['message']}")
        print(f"\narch_check [{engine}]: {scanned} file(s) scanned — "
              f"{len(blocks)} blocking, {len(warns)} warning(s)")
        if engine == "regex":
            print("(regex fallback engine — install PMD 7 for AST-accurate checking; "
                  "see pmdPath in .arch-check.json)")
        if blocks:
            print("Fix the blocking findings above, add an inline "
                  "'// ARCH-EXEMPT: <RULE> <reason>', or commit with --no-verify if it's an emergency.")

    sys.exit(1 if blocks else 0)


if __name__ == "__main__":
    main()
