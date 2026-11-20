---
name: frame-jobs-to-be-done
description: "Apply Jobs-to-be-Done as product methodology: job statements, struggling moments, hire and fire criteria, the functional, emotional and social dimensions of a job, and job-thinking in place of feature-thinking. Use it in positioning, discovery, prioritization or an audit of existing JTBD work. It also spots where JTBD has become ritual. Triggers on jobs-to-be-done, JTBD, switch triggers, switch interviews, outcome-driven innovation, planning or running a JTBD workshop, and on teams that lean on feature-request lists or persona archetypes that do not drive decisions. Do not trigger for generic prioritization or research synthesis with no JTBD angle."
license: MIT
---

Before drafting, read the [build card](_shared/build-card.md) and [readout brief](_runtime/writing-diagnostics/references/registers/readout-brief.md).

# Frame jobs to be done

Read [shared workflow](references/estate/workflow.md). For rendered artifacts, read [brand policy](references/estate/brand.md).

JTBD surfaces what people are trying to accomplish, instead of treating them as a list of feature preferences or as demographic archetypes. Grounded in struggling moments and in why people adopt or abandon a product, it changes decisions. Stopped at the job-statement worksheet, it becomes ritual: teams cite it in strategy documents, run workshops, produce wall-sized artifacts, and keep building from feature requests the next quarter. This skill applies the method and says plainly when it is not helping.

Use it to apply JTBD to a discovery cycle, to replace persona-driven prioritization with job-driven prioritization, to reframe positioning around what customers hire the product to do, or to audit whether existing JTBD work drives decisions.

The worked examples in the method references illustrate reasoning; they do not establish observations about the current user, a client or a real research sample. Supply authorized research before making factual job claims. Preserve the accompanying upstream license and attribution.

## Evidence rules

Jobs come from data. Struggling moments, hire criteria, and fire criteria come from what people actually said or did. A feature request alone does not establish the underlying job.

When no research exists yet, produce candidate jobs marked as hypotheses, state what each is reasoned from, and write the interview prompts that would test them. Do not fabricate quotes, frequencies, moments, willingness to pay, or emotional motives.

Keep proposals separate from what a customer said. Preserve contradictory situations and segment differences instead of forcing one universal persona.

## Showing evidence

Record the basis for every job, moment and criterion: the interview, ticket set or record it came from, or the reasoning behind a hypothesis. Show it as a short reference, such as a superscript number, that points to one evidence list at the end. Do not print "hypothesis", "reported" or a source name beside every statement; repeated labels bury the framing. When a whole set is hypothetical, say so once at the top of the list and once in the readout. The rendered page described under Output carries the same numbers. Name jobs, personas and interviews in plain words, such as "the late-invoice job" or "the second switch interview". Job, persona and claim IDs belong in the evidence list or the source records, never as a statement's label in the readout.

## Feature lists, persona theater, and job framing

A feature-request list ("users want X, Y, Z") treats users as preference aggregators. The team builds the most-requested features and gets a product that satisfies stated preferences while missing what users were trying to accomplish. Users describe symptoms rather than solutions. Products built from those lists improve incrementally without becoming meaningfully better.

Persona theater gives demographic personas cute names and details: "Marketing Manager Maria, 35, urban, drinks oat milk lattes." The characteristics rarely correlate with what the person needs from the product. Nobody cites the posters in prioritization debates.

Job framing says people hire products to do jobs. The job is what the person is trying to accomplish, independent of who they are or which features they request. It surfaces struggling moments (when people feel pulled toward an alternative), hire criteria (why they adopt) and fire criteria (what makes them switch away). Product decisions then rest on motivation instead of description.

The litmus test is a decision the team is already debating. "Should we build feature X?" becomes "Which job would X help people do, and which job is done badly today that X addresses?" If the framing produces clearer arguments on both sides, it earns its keep. If it adds vocabulary without resolving the debate, it is ritual.

## Four mechanics

Each mechanic has its own reference with worked examples and failure modes.

The job statement reads "When [situation], I want to [motivation], so I can [outcome]." The situation is a moment, never a demographic. All three parts have to be specific or the statement drives nothing. [Job statement structure](references/job-statement-structure-patterns.md) gives worked examples and the structural failures.

Struggling moments are where the current approach breaks and the job becomes visible. Ask for the last specific time it happened; a general habit hides the moment. "Users want to be more productive" is not a struggling moment; "I lost an hour on Tuesday assembling board metrics from three dashboards because none had the slice I needed" is one. Across people these moments cluster. Each cluster is a job the market does badly. [Identifying struggling moments](references/identifying-struggling-moments.md) has the discovery prompts and the clustering method.

Hire criteria explain why people adopt a product; fire criteria explain why they leave. The two usually differ, because what wins adoption is not what prevents churn. Recent switch decisions are the richest source, since people remember the moment. The [hire and fire reference](references/hire-and-fire-criteria.md) covers surfacing both.

The three dimensions are functional (what they accomplish), emotional (how they want to feel doing it) and social (the impression they want to make on others). First drafts are usually functional only. The decision often turns on the other two. Do not force all three onto a job that is genuinely functional; add the emotional and social ones only where evidence supports them or where they are marked as hypotheses. The [dimensions reference](references/functional-emotional-social-dimensions.md) explains why functional-only framing fails.

## Where JTBD adds clarity and where it becomes ritual

JTBD earns its keep in three places. In discovery, interviews built around struggling moments and switch decisions produce richer data than interviews about feature preferences. In prioritization, "does this help people do an important job better?" cuts through the politics of feature-request ranking. In positioning, jobs describe the product as a way to accomplish something the customer cares about instead of as a feature list.

It becomes ritual in four ways. A workshop produces a wall of job statements that no later decision references, so the workshop became the deliverable. Job statements replace personas without rigor and get treated as named characters. Every meeting opens with "what's the job?" even where the framing adds nothing, so the method becomes a tax. The organization adopts JTBD because a book or talk endorsed it and produces artifacts to show compliance while nobody decides anything with them.

If the team can show a recent decision that went differently because of the analysis, the framework is earning its keep. Vocabulary with no traceable decision behind it is ritual.

## Where to apply it

In discovery, structure interviews around recent struggling moments and real switch decisions. Gather job statements from the data afterwards, never from a whiteboard beforehand. Cluster across people, then name the jobs from the clusters. [Applying JTBD to discovery](references/applying-jtbd-to-discovery.md) covers interview structure and naming from data.

In prioritization, frame each roadmap candidate by the job it addresses, then ask which jobs the product currently does badly. That question cuts through feature-request politics better than scoring does; [the prioritization reference](references/applying-jtbd-to-prioritization.md) shows how.

In positioning, lead with the job. "Help product teams turn discovery research into decisions" is job framing; "AI-powered research synthesis with collaboration tools" is feature framing. [Job-led positioning](references/applying-jtbd-to-positioning.md) compares the two at length.

## Running a workshop

Run a workshop only when switch-interview evidence exists and a named decision will use the result. The [workshop facilitation guide](references/workshop-facilitation.md) explains the four methods a workshop combines and sets an evidence minimum for each format, from two hours to a full day. It also covers the workflow, the destination of each output and the traps to avoid. The agendas, the switch interview script, the forces canvas and the pre-work email are in `assets/`. Score desired outcomes with `prioritization --framework odi`; ratings that participants give on the customer's behalf stay labelled internal.

## Related skills

`synthesize-discovery` turns raw interviews and transcripts into structured findings, and job statements are one of its outputs; this skill is the bar those statements are held to. `map-journey` lays a job across phases: the Goal lane of a journey map is the job at that phase, struggling moments land where the emotional curve drops, and fire criteria often sit in the final phase where a person decides whether to come back. Handle evidence the same way in both: each item carries a short reference to its source or hypothesis entry in one shared evidence list. `write-feature-spec` takes jobs as input to specifications; its detailed UI and API specification mode covers implementation detail. Positioning and brand work use the job framing but do not replace creative direction. Other strategy frameworks, such as Wardley mapping, North Star metrics, and OKRs, are out of scope.

## Common failure modes

Eleven failures, with diagnoses and cures, are in [common JTBD failures](references/common-jtbd-failures.md). Four account for most of them. "We ran the workshop but nothing changed" means the analysis never happened after the workshop. "Our job statements all sound the same" means they are not grounded in specific moments; re-ground them in interview data. "Our jobs read like feature requests" means the statement names the product ("When using product X, I want feature Y") instead of what the person was trying to accomplish without it. "We cannot agree on the job" usually means different segments have different jobs; surface the split instead of averaging it away.

## The audit: 12 checks

Walk these when applying JTBD or reviewing someone's JTBD work.

1. Job framing in place of a feature list or persona theater.
2. Situation, motivation, and outcome all specific.
3. Grounded in specific recent struggling moments.
4. Hire criteria identified.
5. Fire criteria identified, and different from hire criteria.
6. All three dimensions surfaced where they matter and where evidence supports them.
7. Jobs derived from data, not from a workshop; hypotheses identified in the evidence list.
8. Applied where it earns its keep, not everywhere.
9. Segment differences surfaced rather than averaged.
10. Each major decision traceable to the analysis.
11. Vocabulary not substituted for analytical work.
12. Honest about where the framing does not help.

## Output

Return the job framing that would change a decision, what it implies for that decision and the research questions that remain. If the framing only restates an existing feature list, simplify it and say so.

Save the readout as Markdown; its evidence list is the record of sources. Render the same content as one self-contained HTML page, named like the Markdown file with `.html`. Build it from the `build-roadmap` components so the evidence numbers, layout and brand match the Markdown; [rendering with roadmap components](references/rendering-with-roadmap-components.md) maps each output to a component. The builder applies the project's confirmed brand profile through [brand-renderer](_runtime/brand-renderer/WORKFLOW.md) when the task supplies one, and the neutral profile otherwise. The page shows the job statements, the struggling moments, the criteria behind each hire or fire, what the framing means for the decision and the evidence list. It states nothing the Markdown does not.

## Release gate

Apply [the release gate](_shared/release-gate.md) to the Markdown and the page before delivery. Run `writing` on both, reviewing the page on its extracted text with its file review procedure and the `writing-diagnostics` checker. Run brand-renderer's parity, brand and visual gates on the page, then `review-deliverable` on both files. Until these checks pass for both, the readout is not final.

`scripts/jtbd_framing_selftest.py` checks that every reference is cited and substantive and that the ritual section and the audit remain.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
