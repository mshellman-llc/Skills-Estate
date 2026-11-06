---
skill: plan-offering-artifacts
title: Build order and blockers for a half-finished assessment playbook
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 472ad5c6e512f9f142aacbdcf26cef02e30bc9d93bd5bea308092d502715e240
---

## Request

We're building the playbook for our Data Platform Readiness Assessment (PB-DPR) and I've got a half-finished folder. Can you work out what's left to build, in what order, and what's blocking it? Folder listing and my quote notes are attached.

## Inputs

Run of the built `manage-service-offering` task package in its "offering package planning" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `manifest.draft.json`, `plan.txt`.

#### folder-listing.txt

Folder: PB-DPR Data Platform Readiness Assessment
Listing taken 2026-11-03. No manifest.json in the folder.

PB-DPR_01_readme.md            started, headings only
PB-DPR_02_overview.docx        finished; parity gate passed, visual gate passed, prose gate not run
PB-DPR_03_one-pager.pdf        exported last week; no gates run
PB-DPR_05_qualifier.docx       draft, three questions still marked TODO
(no qualifier.json yet)

Nothing else exists. No talk track, no stage gate workbook, no DDOC, no proposals, no SOWs, no ROM decks.

#### quote-notes.md

#### PB-DPR quote notes (Priya's working notes)

Shape: Assess. Stage: build.

We sell two options.

- **Core**: four-week readiness assessment of one data platform. Quote Q-4471. Active timeline snapshot TS-0912. Modelled margin 41%.
- **Extended**: Core plus a second platform and a migration sequencing workshop. No quote number yet. No timeline snapshot yet. Margin not modelled.

Fee bands are not final. The practice lead recorded a band spread of 2.6 between the Core and Extended bands.

Margin floor: Finance mentioned in a hallway chat that the floor is 35%. I have nothing in writing and no date.

The playbook spec we work to is version 1.2. I do not have the spec document, the manifest schema, the qualifier schema or the stage-gate workbook to hand. They live with the PMO.

Open question from the sales team: should the Extended proposal and SOW wait until the Core ones are signed off? I have not decided.

## Output

PB-DPR has 13 artifacts required and none are complete. 3 are ready to start now, 10 are waiting on earlier artifacts, and nothing can be called release-ready yet.

I ran the planner's rules by hand against your folder listing and notes, because I can't run `plan.py` here. I also had to draft a `manifest.json`, since the folder has none.

#### Gaps in what I was given

- **No specification inputs.** I don't have the approved spec, the manifest schema, the qualifier schema or the stage-gate workbook. You said they sit with the PMO. I could not validate the draft manifest, so treat this as a labeled diagnostic plan and not a conformance result.
- **Spec version mismatch.** You work to version 1.2. The planner models version 1.1, and a changed version string does not make it apply 1.2's rules. The artifact set below may differ under 1.2, and the PMO needs to confirm it before anything is built.
- **No verified margin floor.** The 35% from Finance is a hallway remark with no source and no date, so I left it out of the manifest. Core's 41% margin has nothing to be compared against.

#### Findings

1. No verified margin floor, so commercial approval is unresolved.
2. Extended has no Q-number.
3. Extended has no active timeline snapshot, so its revenue, cost and margin are unsourced.
4. The manifest declares spec 1.2 and the planner is on 1.1.

Core has Q-4471 and snapshot TS-0912, which are your figures.

#### Which artifacts are required

- Shape Assess carries the full suite.
- A band spread of 2.6 is above 2, so the ROM deck (06) is planned for each option. I took your "2.6" to be the number the planner expects. Please confirm that is how the spread is defined.
- That gives 7 playbook-level artifacts (01 to 05, 07, 09) plus 06, 08 and 10 for each of Core and Extended, which makes 13.

#### Plan, in order

| Artifact | Action | Blocked by | Route |
|---|---|---|---|
| 02 Overview | run the gates | none | `manage-service-offering`, offering package planning |
| 05 Qualifier | finish and gate | 02 | `manage-service-offering`, offering package planning |
| 03 One-pager | run the gates | 02 | `manage-service-offering`, internal brief or external handout |
| 04 Talk Track and Objections | build | 02 | `manage-service-offering`, offering package planning |
| 09 Pre-Engagement Stage Gate | build | none | copy the template and adapt the rows |
| 06 ROM deck (Core, Extended) | build | 02 | `build-deck` with a `scope-project` rough estimate |
| 07 DDOC | build | 02, 05 | `build-deck`, scope decision deck |
| 08 Proposal (Core, Extended) | build | 07 | `build-deck` |
| 10 SOW (Core, Extended) | build | 07 | `write-statement-of-work` |
| 01 README | finish and gate | none | this skill, from the manifest |

**Ready now:** 02, 09 and 01.

The next step is the 02 Overview prose gate. The Overview is the dependency for six other artifacts, so that gate is the one holding up the rest. It is the only gate left on that file. Parity and visual have passed, and prose has not run. Once 02 passes, 05, 03, 04 and 06 are all unblocked. 05 then unblocks 07, and 07 unblocks the proposals and SOWs.

Other points:
- **03 One-pager** was exported before 02 passed its gates. If the prose gate changes the Overview, it will need a re-check.
- **05 Qualifier** needs its three TODO questions closed. It also needs a regenerated `qualifier.json`, validated against the supplied qualifier schema, which does not exist yet.
- **06 ROM** is a conditional slot. The 2.6 spread plans it, and the ROM figures come from a rough estimate. Extended has no quote number or snapshot, so that estimate has nothing to rest on until they exist.
- **07 DDOC** runs in decision mode, because there are two options.

#### Decisions to lock

1. **Margin floor.** Someone needs to supply the percentage with its source and verification date. Until then no option can be checked against a floor.
2. **Extended's Q-number and timeline snapshot.** Both are needed before 06, 08 and 10 for Extended carry any figure. No fee bands are final, and I have not filled in any.
3. **Spec version.** The PMO needs to supply the approved spec and schemas, and confirm whether 1.2 changes the artifact set.
4. **Band spread definition.** Confirm that 2.6 is the figure the spec means.
5. **Your sales team's question.** Should the Extended proposal and SOW wait for Core sign-off? I did not pick an answer. The plan has no dependency between them today, so both are blocked only by 07.

#### Not done

I did not run any gates, because I only have a file listing and not the documents. I did not mark anything complete or update gate results. I did not write the missing artifacts, since 04, 06, 07, 08 and 10 are blocked on an earlier artifact or the open decisions above.

#### Files

- `out/manifest.draft.json`: the draft manifest. It holds code PB-DPR, shape Assess, stage build, spec_version "1.2" and band_spread 2.6. The margin floor is null with no source or date. Core has Q-4471, TS-0912 and 41%, and Extended is empty. Four artifacts are listed: 01 draft, 02 present with parity and visual passed, 03 present with no gates, and 05 draft.
- `out/plan.txt`: the hand-run plan above in the planner's text format, with the findings.
