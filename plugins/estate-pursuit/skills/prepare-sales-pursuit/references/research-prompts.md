# Research subagent prompts

Two agents, spawned in the same turn. Fill the `{{SLOTS}}` and send both at once.

Both prompts end with the same output contract. That block is doing more work than it looks like — agents cite inconsistently and blur inference into fact unless asked explicitly, every time. Keep it if you edit anything else.

Expect large returns. Have the agents return raw markdown as their final message, then write it to disk and read it from there rather than holding it in the conversation.

---

## Agent A — the business and the money flow

```
Research {{COMPANY}} ({{TICKER_OR_"private"}}) — {{ONE_LINE_WHAT_THEY_DO}}. Use WebSearch and
WebFetch extensively. Today is {{DATE}}. I need CURRENT information.

Return a detailed, heavily-cited research brief covering:

1. Corporate profile: HQ, employee count, fiscal year end, facility and country count, ownership
   or ticker, and — if public — the stock price trajectory over the last three years, quantified.

2. Business segments and units: reporting segments versus internal business unit names, what each
   does, revenue splits where disclosed. I have heard these unit names internally: {{UNIT_NAMES}}.
   Confirm, correct, and tell me which ones no longer exist.

3. HOW THEY MAKE MONEY — the money flow. This is the most important section.
   Document every entity in the chain and how cash moves:
   - Who are their customers? Name specific customers disclosed in filings, with concentration
     percentages. Who is the largest and has that changed?
   - Do they sell direct, through intermediaries, through distributors and dealers, or all three?
   - What is the contract instrument? How does an order actually arrive?
   - Pricing mechanics: how is price set at the start, and what changes it over the life of the
     deal? Look specifically for escalators, price-downs, rebates, givebacks, cost-sharing
     obligations, pass-through clauses, and anything that transfers cost risk to them.
   - Where does revenue leak, and where do they carry cost ahead of revenue?
   - Which legal entities book revenue and hold assets? Where are the treasury vehicles?
   - Working capital: stated payment terms versus actual DSO, and what explains any gap.

4. Key business processes: the end-to-end lifecycle from first customer contact to cash, as it
   works in this industry. Where does it commonly break?

5. Financial health and recent news, last 24 months: revenue, margins, net income, impairments,
   debt and leverage, covenant amendments or waivers, restructuring, dividend changes,
   leadership changes, litigation, activists, layoffs, closures, analyst commentary.
   Be specific with numbers and dates.

6. Technology stack signals: any public evidence of ERP, PLM, CRM, integration middleware, or
   digital transformation initiatives. Say clearly where there is no evidence.

7. Strategic priorities: what management actually says they are focused on. Quote them verbatim
   where you can, with the date and venue.

Prioritize primary sources: SEC filings, investor relations pages, earnings call transcripts, the
company's own site. Use news for recent events.

CRITICAL OUTPUT REQUIREMENTS:
- Every factual claim needs an inline source URL right next to it.
- Where you cannot verify something and are relying on general industry knowledge, label it
  [INDUSTRY ASSUMPTION] and explain the basis.
- Where sources conflict, say so explicitly and say which one to use and why.
- Be exhaustive on the money-flow section. I need to be able to draw a diagram of entities and
  cash flows from your output.
- Return raw structured markdown. Do not write files. Your final message IS the deliverable.
```

**Slot notes.** `{{UNIT_NAMES}}` should come from the internal harvest — transcripts and Slack routinely surface internal names that never appear in filings, and asking the agent to reconcile them catches units that were divested years ago. If you have no internal names, drop that sentence rather than inventing them.

---

## Agent B — the people, the competitors, the product landscape

```
I have a sales call on {{DATE}} with {{COMPANY}} and {{PARTNER_ORG_IF_ANY}}. I need profiles of
everyone and the competitive landscape. Use WebSearch and WebFetch. Today is {{DATE}}.

Part A — {{COMPANY}} people. Find role, tenure, background, and any public quotes, talks, or
articles for each:
{{ATTENDEE_LIST_WITH_EMAILS_AND_ANY_LINKEDIN_URLS}}

For attendees where I only have an email address, search for likely matches at the company and
report who they most probably are with an explicit confidence level. If you cannot identify
someone, say so plainly rather than guessing.

Also find: the current CEO, CFO, and the executive who owns the function this deal touches. When
were they appointed? Has there been recent turnover, and how much?

Part B — {{PARTNER_ORG_IF_ANY}} team. {{PARTNER_ATTENDEES}}. Find their roles, what they are
compensated on, and their specialties.

Part C — competitors. These firms are competing for this deal: {{COMPETITOR_LIST}}.
For each: size, revenue, headcount, revenue per head, HQ, delivery model and where staff actually
sit, partner tier or certifications, verified project counts versus claimed, notable clients,
public reviews, ownership and any PE involvement, and their productized offerings.
Read what each one actually sells — find the specific product or accelerator they lead with, and
assess whether it applies to this client's situation.
Then compare them to {{OUR_POSITIONING}}.

Part D — product and platform context. Give me factual grounding on:
{{PRODUCTS_PLATFORMS_VENDORS_IN_PLAY}}
For each: what it is, current status, any renames, end-of-sale or end-of-life dates, ownership
changes or acquisitions, migration paths, and known implementation risks as of {{YEAR}}.
Pay particular attention to anything that has changed since {{WHEN_CLIENT_LAST_EVALUATED}} —
the client may be working from a stale mental model.

CRITICAL OUTPUT REQUIREMENTS:
- Inline source URL next to every factual claim.
- Label anything unverified as [ASSUMPTION] or [UNVERIFIED] with a confidence level and your
  reasoning.
- If you cannot find a person or fact, say so explicitly rather than guessing. A clear "not found"
  is more useful to me than a plausible fabrication.
- Note that LinkedIn profile pages are usually blocked to automated retrieval. Where you rely on
  data brokers, say so and flag that titles may lag by 6 to 18 months.
- Return raw structured markdown. Do not write files. Your final message IS the deliverable.
```

**Slot notes.**

`{{WHEN_CLIENT_LAST_EVALUATED}}` is often the highest-yield slot in either prompt. If a transcript mentions the client looked at something three or four years ago, ask what changed since. Vendor acquisitions, end-of-sale announcements, and renames in that window are exactly the material competitors have not raised.

`{{PRODUCTS_PLATFORMS_VENDORS_IN_PLAY}}` should include anything named anywhere in the internal harvest, including offhand Slack mentions. A one-line "X + Y?" message is worth researching — it usually means someone on the team had an instinct they did not have time to check.

---

## A third agent, when warranted

Two agents cover most pursuits. Add a third when:

- **The pursuit is technical enough that architecture decides it.** Have the third agent research the specific integration surface: what connectors exist, what the API surface looks like, what has been deprecated, what the realistic path is. This is where questions no competitor will ask come from.
- **There is a regulatory, compliance, or standards layer.** Certification regimes, industry standards, upcoming enforcement deadlines. Clients are usually relieved when someone understands their compliance obligations without being told.
- **The client is in an industry you have no pattern for.** Ask for the industry's operating model, common systems landscape, and where quote-to-cash or the relevant process typically breaks.

Do not add a third agent just to be thorough. Each one adds wall-clock, and a vague brief is worse than a shorter sharp one.
