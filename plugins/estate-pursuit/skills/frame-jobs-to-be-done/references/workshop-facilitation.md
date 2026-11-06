# Running a JTBD workshop

A workshop is worth running when the team has customer evidence and needs a shared job hierarchy it will use in a decision. It is not a substitute for that evidence. A workshop held without switch interviews or transcripts produces the team's existing opinions in job vocabulary, which is the ritual failure this skill warns about. Plan the session around a named decision, such as which outcomes the next roadmap addresses, and end it with that decision's inputs.

Workshop output follows the evidence rules in SKILL.md. Every statement the workshop produces cites the interview or record it came from. A statement the room believes but cannot trace is a hypothesis with the question that would test it. Scores that participants give on the customer's behalf are hypotheses too; customer ratings are evidence.

## The four methods the workshop combines

**Hiring and firing (Christensen).** Customers hire a product to make progress in a situation and fire it when something serves that progress better. Competition is every alternative hire, including doing nothing. In the morning milkshake example, the milkshake competed with other breakfast foods and with the boredom of the commute, not with another restaurant's milkshake.

**Desired outcomes (Ulwick).** A job such as "close the books at month-end" is too broad to act on, so it is broken into desired-outcome statements a customer can rate:

```text
Minimize the [time | effort | likelihood | cost] of [verb] [object] [context]
```

Examples: "Minimize the time to reconcile processor payouts to the general ledger at month-end." "Minimize the likelihood of an audit finding caused by mismatched payment records." Customers rate each outcome's importance and their satisfaction with current solutions from 0 to 10. The opportunity score is `importance + max(importance - satisfaction, 0)`. Scores of 12 or more mark important, under-served outcomes; scores below 10 mark outcomes that are already served or matter little. Score with `prioritize-work` using `--framework odi`, which flags ratings that did not come from customers.

**Situation, motivation, outcome (Klement).** "When [situation], I want to [motivation], so I can [outcome]" is the job statement format in [job statement structure](job-statement-structure-patterns.md). It also bridges to backlog work: capture-requirements turns a confirmed job and outcome into user stories with Gherkin criteria.

**Switch interviews and the forces of progress (Moesta).** A switch interview reconstructs one recent decision along a timeline: first thought, passive looking, active looking, deciding, first use. Four forces act on it. Push of the current situation and pull of the new solution favour switching; anxiety about the new solution and habit of the present resist it. A switch happens when push and pull together outweigh anxiety and habit. Teams usually invest in pull and neglect anxiety and habit. [Hire and fire criteria](hire-and-fire-criteria.md) covers how the forces show up in adoption and churn.

## Choosing a format

| Format | Use when | Minimum evidence | Output |
|---|---|---|---|
| Two hours | A job hypothesis exists and needs checking; calendars are tight | Two switch-interview summaries read in the room | Top three jobs checked against evidence, three to five outcomes each, one forces map, an owner per outcome |
| Half day | Transcripts exist but there is no shared hierarchy; before roadmap planning | Four to six switch-interview summaries | Ranked job hierarchy, scored outcomes, forces map for the top job, five to ten opportunity statements |
| Full day, or two half days | New product or segment, or a strategy reset | Six to ten transcripts plus one live switch interview | Full hierarchy, 25 to 40 outcomes with scores, forces maps for the top three jobs, 10 to 15 opportunity statements with owners |

A full day needs at least six participants: product managers, designers, engineers, and two people in customer-facing roles. The two-hour format checks a hypothesis; it is not primary discovery. Run segment-specific workshops when segments have different jobs instead of averaging them in one room. Agendas are in [`assets/workshop-agendas.md`](../assets/workshop-agendas.md).

## Workflow

1. **Name the decision** the workshop informs and its owner. Without one, recommend analysis instead of a workshop.
2. **Define the segment** by situation and job, not demographics.
3. **Recruit switchers.** Six to twelve people who switched to or away from the product, or a competitor, within the last 90 days and used both options. Older switches are reconstructions.
4. **Run the switch interviews** with [`assets/switch-interview-script.md`](../assets/switch-interview-script.md). Record with consent. Preserve transcripts through `ingest-transcript` where the project uses it, and synthesize them with `synthesize-discovery`.
5. **Send pre-work** five to seven days ahead with [`assets/pre-work-email.md`](../assets/pre-work-email.md): one-page summaries with identifying details removed.
6. **Run the agenda.** Open each block with five minutes of silent individual writing, then share in turn and cluster, so the most senior voice does not set the jobs. Invite support and engineering explicitly.
7. **Capture live** on [`assets/forces-canvas.md`](../assets/forces-canvas.md) and the outcome table, with an evidence number beside every sticky that came from a transcript.
8. **Score outcomes.** Prefer a customer survey of the outcome list after the workshop. In-room scores are labelled internal.
9. **Write opportunity statements** for the top outcomes, each with an owner and a 30-day next step.
10. **Hand off and revisit.** Send results to the next skill (below). Review the hierarchy quarterly; jobs are stable, satisfaction moves with the market.

## Handing off

| Output | Goes to |
|---|---|
| Opportunity statements and scored outcomes | `prioritize-work` with `--framework odi` |
| Top outcomes as themes and Now candidates | `build-roadmap`, outcome mode |
| Confirmed jobs and outcomes for a feature | `write-feature-spec`, then `capture-requirements` |
| Struggling moments across a journey | `map-journey` |
| Untested assumptions behind a top outcome | the research plan, with interview prompts from [applying JTBD to discovery](applying-jtbd-to-discovery.md) |

## Traps and fixes

| Trap | What you see | Fix |
|---|---|---|
| Solution mode | Jobs name features or the product | Rewrite as "the customer is trying to [verb] [object] [context]"; reject any job with a feature name |
| Demographic framing | "Enterprise customers" or "millennials" stand in for jobs | Ask what that person is trying to get done, and in which situation |
| Slogans instead of jobs | Statements anyone could sign | Break each into three to five measurable outcomes |
| One transcript | The hierarchy rests on one person | Require the evidence minimum for the format |
| Pull only | The forces map lists benefits | Give anxiety and habit equal time; reread transcripts for them |
| Scores that cluster at 8 or 9 | The team rated from its own view | Score from customer data, or label the scores internal |
| Outcomes without owners | Nothing happens after the session | Name an owner and a 30-day step for each top outcome |
| Scoring before outcomes are well formed | Scores attach to vague statements | Apply the verb test first, then score |
| The snippet wall eats the day | No time for the forces map | Timebox the wall; the forces map matters more |
| A "switcher" who never switched | Loose recruiting | Require a switch within 90 days and use of both options |

## Checking the result

- The evidence minimum for the format was in the room, and every job, outcome and force cites it or is labelled a hypothesis.
- The hierarchy has one main job and five to eight sub-jobs, or the reason it does not.
- At least 15 outcomes follow the outcome format, with scores labelled customer or internal.
- The forces map covers the top job (half day) or top three jobs (full day), with anxiety and habit filled from evidence.
- The top five opportunities have owners and 30-day next steps.
- The output reached the decision it was planned for, and the owner can name what the workshop changed. If nothing changed, say so in the readout; that is the ritual signal described in SKILL.md.
