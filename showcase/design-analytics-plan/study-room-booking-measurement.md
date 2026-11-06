---
skill: design-analytics-plan
title: Measurement plan for a library study room booking page
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: fad5d22b7b107b0a195b036d75966ded0b29433b4b996cfc2022f75bd1192841
---

## Request

We're a small library network and want to know whether people who land on our study room page actually go on to book a room, because the branch managers are deciding whether to redesign that page or just add more rooms. Can you draft a measurement plan and event list that fits our data policy? The policy and what we track today are in the attached files.

## Inputs

Run of the built `design-analytics-plan` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### current-tracking.md

#### What we track today (notes from Tomasz Reyes, web officer)

**Page views.** The analytics tool counts a page view per route category per branch per day. This has run since January 2026. Daily counts, no hourly breakdown yet.

**Study room page.** Averaged about 1,450 views a week over the last 8 weeks, but it includes staff who use the page at the desk. We have not tried to separate them.

**Bookings.** The vendor's booking system emails a weekly CSV: confirmed bookings by room, branch and day. Last 8 weeks: 212, 198, 240, 231, 205, 260, 247, 238 confirmed bookings across all branches. Cancellations and no-shows are in a separate column.

**Booking form.** The "Reserve this room" button opens the vendor's hosted form on another domain. We do not track clicks on the button. We don't know what happens after the click except the confirmed bookings.

**Open questions.** Branch managers disagree on whether rooms are fully booked at peak times (a reason to add rooms) or whether people give up before booking (a reason to redesign).

#### data-policy.md

#### Web data policy – Marlowe Valley Libraries (approved March 2026)

- The public website uses cookieless, aggregate analytics. No cookies, local storage or fingerprinting.
- No user IDs, library card numbers, email addresses or IP addresses are stored with analytics events.
- Allowed event properties: event name, route category (a fixed list: home, catalogue, study-rooms, events, account-help, other), branch code, and the hour of day (0–23, branch local time).
- Query strings, search terms, full URLs and free-text fields must not be sent.
- Cross-visit linking is not permitted. Counts are events, not people.
- Aggregated daily counts may be kept for 14 months. Raw event rows are not kept.
- Changes to tracking need sign-off from the Digital Services Lead (Imogen Ashworth) before release.
- The booking system is run by a vendor and holds confirmed bookings. It is the source of truth for bookings.

## Output

I've drafted the plan. It needs one new event, a click on "Reserve this room", and two extra columns from the vendor's export. Nothing is implemented or verified yet, and your policy requires Imogen Ashworth's sign-off before any tracking is released.

#### What the plan tells the managers

The page-or-rooms question splits into three readings:

- Visitors reach the page but few start a booking. This points to the page.
- Visitors start bookings but few finish. This points to the vendor's form or to a lack of free slots.
- Confirmed bookings fill most room-hours at peak times. This points to adding rooms.

Today you can't tell these apart. The reserve button opens the vendor's form on another domain and isn't tracked. The vendor's CSV is by day, not by hour, so peak-time fill can't be seen either.

#### What your numbers show so far

- The study room page averages about 1,450 views a week.
- Confirmed bookings over the last 8 weeks total 1,831, about 229 a week.
- That is roughly 0.16 bookings per page view. I wouldn't call it a conversion rate. Views aren't people, they include staff at the desk, and I don't know how many bookings come from the website.

#### Metrics

All three are ratios of counts. Your policy forbids cross-visit linking, so none of them counts people.

| Metric | Calculation | Source |
|---|---|---|
| Start ratio | `reserve_button_clicked` events ÷ study-rooms page views, weekly by branch | Analytics tool |
| Completion ratio | Confirmed bookings ÷ `reserve_button_clicked` events, weekly by branch | Vendor CSV and analytics tool |
| Peak-hour fill | Booked room-hours ÷ available room-hours, by hour and branch | Vendor export (hourly version needed) |

Cancellations and no-shows stay in their own column and are reported beside confirmed bookings. The vendor system is the source of truth for bookings, as your policy says.

#### Events

| Event | Trigger | Properties | State |
|---|---|---|---|
| Page view, `study-rooms` | Page load | Route category, branch code, day | Exists since January 2026 |
| Page view with hour | Same | Adds hour of day, branch local time | Proposed. I haven't checked whether your tool can add hour to existing page views. |
| `reserve_button_clicked` | A visitor activates "Reserve this room", once per activation, before the hand-off to the vendor | Event name, route category, branch code, hour | Proposed |
| Confirmed booking | Vendor records it | Room, branch, day today. Hour and booking source requested. | Exists (daily). The new columns are not confirmed. |

I left out the room name, the outbound link's URL and query string, the referrer, and any ID or cookie. They aren't on your allowed list, and the outbound link may carry a query string.

#### Checks before the data is trusted

1. In a test environment, click once and confirm exactly one event arrives at the analytics tool.
2. Load the page without clicking and confirm none arrives.
3. Double-click and tap-and-return, and record the counts. Then decide whether to suppress repeats.
4. Inspect the stored payload for anything beyond the four allowed properties, especially a URL or referrer.
5. Don't make a real booking in testing. Ask the vendor whether a test mode exists.

Until these pass, the click event is "proposed".

#### Gaps and assumptions

- **Staff traffic.** Staff use at the desk inflates views and clicks. Your policy rules out IP and identifier filtering, so I've left the exclusion method pending. Report the ratios with that caveat for now.
- **Owners.** I haven't assigned an implementation owner or a vendor contact. Tomasz Reyes holds the tracking notes but isn't named as owner.
- **Vendor.** I couldn't ask the vendor about hourly export, a booking-source column or a test mode. These are requests, not facts.
- **Targets.** None are set. I propose collecting four full weeks of click data after release as a baseline, before any redesign. The four weeks and a monthly review at the managers' meeting are proposals for you to accept or change.
- **Retention.** Daily aggregates for 14 months, with no raw rows, as your policy states.

#### Reading the results

A change in either ratio after a redesign is an observation. Traffic mix, term dates and the new tracking can all move it. Judging the effect of a redesign needs a comparison, such as one branch left unchanged, and the managers would need to choose that.

#### File

- `out/measurement-plan.md`: the full plan, with the metric definitions, event table, verification steps, ownership and review proposals shown above.

### File: measurement-plan.md

#### Study room booking: measurement plan

Status: proposed. Nothing here is implemented or verified, and release needs sign-off from Imogen Ashworth under the web data policy.

##### Decision

Branch managers are choosing between redesigning the study room page and adding rooms. The plan separates three situations:

- Visitors reach the page but few start a booking. This points to the page.
- Visitors start bookings but few finish. This points to the vendor's form or to a lack of free slots.
- Confirmed bookings fill most room-hours at peak times. This points to capacity.

##### Starting point from existing data

- Study room page views: about 1,450 a week over the last 8 weeks. This includes staff using the page at the desk, which has not been separated.
- Confirmed bookings over the same 8 weeks: 212, 198, 240, 231, 205, 260, 247, 238. The total is 1,831, an average of about 229 a week across all branches.
- Dividing the two gives roughly 0.16 bookings per page view. This is a rough ratio of counts and not a conversion rate. Page views are not people, the views include staff, and the booking source (website or other) is not known.

##### Metrics

| Metric | Calculation | Population and unit | Window | Source |
|---|---|---|---|---|
| Start ratio | `reserve_button_clicked` events ÷ study-rooms page views | Event counts, same branch, same period. Not people. | Weekly, by branch | Analytics tool |
| Completion ratio | Confirmed bookings ÷ `reserve_button_clicked` events | Counts from two systems. One person can click several times. | Weekly, by branch | Vendor CSV, analytics tool |
| Peak-hour fill | Booked room-hours ÷ available room-hours, by hour of day | Rooms per branch | Weekly, by branch and hour | Vendor export (hourly version needed) |

Exclusions and limits:

- Staff desk use inflates page views and clicks. The policy does not allow IP or identifier filtering, so the exclusion method is pending. Until then, report the ratios with that caveat.
- Cancellations and no-shows are separate columns in the vendor CSV. Count confirmed bookings and report cancellations beside them.
- Repeat visits cannot be separated, because cross-visit linking is not permitted. Both ratios describe events.
- Use branch local time for hour buckets. Treat the vendor CSV as the source of truth for bookings. Late corrections by the vendor are picked up by re-reading the latest weekly file.

##### Events

| Event | Trigger | Properties (all within policy) | Destination | State |
|---|---|---|---|---|
| Page view, route category `study-rooms` | Page load | Route category, branch code, day | Analytics tool | Exists. Daily counts since January 2026. |
| Page view with hour of day | Same | Adds hour (0–23, branch local time) | Analytics tool | Proposed. Whether the tool can add hour to existing page views is unchecked. |
| `reserve_button_clicked` | A visitor activates "Reserve this room" on the study room page, once per activation, before the hand-off to the vendor's form | Event name, route category `study-rooms`, branch code, hour | Analytics tool | Proposed |
| Confirmed booking | Vendor records a booking | Room, branch, day today. Hour of booking slot and booking source requested from the vendor. | Weekly vendor CSV | Exists (daily). Hourly and source columns not confirmed. |

Properties deliberately left out:

- Room name, the form URL and any query string on the outbound link, and the referrer. They are not on the policy's allowed list, and the outbound link may carry a query string.
- Any ID or cookie to link a click to a booking.

##### Verification before anyone relies on the data

1. In a test branch code or test environment, click the button once and confirm exactly one event arrives at the analytics tool.
2. Load the page without clicking and confirm no click event arrives.
3. Double-click and tap-and-return and record how many events arrive. Decide then whether to suppress repeats.
4. Inspect the stored payload and confirm it holds only the allowed properties, with no URL, query string or referrer.
5. Do not complete a real booking during testing. Use the vendor's test mode if one exists, and ask the vendor.

Record the destination observed and the date of each check. Until then the click event stays "proposed".

##### Retention and ownership

- Retention: daily aggregates for 14 months, with no raw rows, per policy.
- Implementation owner: pending. Tomasz Reyes holds the current tracking notes but has not been named as owner.
- Release sign-off: Imogen Ashworth.
- Vendor requests (hourly export, booking source, test mode): owner pending.

##### Baseline, targets and review

- No numeric targets are set. Targets stay pending until a baseline exists.
- Proposed baseline: four full weeks of click data after release, before any redesign. The four weeks is a proposal for the managers to accept or change.
- Proposed review: monthly, at the branch managers' meeting, with the three metrics by branch.

##### Reading the results

- A low start ratio supports redesigning the page only if the peak-hour fill is not already high.
- A high peak-hour fill at the branch points to capacity regardless of the page.
- A change in either ratio after a redesign is an observation. Traffic mix, term dates and the tracking change itself can move it. Judging the effect of a redesign needs a comparison such as a branch left unchanged, which the managers would need to choose.
