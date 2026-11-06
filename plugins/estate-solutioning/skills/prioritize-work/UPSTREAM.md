# Upstream source

This skill adapts material from the Claude Skills Library by Amin Borghei (borghei), licensed MIT with the Commons Clause condition; the full text is in `LICENSE-UPSTREAM`. The Commons Clause withholds the right to sell the software or a product or service whose value derives entirely or substantially from it. The adapted portions keep that license. Check it before this skill, or material built from it, becomes part of a paid offering.

Upstream repository: https://github.com/borghei/Claude-Skills, commit 2c12c7efaad13a70bdea6e205698a6c4f93a0682 (2026-10-23), read from a local reference copy on 2026-11-04.

## Files adapted

| SHA-256 at adoption | Upstream path |
|---|---|
| 1e6a0ec869145ac36762604849ffe6e3fc8e12ab5e966893fb864cf794e57756 | project-management/execution/prioritization-frameworks/SKILL.md |
| 03d29678803d13eb5e2789a069d9a2c14b2d1cc92fb0f6e240c2480ff47b0209 | project-management/execution/prioritization-frameworks/scripts/prioritization_scorer.py |
| 1b67683fa4038fd4eeab654381ae4aa51d001fa45b86dd5e5816b98ea952c040 | project-management/execution/prioritization-frameworks/references/frameworks-catalog.md |
| 5c7ddb43a3c1bf04451baef80f65b78221f792973c30dad99f303a8670d364be | project-management/execution/prioritization-frameworks/references/prioritization-guide.md |
| 778d61a5b02715b1d66b088e54f1cbaa94c42c8fa11b75e0cefeeb3c05f8bb00 | project-management/execution/prioritization-frameworks/references/red-flags.md |

## What changed

The scorer runs on Python 3.9 (upstream needed 3.10). It adds WSJF and Ulwick's ODI formula next to Olsen's Opportunity Score, which upstream labelled as the only opportunity formula. Three upstream red flags became enforced rules: unsourced confidence above 50% is capped, unsourced effort is flagged, and uniform top impact is reported. Items without a named job or problem are flagged. MoSCoW is no longer scored by the tool because requirements-capture owns those values. The selftest checks that sourced RICE inputs reproduce the upstream demo scores exactly.

## Checking for upstream changes

```bash
python3 tools/upstream_drift.py --upstream /path/to/Claude-Skills
```

The tool compares each path above with the upstream checkout and lists files that changed or disappeared. Review a changed file before porting anything; this skill's own rules and the planning chain take precedence over upstream wording.
