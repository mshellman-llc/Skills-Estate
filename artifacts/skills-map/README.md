# Skills Estate map

[Open the private Skills Estate site](https://megan-skills-estate.livelaughcod-8893.chatgpt.site).

Browse the workflows by work group, sort their names, and copy links to the matching GitHub groups. The site opens directly in a browser.

Each overview explains the task and when to use it. It lists what to provide and what the skill produces, followed by an example request. Filter by intended audience or required setup. [The reuse review](../../browse/reuse-review.md) separates general-use methods from Megan-specific workflows and lists personal references that need attention before sharing.

The catalog distinguishes primary task packages, their included modes, and supporting modules. Its [maintenance review](../../docs/skill-maintenance-review.md) identifies consolidation candidates, conflicting older guidance, and capabilities to preserve before retirement.

The readable instructions omit managed policy blocks, source comments outside code, the repeated title, and the generic build-card preamble. Connection excerpts and print views use the same cleaned text. Exact Markdown remains in Source and files and in downloaded packages. Rendering never executes source HTML.

## Maintain the reader guides

`config/skill-guide.json` holds the reader-facing summaries and the reviewed entrypoint hashes. Review a guide against its source after changing the entrypoint. An unmatched hash makes the map show current source excerpts and a review notice instead of the old guide. Keep the full instructions and downloads unchanged when editing a summary.

`tools/skill_guide.py` scans workflow text, supporting files, declared runtime dependencies, and shared policies for named personal references. It separates examples and tests from workflow text. The audience classification describes intended use; it does not certify that a package works in another environment. The sharing review also identifies shared policy wording copied into every assembled package.

Regenerate the GitHub review with `python3 tools/skill_guide.py --report`. Source or policy changes require reviewing the findings. Changing the catalog does not install, promote, or generalize the working skills.

## Show examples

Each skill's Examples tab shows recorded runs from [`showcase/`](../../showcase/README.md): the request, the inputs and the output the skill produced. Fictional and redacted real examples carry different labels. An example recorded against an older SKILL.md stays visible with a "From an older version" label. The "With examples" filter and the example count on each card show which skills have them. Examples never enter a plugin or task package.

## Refresh the site

Ask Codex to refresh the Skills Estate site from GitHub. The refresh must retrieve a passing build for current main, verify the workflow and group data, update the existing Site, and confirm the deployed GitHub revision.

Site identity: `appgprj_6ae246ca64f88191af4dfb318b704b65`. Preserve its owner-private audience. Read the Site source README and `.openai/hosting.json` before updating it. Reuse this identity rather than creating another Site. The local checkout is `/Volumes/BeastMode/Codex/skills/work/sales-process-and-skills-map/site/`.

GitHub main at `mshellman-llc/Skills-Estate` remains the source of truth. The Site is a published snapshot refreshed on request. GitHub Actions rebuilds the downloadable map and group collections on every main update.

## Share a group

[Browse the groups on GitHub](../../browse/README.md). Each group has a link and a collection of complete task packages. Download `skill-collections` from the [latest successful main workflow](https://github.com/mshellman-llc/Skills-Estate/actions/workflows/verify.yml). Repository access is required for GitHub links.

## Maintain the groups

`config/skill-groups.json` is the shared source for the map and GitHub browse pages. Each source workflow has one group. Optional local skills are declared separately. `config/skill-catalog.json` continues to control task packaging and merged modes.

After adding or moving a workflow between groups, run:

```sh
python3 tools/browse.py
python3 artifacts/skills-map/build.py --base PUBLISHED_COMMIT
```

Commit the group configuration and generated browse pages with the source change. CI rejects missing or duplicate group assignments and stale browse pages. The workflow rebuilds the map before testing and uploading it on every main update. It also supports manual runs.

## Source and build

The builder requires an explicit published base commit reachable from `--published-ref` (default `refs/remotes/origin/main`). Fetch that ref before building locally. For branch previews, compare with the published main baseline; local changes remain labeled. The builder does no network work.

```sh
git fetch origin main
python3 artifacts/skills-map/build.py --base PUBLISHED_COMMIT
python3 tools/browse.py --check
python3 tools/estate.py validate
python3 -m unittest discover -s tests -v
python3 tools/estate.py sync
python3 tools/browse.py --bundle
```

`sync` refreshes candidate build and package ZIPs. The group bundler uses those complete task ZIPs, including their existing dependencies and modes. Collection manifests record the source hash and ZIP hashes. Package readiness follows the current catalog and release gates.

Each mapped workflow retains its exact entrypoint Markdown and hash. Connections quote literal skill-name references from those instructions. Supporting files are inventoried; their contents remain in the skill packages. Families and suggested routes support navigation; the instructions determine which workflow applies.

The map keeps the navy, teal and sand colors and uses the reader's system font. The default view shows search, the family list and a short legend. Secondary filters and the sharing review sit under "More filters and sharing details". The GitHub status and group links are in the footer. The artifact-specific design leaves the global brand policy unchanged.

The claude.ai artifact viewer cannot save files, so the copy published there is built without download buttons or download code:

```bash
python3 artifacts/skills-map/build.py --base origin/main --no-downloads --output <scratch path>/skills-map.html
```

The default build, which the local viewer and the hosted site use, keeps the "Download SKILL.md" and "Download skill packages" buttons. The template marks those parts with `<!--downloads-->` and `/*downloads*/` comments.

## Verify updates

`tests/test_map_updates.py` checks whether an artifact matches current main. It rejects stale or expired artifacts and changed data, and covers interrupted updates and localhost request checks. `tests/test_skill_groups.py` verifies complete group assignment and package-mode links. Browser checks open every readable view and verify exact source downloads. They exercise filters, keyboard behavior and complete package downloads. They also inspect narrow screens and print output.

The local viewer binds only to loopback. Update requests require the same origin and a per-run token. GitHub authentication remains in `gh`; no credentials are embedded in the HTML.

## Download task packages

The hosted map downloads the complete task ZIPs for the filtered workflows. Shared runtime modules travel inside their owning tasks; workflows without a catalog task package are listed in the download notes. Each package is checked against the release manifest from the same successful GitHub run as the map. The outer ZIP includes installation notes, the selected workflow inventory, and package hashes. Downloading candidates does not install or promote them.
