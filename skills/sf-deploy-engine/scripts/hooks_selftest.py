#!/usr/bin/env python3
"""Selftest for the engine's two Claude Code and Codex hooks.

These are walls in front of a production Salesforce org, so the cases that
matter most are the ones where a wall should NOT be there:

  * a repo with no pipeline.yml gets no opinion at all (the master gate)
  * a tier: sandbox row is not engine-managed, so deploying and merging to it
    stays free — that exclusion is what keeps this layer off the daily loop
  * --dry-run against a pipeline org is allowed, since checkOnly mutates nothing

and the ones where it must be, resolved through an alias rather than a literal
username, because that is how anyone actually types it.

Standard library only. Builds throwaway repos and a fake SF alias store; touches
nothing outside its temp dir.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOKS = HERE.parent / "references" / "hooks"
DEPLOY = HOOKS / "guard-engine-deploy.sh"
MERGE = HOOKS / "guard-engine-merge.sh"

PASS, FAIL = 0, 0


def check(cond, label, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {label}")
    else:
        FAIL += 1
        print(f"  FAIL {label}")
        for line in str(detail).splitlines()[:5]:
            print(f"       {line}")


def fire(hook, command, cwd, env=None, expect="allow"):
    """Run a hook with a Bash tool payload. Exit 2 means blocked."""
    e = dict(os.environ)
    if env:
        e.update(env)
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    r = subprocess.run(["bash", str(hook)], input=payload, cwd=cwd,
                       capture_output=True, text=True, env=e)
    got = "block" if r.returncode == 2 else "allow"
    return got, (r.stderr or "").strip()


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


PIPELINE = """\
engine_url: https://engine.example.com

environments:
  devbox:
    org_name: Acme_Dev
    branch: sandbox/dev
    tier: sandbox
    username: dev@acme.com.dev
    test_level: NoTestRun
  preprod:
    org_name: Acme_Staging
    branch: preprod
    username: dev@acme.com.staging
    test_level: RunLocalTests
    destructive_requires_label: false
  main:
    org_name: Acme_Prod
    branch: main
    username: dev@acme.com
    test_level: RunLocalTests
    destructive_requires_label: true
    production: true

routes:
  standard:
    path: [preprod, main]
"""


def make_repo(tmp, name, pipeline=None, branch="sandbox/dev"):
    """Default branch is a NON-environment branch on purpose.

    The deploy guard checks the current branch before it checks the target org,
    so a fixture sitting on `main` would trip the branch rule and mask whatever
    the org rule was supposed to prove. Real local work never happens on an
    environment branch either; the case that it does gets its own test below.
    """
    root = Path(tmp) / name
    root.mkdir(parents=True)
    git(root, "init", "-q", "-b", branch, ".")
    git(root, "config", "user.email", "t@t.test")
    git(root, "config", "user.name", "t")
    if pipeline:
        (root / "pipeline.yml").write_text(pipeline)
    (root / "a.txt").write_text("x\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "init")
    return root


def make_fake_home(tmp):
    """An SF alias store mapping the aliases a human would actually type."""
    home = Path(tmp) / "fakehome"
    (home / ".sfdx").mkdir(parents=True)
    (home / ".sfdx" / "alias.json").write_text(json.dumps({"orgs": {
        "Acme_Prod": "dev@acme.com",
        "Acme_Staging": "dev@acme.com.staging",
        "Acme_Dev": "dev@acme.com.dev",
    }}))
    return home


def test_master_gate(tmp, home):
    print("\n== master gate: no pipeline.yml, no opinion ==")
    plain = make_repo(tmp, "plain")
    env = {"HOME": str(home)}
    for cmd in ("sf project deploy start --source-dir force-app/x --target-org Acme_Prod",
                "gh pr merge 5 --squash"):
        got, _ = fire(DEPLOY if cmd.startswith("sf") else MERGE, cmd, plain, env)
        check(got == "allow", f"silent in a non-engine repo: {cmd.split()[0]}")


def test_deploy_blocks(tmp, home):
    print("\n== deploy guard: engine-managed orgs are refused ==")
    repo = make_repo(tmp, "engine-repo", PIPELINE)
    env = {"HOME": str(home)}

    got, err = fire(DEPLOY, "sf project deploy start --source-dir force-app/x --target-org Acme_Prod", repo, env)
    check(got == "block", "prod, named by alias", err)
    check("dev@acme.com" in err, "message resolves the alias so the org is unambiguous", err)

    got, _ = fire(DEPLOY, "sf project deploy start -o dev@acme.com.staging --source-dir force-app/x", repo, env)
    check(got == "block", "staging, named by username via -o")

    got, _ = fire(DEPLOY, "sfdx force:source:deploy -o Acme_Prod -p force-app/x", repo, env)
    check(got == "block", "legacy sfdx force:source:deploy")

    # The default target org, with no flag on the command at all.
    (repo / ".sf").mkdir(exist_ok=True)
    (repo / ".sf" / "config.json").write_text(json.dumps({"target-org": "Acme_Staging"}))
    got, _ = fire(DEPLOY, "sf project deploy start --source-dir force-app/x", repo, env)
    check(got == "block", "default target-org from .sf/config.json")
    (repo / ".sf" / "config.json").write_text(json.dumps({"target-org": "Acme_Dev"}))


def test_deploy_allows(tmp, home):
    print("\n== deploy guard: what must stay allowed ==")
    repo = make_repo(tmp, "engine-repo-allow", PIPELINE)
    (repo / ".sf").mkdir(exist_ok=True)
    (repo / ".sf" / "config.json").write_text(json.dumps({"target-org": "Acme_Dev"}))
    env = {"HOME": str(home)}

    got, err = fire(DEPLOY, "sf project deploy start --source-dir force-app/x --test-level RunSpecifiedTests --tests Foo", repo, env)
    check(got == "allow", "deploy to a tier: sandbox org (the daily loop)", err)

    got, err = fire(DEPLOY, "sf project deploy start --dry-run --target-org Acme_Prod --source-dir force-app/x", repo, env)
    check(got == "allow", "--dry-run against prod: checkOnly mutates nothing", err)

    got, _ = fire(DEPLOY, "sf project deploy start --check-only --target-org Acme_Prod --source-dir force-app/x", repo, env)
    check(got == "allow", "--check-only against prod")

    got, _ = fire(DEPLOY, "sf project retrieve start --metadata ApexClass", repo, env)
    check(got == "allow", "retrieve is not a deploy")

    got, _ = fire(DEPLOY, "sf project deploy report --job-id 0Af000", repo, env)
    check(got == "allow", "deploy report is not a deploy")

    # Standing on an environment branch is refused even when the org is fine.
    git(repo, "checkout", "-q", "-b", "preprod")
    got, err = fire(DEPLOY, "sf project deploy start --source-dir force-app/x", repo, env)
    check(got == "block", "real deploy from an environment branch", err)
    git(repo, "checkout", "-q", "sandbox/dev")


def test_merge_guard(tmp, home):
    print("\n== merge guard ==")
    repo = make_repo(tmp, "merge-repo", PIPELINE)
    env = {"HOME": str(home)}

    # Method rules need no host CLI: they are refused before the base is read.
    got, err = fire(MERGE, "gh pr merge 5 --squash --delete-branch", repo, env)
    check(got == "block", "--squash refused: cherry-pick -m 1 needs a merge commit", err)

    got, _ = fire(MERGE, "gh pr merge 5 --rebase", repo, env)
    check(got == "block", "--rebase refused for the same reason")

    got, _ = fire(MERGE, "git merge feature/x", repo, env)
    check(got == "allow", "a plain git merge is not a PR-merge surface")

    # Base-branch rule, with a stubbed gh.
    binp = Path(tmp) / "bin"
    binp.mkdir(exist_ok=True)
    stub = binp / "gh"
    stub.write_text(
        '#!/bin/bash\n'
        'if [ "$1" = "pr" ] && [ "$2" = "view" ]; then printf "%s\\n" "${STUB_BASE:-feature/x}"; exit 0; fi\n'
        'exit 1\n'
    )
    stub.chmod(0o755)
    penv = dict(env, PATH=f"{binp}:{os.environ['PATH']}")

    got, err = fire(MERGE, "gh pr merge 5 --merge", repo, dict(penv, STUB_BASE="main"))
    check(got == "block", "merge into an environment branch", err)
    check("release" in err, "and points at the release path instead", err)

    got, _ = fire(MERGE, "gh pr merge 5 --merge", repo, dict(penv, STUB_BASE="preprod"))
    check(got == "block", "merge into the other environment branch")

    got, err = fire(MERGE, "gh pr merge 5 --merge", repo, dict(penv, STUB_BASE="sandbox/dev"))
    check(got == "allow", "merge into a tier: sandbox branch stays free", err)

    got, err = fire(MERGE, "gh pr merge 5 --merge", repo, dict(penv, STUB_BASE="feature/x"))
    check(got == "allow", "merge into an ordinary branch", err)


def test_no_word_boundary_in_sed():
    """BSD sed has no \\b, and the failure is invisible.

    guard-engine-merge.sh extracted the PR number with
    `sed -E 's/.*\\bgh...merge...//'`. On macOS that substitution never matches,
    so PR came back empty, the base-branch lookup returned nothing, and the
    environment-branch rule fell open on EVERY merge -- while the --squash rule
    kept working, so the guard still looked alive. BSD *grep* does support \\b,
    which is why detection was fine and only extraction was dead.

    Asserted on the source rather than behaviourally: a behavioural test would
    pass on any GNU-sed machine and hide the bug exactly where it bites.
    """
    print("\n== no \\b inside sed (BSD sed does not support it) ==")
    import re
    for p in (DEPLOY, MERGE, HOOKS / "_engine-lib.sh"):
        offenders = [l.strip() for l in p.read_text().splitlines()
                     if not l.lstrip().startswith("#")
                     and re.search(r"\bsed\b[^|]*\\b", l)]
        check(not offenders, f"{p.name} uses no \\b in a sed expression",
              "\n".join(offenders))


def test_gate_contract():
    """Pin two things that were briefly wrong and would fail silently.

    The gate moved ahead of the payload parse so a non-engine repo costs two git
    calls instead of a python3 start. That introduced two hazards:

      * exiting without reading stdin leaves the CALLER's write to fail with
        EPIPE. These hooks run in front of every Bash call on the machine, so a
        guard that can upset its own harness is not worth the milliseconds.
      * `$(gate_or_exit)` runs in a subshell, so its `exit 0` would kill only
        that subshell and let the hook carry on with an empty pipeline path --
        a guard continuing past its own gate.
    """
    print("\n== the master gate's contract ==")
    lib = (HOOKS / "_engine-lib.sh").read_text()
    check("cat >/dev/null" in lib,
          "the gate drains stdin before exiting (no EPIPE for the caller)")

    for p in (DEPLOY, MERGE):
        src = p.read_text()
        check("gate_or_exit" in src, f"{p.name} uses the gate")
        check("$(gate_or_exit)" not in src and "`gate_or_exit`" not in src,
              f"{p.name} calls it BARE, never in a command substitution")


def test_no_standards_coupling():
    print("\n== the layer reads and writes nothing of sf-delivery-standards ==")
    for p in (DEPLOY, MERGE, HOOKS / "_engine-lib.sh"):
        src = p.read_text()
        code = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("#"))
        check("aleysian." not in code,
              f"{p.name} reads no aleysian.* git config")
        check(".aleysian/" not in code,
              f"{p.name} touches no ~/.aleysian path")


def main():
    for p in (DEPLOY, MERGE):
        if not p.is_file():
            print(f"missing hook: {p}")
            return 1
    if not shutil.which("git"):
        print("git required; skipping")
        return 0

    tmp = tempfile.mkdtemp(prefix="sfde-hooks.")
    try:
        home = make_fake_home(tmp)
        test_master_gate(tmp, home)
        test_deploy_blocks(tmp, home)
        test_deploy_allows(tmp, home)
        test_merge_guard(tmp, home)
        test_no_word_boundary_in_sed()
        test_gate_contract()
        test_no_standards_coupling()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{PASS} passed, {FAIL} failed")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
