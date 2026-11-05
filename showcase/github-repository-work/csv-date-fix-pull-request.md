---
skill: github-repository-work
title: Open a pull request for a CSV month-end date fix on a protected main
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 416dd70ad35b0187da9d23fa1168ae095aaa59cbaecd47b79525d33b475156e5
---

## Request

I fixed the month-end date bug in our CSV export and want it on GitHub as a pull request against main, following the repo's conventions. Leave my scratch notes alone, they aren't part of this.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the `github-repository-work` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### gh-and-conventions.txt

$ gh auth status --hostname git.example.com
git.example.com
  ✓ Logged in to git.example.com account jrivera-dev (keyring)
  - Git operations protocol: https

$ gh repo view git.example.com/tidewater/ledger-export --json nameWithOwner,viewerPermission,isPrivate
{"nameWithOwner":"tidewater/ledger-export","viewerPermission":"WRITE","isPrivate":true}

--- CONTRIBUTING.md (excerpt) ---
- main is protected: changes land through a pull request with one approving review and passing CI.
- Branch names: fix/<short-topic> or feat/<short-topic>.
- Commit subjects: imperative, under 72 characters, no trailing period.
- PR description needs "What changed", "How tested", and "Risk" sections.
- Do not commit anything under notes/.

#### git-state.txt

$ git remote -v
origin  https://git.example.com/tidewater/ledger-export.git (fetch)
origin  https://git.example.com/tidewater/ledger-export.git (push)

$ git branch --show-current
main

$ git log -1 --oneline
a41c9e2 Release 2.8.0

$ git status --short
 M src/export/csv_writer.py
 M tests/test_csv_writer.py
?? notes/scratch-q4.md

$ git diff
--- a/src/export/csv_writer.py
+++ b/src/export/csv_writer.py
@@ -41,7 +41,7 @@ def format_period_end(d):
-    return (d.replace(day=28) + timedelta(days=4)).replace(day=1).isoformat()
+    return calendar_last_day(d).isoformat()
--- a/tests/test_csv_writer.py
+++ b/tests/test_csv_writer.py
@@ -90,0 +91,8 @@
+def test_period_end_leap_february(): ...   # 2028-02 -> 2028-02-29
+def test_period_end_31_day_month(): ...    # 2026-10 -> 2026-10-31
+def test_period_end_december(): ...        # 2026-12 -> 2026-12-31

$ python -m pytest -q
45 passed in 3.1s
(before the change, the 3 new tests fail: 42 passed, 3 failed)

## Output

The fix is ready to go up as a pull request, but nothing has been committed, pushed or opened yet. Everything below comes from the git and `gh` output you supplied, and I have not run any command myself. Reply "go" and I'll run the commands below in order, stopping if any check fails.

#### What I checked

- **Target:** `origin` is `https://git.example.com/tidewater/ledger-export.git`. This is an enterprise host, so every `gh` command uses `--hostname git.example.com` and the full `git.example.com/tidewater/ledger-export` name.
- **Access:** `gh` is logged in to that host as `jrivera-dev` through the keyring. `gh repo view` reports `viewerPermission: WRITE` on a private repo, which is enough to push a branch and open a PR.
- **Branch:** you are on `main` at `a41c9e2 Release 2.8.0`. `main` is protected, so the change goes on a new branch and lands through a PR with one approving review and passing CI. I won't push to `main` or work around the review.
- **Working tree:** two modified files belong to the fix, `src/export/csv_writer.py` and `tests/test_csv_writer.py`. `notes/scratch-q4.md` is untracked. CONTRIBUTING.md also forbids committing `notes/`, so I'll stage the two fix files by name and leave the notes file alone.
- **Tests:** 45 pass with the change. Before it, the three new tests failed and 42 passed, so the tests do exercise the fix.

#### What the fix does

`format_period_end` returned the first day of the next month, for example `2026-11-01` for an October date. It now returns the last day of the month: `2026-10-31`, `2028-02-29` and `2026-12-31` are the cases the new tests cover.

#### Commands I will run after your go-ahead

```
git switch -c fix/csv-period-end-date
git add src/export/csv_writer.py tests/test_csv_writer.py
git commit -m "Return last day of month from format_period_end"
git push -u origin fix/csv-period-end-date
gh pr create --hostname git.example.com --repo tidewater/ledger-export \
  --base main --head fix/csv-period-end-date \
  --title "Return last day of month from format_period_end" \
  --body-file pr-body.md
```

The branch name follows `fix/<short-topic>`. The commit subject is imperative, 49 characters and has no trailing period.

After the push I will run `gh pr view` and `git ls-remote origin fix/csv-period-end-date`. I'll check that the remote commit matches the local one and that the PR targets `main`. Then I'll report the PR number and CI status. A local commit alone would not count as done.

#### PR description

It uses the three sections CONTRIBUTING.md requires.

> **What changed**
> `format_period_end` in `src/export/csv_writer.py` returned the first day of the following month. It now returns the last calendar day of the month in the input date. Three tests cover a leap-year February, a 31-day month and December.
>
> **How tested**
> `python -m pytest -q` passes with 45 tests. Before the fix, the three new tests fail and the other 42 pass.
>
> **Risk**
> CSV exports will show a different `period_end` value for every month. Anything downstream that read the old value as a first-of-month date needs checking before release.

#### Open points

- The Risk section is my reading of the diff. I have no information on downstream consumers of `period_end`, so please correct it if you know of any.
- The diff calls `calendar_last_day`, and I can't see where it is defined or imported. The 45 passing tests suggest it resolves, but check that the import is in the file you're committing.
- A reviewer must approve before merge. I can't supply that.

#### Files

- `out/pr-body.md`: the PR description above, ready for `--body-file`.
- `out/answer.md`: this reply.

Status: prepared locally only. Not committed, not pushed, no PR opened.

### File: pr-body.md

##### What changed
`format_period_end` in `src/export/csv_writer.py` returned the first day of the following month. It now returns the last calendar day of the month in the input date. Three tests cover a leap-year February, a 31-day month and December.

##### How tested
`python -m pytest -q` passes with 45 tests. Before the fix, the three new tests fail and the other 42 pass.

##### Risk
CSV exports will show a different `period_end` value for every month. Anything downstream that read the old value as a first-of-month date needs checking before release.
