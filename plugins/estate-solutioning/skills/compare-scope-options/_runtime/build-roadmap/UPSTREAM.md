# Upstream source

The outcome mode in this skill (references/outcome-roadmaps.md and scripts/outcome_check.py with its selftest and fixtures) adapts the outcome-roadmap skill from the Claude Skills Library by Amin Borghei (borghei), licensed MIT with the Commons Clause condition; the full text is in `LICENSE-UPSTREAM`. The Commons Clause withholds the right to sell the software or a product or service whose value derives entirely or substantially from it. The adapted portions keep that license. Check it before this material becomes part of a paid offering. The roadmap kit and the rest of the skill are not affected.

Upstream repository: https://github.com/borghei/Claude-Skills, commit 2c12c7efaad13a70bdea6e205698a6c4f93a0682 (2026-10-23), read from a local reference copy on 2026-11-04.

## Files adapted

| SHA-256 at adoption | Upstream path |
|---|---|
| 79c6a71dc3d3ab2a610f4209a76dd6b52139141d8b86e0e1ac254d08078df806 | project-management/execution/outcome-roadmap/SKILL.md |
| 507c3907bb4735942ad844bc94c048902c32394539f291fce33cf1a088075dd8 | project-management/execution/outcome-roadmap/references/outcome-roadmap-guide.md |
| 6c189f10216a9effc3b76b17c048c8f3541aea5cb42d6740eef05fe9870cd216 | project-management/execution/outcome-roadmap/references/outcome-roadmap-workflow.md |
| 682bd1be812e1d7b64f44ca12d0527d7bd7b36a36cff11d061d0d3cb167e2618 | project-management/execution/outcome-roadmap/references/red-flags.md |
| 5ea174ea4611980b8e6567e46fee08bccfaf9a3b476db2b2eebb0989eb3790ea | project-management/execution/outcome-roadmap/assets/outcome_roadmap_template.md |

## What changed

Upstream generated outcome-statement templates from quarter strings and never failed a plan. The estate version works on the kit's plan JSON instead. `outcome_check.py` fails a plan whose Now column exceeds the cap or whose Now outcomes name nothing to measure, and it warns on four other red flags. Horizon windows are labelled as practitioner guidance. Dependencies point at RAID IDs owned by delivery-status, and ranking stays with prioritization. The upstream transformer script and worked example were not carried over.

## Checking for upstream changes

```bash
python3 tools/upstream_drift.py --upstream /path/to/Claude-Skills
```

Review a changed file before porting anything; the kit's schema and the planning chain take precedence over upstream wording.
