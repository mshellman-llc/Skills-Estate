#!/usr/bin/env python3
"""
install_hooks.py — install the arch_check pre-commit hook into a repo.

Copies arch_check.py into <repo>/scripts/ (so the hook is portable for the whole
team once committed) and writes .git/hooks/pre-commit to run it against staged
content. Existing pre-commit hooks are preserved by chaining.

Usage:
  python3 install_hooks.py                 # install into the current repo
  python3 install_hooks.py --repo ../org   # install into another repo
  python3 install_hooks.py --print         # print hook body only (for husky users)
  python3 install_hooks.py --no-copy       # don't copy arch_check.py into the repo
"""

import argparse
import os
import shutil
import stat
import subprocess
import sys

HOOK_BODY = """#!/bin/sh
# arch_check pre-commit hook (installed by sf-enterprise-patterns skill)
# Checks staged Apex/LWC against the house architecture. Warn/block behavior
# is controlled by .arch-check.json in the repo root.
if [ -f scripts/arch_check.py ]; then
  python3 scripts/arch_check.py --staged || exit 1
else
  echo "arch_check: scripts/arch_check.py not found — skipping architecture check" >&2
fi
{chain}exit 0
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".", help="path to the target git repo")
    ap.add_argument("--print", dest="print_only", action="store_true")
    ap.add_argument("--no-copy", action="store_true")
    args = ap.parse_args()

    if args.print_only:
        print(HOOK_BODY.format(chain=""))
        return

    repo = os.path.abspath(args.repo)
    try:
        git_dir = subprocess.run(
            ["git", "rev-parse", "--git-dir"], cwd=repo,
            capture_output=True, text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"install_hooks: {repo} is not a git repo", file=sys.stderr)
        sys.exit(2)
    git_dir = git_dir if os.path.isabs(git_dir) else os.path.join(repo, git_dir)

    # ── Aleysian delivery-standards detection ────────────────────────────────
    # That stack arms hooks machine-wide via `git config core.hooksPath`
    # (~/.aleysian/githooks), which means a .git/hooks/pre-commit written here
    # would be silently inert. Its gate 4 already runs PMD against
    # config/pmd-ruleset.xml, so the correct integration is through that file,
    # not a second hook.
    hooks_path = subprocess.run(
        ["git", "config", "core.hooksPath"], cwd=repo,
        capture_output=True, text=True).stdout.strip()
    aleysian_mode = subprocess.run(
        ["git", "config", "aleysian.mode"], cwd=repo,
        capture_output=True, text=True).stdout.strip()
    if hooks_path or aleysian_mode:
        here = os.path.dirname(os.path.abspath(__file__))
        print("This repo runs the Aleysian delivery-standards stack "
              f"(core.hooksPath={hooks_path or 'unset'}, aleysian.mode={aleysian_mode or 'unset'}).")
        print("A .git/hooks/pre-commit would never fire, so none was written. Integrate instead:")
        print("  1. Copy the architecture ruleset and the combined project ruleset into config/:")
        print(f"       cp {os.path.join(here, 'pmd', 'aleysian-apex.xml')} config/aleysian-apex.xml")
        print(f"       cp <skill>/assets/pmd/pmd-ruleset-project.xml config/pmd-ruleset.xml")
        print("     (if config/pmd-ruleset.xml already exists, append the architecture rule refs")
        print("     from pmd-ruleset-project.xml instead of replacing the project's own bar)")
        print("  2. Gate 4 of the delivery-standards pre-commit now enforces the architecture")
        print("     rules; ratchet with: git config aleysian.pmd block|advise")
        print("  3. For legacy-path downgrades and suppression-reason governance, run")
        print("     arch_check.py in CI or an npm script; add the ESLint no-wire-of-apex rule")
        print("     to the repo's eslint config for gate 3 coverage of LWC001.")
        return

    if not args.no_copy:
        here = os.path.dirname(os.path.abspath(__file__))
        dest_dir = os.path.join(repo, "scripts")
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copyfile(os.path.join(here, "arch_check.py"),
                        os.path.join(dest_dir, "arch_check.py"))
        print(f"copied arch_check.py -> scripts/arch_check.py (commit it so the team shares it)")
        # Ship the PMD ruleset next to the script so the pmd engine works out of the box.
        for cand in (os.path.join(here, "pmd", "aleysian-apex.xml"),
                     os.path.join(here, "..", "assets", "pmd", "aleysian-apex.xml")):
            if os.path.isfile(cand):
                os.makedirs(os.path.join(dest_dir, "pmd"), exist_ok=True)
                shutil.copyfile(cand, os.path.join(dest_dir, "pmd", "aleysian-apex.xml"))
                print("copied aleysian-apex.xml -> scripts/pmd/ (PMD ruleset)")
                break

    hooks_dir = os.path.join(git_dir, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)
    hook_path = os.path.join(hooks_dir, "pre-commit")

    chain = ""
    if os.path.exists(hook_path):
        existing = open(hook_path, encoding="utf-8", errors="replace").read()
        if "arch_check" in existing:
            print("pre-commit hook already runs arch_check — leaving it alone")
            return
        backup = hook_path + ".pre-arch-check"
        shutil.copyfile(hook_path, backup)
        chain = f'sh "{backup}" || exit 1\n'
        print(f"existing pre-commit preserved and chained via {os.path.basename(backup)}")

    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(HOOK_BODY.format(chain=chain))
    os.chmod(hook_path, os.stat(hook_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"installed {os.path.relpath(hook_path, repo)}")
    if not os.path.exists(os.path.join(repo, ".arch-check.json")):
        print("note: no .arch-check.json found — checker will run with defaults "
              "(mode=block, no legacy paths). Copy the template from the skill's assets/.")


if __name__ == "__main__":
    main()
