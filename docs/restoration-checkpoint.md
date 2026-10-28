# Restoration checkpoint — 28 October 2026

This change brings the restored Skills Estate source into the private canonical repository. It contains 79 source modules, 53 task entrypoints, six domain routers, and the optional additional-skills bundle. The source is a restoration candidate; package release acceptance remains pending in `config/plugin-bundles.json`.

The restoration preserves the implementation resources and offline helpers recovered through commit `2aa15f82987435e9422147bc30eeee39c916218e`. The newer sticker-art-direction skill is included with its typography and production references. Its workflow is retained; the shared writing directive is added to match the other entrypoints. Its bundle membership is opt-in.

Validation, the standalone build, plugin packaging, and all 274 local unittest executions passed against the integrated source. Six test executions repeat deck cases through the existing discovery structure. These checks cover packaging, dependency closure, installation safeguards, artifact behavior, and the tested refusal paths. They do not establish capability parity or successful native execution for every skill.

The inventory map now includes the added skill. The writing-runtime test checks every discovered entrypoint without fixing the inventory to a historical count. Shared writing requirements remain enforced for each entrypoint.

Claude reviewed the sticker source and its classification. The requested catalog correction is included. Earlier scoped reviews cover the shared prose extraction and bundled quality-gate repairs. Raw run evidence and recovery archives remain outside the distributable source.

## Remaining acceptance work

Codex coordinates the remaining queue; Claude reviews material Codex changes. Each module and router still needs a recorded capability disposition before package release. The existing candidate status must not be promoted from file counts or passing infrastructure tests alone.

Fresh explicit native cases, complete rendered-output reviews, all-skill discovery and invocation, and everyday installation verification are separate evidence states. ChatGPT personal, Codex personal, Claude account, and Cowork distribution require supported private destinations and execution evidence. Repository publication does not establish any of those account installations.

Salesforce live acceptance remains pending because no disposable test organization was supplied. Offline preparation and explicit-target refusal behavior remain available.

## Recovery

The coordinator preserved the prior canonical checkout, including its uncommitted source, before integration. Recovery archives are private local working records. Git history retains the pre-restoration main commit `5b44e8caf5cb79efaa512ec84fc6060958c98684`. Revert the integration commit to undo the repository change; use the local installer restoration record to reverse an installation separately. Do not overwrite unrelated or platform-managed skills.
