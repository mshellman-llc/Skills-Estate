# Upstream source

This skill adapts material from the Claude Skills Library by Amin Borghei (borghei), licensed MIT with the Commons Clause condition; the full text is in `LICENSE-UPSTREAM`. The Commons Clause withholds the right to sell the software or a product or service whose value derives entirely or substantially from it. The adapted portions keep that license. Check it before this skill, or material built from it, becomes part of a paid offering.

Upstream repository: https://github.com/borghei/Claude-Skills, commit 2c12c7efaad13a70bdea6e205698a6c4f93a0682 (2026-10-23), read from a local reference copy on 2026-11-04.

## Files adapted

| SHA-256 at adoption | Upstream path |
|---|---|
| 3b27234149ba39466d0761e2f86da8a789d0afde946097ed0ee77c7a6a6b5026 | project-management/execution/sprint-plan/SKILL.md |
| e57db136ad6d5d601a8d751d2b722a08d169d7d3fb667f412de2e489e2a9f83f | project-management/execution/sprint-plan/scripts/sprint_planner.py |
| 2e9f122302f479d0d01654f645fbdeb07f51d128cfe112edcf057ec81159a251 | project-management/execution/sprint-plan/references/capacity-math.md |
| 9434a0a0795822e0bf1ca9d1da68e7430381f1b3d342d1cde2df9f8660a20a3f | project-management/execution/sprint-plan/references/sprint-anti-patterns.md |
| 5893d6e0fa0872ec18e3196648bacc641906a56c16e9c6146e1d139f07363dc3 | project-management/execution/sprint-plan/assets/sprint_plan_template.md |

## What changed

The gate was rewritten for the estate. It computes capacity per person, exits 1 on fail findings, reads the backlog-refinement readiness report instead of a self-reported refined flag, checks RAID dependency IDs against the RAID log, and checks the team's own definition of done instead of a fixed four-item list. The capacity reference merges the upstream capacity math and anti-pattern files, labels their ranges as starting assumptions to calibrate, and keeps the worked examples, drains, ramp, velocity and checklist content. Integration with Jira and the upstream mermaid, Confluence, Notion and Linear output formats were not carried over; the estate tool writes Markdown and JSON.

## Checking for upstream changes

```bash
python3 tools/upstream_drift.py --upstream /path/to/Claude-Skills
```

The tool compares each path above with the upstream checkout and lists files that changed or disappeared. Review a changed file before porting anything; this skill's own rules and the planning chain take precedence over upstream wording.
