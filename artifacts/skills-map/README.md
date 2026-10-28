# Skills Estate map

Open `open-map.command` to browse the map with GitHub updates enabled. The launcher uses Python 3 and your existing GitHub CLI login. Keep `viewer.py`, `index.html`, and `index.json` beside it. Opening `index.html` directly still works as an offline reference.

The viewer checks GitHub when it starts. Use **Update from GitHub** to refresh it while it is open. The status line shows the source commit and build date. If GitHub is still building the latest main commit, the viewer retains the saved version and explains when to retry.

[Browse the same groups on GitHub](../../browse/README.md). Each group has a shareable page and a collection of its complete task packages. Name sorting, group links, and filtered CSV export are available in the map.

## Get the current map and collections

Open the latest successful main run of [Verify skills estate](https://github.com/mshellman-llc/Skills-Estate/actions/workflows/verify.yml). Download `skills-estate-map` for the map and launcher, or `skill-collections` for the eight group ZIPs. Repository access is required.

The viewer downloads only a successful workflow artifact for the current GitHub main commit. It checks the embedded map data and skill hashes before replacing the local HTML and JSON. It does not update skill installations. If an artifact has expired, run the workflow again on main.

From a terminal, the equivalent commands are:

```sh
python3 artifacts/skills-map/viewer.py --open
python3 artifacts/skills-map/viewer.py --once --output /path/to/skills-estate-map.html
```

The first command keeps the local viewer running until you close its terminal. The second updates one saved copy and exits.

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

The map retains the navy, teal, sand, and embedded Plus Jakarta Sans design of the current artifact. The fonts' SIL Open Font License is included. The artifact-specific design leaves the global brand policy unchanged.

## Verify updates

`tests/test_map_updates.py` covers current-head selection, stale and expired artifacts, changed data, interrupted update eligibility, and localhost request checks. `tests/test_skill_groups.py` covers complete group assignment and package-mode links. Browser checks cover sorting, group-link copying, search, details, updates, and narrow screens.

The local viewer binds only to loopback. Update requests require the same origin and a per-run token. GitHub authentication remains in `gh`; no credentials are embedded in the HTML.
