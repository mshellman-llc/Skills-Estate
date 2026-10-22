# Interactive Skills Estate map

Open `index.html` in a browser. The file works offline and contains the canonical skill snapshot, searchable families, suggested workflows, source instructions, connections, and package-file inventories.

The checked-in map is generated from repository sources. A personal snapshot can also include a local authoring checkout and explicitly selected additional skill folders. Local revisions and additions remain labeled; building the map does not install, publish, or change a skill.

## Rebuild

Python 3.9 or later, with no third-party dependencies:

```sh
python3 artifacts/skills-map/build.py
```

The default baseline is the checkout's current Git commit. The output includes `index.html` and `index.json`. Rebuild after source changes; an existing map does not refresh itself.

To create a personal snapshot without overwriting the canonical artifact:

```sh
python3 artifacts/skills-map/build.py \
  --repo /path/to/local-authoring-checkout \
  --baseline-repo /path/to/verified-checkout \
  --base VERIFIED_COMMIT \
  --extra /path/to/local-skill \
  --output /path/to/personal-skills-map.html
```

Repeat `--extra` for each additional skill. The builder refuses duplicate names, missing frontmatter, and skills without an explicit family assignment. `--baseline-repo` lets the comparison use a verified commit without fetching into or modifying a dirty authoring checkout.

## Source model

- Each package retains its exact entrypoint Markdown and SHA-256. The readable view supports the Markdown constructs used here; the exact source is also available for inspection and download.
- The initial excerpt uses the first three body blocks after the title, excluding shared-policy routing, subheadings, code blocks, and tables. It is an excerpt, not a replacement for the complete instructions.
- Connections are literal references to mapped skills found in an entrypoint. Single-word names require an explicit code span, link label, or skill reference to avoid mistaking ordinary words for skill names. The surrounding source paragraph is included. A mention is not automatically a dependency or an execution trace.
- Package status compares every included file with its Git blob at the selected baseline. Hidden files, Python caches, and bytecode are excluded. A supporting-file change can produce a local revision even when SKILL.md matches.
- Supporting files are inventoried and hashed, not embedded. Private project records, installed-runtime discovery, external connectors, and account publication are not inspected by the map builder.
- Families and routes are editorial navigation aids. Current source instructions govern invocation, prerequisites, sequence, and authorization.

## Continuity with the prior artifact

The September 1 architecture map supplied the interaction model. This edition preserves search, skill families, detailed purpose and trigger descriptions, execution instructions, relationships, source references, and file inventories. The neutral estate policy replaces the historical company styling.

Subjective quality and cost ratings were deliberately omitted because no current benchmark supports them. Historical platform connector assertions and role tiers were not copied. Source status and the checks written in each skill replace those assumptions. Outputs, required inputs, failure paths, and constraints remain in the complete instructions rather than being forced into fields that some entrypoints do not define.

## Verification

Run the repository checks and the map's source integrity tests:

```sh
python3 tools/estate.py validate
python3 -m unittest discover -s tests -v
python3 tools/estate.py build
```

Browser verification uses Playwright supplied by the local workspace runtime and an isolated headless Chrome session. Set PLAYWRIGHT_CHANNEL to select a different installed channel. `verify.cjs` accepts the artifact HTML path and a directory for screenshots, its report, and a print PDF:

```sh
NODE_PATH=/path/to/node_modules node artifacts/skills-map/verify.cjs /path/to/index.html /path/to/qa
```

Inspect the rendered desktop, narrow-screen, detail, and print views. Automated interaction tests do not establish the quality of a skill's workflow or prove it ran successfully.
