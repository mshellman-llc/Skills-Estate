# Skills map verification

Verified October 22, 2026 against the canonical baseline `e0d71e32db970e6b7fcc31d4c06a9130df8333da`.

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
