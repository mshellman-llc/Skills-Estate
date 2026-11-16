#!/usr/bin/env python3
"""Behavior checks for the bounded work-truth receipt."""

import importlib.util
import pathlib
import subprocess
import tempfile


HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("work_truth", HERE / "work_truth.py")
WORK_TRUTH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WORK_TRUTH)


def git(path, *args):
    subprocess.run(["git", "-C", str(path), *args], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


passed = 0


def check(label, condition):
    global passed
    if not condition:
        raise AssertionError(label)
    passed += 1
    print("PASS {}".format(label))


with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    artifact = root / "result.md"
    artifact.write_text("# Result\n", encoding="utf-8")
    file_result = WORK_TRUTH.file_receipt(artifact, "opened")
    check("file receipt names saved-local state", file_result["state"] == "saved-locally")
    check("file receipt hashes exact bytes", len(file_result["sha256"]) == 64)
    check("file receipt does not infer cloud state", file_result["cloudChanged"] == "not-proven")

    repo = root / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "selftest@example.com")
    git(repo, "config", "user.name", "Self Test")
    tracked = repo / "tracked.txt"
    tracked.write_text("initial\n", encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "initial")
    private_example = "/" + "Users/example/private\n"
    tracked.write_text(private_example, encoding="utf-8")
    git(repo, "add", "tracked.txt")
    git(repo, "commit", "-m", "change")
    git_result = WORK_TRUTH.git_receipt(repo, "HEAD~1", "passed")
    check("git receipt distinguishes local commit", git_result["state"] == "committed-locally")
    check("git receipt counts the branch delta", git_result["changedFiles"] == 1)
    check("git receipt flags private path patterns", git_result["privateFindings"] == 1)
    check("rendered receipt stays bounded", len(WORK_TRUTH.render(git_result).splitlines()) <= 12)
    (repo / "untracked.txt").write_text("new\n", encoding="utf-8")
    dirty_result = WORK_TRUTH.git_receipt(repo, "HEAD~1", "not-run")
    check("git receipt counts untracked files", dirty_result["changedFiles"] == 2)
    check("dirty work stays built locally", dirty_result["state"] == "built-locally")

print("{} passed".format(passed))
