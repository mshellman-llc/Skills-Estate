# Skills Estate

Read `AGENTS.md` for the repository workflow. Use the same canonical skills and commands as Codex. Keep account-synced and vendor-managed skills outside this repository's installer.

## Session rules

- Push branches with `git push -u`, open a pull request and merge it once CI is green. Merging to main publishes the plugins and does not wait for Megan. These still wait for her: putting something on the public site or sharing a page, spending money, sending messages, deleting things, and force-pushing or rewriting history.
- Record the plugin version (`tools/plugin_version.py --record`) on a branch rebased onto the latest `origin/main`. Main moves often, and a version recorded on an old base collides.
- Account plugins reach the new version about 20 to 25 minutes after the publish commit on main. Compare the installed version with `config/plugin-bundles.json` before saying they match. Megan can start a manual sync from Customize, then Plugins.
- In the cloud container, `tools/verify.py` fails 4 tests for missing dependencies: the image-size module and the PDF font render. CI checks those. Report them as environment failures.
- In a Claude Code cloud session, `gh pr create` and `gh pr merge` fail because GraphQL is blocked. Use REST with the path first, as `gh api repos/mshellman-llc/Skills-Estate/pulls -X POST ...` and `gh api repos/mshellman-llc/Skills-Estate/pulls/<n>/merge -X PUT`, so the allow rules match.

## Who reads this repository

- The MeganOS workspace (`mshellman-llc/meganos-workspace`, `src/lib/skills.ts`) reads `artifacts/skills-map/index.json`, `artifacts/skills-map/workflows.json`, `config/plugin-bundles.json` and `config/skills-publication.json` at main's commit. Renaming or reshaping any of them breaks its Skills page and connector tools, so change `skills.ts` in the same piece of work.
- Skill guide wording appears in three places: the map in this repository, the MeganOS Skills page (it refreshes from main within an hour) and the shared map artifact, which is rebuilt by hand. A wording fix is done when the shared map is rebuilt or listed as pending.
