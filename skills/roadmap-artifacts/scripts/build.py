#!/usr/bin/env python3
"""Build a Roadmap Kit bundle: a folder of separate files, not one HTML file.

  python3 build.py plan.json --brand brand.md --out dist/q3-roadmap            # claude.ai Artifact (default)
  python3 build.py plan.json --brand brand.json --out public/roadmap --target web
  python3 build.py plan.json --check                                            # validate only

Writes index.html, rk.css, theme.css, rk.js, rk-live.js (when the plan has live bindings), plan.json and the
logo file. Prints the Artifact publish inputs (files map and capabilities) for --target artifact.
--brand takes a client-brand brand.md, an estate profile (brand.md with a JSON block) or a kit brand JSON.
Without it, each mode keeps its default look.
"""
import argparse
import html
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
KIT = HERE.parent
BLOCK_TYPES = {"board", "timeline", "matrix", "callouts", "meters", "table", "checklist", "text", "evidence"}


def cited(plan):
    """Every cite number on cards, callouts, table rows and timeline rows."""
    found = set()
    for b in plan.get("blocks", []):
        for item in b.get("cards", []) + b.get("items", []) + b.get("rows", []) if b.get("type") != "evidence" else []:
            if isinstance(item, dict) and item.get("cite") is not None:
                found.update(item["cite"] if isinstance(item["cite"], list) else [item["cite"]])
    return found


def check(plan):
    errs = []
    if plan.get("kit") != 1:
        errs.append('"kit" must be 1')
    if not plan.get("id"):
        errs.append('"id" is required (used to remember board moves)')
    if not (plan.get("meta") or {}).get("title"):
        errs.append('"meta.title" is required')
    groups = {g["key"] for g in (plan.get("legend") or {}).get("items", [])}
    for i, b in enumerate(plan.get("blocks", [])):
        t = b.get("type")
        where = f"blocks[{i}] ({t})"
        if t not in BLOCK_TYPES:
            errs.append(f"{where}: unknown type")
            continue
        if t in ("board", "matrix"):
            cols = {c["id"] for c in b.get("columns", [])}
            rows = {r["id"] for r in b.get("rows", [])} if t == "matrix" else None
            for c in b.get("cards", []):
                if c.get("col") not in cols:
                    errs.append(f'{where}: card "{c.get("title")}" has unknown col "{c.get("col")}"')
                if rows is not None and c.get("row") not in rows:
                    errs.append(f'{where}: card "{c.get("title")}" has unknown row "{c.get("row")}"')
                if c.get("group") and c["group"] not in groups:
                    errs.append(f'{where}: card "{c.get("title")}" uses group "{c["group"]}" missing from legend')
                if t == "board" and b.get("movable", True) and not c.get("id"):
                    errs.append(f'{where}: movable card "{c.get("title")}" needs an id')
        if t == "timeline":
            for k in ("start", "end"):
                if not b.get(k):
                    errs.append(f"{where}: {k} is required")
            ids = set()
            for r in b.get("rows", []):
                for br in r.get("bars") or ([r] if r.get("start") else []):
                    if br.get("id"):
                        ids.add(br["id"])
                    if br.get("end", "") < br.get("start", ""):
                        errs.append(f'{where}: "{br.get("label") or r.get("label")}" ends before it starts')
                    if b.get("start") and br.get("start", "") < b["start"] or b.get("end") and br.get("end", "") > b["end"]:
                        errs.append(f'{where}: "{br.get("label") or r.get("label")}" falls outside {b.get("start")}..{b.get("end")}')
            for r in b.get("rows", []):
                for br in r.get("bars") or ([r] if r.get("start") else []):
                    for dep in br.get("deps", []):
                        if dep not in ids:
                            errs.append(f'{where}: dependency "{dep}" does not match any bar id')
    cites = cited(plan)
    lists = [b for b in plan.get("blocks", []) if b.get("type") == "evidence"]
    if len(lists) > 1:
        errs.append("use one evidence block; cite numbers point to a single list")
    for b in lists:
        if not b.get("items"):
            errs.append("evidence block needs items")
        for n in sorted(cites):
            if not isinstance(n, int) or not 1 <= n <= len(b.get("items", [])):
                errs.append(f"cite {n} has no entry in the evidence block")
    live_ok = {"board", "matrix", "timeline", "table"}
    blocks = plan.get("blocks", [])
    for k, lb in enumerate(plan.get("live") or []):
        where = f"live[{k}]"
        for key in ("block", "server", "tool", "items", "map"):
            if key not in lb:
                errs.append(f"{where}: {key} is required")
        bi = lb.get("block")
        if not isinstance(bi, int) or not 0 <= bi < len(blocks):
            errs.append(f"{where}: block {bi} does not exist")
        elif blocks[bi].get("type") not in live_ok:
            errs.append(f"{where}: block {bi} is a {blocks[bi].get('type')}; live data fills board, matrix, timeline or table")
        m = lb.get("map") or {}
        is_table = isinstance(bi, int) and 0 <= bi < len(blocks) and blocks[bi].get("type") == "table"
        if not is_table and not ("id" in m and "title" in m):
            errs.append(f"{where}: map needs id and title")
        if not lb.get("verified"):
            errs.append(f"{where}: set \"verified\" to the date you observed a real {lb.get('server')} {lb.get('tool')} result and matched these paths to it. Never ship guessed paths.")
    return errs


def page(plan, target):
    title = html.escape(plan["meta"]["title"])
    live = '<script src="rk-live.js"></script>\n' if plan.get("live") else ""
    body = (f'<link rel="stylesheet" href="rk.css">\n<link rel="stylesheet" href="theme.css">\n'
            '<style>html, body { margin: 0; background: var(--brand-background, #ffffff); }</style>\n'
            f'<rk-roadmap src="plan.json" label="{title}"></rk-roadmap>\n'
            f'<script src="rk.js"></script>\n{live}')
    if target == "artifact":
        return f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + body
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<title>{title}</title>\n</head>\n<body>\n{body}</body>\n</html>\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--out")
    ap.add_argument("--brand", help="brand.md or brand JSON; default: themes/neutral.json")
    ap.add_argument("--allow-draft", action="store_true", help="the user said to proceed on a draft brand profile")
    ap.add_argument("--target", choices=["artifact", "web"], default="artifact")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    plan_path = pathlib.Path(a.plan)
    plan = json.loads(plan_path.read_text())
    errs = check(plan)
    for e in errs:
        print("plan error:", e, file=sys.stderr)
    if errs:
        sys.exit(1)
    if a.check:
        print("plan ok")
        return
    if not a.out:
        sys.exit("--out is required")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    brand = pathlib.Path(a.brand) if a.brand else None
    if brand:
        cmd = [sys.executable, str(HERE / "brand.py"), str(brand), "-o", str(out / "theme.css")]
        if a.allow_draft:
            cmd.append("--allow-draft")
        r = subprocess.run(cmd, capture_output=True, text=True)
        sys.stdout.write(r.stdout)
        if r.returncode:
            sys.stderr.write(r.stderr)
            sys.exit(r.returncode)
    else:
        (out / "theme.css").write_text("/* No brand profile: each mode keeps its default look (Work: Venture, Pastel: Coursify, Present: Avalon). */\n")
        print("No --brand given: theme.css is empty and each mode keeps its default look.")
    files = ["rk.css", "rk.js"] + (["rk-live.js"] if plan.get("live") else [])
    for f in files:
        shutil.copyfile(KIT / "assets" / f, out / f)
    logo = (plan.get("meta") or {}).get("logo")
    if logo and logo.get("file"):
        src = (plan_path.parent / logo["file"]).resolve()
        if not src.exists():
            src = (brand.parent / logo["file"]).resolve()
        shutil.copyfile(src, out / src.name)
        logo["src"] = src.name
        files.append(src.name)
    (out / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    (out / "index.html").write_text(page(plan, a.target))
    files += ["theme.css", "plan.json"]
    print(f"wrote {out}/: index.html, " + ", ".join(files))
    if a.target == "artifact":
        fmap = {f: str(out / f) for f in files}
        print("\nArtifact publish inputs:")
        print("  file_path:", out / "index.html")
        print("  files:", json.dumps(fmap))
        if plan.get("live"):
            servers = {}
            for lb in plan["live"]:
                servers.setdefault(lb["server"], set()).add(lb["tool"])
            caps = {"mcp": {"servers": [{"server": s, "tools": sorted(t)} for s, t in servers.items()]}}
            print("  capabilities:", json.dumps(caps))


if __name__ == "__main__":
    main()
