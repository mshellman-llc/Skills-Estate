# Customer lifecycle and capability workshop kit

The customer lifecycle workshop gathers several lines of business in one room, or one shared board, to describe how the business serves its customers stage by stage. It surfaces goals, challenges, touchpoints, stakeholders and systems for each team, and produces the raw material for the capability model and its scores. Run it after the strategy goals are known and before the map is scored.

## Prepare

- Confirm the decision the map supports and the executive who will act on it.
- Invite one or two people from each line of business along the lifecycle: marketing, sales, service, customer success, operations and finance, plus the person who owns the main systems. When the room is too large for one conversation, plan breakout groups by stage from the start.
- Collect the goals in advance (V2MOM, OKRs or executive interview notes) and print or pin them where everyone can see them.
- Agree the lifecycle stage names with the sponsor. Use the client's own terms when it has them.
- Prepare a draft capability model if a reference catalog or earlier interviews exist. Mark every entry as a hypothesis.
- Generate the capture workbook: `python3 scripts/build_capability_map.py workshop --stages "..." --title "..." --output-dir workshop/`. Copy its Lifecycle board sheet to a whiteboard tool if the session is remote.

## Board layout

Write the lifecycle stages across the top. Down the side, use these rows:

| Row | What participants write |
| --- | --- |
| External activities | What the customer does at this stage. |
| Internal activities | What each team does at this stage, including manual work. |
| Goals | What each team is trying to achieve here. |
| Pains | What goes wrong, for the customer or for the team. |
| Opportunities | What would make this stage better. |
| Stakeholders | Who is involved, internally and externally. |
| Systems | Tools used, including spreadsheets and email. |
| Capabilities today | What the business can do at this stage. |
| Capabilities needed | What the business should be able to do and cannot. |

## Agenda for a half-day session

| Time | Activity | Output |
| --- | --- | --- |
| 0:00 | Sponsor opens: the goals and the decision this work feeds. | Participants know the goals and the decision. |
| 0:15 | Walk the lifecycle stages and agree their boundaries. | Stage list with start and end events. |
| 0:30 | Teams fill the board rows stage by stage, external activities first. | Filled board. |
| 1:30 | Break. Facilitator groups similar capability notes. | Grouped notes. |
| 1:45 | Agree capability names and definitions; merge duplicates; add missing ones. | Draft capability model. |
| 2:30 | Score maturity on five dimensions and impact, with reasons. A large room splits into its stage breakouts. | Scoring sheet rows. |
| 3:15 | Read the scores back; the whole room adjusts them. | Agreed scores. |
| 3:45 | Each participant votes for the capabilities they consider most important. | Votes per capability. |
| 4:00 | Close: next steps, owners for open items. | Open item list. |

For a remote or larger group, split this into two sessions: the board and capability naming in the first, scoring and voting in the second. The gap between them gives the facilitator time to clean the model.

## Facilitation notes

- Start with external activities, so each team places its own work on the customer's path.
- Keep systems on the Systems row. When someone names a tool as a capability, ask what the tool lets the business do, and write that.
- When two teams describe the same capability differently, write both, then agree one name and keep the other as an alias.
- Score maturity and impact separately. For impact, ask what changes for the goals if the capability improves.
- Ask for the reason behind every color. "Red because parts are tracked in three spreadsheets and nobody trusts the counts" gives the team something to fix; a bare "red" gives it nothing.
- Let ties stand in the vote. Equal votes mean different groups care equally.
- Capture the session in a transcript or notes, and cite it as evidence (`type: workshop`).

## Question bank

### Discovering capabilities, by stage

- Awareness: How do prospects first hear about you? How do you decide whom to target and with which message? How do you know a campaign worked?
- Acquisition: How does a prospect compare you with alternatives? Who prepares quotes or proposals, and how long does it take? Where do deals stall?
- Onboard: What happens between signature and first value? Who sets the customer up, and what do they need from the customer? What usually goes wrong in the first month?
- Engage: How do you learn what each customer uses and needs next? How do you offer related products? Who owns the relationship after onboarding?
- Retain and support: How does a customer get help? How do you spot a customer at risk of leaving? Which parts, people or information do your service teams wait for?
- Advocacy: How do renewals and expansions happen? How do you ask satisfied customers for referrals or reviews, and how do you thank them?
- Enabling: Which back-office work would stop the customer stages if it failed: billing, finance, inventory, workforce, compliance?

### Finding missing capabilities

- What can your strongest competitor do that you cannot?
- If you doubled the business next year, what would break first?
- What do customers ask for that you have to refuse or handle by exception?
- Which work depends on one person who knows how to do it?

### Scoring maturity

- People: Is the capability adequately staffed and skilled, or are people scrambling and letting issues fall through?
- Process: Is there a standard process with automation that removes manual steps, or a lot of cumbersome manual work?
- Data: How reliable is the data this capability depends on? Who would notice if it were wrong?
- Technology: Will the tools used today scale as the business grows?
- Organization: Who is accountable for this capability end to end?

### Rating impact

- How much does improving this capability move the business toward the goals on the wall?
- Would customers or employees notice the improvement?
- Does it help the whole organization or one team?
- What does the current gap cost, and who has measured it?

## After the workshop

1. Type the agreed names, definitions, scores, reasons and votes into the Scoring sheet of the capture workbook, one row per capability.
2. Run `ingest` to merge the sheet into the model, then add the goal list, the evidence items and any stage or goal links the sheet left blank.
3. Build the outputs and send the draft readout to participants to check their scores and reasons.
4. Record corrections, set `meta.status` to `validated` when the sponsor accepts the scores, and rebuild.
