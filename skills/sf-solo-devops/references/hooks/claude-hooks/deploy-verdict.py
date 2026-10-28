#!/usr/bin/env python3
"""Interpret a complete CLI JSON result without contacting an org."""
import json
import hashlib
from pathlib import Path
import re
import shlex
import subprocess
import sys


def command_context(command):
    """Accept one literal CLI operation; ambiguous shell text carries no proof."""
    args = shlex.split(command)
    if len(args) < 4 or Path(args[0]).name not in ("sf", "sfdx"):
        raise ValueError("Not a literal Salesforce command")
    if args[1:3] != ["project", "deploy"] or args[3] not in ("start", "validate", "report", "resume", "quick"):
        raise ValueError("Not a supported deployment operation")
    if any(any(mark in arg for mark in (";", "|", "&", "`", "$(", "\n")) for arg in args):
        raise ValueError("Compound or dynamic shell text cannot establish a receipt")
    target, job = [], []
    for i, arg in enumerate(args[4:], 4):
        for names, dest in ((("--target-org", "-o"), target), (("--job-id", "-i"), job)):
            if arg in names:
                dest.append(args[i + 1])
            elif any(arg.startswith(name + "=") for name in names):
                dest.append(arg.split("=", 1)[1])
    if len(target) != 1 or not target[0] or target[0].startswith("-"):
        raise ValueError("One explicit target is required")
    if len(job) > 1 or (job and not re.fullmatch(r"0Af[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?", job[0])):
        raise ValueError("Invalid or ambiguous job")
    if args[3] in ("report", "resume", "quick") and not job:
        raise ValueError("An explicit job is required")
    if any(arg.startswith("--use-most-recent") for arg in args):
        raise ValueError("Implicit job selection is not evidence")
    if any(arg.startswith("--dry-run=") for arg in args):
        raise ValueError("Use a literal --dry-run flag")
    return {"operation": args[3], "target": target[0], "job": job[0] if job else None,
            "check": "--dry-run" in args or args[3] == "validate"}


def pending_job(payload, command):
    """Only a successful async-start response can register an in-flight job."""
    try:
        context = command_context(command)
        data = json.loads(payload)
        result = data["result"]
        job = result["id"]
        if (context["operation"] not in ("start", "validate") or
                "--async" not in shlex.split(command) or type(data.get("status")) is not int or
                data["status"] != 0 or result.get("done") not in (None, False) or
                result.get("status") not in (None, "Pending", "InProgress", "Queued") or
                not re.fullmatch(r"0Af[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?", job)):
            return ""
        if "checkOnly" in result and (type(result["checkOnly"]) is not bool or result["checkOnly"] != context["check"]):
            return ""
        return job
    except (ValueError, TypeError, KeyError, IndexError, AttributeError):
        return ""


def source_root(command):
    """Resolve every explicit source path to one Git worktree."""
    command_context(command)
    args = shlex.split(command)
    paths = []
    flags = ("--source-dir", "-d", "--manifest", "-x")
    for index, arg in enumerate(args):
        if arg in flags:
            values = []
            for value in args[index + 1:]:
                if value.startswith("-"):
                    break
                values.append(value)
            if not values:
                raise ValueError("Missing source path")
            paths.extend(values)
        elif any(arg.startswith(flag + "=") for flag in flags):
            paths.append(arg.split("=", 1)[1])
    roots = set()
    for value in paths or ["."]:
        path = Path(value).resolve(strict=True)
        directory = path if path.is_dir() else path.parent
        result = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                                capture_output=True, text=True, timeout=10, check=True)
        roots.add(str(Path(result.stdout.strip()).resolve()))
    if len(roots) != 1:
        raise ValueError("Source paths span multiple Git worktrees")
    return roots.pop()


def verdict(payload, command):
    try:
        data = json.loads(payload)
        context = command_context(command)
        result = data['result']
        result_id = result.get('id', '')
        if not re.fullmatch(r'0Af[A-Za-z0-9]{12}(?:[A-Za-z0-9]{3})?', result_id):
            return 'UNKNOWN'
        if context["job"] and context["job"] != result_id:
            return 'UNKNOWN'
        status = result.get('status')
        if status in ('Failed', 'Canceled'):
            return 'FAILED'
        if (type(data.get('status')) is not int or data['status'] != 0 or
                status != 'Succeeded' or result.get('done') is not True or
                type(result.get('checkOnly')) is not bool):
            return 'UNKNOWN'
        check_only = result['checkOnly']
        requested_check = context["check"]
        if requested_check and not check_only:
            return 'UNKNOWN'
        if context["operation"] in ("start", "quick") and not requested_check and check_only:
            return 'UNKNOWN'
        return 'VALIDATE' if check_only else 'DEPLOY'
    except (ValueError, TypeError, KeyError, IndexError, AttributeError):
        return 'UNKNOWN'


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == "--target-key":
        try:
            print(hashlib.sha256(command_context(sys.argv[2])["target"].encode()).hexdigest())
        except (ValueError, TypeError, IndexError):
            pass
    elif len(sys.argv) == 3 and sys.argv[1] == "--pending":
        print(pending_job(sys.stdin.read(), sys.argv[2]))
    elif len(sys.argv) == 3 and sys.argv[1] == "--source-root":
        try:
            print(source_root(sys.argv[2]))
        except (OSError, ValueError, TypeError, IndexError, subprocess.SubprocessError):
            sys.exit(1)
    else:
        print(verdict(sys.stdin.read(), sys.argv[1] if len(sys.argv) == 2 else ''))
