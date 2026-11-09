# Skill build and release standard

This standard governs how an estate skill is written, changed, checked and published to each host. An estate skill must perform its stated task with the resources available on its declared host. A valid folder or a successful packaging command does not establish that capability.

Writing integrity is the first gate. No change to authored language merges, ships or reaches a host until the writing check passes and someone has read the result in full.

## Source and change control

The repository is the only source. Author skills in `skills/<name>/`, shared rules in `policies/` and runtime relationships in `config/`. Never edit `plugins/`, `build/`, `dist/` or an installed host copy. A defect found on a host returns to the repository as a pull request. The host copy is then rebuilt from the merged source.

Every change reaches `main` through a pull request that passes CI. An agent may prepare the change; the owner approves each pull request and each new host copy. Before packaging, raise the plugin version and record its note with `tools/plugin_version.py`. Commit messages follow [naming](naming.md).

## Skill anatomy

Give each skill a distinct lowercase hyphenated name that matches its folder, frontmatter, catalog entry and every host copy. The description names the task and the requests that select it. When confusion is likely, it also distinguishes the closest neighbor. Keep the procedure in `SKILL.md` and load longer references only when the task needs them. Modes stay inside their owning skill, and runtime components stay internal.

Preserve working scripts, templates and adapters. Every new or changed script that transforms data or produces an artifact gets a `*_selftest.py`, which the test suite runs. Inputs that vary by person, client or project arrive as explicit task inputs, so account names and source locations stay configurable. Branding resolves through a profile, under the shared brand policy.

The authoring intake records the job and its boundaries, the input and output contract, selection examples, related skills and required capabilities. Risk controls and stewardship have their own fields. Costs and efficiency stay unknown until a dated run measures them. A draft can carry an incomplete intake record. A released skill cannot rely on unfinished instructions or a missing component.

## Writing integrity

The gate covers every authored word a change touches: `SKILL.md` and its references, policies, READMEs and browse sources, agent routers, template copy, code comments, text fields in `config/`, the version note, commit messages and pull request descriptions. On Hyperagent it also covers each skill's description, when-to-use text and documentation.

For each changed file:

1. Run `python3 skills/writing-diagnostics/scripts/writing_check.py --config skills/writing-diagnostics/house.json FILE`.
2. Fix each finding in the text, then run the check again.
3. Read the complete file for meaning, structure and the facts it must keep.
4. For a substantive rewrite, keep the earlier version, reconcile figures with `rewrite_scan.py --tie-out`, and emit and validate a receipt with `prose_receipt.py`.

A file passes when the check exits 0. The checker gives no exemption to Markdown quotes or code, so a file can also pass with a receipt at `.writing-receipts/<path>.json`. The receipt quotes each piece of protected text exactly and gives its kind and a reason. The kinds are an exact source quotation, executable syntax, a required identifier and a quoted example in a file that teaches writing patterns. The gate masks that text and checks the file again. Afterwards, only a C24 to C27 candidate may remain, retained in the receipt with a reason and a source. No other finding can be waived. Third-party license text stays verbatim. Never rename a file, mark your own prose as protected or lower a budget to obtain a pass. Changes to the checker, its word lists or `house.json` need positive and valid examples. They may add checks and must never relax an existing one.

Some files predate the gate and still have findings. Editing prose in one of them means bringing the whole file to a pass in the same pull request. A change limited to code, identifiers or paths may leave older findings in place, but it cannot add one, and the file joins the clean-up list. Each skill is cleaned in full before its first Hyperagent build, so the ingest clears the backlog one skill at a time.

Agents run the gate before they propose a change. Three layers then enforce it with `tools/writing_gate.py`, which covers Markdown under `skills/`, `agents/`, `policies/` and `docs/`. The pre-commit hook in `.githooks` checks staged files and blocks a commit with a new or unaccounted finding; enable it once per clone with `git config core.hooksPath .githooks`. CI checks every file a pull request changes and fails the pull request on any such finding. The Hyperagent build runs the same check before a skill card goes to the owner.

## Separation

No file, identifier, commit or pull request may carry the name, abbreviation, prefix, logo, template or sample data of a former employer or a client. Names to keep out belong in a private terms file outside the repository, passed through `ESTATE_PRIVATE_TERMS_FILE`. The skill guide applies that list to each skill's files and the shared policies. `tools/private_terms.py` applies it to every tracked file outside `plugins/`, so a removed name cannot return. The pre-commit hook and the test suite run it wherever the list is configured. In CI it reads the list from the `ESTATE_PRIVATE_TERMS` repository secret and runs before any step regenerates files. A match is reported by path, line and position in the list, never by the name.

## Licenses and provenance

Keep upstream LICENSE and NOTICE files verbatim, add an attribution line to `SKILL.md`, and record the upstream source in the catalog. Check the license of new third-party material before it merges.

Material under the Commons Clause can be used and changed but cannot be sold, which includes paid hosting or support built around it. Mark those skills in the catalog as not for sale and keep them out of anything sold until they are rewritten without the upstream material or licensed. This applies today to build-roadmap, frame-jobs-to-be-done, plan-sprint, prioritize-work and refine-backlog.

## Host builds

Every host copy is built from a committed revision and records that revision. Use the repository's current build and sync tools, whose receipts identify the exact source and destination state. Reconcile existing local edits before an installation replaces them. Source text stays host-neutral, and a step that only one host needs goes in a labeled host section. When a general procedure contains Claude Code or Codex wording, correct the source rather than patching one host's copy.

Claude Code and Codex install from the plugin marketplace and the updater. Hyperagent receives one skill per task skill:

- Name, description and procedure come from the source. The when-to-use text comes from the guide's `when` field and names the closest skill to avoid, and the tags record the group, the plugin and `skills-estate`.
- Hyperagent stores a skill's files as one flat list. A file keeps its name unless it clashes with another, in which case its full path becomes the name, with `__` in place of each slash. A bundled restore script rebuilds the original folders and checks every file's hash before any script runs.
- Shared runtimes become internal Hyperagent skills, each built when the first task needs it: `estate-policies` and `review-writing` first, then `brand-renderer`, `evidence-core` and `review-deliverable`. Task skills load them by name instead of carrying copies.
- Guide connectors map to Hyperagent integrations. Credentials enter only through a skill's credential fields.
- The ingest tracker records each skill's status (not started, drafted, approved, verified or parked) and its source revision. A monthly check compares `main` with every recorded revision and lists the skills to rebuild.

## Release checks

| Check | Required evidence |
|---|---|
| Writing | Every changed file passes the writing check and has been read in full. A substantive rewrite carries a validated receipt. |
| Separation | The private terms check passes on the whole tree. |
| Resources | Every promised local file and executable dependency exists in an isolated package. |
| Behavior | A representative task produces the intended result, and meaningful failure cases behave as described. Retain inputs with their outputs and keep the errors from each attempt. |
| Selection | Requests for the skill route to it, and adjacent requests keep their intended workflow. |
| Content | Generated material matches its controlling inputs. A render or syntax check is insufficient. |
| Presentation | Inspect the actual pages or interface when layout affects use. |
| Overlap | Record whether the job belongs in a separate skill, mode, component, reference, adapter, alias or existing skill. |
| Host and sync | Test the declared invocation on each intended host and compare installed files with the packaged source. Report cloud publication separately from local installation. |

When a dependency is unavailable, test a substitute against the requested result, or deliver a supported mode within a stated boundary. Salesforce metadata preparation works offline, for example, while deployment needs an authorized org. Never present a simulated deployment as a live success.

An internal repair needs checks for the changed behavior and its affected dependents. Routing changes add adjacent-request checks, and changes to shared packaging or installers add the estate checks. A release runs all of them.

Keep original source archives separate from the reusable release. Remove company-specific defaults and private sample data without discarding the workflows they illustrate, and build examples from synthetic fixtures. Keep the test transcript and the Git commit as separate records, and record an upload separately from a verified host invocation.
