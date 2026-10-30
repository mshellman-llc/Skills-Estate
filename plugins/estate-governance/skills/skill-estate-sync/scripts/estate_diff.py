#!/usr/bin/env python3
"""estate_diff.py - classify every house skill across every surface.

Dependency-free (stdlib only). Scans the source skills directory, compares each
skill against each configured surface, and reports drift. It grows by scanning,
not by an enumerated list: drop a new skill folder into the source and it is
covered automatically.

The dangerous case this exists to catch is a surface mounting a SKILL.md-only
stub whose scripts and references exist only in source.

The second case: a skill citing a file under `_shared/` that is not in the repo.
`_shared/` holds no SKILL.md, so it is not a skill and is skipped by the mirror
scan. Shared references must be resolved against source before the estate can
report green.

The third case: an artifact-producing skill that does not load the shared build
card. Its output still reaches a client, in colours nobody chose and a voice
nobody gated. `--json` used to skip that check entirely, because the report was
serialized before the check ran, so an automated caller read a green estate that
the same command printed as red.

Usage:
    python3 estate_diff.py [--config surfaces.json] [--source DIR] [--json]

Exit codes:
    0  every configured local surface is identical to source
    1  a skill is missing, a stub, or has entrypoint/resource drift; a shared reference is missing,
       or an artifact-producing skill does not load the build card
    2  bad invocation / unreadable config

A pending cloud upload is not a failure. It is a human step this toolchain
cannot perform or verify, so it is reported and the exit code stays 0.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from pathlib import Path

IGNORE_NAMES = {".DS_Store", "__pycache__", ".git", "node_modules", "package-lock.json"}
DRAFT_DIRS = {"_drafts", "_shared"}

# A path into the shared dir, cited in any text file a skill ships. Trailing
# punctuation and the closing backtick of an inline-code span are not part of it.
SHARED_REF = re.compile(r"_shared/[A-Za-z0-9_][A-Za-z0-9_./-]*")
TEXT_SUFFIXES = {".md", ".py", ".js", ".json", ".txt", ".html", ".css", ".sh", ".yaml", ".yml"}


def skill_dirs(root: Path):
    """Every immediate subdirectory of root that holds a SKILL.md."""
    if not root.exists():
        return []
    out = []
    for d in sorted(root.iterdir()):
        if d.is_dir() and d.name not in DRAFT_DIRS and (d / "SKILL.md").exists():
            out.append(d)
    return out


def file_hashes(skill: Path) -> dict:
    """Relative-path -> sha1 for every non-ignored file under a skill dir."""
    h = {}
    for dp, dns, fns in os.walk(skill):
        dns[:] = [d for d in dns if d not in IGNORE_NAMES]
        for fn in fns:
            if fn in IGNORE_NAMES:
                continue
            p = Path(dp) / fn
            rel = str(p.relative_to(skill))
            try:
                h[rel] = hashlib.sha1(p.read_bytes()).hexdigest()
            except OSError:
                h[rel] = "UNREADABLE"
    return h


def has_machinery(skill: Path) -> bool:
    return (skill / "scripts").is_dir() or (skill / "references").is_dir()


def shared_refs(skill: Path) -> set:
    """Every `_shared/...` path this skill's text files cite."""
    refs = set()
    for dp, dns, fns in os.walk(skill):
        dns[:] = [d for d in dns if d not in IGNORE_NAMES]
        for fn in fns:
            # A selftest's paths are synthetic fixtures, not dependencies.
            if fn.endswith("_selftest.py"):
                continue
            p = Path(dp) / fn
            if p.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for m in SHARED_REF.findall(text):
                refs.add(m.rstrip("./-"))
    return refs


# Skills that produce an artifact somebody sees. Each must load the build card
# before writing, because the failure this catches is silent: a deck that looks
# roughly branded, in colours nobody chose, gated after the fact.
# Every skill that emits text a person reads must load the build card. The
# exclusions are the few whose entire output is a verdict or a package, with no
# prose of their own. The earlier, narrower "content skills" list was wrong:
# process writes an SOP, session-handoff writes a file, a deck skill emits a deck.
# They all create something eventually.
# Each entry needs a reason, because an exclusion nobody can read is how this
# set grows back into the list it replaced.
NO_PROSE_SKILLS = {
    "org-preflight":          "output is a go or no-go on which org is live",
    "skill-estate-sync":      "output is a drift table and a set of bundles",
    "scoping-agent":          "output is scope rows and quote fields in Salesforce",
    "sf-deploy-engine":       "output is pipeline state and deploy results",
    "prose-pass":             "owns the voice rules the card points at",
    "sf-enterprise-patterns": "output is Apex and LWC source plus arch-check results",
    "sf-headless-screenshot": "output is captured page evidence from a CLI",
}


def unwired_content_skills(skills) -> list:
    """Prose-producing skills whose SKILL.md no longer points at the build card."""
    out = []
    for sk in skills:
        if sk.name in NO_PROSE_SKILLS:
            continue
        head = (sk / "SKILL.md").read_text(encoding="utf-8", errors="ignore")[:3000]
        if "_shared/build-card.md" not in head:
            out.append(sk.name)
    return sorted(out)


def canon_exemptions(skills) -> dict:
    """skill name -> declared reason, for skills claiming the G4/G5 engineering-doc
    carve-out. STANDARD.md requires it be declared rather than argued, so that a
    reviewer can see whether the exemption is still two skills or has quietly
    become twelve. Counting it is the whole point of declaring it."""
    out = {}
    for sk in skills:
        head = (sk / "SKILL.md").read_text(encoding="utf-8", errors="ignore")[:4000]
        m = re.search(r"^\s*canon_exempt:\s*(\S+)", head, re.M)
        if not m:
            continue
        why = re.search(r"^\s*canon_exempt_reason:\s*(.+)$", head, re.M)
        out[sk.name] = (m.group(1), (why.group(1).strip() if why else "NO REASON GIVEN"))
    return out


def _ledger_state(skill_root: Path, cfg: dict, surface: str, source: Path | None = None) -> tuple:
    """-> (never recorded, changed since recorded, last-recorded date).

    Reads the publish ledger and the built bundles. Absent either one, the tier
    reports as never recorded, which is the honest answer rather than a pass.
    """
    ledger_file = skill_root / cfg.get("ledger", "publish-ledger.json")
    dist = (source.parent if source is not None else skill_root.parent.parent) / "dist"
    try:
        recorded = json.loads(ledger_file.read_text())["surfaces"][surface]
    except (OSError, json.JSONDecodeError, KeyError):
        recorded = {"bundles": {}, "last_recorded": "never"}
    have = recorded.get("bundles", {})
    now = {}
    if dist.exists():
        for b in sorted(dist.glob("*.skill")):
            now[b.stem] = hashlib.sha1(b.read_bytes()).hexdigest()
    never = sorted(n for n in now if n not in have)
    stale = sorted(n for n in now if n in have and have[n] != now[n])
    return never, stale, recorded.get("last_recorded", "never")


def missing_shared(source: Path, skills) -> dict:
    """skill name -> sorted `_shared/...` refs that do not resolve under source.

    A ref ending in a directory name resolves if the directory exists, so a
    citation of a schema folder is satisfied by the folder itself.
    """
    out = {}
    for sk in skills:
        gone = sorted(r for r in shared_refs(sk) if not (source / r).exists())
        if gone:
            out[sk.name] = gone
    return out


def find_on_surface(name: str, surface: Path):
    """Locate a skill dir named `name` (holding SKILL.md) anywhere under surface."""
    direct = surface / name
    if (direct / "SKILL.md").exists():
        return direct
    for dp, dns, fns in os.walk(surface):
        dns[:] = [d for d in dns if d not in IGNORE_NAMES]
        if Path(dp).name == name and "SKILL.md" in fns:
            return Path(dp)
    return None


def classify(src: Path, srf: Path | None) -> str:
    if srf is None:
        return "missing"
    src_only_skill = list(file_hashes(src)) == ["SKILL.md"] or not has_machinery(src)
    srf_files = file_hashes(srf)
    if list(srf_files) == ["SKILL.md"] and has_machinery(src):
        return "stub"          # surface has only SKILL.md; source ships machinery
    if file_hashes(src) == srf_files:
        return "identical"
    # SKILL.md same but resources differ, or SKILL.md differs
    if (src / "SKILL.md").read_bytes() == (srf / "SKILL.md").read_bytes():
        return "resource-drift"
    return "drift"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path)
    ap.add_argument("--source", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    here = Path(__file__).resolve()
    cfg_path = args.config or (here.parent.parent / "surfaces.json")
    try:
        cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: bad config {cfg_path}: {e}", file=sys.stderr)
        return 2

    # Default to this repo's own skills/ so a fresh clone works with no local config. An absolute
    # `source` in surfaces.json is machine-specific by nature: on any other checkout it resolves to
    # nothing, and a scan of nothing used to compare nothing and print "all mirrored (exit 0)".
    default_source = here.parent.parent.parent
    source = args.source or Path(os.path.expanduser(cfg.get("source") or str(default_source)))
    surfaces = cfg.get("surfaces", [])
    for s in surfaces:
        s["_path"] = Path(os.path.expanduser(s["path"]))

    skills = skill_dirs(source)
    # A source that resolves to nothing is a broken config, not a clean estate. Reporting it as a
    # pass is the worst outcome available: a gate that is bypassed while everything happens to be
    # fine looks exactly like a gate that works.
    if not skills:
        print(f"error: source {source} has no skills to compare.\n"
              f"       Fix `source` in {cfg_path}, pass --source DIR, or drop the key to use "
              f"this repo's {default_source}.", file=sys.stderr)
        return 2
    report, worst = {}, 0
    for sk in skills:
        row = {}
        for s in surfaces:
            found = find_on_surface(sk.name, s["_path"]) if s["_path"].exists() else None
            verdict = classify(sk, found)
            row[s["name"]] = verdict
            if verdict != "identical":
                worst = 1
        report[sk.name] = row

    # surface-only skills (present on a surface, absent from source) are informational
    src_names = {sk.name for sk in skills}
    surface_only = {}
    for s in surfaces:
        if not s["_path"].exists():
            continue
        found = set()
        for dp, dns, fns in os.walk(s["_path"]):
            dns[:] = [d for d in dns if d not in IGNORE_NAMES]
            if "SKILL.md" in fns:
                found.add(Path(dp).name)
        extra = sorted(found - src_names)
        if extra:
            surface_only[s["name"]] = extra

    # shared dependencies: `_shared/` holds no SKILL.md, so the mirror scan skips
    # it. Resolve every reference into it against source instead.
    broken_shared = missing_shared(source, skills)
    if broken_shared:
        worst = 1

    # Artifact-producing skills that never load the build card. This ran after
    # the JSON branch returned, so `--json` reported a clean estate over the
    # exact defect the human table printed in capitals. Both modes read it now.
    unwired = unwired_content_skills(skills)
    if unwired:
        worst = 1
    exempt = canon_exemptions(skills)

    cloud = cfg.get("cloud_surfaces", [])
    cloud_state, cloud_behind = [], 0
    for c in cloud:
        never, stale, when = _ledger_state(cfg_path.parent, cfg, c["name"], source)
        behind = len(never) + len(stale)
        cloud_behind += behind
        inventory_available = any((source.parent / "dist").glob("*.skill"))
        cloud_state.append({"surface": c["name"], "last_recorded": when,
                            "never_recorded": never, "changed_since_recorded": stale,
                            "pending": behind, "bundle_inventory_available": inventory_available,
                            "note": c.get("note", "")})

    local_drift = {name: {srf: verdict for srf, verdict in row.items()
                          if verdict != "identical"}
                   for name, row in report.items()}
    local_drift = {k: v for k, v in local_drift.items() if v}

    if args.json:
        print(json.dumps({
            "source": str(source),
            "skills": report,
            "surface_only": surface_only,
            "missing_shared": broken_shared,
            "unwired_content_skills": unwired,
            "canon_exemptions": {name: {"kind": kind, "reason": why}
                                 for name, (kind, why) in sorted(exempt.items())},
            "local_surface_drift": local_drift,
            "cloud_publications": {
                "verified": False,
                "basis": "publish ledger; a human recorded these uploads",
                "pending_total": cloud_behind,
                "surfaces": cloud_state,
            },
            "exit": worst,
        }, indent=2))
        return worst

    names = [s["name"] for s in surfaces]
    print(f"\nestate diff  source={source}  ({len(skills)} skills, {len(surfaces)} surfaces)\n")
    w = max([len(n) for n in report] + [12])
    print(f"  {'skill':{w}}  " + "  ".join(f"{n:>14}" for n in names))
    for sk, row in report.items():
        cells = "  ".join(f"{row.get(n,'-'):>14}" for n in names)
        flag = "  <-- FIX" if any(row.get(n) != "identical" for n in names) else ""
        print(f"  {sk:{w}}  {cells}{flag}")
    for sname, extra in surface_only.items():
        print(f"\n  surface-only on {sname}: {', '.join(extra)}")

    # Cloud tiers cannot be read from here, so they are reported from the publish
    # ledger rather than omitted. Omitting them was the real problem: the summary
    # said "all mirrored" while two of three surfaces went unchecked for months.
    if unwired:
        print("\n  ARTIFACT-PRODUCING SKILLS NOT READING THE BUILD CARD:")
        for name in unwired:
            print(f"    {name}")
        print("    Each must link _shared/build-card.md near the top of SKILL.md.")

    if exempt:
        print(f"\n  canon exemptions ({len(exempt)} of {len(skills)} skills):")
        for name, (kind, why) in sorted(exempt.items()):
            print(f"    {name:22} {kind:18} {why[:60]}")
            if why == "NO REASON GIVEN":
                print(f"      ^ STANDARD.md requires a canon_exempt_reason")

    if cloud_state:
        print("\n  cloud tiers (publication records from the ledger, not verified):")
        for row in cloud_state:
            state = ("bundle inventory unavailable" if not row["bundle_inventory_available"]
                     else "recorded hashes match; unverified" if row["pending"] == 0
                     else f"{row['pending']} bundle(s) pending upload")
            print(f"    {row['surface']:16} last recorded {row['last_recorded']:12} {state}")
        print("    a row records what a human said they uploaded. Nothing here")
        print("    reads the tier, so none of it is independent verification.")
        print("    record an upload with scripts/record_publish.py --surface <name>")
    if broken_shared:
        print("\n  MISSING SHARED DEPENDENCIES (not in source):")
        for name, refs in broken_shared.items():
            for r in refs:
                print(f"    {name} -> {r}")
    if worst:
        summary = "DRIFT FOUND (exit 1)"
    elif cloud_behind:
        # Local surfaces are clean, but printing "all mirrored" here would repeat
        # the omission this section exists to end. Exit stays 0: a pending upload
        # is a human step, not a broken build.
        summary = f"local surfaces mirrored; {cloud_behind} cloud upload(s) pending (exit 0)"
    else:
        summary = "configured local comparisons passed; cloud state is not independently verified (exit 0)"
    print(f"\n  {summary}")
    return worst


if __name__ == "__main__":
    sys.exit(main())
