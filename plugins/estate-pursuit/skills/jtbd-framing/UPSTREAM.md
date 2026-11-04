# Upstream source

The workshop material in this skill (references/workshop-facilitation.md and the four files in assets/) adapts the jtbd-workshop skill from the Claude Skills Library by Amin Borghei (borghei), licensed MIT with the Commons Clause condition; the full text is in `LICENSE-UPSTREAM`. The Commons Clause withholds the right to sell the software or a product or service whose value derives entirely or substantially from it. The adapted portions keep that license. Check it before this material becomes part of a paid offering. The rest of the skill keeps its own license in `LICENSE`.

Upstream repository: https://github.com/borghei/Claude-Skills, commit 2c12c7efaad13a70bdea6e205698a6c4f93a0682 (2026-10-23), read from a local reference copy on 2026-11-04.

## Files adapted

| SHA-256 at adoption | Upstream path |
|---|---|
| 23243e0ebd50d32f189093ae3b8239f4a0d8690bad25a95e1b58538442b377fd | project-management/discovery/jtbd-workshop/SKILL.md |
| 220e52611c66725b8c35232b5b7a601ddb247ed3fda3d7ee80be94bef7a182f6 | project-management/discovery/jtbd-workshop/references/facilitation-playbook.md |
| 91ba39c39281f720fa64b3917a4050a647274fbee162e9f81087e9c38f9dfcd0 | project-management/discovery/jtbd-workshop/assets/forces_of_progress_canvas.md |
| 9fed788ac1ba14ae6888f29528833fd6a07d1e7f4263d337f66952748f90fe51 | project-management/discovery/jtbd-workshop/assets/pre_work_email.md |
| 7e988c5384d9330ae4b83fe35e7131a0c4e66b994694075477841225b5d38430 | project-management/discovery/jtbd-workshop/assets/switch_interview_script.md |
| 7849e08437f015d8ecb316ef147ddcd650a7991eff88a02cb60facdb26fb253f | project-management/discovery/jtbd-workshop/assets/workshop_agenda_2hr.md |
| 426ff0f4ab05e1a2cb0d8b3e33b838499f02000607473095e006356a33dd4c90 | project-management/discovery/jtbd-workshop/assets/workshop_agenda_4hr.md |
| 1a36d023c1a52fba77bb2c1fc46dfe4b118028319481e1c1450714f97b8d872e | project-management/discovery/jtbd-workshop/assets/workshop_agenda_8hr.md |

## What changed

The three agenda files became one. Each format now has an evidence minimum, and the workflow starts by naming the decision the workshop informs, so a workshop held without switch-interview evidence is treated as the ritual failure this skill already describes. Scores that participants give on the customer's behalf are labelled internal, and ODI scoring runs through `prioritization --framework odi`. Hand-offs name estate skills instead of upstream ones. The upstream worked example and its figures were not carried over.

## Checking for upstream changes

```bash
python3 tools/upstream_drift.py --upstream /path/to/Claude-Skills
```

Review a changed file before porting anything; this skill's evidence rules take precedence over upstream wording.
