---
skill: roadmap-artifacts
title: Database migration roadmap with go/no-go gates and rollback
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: f8049332aee2da80393fa10a6ef24133b92effb692626bf6999231c7f0ffb530
---

## Request

We're moving our dock scheduling system off the old on-prem Oracle database onto managed Postgres, and I need a migration roadmap I can embed in our engineering wiki page. The brief and constraints are in the attached files; please make it something the team can read at a glance in standup.

## Inputs

Run of the built `roadmap-artifacts` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `index.html`, `plan.json`, `theme.css`.

#### constraints.txt

Constraints from the ops director (Imani Okafor)
- Downtime budget at cutover: 45 minutes, Sunday night only. No cutover in the week of Feb 15 (peak carrier season starts).
- Rollback to Oracle must be possible for 14 days after cutover.
- Shadow-read mismatch rate must be under 0.01% of compared rows before cutover is approved.
- Go/no-go decisions are made by Imani and Priya together.
- Risk tolerance: low. We would rather slip two weeks than cut over with open mismatches.

Owners: Priya Raman (overall), Tomasz Wieczorek (schema, procedures, CDC), Jun Park (API), Alicia Mendes (carrier portal), Dev Anand (finance feeds and decommission).

#### migration-brief.md

#### Dock scheduling: Oracle to Postgres

Owner: Priya Raman (engineering manager, Dock Systems). Team: 5 engineers plus 1 DBA, Tomasz Wieczorek.

##### Why now
- Oracle 12c support contract ends 31 March 2027. Renewal quote is $182,000 a year.
- Nightly batch job (slot reconciliation) now takes 6h10m and sometimes overlaps the 05:00 shift start.
- Managed Postgres in our cloud account is already approved by security.

##### What is affected
- Dock Scheduler API (Java), about 140 tables, 38 stored procedures (PL/SQL).
- Carrier portal read replica, used by 62 carriers.
- Nightly slot reconciliation job (PL/SQL package RECON_PKG).
- Reporting extracts to the finance warehouse, 4 feeds.

##### Plan so far
- Weeks 1-4 (Nov 16 - Dec 11): inventory, schema conversion, convert the 38 procedures, set up change data capture from Oracle.
- Weeks 5-8 (Jan 4 - Jan 29): run both databases in parallel. Writes go to Oracle, shadow reads compared against Postgres.
- Weeks 9-10 (Feb 1 - Feb 12): cutover on a Sunday night, Feb 7 at 22:00.
- Weeks 11-14 (Feb 15 - Mar 12): decommission Oracle, drop CDC, archive.

##### Known risks
- RECON_PKG uses Oracle-specific hierarchical queries and has no tests.
- Carrier portal replica lag must stay under 30 seconds.
- Two finance feeds depend on Oracle date formatting.

## Output

I've built the migration roadmap as a plan file plus a page shell. It is not rendered or build-checked yet, and the plan has one date conflict you need to settle (below).

**Template and format:** Tech migration, with four phases (Prep, Parallel run, Cutover, Cleanup) and a go/no-go card at the end of each. I used the Compact format because your team will read it in standup. It is a dense working view with bordered columns.

**Brand:** No brand profile was supplied, so it uses the kit's Compact defaults. I haven't called it on-brand. If your wiki has a `brand.md` or design tokens, send them and I'll compile a theme.

#### What I changed from your brief

**The cleanup phase now starts later than your brief says.** Your rollback commitment runs 14 days after the 7 Feb cutover, so it ends on 21 Feb. The brief starts decommissioning on 15 Feb. Dropping the CDC or Oracle that week would remove the rollback path. In the roadmap, Oracle stays on standby until 21 Feb. Imani and Priya confirm on 22 Feb, and CDC then stops. The Oracle shutdown go/no-go falls on 12 Mar, which still leaves about three weeks before support ends on 31 Mar. Please confirm this is acceptable.

#### Contents of the roadmap

Header: downtime budget 45 min, cutover Sun 7 Feb 2027 22:00, rollback window 14 days, Oracle support ends 31 Mar 2027.

| Phase | Dates | Steps | Biggest risk |
|---|---|---|---|
| Prep | 16 Nov – 11 Dec | Inventory 140 tables, 38 procedures and 4 feeds; convert the schema with row-count and checksum checks; convert the 38 procedures; write tests for RECON_PKG; start CDC; alert on CDC lag over the holiday gap; Go/no-go 1 | RECON_PKG has no tests |
| Parallel run | 4 – 29 Jan | Shadow reads (mismatch under 0.01%); rewrite RECON_PKG; carrier portal replica (lag under 30 s); reproduce the 4 finance feeds; timed staging rehearsal; Go/no-go 2 on 29 Jan | Shadow-read mismatches |
| Cutover | 1 – 12 Feb | Freeze writes and drain CDC at 22:00; switch the API; repoint portal and feeds; reverse sync to Oracle for 14 days; Go/no-go 3 at 04:00 Monday, before the 05:00 shift | Overrunning 45 minutes |
| Cleanup | 15 Feb – 12 Mar | Oracle on standby to 21 Feb; stop CDC and reverse sync 22 Feb; remove Oracle code from the API; archive and shut down Oracle; Go/no-go 4 | Dropping Oracle inside the rollback window |

Every step card has an owner from your constraints file, a risk tag, an exit criterion, a rollback and a verification. A "Riskiest steps" block and a three-item evidence list (the contract and quote, the batch job, your constraints) sit below the board. The board is fixed in order, so cards can't be dragged.

#### Inferred, so please confirm

- **Reverse sync (Postgres to Oracle, 14 days).** Without it, a rollback after live bookings would lose them. This is the main addition. The cutover rehearsal should test it.
- **Holiday gap, 14 Dec – 3 Jan.** The brief schedules nothing there while CDC runs unattended. I added a lag-alert step owned by Priya.
- **14 clean reconciliation nights** as the exit criterion for the RECON_PKG rewrite. The brief only says the job must stop overlapping the 05:00 shift start.
- **The step-level breakdown and owner assignments per step.** The brief gave phases and a list of owners, not individual steps.
- **Go/no-go 2 fallback.** If it fails, cutover moves to a Sunday before 15 Feb, or after peak season. Your constraint rules out the week of 15 Feb.

These are listed in the page footer, and the inferred cards carry an "Inferred" tag.

#### How it was checked

- I couldn't run `build.py` here, so I followed the "no shell" route and wrote the files by hand.
- By hand I checked these rules: every card's column exists, every group is in the legend, and cite numbers 1–3 have evidence entries. I also checked that the legend has 5 groups, under the limit of 6.
- I haven't rendered the page. Run `python3 scripts/build.py plan.json --out <dir>` to validate and build it.
- The outcome-mode check doesn't apply, because this isn't a now/next/later board.

#### Putting it in the wiki

Copy `rk.css` and `rk.js` unchanged from the skill's `assets/` folder into your wiki's static files, next to `theme.css`. Then place `<rk-roadmap src="/path/plan.json"></rk-roadmap>` where it belongs. I did not copy those two kit files into `out/`.

#### Follow-up

**Riskiest step:** rewriting RECON_PKG. It uses Oracle hierarchical queries and has no tests, so Oracle's output is the only specification. Don't start the rewrite until the characterization tests pass against Oracle.

**Cheapest de-risking test:** run the staging rehearsal early, with the reverse sync included, and time it. If the runbook doesn't fit in 45 minutes, you'll know by January rather than on the night.

#### Files

All in `./out/`:

- `plan.json`: the roadmap data (all four phases, 22 cards, callouts, evidence).
- `theme.css`: empty on purpose, since no brand profile was confirmed.
- `index.html`: page shell with the two stylesheet links, `<rk-roadmap src="plan.json">` and the `rk.js` script.
- `answer.md`: this reply.
