#!/usr/bin/env python3
"""Selftest for the sf-deploy-engine skill's three scripts.

What is actually worth pinning down here is the logic that reads pipeline.yml and
the logic that builds an API request body, because both are places where a wrong
answer is silent:

  * init.sh derives estate.protected from pipeline.yml. Including a
    `tier: sandbox` branch there would block the merge people are SUPPOSED to
    make every day; omitting a pipeline branch leaves an environment unguarded.
  * doctor.sh parses environments and promotion edges out of YAML with awk, from
    two different config shapes (`routes:` and the deprecated `promotions:`). A
    parser that silently returns nothing turns every downstream check into a
    confident pass.
  * engine.sh builds the /api/release body. The API requires a source per ticket
    and rejects a flat list without one, so a client that omits `--from` produces
    a 400 the user has to decode. It should refuse locally instead.

Standard library only. Builds throwaway git repos, touches nothing else.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INIT = HERE / "init.sh"
DOCTOR = HERE / "doctor.sh"
ENGINE = HERE / "engine.sh"

PASS, FAIL = 0, 0


def check(cond, label, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}")
        if detail:
            for line in str(detail).splitlines()[:6]:
                print(f"       {line}")


def run(cmd, cwd=None, env=None, stdin=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    return subprocess.run(
        cmd, cwd=cwd, env=e, input=stdin,
        capture_output=True, text=True,
    )


def git(cwd, *args):
    return run(["git", *args], cwd=cwd)


PIPELINE_ROUTES = """\
engine_url: https://engine.example.com

environments:
  sandbox-a:
    org_name: Example_Dev_A
    branch: sandbox/developer-a
    tier: sandbox
    test_level: NoTestRun
  preprod:
    org_name: Staging
    branch: preprod
    tier: pipeline
    test_level: RunLocalTests
    destructive_requires_label: false
  main:
    org_name: Prod
    branch: main
    test_level: RunLocalTests
    destructive_requires_label: true
    production: true

routes:
  standard:
    path: [preprod, main]
    back_merge: [preprod]
  hotfix:
    path: [main]
    entry_requires_label: hotfix
"""

PIPELINE_LEGACY = """\
engine_url: https://engine.example.com

environments:
  preprod:
    org_name: Staging
    branch: preprod
    test_level: RunLocalTests
    destructive_requires_label: false
  main:
    org_name: Prod
    branch: main
    test_level: RunLocalTests
    destructive_requires_label: true
    production: true

promotions:
  - from: preprod
    to: main
"""


def arm_engine_home(tmp, name):
    """Build an isolated HOME with the engine guards installed and registered.

    doctor.sh reports missing engine guards and returns immediately, because that
    is the headline problem when they are absent. The shadowing and dangling
    checks sit after that return and inside the "registered >= 2" branch, so a
    repo with no armed stack never reaches them.

    Any test asserting on those two checks has to arm the stack first, or it is
    asserting against output doctor.sh was never going to produce. Two guards are
    installed because count_registered_hooks.py counts distinct commands
    containing .estate-engine/ and doctor.sh requires at least two.
    """
    home = Path(tmp) / (name + "-home")
    hooks = home / ".estate-engine" / "hooks"
    hooks.mkdir(parents=True)
    commands = []
    for guard in ("guard-engine-deploy.sh", "guard-engine-merge.sh"):
        path = hooks / guard
        path.write_text("#!/bin/bash\nexit 0\n")
        path.chmod(0o755)
        commands.append(str(path))
    (home / ".claude").mkdir(parents=True)
    (home / ".claude" / "settings.json").write_text(json.dumps({
        "hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "command": c}]}
            for c in commands
        ]},
    }))
    return home


def make_repo(tmp, name, pipeline):
    root = Path(tmp) / name
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", "main", ".")
    git(root, "config", "user.email", "t@t.test")
    git(root, "config", "user.name", "t")
    (root / "pipeline.yml").write_text(pipeline)
    (root / "a.txt").write_text("x\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "init")
    return root


def test_init_wiring(tmp):
    """init.sh must isolate to the fake HOME.

    It installs hooks under $HOME/.estate-engine and registers them in both
    Claude and Codex settings by default. Running it against the real HOME from a test
    would edit the developer's own agent config, so every invocation below
    passes an isolated one and then asserts against that.
    """
    print("\n== init.sh: wiring a repo to a running engine ==")
    root = make_repo(tmp, "routes-repo", PIPELINE_ROUTES)
    home = Path(tmp) / "inithome"
    home.mkdir()
    env = {"HOME": str(home)}

    r = run([str(INIT), "--check"], cwd=root, env=env)
    check(r.returncode == 0, "--check exits 0", r.stderr)
    check("main preprod" in r.stdout, "--check reports the engine-managed branches", r.stdout)
    branches = r.stdout.split("engine-managed branches:")[1].split("\n")[0]
    check("sandbox/developer-a" not in branches,
          "a tier: sandbox branch is NOT engine-managed", branches)
    check(not (home / ".estate-engine").exists(), "--check installed nothing")

    r = run([str(INIT)], cwd=root, env=env)
    check(r.returncode == 0, "real run exits 0", r.stderr)

    hooks = home / ".estate-engine" / "hooks"
    check((hooks / "guard-engine-deploy.sh").is_file(), "installed the deploy guard")
    check((hooks / "guard-engine-merge.sh").is_file(), "installed the merge guard")
    check(os.access(hooks / "guard-engine-deploy.sh", os.X_OK), "guards are executable")
    check(not os.access(hooks / "_engine-lib.sh", os.X_OK),
          "the sourced lib is NOT executable (it is not a hook)")

    settings = home / ".claude" / "settings.json"
    check(settings.is_file(), "wrote ~/.claude/settings.json")
    if settings.is_file():
        data = json.loads(settings.read_text())
        cmds = [h.get("command", "")
                for e in data.get("hooks", {}).get("PreToolUse", [])
                for h in e.get("hooks", [])]
        check(sum(1 for c in cmds if ".estate-engine/" in c) == 2,
              "registered both guards on Claude PreToolUse", cmds)

    codex_settings = home / ".codex" / "hooks.json"
    check(codex_settings.is_file(), "wrote ~/.codex/hooks.json")
    if codex_settings.is_file():
        codex_data = json.loads(codex_settings.read_text())
        codex_cmds = [h.get("command", "")
                      for e in codex_data.get("hooks", {}).get("PreToolUse", [])
                      for h in e.get("hooks", [])]
        check(sum(1 for c in codex_cmds if ".estate-engine/" in c) == 2,
              "registered both guards on Codex PreToolUse", codex_cmds)

    # No sf-delivery-standards here, so there is nothing to reconcile and it must
    # not invent a key in a stack that is not installed.
    sq = run(["git", "config", "--get", "estate.squash"], cwd=root).stdout.strip()
    check(sq == "", f"sets no estate.* key when that stack is absent (got {sq!r})")

    vs = root / ".vscode" / "settings.json"
    check(vs.is_file(), "writes .vscode/settings.json")
    if vs.is_file():
        data = json.loads(vs.read_text())
        check(data.get("sfDeployEngine.engineUrl") == "https://engine.example.com",
              "engineUrl comes from pipeline.yml", data)

    # Idempotent: agents re-run init, and a second pass must not double-register.
    run([str(INIT)], cwd=root, env=env)
    data = json.loads(settings.read_text())
    cmds = [h.get("command", "")
            for e in data.get("hooks", {}).get("PreToolUse", [])
            for h in e.get("hooks", [])]
    check(sum(1 for c in cmds if ".estate-engine/" in c) == 2,
          "re-running does not duplicate the Claude registrations", cmds)
    codex_data = json.loads(codex_settings.read_text())
    codex_cmds = [h.get("command", "")
                  for e in codex_data.get("hooks", {}).get("PreToolUse", [])
                  for h in e.get("hooks", [])]
    check(sum(1 for c in codex_cmds if ".estate-engine/" in c) == 2,
          "re-running does not duplicate the Codex registrations", codex_cmds)


def test_init_reconciles_squash_only_when_armed(tmp):
    """The one point of contact with sf-delivery-standards.

    Its merge gate defaults to squash=require, which refuses the merge commits
    promotion and rollback depend on. init.sh demotes that to the skill's own
    existing `prefer` value -- and only when that stack is actually armed here,
    so it never writes config into a repo that does not use it.
    """
    print("\n== init.sh: the single standards touchpoint ==")
    root = make_repo(tmp, "armed-repo", PIPELINE_ROUTES)
    home = Path(tmp) / "armedhome"
    home.mkdir()
    env = {"HOME": str(home)}

    run(["git", "config", "estate.mode", "native"], cwd=root)
    run([str(INIT)], cwd=root, env=env)
    sq = run(["git", "config", "--get", "estate.squash"], cwd=root).stdout.strip()
    check(sq == "prefer", f"require -> prefer when the stack is armed (got {sq!r})")

    # An explicit non-default answer is the user's, not ours to overwrite.
    run(["git", "config", "estate.squash", "merge"], cwd=root)
    run([str(INIT)], cwd=root, env=env)
    sq = run(["git", "config", "--get", "estate.squash"], cwd=root).stdout.strip()
    check(sq == "merge", f"an explicitly-set value is left alone (got {sq!r})")


def test_init_refuses_non_engine_repo(tmp):
    print("\n== init.sh / doctor.sh: repo with no pipeline.yml ==")
    root = Path(tmp) / "plain"
    root.mkdir()
    git(root, "init", "-q", "-b", "main", ".")

    r = run([str(INIT)], cwd=root)
    check(r.returncode != 0, "init refuses", r.stdout)
    check("sf-delivery-standards" in (r.stderr + r.stdout),
          "and points at the skill that does own that case", r.stderr)

    d = run([str(DOCTOR)], cwd=root)
    check(d.returncode == 2, f"doctor exits 2, not 0 (got {d.returncode})", d.stderr)


def test_doctor_parsing(tmp):
    print("\n== doctor.sh: pipeline.yml parsing, both config shapes ==")

    root = make_repo(tmp, "doctor-routes", PIPELINE_ROUTES)
    r = run([str(DOCTOR)], cwd=root, env={"ENGINE_URL": "http://127.0.0.1:9"})
    out = r.stdout
    check("3 environment(s)" in out, "counts every environment", out)
    check("routes: topology declared" in out, "recognises the routes shape", out)
    check("tier: sandbox" in out, "calls out sandbox rows as non-deployed", out)
    check(r.returncode == 1, "exits 1 when the engine is unreachable", out)

    legacy = make_repo(tmp, "doctor-legacy", PIPELINE_LEGACY)
    r = run([str(DOCTOR)], cwd=legacy, env={"ENGINE_URL": "http://127.0.0.1:9"})
    check("deprecated promotions" in r.stdout,
          "flags the deprecated promotions shape", r.stdout)

    # --ready must derive the promotion edge from either shape. No branches exist
    # in these throwaway repos, so the assertion is that the EDGE was resolved,
    # not that commits were found.
    r = run([str(DOCTOR), "--ready"], cwd=legacy)
    check("preprod -> main" in r.stdout,
          "derives the promotion edge from promotions:", r.stdout)
    r = run([str(DOCTOR), "--ready"], cwd=root)
    check("preprod -> main" in r.stdout,
          "derives the promotion edge from routes:", r.stdout)


def test_doctor_sees_a_competing_stack(tmp):
    """The fail-open this check exists to close.

    doctor.sh once reported "clean" over a repo where a repo-level .claude/hooks
    stack sat in front of the engine guards and refused first, so the engine
    guard's reasoning was never shown -- and the repo-level deploy guard does not
    resolve the target org, which is precisely the case the engine guard adds.
    An auditor that calls that clean is worse than no auditor.
    """
    print("\n== doctor.sh: a second hook stack is not 'clean' ==")
    root = make_repo(tmp, "two-stacks", PIPELINE_ROUTES)
    hooks = root / ".claude" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "guard-deploy-tests.sh").write_text("#!/bin/bash\nexit 0\n")
    home = arm_engine_home(tmp, "two-stacks")

    r = run([str(DOCTOR)], cwd=root,
            env={"ENGINE_URL": "http://127.0.0.1:9", "HOME": str(home)})
    check("engine guards not installed" not in r.stdout,
          "the engine stack is armed, so the shadowing check is reachable",
          r.stdout[-600:])
    check("second, repo-level hook stack" in r.stdout,
          "names the competing stack", r.stdout[-600:])
    check("guard-deploy-tests.sh" in r.stdout,
          "names the specific file found", r.stdout[-600:])
    check(r.returncode != 0,
          f"and does NOT exit clean (got {r.returncode})")


def test_doctor_sees_dangling_registrations(tmp):
    """A hook entry pointing at a deleted script is not 'clean'.

    This is the bug that motivated the check, and it shipped: `git rm` staged the
    hook deletions, the settings.json edit was left UNSTAGED, and `git commit -m`
    without -a took only what was staged. The scripts went away, the entries
    stayed, and Claude Code emitted a non-blocking hook error on every Bash call
    while doctor still said clean.
    """
    print("\n== doctor.sh: registrations pointing at nothing ==")
    root = make_repo(tmp, "dangling", PIPELINE_ROUTES)
    claude = root / ".claude"
    claude.mkdir()
    (claude / "settings.json").write_text(json.dumps({
        "permissions": {"deny": []},
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [
            {"type": "command", "command": ".claude/hooks/guard-deleted.sh"}]}]},
    }))

    home = arm_engine_home(tmp, "dangling")
    r = run([str(DOCTOR)], cwd=root,
            env={"ENGINE_URL": "http://127.0.0.1:9", "HOME": str(home)})
    check("engine guards not installed" not in r.stdout,
          "the engine stack is armed, so the dangling check is reachable",
          r.stdout[-500:])
    check("point at files that do not exist" in r.stdout,
          "reports the dangling registration", r.stdout[-500:])
    check("guard-deleted.sh" in r.stdout, "names the missing target", r.stdout[-500:])
    check(r.returncode != 0, f"does not exit clean (got {r.returncode})")


def test_doctor_force_fetch():
    print("\n== doctor.sh: tags must be fetched with --force ==")
    src = DOCTOR.read_text()
    # deployed/<branch> is force-moved by the engine on every deploy. A plain
    # `git fetch --tags` REFUSES to move an existing tag, prints "would clobber"
    # to stderr, and still exits 0 — so every tag comparison silently reads a
    # stale value while the fetch reports success.
    check("--force" in src and "--tags" in src,
          "fetches tags with --force")
    check("git fetch --quiet --tags --prune origin\n" not in src,
          "no un-forced tag fetch remains")
    check('"refs/remotes/origin/$n" "refs/heads/$n"' in src,
          "resolves origin before a possibly-stale local branch")


def test_engine_release_body():
    print("\n== engine.sh: /api/release body construction ==")
    env = {"ENGINE_URL": "http://127.0.0.1:9", "SFDE_TOKEN": "x"}

    # No --from: the API rejects a flat list without a source, so refuse locally
    # rather than shipping a request that comes back 400.
    r = run([str(ENGINE), "release", "--to", "main", "GH-397"], env=env)
    check(r.returncode != 0, "refuses tickets with no --from", r.stdout)
    check("--from" in (r.stderr + r.stdout),
          "and names the missing flag", r.stderr)

    r = run([str(ENGINE), "release"], env=env)
    check(r.returncode != 0, "refuses an empty selection", r.stdout)

    r = run([str(ENGINE), "rollback", "--env", "main",
             "--ticket", "GH-1", "--sha", "abc"], env=env)
    check(r.returncode != 0, "rollback refuses both --ticket and --sha", r.stdout)

    r = run([str(ENGINE), "rollback", "--env", "main"], env=env)
    check(r.returncode != 0, "rollback refuses neither", r.stdout)

    r = run([str(ENGINE), "rollback", "--env", "main",
             "--ticket", "GH-1", "--mode", "sideways"], env=env)
    check(r.returncode != 0, "rollback rejects an unknown --mode", r.stdout)


def test_engine_needs_token(tmp):
    print("\n== engine.sh: auth is not optional ==")
    home = Path(tmp) / "emptyhome"
    home.mkdir()
    r = run([str(ENGINE), "status"],
            env={"ENGINE_URL": "http://127.0.0.1:9", "HOME": str(home), "SFDE_TOKEN": ""})
    check(r.returncode != 0, "fails without a token", r.stdout)
    check("login" in (r.stderr + r.stdout),
          "and says how to mint one", r.stderr)


def main():
    for p in (INIT, DOCTOR, ENGINE):
        if not p.is_file():
            print(f"missing script: {p}")
            return 1
        if not os.access(p, os.X_OK):
            print(f"not executable: {p}")
            return 1

    if not shutil.which("git"):
        print("git required; skipping")
        return 0

    tmp = tempfile.mkdtemp(prefix="sfde-selftest.")
    try:
        test_init_wiring(tmp)
        test_init_reconciles_squash_only_when_armed(tmp)
        test_init_refuses_non_engine_repo(tmp)
        test_doctor_parsing(tmp)
        test_doctor_sees_a_competing_stack(tmp)
        test_doctor_sees_dangling_registrations(tmp)
        test_doctor_force_fetch()
        test_engine_release_body()
        test_engine_needs_token(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
