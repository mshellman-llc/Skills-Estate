#!/usr/bin/env python3
"""rewrite_scan.py - deterministic AI-tell scanner for prose-pass.

This file is the SINGLE AUTHORITATIVE HOME for all word and phrase lists
in the house writing system. Lexical tells decay once publicized (the "delve"
effect, 2024), so treat the lists below as dated data: review quarterly,
retire faded entries, add new risers. Structural/rhetorical judgment
patterns live in references/patterns.md and do not decay.

WORDLIST_UPDATED = 2026-06-12 (v4.0.0; sources: Kobak/Liang corpus studies,
Wikipedia Signs-of-AI-writing, Lohfeld evaluator commentary, field-observed
Estate tells)

Usage:
    python3 rewrite_scan.py <file> [<file> ...]
    echo "text" | python3 rewrite_scan.py
    python3 rewrite_scan.py --json <file>
    python3 rewrite_scan.py --tie-out <source> <rewrite>

Scan mode reports, with line numbers: em dashes, banned/review vocabulary,
hedges, fillers, transitions, chatbot artifacts, cutoff disclaimers, vague
attributions, generic conclusions, AI-correction artifacts (Classes A-D),
audience indictment, stakes inflation, false balance, "it's not X, it's Y"
constructions, colon density, bold and emoji tells.

Tie-out mode extracts every figure (currency, percentages, numbers) from
source and rewrite and reconciles them. A figure in the rewrite absent
from the source = INVENTED = FAIL. A source figure absent from the
rewrite = DROPPED = WARN (confirm the cut was intentional).

Exit code 1 if any BANNED-severity hits (scan) or invented figures
(tie-out) are found, 0 otherwise.
Severities:
  BANNED - always slop; the rewrite must remove every hit
  REVIEW - context-dependent; judge each occurrence individually
  INFO   - density metrics for judgment (colons, bold)
"""

import json
import re
import sys

# (category, severity, [regexes])  -- all matched case-insensitively
PATTERNS = [
    # em dash severity is decided dynamically in scan_text():
    # BANNED above 1 per 1,000 words (the hard max), REVIEW below it.
    ("em dash", "DYNAMIC", [r"—"]),
    ("banned vocabulary", "BANNED", [
        r"\bdelve[sd]?\b", r"\bdelving\b", r"\btapestry\b", r"\bparadigm\b",
        r"\bembark(s|ed|ing)?\b", r"\bbeacon\b", r"\btestament to\b",
        r"\bcutting.edge\b", r"\bleverag(e[sd]?|ing)\b", r"\bharness(es|ed|ing)?\b",
        r"\bseamless(ly)?\b", r"\bunleash(es|ed|ing)?\b", r"\bsynerg(y|ies|istic)\b",
        r"\bgame.chang(er|ing)\b", r"\butiliz(e[sd]?|ing|ation)\b",
        r"\bcommence[sd]?\b", r"\bascertain(s|ed|ing)?\b", r"\bendeavor(s|ed|ing)?\b",
        r"\btransformative\b", r"\bholistic(ally)?\b", r"\bmeticulous(ly)?\b",
        r"\bin order to\b", r"\bdue to the fact that\b", r"\bserves as\b",
        r"\bboasts?\b", r"\bnestled\b", r"\bunderscor(e|es|ed|ing)\b",
    ]),
    ("review vocabulary (judge each use)", "REVIEW", [
        r"\blandscape\b", r"\brealm\b", r"\brobust(ly|ness)?\b",
        r"\bcomprehensive(ly)?\b", r"\bpivotal\b", r"\bnavigat(e[sd]?|ing)\b",
        r"\bfoster(s|ed|ing)?\b", r"\belevat(e[sd]?|ing)\b", r"\bstreamlin(e[sd]?|ing)\b",
        r"\bempower(s|ed|ing|ment)?\b", r"\bcrucial(ly)?\b", r"\bvibrant\b",
        r"\bthriving\b", r"\bshowcas(e[sd]?|ing)\b", r"\bunlock(s|ed|ing)?\b",
        r"\bstate.of.the.art\b", r"\btailored solution\b", r"\bintricate\b",
        r"\bcommendable\b", r"\bbeyond (that|these)\b",
    ]),
    ("audience indictment", "BANNED", [
        r"\bwhat most \w+ (get|are getting) wrong\b",
        r"\bthe mistake \w+ keeps? making\b",
        r"\bleaving money on the table\b",
        r"\bproblem \w+ (isn't|aren't|is not|are not) solving\b",
    ]),
    ("stakes inflation (check for an anchoring number)", "REVIEW", [
        r"\bfundamental breakdown\b", r"\bexistential\b", r"\bat stake\b",
        r"\binability to compete\b", r"\bincreasingly complex (market|landscape|environment)\b",
    ]),
    ("false balance / too-polished quote", "BANNED", [
        r"\bwhile challenges (exist|remain)\b", r"\bfar outweigh\b",
        r"\bas one \w+ (noted|put it|observed),? [\"“']",
    ]),
    ("enthusiasm without specificity", "REVIEW", [
        r"\bremarkable results\b", r"\bmeaningful outcomes\b",
        r"\bsignificant impact\b",
    ]),
    ("hollow intensifiers / hedges", "BANNED", [
        r"\btruly\b", r"\bquite frankly\b", r"\bto be honest\b",
        r"\blet'?s be clear\b", r"\bit'?s worth noting\b",
        r"\bcould potentially\b", r"\bit is important to note\b",
        r"\bit'?s important to note\b",
    ]),
    ("transition tells", "REVIEW", [
        r"\bmoreover\b", r"\bfurthermore\b", r"^\s*additionally\b",
        r"\bin today'?s\b", r"\bin an era where\b", r"\bnotably\b",
        r"\bin conclusion\b", r"\bto summarize\b", r"\bwhen it comes to\b",
        r"\bat the end of the day\b", r"\bthat (being )?said\b",
        r"\bin terms of\b", r"\bthe reality is that\b",
    ]),
    ("chatbot artifacts", "BANNED", [
        r"\bI hope this helps\b", r"\bGreat question\b", r"\bCertainly!\B",
        r"\bAbsolutely!\B", r"\bfeel free to reach out\b",
        r"\blet me know if you (need|have)\b",
        r"\bin this (article|post|guide),? we (will|'ll)\b", r"\blet'?s dive in\b",
    ]),
    ("cutoff disclaimers", "BANNED", [
        r"\bas of my last update\b",
        r"\bspecific details are limited based on available information\b",
        r"\bbased on available information\b",
    ]),
    ("vague attributions", "REVIEW", [
        r"\bexperts (believe|say|agree)\b", r"\bstudies (show|suggest|indicate)\b",
        r"\bresearch (shows|suggests|indicates)\b",
    ]),
    ("generic conclusions", "BANNED", [
        r"\bthe future looks bright\b", r"\bonly time will tell\b",
        r"\bone thing is certain\b", r"\bas we move forward\b",
    ]),
    ("it's-not-X-it's-Y construction", "REVIEW", [
        r"\b(it|this|that)'?s not (just |only |about )?[^.;:!?]{2,60}[,;—-]\s*(it|this|that)'?s\b",
        r"\bnot just [^.;:!?]{2,40}\b(but|it'?s)\b",
    ]),
    ("scope callouts (Class A)", "BANNED", [
        r"\bthis (document|guide|section|overview|summary) (covers|addresses|focuses on|is intended to|provides|explores|examines)\b",
        r"\bthis is not an? (comprehensive|exhaustive|complete) (guide|overview|list)\b",
        r"\bfor the purposes of this (document|guide|section)\b",
        r"\bthe scope of this (document|analysis) (includes|is limited to|encompasses)\b",
        r"\bthis (guide|document) is designed to (help|assist|support|provide)\b",
        r"\bnote:? this (document|section) does not (address|cover|include)\b",
    ]),
    ("cross-reference callouts (Class B)", "REVIEW", [
        r"\bas (mentioned|noted|described|discussed|outlined|referenced) (above|below|earlier|previously)\b",
        r"\bas we (discussed|mentioned|noted|explored) (above|earlier|previously)\b",
        r"\brefer to .{1,40} for (more|additional|further) (details|context|information)\b",
        r"\bfor (more|additional|further) (information|details|context|background),? see\b",
        r"\bas (covered|explained|introduced) in the (preceding|previous) section\b",
    ]),
    ("correction hedging (Class C)", "BANNED", [
        r"\bit'?s important to (clarify|understand|recognize|acknowledge)\b",
        r"\bit'?s worth (clarifying|noting|mentioning|pointing out)\b",
        r"\b(please note|note) that this (may|might|could) (vary|differ|not apply)\b",
        r"\bresults (may|might|will) vary\b",
        r"\bthis (may|might) not apply in all (cases|situations|contexts)\b",
        r"\bgenerally speaking\b",
        r"\bthis is intended as a (starting point|foundation|baseline|framework)\b",
        r"\bplease (consult|refer to) .{1,40} for (authoritative|definitive|official)\b",
    ]),
    ("editorial framing (Class D)", "REVIEW", [
        r"\bto (understand|provide|give) (context|background|perspective)\b",
        r"\bbefore (we|you) (dive into|look at|examine|begin)\b",
        r"\bwith that (in mind|said|context established)\b",
        r"\bbuilding on (the above|this foundation|these principles)\b",
        r"\bin (the context of|light of) (this|the above)\b",
    ]),
]

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F000-\U0001F0FF\U00002600-\U000026FF]"
)


def scan_text(text):
    lines = text.splitlines()
    hits = []
    for category, severity, regexes in PATTERNS:
        for rx in regexes:
            crx = re.compile(rx, re.IGNORECASE)
            for i, line in enumerate(lines, 1):
                for m in crx.finditer(line):
                    hits.append({
                        "category": category, "severity": severity,
                        "line": i, "match": m.group(0).strip(),
                        "context": line.strip()[:120],
                    })
    # resolve dynamic em-dash severity against the 1-per-1,000-words hard max
    words = max(len(text.split()), 1)
    dash_rate = text.count("—") * 1000 / words
    for h in hits:
        if h["severity"] == "DYNAMIC":
            h["severity"] = "BANNED" if dash_rate > 1.0 else "REVIEW"
    info = {
        "word_count": words,
        "em_dash_count": text.count("—"),
        "em_dash_per_1000_words": round(text.count("—") * 1000 / words, 2),
        "colon_count": sum(l.count(":") for l in lines if not l.strip().startswith(("http", "```"))),
        "colon_lines_pct": round(100 * sum(1 for l in lines if ":" in l and l.strip()) / max(sum(1 for l in lines if l.strip()), 1)),
        "bold_phrase_count": len(re.findall(r"\*\*[^*\n]+\*\*", text)),
        "emoji_in_headers": [i for i, l in enumerate(lines, 1) if l.lstrip().startswith("#") and EMOJI_RE.search(l)],
    }
    return hits, info


def report(name, hits, info, quiet=False):
    banned = [h for h in hits if h["severity"] == "BANNED"]
    review = [h for h in hits if h["severity"] == "REVIEW"]
    print(f"=== {name} ===")
    print(f"words: {info['word_count']} | em dashes: {info['em_dash_count']} "
          f"({info['em_dash_per_1000_words']}/1000w, hard max 1.0) | "
          f"colons: {info['colon_count']} on {info['colon_lines_pct']}% of lines | "
          f"bold phrases: {info['bold_phrase_count']}")
    if info["emoji_in_headers"]:
        print(f"emoji in headers on lines: {info['emoji_in_headers']}")
    for label, group in (("BANNED", banned), ("REVIEW", review)):
        if not group:
            continue
        print(f"\n{label} ({len(group)} hits):")
        bycat = {}
        for h in group:
            bycat.setdefault(h["category"], []).append(h)
        for cat, items in bycat.items():
            if quiet:
                lines = ",".join(f"L{h['line']}" for h in items)
                terms = sorted({h["match"].lower() for h in items})
                print(f"  {cat} ({len(items)}): {terms} at {lines}")
            else:
                print(f"  {cat}:")
                for h in items:
                    print(f"    L{h['line']}: \"{h['match']}\"  | {h['context']}")
    if not banned and not review:
        print("\nNo pattern hits. Clean on the mechanical checks.")
    print(f"\nresult: {'FAIL' if banned else 'PASS'} "
          f"({len(banned)} banned, {len(review)} review)\n")
    return len(banned)


NUM_RE = re.compile(r"\$\s?[\d,]+(?:\.\d+)?[kKmM]?|\d[\d,]*(?:\.\d+)?\s?%|\d[\d,]*(?:\.\d+)?")
ENUM_RE = re.compile(r"^\s*\d+[.)]\s")  # list enumerators: "1. " / "2) "


def extract_figures(text):
    figs = set()
    for line in text.splitlines():
        line = ENUM_RE.sub("", line)
        for m in NUM_RE.finditer(line):
            tok = m.group(0).replace(",", "").replace(" ", "")
            figs.add(tok.lower())
    return figs


def tie_out(source_path, rewrite_path):
    src = extract_figures(open(source_path, encoding="utf-8", errors="replace").read())
    rew = extract_figures(open(rewrite_path, encoding="utf-8", errors="replace").read())
    invented = sorted(rew - src)
    dropped = sorted(src - rew)
    print(f"=== tie-out: {rewrite_path} vs {source_path} ===")
    print(f"source figures: {len(src)} | rewrite figures: {len(rew)}")
    if invented:
        print(f"\nFAIL - INVENTED (in rewrite, not in source): {invented}")
        print("A rewrite must never introduce a figure the source doesn't contain.")
    if dropped:
        print(f"\nWARN - DROPPED (in source, missing from rewrite): {dropped}")
        print("Confirm each cut was intentional.")
    if not invented and not dropped:
        print("\nAll figures reconcile. PASS")
    elif not invented:
        print("\nresult: PASS with warnings")
    sys.exit(1 if invented else 0)


def main():
    if "--tie-out" in sys.argv:
        paths = [a for a in sys.argv[1:] if a != "--tie-out"]
        if len(paths) != 2:
            print("usage: rewrite_scan.py --tie-out <source> <rewrite>")
            sys.exit(2)
        tie_out(paths[0], paths[1])
    args = [a for a in sys.argv[1:] if a not in ("--json", "--quiet")]
    as_json = "--json" in sys.argv
    quiet = "--quiet" in sys.argv
    sources = [(p, open(p, encoding="utf-8", errors="replace").read()) for p in args] \
        if args else [("stdin", sys.stdin.read())]
    total_banned = 0
    out = []
    for name, text in sources:
        hits, info = scan_text(text)
        if as_json:
            out.append({"file": name, "info": info, "hits": hits})
            total_banned += sum(1 for h in hits if h["severity"] == "BANNED")
        else:
            total_banned += report(name, hits, info, quiet=quiet)
    if as_json:
        print(json.dumps(out, indent=2))
    sys.exit(1 if total_banned else 0)


if __name__ == "__main__":
    main()
