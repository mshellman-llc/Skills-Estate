---
skill: beastmode-reconcile
title: Reconcile a volunteer onboarding folder and archive verified duplicates
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 70bfeccd296dc9c6f8ee7a290a5b605e1087b1abb0c5bd4794ac969945acc9e4
---

## Request

Compare the Volunteer Onboarding intake folder with our current Operations Handbook and the Pantry Ops shared folder, keep anything unique, and archive the verified duplicates. Hub status and the file inventory are attached.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `beastmode-reconcile` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `volunteer-2026-rows-proposed.csv`.

#### hub-status.md

#### Hub status export, 2026-11-04 (Larkfield Food Bank)

Router: /Hub/_router/router.md (rev 41). Permitted hub: larkfield-ops. `get_context` returned:

- Project: Volunteer programme records cleanup
- Reconciliation record: /Hub/_Reconcile/map/volunteer-2026.csv (rev 7, last row 2026-10-21). Format: source, retained, archive_dest, sha256, class, reason, inverse.
- Rollback mechanism: inverse column in the map, applied by the same operator in reverse row order.
- Named folder: /Hub/Intake/volunteer-onboarding
- Comparison roots (both are sources): /Hub/Operations-Handbook/volunteers (handbook owner: Priya Raman, current to 2026-09) and /Shared/Programs/Pantry-Ops (owner: Tomas Weber)
- Authority questions: which safety briefing is in force; whether the 2023 slides are superseded.
- Authorised action: archive verified duplicates (caller's request, 2026-11-04).

Mounts: /Hub and /Shared both mounted and readable.

Active consumers found by link search:
- /Hub/pages/volunteer-signup.md links to /Hub/Intake/volunteer-onboarding/safety-briefing-v2.pdf
- Scheduled job `roster-sync` (runs 06:00 daily) reads /Hub/Intake/volunteer-onboarding/shift-roster-template.xlsx

Hub note: the hub store is synchronised Markdown; page edits go through version-checked proposals (volunteer-signup.md is at rev 12).

#### inventory.txt

Inventory of /Hub/Intake/volunteer-onboarding with matches in the two comparison roots.
Hashes are full SHA-256, computed 2026-11-04 (earlier hashes for unchanged files reused).

1. welcome-letter.docx
   sha256 a1f3c09e5b7d42816e0a9c3f7d5b2e48a1c6f0937d4e2b85c9a0f1e3d6b7a842
   Handbook: volunteers/welcome-letter.docx  sha256 a1f3c09e5b7d42816e0a9c3f7d5b2e48a1c6f0937d4e2b85c9a0f1e3d6b7a842

2. safety-briefing-v2.pdf
   sha256 7be2d4410c9a5f3e8d16b27a04c93e5f1d8a6b72c0e94f35a7d1b8c2e6f09d13
   Pantry-Ops: safety/safety-briefing-v2.pdf  sha256 7be2d4410c9a5f3e8d16b27a04c93e5f1d8a6b72c0e94f35a7d1b8c2e6f09d13

3. safety-briefing-v3-draft.pdf (modified 2026-06-02)
   sha256 3c90e7a1d5b84f2602e9a7c4b1d3f85e0a62c7941b8d5e3f0a9c6d27e41b8f05
   Handbook: volunteers/safety-briefing-v3.pdf (modified 2026-08-14) sha256 d84a1f6e2b03c95a7e18d4f0b6a2937c5e1f80d3a4b69c27e0f5a8d1b3c7e926
   Text diff: draft has a "Cold storage" section (walk-in freezer entry limit 15 minutes, buddy rule). Final v3 has no such section and gives a 20-minute freezer limit in the "Warehouse" section.

4. shift-roster-template.xlsx
   sha256 59d2b8c7e3a104f6d95b7a2c8e10f4d3a6b9c05e7f21d8a43b6e9c0d5f7a1e38
   Handbook: volunteers/shift-roster-template.xlsx  sha256 59d2b8c7e3a104f6d95b7a2c8e10f4d3a6b9c05e7f21d8a43b6e9c0d5f7a1e38

5. volunteer-faq-notes.md
   sha256 0e6a47b3d9c158f2a4e70b1d63c8f952e7a0d4b1c68f3e95a2d7b0c4f81e6a59
   No match by hash or title in either root. Contains 14 Q&A items written by site lead Imani Okafor, e.g. parking, under-18 sign-in rules, allergen handling.

6. orientation-slides-2023.pptx
   sha256 c47f19e0a6b2d3584e9c1f7a0d62b8e35f4a97c1d0e8b3625a9f7e4c1b08d6a2
   Handbook: volunteers/orientation-slides-2025.pptx  sha256 92b5e8d1f40a7c3695d2e1b8a7f04c63d9e5a1b27c80f4e3d6a95b1c2e7f0384
   Slides differ: 2025 deck replaces the 2023 shift-length table (4 h to 3 h) and drops the volunteer-of-the-month slide.

7. background-check-guide.pdf
   Hash failed: read error (I/O error at byte 1,310,720). No comparison possible.

8. shared-login-recovery-codes.txt
   Recovery material for the shared rota account. Not opened.

## Output

One of the eight files in the Volunteer Onboarding intake folder is ready to archive. Two more are exact duplicates but are in use, so I held them. The rest stay where they are. I prepared the manifest but did not move anything. I have no file-system access here, only your exports.

#### What I checked

- The hub context names the map `/Hub/_Reconcile/map/volunteer-2026.csv` (rev 7). Its inverse column is the rollback, so I used its row format instead of making a new ledger.
- I treated the Operations Handbook `volunteers` folder and the Pantry Ops folder as equal sources. Neither outranks the other by location.
- I used the full SHA-256 values you supplied and did not re-hash anything.
- I searched for consumers of each file. There are two: the signup page and the `roster-sync` job.

#### Disposition

| File | Class | Decision |
|---|---|---|
| `welcome-letter.docx` | Exact duplicate of the handbook copy | **Archive now.** No consumer found. |
| `safety-briefing-v2.pdf` | Exact duplicate of the Pantry Ops copy | **Hold.** `volunteer-signup.md` links to the intake path. |
| `shift-roster-template.xlsx` | Exact duplicate of the handbook copy | **Hold.** `roster-sync` reads the intake path at 06:00 daily. |
| `safety-briefing-v3-draft.pdf` | Divergent from handbook `safety-briefing-v3.pdf` | **Keep.** Open question below. |
| `orientation-slides-2023.pptx` | Divergent from handbook `orientation-slides-2025.pptx` | **Keep.** |
| `volunteer-faq-notes.md` | Unique | **Keep.** No match in either root. |
| `background-check-guide.pdf` | Unresolved | **Keep.** Read error, so coverage is incomplete. |
| `shared-login-recovery-codes.txt` | Excluded | **Not opened, not copied.** |

Matching bytes do not authorise breaking a live route. That is why two exact duplicates are held.

##### Details behind the decisions

- **Safety briefing drafts.** The draft adds a cold-storage section with a 15-minute freezer limit and a buddy rule. The final handbook v3 has no such section and gives a 20-minute limit under "Warehouse". The newer file (the handbook one, dated 2026-08-14) is not automatically the correct fact. Priya Raman owns the handbook, so she needs to say whether the 15-minute rule was dropped on purpose.
- **Which briefing is in force.** The signup page points at v2, and the handbook holds a final v3. I did not choose between them. The link repair below keeps v2 so the page's behaviour does not change.
- **Slides.** The 2025 deck changes the shift-length table from 4 hours to 3 hours and drops the volunteer-of-the-month slide. It looks like a successor, but it is a different version. I kept the 2023 deck until someone confirms.
- **FAQ notes.** Imani Okafor's 14 Q&A items cover parking, under-18 sign-in and allergen handling. I recommend a proposal to merge them into the handbook, with Imani credited. I did not draft one.

#### Manifest

Saved as `out/volunteer-2026-rows-proposed.csv`, using the map columns: source, retained, archive_dest, sha256, class, reason, inverse. The rows that would move go to `/Hub/_Reconcile/archive/2026-11-04/volunteer-onboarding/`.

Row for the one file ready to archive:

```
source:   /Hub/Intake/volunteer-onboarding/welcome-letter.docx
retained: /Hub/Operations-Handbook/volunteers/welcome-letter.docx
dest:     /Hub/_Reconcile/archive/2026-11-04/volunteer-onboarding/welcome-letter.docx
sha256:   a1f3c09e5b7d42816e0a9c3f7d5b2e48a1c6f0937d4e2b85c9a0f1e3d6b7a842
inverse:  move dest back to source
```

Before the move, the operator should re-hash source and retained copy and confirm the destination is empty. The move stays within the same hub volume, so staged copy-and-verify is not needed. Afterwards, confirm the archived file's hash, and confirm the handbook copy is still intact.

Moving single files leaves the folder in place, since it still holds unique and divergent material.

#### Status

**Changed now:** nothing on disk. The manifest rows are prepared locally.

**Verified:** the three duplicate hash matches (from your export), the two consumers, and the content differences for the two divergent pairs.

**Still unchanged:** all eight files, the signup page, the `roster-sync` job, and the hub map (still rev 7).

**Not verified:** the hub ingestion of any change, because none has been made.

#### Next actions

1. Run the `welcome-letter.docx` move per the manifest, then append the row to the map.
2. Submit a version-checked proposal against `volunteer-signup.md` rev 12 that repoints the safety-briefing link to `/Shared/Programs/Pantry-Ops/safety/safety-briefing-v2.pdf`. I could not submit it from here. Once it is accepted and the page is retrieved with the new link, archive `safety-briefing-v2.pdf`.
3. Ask Tomas Weber or whoever manages `roster-sync` to repoint it to the handbook roster template. Archive the intake copy after one successful 06:00 run. The job must be configured by its owner. I changed nothing.
4. Ask Priya Raman about the 15-minute freezer rule and whether v2 or v3 should be linked from signup.
5. Re-run the hash on `background-check-guide.pdf` after checking the disk or restoring the file from backup. A read error does not count as a duplicate or a successful archive.

#### Files

- `out/volunteer-2026-rows-proposed.csv`: eight rows, one per file in the folder. Three are classed as exact duplicates (one ready, two held), two divergent, one unique, one unresolved, one excluded.
