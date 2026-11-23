# Skills Estate site

`build.py` builds the Skills Estate website as one self-contained `index.html` in the LiveLaughCode brand. It reads the catalog from `artifacts/skills-map/index.json` and `artifacts/skills-map/workflows.json`, and it applies `config/skills-publication.json` when given `--target`.

```sh
python3 artifacts/skills-site/build.py --target estate --out .local/skills-site/index.html
```

The builder stops with a catalog drift error when `index.json` and the `skills/` folder list different skills. Rebuild the map first in that case.

## What the page shows

The page opens on an overview of the families. Its Skills, Workflows and Plugins pages each have a search field and filters. The fact cards above each list filter it by kind of skill, scoped to the open family. Opening a row shows its command, example request and connections directly beneath it. Pages link as `#skill-<id>`, `#workflow-<id>`, `#plugin-<id>` and `#family-<id>`, and older `#skill-` and `#workflow-` links still open.

## Files

- `app.js` mounts the page from the LiveLaughCode components in `vendor/bundle.js`.
- `page.css` lays those components out using design-system tokens.
- `icons.json` holds the sidebar and family icons, copied from the design system's Icons group, and which icon goes with which family.
- `vendor/` holds the design system's stylesheets and script, the Instrument Sans fonts with their license, and React 18 with its license.

The Engrace font for the wordmark is licensed for web embedding and is not committed. CI writes it from the `LLC_ENGRACE_WOFF2_BASE64` repository secret before building. A local build uses `vendor/Engrace-ItalicVF.woff2` when that file is present; without it the wordmark falls back to an installed Engrace.

## Publishing

On every main update, CI uploads the built page as the `skills-estate-site` artifact. Publishing the Site replaces its page with that file. The Site keeps its identity, audience and access controls.
