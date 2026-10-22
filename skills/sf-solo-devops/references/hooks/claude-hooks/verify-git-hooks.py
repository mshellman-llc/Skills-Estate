#!/usr/bin/env python3
"""Inspect local hook wiring; never install, chmod, or replace another manager."""
import json
import os
from pathlib import Path
import shlex
import subprocess


def inspect(project):
    report = {"state": "inspected", "configuration_changed": False,
              "problems": [], "review": [], "checked": []}
    def git(*args):
        result = subprocess.run(["git", "-C", str(project), *args],
                                capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout.strip()

    code, root_text = git("rev-parse", "--show-toplevel")
    if code:
        report["state"] = "unavailable"
        report["problems"].append("The selected project is not an accessible Git checkout.")
        return report
    root = Path(root_text).resolve()
    report["project"] = str(root)
    code, configured = git("config", "--get", "core.hooksPath")
    if code not in (0, 1):
        report["problems"].append("Git hook configuration could not be read.")
    elif configured != ".githooks":
        report["review"].append(
            "core.hooksPath is " + (repr(configured) if configured else "unset") +
            ". Reconcile the existing Git hooks before selecting .githooks; "
            "the estate commit gates have not been verified as active.")
    report["configured_hooks_path"] = configured or None

    def check_file(relative, executable=True):
        candidate = root / relative
        resolved = candidate.resolve()
        if root != resolved and root not in resolved.parents:
            report["problems"].append(str(relative) + " resolves outside this checkout.")
            return
        if not candidate.is_file():
            report["problems"].append(str(relative) + " is missing.")
            return
        if executable and not os.access(candidate, os.X_OK):
            report["problems"].append(str(relative) + " is not executable.")
        if executable:
            with candidate.open("rb") as source:
                if not source.readline().startswith(b"#!"):
                    report["problems"].append(str(relative) + " has no executable shebang.")
        report["checked"].append(str(relative))

    for name in ("pre-commit", "commit-msg"):
        check_file(".githooks/" + name)

    settings = root / ".claude/settings.json"
    if not settings.is_file():
        report["problems"].append(".claude/settings.json is missing.")
        return report
    if root not in settings.resolve().parents:
        report["problems"].append(".claude/settings.json resolves outside this checkout.")
        return report
    data = json.loads(settings.read_text())
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        report["problems"].append("settings.json has no hooks object.")
        return report
    commands = []
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            report["problems"].append("Invalid hook groups for " + str(event))
            continue
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                report["problems"].append("Invalid hook group for " + str(event))
                continue
            for hook in group["hooks"]:
                if not isinstance(hook, dict):
                    report["problems"].append("Invalid hook entry for " + str(event))
                elif hook.get("type") == "command":
                    commands.append(hook.get("command"))
    if not commands:
        report["problems"].append("No command hooks are configured.")
    for command in commands:
        if not isinstance(command, str) or not command.strip():
            report["problems"].append("A command hook has no command.")
            continue
        try:
            parts = shlex.split(command)
        except ValueError:
            report["problems"].append("A hook command has malformed quoting.")
            continue
        if not parts:
            report["problems"].append("A command hook is empty after parsing.")
            continue
        first = parts[0]
        for prefix in ("${CLAUDE_PROJECT_DIR}/", "$CLAUDE_PROJECT_DIR/"):
            if first.startswith(prefix):
                first = first[len(prefix):]
        if first.startswith("./"):
            first = first[2:]
        if first.startswith(".claude/hooks/") and len(parts) == 1:
            check_file(first)
            helpers = {
                "guard-sf-flags.sh": "guard-sf-flags.py",
                "verify-git-hooks.sh": "verify-git-hooks.py",
                "record-validate.sh": "deploy-verdict.py",
                "auto-label-deploy.sh": "deploy-verdict.py",
            }
            helper = helpers.get(Path(first).name)
            if helper:
                check_file(".claude/hooks/" + helper, executable=False)
        else:
            report["review"].append(
                "A command uses a wrapper, arguments, or an external path; "
                "verify that configured command separately. It was not executed.")
    report["state"] = "needs_attention" if report["problems"] or report["review"] else "wiring_present"
    report["scope"] = "File and configuration inspection only; host invocation still needs a test."
    return report


def main():
    try:
        report = inspect(Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")))
    except (OSError, ValueError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        report = {"state": "unavailable", "configuration_changed": False,
                  "problems": ["Hook verification failed: " + str(error)]}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
