# Skills map verification

## GitHub updates and groups: October 28, 2026

The map compares all 79 source workflows against published main commit `a9424d7e1635832e4a60b5d1037e03324a75bd04`. The eight groups in `config/skill-groups.json` generate both the map and GitHub browse pages. All 53 task packages appear in the collections. Cross-group modes include their complete parent package.

All 305 repository tests passed in 54.100 seconds using the declared Python dependencies and installed browser renderer. Source validation, candidate build, package ZIPs, and all eight collection archives passed. Nested package hashes were checked against the release manifest. The design checker reported zero findings.

Browser checks opened all 79 instruction views. Additional checks covered descending sort, empty/reset, the selected GitHub group URL, link-copy feedback, updated task invocations, and supporting workflows. The 390px layout fit without page overflow. The navy, teal, sand, and embedded Plus Jakarta Sans styling was retained.

Updater tests cover exact-main workflow selection, expired and stale downloads, HTML/JSON agreement, skill hashes, GitHub changing during download, and same-origin localhost requests. The local viewer keeps its previous HTML when those checks fail. Live download verification is recorded after the main build completes.

These changes affect browsing and map downloads. Skill instructions, task consolidation, plugin routing, package acceptance gates, and installed releases are unchanged.

## Previous candidate: October 23, 2026

The restored candidate has 78 source modules and 52 standalone entrypoints. The generated map was refreshed after the map-journey and JTBD restoration and the current writing-policy merge. Validation, standalone packaging and the solutioning/quality plugin candidate build passed with source hash `a19d7ce5933fca9dde1d35924fa8bf9f89760da46a529980b9b45ea3c1eba97d`.

The repository suite reported 251 passing tests in 58.172 seconds at source commit `14f160323215bd7f489fb75be413f97f277b881e`. Private coordination records retain the logs and fixtures. A follow-up receipt binds verification to the exact candidate commit and tracked tree. This documentation update does not establish a new whole-map visual or prose review.

Plugin packages remain candidates. Whole-skill capability review, fresh native-host execution and account distribution are pending.

## Historical verification: October 22, 2026

The following observations describe baseline `e0d71e32db970e6b7fcc31d4c06a9130df8333da`. They do not establish the current candidate's inventory or current rendered output.

## Source and behavior

- The checked-in snapshot contains all 74 canonical packages, once each. All entrypoint bytes and supporting-file hashes match the source checkout.
- A separate personal snapshot contains those 74 skills and four explicitly selected local additions. It retains 78 exact entrypoints and distinguishes matching packages, local revisions, and local additions. Personal source changes are not imported into this branch.
- Both the 74-skill canonical map and the 78-skill personal map passed browser checks for every detail view, search, combined filters, empty-state recovery, CSV export, keyboard activation, dialog focus, arrow-key tab navigation, connections, workflow links, and mobile overflow.
- The offline browser checks recorded no external requests and no JavaScript errors.
- Repository validation and build passed. All 22 repository tests passed, including six map tests for complete coverage, byte preservation, embedded-data parity, source-backed connections, safe Markdown rendering, and tables/code.

## Visual and content review

Desktop, 390px mobile, detail-dialog, workflow, and print views were rendered and inspected. The map uses the estate's confirmed neutral palette and system fonts from `policies/brand.md`.

The Editorial design checker uses a different default palette. Its palette findings are resolved by the explicit estate policy; the artifact's actual tokens were compared with that policy. Border and alignment findings were corrected. Neutral identity scanning passed.

The parity audit reported no lexical or structural errors. Its hidden-content warning refers to the inactive workflow view, which becomes visible through the tested view control. Its visual-review warning is addressed by the rendered inspections above.

New interface and maintenance prose passed the prose checker. Findings in the rendered catalog include verbatim source descriptions, repeated skill/family names in navigation, and source terminology. Those strings were retained to preserve the source meaning. The snapshot footer was rewritten as a complete sentence.

## Limits

This is a skill reference, not an installation audit or a runtime benchmark. Supporting files are inventoried but not embedded. External project records and connector availability are not verified. Families and suggested routes are authored navigation aids; source instructions govern each workflow. The map is a dated snapshot and must be rebuilt after source changes.
