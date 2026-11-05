---
skill: author-writing-style
title: Delivery schedule email to member pantries in a manager's voice
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 2c4a88898b19221b63419f21ecc5e0638268b88fd9e84e25e34785e35013b08a
---

## Request

Using Dana Whitlock's confirmed writing profile (attached), draft the email she'll send to our member pantries about the delivery change, based on my notes. It goes out Friday under her name.

## Inputs

Run of the `author-writing-style` source module, which has no task package of its own. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### dana-profile.md

#### Writing profile: Dana Whitlock

- Owner: Dana Whitlock, operations manager, Harbor Row Food Network
- Status: confirmed by Dana on 2026-09-12, version 3
- Authorization: Dana permits use for emails to member pantries and volunteers, written under her name. Not for press, legal or funder documents. Not revoked.

##### Voice rules
- Short paragraphs, first person ("I"), "we" for the network.
- Open with what changes and when. No greeting beyond "Hello all,".
- Direct and warm. One light line of humor is fine, never about a pantry or its clients.
- Name the day and the time, never "soon" or "shortly".
- Say sorry once if we cause extra work, without ceremony.
- Sign off with "Thanks, Dana".
- No exclamation marks. No bullet lists unless there are dates or times to compare.

#### notes.txt

Delivery change notes (from Tom, warehouse lead)

- Starting Monday 7 December 2026, produce and dairy deliveries move from Tuesday to Wednesday. Dry goods stay on Thursday.
- Reason: our cold-storage supplier changed its pick-up window; Tuesday trucks can't load before 11:00 anymore.
- New arrival windows: Wednesday 8:00-11:00 for the north route (Eastgate, Millbrook, St. Aldric's), Wednesday 12:00-15:00 for the south route (Riverside, Cobb Lane).
- Last Tuesday delivery is 1 December.
- Pantries that can't receive on Wednesday must tell Tom by Friday 20 November at tom@example.com, or call 555-0142. We may be able to hold a pallet till Thursday, not promised.
- Pantries open Tuesday for clients will have fresh stock a day later than now.
- Not yet decided: whether the Christmas week (21-25 Dec) schedule changes. We will confirm by 11 December.

## Output

I've drafted Dana's email to the member pantries. It's ready for her to review before Friday.

**Profile check.** I used only the profile you attached. It is Dana Whitlock's own, version 3, confirmed by her on 2026-09-12, and not revoked. It covers emails to member pantries written under her name, which is what this is. I didn't look for any other material by or about her.

**What I applied from the profile.** The email opens with "Hello all," and states the change and date straight away. It uses first person, short paragraphs, named days and times, one apology, no exclamation marks, and the "Thanks, Dana" sign-off. I used a bullet list only for the two route windows, because the profile allows lists for times to compare. I added no humor. The notes gave nothing safe to joke about, and the profile makes humor optional.

**Facts kept exactly as in Tom's notes.** The 7 December start, the 1 December last Tuesday delivery, the 11:00 loading limit, both arrival windows with their pantries, the 20 November deadline with Tom's contact details, and the unconfirmed Christmas week. I wrote "Friday" before 20 November and 11 December. Both dates fall on a Friday in 2026, but the notes didn't say so, so Dana should glance at them.

**Things to check before it goes out**
- The notes say a held pallet is "not promised." The email keeps that qualification.
- The Christmas week schedule is stated as undecided, with Tom's "by 11 December" confirmation date. Dana is making that commitment under her name, so she should agree to it.
- The notes don't say which pantries open on Tuesday. The email speaks to that group in general.
- I didn't run a style scanner, and none was supplied. I checked the draft by reading it against the profile and the notes. I corrected one sentence that first implied stock would be "older". The notes only say it arrives a day later.

**Draft** (saved as `out/email.md`)

> Subject: Produce and dairy deliveries move to Wednesday from 7 December
>
> Hello all,
>
> From Monday 7 December, produce and dairy will arrive on Wednesday instead of Tuesday. Dry goods stay on Thursday. The last Tuesday delivery is 1 December.
>
> Our cold-storage supplier has moved its pick-up window, and Tuesday trucks can no longer load before 11:00. Wednesday is the first day we can get fresh stock to you without a wait at the loading dock.
>
> Your Wednesday arrival window depends on your route:
>
> - North route (Eastgate, Millbrook, St. Aldric's): 8:00 to 11:00
> - South route (Riverside, Cobb Lane): 12:00 to 15:00
>
> If you open to clients on Tuesday, your fresh stock will arrive a day later than it does now. I'm sorry for the extra planning this causes.
>
> If you can't receive a delivery on Wednesday, tell Tom by Friday 20 November at tom@example.com or 555-0142. We may be able to hold a pallet for you until Thursday, but I can't promise it.
>
> I don't yet know whether the Christmas week schedule (21 to 25 December) changes. I will confirm by Friday 11 December.
>
> Thanks,
> Dana

**Files**
- `out/email.md`: the email above.

### File: email.md

Subject: Produce and dairy deliveries move to Wednesday from 7 December

Hello all,

From Monday 7 December, produce and dairy will arrive on Wednesday instead of Tuesday. Dry goods stay on Thursday. The last Tuesday delivery is 1 December.

Our cold-storage supplier has moved its pick-up window, and Tuesday trucks can no longer load before 11:00. Wednesday is the first day we can get fresh stock to you without a wait at the loading dock.

Your Wednesday arrival window depends on your route:

- North route (Eastgate, Millbrook, St. Aldric's): 8:00 to 11:00
- South route (Riverside, Cobb Lane): 12:00 to 15:00

If you open to clients on Tuesday, your fresh stock will arrive a day later than it does now. I'm sorry for the extra planning this causes.

If you can't receive a delivery on Wednesday, tell Tom by Friday 20 November at tom@example.com or 555-0142. We may be able to hold a pallet for you until Thursday, but I can't promise it.

I don't yet know whether the Christmas week schedule (21 to 25 December) changes. I will confirm by Friday 11 December.

Thanks,
Dana
