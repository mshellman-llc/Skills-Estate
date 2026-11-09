# Private plugin candidates

`tools/plugins.py` generates Claude and Codex distributions from the existing portable skill build. `config/plugin-bundles.json` owns membership and review status. The nine `agents/*-router.md` files remain the source for the routing method and historical selections. The pursuit configuration adds map-sales-process and review-sales-journey. Salesforce development belongs to `estate-salesforce`, separate from project delivery. Career, applications and portfolio workflows belong to the opt-in `estate-career`; stickers and game planning belong to the opt-in `estate-personal`. These two optional bundles have no router. Independent product development belongs to `estate-product`. Each plugin is installable on its own and includes its required runtime helpers.

## Separate installation and sharing

Choose `estate-salesforce` for Salesforce development, `estate-career` for applications and portfolio work, or `estate-personal` for stickers and game planning. Each has its own marketplace entry and plugin ZIP on the Plugins (latest) GitHub release. Share the selected plugin ZIP; its required helpers travel with it.

When updating from 0.3.x, install `estate-salesforce` if you previously used the Salesforce skills inside `estate-delivery`, and install `estate-career` if you used career skills inside `estate-personal`. The updated delivery plugin contains project delivery work, and the updated personal plugin contains the creative workflows. Independent product development is in `estate-product`. Updating the repository does not select or install these new plugins in an existing Claude profile.

The current catalog consolidates some historical workflows as modes. A bundle owns each public entry once. A router can still select the complete mode workflow. Cross-bundle routes and controls are copied into that plugin's hidden `runtime/` directory, so resolving them does not depend on another plugin's installation behavior. These resources have `WORKFLOW.md`, not a duplicate discoverable `SKILL.md`.

Build the pilot from the repository root:

```sh
python3 tools/plugins.py --candidate --bundle estate-solutioning --bundle estate-quality
```

Output is under `dist/plugins/claude/` and `dist/plugins/codex/`. Each host directory contains a private marketplace catalog, plugin directories and ZIPs. Each plugin has a portable root manifest plus Claude and Codex compatibility metadata. Claude receives native router agents. Codex receives explicit router skills generated from the same routing selection and method. The authoring workflows remain unchanged.

The build rejects missing classifications, duplicate owners, missing workflows, unresolved runtime dependencies and broken generated router links. It carries the repository's pinned dependency manifests into each package. It does not install Node packages, Python packages or browsers. Artifact execution still needs the documented runtime and must be checked in each host.

Without `--candidate`, packaging refuses any selected workflow, router or shared assembly that lacks accepted review evidence matching its current hash. `release.json` lists the required review hashes. Module reviews cover their source trees; every required dependency needs its own review. The shared review covers policies, assembly tools, configuration and dependency manifests. Review records are input, so only the coordinator may update them after independent acceptance. Changes to reviewed bytes invalidate acceptance.

A candidate is for isolated testing. Each manifest description starts with “Unreviewed candidate for isolated testing.” The marketplace makes candidates available so they can be tested in an isolated profile; availability does not indicate release approval. A candidate has not passed capability, privacy or host acceptance merely because its manifest validates. `estate-release.json` records that distinction inside the package. Review all distributable files before uploading or publishing. No output from this command modifies everyday installations or an account surface.

The current owner marketplace uses `--owner` and records review gaps without enforcing source acceptance. This is distinct from normal reviewed packaging; neither mode proves host execution. Every mode enforces current catalog ownership, retired entrypoints, dependency closure and version/content binding. See [the maintained release workflow](../skills/maintain-skills-estate/references/release-workflow.md) for preparation and update commands.

The manifest and marketplace adapters follow the [OpenAI packaging reference](https://developers.openai.com/plugins/build/plugins) and [Claude manifest reference](https://code.claude.com/docs/en/plugins-reference), inspected on October 22, 2026. Claude's [dependency behavior](https://code.claude.com/docs/en/plugins/dependencies) is host-specific; this pilot includes its routed resources and makes no automatic dependency-install assumption for Codex.
