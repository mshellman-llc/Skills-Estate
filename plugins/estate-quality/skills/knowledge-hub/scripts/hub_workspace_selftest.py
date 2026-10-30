#!/usr/bin/env python3
"""Behavior tests for the pursuit workspace verbs, including the sync-race drill.

Runs against temporary directories only. Needs git on PATH for the repository
checks; without it those checks are skipped and reported, never faked.
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import hub_workspace as ws  # noqa: E402

passed = 0
failed = 0
skipped = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS {}".format(label))
    else:
        failed += 1
        print("  FAIL {}".format(label))


def skip(label):
    global skipped
    skipped += 1
    print("  SKIP {}".format(label))


def run(*argv):
    """Run the CLI in-process and return (exit code, report dict)."""
    import io
    import json
    import contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = ws.main(["--json"] + list(argv))
    text = out.getvalue()
    report = json.loads(text) if text.strip() else {}
    return code, report


def codes(report):
    return sorted({f["code"] for f in report.get("findings", [])})


def git(hub, *args):
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@example.invalid",
        "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@example.invalid",
    })
    return subprocess.run(["git", "-C", str(hub)] + list(args), env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


# Commits inside the selftest need an identity even on a machine without one.
for key, value in {
    "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@example.invalid",
    "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@example.invalid",
}.items():
    os.environ.setdefault(key, value)

HAVE_GIT = shutil.which("git") is not None

# ---------------------------------------------------------------------------
# init is idempotent and creates the documented skeleton
# ---------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as directory:
    hub = pathlib.Path(directory) / "AI Knowledge Hub"
    code, report = run("init", "--hub", str(hub), "--client", "Example Manufacturing (synthetic)",
                       "--opportunity", "opp-2026-example", "--opportunity-name", "Commerce replatform",
                       *([] if HAVE_GIT else ["--no-git"]))
    check("init exits 0", code == 0)
    for name in ("hub.yaml", "AGENTS.md", "CLAUDE.md", "TODO.md", "STANDARDS.md", "METHODOLOGY.md", ".gitignore"):
        check("init creates {}".format(name), (hub / name).exists())
    check("CLAUDE.md is the one-line pointer", (hub / "CLAUDE.md").read_text().strip() == "@AGENTS.md")
    check("AGENTS.md carries the client name", "Example Manufacturing (synthetic)" in (hub / "AGENTS.md").read_text())
    check("no template placeholder survives",
          "{{" not in (hub / "AGENTS.md").read_text() and "{{" not in (hub / "opportunities" / "opp-2026-example" / "00-OPPORTUNITY.md").read_text())
    manifest = ws.load_manifest(hub)
    check("manifest is JSON-readable YAML with a local primary store",
          manifest["primaryStore"] == "local" and manifest["client"]["clientId"] == "client-example-manufacturing-synthetic")
    check("manifest registers the opportunity",
          manifest["opportunities"][0]["opportunityId"] == "opp-2026-example")
    for folder in ("inputs/transcripts", "research", "synthesis", "evidence", "deliverables"):
        check("workspace has {}".format(folder), (hub / "opportunities" / "opp-2026-example" / folder).is_dir())
    check("no empty stage records are created",
          not (hub / "opportunities" / "opp-2026-example" / "qualification.md").exists())

    (hub / "AGENTS.md").write_text("# edited by a human\n")
    code, report = run("init", "--hub", str(hub), "--opportunity", "opp-2026-example",
                       *([] if HAVE_GIT else ["--no-git"]))
    check("second init exits 0 without --client", code == 0)
    check("second init keeps the human edit", (hub / "AGENTS.md").read_text() == "# edited by a human\n")
    check("second init does not duplicate the opportunity", len(ws.load_manifest(hub)["opportunities"]) == 1)

    if HAVE_GIT:
        check("init created a git repository", (hub / ".git").is_dir())
        log = git(hub, "log", "--oneline")
        check("init committed the skeleton", "init:" in log.stdout)
        code, report = run("audit", "--hub", str(hub))
        check("audit on a fresh hub is clean", code == 0 and report["blocking"] == 0)
    else:
        skip("git repository checks (git not installed)")

    code, report = run("check", "--hub", str(hub))
    check("check on an empty workspace passes", code == 0)

# ---------------------------------------------------------------------------
# audit: missing manifest and conflict copies
# ---------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as directory:
    hub = pathlib.Path(directory)
    code, report = run("audit", "--hub", str(hub))
    check("audit without a manifest is blocking", code == 1 and "MANIFEST-MISSING" in codes(report))
    run("init", "--hub", str(hub), "--client", "Acme", "--no-git")
    (hub / "notes (1).md").write_text("dup\n")
    (hub / ".~lock.deck.pptx#").write_text("")
    code, report = run("audit", "--hub", str(hub))
    check("a conflict copy outside .git is a warning, not blocking",
          code == 0 and "SYNC-CONFLICT" in codes(report) and "LOCK-FILE" in codes(report))
    (hub / "CLAUDE.md").unlink()
    code, report = run("audit", "--hub", str(hub))
    check("missing pointer file is reported", "INDEX-MISSING" in codes(report))
    code, report = run("doctor", "--hub", str(hub))
    check("doctor restores the pointer file", (hub / "CLAUDE.md").exists()
          and any(a["path"] == "CLAUDE.md" for a in report["actions"]))

# ---------------------------------------------------------------------------
# the sync-race drill: two commits from one parent, the ref reset to the loser
# ---------------------------------------------------------------------------
if HAVE_GIT:
    with tempfile.TemporaryDirectory() as directory:
        hub = pathlib.Path(directory) / "hub"
        run("init", "--hub", str(hub), "--client", "Race Co")
        base = git(hub, "rev-parse", "HEAD").stdout.strip()
        # Machine A commits.
        (hub / "a.md").write_text("machine A\n")
        git(hub, "add", "-A"); git(hub, "commit", "-q", "-m", "A: research landed")
        sha_a = git(hub, "rev-parse", "HEAD").stdout.strip()
        # Machine B, unaware, commits from the same parent, and Drive's
        # last-writer-wins on refs/heads/<branch> drops A off the branch.
        git(hub, "update-ref", "HEAD", base)
        (hub / "b.md").write_text("machine B\n")
        git(hub, "add", "-A"); git(hub, "commit", "-q", "-m", "B: synthesis pass")
        # A's commit is now unreachable from any ref.
        dangling, problems = ws.dangling_commits(hub)
        check("drill: the dropped commit is dangling", sha_a in dangling and not problems)
        code, report = run("audit", "--hub", str(hub))
        check("drill: audit reports the dropped commit as blocking",
              code == 1 and "GIT-DANGLING" in codes(report))
        code, report = run("doctor", "--hub", str(hub))
        recovered = ws.recovered_refs(hub)
        check("drill: doctor reattaches it under recovered/",
              len(recovered) == 1 and recovered[0].startswith("recovered/")
              and any("reattached" in a["message"] for a in report["actions"]))
        check("drill: the recovered branch points at the lost commit",
              git(hub, "rev-parse", recovered[0]).stdout.strip() == sha_a)
        check("drill: post-repair audit passes with a review warning",
              code == 0 and "GIT-RECOVERED" in codes(report) and "GIT-DANGLING" not in codes(report))
        check("drill: the lost file is retrievable",
              git(hub, "show", "{}:a.md".format(recovered[0])).stdout == "machine A\n")
        # A conflict copy inside .git that is byte-identical to its original is removed.
        original = hub / ".git" / "HEAD"
        copy = hub / ".git" / "HEAD (1)"
        copy.write_bytes(original.read_bytes())
        code, report = run("audit", "--hub", str(hub))
        check("drill: a conflict copy inside .git is blocking", code == 1 and "SYNC-CONFLICT-GIT" in codes(report))
        code, report = run("doctor", "--hub", str(hub))
        check("drill: doctor removes the identical copy", not copy.exists() and "SYNC-CONFLICT-GIT" not in codes(report))
else:
    skip("sync-race drill (git not installed)")

# ---------------------------------------------------------------------------
# check: frontmatter, tags, references, append-only ledger
# ---------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as directory:
    hub = pathlib.Path(directory) / "hub"
    run("init", "--hub", str(hub), "--client", "Gate Co", "--opportunity", "opp-1",
        *([] if HAVE_GIT else ["--no-git"]))
    context = hub / "opportunities" / "opp-1"
    good = (
        "---\ntitle: Current-state architecture\nstatus: draft\nowner: research agent\n"
        "updated: 2026-09-04\nsources:\n  - SRC-002\n---\n\n"
        "Dealer ordering runs through order API plus email into order console [STATED] (CLM-014, SRC-002).\n"
        "The catalog platform is unknown [ASSUMED].\n\n## Assumptions to validate\n\n- The catalog platform.\n"
    )
    (context / "research" / "current-state-architecture.md").write_text(good)
    ledger = context / "evidence" / "evidence-ledger.jsonl"
    ledger.write_text(
        '{"event":"context","clientId":"client-gate-co","clientName":"Gate Co","scopeType":"opportunity","contextId":"opp-1"}\n'
        '{"event":"source","sourceId":"SRC-002","sourceType":"meeting_transcript","title":"Discovery call","authority":70,"observedAt":"2026-09-04T00:00:00Z","locator":"inputs/transcripts/call.md"}\n'
        '{"event":"claim","claimId":"CLM-014","statement":"order API plus email","tag":"STATED","sourceIds":["SRC-002"],"asOf":"2026-09-04T00:00:00Z","loadBearing":true,"domains":["scope"]}\n'
    )
    code, report = run("check", "--hub", str(hub))
    check("check passes a compliant file with resolving references", code == 0 and report["blocking"] == 0)

    bad = context / "research" / "Bad File (1).md"
    bad.write_text("No frontmatter. Uses [CONFIRMED] and cites CLM-999. Decided recently.\n[ASSUMED] with no section.\n")
    code, report = run("check", "--hub", str(hub))
    found = codes(report)
    check("check fails a non-compliant file", code == 1)
    for expected in ("SYNC-CONFLICT", "FRONTMATTER-MISSING", "TAG-VOCABULARY", "ASSUMPTIONS-SECTION", "CLM-UNRESOLVED"):
        check("check reports {}".format(expected), expected in found)
    check("check warns on a relative date", "RELATIVE-DATE" in found)
    bad.unlink()
    code, report = run("check", "--hub", str(hub), str(context / "research"))
    check("check accepts an explicit folder inside the hub", code == 0)

    if HAVE_GIT:
        git(hub, "add", "-A"); git(hub, "commit", "-q", "-m", "gate: research landed")
        with ledger.open("a") as handle:
            handle.write('{"event":"supersede","claimId":"CLM-014","by":"CLM-015","asOf":"2026-09-05T00:00:00Z"}\n')
            handle.write('{"event":"claim","claimId":"CLM-015","statement":"order API only","tag":"STATED","sourceIds":["SRC-002"],"asOf":"2026-09-05T00:00:00Z","loadBearing":true,"domains":["scope"]}\n')
        code, report = run("check", "--hub", str(hub))
        check("appending ledger lines passes", code == 0)
        lines = ledger.read_text().splitlines()
        lines[2] = lines[2].replace("order API plus email", "order API edited in place")
        ledger.write_text("\n".join(lines) + "\n")
        code, report = run("check", "--hub", str(hub))
        check("editing a committed ledger line is blocking", code == 1 and "LEDGER-APPEND-ONLY" in codes(report))
    else:
        skip("append-only ledger check (git not installed)")

    ledger.write_text("not json\n")
    code, report = run("check", "--hub", str(hub))
    check("a malformed ledger line is blocking", code == 1 and "LEDGER-JSON" in codes(report))

# ---------------------------------------------------------------------------
# exit 2 for a tool that cannot run
# ---------------------------------------------------------------------------
code, _ = run("audit", "--hub", "/nonexistent/hub/path")
check("a missing hub root exits 2", code == 2)
with tempfile.TemporaryDirectory() as directory:
    code, _ = run("init", "--hub", directory, "--no-git")
    check("init on an empty folder without --client exits 2", code == 2)

print("{} passed, {} failed, {} skipped".format(passed, failed, skipped))
if failed:
    sys.exit(1)
