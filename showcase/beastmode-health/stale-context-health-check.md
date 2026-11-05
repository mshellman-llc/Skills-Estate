---
skill: beastmode-health
title: Diagnosing missing phone notes and a stalled photo index
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 0ce765154b0ab3cdbf638c3cd4e5e7697a89f3444d9dbba89d22a81ee4e20320
---

## Request

$beastmode-health Notes I saved from my phone yesterday aren't showing up when I ask the assistant on my laptop, and the survey photos folder seems to have stopped indexing. Check what is working and what needs attention. I've pasted the health response and an export of the hub state; don't change anything.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `beastmode-health` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### check_health-response.md

#### check_health response (pasted by user)

Observed: 2026-11-04T08:10:00Z
Route: remote gateway (web assistant)
Actor scope: priya-anand, common contract plus own private records
Contract revision (get_context): r212
Retrieval revision (pinned fetch of note "Site visit 3 Nov"): r209

```
status: ok
visible_findings: 0
backup: null
budget: null
bridge: null
jobs: null
```

Note from Priya: the phone save of "Site visit 3 Nov" returned "saved" on 2026-11-03 around 16:20Z.

#### hub-state-export.md

#### Hub state export (read-only, taken 2026-11-04T08:10:00Z)

Config used (owner-authorized, outside the package):
runtimeRoot /Users/priya/BeastModeRuntime; offMacBackupDir /Volumes/OffsiteVault/hub-backups;
bridgeMaxAgeSeconds 900; mountRoots /Volumes/FieldData;
skillEntrypoints /Users/priya/skills/beastmode-capture/SKILL.md, /Volumes/FieldData/skills/photo-index/SKILL.md;
launchdJobs com.example.beastmode.maintenance

manifest.json generation: 418

settings.last_backup: at 2026-11-04T02:00:12Z, generation 418, offService false,
  destination /Users/priya/BeastModeRuntime/backups/hub-418-20261104.enc, recorded sha256 matches file (recomputed)

settings.last_restore: at 2026-10-27T03:15:40Z, state passed, generation 391, records 5120,
  backupHash matches file hub-391-20261027.enc

Off-Mac folder listing: hub-412-20261101.enc, hub-415-20261102.enc (separate volume from runtime)

bridge (latest heartbeat): at 2026-11-04T07:41:05Z
  roots: /Users/priya/Notes mounted; /Volumes/FieldData not mounted
  sources: field-notes ok; survey-photos offline-or-missing

jobs (newest first):
  ingest        done    2026-11-04T07:30:00Z
  maintenance-cycle failed 2026-11-02T03:00:04Z
  maintenance-cycle done   2026-10-30T03:00:02Z

skill entrypoints: beastmode-capture/SKILL.md readable;
  /Volumes/FieldData/skills/photo-index/SKILL.md not found (FieldData not a mount point)

launchctl print com.example.beastmode.maintenance: state = waiting

## Output

**The hub is reachable, but retrieval is behind and the photo index is stopped. Nothing here was changed.**

The most important next action is to mount `/Volumes/FieldData` on the Mac. That fixes the photo indexing. Then rerun the maintenance cycle, which has been failing since 2 Nov.

#### Scope of this check

- Observed 2026-11-04T08:10Z.
- Route: remote gateway (web assistant), actor `priya-anand`, common contract plus your own private records.
- Local evidence: your hub-state export, read with the `collect_evidence.py` rules. I applied those rules by hand because I can't run scripts here. I did not probe the Mac or the launchd job live.
- The hub runs only on the Mac. While the Mac is asleep or offline, Mac-local agents and every remote client lose access.

#### Why the phone note is missing

The pinned fetch of "Site visit 3 Nov" returned revision **r209**. The contract revision is **r212**. Retrieval is three revisions behind, so the assistant on your laptop is reading older context. The phone's "saved" reply on 3 Nov (~16:20Z) shows the save was accepted. It doesn't show the note was indexed.

I can't name the cause from this evidence. The likely suspects are the failed maintenance cycle (F-02) and the stopped photo source (F-01). The export doesn't show which one blocks the note. The note's own record and the ingest log would show it. Ingest itself ran fine at 07:30Z.

#### Findings

| ID | Area | Status | Evidence |
|---|---|---|---|
| F-01 | Bridge / sources | Needs attention | Latest heartbeat 07:41:05Z is 29 min old, over the 15 min limit. `/Volumes/FieldData` is not mounted and `survey-photos` is offline-or-missing. `field-notes` is ok. |
| F-02 | Maintenance job | Needs attention | `maintenance-cycle` failed 2026-11-02T03:00Z. The last success was 30 Oct. Launchd shows the job as `waiting`. Waiting is normal between runs, so the failed run is the real signal. |
| F-03 | Restore evidence | Needs attention | The last isolated restore (27 Oct, generation 391, 5,120 records, passed) predates the failed cycle and covers an old generation. The current generation is 418. The restore is not evidence for the current data. |
| F-04 | Off-Mac backup | Needs attention | The latest backup (generation 418, 02:00Z today) is local only. Off-Mac holds generations 412 and 415, so the current generation has no off-Mac copy. |
| F-05 | Retrieval parity | Needs attention | r209 against r212, described above. |
| F-06 | Skill links | Partly not rechecked | `beastmode-capture` is readable. `photo-index` could not be checked because FieldData isn't mounted. This is a result of F-01, not a separate fault. |

Verified now:
- **Local backup.** The generation 418 file's hash matches its recorded value, and it covers the current generation. It was written at 02:00Z, about 8 hours ago.
- **Ingest.** The last ingest job finished at 07:30Z.
- **Notes root.** `/Users/priya/Notes` is mounted.

#### What this check could not see

- **Budget, backup, bridge and jobs from the gateway.** All came back null. Null means unavailable to this check, not healthy. I took those areas from your local export instead.
- **"Zero visible findings."** That is a common-contract view and says nothing about your private hub.
- **Key recovery.** Not rechecked. No key escrow evidence was supplied.
- **Monthly usage and infrastructure reserve.** Not rechecked, because the budget field was null. I have no ledger or provider billing figures.
- **Local service against remote gateway.** The gateway answered a read. The local service was not probed live, so its current state is known only from the 08:10Z export.

#### Next actions, in order

1. Mount `/Volumes/FieldData` on the Mac, then look for a new bridge heartbeat. It should be under 15 minutes old with `survey-photos` ok. (F-01, F-06)
2. Read the log for the 2 Nov `maintenance-cycle` failure and rerun the cycle once the source is mounted. Rerunning is a repair, so tell me if you want me to do it. (F-02)
3. After that, fetch "Site visit 3 Nov" again and compare it with the contract revision. It should return r212 or later. (F-05)
4. Let the nightly run copy generation 418 to the off-Mac volume. Check for a `*-418-*.enc` file in `/Volumes/OffsiteVault/hub-backups` tomorrow. (F-04)
5. Schedule a fresh isolated restore of the current generation. A restore changes state, so I haven't started one. (F-03)

If you reopen this later, findings F-01 to F-06 keep these IDs. A narrower check will leave the others marked not rechecked. I'll mark one resolved only after passing evidence.

#### Files

No files were produced. The only artefact is this report.
