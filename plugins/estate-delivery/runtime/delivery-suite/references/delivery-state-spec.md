# DELIVERY-STATE.md specification

One file per engagement, at the engagement folder root. It mirrors the playbook
00-STATE convention: a small, human-readable, machine-parseable markdown file that
says where the engagement is, so a fresh session does not reconstruct position
from chat memory. `scripts/plan.py` parses exactly this format.

## Truth hierarchy

The state file is a pointer, never the truth. When it disagrees with anything
above it, the thing above wins and the state file gets corrected:

executed SOW/quote > artifact files > DELIVERY-STATE.md > memory > chat

The planner enforces one consequence of this: gate statuses outrank the declared
`current:` stage line. A `current:` line that disagrees with the gate ledger is a
finding, and the gates win.

## Format

```markdown
# DELIVERY-STATE

- Engagement: <client> <engagement name>
- SOW: <SOW id> (executed <date>, <path to executed copy>)
- Quote: <Q-number>
- As of: <YYYY-MM-DD of last update>

## Stage

current: <stage name, lowercase: handoff | mobilize | analyze | design | build | validate | deploy | closeout>

## Gates

- brief_accepted: <status> <date>
- charter_signed: <status> <date>
- requirements_cosigned: <status> <date>
- sdd_cosigned: <status> <date>
- build_complete: <status> <date>
- go_no_go: <status> <date>
- golive_acceptance: <status> <date>
- hypercare_closeout: <status> <date>

## Artifacts

- <artifact name>: <path, relative to the engagement folder>

## Open decisions

- <decision>, owner: <role>, resolve by: <date>, blocks: <gate key>

## Log (append only)

- <YYYY-MM-DD>: <what happened, past tense, with the role that did it>
```

## Rules

- **Gate keys and order are fixed.** The eight keys above, always all present,
  always in lifecycle order. A gate that has not been reached is `open`, never
  omitted. (Provenance rule: sections are never dropped because a fact is
  missing.)
- **Passed statuses:** `accepted`, `signed`, `met`, `issued`, `delivered`. Use
  the one that matches how the gate actually closes (a brief is accepted, a
  charter is signed, Go-Live Acceptance is issued). **Open statuses:** `open`,
  `pending`, `blocked`. Anything else is a parse finding and is treated as open.
- **Date after every passed status.** A passed gate with no date is a claim with
  no provenance; add the date from the signed artifact.
- **The log is append only.** Never edit or delete a prior line. Corrections are
  new dated lines. This is what makes the file auditable after a dispute.
- **Update on every gate event, in the same working session.** A state file that
  lags the folder makes the next plan wrong. Whichever skill closes a gate
  updates this file as part of closing it; this suite verifies the update when
  it next routes.
- **Open decisions name the gate they block.** A decision with no blocked gate
  is a note; put it in the log instead.
- **Roles, not names, where the file might travel.** Use names only in files
  that stay inside the engagement folder.
- **No numbers authored here.** Fees, hours, and dates of record live in the
  SOW and quote; this file may cite them with a pointer, never restate them as
  its own facts.

## Creating the file

The `s2d-handoff` skill creates DELIVERY-STATE.md as part of the handoff
package, seeded from the executed SOW. If an engagement predates the convention,
this suite writes one from what is on disk before routing anything: read the
engagement folder, set gate statuses only where a signed artifact proves them,
and log the reconstruction as the first entry.
