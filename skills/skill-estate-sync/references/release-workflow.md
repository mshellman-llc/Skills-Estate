# Maintain the functional plugins

Author each workflow in `skills/`, shared rules in `policies/`, and runtime relationships in `config/runtime-dependencies.json`. `config/skill-catalog.json` maps public tasks and internal modes; `config/plugin-bundles.json` assigns those tasks to the existing nine plugins. Do not edit installed copies or generated `plugins/`, `build/` or `dist/` as source.

## Change and verify

Use the existing governed intake for a new skill. Preserve useful resources and failure behavior in a repair. Follow `policies/skill-standard.md`; a schema or keyword check does not establish semantic quality. Complete the changed behavior tests, relevant dependent tests and actual output review. Shared assembly changes require the estate suite. Keep private originals and task evidence outside portable packages.

From the repository root:

```sh
python3 tools/estate.py validate
python3 tools/run_tests.py --report .local/test-results.json
```

The runner reports browser, loopback and generated-map coverage separately. Use `--all-integrations` in a supported environment. Never launch installed macOS Chrome through Node or Playwright; use the guarded supported browser route. A deferred check stays pending, not passed.

## Record a release version

After source, dependencies and assembly are stable, raise the `version` in `config/plugin-bundles.json` and record its change note:

```sh
python3 tools/plugin_version.py --record 'Describe the functional changes and relevant verification.'
# Commit the reviewed source and version record before packaging.
python3 tools/estate.py sync
python3 tools/plugins.py --candidate
```

`config/plugin-version-history.json` binds each version to the source, dependency, routing and assembly inputs. Reusing a version for changed content fails. The history is excluded from its own fingerprint; changing review receipts alone does not alter functional content. Keep previous notes and records for rollback. Package assembly reads committed `HEAD` contents and includes all transitive dependencies. Local changes, including staged files, are excluded; manifests name the commit. Inspect the actual generated files and host manifests before authorizing distribution.

## Existing distribution route

The marketplace is `.claude-plugin/marketplace.json`. The existing GitHub workflow builds nine plugins from main and publishes the generated folders and ZIPs. Publication remains a separate authorized action. Owner publication records unresolved acceptance gaps; it does not convert them into reviewed or host-verified status. Ordinary reviewed packaging still requires matching accepted source, router and shared-assembly evidence. The authoring repository and its history can contain private recovery context; portable package review covers the generated payload, not permission to share the repository.

Automated publication requires a successful `verify.yml` run for that source revision. A generated-only publication commit may reuse its immediate verified parent's result; any source change or pending/failed verification blocks that fallback. If main advances while building, publication stops and the next run rebuilds. It never rebases old generated files onto new source. The release targets the actual publication commit, and subsequent runs compare ZIP bytes and repair missing uploads. Unexpected extra ZIPs require review before removal.

Claude uses the configured marketplace. `python3 tools/estate.py update` is the existing owner-authorized Mac update: fetch verified GitHub main into a temporary checkout, run existing local checks with the fetched code, build, then update Codex and back up duplicate Claude copies in the existing activation transaction. It changes installations and is not part of a source-only repair. It preserves the authoring checkout and records commit, verification, test and rollback evidence under the durable repository identity. Claude marketplace caches remain managed by Claude.

`test-local` is the explicit development check/build path and does not install. `sync` changes only candidate build and ZIPs. Versioned local releases and restore receipts preserve rollback. Account uploads and live host invocation remain separate evidence.

To deploy a merged updater repair without switching or overwriting an authoring branch, run its tooling from a separate clean checkout: `python3 /path/to/clean-checkout/tools/estate.py update --repository /path/to/canonical-checkout`. The explicit repository remains the durable installation identity. Merging the repair alone does not replace tooling in an older open branch.


## Context and retirements

Client facts, contract policies, accounts, paths and author profiles come from explicit task inputs. Writing Integrity's learning helper requires an explicit authorized `--store`; no environment or personal default selects a profile. Keep learning history and private evidence outside source and plugin trees. Unconfigured optional context uses the documented core method or a bounded refusal, never another person's defaults.

`config/retired-entrypoints.json` preserves the 15 removed standalone predecessors and the earlier standalone Prose Pass retirement. Their necessary implementations remain internal modes or diagnostics under their recorded successors. Catalog construction and ordinary activation reject retired standalone names. Explorer remains available under the later keep decision. Recovery through an old receipt is an explicit reversal, not an ordinary update.
