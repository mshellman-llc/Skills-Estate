# Git and repository work

Before editing, record the repository root, current branch, current commit,
working-tree status, remote base, and requested finish line. Preserve unrelated
changes. A release branch starts from the current authoritative base, normally
`origin/main`, unless the user names another starting point.

Keep one independently reviewable objective per branch. Do not import an old
audit, archive, dirty checkout, or similarly named folder merely because it
contains related work.

Before handoff:

1. Compare the full branch with its remote base, not only the last commit.
2. Confirm the commit and changed-file counts match the intended scope.
3. Inspect changed filenames and the diff for unrelated work, private paths,
   client data, credentials, and generated local artifacts.
4. Run focused tests and the repository's full verification in proportion to
   risk.
5. Confirm the working tree is clean when claiming a committed result.

`committed-locally` does not mean the branch exists on GitHub. `pr-open` does
not mean merged. `merged` does not prove publication, installation, deployment,
or live behavior.
