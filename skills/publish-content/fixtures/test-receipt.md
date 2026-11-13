# Test receipt, 13 Nov 2026

Draft built outside the repository; the Skills-Estate checkout was not reachable from this session.

| Check | Command | Result |
| --- | --- | --- |
| Script self-test | python3 scripts/evidence_scan_selftest.py | 8 checks passed |
| Isolated package | copy to an empty folder, run the self-test and a scan of SKILL.md | passed; first run exposed list markers counted as figures, fixed and covered by a new test |
| Writing gate | owner writing check (rules folder copy of 13 Nov) on SKILL.md and every reference | pass; two files pass with receipts for the quoted ban list and a source title |
| Local links | scan of every relative .md link | none broken |
| Rescue fixture | evidence_scan.py and the owner writing check on fixtures/rescue-input.md | both exit 1; caught rigor talk, figure overload and the signpost; rescue-expected.md records the procedure's decision |

Not run yet:

- The estate's own gate (skills/writing-diagnostics writing_check.py with house.json), private-terms check, tools/estate.py validate and build.
- Host selection for the positive, adjacent and negative prompts in governance.yaml.
- A full pipeline run on a real topic with the owner's evidence; cost and efficiency stay unknown until then.
