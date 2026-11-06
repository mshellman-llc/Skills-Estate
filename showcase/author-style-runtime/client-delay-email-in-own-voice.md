---
skill: author-style-runtime
title: Client delay email drafted in the author's confirmed voice
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: acdb326d7eae4166a419e6ff07245f9afe6174a826d613d474bb21043e852b90
---

## Request

Please draft an email from me (Priya) to Tomas at Alderbank Retail telling him the October sales report will slip from the 13th, and asking him for the missing store files. Use my confirmed writing profile; my notes and profile summary are in the inputs folder.

## Inputs

Run of the `author-style-runtime` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### notes.md

#### Notes for the Alderbank email

- Client: Alderbank Retail. Contact: Tomas Ekwueme (tomas.ekwueme@example.com). We've worked together since March; he's friendly and brisk.
- October sales report was due Friday 13 November.
- Cause: the October store-level export from their warehouse team is missing 14 of 62 stores (store IDs listed in the shared tracker, tab "Oct gaps").
- We can't finish the regional roll-up without those files. The other 48 stores are already loaded and checked.
- If the files reach us by Monday 16 November, we can deliver Thursday 19 November.
- If they arrive later, the delivery date moves day for day. Don't promise anything beyond that.
- Do not offer a discount or mention the contract's late-delivery clause.

#### profile.json

{
  "person_id": "priya-nandakumar",
  "authorization": {"granted": true, "granted_at": "2026-09-02T00:00:00Z", "scope": "own written drafting"},
  "revoked": false,
  "last_confirmed": "2026-09-02T00:00:00Z",
  "routing": {
    "modes": ["written"],
    "surfaces": ["chat", "email"],
    "audiences": ["peer", "client"],
    "relationships": ["established", "transactional"],
    "jobs": ["inform", "request"]
  },
  "base_profile": {
    "written": {
      "core_tendencies": [
        {"pattern": "Opens with the decision or news in the first sentence, no greeting filler", "confidence": "high"},
        {"pattern": "Short paragraphs of one to three sentences", "confidence": "high"},
        {"pattern": "Dates written as weekday plus day and month, e.g. Thursday 19 November", "confidence": "high"},
        {"pattern": "Uses contractions (I'd, we'll, can't); no exclamation marks", "confidence": "high"},
        {"pattern": "Ends with one explicit ask and the date it is needed by", "confidence": "medium"},
        {"pattern": "Signs off with 'Thanks,' and first name only", "confidence": "high"}
      ],
      "insufficient_evidence_for": ["leadership", "public"]
    }
  },
  "channel_overlays": {
    "email|client|inform": [
      {"pattern": "States the effect on the client in the first two sentences, then the cause in one sentence; never opens with 'Unfortunately' or an apology paragraph", "confidence": "medium"},
      {"pattern": "Gives a firm new date rather than a range", "confidence": "medium"}
    ]
  }
}

## Output

Here's the draft, written in your confirmed profile.

**To:** tomas.ekwueme@example.com
**Subject:** October sales report: new delivery date Thursday 19 November

Hi Tomas,

The October sales report won't be ready on Friday 13 November. I can deliver it on Thursday 19 November.

The October store-level export is missing 14 of the 62 stores, and we can't finish the regional roll-up without them. The other 48 stores are loaded and checked.

The missing store IDs are in the shared tracker, tab "Oct gaps". If the files reach us by Monday 16 November, the 19th holds. If they arrive later, the date moves back day for day.

Could your warehouse team send the 14 files by Monday 16 November?

Thanks,
Priya

#### How the profile was applied

I did the routing check by hand, following the rules in `route_check.py`, because I can't run scripts here.

- **Gate:** the profile isn't revoked, and authorization is granted. You are the author. The content isn't a quotation, and no legal or contractual voice governs it.
- **Route:** written, email, client, established relationship. The jobs are informing and requesting, and both are in the profile's routing list. "Client" is not on the `insufficient_evidence_for` list, which only names leadership and public.
- **Base tendencies used:**
  - The news comes first.
  - Paragraphs are short.
  - Dates are written as weekday plus day and month.
  - The draft uses contractions and has no exclamation marks.
  - It ends on one ask with a date.
  - It signs off "Thanks," with your first name.
- **Email, client, inform overlay used:** the effect on Tomas is in the first two sentences, the cause follows in one sentence, and there is no "Unfortunately" or apology paragraph. The new date is firm.
- **Facts and instructions that outrank voice:** I used your notes only. The draft says the date moves day for day after 16 November and promises nothing beyond that. It leaves out any discount and the contract's late-delivery clause, as you asked.

#### Things to check

- I couldn't read the build card (`_shared/build-card.md`) or run the writing checker, because neither is in the material I was given. I read the draft by hand for filler, repeated constructions and stock transitions, and found none.
- The profile has no confidence above "medium" for the client overlay. If the draft doesn't sound like you, tell me which line, and I'll fix that construction wherever it recurs.
- The notes don't say when Tomas's team can realistically send the files. If Monday is unlikely, I'd rather change both dates than leave a promise you can't keep.

No files were saved besides this answer.
