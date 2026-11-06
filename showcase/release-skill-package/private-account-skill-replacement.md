---
skill: release-skill-package
title: Replace a skill in a private Claude account and install it locally
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: fe3cdfc727e15ce6301c32f55d1e31be3cac6f01f4bcafef9ffc6282b727afd4
---

## Request

Replace the invoice-triage skill in my private Claude account with the current build from our finance-skills repo, and install the same package for Claude Code and Codex on this laptop. Don't publish it to the org. The status listing and account notes are in inputs/.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `maintain-skills-estate` task package in its "release to another host or account" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### account-notes.txt

Claude account (signed in as the requester), Settings > Skills
 invoice-triage  | visibility: Private | version v3 | updated 2026-10-20 | uploaded by requester
 "Publish to org" button present, not used.

Export downloaded from the account (invoice-triage-account-v3.zip) members:
 SKILL.md
 references/approval-limits.md
 references/vendor-terms.md
 references/tax-codes.md
 scripts/match_po.py
 templates/query-email.md
Account export SKILL.md line 41 also reads: For VAT treatment see references/tax-codes.md
Account export approval-limits.md says auto-approve limit 2,000 (source says 2,500).

Upload attempt, 2026-11-04 11:02 (browser session, Replace > select invoice-triage-v003.zip):
 11:02:12 file chosen, upload started
 11:02:41 spinner, no confirmation banner
 11:03:40 "Request timed out" toast
 Page not reopened afterwards. No second upload was attempted.

#### source-and-package-state.txt

== Source: ~/work/finance-skills/skills/invoice-triage ==
branch main, HEAD 4e1a9c7 "Add export_ledger.py, merge tax codes into approval-limits"
git status --short:
 M skills/invoice-triage/scripts/match_po.py     (modified 2026-11-03 16:40, uncommitted)
git log -3 --oneline -- skills/invoice-triage:
 4e1a9c7 Add export_ledger.py, merge tax codes into approval-limits
 b81d3f2 Raise auto-approve limit wording to 2,500
 0c5e6aa Initial invoice-triage

Source files:
 SKILL.md
 references/approval-limits.md   (now contains the tax-code table, section "Tax codes")
 references/vendor-terms.md
 scripts/match_po.py
 scripts/export_ledger.py
 templates/query-email.md

grep -n "tax-codes" SKILL.md references/*:
 SKILL.md:41: For VAT treatment see references/tax-codes.md
 (no other hits; references/tax-codes.md does not exist in source)

grep -n "/Users/" scripts/*:
 scripts/export_ledger.py:12: OUT = "/Users/priya/Documents/ledger-exports/"

== Built package ==
dist/release.json entry:
 skill: invoice-triage, archive: invoice-triage-v003.zip
 sha256: 91c4d07e...a3  (recorded 2026-11-03 09:12)
 source_revision: 4e1a9c7 (clean at build time)

sha256 of dist/invoice-triage-v003.zip on disk now: 91c4d07e...a3  (matches release.json)
Zip modified 2026-11-03 09:12; match_po.py in zip is the 09:12 version.
Zip members (unzip -l): SKILL.md, references/approval-limits.md, references/vendor-terms.md,
 scripts/match_po.py, scripts/export_ledger.py, templates/query-email.md

== Local installs ==
~/.claude/skills/invoice-triage  -> real directory (not a link), edited 2026-10-12, 5 files
   files: SKILL.md, references/approval-limits.md, references/vendor-terms.md, scripts/match_po.py, templates/query-email.md
   diff vs v003 zip: SKILL.md differs, match_po.py differs, export_ledger.py missing
~/.agents/skills/invoice-triage  -> not present
~/.codex/skills/invoice-triage   -> not present

## Output

I have not replaced or installed anything yet, and I recommend against shipping the v003 package as it stands. It has two defects that would reach every destination, and your 11:02 upload may have already put it in the account. I've written the plan and record to `out/release-record.md`.

#### 1. Check the account before anything else

The Replace upload at 11:02 ended in a "Request timed out" toast with no confirmation, and the page wasn't reopened. Open Settings > Skills > invoice-triage and read the version, update time and file list.

- If it still shows v3 (updated 2026-10-20), the upload didn't land.
- If it shows a newer version or a 2026-11-04 update time, v003 landed. It has the defects below, so it needs a corrected replacement, but only after you've seen its state.

Don't retry blindly. Repeated uploads create successive versions you can't tell apart. If the page is unclear, stop and report that.

#### 2. Problems in the v003 package

| # | Finding | Evidence | Fix |
| --- | --- | --- | --- |
| 1 | Dead reference. `SKILL.md:41` says "see references/tax-codes.md", which isn't in the package. | Commit 4e1a9c7 merged tax codes into `references/approval-limits.md`. The account's v3 still has `tax-codes.md`, so v3 works and v003 doesn't. | Point line 41 at the "Tax codes" section of `approval-limits.md`. The file removal is intentional. |
| 2 | Mac-only path. `scripts/export_ledger.py:12` writes to `/Users/priya/Documents/ledger-exports/`. | Fails in an account runtime and on any other machine. | Take the output folder from an argument or environment variable, default to a folder in the working directory, and create it if missing. |
| 3 | Uncommitted edit to `scripts/match_po.py`, made 2026-11-03 16:40. | v003 was built at 09:12 from clean 4e1a9c7, so it doesn't include the edit. | You decide. If the edit is meant to ship, commit it. If it isn't, stash it. Either way the archive must match a known revision. |

Two other differences are intended, but you should know them:

- The account's v3 says the auto-approve limit is 2,000. The source says 2,500 (commit b81d3f2). Replacing v3 changes what invoices the skill will auto-approve.
- `export_ledger.py` is new. It's in neither the account copy nor the local Claude Code copy.

The account export and the local copy are older than the source here, and source history explains each difference. I'm treating the repository as the authority, not the newer upload date.

#### 3. Local destinations

- **Claude Code:** `~/.claude/skills/invoice-triage` is a plain directory, edited 2026-10-12, with 5 files. Its `SKILL.md` and `match_po.py` differ from v003. Diff both against the repository history first. If it holds work that isn't in git, copy it into the repo. Then back it up and replace it using the estate's `adopt` for this one skill. That keeps a restore receipt.
- **Codex:** `~/.agents/skills/invoice-triage` and `~/.codex/skills/invoice-triage` are both missing, so a normal install works. Use `install --skill invoice-triage --expected-source <reviewed hash>`, which leaves other installed skills alone.
- Open a fresh session in each host before testing. Cached discovery can hide the new version.

#### 4. Order of work

1. Reopen the account page (section 1).
2. Fix findings 1 and 2, settle finding 3, and commit.
3. Run `validate`, the tests, `build` and `bundle`. I can't run these from here. Run `tools/estate.py` yourself or have me run it in the checkout.
4. Compare the new zip's SHA-256 with `dist/release.json`, extract it to an empty folder, and diff it against `build/skills/invoice-triage` including file modes.
5. Using the extracted package, run one sample invoice, one adjacent request that should be unaffected, and one run with the ledger output folder missing.
6. Install locally for Claude Code and Codex, then invoke the skill in a fresh session of each.
7. In the account, choose **Replace** on the existing skill, not a new upload. Confirm the selected file has the reviewed hash and visibility stays Private. Don't touch **Publish to org**.
8. Reopen the account skill, record version, update time and file list, open `SKILL.md`, `approval-limits.md` and `export_ledger.py`, and run an invocation.
9. Only then run `record-publication --surface claude-account --skill invoice-triage --reference '...'`. That entry records the upload, not that it worked. Keep the invocation output separately.

Keep the archive filename, source version and the version the account assigns as separate fields. A file called `-v004.zip` can become account v5.

#### Questions for you

- Should the `match_po.py` edit ship?
- Is 2,500 the intended auto-approve limit going to the account?

#### Current state

| Destination | State |
| --- | --- |
| Source | Needs two fixes, one decision |
| Package | v003 built and hash-matched, not fit to release; new build pending |
| Private account | Unknown after a timed-out upload |
| Claude Code | Unchanged, divergent older copy |
| Codex | Not installed |
| Organization | Not requested, untouched |

Files: `out/release-record.md` (the table, three blockers and nine-step sequence above), `out/answer.md`.

### File: release-record.md

#### Release record: invoice-triage

Requested destinations: private Claude account (replace), Claude Code (local), Codex (local). Not requested: organization distribution.

| Field | Value |
| --- | --- |
| Source | ~/work/finance-skills, HEAD 4e1a9c7, one uncommitted change (scripts/match_po.py) |
| Archive reviewed | invoice-triage-v003.zip, sha256 91c4d07e...a3, built from clean 4e1a9c7 |
| Archive to release | Not built yet. Needs a rebuild after the two source fixes below |
| Account before | v3, Private, updated 2026-10-20 |
| Account after the 11:02 upload | Unknown. Timed out, page not reopened |
| Claude Code | Real directory, 5 files, edited 2026-10-12, differs from v003 |
| Codex | Not installed |

##### Blockers found

1. SKILL.md line 41 points to references/tax-codes.md. Commit 4e1a9c7 merged that file into references/approval-limits.md ("Tax codes" section), so v003 ships a dead reference.
2. scripts/export_ledger.py line 12 writes to /Users/priya/Documents/ledger-exports/, which does not exist on other machines or in an account runtime.
3. match_po.py has an uncommitted edit made after the v003 build. v003 does not contain it.

##### Sequence

1. Reopen the account skill page and read version, update time and file list. Do not upload again before this.
2. Fix blockers 1 and 2 in source; decide blocker 3. Commit. Run validate, tests, build, bundle.
3. Compare the new zip with dist/release.json; extract and diff against build/skills/invoice-triage.
4. Run a sample invoice through the extracted package, an adjacent request, and a run with export_ledger.py's output directory missing.
5. Local: back up and adopt the Claude Code directory, install for Codex, open fresh sessions, invoke.
6. Account: Replace (not a new skill), keep Private, reopen, compare files, invoke.
7. Record the publication only after step 6 succeeds.

Nothing in this record has been executed.
