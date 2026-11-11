#!/usr/bin/env python3
"""Structural gate for the Estate business case draft (markdown).

Deliberately light: this artifact lives on judgment, and the honest weighing
cannot be scripted. What CAN be checked deterministically is checked here:

  1. The five load-bearing sections exist and have content
     (executive frame, economics, case against, risk, the ask).
  2. The case-against section is non-empty (three or more content lines).
  3. Every line carrying a currency figure or percentage ends with a source
     token: [src: ...], [quote: ...], [inferred: ...], [gap: ...],
     or [computed: ...].
  4. At least one printed cost-of-delay computation exists in the economics
     (or cost-of-waiting) content, and every shown product in the document
     recomputes within 1 percent.
  5. No em dash anywhere in the file.

Contextual sections (client and gap, timing, investment and delivery) warn
when absent; the flex table in references/section-catalog.md governs whether
that is acceptable.

Usage: python3 case_gate.py CASE.md
Exit 0 on pass, 1 on fail, 2 on usage error. Stdlib only.
"""

import re
import sys

EM_DASH = "\u2014"

SOURCE_TOKEN = re.compile(r"\[(src|quote|inferred|gap|computed):[^\]]*\]")
CURRENCY = re.compile(r"\$\s?\d")
PERCENT = re.compile(r"\d(?:\.\d+)?\s?%")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
NUM = r"\$?\s?(\d[\d,]*(?:\.\d+)?)"
PRODUCT = re.compile(
    NUM + r"(?:\s*/\s*\w+)?\s*[x\*×]\s*" + NUM + r"(?:\s*\w+)?\s*=\s*" + NUM
)

# Domains claim headings in this order so a heading like "The case against
# the investment" satisfies case_against, not investment.
LOAD_BEARING = [
    ("case against", r"case\s+against|\bagainst\b"),
    ("executive frame", r"executive\s+frame|recommendation"),
    ("economics", r"economics|case\s+for|benefit|value|cost\s+of\s+(waiting|delay|inaction)"),
    ("risk", r"\brisks?\b"),
    ("the ask", r"\bask\b|\bdecision\b|approval"),
]
CONTEXTUAL = [
    ("client and gap", r"\bgap\b|client|customer|situation"),
    ("timing", r"why\s+now|timing|moment|window"),
    ("investment and delivery", r"investment|delivery"),
]


def parse_sections(lines):
    """Return list of (heading_text, [content lines]) in document order."""
    sections = []
    current = None
    in_fence = False
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            if current:
                current[1].append(line)
            continue
        m = HEADING.match(line)
        if m:
            current = (m.group(1).strip(), [])
            sections.append(current)
        elif current is not None:
            current[1].append(line)
    return sections


def assign_domains(sections):
    """Claim headings for domains, load-bearing first, in priority order."""
    claimed = {}
    taken = set()
    for name, pattern in LOAD_BEARING + CONTEXTUAL:
        rx = re.compile(pattern, re.IGNORECASE)
        for idx, (heading, _content) in enumerate(sections):
            if idx in taken:
                continue
            if rx.search(heading):
                claimed[name] = idx
                taken.add(idx)
                break
    return claimed


def content_lines(section):
    return [ln for ln in section[1] if ln.strip()]


def check(path):
    failures = []
    warnings = []
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        print(f"FAIL cannot read {path}: {exc}")
        return 2

    lines = text.splitlines()

    # 5. em dashes
    for n, line in enumerate(lines, 1):
        if EM_DASH in line:
            failures.append(f"line {n}: em dash present")

    sections = parse_sections(lines)
    claimed = assign_domains(sections)

    # 1. load-bearing sections present and non-empty
    for name, _ in LOAD_BEARING:
        if name not in claimed:
            failures.append(f"load-bearing section missing: {name}")
        elif len(content_lines(sections[claimed[name]])) < 2:
            failures.append(f"load-bearing section empty: {name}")

    # 2. case against gets a stricter floor
    if "case against" in claimed:
        n_lines = len(content_lines(sections[claimed["case against"]]))
        if n_lines < 3:
            failures.append(
                f"case-against section too thin: {n_lines} content line(s), need 3+"
            )

    # contextual sections warn only
    for name, _ in CONTEXTUAL:
        if name not in claimed:
            warnings.append(f"contextual section absent: {name} (flex table governs)")

    # 3. every figure line carries a source token
    in_fence = False
    for n, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or HEADING.match(line):
            continue
        if (CURRENCY.search(line) or PERCENT.search(line)) and not SOURCE_TOKEN.search(line):
            failures.append(f"line {n}: figure without a source token")

    # 4a. shown products recompute
    for n, line in enumerate(lines, 1):
        for m in PRODUCT.finditer(line):
            a, b, c = (float(g.replace(",", "")) for g in m.groups())
            if c == 0 or abs(a * b - c) / max(abs(c), 1e-9) > 0.01:
                failures.append(
                    f"line {n}: arithmetic does not compute ({a} x {b} != {c})"
                )

    # 4b. at least one printed computation in economics / cost-of-waiting content
    delay_rx = re.compile(r"cost\s+of\s+(waiting|delay|inaction)|economics", re.IGNORECASE)
    delay_text = []
    for heading, content in sections:
        if delay_rx.search(heading):
            delay_text.extend(content)
    if "economics" in claimed:
        delay_text.extend(sections[claimed["economics"]][1])
    if not any(PRODUCT.search(ln) for ln in delay_text):
        failures.append(
            "no printed cost-of-delay computation found in economics or "
            "cost-of-waiting content (need inputs x interval = result)"
        )

    for w in warnings:
        print(f"WARN {w}")
    for f in failures:
        print(f"FAIL {f}")
    print(
        f"case_gate: {len(failures)} fail, {len(warnings)} warn, "
        f"{len(sections)} sections, {len(claimed)} domains matched"
    )
    return 1 if failures else 0


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    return check(argv[1])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
