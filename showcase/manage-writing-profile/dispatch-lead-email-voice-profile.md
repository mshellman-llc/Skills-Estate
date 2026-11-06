---
skill: manage-writing-profile
title: Building an email voice profile from mixed-provenance samples
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: e379f9a134e038cc87e2013b0238f114fbad46e874d27dada6e878b688557b02
---

## Request

I'd like you to build a writing profile of my own voice from the samples in inputs/samples.md, so a drafting assistant can later write my customer and team emails the way I do. I'm authorizing the use of only those samples, for this purpose; the notes file says which ones I know aren't purely mine.

## Inputs

Run of the built `manage-writing-profile` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `profile-draft.json`.

#### notes.md

#### Notes from Dana

- S6 is a vendor's text; I only added "FYI".
- S7: the signature line is our company template. The sentence above it is mine.
- S8 came out of an AI tool. I sent it unchanged because I was rushed.
- Everything else I wrote myself.
- Use: drafting customer and team emails. Please don't build anything for public posts or phone calls.

#### samples.md

#### Writing samples (Dana Ostrow, dispatch operations lead)

##### S1. Email to dispatch team (peers), Tue
Subject: Dock 4 swap
Need two people to cover Dock 4 Thursday 6-10am. Sam is out. Reply by noon with who can do it, and if nobody can I'll cover the first hour myself. Thanks.

##### S2. Chat to a peer
can you check the Halvorsen pallet count before 3? i think the scan is off by one. don't re-scan, just eyeball it

##### S3. Email to client (established)
Subject: Late delivery, order 4471
Hi Marcus,

The 4471 truck missed its window. It left the depot two hours late because the loader broke down, and that is on us. It will reach you tomorrow by 10am. I've taken the freight charge off the invoice. If 10am doesn't work for your receiving crew, tell me and I'll move it.

Dana

##### S4. Email to client (new relationship)
Subject: Intro and pickup schedule
Hello Ms. Teague,

I'm Dana, I run dispatch for your account. I think Tuesday and Friday pickups might work best for you, but please tell me if that doesn't fit. Happy to adjust whatever you need. Looking forward to working together.

Best,
Dana

##### S5. Email to director (leadership)
Subject: Overtime request, December
Recommendation: approve 120 overtime hours for December. Peak volume is up on last year and the alternative is two missed client windows a week. I'd rather spend the hours than the goodwill. I need a yes or no by the 12th.

##### S6. Forwarded vendor note
From the tire supplier: "Pricing is valid through month end. Please confirm quantities." (I forwarded this with "FYI".)

##### S7. Email with signature template
Hi all, route sheet attached. Changes are in yellow.
--
Dana Ostrow | Dispatch Operations | Tel 555-0100 | "Delivering on time, every time"

##### S8. Draft written by an AI tool, sent by me
Dear valued partner, I hope this message finds you well. We are delighted to inform you of our updated holiday schedule...

##### S9. Voice-memo transcript (spoken, to myself)
ok so for Monday, first thing, call the carrier, then walk the yard, um, then I guess check the sheet.

## Output

I've drafted your profile from the samples you authorized, and it is waiting for your confirmation. It isn't final, `last_confirmed` is empty, and I haven't stored it anywhere.

#### Authorization I logged

- **Whose voice:** yours.
- **Sources:** the samples in `inputs/samples.md`, and nothing else.
- **Purpose:** drafting customer and team emails.
- **Exclusions:** public posts and phone calls. The profile has no entries for either.

#### What I used and what I set aside

I used five complete messages and one sentence. The five are the team email, the chat to a colleague, the two client emails and the leadership overtime request. The sentence is the line above the signature in S7.

I discarded these before drawing any patterns:

- **S6:** the vendor's note. Your "FYI" is too short to show anything.
- **S7 signature line:** the company template.
- **S8:** the AI-drafted holiday notice. You sent it unchanged, so it isn't evidence of your voice.
- **S9:** the voice memo. It's one note to yourself with no audience, so it only supports "spoken: insufficient evidence".

#### Proposed profile

**Written, all channels**

| Pattern | Confidence | Samples |
|---|---|---|
| Short declarative sentences, plain verbs, no filler openers or closers | high | 6 |
| Internal messages open with the ask or the recommendation, with no greeting | medium | 3 |
| The ask comes with a deadline, a time or a fallback | medium | 3 |
| One clause for the reason, then straight to what happens next | medium | 3 |

**Adjustments by situation** (each rests on one message, so all are low confidence)

- **Email to peers, request:** plain subject line, a reply-by time, and an offer to cover the gap yourself if nobody answers.
- **Chat to a peer, request:** lowercase, no sign-off, and a shortcut about what not to do.
- **Email to an established client, correcting a miss:**
  - First-name greeting.
  - The fault is stated early and called the company's.
  - New time, remedy already applied, one specific alternative.
  - Signed with first name only.
- **Email to a new client, informing:** introduces your role, proposes a schedule with softeners and invites correction, and ends warmly.
- **Email to leadership, deciding:** opens with "Recommendation:", gives the cost of the alternative in one sentence, and ends with the decision date.

**Conflict I did not resolve**

With the established client you were direct and unhedged. With the new client you were hedged and open-ended ("might work", "whatever you need"). The obvious reading is that it depends on how well you know the person, but that rests on one message each. I kept both readings and did not pick a side. Which is right for you?

**Gaps recorded as insufficient evidence**

- Written: documents, briefs, decks, public audiences, setting a boundary, persuading, facilitating, supporting someone, and close relationships.
- Spoken: everything.

For any of these the drafting assistant should fall back to plain, unstyled writing.

#### What I need from you

1. Confirm or correct the patterns above, and say which way the hedging conflict should go.
2. Tell me where the profile should live. The install configuration didn't name a path, so I've kept the draft in `./out/`, which is a working copy and not a store. The raw-evidence log should sit apart from the compact profile, with the narrowest access you have available.
3. The sample is small: six units, one per situation. If you can add two or three more client emails and some chat messages you wrote yourself, the low-confidence adjustments could be firmed up.

#### How I checked it

- **Script:** I couldn't run `profile_builder.py`, so I applied its rules by hand. Only authored and edited-template material was kept. The draft has every top-level key and every routing key. Authorization is true. Every tendency has an eligible provenance and a source count above zero. I haven't run the real validator.
- **Prose checker:** I couldn't run the writing checker, so I read the authored text myself.
- **Missing file:** `_shared/build-card.md` isn't in the package, so I skipped its run-record gates.
- **Names:** The profile holds no names, figures or order details from the samples, only patterns.

#### Files

- `out/profile-draft.json`: the compact runtime profile (draft, unconfirmed), with the structure above plus `history` (one entry: draft created, not yet confirmed) and `conflicts` (the hedging entry, unresolved).
- `out/evidence-log.md`: the provenance table for S1–S9, kept apart from the profile.

If you confirm, I'll set `last_confirmed`, add a history entry and move the profile to the location you name. You can correct a single field, add evidence, pause automatic use (revoke), or have the profile and the evidence log deleted outright.

### File: evidence-log.md

#### Evidence tagging (raw-evidence side; keep apart from the runtime profile)

| Unit | Channel / audience / job | Provenance | Used |
|---|---|---|---|
| S1 | email / peers / request | authored | yes |
| S2 | chat / peer / request | authored | yes |
| S3 | email / established client / correct | authored | yes |
| S4 | email / new client / inform | authored | yes |
| S5 | email / leadership / decide | authored | yes |
| S6 | vendor text, forwarded | forwarded | no (only "FYI" is hers, too short) |
| S7 body | email / group / inform | authored | yes (one sentence) |
| S7 signature | company template | templated | no |
| S8 | email / partner / inform | ai-generated | no |
| S9 | spoken, to self | authored, spoken | one unit, no audience; recorded as insufficient evidence |

Conflict list: hedging with clients (S3 vs S4).
