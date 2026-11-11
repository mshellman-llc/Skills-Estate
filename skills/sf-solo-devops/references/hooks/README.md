# Salesforce workflow hooks

These reference hooks support the solo Salesforce workflow in Claude Code. Git hooks can run in other Git clients when configured. Claude event hooks do not automatically run in Codex; Codex must perform the same workflow checks directly or use a separately tested adapter.

No hook installation is implied by this directory. Merge the settings into the project's existing configuration, preserve existing permissions, and test the installed copies with synthetic events before relying on them. The template does not grant blanket Bash permission.

## Use without an org

The local preparation path includes source changes, local checks, and permission-set generation. `ensure-worktree-config.sh` can link a main checkout's Node dependencies into a worktree. It does not copy an org alias, set `target-org`, or call Salesforce.

`guard-sf-flags.sh` invokes its adjacent Python helper. Keep both files together. The helper permits known local CLI operations, requires one explicit target for org operations, refuses `--use-most-recent`, and refuses routine retrieves. An explicit target still needs the `org-preflight` identity check and the user's authorization for the intended action. Shell wrappers and dynamically assembled commands require direct review; this parser is not a security sandbox.

## Check source before deployment

`guard-sf-deploy.sh` checks the source checkout for real `start` and `quick` deployments. It refuses an unverified checkout, a worktree or branch other than `main`, uncommitted `force-app` changes, and a missing or mismatched `origin/main`. Refresh remote state before evaluating it; a local remote-tracking ref is not a live fetch.

Dry runs and production validation remain available from a worktree. The workflow chooses tests according to the target and project requirements. The guard does not prohibit `RunLocalTests` or `RunAllTestsInOrg`. See [Salesforce's deployment test-level documentation](https://github.com/salesforcecli/plugin-deploy-retrieve/blob/main/messages/deploy.metadata.md).

Use explicit source paths or a reviewed manifest. The reference guard's path rules are not proof that the package contains exactly the requested components; inspect the package and deployment result.

## Record results without background org calls

`record-validate.sh` and `auto-label-deploy.sh` use `_lib.sh` and `deploy-verdict.py` to interpret complete CLI JSON responses. Keep the Python helper beside the shell hooks and use `--json` on deployment commands.

The verdict requires a completed result, a valid job ID, boolean `checkOnly`, a successful CLI envelope, and an explicit command target. A report's result must match its requested job ID. Plain text such as `Status: Succeeded` cannot establish deployment success. Missing or ambiguous output remains unknown. The interpreter does not call Salesforce to fill gaps.

Validation from dirty source is not credited to a Git commit. Async reports are associated with a locally observed start through `.claude/.pending-jobs`; an unrelated historical job lookup must not credit the current commit. Retain the full raw response, source commit, package contents, preflight receipt, and acceptance checks in the private project alongside these local indexes.

| Local index | Purpose |
|---|---|
| `.claude/.validate-log` | Commit and branch credited with a successful check-only result. |
| `.claude/.deploy-log` | Commit and job ID credited with a successful deployment result. |
| `.claude/.pending-jobs` | Job IDs associated with observed async starts. |
| `.claude/.hatch-log` | Overrides observed through the agent hooks. |
| `.claude/.dod-state` | Stop-hook state used to avoid repeated notices. |

These files are evidence indexes for one clone, not proof of current org parity. They do not replace the raw result or runtime acceptance checks. Keep them gitignored and private.

`auto-label-deploy.sh` records locally by default. GitHub issue labels and comments require explicit project opt-in through `SOLO_GITHUB_UPDATES=1`, after the user has authorized those updates. A deployment does not establish that acceptance criteria passed or that a ticket can be closed.

## Wire the hooks

Copy the reference `githooks/` files into the project's `.githooks/`, and the complete `claude-hooks/` directory into `.claude/hooks/`. Shell scripts must be executable; their Python helpers must be readable. Keep the hook code tracked so worktrees receive the same version.

Review `claude-settings-template.json` against existing settings before merging. Do not overwrite a user's settings or remove an existing hook manager without preserving and reconciling its behavior. Configure `core.hooksPath` only after that review. A configuration entry alone does not prove the hook fired.

PreToolUse refusals use exit 2. PostToolUse output should explain observed results without blocking or claiming that unknown work succeeded. The local event tests do not establish how an installed host handles every event; run a host-level invocation check after installation.

## Verify the repaired behavior

The estate tests are `tests/test_sf_command_guards.py` and `tests/test_sf_deploy_receipts.py`. They feed synthetic events to the shipped shell and Python helpers, retain their output, and put fake `sf` and `gh` executables on PATH to detect unintended calls. They cover local preparation, explicit targets, multiple CLI invocations, missing Git state, structured deployment verdicts, dirty-source refusal, and local-only recording.

The other reference hooks cover editing, commits, merges, issue closure, session status, and worktree cleanup. Validate those hooks and their integration separately before reporting the complete enforcement stack as installed or verified. No test in this directory proves an actual Salesforce deployment.
