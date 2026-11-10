# Skills Estate map

[Open the current Skills Estate site](https://megan-skills-estate.livelaughcod-8893.chatgpt.site).

Browse the workflows by work group, sort their names, and copy links to the matching GitHub groups. The site opens directly in a browser.

Each overview explains the task and when to use it. It lists what to provide and what the skill produces, followed by an example request. Open the setup and sharing details when needed. [The reuse review](../../browse/reuse-review.md) separates general-use methods from workflows that need personal context and lists personal references that need attention before sharing.

The catalog distinguishes primary task packages, their included modes, and supporting modules. The [naming convention](../../policies/naming.md) defines identifiers for public workflows and supporting modules.

The readable instructions omit managed policy blocks, source comments outside code, the repeated title, and the generic build-card preamble. Connection excerpts and print views use the same cleaned text. Exact Markdown remains in Source and files and in downloaded packages. Rendering never executes source HTML.


## Portable owner kit and website exports

Download **skills-estate-portable** from a successful main [verification run](https://github.com/mshellman-llc/Skills-Estate/actions/workflows/verify.yml). It contains three ZIPs:

- `skills-estate-owner.zip`: the complete local catalog, show/hide manager and launcher. Unzip, then open `open-map.command` on macOS or run `python3 viewer.py --settings visibility.json --open`. Python 3.10 or later is required. Initial refresh uses an authenticated GitHub CLI; if unavailable, the existing snapshot remains usable.
- `skills-estate-estate.zip`: the selected Skills Estate website, with its reusable component and export manifest.
- `skills-estate-portfolio.zip`: the independently selected portfolio website. Its initial selection is empty; no portfolio content is published by assumption.

In the owner kit, choose **Manage content**. Set visibility separately for Skills Estate and Portfolio. Filter by content type or work group, select rows for bulk actions, and set downloads, featured placement and order for each destination. Preview checks the current draft; save persists choices locally with revision protection and a previous-save restore. Export produces a new filtered website ZIP. The public exports omit the owner manager, settings and excluded records.

The [portfolio integration guide](INTEGRATION.md) includes a working HTML component example and the boundary for future Railway/Supabase integration. No portfolio framework or hosting account is created by this project.

From a checkout, build the portable artifacts after rebuilding the map:

```sh
python3 artifacts/skills-map/package_portable.py --output .local/portable
```

Add `--packages dist` only when the built release's source commit matches the catalog baseline. Actions does this on main after building task packages. Exports reject mismatched revisions and package hashes; without matching packages, task ZIP controls are omitted. Individual Markdown downloads and published plugin links follow their own per-item controls. There is no CSV export.

The show/hide configuration is `config/skills-publication.json`. It controls website presentation and does not change installed plugins or task dependencies. Salesforce development, career, and personal skills remain separate installable plugins. Newly discovered IDs default to hidden, and a workflow with a hidden required skill is omitted with a report in the owner preview. Website settings are excluded from the plugin version fingerprint and runtime packages.

## Maintain the reader guides

`config/skill-guide.json` holds the reader-facing summaries and the reviewed entrypoint hashes. Review a guide against its source after changing the entrypoint. An unmatched hash makes the map show current source excerpts and a review notice instead of the old guide. Keep the full instructions and downloads unchanged when editing a summary.

`tools/skill_guide.py` scans workflow text, supporting files, declared runtime dependencies, and shared policies for named personal references. It separates examples and tests from workflow text. The audience classification describes intended use; it does not certify that a package works in another environment. The sharing review also identifies shared policy wording copied into every assembled package.

Regenerate the GitHub review with `python3 tools/skill_guide.py --report`. Source or policy changes require reviewing the findings. Changing the catalog does not install, promote, or generalize the working skills.

## Show examples

Each skill's Examples tab shows recorded runs from [`showcase/`](../../showcase/README.md): the request, the inputs and the output the skill produced. Fictional and redacted real examples carry different labels. An example recorded against an older SKILL.md stays visible with a "From an older version" label. The "With examples" filter finds skills with recorded examples. Examples never enter a plugin or task package.

## Refresh the site

Ask Codex to refresh the Skills Estate site from GitHub. The refresh must retrieve a passing build for current main, verify the workflow and group data, update the existing Site, and confirm the deployed GitHub revision.

Site identity: `appgprj_6ae246ca64f88191af4dfb318b704b65`. Preserve its existing audience and access controls. Read the Site source README and `.openai/hosting.json` before updating it. Reuse this identity rather than creating another Site. Resolve the local checkout through the private workspace configuration.

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

The map uses the Index design: a warm neutral page, charcoal text, rust links and bundled Inter fonts. Skill rows expand in place; the five detail tabs retain the overview, instructions, examples, connections and source files. Status and audience badges are removed. Secondary filters and sharing details remain available on demand. Nineteen suggested workflows cover product research, delivery, Salesforce development, sales, career, writing, creative work and knowledge maintenance. Each gives starting inputs, a request to copy, the reason for each step and the result to expect. These suggested paths are separate from recorded skill examples.

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
