# Template catalog

Each template is a recipe for a plan JSON. Pick the template, gather its inputs, fill the blocks listed, then write the follow-up analysis in chat after the roadmap. The source prompts asked for "one self-contained HTML file with inline CSS". That requirement is replaced by the kit: output is a plan rendered by the shared components in the org's theme, on whatever target the user needs (`SKILL.md`, Targets). The visual design never changes between templates. Only the blocks and data do.

Shared rules for every template:

- Fill every column, lane and phase with specifically named work derived from the inputs. Never leave placeholders for the work itself. Owners may be `"TBD"`.
- Tie every card or bar to a measurable outcome, metric or exit criterion.
- If the user did not give an input, infer a realistic value, say so in `meta.source`, and list the inferred inputs in the follow-up.
- When the work already lives in a tool (Sheets, Linear, Jira, Asana, Notion), read it from there instead of asking for it, and record it in `meta.sources`. See `connectors.md`.
- Example ids below match `examples/`.

## Product & engineering

### 1. `product-now-next-later`: Product roadmap (Now / Next / Later)
Role: senior product manager who builds clear, opinionated roadmaps.
Inputs: product and stage; north-star goal for the period; known initiatives or asks; team capacity and squads; hard dates or constraints; themes.
Blocks: `board` with columns `now`, `next`, `later`. Legend = themes. Cards: title, `body` = problem, `fields.Outcome` = target metric, `owner`, tags = size (S/M/L) + confidence (`good`/`warn`/`crit`). Header: `northStar` + period stat.
Follow-up: how Now was separated from Later; which two bets to cut if capacity dropped.
Outcome mode: write each Outcome as baseline → target and run `scripts/outcome_check.py`; see `references/outcome-roadmaps.md`.
Example: `examples/01-now-next-later.json`.

### 2. `quarterly-feature-timeline`: Gantt-style feature timeline
Role: product operations lead who turns plans into readable timelines.
Inputs: period; features and rough durations; dependencies; teams or owners; fixed milestones.
Blocks: `timeline` (scale `week` up to 6 months, `month` beyond), one row per feature, `deps` for every "X before Y", `milestones` for beta/GA, `markers` for the immovable date, `critical` = the critical path. Legend = teams. Add `callouts` for the slip risk.
Follow-up: the critical path in order; the one dependency most likely to slip the launch.
Example: `examples/02-feature-timeline.json`.

### 3. `tech-migration`: Tech migration / re-platform roadmap
Role: staff engineer who plans low-risk migrations.
Inputs: from → to; why now; systems affected; risk tolerance and downtime budget; team and timeframe.
Blocks: `board` (movable false) with columns `prep`, `parallel`, `cutover`, `cleanup`. Each column `subtitle` = duration + biggest risk. Cards are steps: `fields` = Rollback, Exit criterion, Verification; tags = risk tone; owner. Include expand-and-contract or strangler-fig steps where relevant and a "Go / no-go" card at the end of each phase. Header stats: downtime budget, target date.
Follow-up: the riskiest step; the cheapest test that de-risks it before cutover.

### 4. `platform-maturity`: Platform / API roadmap by maturity stage
Role: platform product lead who sequences infrastructure investments.
Inputs: platform or API; current developer pain; capabilities; consumers (internal, partner, public); horizon.
Blocks: `board` with columns `foundational`, `self-serve`, `scalable`, `ecosystem`. Legend = consumer type. Cards: title = capability, `fields` = Developer outcome, Requires, Serves. `meta.northStar` = end-state developer experience.
Follow-up: which foundational capability gates the most downstream work.

### 5. `reliability-hardening`: Bug-bash & reliability hardening roadmap
Role: SRE lead who plans reliability work leadership will fund.
Inputs: reliability pain; SLO targets; weak spots; capacity percentage; timeframe.
Blocks: `callouts` titled "Fire now" (top three), then `matrix` with rows `obs`, `res`, `perf`, `toil` (Observability, Resilience, Performance, Toil reduction) and columns by order (`first`, `then`, `later`), ranked by risk reduced per effort. Cards: `fields` = Metric improved, Effort; owner. Header `stats` = each SLO with `value` (current) and `target`.
Follow-up: a one-sentence pitch per fire-now item for a skeptical exec.

## Project & delivery

### 6. `project-delivery`: Phases and milestones
Role: delivery-focused project manager.
Inputs: goal and definition of done; start and deadline; phases; workstreams and owners; milestones; known risks.
Blocks: `timeline` with one row per phase (`owner` set), `milestones`, a `kind: "buffer"` row before every external sign-off, `markers` for the deadline. Header stats: start, deadline, duration.
Follow-up: the tightest milestone; where to add buffer.

### 7. `cross-team-swimlane`: Cross-team swimlane roadmap
Role: program manager coordinating several teams toward one launch.
Inputs: shared goal or launch; teams; deliverables per team; cross-team dependencies; timeframe and launch date.
Blocks: `timeline` with one row per team using `bars` (multi-bar swimlane), `deps` for every handoff, `markers` for the launch date. Legend = teams. `callouts` titled "Riskiest handoffs" with `ref` to the bars.
Follow-up: three handoffs most likely to cause a slip and who owns each.

### 8. `agile-release-train`: Sprint-by-sprint release roadmap
Role: agile delivery lead.
Inputs: release goal; sprint length and count; epics and sizes; velocity; fixed dates.
Blocks: `board` with `stack: false`, one column per sprint (`capacity` = velocity, dated `subtitle`, tags for demo/freeze/release), plus a `spillover` column with no capacity. Cards carry `points`. Legend = epics. Over-filled sprints turn red on their own.
Follow-up: which epic to cut or split if velocity comes in 20% lower.
Example: `examples/03-release-train.json`.

### 9. `launch-countdown`: Event / launch countdown
Role: event producer who runs tight countdowns.
Inputs: event and date; workstreams; must-hit milestones; owners; lead time.
Blocks: `timeline` with `countdown: {date, unit: "week"}`, one row per workstream with `milestones` at the week they must complete, `owner` per row. `checklist` titled "Day-of (T-0)".
Follow-up: which milestone, if missed, forces moving the event date.

### 10. `risk-aware-raid`: Risk-aware roadmap with RAID overlay
Role: delivery manager who plans for what can go wrong.
Inputs: project and phases; timeframe; risks and impact; assumptions; external dependencies.
Blocks: `timeline` with one row per phase (`heat`, `owner`, `milestones`), then `table` RAID register with columns type, item, threatens (`swatch`), severity, likelihood, mitigation, owner. Every row has `ref` = phase id and `group` = that phase's legend key. Legend = phases. No item without a phase and mitigation.
Follow-up: the mitigation that buys the most schedule safety.
Example: `examples/05-raid.json`.

## Marketing, content & GTM

### 11. `marketing-campaigns`: Multi-channel campaign roadmap
Role: head of marketing.
Inputs: goal; channels; campaigns or moments; budget weighting; timeframe.
Blocks: `meters` with one item per channel (budget weight, `max: 100`, unit "%"), then `timeline` scale `month`, one row per channel with named campaign `bars` grouped by the goal they serve, `markers` for launches and events.
Follow-up: which channel carries the launch; where the calendar is over-crowded.

### 12. `content-pillars`: Content roadmap (pillars and cadence)
Role: content strategist.
Inputs: audience and desired action; 3 to 5 pillars; formats; cadence and capacity; timeframe; key dates.
Blocks: `matrix` with rows = pillars, columns = weeks (`subtitle` = date). Cards: working title, `kicker` = format, tags = funnel stage (`TOFU`, `MOFU`, `BOFU`) + format, owner. Then `meters` with per-pillar counts. Balance pillars and stages per week.
Follow-up: the pillar and funnel balance; which week to keep if capacity is cut.

### 13. `gtm-launch`: GTM roadmap for a launch
Role: product marketing lead.
Inputs: product and date; segment and core message; functions; launch tier; success metric.
Blocks: `matrix` with columns `pre`, `week`, `post` and one row per function. Cards: concrete activity, `kicker` = launch-relative offset (L-14, L-Day, L+7), owner. `meta.northStar` = the promise; stats = metric and tier. `callouts` "Must not slip".
Follow-up: three must-not-slip launch-week activities and owners.
Example: `examples/04-gtm-launch.json`.

### 14. `startup-gtm`: Startup GTM and growth (0 to traction)
Role: startup growth advisor.
Inputs: product and ICP; current stage; channels to test; resources; traction goal and horizon.
Blocks: `board` (movable false) with columns `validate`, `channel-fit`, `repeatable`, `scale`; each column `tags` = graduation metric. Cards = experiments with `fields` = Metric, Kill if; owner. Legend = channel.
Follow-up: the single channel to bet on first; the metric that proves channel-fit.

### 15. `brand-demand`: Brand / demand roadmap by quarter
Role: marketing director balancing brand and demand.
Inputs: annual goal; brand narrative; demand programs; brand programs; quarters.
Blocks: `matrix` with columns = quarters (`subtitle` = theme, `split` = brand vs demand effort) and rows `brand`, `demand`. Cards: named program, `fields.Metric`, owner. Legend: brand and demand.
Follow-up: how the split shifts across the year and why.

## OKR & strategy

### 16. `okr-roadmap`: Quarterly OKR roadmap (objectives to initiatives)
Role: strategy operations lead.
The source prompt was cut off after its first input. Draft recipe until the full prompt is added: `matrix` with rows = objectives and columns = key results, cards = owning initiatives with `fields.Moves` = the KR delta. Initiatives that move no KR go in a `callouts` block titled "Drop or re-scope".

### 17 to 30
Not yet added. Add each as a section here with the same five lines: id, role, inputs, blocks, follow-up.
