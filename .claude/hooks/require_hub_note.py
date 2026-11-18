#!/usr/bin/env python3
"""Claude Code Stop hook: a session that did real work saves a Hub session note before it ends.

Blocks the stop once, with a reason Claude reads, when the transcript has at least
MIN_TOOL_CALLS tool calls and no call to the Knowledge Hub's save_update tool.
It never blocks twice in a row (stop_hook_active), so it cannot loop.
"""
import json, sys

MIN_TOOL_CALLS = 3

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("stop_hook_active"):
        return 0
    path = data.get("transcript_path")
    if not path:
        return 0
    calls, saved = 0, False
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                content = (ev.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "tool_use":
                        calls += 1
                        if str(part.get("name", "")).endswith("save_update"):
                            saved = True
    except OSError:
        return 0
    if saved or calls < MIN_TOOL_CALLS:
        return 0
    print(json.dumps({
        "decision": "block",
        "reason": ("Before ending: save a Knowledge Hub session note with save_update "
                   "(kind session, a known project_id, a stable key, summary, files_changed, next_step), "
                   "then check get_save_receipt. Never call write_record. If the Hub is not connected, "
                   "say so in one line and stop."),
    }))
    return 0

if __name__ == "__main__":
    sys.exit(main())
