<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->

Before drafting, read the [build card](../../_shared/build-card.md) and [readout brief](../../prose-pass/references/registers/readout-brief.md).

# Capability mapping method

Read [shared workflow](estate/workflow.md). For a rendered or branded artifact, read [brand policy](estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

A business capability is something the organization can do, named as a stable noun phrase such as "Order management" or "Field inventory management". A capability map is the hierarchy of those capabilities for one business. This method builds that map from evidence, places each capability on the customer lifecycle and the strategy it serves, scores how well the organization performs it today, and ranks the gaps worth closing. The sponsor decides from the ranked gap list.

The method is stack-neutral. Systems appear as attributes of a capability, never as capabilities. A software vendor's reference capability catalog can seed the model; the vendor's platform is one supporting system among others.

## Rules that apply throughout

Write the scope before modeling: the business (the whole enterprise, one business unit, or two merging companies), the state being mapped (current, target, or both), and the decision the map supports. Example: "Combined current-state map of Northfield Climate and the acquired Pine Ridge Service, to choose the first two transformation releases."

Keep one map for a business. Every business unit contributes to the same model. Separate maps per division make cross-unit planning impossible, because the same capability appears under different names with different scores.

Rationalize each capability into a single occurrence. Account management appears once even when sales, service and finance all perform it. Record who performs it in `holders`. When two companies merge, `holders` shows which company had the capability before the merger. Comparing holders exposes capabilities both companies perform and capabilities only one of them had.

Name what the business can do. A capability is a noun phrase that stays true when the process, the team or the system changes. "Quote approval workflow in the CPQ tool" is a process on a system; the capability is "Quote management". Test each name with two questions: would it survive a reorganization, and would it survive replacing the system? If either answer is no, rename it or move the detail into `definition`, `systems` or a process map.

Include manual capabilities. A capability performed in spreadsheets or by one experienced person is still a capability. Leaving it out hides a gap the transformation may need to close.

Source every score. Each maturity score, target and impact rating carries an evidence basis: observed (system records, data quality checks, built behavior), reported (what a stakeholder said in an interview or workshop), or hypothesis (reasoned without stakeholder evidence). Observed and reported entries cite at least one evidence item. Use `null` for a value nobody has supplied; the outputs show it as `OPEN` and list it for follow-up. Never fill an unknown score to complete a heatmap.

Distinguish the computed ranking from the decision. The bundled script ranks gaps by a stated formula. Stakeholders may decide otherwise. Record their decision in `priority_override` with its reason and source; the outputs show both.

Use plain language on client-facing surfaces. Capability IDs, level numbers and method labels stay off them unless the client uses them.

## Capability, process and experience

Use these three views together and keep them separate in the model.

| View | Question it answers | Example for an online order |
| --- | --- | --- |
| Capability | What can the organization do? | Order management |
| Process | How does it do it, step by step? | Validate cart, reserve stock, take payment, release to the warehouse |
| Experience | How does the customer perceive the interaction? | Was it easy to choose the options I wanted and reach checkout? |

A capability is delivered by one or more processes and felt through one or more experiences. When a request is about steps, route the detail to `process`. When it is about one actor's perception across touchpoints, route it to `journey-mapping`. Link to those artifacts from the capability rather than copying their content into it.

## Decomposing the hierarchy

Use up to three levels:

1. Level 1 domain: a broad area such as Marketing, Sales, Service, Supply chain or Finance. Domains group capabilities for reading; they are not scored.
2. Level 2 capability: the unit that is scored, placed on the lifecycle and linked to strategy, such as "Audience segmentation and activation".
3. Level 3 capability: a child of a Level 2 capability, used only where the Level 2 score hides a real difference. Example: under "Procurement", "Supplier onboarding" is mature while "Contract compliance" is not.

Stop decomposing when a child would describe process steps or when nobody can score it separately. A parent with Level 3 children takes no score of its own; the outputs show its children's scores.

## Deriving capabilities

Use one or more of these approaches. A common combination seeds the model from a reference catalog, then validates it in interviews or the workshop.

1. Discovery interviews. Meet stakeholders from each line of business (marketing, sales, service, customer success, operations, finance) one at a time. Summarize the notes into capabilities with each source cited.
2. Reference-model hypothesis. Start from an industry or vendor capability catalog and mark every inherited capability `basis: hypothesis` until the client confirms it. Record the catalog as an evidence item with its version. Paraphrase catalog definitions in the client's terms; do not copy a licensed catalog into a client deliverable without checking its terms. A catalog entry often lists the capability's functions and KPIs. Keep them in `functions` and `kpis`, reworded for the client, so the map shows how an improvement will be measured.
3. Customer lifecycle analysis workshop. Bring every line of business into one session, walk the customer lifecycle stage by stage, and derive capabilities from what each team does and needs there. The [workshop kit](workshop-kit.md) contains the agenda, board layout and question bank.

Find missing capabilities from three places: what comparable organizations or competitors can do, what reference catalogs list for the industry, and what stakeholders say the business should be able to do. Stakeholder proposals show where the business wants to differentiate, which no catalog can tell you. Record each as `status: new` with `current: 0`.

When participants describe the same capability in different words, group the notes, agree on one name and one definition, and keep the alternate names in `aliases`.

## Aligning to the customer lifecycle

Place every scored capability on the lifecycle stages where it serves the customer. The default stages are:

| Stage | What the business is trying to achieve |
| --- | --- |
| Awareness | Prospects learn the offering exists and how it could help them. |
| Acquisition | The prospect evaluates and decides to buy. |
| Onboard | The first purchase and setup go smoothly and personally. |
| Engage | The customer gets value from the offering and finds related offerings. |
| Retain and support | Problems get resolved before the customer leaves. |
| Advocacy | The customer renews, expands and recommends. |

Replace the defaults with the client's own stage names whenever it has them, for example "Design and preparation" or "Installation and setup" for an installation business. Keep the stage IDs stable once the map is shared.

A capability may sit on several stages. A capability that serves no customer stage directly, such as financial close or workforce planning, is an enabling capability; leave `stages` empty and the outputs place it in an Enabling column.

## Aligning to strategy

List the business goals the map must serve in `goals`. Take them from the client's own strategy: a V2MOM (use its methods as goals and its measures as `measure`), OKRs (objectives as goals, key results as measures), or a stated goal list from executive interviews. Cite the source of each goal.

Link capabilities to the goals they enable. Two checks follow from the links, and the script reports both:

- A goal with no linked capability means the strategy names an outcome no capability delivers. Either a capability is missing or the goal needs a different owner.
- A high-priority capability with no linked goal means the ranking rests on maturity alone. Confirm the business reason or lower its impact.

Obstacles recorded in a V2MOM can point to the dimension that needs work (people, process, data, technology or organization). Cite them as evidence on the affected capability scores.

## Assessing capabilities: map and gap

Every scored capability, whether Level 2 or a Level 3 child, gets two independent judgments. Maturity describes today's execution. Business impact describes how much the capability matters to the goals. Keep them independent: a capability can be very mature and matter little (booking rooms for internal events), or immature and decisive (spare-part inventory that leaks money every month).

### Maturity

Score current and target maturity on this scale:

| Score | Level | What it looks like |
| --- | --- | --- |
| 0 | Absent | The organization cannot do this today. Required for `status: new`. |
| 1 | Initial | Ad hoc and person-dependent; mostly manual; results vary. |
| 2 | Repeatable | Done the same way in some teams; partial tooling; data often incomplete. |
| 3 | Defined | A standard process across the business with system support and known owners. |
| 4 | Managed | Measured against targets, integrated with neighboring capabilities, data trusted. |
| 5 | Optimized | Automated where useful and improved from its own measures. |

Derive the score from five dimensions, rated red, amber or green with a reason:

- People: is the capability staffed and skilled, or are people scrambling and letting issues fall through?
- Process: is the process standard, with automation that removes manual steps, or is it cumbersome and inconsistent?
- Data: is the data the capability depends on complete, current and trusted?
- Technology: will the current tools scale as the business grows?
- Organization: is ownership clear, and is the capability delivered by one accountable structure?

A workshop may rate in red, amber and green before agreeing on numbers. The display mapping is 0 to 1 red, 2 to 3 amber, 4 to 5 green. Agree on the number with the group; do not average dimension colors into a score mechanically.

Set the target from what the goals require. A capability can rightly stay where it is when raising it would cost more than it returns, or would not change customer or employee satisfaction. A target equal to the current score is a valid decision and produces a Hold band.

### Business impact

Rate impact high, medium or low with a written reason. Consider:

- Value realization: would improving the capability help achieve and demonstrate the business value the goals name?
- Satisfaction: would it improve customer satisfaction, or employee satisfaction that carries through to customers?
- Breadth: would it improve things for the whole organization or for one small part?

Stakeholders may disagree. Collect a vote per stakeholder on the capabilities they consider most important and record the count in `votes`. Equal votes mean equal importance to different groups; keep the tie rather than breaking it arbitrarily.

### Gap and priority

The script computes these from the stored values:

- Gap = target maturity minus current maturity.
- Impact weight = 3 for high, 2 for medium, 1 for low.
- Priority score = gap multiplied by impact weight, at most 15. A target below the current score gives a negative score.
- Band: Invest now for a score of 6 or more, Plan for 3 to 5, Monitor for 1 or 2, Hold for 0 or less. A capability with `status: redundant` goes to Retire review regardless of score or missing inputs. Otherwise, any missing input makes the band `OPEN`.
- Rank orders the bands, then the score, then votes. Capabilities with the same band, score and votes share a rank.

These bands are the default. If the engagement agrees different thresholds, record them in `meta.priority_bands` and say so in the readout.

### Tracing a planned release

When a release is already planned, trace it against the map before anyone reads the ranking. Record the release in `meta.release`. For each capability, list the stories or epics that move it in `delivered_by`, with their priority and delivery status, and set `after_release` to where the release leaves the capability if its Must and Should stories ship. A release can lower a capability: when it switches off a legacy tool before its replacement is live, `after_release` is below `current`.

The trace answers what the stories alone do not:

- Which goals the release leaves short. A goal is short when a linked high-impact capability ends below target. This is the expectation the sponsor has to reset before launch.
- Which capabilities the release makes worse, so a transition plan covers them.
- Where delivery is at risk: Must and Should stories that are blocked or not yet ticketed, counted per capability.
- What comes next. The remaining gap after the release, times impact, ranks the candidates for the following release.

Give every decision an owner in `open_items`. An open decision without an owner is a finding, because the stories it blocks cannot move until someone takes it.

Transition work such as cutover runbooks and legacy removal belongs to the release plan, not to a capability. Trace it where it changes a capability's score, as with a retired forecast.

### Redundant capabilities

Gap analysis finds three things: capabilities to add, capabilities to strengthen, and capabilities performed twice. Mark a duplicated capability `status: redundant` on the occurrence that should be retired (for example, a second order-entry capability kept by the acquired company) and link the surviving capability in `definition` or `aliases`. A redundant capability stays visible until the retirement is decided.

## Workflow

1. Scope: the business, the state, the decision and the audience, written down.
2. Gather the strategy (V2MOM, OKRs or executive interview notes), discovery notes, any reference catalog, and the system inventory.
3. Draft the model: domains, Level 2 capabilities with definitions, and stages. Share it early so stakeholders correct names and definitions before anyone scores.
4. Run the lifecycle workshop or the interviews. Validate names and definitions, add missing capabilities, and merge duplicates.
5. Link capabilities to stages and goals.
6. Score current maturity, target maturity and impact with reasons, in stage breakout groups when the room is large, then review the scores with the whole group.
7. Build the outputs with the script and inspect them.
8. Walk the ranked gaps with the decision makers. Record overrides with reasons.
9. When a release is planned, trace it: stories per capability, the score after the release, and an owner for every open decision.
10. Hand the results to the skills that act on them. The build writes `handoffs.json`: run `roadmap-artifacts` on the capabilities left short after the release, `requirements-capture` on the Must and Should stories not yet ticketed, and `deck-builder` on the goals left short and the decisions needed. Send solution questions to `solution-brief` or `system-design`, process redesign to `process`, and effort and price to `scoping-agent` or `rom`.
11. Maintain the map. Rescore after a major release, a reorganization or an acquisition; keep the earlier model file as the dated baseline.

## Producing the outputs

Keep the JSON model as the single editable source; its contract is in [the model schema](model-schema.md). Build every output from it with the bundled script, run from the skill directory:

```sh
python3 scripts/build_capability_map.py build model.json --output-dir out/
```

The command validates the model, computes gaps and priorities, and writes:

- `capability-map.html`: the decision dashboard on the Baseline design system. It opens with the capabilities to invest in first, then shows the capability heatmap, the gap to target, strategy and lifecycle coverage, and the full table and evidence.
- `capability-assessment.xlsx`: the operational tracker with live formulas for gap, score and band, plus lifecycle, strategy, rubric, evidence and open-item sheets. Requires `openpyxl`; without it the command writes the other outputs and reports the workbook as not produced.
- `capability-readout.md`: the decision narrative with the top gaps, goal coverage findings, open items and validation questions.
- `model.computed.json`: the model with computed fields, for storage or handoff to another skill.
- `handoffs.json`: the inputs for `roadmap-artifacts`, `requirements-capture` and `deck-builder`, built from the release trace.

For a workshop, generate the capture workbook and a seeded model first:

```sh
python3 scripts/build_capability_map.py workshop --stages "Awareness,Acquisition,Onboard,Engage,Retain and support,Advocacy" --title "Capability workshop" --output-dir workshop/
python3 scripts/build_capability_map.py ingest workshop/workshop-capture.xlsx --model workshop/model.json --output model.json
```

`ingest` reads the filled scoring sheet into the model and refuses rows that name an unknown stage or goal. Review the merged model before building.

The output layout is described in [rendered outputs](rendered-outputs.md). Apply a confirmed project brand through [client-brand](../../client-brand/SKILL.md) when one exists; the starter uses the neutral profile. When retrieving or saving shared project records, read [knowledge-hub](../../knowledge-hub/SKILL.md) to resolve the actual local or connected storage.

## Failure patterns

- A map per division, so one capability shows up three times with three scores.
- Capabilities named after systems or teams, so the map changes at every reorganization.
- Processes listed as capabilities, so the map turns into a process inventory nobody can score.
- Only automated capabilities mapped, so the manual work the transformation has to change is missing.
- One color per capability with no reason, so nobody can tell what would turn it green.
- Every target set to 5, so every gap looks urgent and the ranking means nothing.
- Prioritizing by red alone, ignoring impact.
- A reference catalog presented as the client's confirmed map.
- A heatmap filled with guessed scores to look complete.
- Gaps identified and never handed to a roadmap or backlog.
- A map built after the release is scoped that only restates the stories. Trace the release instead and report what it leaves short.

## Before shipping

Follow the [release gate](../../_shared/release-gate.md). Reconcile every score and goal link with the evidence list; a governed client engagement also runs [evidence-core](../../evidence-core/SKILL.md) against its ledger. Confirm the readout's figures match the computed model. Open the HTML and the workbook and inspect them. Review the prose with `writing-integrity`. Run `brand-renderer` on styled output with the brand resolved above. Run `quality-gate`; do not call the map final until every applicable check passes. Route any price or effort question to `scoping-agent` or `rom`.

`scripts/capability_mapping_selftest.py` checks that this method, its references and the starter still carry the scales, bands, outputs and failure handling described here.
