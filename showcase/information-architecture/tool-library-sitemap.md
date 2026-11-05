---
skill: information-architecture
title: Navigation and sitemap for a community tool library website
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 6ebd0a149d475ccda8664a397b49ae94b9470a120f0c605d63459c9f6446e6e3
---

## Request

Our tool library's website has grown messy and members keep emailing us to ask things they should be able to find themselves. Can you propose a new navigation and sitemap from the inventory and notes I've attached? We'd like to keep our existing URLs if we can.

## Inputs

Run of the built `information-architecture` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### current-site.md

#### Current site: Fernbank Tool Library (example.com/fernbank)

Top navigation today: Home | About Us | Our Stuff | Members | Get Involved | News | Contact

| Page | URL | Current parent | Notes |
|---|---|---|---|
| Home | / | – | Hero photo, latest news |
| About Us | /about | Top | Mission, history |
| Our Team | /about/team | About Us | Staff and volunteers |
| Opening Hours | /about/hours | About Us | Hours for both sites |
| Find Us | /about/find-us | About Us | Maps, parking, step-free access |
| Our Stuff | /catalogue | Top | Searchable catalogue, 1,100 items |
| Tool Categories | /catalogue/categories | Our Stuff | Garden, Wood, Electrical, etc. |
| Workshop Kits | /catalogue/kits | Our Stuff | Bundled loan kits |
| Join | /members/join | Members | Sign-up form, fee table |
| Membership Fees | /members/fees | Members | Duplicate of fee table on Join? (not compared) |
| Borrowing Rules | /members/rules | Members | Loan length, late fees, damage policy |
| My Account | /members/login | Members | Login, renewals, reservations |
| FAQ | /faq | Top (footer only) | 42 questions in one list |
| Skills Workshops | /events/workshops | Get Involved | Booking links |
| Repair Café | /events/repair-cafe | Get Involved | Monthly |
| Volunteer | /get-involved/volunteer | Get Involved | Role list, form |
| Donate Tools | /get-involved/donate-tools | Get Involved | What we accept |
| Donate Money | /get-involved/donate | Get Involved | |
| News | /news | Top | 60 posts, mostly 2022–2024 |
| Contact | /contact | Top | Form only, no phone or email shown |
| Accessibility statement | – | – | Does not exist yet |

#### notes.md

#### Notes from the coordinator

Last quarter's enquiry emails (about 90, hand-tallied):
- 31: "Can I borrow X?" or "do you have X?" (people didn't find the catalogue search)
- 22: opening hours or which site to go to
- 14: how much membership costs / how long I can keep things
- 9: "can I donate my dad's tools?"
- 8: how to book a workshop
- 6: wheelchair access
Rest: miscellaneous.

Audiences: current members (borrow, renew, reserve), prospective members (cost, how it works), donors and volunteers, and a few schools and local groups who ask about group bookings. No analytics available; no user research done.

Constraints:
- Two sites: Fernbank (main) and Lowmoor (open Saturdays only).
- Name "Repair Café" and "Workshop Kits" are established; keep them.
- Volunteers keep the site in a basic CMS; URL changes are painful, and external links from the council website point at /catalogue and /members/join.
- Group bookings (schools) have no page today.

## Output

### Fernbank Tool Library: proposed navigation and sitemap

I propose six top-level groups built around what members and visitors ask you about, and every current URL stays as it is. Only the navigation labels and groupings change, so the council links to `/catalogue` and `/members/join` keep working and no redirects are needed. The structure is provisional. You have no analytics or user research, so it rests on your enquiry tally and the page inventory, and the validation plan at the end covers what to test.

#### What the structure responds to

Your 90 enquiries break down like this:

| Question | Emails | Where it is answered today | Problem |
|---|---|---|---|
| Do you have X / can I borrow X | 31 | `/catalogue`, under "Our Stuff" | The label doesn't say "borrow" or "search" |
| Opening hours, which site | 22 | `/about/hours`, under "About Us" | Visitors don't look for practical visit info under "About" |
| Cost, loan length | 14 | `/members/fees`, `/members/rules` | Under "Members", which reads as a member-only area |
| Donating tools | 9 | `/get-involved/donate-tools` | Two clicks deep, behind a generic label |
| Booking a workshop | 8 | `/events/workshops` | Filed under "Get Involved" |
| Wheelchair access | 6 | `/about/find-us` | Buried in a map page; no accessibility statement |

Prospective members, current members, donors/volunteers and group organisers have different goals, so the groups follow tasks rather than your internal teams.

#### Proposed primary navigation

Header, left to right: **Borrow | Membership | Visit us | Workshops and repairs | Support us | About** — plus utility links on the right: **Search**, **Log in**, **Contact**.

| Group | Purpose | Contents (URL unchanged) |
|---|---|---|
| **Borrow** | Find out whether we have a tool and how to get it | Search the catalogue `/catalogue` · Browse by category `/catalogue/categories` · Workshop Kits `/catalogue/kits` |
| **Membership** | Decide to join, then understand the terms | Join `/members/join` · Fees `/members/fees` · Borrowing rules `/members/rules` · FAQ `/faq` |
| **Visit us** | Plan a trip to Fernbank or Lowmoor | Opening hours `/about/hours` · Find us and step-free access `/about/find-us` · Accessibility statement (new, no URL yet) |
| **Workshops and repairs** | Learn a skill or fix something | Skills Workshops `/events/workshops` · Repair Café `/events/repair-cafe` · Group bookings (new, no URL yet) |
| **Support us** | Give tools, time or money | Donate tools `/get-involved/donate-tools` · Volunteer `/get-involved/volunteer` · Donate money `/get-involved/donate` |
| **About** | Background on the library | About us `/about` · Our team `/about/team` · News `/news` |

Utility links: **Log in** goes to `/members/login` (My Account, covering renewals and reservations), **Contact** to `/contact`, **Search** to the catalogue search.

##### Reasons for the less obvious choices

- **"Borrow" replaces "Our Stuff".** The 31 "do you have X" emails suggest people don't recognise "Our Stuff" as the place to search. "Borrow" names the task. The catalogue keeps its established URL.
- **Fees and rules sit under "Membership", not "Members".** Prospective members ask about cost and loan length before they join, so these pages need to read as public.
- **My Account moves out of the menu into a "Log in" utility link.** Current members use it as an action, not a place to browse. It still has its own URL.
- **Opening hours and access move into "Visit us".** That takes the 22 hours enquiries and 6 access enquiries out of "About". `/about/hours` and `/about/find-us` keep their paths, so the label and the URL will disagree. That is acceptable for now; renaming the URLs later would need the redirect work described below.
- **Workshops and Repair Café are one group.** Both are events a visitor books or attends. The names "Repair Café" and "Workshop Kits" are kept as established. Kits stay under Borrow because they are loaned items, not events. Add a line on the Kits page pointing to workshops that use them, if any do (I have no information on that).
- **"Get Involved" is renamed "Support us" and no longer holds events.** Events are an activity for members and the public, not a way of giving support.
- **News moves under About.** Its 60 posts are mostly 2022–2024, so it doesn't earn a top-level slot. It stays reachable from the home page for recent items.

##### Page-level and contextual links

These do a different job from the menu, so they are not extra menu items:

- Home page: a catalogue search box above the fold, and four quick links — Opening hours, Join, Donate tools, Book a workshop. These cover about 75 of the 90 enquiries.
- Join, Fees and Rules link to each other in a "Membership" side list.
- Each catalogue category and item page shows "How borrowing works" (link to `/members/rules`) and which site holds the item, if the catalogue records that.
- The footer repeats the primary groups and adds Contact, FAQ, Accessibility statement and a Lowmoor/Fernbank hours summary.

#### Representative paths

| Task | Path | Clicks from home |
|---|---|---|
| Check whether you have a mitre saw | Home search box → results (or Borrow → `/catalogue`) | 1–2 |
| Find Saturday opening hours for Lowmoor | Visit us → Opening hours | 2 |
| Learn what membership costs | Membership → Fees | 2 |
| Donate a late relative's tools | Support us → Donate tools | 2 |
| Book a workshop | Workshops and repairs → Skills Workshops | 2 |
| Check step-free access | Visit us → Find us and step-free access, or Accessibility statement once written | 2 |
| Renew a loan | Log in → My Account | 2 |
| A school asks about a group visit | Workshops and repairs → Group bookings (page needed) | 2 |

These are paths in the proposal, not results from users.

#### Current-to-proposed map

No URL changes. Redirects and internal link updates are not required for this proposal. The only link work is editing menu labels and groupings in the CMS, and the home-page quick links.

| Current URL | Current placement | Proposed placement |
|---|---|---|
| `/` | Home | Home |
| `/about` | About Us | About |
| `/about/team` | About Us | About |
| `/about/hours` | About Us | Visit us |
| `/about/find-us` | About Us | Visit us |
| `/catalogue` | Our Stuff | Borrow |
| `/catalogue/categories` | Our Stuff | Borrow |
| `/catalogue/kits` | Our Stuff | Borrow |
| `/members/join` | Members | Membership |
| `/members/fees` | Members | Membership |
| `/members/rules` | Members | Membership |
| `/members/login` | Members | Log in (utility link) |
| `/faq` | Footer only | Membership, plus footer |
| `/events/workshops` | Get Involved | Workshops and repairs |
| `/events/repair-cafe` | Get Involved | Workshops and repairs |
| `/get-involved/volunteer` | Get Involved | Support us |
| `/get-involved/donate-tools` | Get Involved | Support us |
| `/get-involved/donate` | Get Involved | Support us |
| `/news` | Top | About |
| `/contact` | Top | Utility link |

#### Content gaps that affect the paths

1. **Accessibility statement.** It doesn't exist, and 6 enquiries concerned wheelchair access. Until it is written, the Visit us path depends on the step-free information on `/about/find-us`. I haven't seen that page's content, so I can't say whether it covers both sites.
2. **Group bookings page.** Schools and local groups have no page. The group is placed in the menu on the assumption that the page will be written; if it isn't, drop the item rather than link to nothing. Its URL should be chosen under `/events/` to match the established convention, for example `/events/group-bookings`.
3. **Contact page shows a form only.** Visitors who can't find an answer have no phone or email. Add the library's contact details, and consider showing them beside the hours.
4. **Fees may be duplicated.** `/members/fees` and the fee table on `/members/join` were not compared. Check whether they match before deciding to merge; if they do, keep both URLs and have one link to the other, since the council links to `/members/join`.
5. **FAQ is one list of 42 questions.** I haven't seen the questions, so I haven't regrouped them. Group them by the headings above (Borrowing, Membership, Visiting, Donating, Workshops) and link relevant questions from each section's pages.
6. **Lowmoor information.** Confirm that the hours page and catalogue make clear which site is open when and which holds an item. The inventory doesn't say.
7. **News.** Decide whether to archive posts older than 2024 behind a year filter. This changes no URLs.

#### Validation plan

Nothing here has been tested with people, so treat the groupings and labels as a draft. The main uncertainties and the method for each:

| Uncertainty | Method | Participants |
|---|---|---|
| Does "Borrow" and "Membership" lead people to the right place, especially for cost and rules? | Tree test of the hierarchy above with goal-based tasks | 15–20 mix of members and non-members, including some who emailed you |
| Is "Support us" clear for donors, and "Workshops and repairs" clear for the workshop booking? | Same tree test | As above, plus a few people from schools or local groups |
| Does the home page search box get used as the first click? | First-click test on a mock-up of the home page | As above |
| Are there items (for example Kits) that people expect elsewhere? | Open card sort of the 20 page titles | 8–10 people, if you want to challenge the groupings |

Suggested tree-test tasks, each with one target page: find what a year's membership costs (`/members/fees`); find out whether you can borrow a tile cutter (`/catalogue`); find when Lowmoor opens (`/about/hours`); offer your late father's tools (`/get-involved/donate-tools`); check whether a wheelchair user can reach the Fernbank workshop (`/about/find-us`); renew a loan (`/members/login`); ask about a class visit (group bookings, once it exists). Record the path each participant took and success counts, and report the small sample size with the results. A sample this size shows where labels fail; it doesn't give a reliable percentage.

A cheaper check before testing: after the menu change, tally enquiry emails again over the next quarter. The "do you have X" and "opening hours" counts (31 and 22) are the ones to watch, though this is an indirect signal and other factors will affect it.

#### Files

No file was produced; the full proposal is above.
