---
skill: writing-diagnostics
title: Rewrite a stiff delay email to a facilities committee
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 0daa9be3fbb824299b036c91f0b07559db7558fffab208cf9e1bcee383167749
---

## Request

Can you fix my draft email to the facilities committee about the pool roof delay? It reads stiff and I don't want it to sound machine-written. My project notes are in inputs/ and every figure has to stay as it is.

## Inputs

Run of the `writing-diagnostics` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `revised-email.txt`.

#### draft-email.txt

Subject: Exciting Update: Pool Reopening Timeline

Dear Committee Members,

I hope this email finds you well. I am thrilled to share a transformative update on the Alderbank Pool roof project. Navigating unforeseen challenges, our team has worked tirelessly to ensure a seamless path forward.

The reopening, originally planned for 3 March, is now expected on 14 April. This delay is not about quality, it's about safety. Inspectors found corroded steel in 6 of the 22 roof trusses, and replacing them adds $38,400 to the $212,000 contract. Fortunately, our contingency fund of $45,000 can absorb the cost, so no new money is needed.

Time is of the essence, as the steel quote expires soon. We will need your approval promptly to keep the project on track. Feel free to reach out with any questions, and thank you for your continued support and partnership.

Warm regards,
Tomasz Weber
Facilities Manager

#### project-notes.md

#### Alderbank Pool roof: notes, 3 November

- Old cladding came off the week of 20 October. Inspector (Dana Okafor, Ridgeway Structural) found corrosion in 6 of the 22 trusses.
- Contract with Calloway Roofing: $212,000. Change order for replacing the 6 trusses: $38,400, quote Q-2291.
- Quote Q-2291 holds until 25 November. After that the steel price is re-quoted.
- Contingency fund balance: $45,000. Change order needs committee approval because it is over the $25,000 delegated limit.
- Facilities committee meets 18 November.
- Original reopening: 3 March. New reopening: 14 April, only if the steel arrives within 5 weeks of the order.
- Swim club has been told the pool stays closed until the new date; they have asked for a written update.

## Output

I rewrote the email and saved it as `out/revised-email.txt`. Your original stays in `inputs/draft-email.txt`. The text is below.

```
Subject: Alderbank Pool roof: approval needed on 18 November for a 14 April reopening

Dear committee members,

The pool will reopen on 14 April instead of 3 March. After the old cladding came off, Dana Okafor of Ridgeway Structural inspected the roof and found corrosion in 6 of the 22 trusses.

Calloway Roofing quotes $38,400 to replace those six (Q-2291), on top of the $212,000 contract. The contingency fund holds $45,000, so the cost fits inside it. Because the change order is over the $25,000 limit delegated to me, it needs a committee vote.

The quote holds until 25 November, after which the steel is re-quoted. I am asking for approval at your 18 November meeting so the order goes in before the quote lapses. The 14 April date also depends on the steel arriving within 5 weeks of the order.

The swim club has asked for a written update. I would like to send it after your vote.

Tomasz Weber
Facilities Manager
```

#### What changed

- **Opening and subject.** The draft started with "I hope this email finds you well" and "thrilled to share a transformative update". The new version opens with the reopening date and puts the decision and its deadline in the subject.
- **Vague wording replaced with your notes.** "Unforeseen challenges", "worked tirelessly" and "expires soon" are gone. In their place are the inspector, the 6 of 22 trusses, the quote number and the 25 November lapse date.
- **Ask with a date.** "We will need your approval promptly" now reads "approval at your 18 November meeting". The notes explain why a vote is needed: the change order is over the $25,000 delegated limit.
- **Forced contrast removed.** "Not about quality, it's about safety" is deleted. Your notes don't say the delay was about safety, so that claim was not supported.
- **Dependency added.** The draft gave 14 April as firm. Your notes say it holds only if the steel arrives within 5 weeks of the order, so that condition is now in the email.
- **Closers removed.** "Feel free to reach out", "continued support and partnership" and "Warm regards" are cut. The email ends on the swim club item.
- **Ownership made explicit.** "The delegated limit" now says it is yours ("delegated to me"), and the approver is the committee.

#### Figures check

I did the tie-out by hand because I can't run `rewrite_scan.py --tie-out` here. Every figure and date in the revision matches your notes: 14 April, 3 March, 6 of 22 trusses, $38,400, $212,000, $45,000, $25,000, 25 November, 18 November, 5 weeks and Q-2291. I added no figures. Your draft said "no new money is needed"; I replaced it with "the cost fits inside" the contingency fund, which is the only claim the $45,000 balance supports. I did not compute a remaining balance, since your notes don't give one.

#### Checks I could not run

- I could not run `writing_check.py`, so there is no checker result. I read the text by hand against the construction rules instead: balanced clauses, antithesis, triads, stacked fragments, deference phrasing, chatbot closers and repeated phrases. I found none left, and I made a second pass to remove two sentences I had added without a source. This is a reading pass, not a scanner pass.
- No review receipt was produced, because this was a short message. The skill treats short messages as a quick pass without one.

#### Please confirm

- **Swim club line.** "I would like to send it after your vote" is my wording. Your notes say only that the club wants a written update. Change or delete it if you plan to send it sooner.
- **Dana Okafor's mention.** I named the inspector because your notes do. Remove the name if the committee doesn't need it.
- **Cladding timing.** I kept "after the old cladding came off" without a date. Your notes say the week of 20 October, so add it if you want.

Files:
- `out/revised-email.txt`: the revised email shown above.
