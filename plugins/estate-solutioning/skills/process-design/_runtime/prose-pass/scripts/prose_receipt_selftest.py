#!/usr/bin/env python3
"""Self-test for prose_receipt.py: the bypass and lazy-pass regressions.

Each case is a receipt scenario with the exit code and failure codes it must
produce. The two that matter most are the regressions this tool exists for: a
byte-identical result with no justification must fail (lazy pass), and a
no-change claim on prose the checker still fails must fail (a known poor-prose
fixture cannot be waved through). Sound prose left alone with a justification
must pass, so the tool never demands arbitrary edits.

Standard library only. Exits nonzero if any expectation breaks.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / "prose_receipt.py"

SLOP = (
    "In today's rapidly evolving landscape, we leverage robust synergies to "
    "deliver seamless, holistic transformation. We delve into transformative "
    "outcomes.\n"
)

SOUND = (
    "Quote turnaround dropped from six days to 41 hours after the rating API "
    "went live on 2026-03-02. Gene Marsh now reviews eleven exceptions a week "
    "instead of building every quote himself.\n"
)

SOUND_REWRITTEN = (
    "Quote turnaround dropped from six days to 41 hours after the rating API "
    "went live on 2026-03-02. Gene Marsh now reviews eleven exceptions a week. "
    "The regional managers build the standard quotes themselves.\n"
)

WARNING_ONLY = (
    "The parser serves as the entry point. The router stands as the final gate.\n"
)


def run(args: list) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL)] + args,
                          capture_output=True, text=True)


def emit(artifact: Path, out: Path, extra: list) -> subprocess.CompletedProcess:
    return run(["emit", str(artifact), "--out", str(out)] + extra)


def main() -> int:
    failures = []

    def expect(name: str, ok: bool, detail: str = "") -> None:
        print("  {}: {}".format(name, "OK" if ok else "FAIL " + detail))
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # 1. Sound prose, genuinely rewritten: receipt emits and validates.
        before = root / "sound-before.md"
        before.write_text(SOUND, encoding="utf-8")
        after = root / "sound.md"
        after.write_text(SOUND_REWRITTEN, encoding="utf-8")
        receipt = root / "r1.json"
        p = emit(after, receipt, ["--before-file", str(before),
                                  "--change", "structure: split a balanced clause",
                                  "--protected", "figures: 41 hours, 2026-03-02"])
        expect("rewrite_emits_clean", p.returncode == 0, p.stdout + p.stderr)
        p = run(["validate", str(receipt)])
        expect("rewrite_validates", p.returncode == 0, p.stdout)

        # 2. Lazy pass: byte-identical, no justification. Must fail.
        same = root / "same.md"
        same.write_text(SOUND, encoding="utf-8")
        receipt = root / "r2.json"
        p = emit(same, receipt, [])
        expect("lazy_pass_rejected", p.returncode == 1 and "lazy-pass" in p.stdout,
               p.stdout)

        # 3. Justified no-change on sound prose: must pass. No arbitrary edits
        #    demanded when the prose is already right.
        receipt = root / "r3.json"
        p = emit(same, receipt,
                 ["--no-change-justification",
                  "Reviewed 2026-08-18: specific, sourced, checker-clean."])
        expect("justified_no_change_passes", p.returncode == 0, p.stdout)

        # 4. Known poor-prose fixture claiming no change needed: must fail.
        #    A justification cannot wave through prose the checker fails.
        slop = root / "slop.md"
        slop.write_text(SLOP, encoding="utf-8")
        receipt = root / "r4.json"
        p = emit(slop, receipt,
                 ["--no-change-justification", "Looks fine to me."])
        expect("hollow_justification_rejected",
               p.returncode == 1 and "hollow-justification" in p.stdout, p.stdout)

        # 5. WARN-only prose is still unfinished. A no-change justification
        #    cannot convert a checker warning into a valid receipt.
        warned = root / "warned.md"
        warned.write_text(WARNING_ONLY, encoding="utf-8")
        receipt = root / "r-warning.json"
        p = emit(warned, receipt,
                 ["--no-change-justification", "The construction is acceptable."])
        expect("warning_disposition_rejected",
               p.returncode == 1 and "hollow-justification" in p.stdout, p.stdout)

        # 6. Poor prose actually corrected: the same fixture rewritten to
        #    substance emits a clean receipt. This is the substantive-correction
        #    path the poor-prose fixture must be able to take.
        fixed = root / "fixed.md"
        fixed.write_text(SOUND, encoding="utf-8")
        receipt = root / "r5.json"
        p = emit(fixed, receipt,
                 ["--before-file", str(slop),
                  "--change", "vocabulary: removed banned terms",
                  "--change", "specificity: replaced generic claims with figures",
                  "--added-figure", "41:rating API launch report",
                  "--added-figure", "2026:rating API launch report",
                  "--added-figure", "03:rating API launch report, date part",
                  "--added-figure", "02:rating API launch report, date part"])
        expect("corrected_slop_passes", p.returncode == 0, p.stdout + p.stderr)

        # 7. Changed text with no logged changes: must fail.
        receipt = root / "r6.json"
        p = emit(fixed, receipt, ["--before-file", str(slop)])
        expect("unlogged_changes_rejected",
               p.returncode == 1 and "unlogged-changes" in p.stdout, p.stdout)

        # 8. Figure invention: a number in the rewrite absent from the source.
        invented = root / "invented.md"
        invented.write_text(SOUND + "Savings reached $2,400,000.\n", encoding="utf-8")
        receipt = root / "r7.json"
        p = emit(invented, receipt,
                 ["--before-file", str(before), "--change", "added a claim"])
        expect("figure_invention_rejected",
               p.returncode == 1 and "figure-invention" in p.stdout, p.stdout)

        # 9. An old receipt cannot waive a finding through unresolved_flags.
        target = root / "unresolved.md"
        target.write_text(SOUND, encoding="utf-8")
        receipt = root / "r-unresolved.json"
        emit(target, receipt,
             ["--no-change-justification", "Checker-clean source prose."])
        data = json.loads(receipt.read_text(encoding="utf-8"))
        data["unresolved_flags"] = [
            {"rule": "C18-copula-avoidance", "reason": "accepted"}
        ]
        receipt.write_text(json.dumps(data), encoding="utf-8")
        p = run(["validate", str(receipt)])
        expect("unresolved_disposition_rejected",
               p.returncode == 1 and "unresolved-not-allowed" in p.stdout, p.stdout)

        # 10. Tamper after the receipt: validate must fail on hash-mismatch.
        target = root / "tamper.md"
        target.write_text(SOUND, encoding="utf-8")
        receipt = root / "r8.json"
        emit(target, receipt, ["--no-change-justification", "Checker-clean."])
        target.write_text(SOUND + "One more sentence.\n", encoding="utf-8")
        p = run(["validate", str(receipt)])
        expect("tamper_rejected",
               p.returncode == 1 and "hash-mismatch" in p.stdout, p.stdout)

        # 11. Bypass shape: a receipt missing required fields is invalid.
        broken = root / "r9.json"
        broken.write_text(json.dumps({"artifact": str(target)}), encoding="utf-8")
        p = run(["validate", str(broken)])
        expect("missing_fields_rejected",
               p.returncode == 1 and "missing-field" in p.stdout, p.stdout)

    if failures:
        print("prose_receipt_selftest: {} failure(s): {}".format(
            len(failures), ", ".join(failures)))
        return 1
    print("prose_receipt_selftest: PASS (11 cases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
