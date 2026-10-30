#!/usr/bin/env python3
"""Print how many distinct engine guards are registered for Claude or Codex.

A separate file rather than a heredoc inside doctor.sh: settings.json is JSON
with no guaranteed shape, and the parsing wants real exception handling rather
than a shell pipeline that reports 0 for "no hooks" and 0 for "file unreadable"
alike. Prints a single integer; prints 0 on any failure to read or parse.
"""

import json
import os
import sys


def main() -> int:
    commands = set()
    for path in (os.path.expanduser("~/.claude/settings.json"),
                 os.path.expanduser("~/.codex/hooks.json")):
        try:
            with open(path) as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        for entry in (data.get("hooks") or {}).get("PreToolUse") or []:
            if not isinstance(entry, dict):
                continue
            for hook in entry.get("hooks") or []:
                if isinstance(hook, dict) and hook.get("command"):
                    commands.add(hook["command"])

    print(sum(1 for c in commands if ".estate-engine/" in c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
