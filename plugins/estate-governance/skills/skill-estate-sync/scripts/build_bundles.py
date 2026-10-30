#!/usr/bin/env python3
"""build_bundles.py - package each house skill as an uploadable .skill bundle.

Dependency-free. Gates on quality first: every skill that ships a *_selftest.py
must pass before it is bundled. A skill that fails its own test is never shipped.
Grows by scanning the source skills directory, not by a list.

Usage:
    python3 build_bundles.py [--source DIR] [--out DIR] [--skill NAME] [--no-gate]

--no-gate skips the per-skill selftest gate. It does not skip the release-class
filter: a draft is never bundled, flag or no flag.

Exit codes:
    0  all requested skills bundled (and passed their selftests)
    1  a selftest failed; that skill was not bundled
    2  bad invocation
"""
from __future__ import annotations
import argparse, subprocess, sys, zipfile, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estate_diff  # noqa: E402  (shared-reference resolution lives there)

IGNORE = {".DS_Store", "__pycache__", ".git", "node_modules"}
DRAFT_DIRS = {"_drafts", "_shared"}

# Release classes that may be bundled. The Claude.ai and Cowork upload path has
# to ship the same set as every other surface, or a skill withheld from Claude
# Code arrives through a different door.
RELEASED = ("stable", "control")

# Cloud skill mounts are isolated. A routed skill may be installed beside its
# dependency, but Claude.ai and Cowork do not guarantee a sibling-relative path
# or even the same user/org tier. These dependencies therefore travel as
# executable runtime data inside the entry point that calls them. They are not
# nested skills: top-level metadata is omitted so the loader still sees one skill.
#
# The graph is a DAG with one root. brand-renderer is the cross-surface entry
# point, so it carries the voice engine and the release validator it calls.
# quality-gate carries neither: it is called BY brand-renderer, and giving it a
# second copy of brand-renderer made the two skills package each other. Two
# renderers then shipped from one upload, and a fix to either could reach an
# artifact through the stale copy of the other.
RUNTIME_DEPS = {
    "brand-renderer": ("prose-pass", "quality-gate"),
}

RUNTIME_DIR = "_runtime"

# Metadata that would make a vendored dependency load as a second skill. Dropped
# wherever it appears under `_runtime/`, including in a copy some earlier build
# left committed in the source tree.
NESTED_METADATA = {
    "SKILL.md", "skill.yaml", "skill.json", "skill.md",
    "AGENTS.md", "agent.yaml", "agent.json", "README.md",
    "icon.png", "icon.svg", "icon.jpg",
}


def nested_metadata(rel: Path) -> bool:
    """True for a path a loader would read as another skill's identity."""
    parts = rel.parts
    if not parts or parts[0] != RUNTIME_DIR:
        return False
    # `_runtime/<dep>/<file>`: the dependency's own top-level metadata.
    if len(parts) == 3 and parts[2] in NESTED_METADATA:
        return True
    # A runtime inside a runtime is a previous build's leftover, never a
    # dependency this graph declares. Drop the whole subtree.
    return RUNTIME_DIR in parts[1:]


def released(root: Path) -> dict:
    """Parse inventory/release-classification.yaml without a YAML dependency.

    This script is deliberately dependency-free, and the file's shape is fixed:
    two-space skill keys, four-space fields. Anything richer belongs in the
    repository tooling, which does have PyYAML.
    """
    path = root.parent / "inventory" / "release-classification.yaml"
    if not path.exists():
        print(f"  NOTE no release classification at {path}; the class filter is "
              f"inert this run. Skills with status draft and the structural "
              f"directories {', '.join(sorted(DRAFT_DIRS))} are still excluded.")
        return {}
    classes, current = {}, None
    in_skills = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("skills:"):
            in_skills = True
            continue
        if not in_skills or not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  ") and not line.startswith("    ") and line.rstrip().endswith(":"):
            current = line.strip().rstrip(":")
        elif current and line.strip().startswith("release:"):
            classes[current] = line.split("release:", 1)[1].strip()
    return classes


def declared_status(skill: Path) -> str | None:
    """Read the top-level lifecycle status without adding a YAML dependency."""
    path = skill / "skill.yaml"
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def skills(root: Path, only: str | None, classes: dict):
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name in DRAFT_DIRS or not (d / "SKILL.md").exists():
            continue
        if only and d.name != only:
            continue
        # The release-classification inventory is optional during migration,
        # but a skill's own draft status is authoritative. The command promises
        # that drafts never become uploadable bundles, including targeted runs.
        if declared_status(d) == "draft":
            print(f"  SKIP {d.name}: skill status draft")
            continue
        # Unconditional. --no-gate skips the selftest gate, which is a quality
        # question. Whether a skill is cleared for release is not, so no flag
        # turns this off.
        if classes:
            cls = classes.get(d.name)
            if cls is None:
                print(f"  SKIP {d.name}: no release class recorded")
                continue
            if cls not in RELEASED:
                print(f"  SKIP {d.name}: release class {cls}")
                continue
        yield d


def run_selftests(skill: Path) -> tuple[bool, list[str]]:
    """Pass only when the skill ships at least one selftest and all of them pass.

    An empty test list used to return pass, so a skill with no test bundled clean
    and the estate reported green over untested code. STANDARD.md requires a
    selftest per skill; absence is now a gate failure, not a silent exemption.
    """
    tests = sorted(skill.glob("scripts/*_selftest.py"))
    if not tests:
        return False, ["no scripts/*_selftest.py (STANDARD.md requires one per skill)"]
    log = []
    for t in tests:
        r = subprocess.run([sys.executable, str(t)], capture_output=True, text=True,
                           cwd=str(skill.parent))
        log.append(f"{t.name}: {'PASS' if r.returncode == 0 else 'FAIL(' + str(r.returncode) + ')'}")
        if r.returncode != 0:
            return False, log
    return True, log


def _text_shared_refs(path: Path) -> set[str]:
    """Shared references in one vendored text file.

    `estate_diff.shared_refs` starts from a skill directory. Bundling also has
    to follow references found inside shared Markdown such as build-card.md.
    That card names the fonts and logos a producer needs, so stopping after the
    first edge creates a bundle with the card and CSS but no binary assets.
    """
    if path.suffix.lower() not in estate_diff.TEXT_SUFFIXES:
        return set()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    return {m.rstrip("./-") for m in estate_diff.SHARED_REF.findall(text)}


def _files_for_shared_ref(ref: str, source: Path) -> list[tuple[Path, Path]]:
    target = source / ref
    if target.is_file():
        return [(target, Path(ref))]
    # `_shared/<pkg>` is a namespace directory and does not pull its full tree.
    # A root-level shared file such as `_shared/build-card.md` is a real,
    # explicit dependency even though it also has only two path components.
    if len(Path(ref).parts) < 3:
        return []
    if not target.is_dir():
        return []
    files = []
    for dp, dns, fns in os.walk(target):
        dns[:] = [d for d in dns if d not in IGNORE]
        for fn in sorted(fns):
            if fn in IGNORE:
                continue
            p = Path(dp) / fn
            files.append((p, Path(ref) / p.relative_to(target)))
    return files


def shared_payload(skill: Path, source: Path) -> list:
    """(disk path, path relative to the skills root) for every `_shared/` file
    this skill cites.

    A .skill bundle mounts alone, so a shared file has to travel inside every
    bundle that cites it. The repo keeps one copy; the bundler vendors it in at
    build time, so the citation resolves on a surface without the copy drifting.
    """
    pending = list(estate_diff.shared_refs(skill))
    seen_refs: set[str] = set()
    out: set[tuple[Path, Path]] = set()
    while pending:
        ref = pending.pop()
        if ref in seen_refs:
            continue
        seen_refs.add(ref)
        files = _files_for_shared_ref(ref, source)
        out.update(files)
        for disk, _ in files:
            pending.extend(_text_shared_refs(disk) - seen_refs)
    # A file reached through both a direct ref and its parent dir lands once.
    return sorted(out)


def runtime_payload(skill: Path, source: Path) -> list[tuple[Path, Path]]:
    """Executable dependencies vendored below `_runtime/<skill>/`.

    The dependency's top-level metadata is intentionally omitted. Scripts,
    configs, references, and any transitive shared data remain available, while
    the cloud loader cannot mistake the runtime copy for another routed skill.
    """
    out: set[tuple[Path, Path]] = set()
    for name in RUNTIME_DEPS.get(skill.name, ()):
        dep = source / name
        if not (dep / "SKILL.md").is_file():
            raise FileNotFoundError(f"runtime dependency missing: {name}")
        for dp, dns, fns in os.walk(dep):
            # A dependency carrying its own `_runtime/` is a previous build's
            # output, not a declared edge. Following it would nest a runtime
            # inside a runtime and reintroduce the recursion by the back door.
            dns[:] = [d for d in dns if d not in IGNORE and d != RUNTIME_DIR]
            for fn in fns:
                if fn in IGNORE:
                    continue
                p = Path(dp) / fn
                rel = p.relative_to(dep)
                if len(rel.parts) == 1 and fn in NESTED_METADATA:
                    continue
                out.add((p, Path(RUNTIME_DIR) / name / rel))
        for disk, rel in shared_payload(dep, source):
            out.add((disk, Path("_runtime") / name / rel))
    return sorted(out)


def archive_map(skill: Path, source: Path) -> dict:
    """archive path -> disk file, one entry per path.

    A zip accepts the same name twice and most readers surface only the first
    entry, so a stale `_runtime/` copy committed under a skill used to shadow the
    dependency this build resolved. Later writes overwrite earlier ones here, and
    the order below is the precedence: the skill's own files, then vendored
    shared data, then the governed runtime last and winning.
    """
    files: dict = {}
    for dp, dns, fns in os.walk(skill):
        dns[:] = [d for d in dns if d not in IGNORE]
        for fn in sorted(fns):
            if fn in IGNORE:
                continue
            p = Path(dp) / fn
            rel = p.relative_to(skill)
            if nested_metadata(rel):
                continue
            files[str(rel)] = p
    for disk, rel in shared_payload(skill, source):
        files[str(rel)] = disk
    for disk, rel in runtime_payload(skill, source):
        files[str(rel)] = disk
    return files


def bundle(skill: Path, out: Path, source: Path | None = None) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    dest = out / f"{skill.name}.skill"
    if dest.exists():
        dest.unlink()
    files = archive_map(skill, source or skill.parent)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(files):
            z.write(files[rel], str(Path(skill.name) / rel))
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve()
    ap.add_argument("--source", type=Path, default=here.parent.parent.parent)
    ap.add_argument("--out", type=Path, default=here.parent.parent.parent.parent / "dist")
    ap.add_argument("--skill")
    ap.add_argument("--no-gate", action="store_true")
    args = ap.parse_args()

    if not args.source.exists():
        print(f"error: source {args.source} not found", file=sys.stderr)
        return 2

    classes = released(args.source)
    built, failed = [], []
    for sk in skills(args.source, args.skill, classes):
        if not args.no_gate:
            ok, log = run_selftests(sk)
            if not ok:
                failed.append(sk.name)
                print(f"  SKIP {sk.name}: selftest failed ({'; '.join(log)})")
                continue
        dest = bundle(sk, args.out, args.source)
        built.append(sk.name)
        kb = dest.stat().st_size // 1024
        n_shared = len(shared_payload(sk, args.source))
        n_runtime = len(runtime_payload(sk, args.source))
        vendored = f", +{n_shared} shared" if n_shared else ""
        if n_runtime:
            vendored += f", +{n_runtime} runtime"
        print(f"  OK   {sk.name} -> {dest.name} ({kb} KB{vendored})")

    print(f"\n  bundled {len(built)}; failed gate {len(failed)}: {', '.join(failed) or 'none'}")
    if classes:
        approved = sum(1 for c in classes.values() if c in RELEASED)
        print(f"  approved for release: {approved} of {len(classes)} classified")
    print(f"  out: {args.out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
