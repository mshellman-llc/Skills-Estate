#!/usr/bin/env python3
"""Deterministic checks for the publish-content Evidence rules.

Flags paragraphs with more than two figures, sections denser than one figure per
40 words, rigor talk (text claiming its own sourcing) and production vocabulary
leaking into published copy. Exit 0 when nothing blocks, 1 when something does,
2 when the file cannot be read.
"""
import argparse
import json
import re
import sys

FIGURE = re.compile(r"(?<![\w.])(?:[$£€]\s?)?\d[\d,]*(?:\.\d+)?(?:\s?%|\s?(?:k|K|M|B|bn|x|×))?(?![\w])")
YEAR = re.compile(r"^(?:19|20)\d{2}$")

RIGOR = re.compile(
    r"\b(?:data|research|evidence|fact|science)[- ](?:driven|backed|based|led|grounded|informed)\b"
    r"|\bbacked by (?:real |hard )?(?:data|research|evidence|facts|science|numbers)\b"
    r"|\bgrounded in (?:real |hard |verified |the )?(?:data|evidence|research|facts)\b"
    r"|\b(?:every|each|all) (?:claims?|figures?|numbers?|facts?|statistics?|stats?)\b[^.!?\n]{0,30}\b(?:sourced|traceable|verified|cited|checked|backed|fact-checked)\b"
    r"|\b(?:fully|rigorously|carefully|independently|thoroughly) (?:sourced|cited|verified|vetted|fact-checked|researched|validated)\b"
    r"|\b(?:is|are|stays?|remains?) traceable\b|\bhard (?:data|numbers|evidence|facts)\b"
    r"|\bthe (?:data|numbers|evidence|facts) (?:speaks?|don't lie|doesn't lie|tells? the story|backs? (?:this|it) up)\b"
    r"|\b(?:verified|vetted) (?:sources|data|figures|numbers)\b|\bnot (?:opinion|guesswork|speculation|theory)\b"
    r"|\bproof (?:points?|stays?|lives?)\b|\breceipts\b|\bshow(?:s|ing)? (?:the|its|our|my) work\b",
    re.I)

LEAK = re.compile(
    r"\bload[- ]bearing\b|\bbackstage\b|\bevidence (?:file|ledger|trail|register|gate)s?\b|\basset IDs?\b"
    r"|\bregister (?:rows?|entr(?:y|ies)|IDs?)\b|\binformation[- ]gain\b|\bgate packets?\b|\brun ledger\b"
    r"|\bmeaning diff\b|\bdefect log\b|\bsource register\b|\bslop\b|\bhuman (?:sign-off|in the loop)\b"
    r"|\[(?:S|A|E)\d+\]",
    re.I)


LIST_MARKER = re.compile(r"(?:^|(?<=\s))\d+[.)](?=\s)")
LINK_TARGET = re.compile(r"\]\([^)]*\)")


def figures(text):
    text = LINK_TARGET.sub("]", LIST_MARKER.sub(" ", text))
    out = []
    for m in FIGURE.finditer(text):
        token = m.group(0).strip()
        if YEAR.match(token):
            continue
        out.append(token)
    return out


def blocks(text):
    """Split into (heading, [paragraphs]) sections; skip fenced code and tables."""
    sections, heading, para, fenced = [], "(start)", [], False
    current = []
    def flush_para():
        if para:
            current.append(" ".join(para).strip())
            para.clear()
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            flush_para()
            continue
        if fenced or line.lstrip().startswith("|"):
            flush_para()
            continue
        if re.match(r"^#{1,6}\s", line):
            flush_para()
            sections.append((heading, current))
            heading, current = line.lstrip("# ").strip(), []
            continue
        if not line.strip():
            flush_para()
        else:
            para.append(line.strip())
    flush_para()
    sections.append((heading, current))
    return [(h, ps) for h, ps in sections if ps]


def scan(text, data_piece=False, published=True, max_per_para=2, words_per_figure=40):
    findings = []
    for heading, paras in blocks(text):
        sec_words = sec_figs = 0
        for i, p in enumerate(paras, 1):
            figs = figures(p)
            words = len(p.split())
            sec_words += words
            sec_figs += len(figs)
            if not data_piece and len(figs) > max_per_para:
                findings.append({"rule": "figures-per-paragraph", "section": heading, "paragraph": i,
                                 "detail": f"{len(figs)} figures", "text": p[:120]})
            for m in RIGOR.finditer(p):
                findings.append({"rule": "rigor-talk", "section": heading, "paragraph": i, "text": m.group(0)})
            if published:
                for m in LEAK.finditer(p):
                    findings.append({"rule": "production-vocabulary", "section": heading, "paragraph": i, "text": m.group(0)})
        if not data_piece and sec_figs and sec_words / sec_figs < words_per_figure:
            findings.append({"rule": "section-density", "section": heading,
                             "detail": f"{sec_figs} figures in {sec_words} words"})
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True)
    ap.add_argument("--data-piece", action="store_true", help="numbers are the subject; skip density limits")
    ap.add_argument("--internal", action="store_true", help="internal document; skip the production-vocabulary check")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        text = open(a.file, encoding="utf-8").read()
    except OSError as e:
        print(json.dumps({"status": "incomplete", "reason": str(e)}))
        return 2
    f = scan(text, data_piece=a.data_piece, published=not a.internal)
    result = {"status": "fail" if f else "pass", "findings": f}
    if a.json:
        print(json.dumps(result, indent=1))
    else:
        print(result["status"])
        for x in f:
            print(f"  [{x['rule']}] {x['section']}: {x.get('detail') or x.get('text')}")
    return 1 if f else 0


if __name__ == "__main__":
    sys.exit(main())
