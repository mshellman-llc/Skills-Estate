# Add Skills Estate to a future portfolio

No portfolio application or framework is required by this package. The portfolio export is a static website and a reusable browser component. The existing Skills Estate repository remains the skill source.

## Select what appears

Run the local owner kit, open **Manage content**, and check the **Portfolio** column for the skills, workflow examples and installable plugins to include. The **Skills Estate** column is independent. The target selector controls downloads, featured placement and order for the selected destination. Bulk actions apply to selected rows; search and category filters help select a group.

Save choices, then export the portfolio website. Preview uses the current draft, including unsaved changes. New content starts hidden until explicitly selected. A workflow is omitted if a required skill is hidden; the manager reports the missing skills. Existing choices survive catalog refreshes because they live in a separate file.

The repository stores these choices in `config/skills-publication.json`. The downloaded owner kit stores them beside the launcher in `visibility.json`. Save writes that local file. It does not commit to GitHub or deploy a website. Download choices to move them between checkouts; import does not save until **Save choices** is pressed. A revision check rejects stale saves, and **Restore previous save** reverses the last successful save.

## Use a complete page

Unzip the portfolio website into the future application's public assets, for example `public/skills/`. Its `index.html` works as an independent page at `/skills/`. Keep the directory structure, including fonts, catalog and any included downloads. No database, build step or secret is needed to serve this export.

## Embed the explorer inside a page

Serve these files over HTTP from the future site. The export includes a working `integration-example.html`.

```html
<script type="module" src="/skills/skills-estate.js"></script>
<skills-estate-explorer catalog-src="/skills/catalog.json"></skills-estate-explorer>
```

The component uses Shadow DOM to keep its CSS from changing the host page. The catalog contains only the selected destination's records. Links to exact-source task packages resolve relative to the catalog; set `downloads-base-url` when hosting downloads elsewhere. Fonts and the component stylesheet resolve relative to the JavaScript module.

A framework can mount the same explorer directly and supply its own route handling:

```js
import { mountSkillsEstate } from '/skills/skills-estate.js';

const response = await fetch('/skills/catalog.json');
if (!response.ok) throw new Error('Skills could not be loaded');
const data = await response.json();
const view = mountSkillsEstate(document.querySelector('#skills'), {
  data,
  downloadBase: new URL('/skills/', location.origin).href,
  initialSkill: new URLSearchParams(location.hash.slice(1)).get('skill'),
  onSelect(id) {
    history.replaceState(null, '', id ? '#skill=' + encodeURIComponent(id) : location.pathname);
  }
});
// Call view.destroy() when the host page unmounts the explorer.
```

The custom element emits a bubbling `skill-select` event with `event.detail.id`; collapsing emits `null`. The mount function also returns `openSkill(id)` and `closeSkill()`. The host owns its URL and navigation. Two mounted explorers keep independent search and selection state.

## Railway and Supabase later

Railway can serve the future application and these exported assets. Supabase becomes useful if you want to change visibility from an authenticated editor on the deployed portfolio. That editor does not exist in this portable kit.

To add it, retain stable content IDs and the two independent destination selections. Store visibility, download permission, featured placement and order in owner-editable records. Use authenticated, owner-restricted database policies for writes. Generate or serve a filtered public catalog on the server; a hidden CSS class is insufficient. Preserve revision checks so two windows cannot overwrite each other's choices. Keep service credentials on the server.

The local owner server binds to `127.0.0.1`; it is not an authenticated public administration service. Deploy only the selected website export. Keep the owner kit, full catalog, settings, history and private project inputs out of public assets.

## What hiding means

Hiding removes that record from the exported catalog and HTML. It does not revoke access to files already shared elsewhere, remove GitHub history, sanitize the prose of visible instructions, or remove dependencies from an installable plugin. A visible skill can still mention another workflow in its source instructions. A plugin downloads as its complete published package, including required helper skills; its visibility and download controls are separate from individual skill controls.

Before publishing, read the selected content and check its examples, references and permissions for the intended audience. The export manifest records the catalog source commit, selection revision and SHA-256 for every exported file. Task ZIPs are included only when their release commit and hashes match that catalog. Plugin links point to the repository's latest published plugin release and may move independently of the snapshot.

## Refresh without losing choices

In the local viewer, **Update from GitHub** checks for a successful verification run at the current main commit and refreshes the catalog. It preserves visibility settings. Export again to rebuild each destination from those choices. Save the settings in GitHub when you want Actions to reproduce the same selection on subsequent main builds.

The catalog updater does not replace the owner application's Python or JavaScript source files. Download a new owner kit for application updates and import the saved choices. The kit requires Python 3.10 or later; GitHub refresh additionally requires the GitHub CLI signed into an account with repository access. Browsing an exported website requires neither tool.
