---
name: github-repository-work
description: Work with repositories owned by mshellman-llc using the shared authenticated GitHub CLI and Git. Use for repository access, commits, pushes, pull requests, releases, and repository deployment workflows.
---

# GitHub repository work

Claude Code and Codex use the same user-level GitHub CLI login on this Mac. Use `gh` from PATH, or `~/.local/bin/gh` when the shell has not refreshed. Credentials belong in the system keychain; never print, copy, store in a repository, or request the token.

Check `gh auth status` and `gh api user --jq .login` when access is uncertain. The intended owner is `mshellman-llc`. Inspect `git remote -v`, branch, commit, and working-tree changes before acting. Use `gh repo view OWNER/REPO --json nameWithOwner,viewerPermission,isPrivate` to verify the target and current access.

Use the user's requested scope. Preserve unrelated changes, use the project's branch and review conventions, and test the actual change before committing. Push to the verified remote and read back the remote commit or pull request. A local commit is not a remote update.

For deployment, read the repository's workflow and target environment. Use its existing GitHub Actions or connected deployment service when the user authorizes that action. GitHub authentication does not supply another service's credentials. Observe the run or service state before calling a deployment complete. Do not bypass protected branches, reviews, or environment approvals.

If CLI access fails, report the account, repository, and non-secret error. Use the normal `gh auth login --hostname github.com --git-protocol https --web` flow when the user authorizes authentication. Never weaken agent approval settings or create tokens in project files to make access easier.
