# Skill showcase

This folder holds recorded runs of the skills: the request, the inputs and the output each skill produced. The skills map shows them in each skill's Examples tab. They are not runtime material. No plugin, task package or shared-assembly hash includes this folder, so adding or editing an example never changes a release.

Each example lives at `showcase/<skill-id>/<example-id>.md`, where `<skill-id>` is the source workflow's folder name under `skills/`.

## Format

```markdown
---
skill: call-prep
title: First discovery call with a regional freight carrier
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: <SHA-256 of skills/call-prep/SKILL.md when the run happened>
---

## Request

The request as a user would type it.

## Inputs

What the skill was given, or a summary of it.

## Output

The answer exactly as the skill produced it.
```

`source` is `fictional` for an invented scenario or `real-redacted` for redacted real work. A `real-redacted` example also needs `approvedBy`, naming the owner who approved it for the repository. The map builder rejects an example with a missing field, an unknown skill or a missing Request or Output section.

When a skill's SKILL.md changes, its older examples stay visible and the map labels them "From an older version". Record a new run to replace them.

## Recording a fictional run

Run the built task package on invented inputs: a fictional company, fictional people and fictional figures. Save the skill's actual answer. Do not write or polish the output by hand. Long outputs can be cut with a marked `[trimmed]` note. If the run could not use a connector or script, say so in Inputs.

## Adding real work

Real outputs are redacted outside the repository first and reviewed by the owner. Copy one here only after the owner approves it, and record the approver in `approvedBy`.
