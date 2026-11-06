# Private plugin candidates

`tools/plugins.py` generates Claude and Codex distributions from the existing portable skill build. `config/plugin-bundles.json` owns membership and review status. The eight `agents/*-router.md` files remain the source for the routing method and historical selections. The pursuit configuration adds map-sales-process and review-sales-journey. Career, portfolio and personal project workflows belong to the opt-in `estate-personal` bundle, which has no router.

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
