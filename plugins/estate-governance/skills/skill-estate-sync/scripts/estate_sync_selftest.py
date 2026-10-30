#!/usr/bin/env python3
"""Selftest for skill-estate-sync. No third-party deps, no network.

Builds a synthetic source with two skills and two surfaces (one clean mirror,
one with a stub and a drift), runs estate_diff.classify, and asserts the
verdicts. Also bundles a synthetic skill and confirms the .skill zip is created
and gated by a selftest. Prints observed vs expected; nonzero on mismatch.
"""
import sys, tempfile, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import estate_diff as ed          # noqa: E402
import build_bundles as bb        # noqa: E402

fail = []


def mkskill(root, name, with_scripts=True, skill_body="# s\n"):
    d = root / name
    (d / "scripts").mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(skill_body)
    (d / "skill.yaml").write_text("status: active\n")
    if with_scripts:
        (d / "scripts" / "run.py").write_text("print('x')\n")
    return d


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    src = tmp / "source"; src.mkdir()
    full = mkskill(src, "alpha", with_scripts=True, skill_body="# alpha\nbody\n")
    mkskill(src, "beta", with_scripts=True, skill_body="# beta\n")

    # surface 1: clean mirror of alpha only
    s1 = tmp / "s1"; s1.mkdir()
    mkskill(s1, "alpha", with_scripts=True, skill_body="# alpha\nbody\n")
    # surface 2: alpha as a SKILL.md-only STUB; beta present but DRIFTED
    s2 = tmp / "s2"; s2.mkdir()
    (s2 / "alpha").mkdir(); (s2 / "alpha" / "SKILL.md").write_text("# alpha\nbody\n")
    mkskill(s2, "beta", with_scripts=True, skill_body="# beta CHANGED\n")

    checks = [
        ("alpha vs s1 mirror", ed.classify(full, s1 / "alpha"), "identical"),
        ("alpha vs s2 stub", ed.classify(full, ed.find_on_surface("alpha", s2)), "stub"),
        ("beta vs s2 drift", ed.classify(src / "beta", ed.find_on_surface("beta", s2)), "drift"),
        ("alpha vs missing", ed.classify(full, None), "missing"),
    ]
    for label, got, want in checks:
        print(f"  {label:24} got={got:14} want={want}")
        if got != want:
            fail.append(f"{label}: got {got}, want {want}")

    # discovery: scanning finds both skills, ignores a _drafts dir
    (src / "_drafts").mkdir(); (src / "_drafts" / "z").mkdir(parents=True)
    (src / "_drafts" / "z" / "SKILL.md").write_text("# draft\n")
    found = {d.name for d in ed.skill_dirs(src)}
    print(f"\n  discovered={sorted(found)} (expect alpha,beta; not z)")
    if found != {"alpha", "beta"}:
        fail.append(f"discovery: {found}")

    # shared deps: a `_shared/` ref that resolves is silent; one that does not is
    # reported. This is the case the mirror scan cannot see, because `_shared`
    # carries no SKILL.md and is skipped as a skill.
    (src / "_shared" / "spec" / "schema").mkdir(parents=True)
    (src / "_shared" / "spec" / "SPEC.md").write_text("# spec\n")
    (full / "SKILL.md").write_text(
        "# alpha\nbody\nRead `_shared/spec/SPEC.md` and `_shared/spec/schema/`.\n")
    (src / "beta" / "SKILL.md").write_text("# beta\nSee `_shared/spec/GONE.md`.\n")
    broken = ed.missing_shared(src, ed.skill_dirs(src))
    print(f"\n  missing_shared={broken} (expect beta -> _shared/spec/GONE.md only)")
    if broken != {"beta": ["_shared/spec/GONE.md"]}:
        fail.append(f"shared-dep check: {broken}")

    # vendoring: a bundle mounts alone, so a cited shared file must travel in it
    vend = bb.bundle(full, tmp / "dist-shared", src)
    names = set(zipfile.ZipFile(vend).namelist())
    want = "alpha/_shared/spec/SPEC.md"
    print(f"\n  vendored {want!r} into bundle = {want in names}")
    if want not in names:
        fail.append(f"shared file not vendored; bundle holds {sorted(names)}")

    # A bare `_shared/<pkg>` mention is a namespace reference, not a dependency.
    # Without this, prose naming a shared package drags its whole tree into every
    # bundle that merely talks about it (2.6 MB of brand fonts, five times over).
    (src / "_shared" / "big").mkdir()
    for i in range(3):
        (src / "_shared" / "big" / f"f{i}.bin").write_text("x" * 1000)
    (src / "beta" / "SKILL.md").write_text("# beta\nBrand lives in `_shared/big`.\n")
    payload = bb.shared_payload(src / "beta", src)
    print(f"  bare `_shared/big` mention vendored {len(payload)} files (expect 0)")
    if payload:
        fail.append(f"namespace mention pulled in {len(payload)} files")

    # citing a path INSIDE the package still vendors it
    (src / "beta" / "SKILL.md").write_text("# beta\nReads `_shared/big/f1.bin`.\n")
    payload = bb.shared_payload(src / "beta", src)
    print(f"  explicit `_shared/big/f1.bin` vendored {len(payload)} file(s) (expect 1)")
    if len(payload) != 1:
        fail.append(f"explicit shared file not vendored: {payload}")

    # Transitive shared deps: a producer usually cites build-card.md, and the
    # card cites the actual logo and font directories. Stopping at the card was
    # the cloud packaging defect that shipped CSS without either binary asset.
    (src / "_shared" / "card.md").write_text(
        "Use `_shared/brand/logos/` and `_shared/brand/fonts/`.\n")
    (src / "_shared" / "brand" / "logos").mkdir(parents=True)
    (src / "_shared" / "brand" / "fonts").mkdir(parents=True)
    (src / "_shared" / "brand" / "logos" / "real.png").write_bytes(b"png")
    (src / "_shared" / "brand" / "fonts" / "house.ttf").write_bytes(b"ttf")
    (src / "beta" / "SKILL.md").write_text("# beta\nRead `_shared/card.md`.\n")
    payload_names = {str(rel) for _, rel in bb.shared_payload(src / "beta", src)}
    transitive_want = {
        "_shared/card.md",
        "_shared/brand/logos/real.png",
        "_shared/brand/fonts/house.ttf",
    }
    print(f"  transitive shared assets present = {transitive_want <= payload_names}")
    if not transitive_want <= payload_names:
        fail.append(f"transitive shared files not vendored: {sorted(payload_names)}")

    # Runtime deps: brand-renderer is the cross-surface entry point, so it has to
    # carry the voice engine and the release validator it calls. Cloud mounts do
    # not promise sibling skill paths. Metadata is omitted so a nested copy cannot
    # be routed as a second skill.
    prose = mkskill(src, "prose-pass", with_scripts=True)
    (prose / "house.json").write_text("{}\n")
    qgate = mkskill(src, "quality-gate", with_scripts=True)
    (qgate / "skill.yaml").write_text("name: quality-gate\n")
    renderer = mkskill(src, "brand-renderer", with_scripts=True)
    runtime = bb.runtime_payload(renderer, src)
    runtime_names = {str(rel) for _, rel in runtime}
    for want in ("_runtime/prose-pass/scripts/run.py",
                 "_runtime/quality-gate/scripts/run.py"):
        print(f"  brand-renderer carries {want} = {want in runtime_names}")
        if want not in runtime_names:
            fail.append(f"runtime not vendored: {want} in {sorted(runtime_names)}")
    exposed = sorted(n for n in runtime_names
                     if Path(n).name in bb.NESTED_METADATA)
    print(f"  nested metadata exposed = {exposed} (expect none)")
    if exposed:
        fail.append(f"runtime dependency exposed nested metadata: {exposed}")

    # The graph is a DAG. quality-gate must not carry brand-renderer back, or the
    # two skills package each other and one upload ships two renderers.
    back_edge = {str(rel) for _, rel in bb.runtime_payload(qgate, src)}
    print(f"  quality-gate carries {len(back_edge)} runtime file(s) (expect 0)")
    if back_edge:
        fail.append(f"quality-gate re-packages a dependency: {sorted(back_edge)}")

    # Archive-path collision: an older embedded runtime committed under the skill
    # targets the same path as the governed dependency. A zip takes both names and
    # most readers surface the first, so the stale copy used to shadow the fresh
    # one. One entry per path now, and the governed dependency wins.
    stale = renderer / "_runtime" / "prose-pass" / "scripts"
    stale.mkdir(parents=True)
    (stale / "run.py").write_text("print('stale 2026-01 copy')\n")
    (stale.parent / "SKILL.md").write_text("# prose-pass\n")
    (stale.parent / "icon.png").write_bytes(b"png")
    mapped = bb.archive_map(renderer, src)
    collided = "_runtime/prose-pass/scripts/run.py"
    resolved = mapped[collided].read_text()
    print(f"  colliding path resolves to the governed copy = "
          f"{'stale' not in resolved}")
    if "stale" in resolved:
        fail.append(f"stale embedded runtime won the collision: {resolved!r}")
    leaked = sorted(k for k in mapped if Path(k).name in bb.NESTED_METADATA
                    and k.startswith("_runtime/"))
    print(f"  embedded runtime metadata in archive = {leaked} (expect none)")
    if leaked:
        fail.append(f"embedded runtime metadata reached the archive: {leaked}")

    zipped = bb.bundle(renderer, tmp / "dist-runtime", src)
    entries = zipfile.ZipFile(zipped).namelist()
    dupes = sorted({n for n in entries if entries.count(n) > 1})
    print(f"  duplicate archive entries = {dupes} (expect none)")
    if dupes:
        fail.append(f"bundle wrote duplicate archive paths: {dupes}")

    # An unwired artifact-producing skill fails the audit in BOTH modes. The
    # human table printed it in capitals while `--json` returned a clean report,
    # because the check ran after the JSON branch had already returned. An
    # automated caller therefore read green over the exact defect on screen.
    import json as _json, subprocess as _sp
    unwired_src = tmp / "unwired-source"
    unwired_src.mkdir()
    mkskill(unwired_src, "wired", skill_body="# wired\nRead `_shared/build-card.md`.\n")
    mkskill(unwired_src, "loose", skill_body="# loose\nNo card here.\n")
    (unwired_src / "_shared").mkdir()
    (unwired_src / "_shared" / "build-card.md").write_text("# card\n")
    empty_cfg = tmp / "no-surfaces.json"
    empty_cfg.write_text('{"surfaces": [], "cloud_surfaces": []}')
    diff_script = HERE / "estate_diff.py"

    def run_diff(*extra):
        return _sp.run([sys.executable, str(diff_script), "--config", str(empty_cfg),
                        "--source", str(unwired_src), *extra],
                       capture_output=True, text=True)

    human, machine = run_diff(), run_diff("--json")
    print(f"\n  unwired skill fails human mode = {human.returncode == 1}")
    if human.returncode != 1:
        fail.append(f"human mode passed an unwired skill (exit {human.returncode})")
    if "loose" not in human.stdout:
        fail.append("human mode did not name the unwired skill")
    print(f"  unwired skill fails json mode  = {machine.returncode == 1}")
    if machine.returncode != 1:
        fail.append(f"json mode passed an unwired skill (exit {machine.returncode})")
    payload = _json.loads(machine.stdout)
    print(f"  json names it = {payload.get('unwired_content_skills')}")
    if payload.get("unwired_content_skills") != ["loose"]:
        fail.append(f"json omitted the unwired skill: {payload.get('unwired_content_skills')}")

    # The machine report carries every field a caller has to act on.
    required_fields = {"missing_shared", "unwired_content_skills", "canon_exemptions",
                       "local_surface_drift", "cloud_publications"}
    absent = sorted(required_fields - set(payload))
    print(f"  json report fields absent = {absent} (expect none)")
    if absent:
        fail.append(f"estate report is missing fields: {absent}")
    # A cloud row is a publication record. Nothing here reads the tier.
    if payload["cloud_publications"].get("verified") is not False:
        fail.append("cloud publications claim verification this toolchain cannot do")

    # restore alpha/beta bodies so the bundle checks below are unaffected
    (full / "SKILL.md").write_text("# alpha\nbody\n")
    (src / "beta" / "SKILL.md").write_text("# beta\n")

    # bundle gate: a passing selftest bundles; a failing one does not
    gs = mkskill(src, "gamma", with_scripts=True, skill_body="# gamma\n")
    (gs / "scripts" / "ok_selftest.py").write_text("import sys; sys.exit(0)\n")
    out = tmp / "dist"
    dest = bb.bundle(gs, out)
    ok, _ = bb.run_selftests(gs)
    print(f"\n  gamma selftest pass={ok}, bundle exists={dest.exists()}, is_zip={zipfile.is_zipfile(dest)}")
    if not (ok and dest.exists() and zipfile.is_zipfile(dest)):
        fail.append("bundle/gate")
    gs2 = mkskill(src, "delta", with_scripts=True)
    (gs2 / "scripts" / "bad_selftest.py").write_text("import sys; sys.exit(1)\n")
    ok2, _ = bb.run_selftests(gs2)
    print(f"  delta selftest pass={ok2} (expect False)")
    if ok2:
        fail.append("gate did not catch failing selftest")

    # A skill with NO selftest must fail the gate too. An empty test list used to
    # return pass, which let untested skills bundle clean and report green.
    gs3 = mkskill(src, "epsilon", with_scripts=True)
    ok3, log3 = bb.run_selftests(gs3)
    print(f"  epsilon (no selftest at all) pass={ok3} (expect False)")
    if ok3:
        fail.append("gate passed a skill shipping no selftest")
    if not any("no scripts" in line for line in log3):
        fail.append(f"missing-selftest failure is not explained: {log3}")

    # Draft status is authoritative even when the optional release inventory is
    # absent. Targeting a draft by name must not turn it into an upload bundle.
    draft = mkskill(src, "zeta", with_scripts=True)
    (draft / "skill.yaml").write_text("status: draft\n")
    selected = [d.name for d in bb.skills(src, "zeta", {})]
    print(f"  zeta draft selected for bundling={selected} (expect none)")
    if selected:
        fail.append("draft skill selected when release classification is absent")

    # A source checkout can also validate its shared-card runtime. An isolated
    # maintainer package does not contain the entire estate; its unit tests must
    # not mistake the package's parent for a source tree.
    import subprocess as _sp
    real = HERE.parent.parent.parent
    card_sync = real / "skill-estate-sync" / "scripts" / "sync_build_card.py"
    if card_sync.exists() and (real / "_shared/build-card.md").is_file():
        r = _sp.run([sys.executable, str(card_sync), "--skills-root", str(real), "--check"],
                    capture_output=True, text=True)
        print(f"\n  build card in sync = {r.returncode == 0}: {r.stdout.strip()[:60]}")
        if r.returncode != 0:
            fail.append("build-card.md is stale; run sync_build_card.py")
    else:
        print("\n  Canonical shared-runtime integration not checked: isolated package. "
              "Run sync_build_card.py --skills-root CHECKOUT/skills --check against the estate.")

if fail:
    print("\nSELFTEST FAILED")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nSELFTEST PASSED")
