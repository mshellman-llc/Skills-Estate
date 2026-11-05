---
skill: usability-testing
title: Synthesizing usability findings for a library app's loans and holds
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 1bd1c6d7af93f9ec601b9d7a13dd252e98af94236d23995d6b509ffe316355a8
---

## Request

I've attached my brief and moderator notes from four usability sessions on the Larchmont Library app, build 4.2. Please synthesize the findings by task and tell me what we should fix before the 18 November release.

## Inputs

Run of the built `usability-testing` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### brief.md

#### Larchmont Library app, build 4.2: study brief

Decision: which loan and hold issues to fix before the 18 November release.

Setup: moderated, in person, test accounts on a test server, 30 minutes each. Participants recorded with written consent; notes below are moderator notes, not transcripts. No task times were recorded.

Tasks (wording given to participants):
- T1: "One of your books is due tomorrow and you want to keep it longer. Do that."
- T2: "You want the novel *The Salt Road*, which is checked out. Reserve it for pickup at the Eastgate branch."
- T3: "Find out whether you owe the library any money."

Moderator completion conditions:
- T1: loan due date is extended.
- T2: hold placed with Eastgate as pickup branch.
- T3: participant states the correct balance.

Stopping rule: moderator gives a hint after about 2 minutes without progress and records it.

Recruited: 4 current cardholders from the library's volunteer panel. No under-18s, no screen-reader users.

#### session-notes.md

#### Moderator notes

##### P1 (adult, uses app weekly, iPhone)
- T1: Account > Loans > "..." menu > Renew. No hint. Done.
- T2: Searched title, tapped Reserve, picked Eastgate. No hint. Done.
- T3: Read balance from Account home. Stated it correctly. No hint.

##### P2 (older adult, first time in the app, Android)
- T1: Opened Loans, tapped the book title, looked around the detail page. Said: "I expected a button next to the book." Stalled about 2 minutes; I pointed to the "..." menu. Renewed after the hint.
- T2: Done, no hint.
- T3: Stated balance correctly, no hint.

##### P3 (parent, mostly uses the website, iPhone)
- T1: Found "..." menu, renewed. No hint.
- T2: Placed the hold but chose Northgate by mistake. Went to My Holds and tapped "Remove" to fix it. The hold was cancelled and it was number 14 in the queue. Said: "I thought it would just take it off my screen." I recreated the hold for Eastgate; the new hold is last in the queue. Counted as completed with a mistake, not a clean completion.
- T3: Stated balance correctly, no hint.

##### P4 (student, uses app monthly, Android)
- T1: Renewed from "..." menu. No hint.
- T2: Not attempted. Room booking ended the session at 25 minutes.
- T3: Stated balance correctly, no hint.

## Output

### Larchmont Library app 4.2: findings from four sessions

Fix the "Remove" button on My Holds before 18 November, and make Renew visible on the loan row. Both came from single participants in a four-person study, so the counts below describe these sessions only.

#### Results by task

| Task | Attempted | Clean, unassisted | Notes |
|---|---|---|---|
| T1 Renew a book | 4 of 4 | 3 | P2 needed a hint |
| T2 Reserve for Eastgate pickup | 3 of 4 | 2 | P3 completed with a mistake; P4 not attempted |
| T3 Check what you owe | 4 of 4 | 4 | No problems |

No task times were recorded, so none are reported. The notes are moderator notes, not transcripts. The one quote below is the moderator's written record of what was said.

#### Findings

**1. Removing a hold cancels it and loses the queue place (T2, P3). Severity: high.**
P3 placed the hold with Northgate by mistake. To fix it, they tapped "Remove" in My Holds. The hold was cancelled at queue position 14. P3 said: "I thought it would just take it off my screen." The moderator recreated the hold for Eastgate, and it went to the back of the queue.

- Observed: the button cancelled the hold, and P3 did not expect that.
- Harm: the loss of queue place is not recoverable by the participant. One observation is enough to rank this high, because a real cardholder would lose a place in a long queue.
- Opportunity count: only P3 used "Remove". The other two who attempted T2 did not need to correct a hold, so the sample says nothing about how often others would.
- Hypothesis, not tested: the label "Remove" reads as hiding an item, and nothing warns that the queue place is lost. Whether the label, the missing confirmation, or both caused the mistake is not established.
- Second issue in the same sequence: P3 had no obvious way to change the pickup branch on an existing hold. The notes do not say whether such an option exists, so check the build.

**2. Renew is inside a "..." menu (T1, P2). Severity: medium.**
P2, new to the app, opened the book's detail page instead. They said: "I expected a button next to the book." After about 2 minutes without progress, the moderator pointed to the "..." menu, and P2 renewed. That is an assisted completion and should not be counted as unassisted.

- 3 of 4 found the menu without help (P1 weekly user, P3 mostly a website user, P4 monthly user). Only the first-time user failed, so the finding concerns discoverability for new users. The study did not test that directly.
- Harm: the task was recoverable with a hint, but a cardholder with a book due tomorrow and no moderator could abandon it. Whether they would is unknown.
- Hypothesis: a visible Renew button on the row would remove the problem. This is a proposal, not a verified fix.

**3. Checking the balance worked (T3).**
All four stated the balance correctly from Account home with no hints. No change is indicated by this evidence.

#### What the study cannot say

- T2 has three attempts. P4's session ended after 25 minutes because of a room booking, so there is no data from them on the reserve flow.
- Only four cardholders from the library's volunteer panel took part. There were no under-18s and no screen-reader users, so accessibility of the "..." menu and the holds list is untested.
- Neither finding supports a rate for all users.

#### Recommended before 18 November

1. **Hold removal.** Rename "Remove" to "Cancel hold" and add a confirmation that states the queue position will be lost. If the pickup branch can be changed on an existing hold, expose that option in the same screen.
2. **Renew.** Add a Renew button to each loan row, keeping the "..." menu for other actions.
3. **Retest.** Rerun T1 and T2 on the revised build with at least 3 participants, including two who have not used the app before and one screen-reader user. Reuse the same task wording and completion conditions. Add a variant of T2 where the participant has picked the wrong branch, so the correction path is observed deliberately. Record the build number and who participated.

Neither change is a verified fix until that retest is done. I did not contact anyone or alter any records.

#### Evidence record

| Participant | Task | Build | Behavior | Outcome | Assistance | Source |
|---|---|---|---|---|---|---|
| P1 | T1, T2, T3 | 4.2 | Used "..." menu; reserved Eastgate; read balance | Complete | None | session-notes.md, P1 |
| P2 | T1 | 4.2 | Opened detail page; stalled about 2 min | Complete | Hint to "..." menu | session-notes.md, P2 |
| P2 | T2, T3 | 4.2 | As expected | Complete | None | session-notes.md, P2 |
| P3 | T1, T3 | 4.2 | As expected | Complete | None | session-notes.md, P3 |
| P3 | T2 | 4.2 | Chose Northgate; tapped "Remove"; hold cancelled at position 14 | Completed with mistake | Moderator recreated hold | session-notes.md, P3 |
| P4 | T1, T3 | 4.2 | As expected | Complete | None | session-notes.md, P4 |
| P4 | T2 | 4.2 | Not attempted | Not attempted | n/a | session-notes.md, P4 |

#### Files

No files were generated beyond this answer: `./out/answer.md`. The bundled writing checker script could not be run here, so I read the text through by hand for filler and unsupported claims.
