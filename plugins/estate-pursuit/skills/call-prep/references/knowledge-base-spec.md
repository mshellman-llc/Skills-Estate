# Knowledge base specification

Twelve markdown files in a `knowledge-base/` folder, one topic each. Numbered so they sort, footnoted so any one can be read alone.

The atomicity is not filing tidiness. A colleague who needs the competitive picture two months from now should not have to read the financial analysis to get it, and a future Claude session should be able to load one file instead of the whole corpus. Splitting also surfaces thin topics — if a file is three lines, that topic did not actually get researched.

---

## The files

| File | Contains |
|---|---|
| `00-INDEX.md` | The call itself, attendee table, file map, source conventions |
| `01-company-profile.md` | What they are, segments, business units, footprint, recent structural changes |
| `02-business-model-money-flow.md` | **The centerpiece.** Who pays them, contract mechanics, lifecycle, channels, working capital, the entity map |
| `03-financials-and-pressures.md` | P&L, debt and covenants, litigation, guidance, and what they can realistically say yes to |
| `04-org-and-stakeholders.md` | Every person, the read on them, who signs, who blocks, who is decisive but absent |
| `05-current-state-and-requirements.md` | The actual problem, verbatim from transcripts, plus a consolidated requirements table |
| `06-competitive-landscape.md` | Each competitor, head-to-head, the wedges, and where we are exposed |
| `07-product-and-tech-context.md` | Platforms, vendors, versions, what changed recently, integration surface |
| `08-deal-strategy.md` | Positioning, talk track, phasing, landmines, next-step options |
| `09-discovery-questions.md` | Ranked questions, plus questions **not** to ask |
| `10-assumptions-register.md` | Every inference in the corpus, with confidence and a say-it verdict |
| `11-sources.md` | Master source list, including sources treated as low confidence and why |

Rename or merge where a pursuit genuinely does not have the material. Do not pad a file to fill the slot — an honest "not enough here" is more useful than three paragraphs of filler.

---

## Footnote conventions

Typed prefixes so a reader knows the provenance class before they click:

- `[^S1]` — SEC filing, investor materials, or the company's own site
- `[^W1]` — web, news, third-party databases
- `[^I1]` — internal Estate: Slack, Drive, CRM, calendar
- `[^A1]` — assumption, always paired with an entry in the register
- `[^T1]` — call transcripts, when a pursuit leans on them heavily enough to deserve their own class

Internal footnotes need enough detail to re-find the source cold:

```markdown
[^I1]: Synthetic workshop coordinator, #sample-registration, 2030-01-10 09:00 UTC, reporting a booking issue.
[^T1]: Synthetic registration interview, source ID SYNTH-T1, created 2030-01-11.
        Transcript excerpt covers 00:02:00 to 00:05:00; no real meeting is represented.
```

Note the transcript coverage range. Partial transcripts are common, and a future reader needs to know they are not looking at the whole call.

---

## Flagging conflicts

When sources disagree, show both and rule:

```markdown
> **Synthetic conflict:** a draft lists 28 adult places and 17 child places,
> but the signed register contains 25 adult places and 15 child places, totaling 40.
> Use the signed register because it is the stated authority; retain the draft discrepancy.
```

This costs three lines and buys a great deal. A brief that quietly picks a number and gets it wrong in front of a client does more damage than one that shows the disagreement. It also protects the seller: if the client cites the other figure, they know why and can respond.

---

## The assumptions register

Its own file, and the one most likely to get read under pressure. Columns:

| ID | Assumption | Confidence | Basis | Safe to say to the client? |
|---|---|---|---|---|

Confidence bands, stated at the top of the file so they mean the same thing to every reader:

- **High** — 80% and above
- **Moderate-high** — 65 to 80
- **Moderate** — 45 to 65
- **Low** — under 45

Every inline `[ASSUMPTION]` callout in any other file carries its register ID, so a reader can jump between them.

The "safe to say" column is what makes this useful rather than decorative. Three shapes of answer:

- **"No. Not confirmed in current filings."** — the inference is load-bearing for strategy but would be a fabrication if spoken.
- **"Yes, framed as an industry norm."** — safe if presented as how the industry generally works rather than a claim about this client.
- **"It's a read, not a claim. Act on it, don't say it."** — behavioral inferences about people. Useful for how you run the room, damaging if voiced.

Close the file with two short sections that repeatedly earn their space:

**Facts commonly misstated.** Where the accurate version is easy to get subtly wrong — an end-of-sale that is not an end-of-life, a recapitalization that is not an acquisition, a divested unit someone still lists as live. Sellers get these wrong from stale memory, and being right in the room is cheap credibility.

**Things we could not verify at all.** Naming the gaps prevents a future session from assuming they were checked, and it tells the seller which questions are genuinely open.

---

## What good looks like in the strategy files

`08-deal-strategy.md` and `09-discovery-questions.md` are where research becomes usable. Research that stops at facts leaves synthesis to the seller in the car on the way over.

**Deal strategy** should carry: the single message; the two or three differentiated facts and exactly how to deploy each; a time-boxed talk track; how to read each person in the room; landmines; phasing that fits the client's actual financial position; and specific next-step options rather than "propose a follow-up."

Write the talk-track lines as **verbatim, speakable sentences**, not bullet summaries. A seller can say a sentence you wrote. They cannot say a bullet.

**Discovery questions** should be ranked in tiers, each with the question as spoken and a one-line "why this matters." Include the do-not-ask list — the topics that damage the relationship or expose an inference as a fabrication.

---

## Writing style

These files get read fast and under stress. Lead with the finding, then the evidence. Bold the number or name that matters. Use tables for anything with more than three parallel items.

Quote authorized client evidence exactly and attribute it. Keep a source locator; do not ship real quotations as reusable examples.

Where you calculate something rather than citing it, say so — "our calculation" or "derived" — so a reader knows which numbers came from a filing and which came from you.
