---
skill: build-interactive-explorer
title: Explorer for a community tool library's borrowing process
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 3a8479870a7aa884a1c5739c1d9da9e95e1ea069ffb1c0c924e20dbc0a8852e8
---

## Request

I've pasted our interview notes and the board's decision note from the tool library review. Can you build an interactive explorer for the board and volunteer leads that shows how borrowing works today for members and for desk volunteers, where it breaks, and what we still have to decide? Local files only, please, don't publish it anywhere.

## Inputs

Run of the built `build-interactive-explorer` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `content.json`.

#### board-decision-note.md

#### Board decision note: borrowing process
Dated 21 October 2026. Author: Dana Whitfield, board secretary.

##### Decided
- The library keeps staffing the desk with volunteers; no paid coordinator this year.
- The 3-day grace period and $2 per day fee in the bylaws stay as written.
- A members-only stock list will be trialled online. The board approved a trial only, not a full catalogue.

##### Not decided
- Whether a one-weekend "day pass" membership should exist, and what it would cost.
- Who may waive a fee: any desk volunteer, the shift lead, or only the board.
- Who owns tool repairs, and whether Thursday-only repair is acceptable.
- Whether the paper binder is retired or kept alongside the spreadsheet.

##### Constraints
- Budget for software: up to $300 for the year.
- Volunteers have no shared email accounts; the library holds member phone numbers and addresses on paper.

#### interview-notes.md

#### Tool library borrowing review: interview notes
Compiled 14 October 2026 by Priya Anand (volunteer researcher). 9 interviews: 6 members, 3 desk volunteers. Small sample; findings are reported, not measured.

##### Members (6)
- 4 of 6 said they were unsure whether a tool was in stock before travelling to the library. The only check is a printed shelf list updated monthly.
- 3 of 6 had arrived to find the tool out on loan. One said they "bought one instead and haven't been back".
- 5 of 6 borrow for a single weekend project. Joining takes about 15 minutes on paper at the desk, which two found off-putting for a one-off job.
- 2 members returned tools late because they did not know the due date. Due dates are written on a paper slip that is kept in the loan binder, not given to the member.
- No member knew how to report a damaged tool; 1 returned a cracked saw guard without saying anything.

##### Desk volunteers (3)
- All 3 look up members and tools in a paper binder, and one in a shared spreadsheet kept "for backup". The two records disagree about once a week, according to one volunteer.
- Volunteers decide alone whether a late return incurs a fee. Practice differs: one waives the first lateness, one never charges, one charges always. The bylaws say a fee of $2 per day applies after a 3-day grace period.
- Damaged tools go on a shelf marked "Repair". Nobody has a clear owner for repairs; the workshop lead (Tomas Reyes) fixes them when he is in on Thursdays.
- 2 of 3 would like a way to see a member's open loans on one page.

##### Not covered
No interviews with non-members, board members or the Thursday workshop team. No data on how many loans end late or damaged.

## Output

I've written the content for the explorer, but I haven't built the site yet. Nothing is published, as you asked. The site generator is a Python script and I couldn't run scripts here, so I checked the content by hand against its rules. Run the command below to produce the site.

#### What the explorer shows

**Headline:** "How a tool gets from the shelf to a member and back, and what the board still has to **decide.**"

**Two paths**, each with ordered stages that open to show the action, decision, handoff, reported finding and open question:

| Path | Stages |
| --- | --- |
| Member | Find a tool, Join or sign in, Borrow, Return or report damage |
| Desk volunteer | Look up member and tool, Handle a late return, Route a damaged tool |

**Other views:**
- **Roles:** Member and Desk volunteer cards, each with a borrowing journey.
- **Problem areas:** five areas, each linked to the stages it affects:
  - Stock visibility
  - One-weekend access
  - Due dates and late fees
  - Member and loan records
  - Damage reports and repairs
- **Board decisions:** what the board settled on 21 Oct 2026, plus the $300 software budget and the lack of shared email accounts.
- **Open decisions:** four items:
  - Day pass
  - Who may waive a fee
  - Repair ownership
  - Binder or spreadsheet
- **Sources:** both documents, with dates and authority.

**Findings, as the interviews report them:**
- 4 of 6 members were unsure of stock before travelling, and 3 of 6 found the tool already out.
- Due dates stay on a slip in the binder, and 2 members returned tools late because they didn't know theirs.
- Three volunteers apply late fees three different ways, although the bylaws say $2 a day after 3 days.
- Damaged tools wait on the Repair shelf for Thursday, and nobody owns repairs.

**Decisions that are already made:** the volunteer-staffed desk, the bylaw fee, and a trial of a members-only online stock list. The explorer shows the stock list as a trial, not a full catalogue.

#### Choices I made
- **No roadmap.** Your notes give no dates or sequence of planned work, so I left the roadmap view out.
- **No proposed solutions.** The explorer doesn't offer a day-pass price, a fee-waiver rule or a repair owner. It marks these as undecided, and the "proposed" fields say so.
- **Limits of the evidence.** The header and the Sources entry say the findings come from 9 interviews. They also say there are no loan counts and no interviews with non-members, board members or the workshop team.
- **Source IDs.** These appear only in the Sources view. Elsewhere the explorer shows document titles.

#### Checks
- **Done by hand, following the generator's rules:**
  - The required fields are present.
  - IDs are unique within each group.
  - The accent phrase isn't repeated inside the headline.
  - Every `sourceIds`, `moduleIds` and `roleIds` entry points to something that exists.
  - No source has a URL, so no link needs checking.
- **Not done:** the generator's own validation, `node --check` on the generated JavaScript, and any browser check. These need the script to run first.
- **Not checked:** the writing checker (`writing_check.py`). I only re-read the text.
- **Not verified:** the explorer reports what the interviews and the board note say. It doesn't show that any change would work.

#### To build it locally
```bash
python3 <skill-directory>/scripts/create_explorer.py \
  --content <absolute-path>/out/content.json \
  --output <absolute-path>/out/site
```
The output directory must be new or empty. Open `out/site/dist/index.html` afterwards.

#### Files
- `out/content.json`: the explorer content (2 paths with 7 stages, 2 roles, 5 problem areas, 2 board-decision categories, 4 open decisions, 2 sources).
- `out/answer.md`: this reply.
