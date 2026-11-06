# Upstream source

This skill adapts material from the Claude Skills Library by Amin Borghei (borghei), licensed MIT with the Commons Clause condition; the full text is in `LICENSE-UPSTREAM`. The Commons Clause withholds the right to sell the software or a product or service whose value derives entirely or substantially from it. The adapted portions keep that license. Check it before this skill, or material built from it, becomes part of a paid offering.

Upstream repository: https://github.com/borghei/Claude-Skills, commit 2c12c7efaad13a70bdea6e205698a6c4f93a0682 (2026-10-23), read from a local reference copy on 2026-11-04.

## Files adapted

| SHA-256 at adoption | Upstream path |
|---|---|
| 4db7c82a76ac38a8baa7057655937e23116c831bffb80ecb086938227deb979a | project-management/execution/backlog-refinement/SKILL.md |
| 66b7c79e682e2202aa478d3dcab651f1e08bcb8a9b7d9b8f84f8580f52d77b8b | project-management/execution/backlog-refinement/scripts/refinement_scorer.py |
| fdacc5ab8234931cd6da7ce28ab73801e6e0a44158750cc40f4fe6afbee5f47d | project-management/execution/backlog-refinement/references/invest-and-splitting-guide.md |
| d87995e16c4629afc1f5c87cfaeaa97977f267eaaa2cbef11ba51ef8a4ae0d47 | project-management/execution/backlog-refinement/references/refinement-playbook.md |
| 5128ceec9d4df7cda9e46d917a25ef69028e496953b0eb5ec4b5d3e57ab0a6ee | project-management/execution/backlog-refinement/references/red-flags.md |
| f1773108bcb0a555ff31e2616b4d5ee2eb32cd1da04741ae01cd5dc67a306f2f | project-management/execution/backlog-refinement/assets/refinement_checklist.md |
| 9d1aa2c69ac97920e1ea11e1e3f1de2c1ab7e78edf516848e549a3a916df89b3 | project-management/execution/story-splitting/SKILL.md |
| acdb50fb0abfa3399794202325bf3f85c4a5339f7e1c094b2bf264f1f45a9512 | project-management/execution/story-splitting/references/splitting-patterns-guide.md |
| 6695e01707dc4cd95ee90d91e8594e856eaa20a98dded4c398cb8db7aad9d7be | project-management/execution/story-splitting/references/story-splitting-procedure.md |

## What changed

The grader reads the requirements-capture Requirements tab (CSV or JSON) with its column names instead of the upstream why/what JSON. Testable requires a complete Gherkin scenario instead of four acceptance criteria. Valuable checks that So That states a change rather than matching a keyword list. Independent accepts dependencies tracked as RAID D-### entries. Verdicts carry the refinement-session counter, and the tool exits 1 when any graded item is not READY. The upstream story-splitting skill and the refinement splitting guide disagreed on the nine patterns; splitting.md keeps every pattern from both, records the disagreement, and adds how a split is recorded in the requirements workbook. The upstream red flags became the failure-mode table in SKILL.md. Upstream mermaid, Confluence, Notion and Linear output formats were not carried over.

## Checking for upstream changes

```bash
python3 tools/upstream_drift.py --upstream /path/to/Claude-Skills
```

The tool compares each path above with the upstream checkout and lists files that changed or disappeared. Review a changed file before porting anything; this skill's own rules and the planning chain take precedence over upstream wording.
