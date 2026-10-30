---
name: github-repository-work
description: Work with the task-selected GitHub repository using an available authenticated GitHub CLI and Git. Use for repository access, commits, pushes, pull requests, releases, and repository deployment workflows.
---


# GitHub repository work

Resolve `gh` from PATH or an explicitly configured executable path. Identify the requested host, owner and repository from the task and verified remote; do not assume hosts share a login or that an account is configured. Keep credentials in the host's supported credential store; never print, copy, store in a repository, or request the token.

Inspect `git remote -v`, branch, commit and working-tree changes before acting. Resolve `HOST/OWNER/REPO` explicitly, including an enterprise host when applicable. Check `gh auth status --hostname HOST` and `gh api --hostname HOST user --jq .login` when access is uncertain. Use `gh repo view HOST/OWNER/REPO --json nameWithOwner,viewerPermission,isPrivate` to verify the target and current access. Replace the uppercase placeholders with the verified target; do not choose an owner from the authenticated username alone.

Use the user's requested scope. Preserve unrelated changes, use the project's branch and review conventions, and test the actual change before committing. Push to the verified remote and read back the remote commit or pull request. A local commit is not a remote update.

For deployment, read the repository's workflow and target environment. Use its existing GitHub Actions or connected deployment service when the user authorizes that action. GitHub authentication does not supply another service's credentials. Observe the run or service state before calling a deployment complete. Do not bypass protected branches, reviews, or environment approvals.

If CLI access fails, report the account, repository, and non-secret error. Use the normal `gh auth login --hostname HOST --git-protocol https --web` flow when the user authorizes authentication. Never weaken agent approval settings or create tokens in project files to make access easier.
