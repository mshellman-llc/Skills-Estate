---
name: prepare-sales-pursuit
description: 'Plan a sales pursuit in two modes: maintain its canonical Pursuit Brief or prepare one upcoming call. Use for a pursuit overview, recommended call sequence, objective, attendee plan, agenda, tailored questions, talk track, negotiation preparation, or prospect, account, and competitor research before a sales conversation. Route post-call discovery and transcript ingestion to maintain-discovery-record, scope and pricing to scope-project, and signed work to delivery skills.'
---


# Prepare sales pursuit

## Caller context and source boundary

Use only the current task's supplied or explicitly authorized account, project sources and destinations. Resolve record names such as `client.profile` within that confirmed context; they are logical slots, not a default personal store. Connector availability alone does not authorize searching another account. Organization-specific pricing, capability catalogs, approval roles and policies must be supplied or confirmed; absent material context remains an explicit gap. Keep reusable package files immutable during a client task and save client records outside them. Never populate an example with private source material.


> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [`readout-brief.md`](_runtime/writing-diagnostics/references/registers/readout-brief.md). Inputs, not a final pass.**

One skill turns the firm's pursuit knowledge into an actionable plan. Mode A
maintains the canonical opportunity overview. Mode B prepares one upcoming call.
Every run leaves a durable Markdown record per `_shared/output-contract.md`.

Two rules carry both modes:

**Every claim traces to a source.** Sellers repeat what you write to a client. A confident sentence with no provenance is a live grenade. Footnote everything.

**Every inference is labeled as one.** Who probably signs, what a competitor probably cannot do, what a number probably means: worth having, dangerous to say out loud as facts. Each carries an ID, a confidence band, its basis, and an explicit verdict on whether it is safe to say to the client.

And one boundary: this skill never owns the post-call record. Transcript ingestion, closing answered questions, and the discovery ledger belong to **maintain-discovery-record**. Hand the transcript there; read its output here.

## Choosing the mode

- The user wants an overview of the pursuit, asks which calls to schedule, or new facts have arrived that should update the standing picture: **Mode A**.
- A specific call is on the calendar and someone needs to walk in ready: **Mode B**. Mode B reads the Pursuit Brief first and updates it after (via Mode A) when prep surfaced something new.
- Neither exists yet and a call is imminent: run Mode B for the call, then seed the Pursuit Brief from what the prep produced.

## Mode A: maintain the Pursuit Brief

Create it once the org and opportunity are understood. Maintain one concise
canonical document per pursuit and update that file in place.

### Required content

Every Pursuit Brief carries these sections, and `scripts/check_pursuit_brief.py` verifies them:

1. **Client and opportunity context**: who they are, what is in play, where the pursuit stands.
2. **Situation**: the overall picture in a few paragraphs.
3. **Desired business outcomes**: what the client is trying to change, in their terms.
4. **Confirmed facts**: each with a named source and date.
5. **Assumptions**: every entry is a bulleted line starting `Assumption:` (optionally with an ID, `Assumption A-03:`), with basis and confidence. Nothing unlabeled enters this section, and no assumption hides among the facts.
6. **Important unknowns**: what was searched for and not found.
7. **Stakeholders**: known people with roles, and the missing stakeholder ROLES the pursuit still needs. Never invent a name, a title-holder, availability, or a commitment. When the identity is unknown, recommend the role ("we need the person who owns quoting operations"), never a guessed person.
8. **Risks and warning signs**.
9. **Qualification status**: where the deal sits and what evidence supports that.
10. **Recommended calls**: the calls to schedule and their sequence. Each call is a `###` subheading carrying three labeled lines: `Purpose:`, `Desired outcome:`, and `Prerequisites:` (the evidence each call is expected to produce or require).
11. **Immediate next steps**: each with an owner and timing.
12. **Decisions needed**: what the team must decide and who decides it.
13. A **last-updated provenance line**: `Last updated: YYYY-MM-DD by <who or what run>, from <sources>`.

Record genuinely unknown content under Important unknowns. An unresolved
placeholder (`TBD`, `TKTK`, `{{ }}`) fails the brief.

### The brief is a living artifact

Repeated runs update it idempotently: re-running on the same facts changes nothing, and new facts update the sections they belong to rather than appending duplicates.

Human-authored material is protected with HTML comment markers:

```markdown
<!-- human -->
The CFO told me directly he will not fund this before Q3. Do not push timeline.
<!-- /human -->
```

Updates must NEVER rewrite, trim, or reflow anything between `<!-- human -->` and `<!-- /human -->`. Content moves around them, not through them. The checker enforces this: run `check_pursuit_brief.py --before old.md --after new.md` before replacing the file, and abort the update if it fails.

### Where it lives

The Pursuit Brief draws its durable client facts from `client.profile` and
`client.relationships`, then points to the active `opportunity.front_door`.
Update only the records this skill owns, idempotently, under the Hub contract.
The full brief remains a durable Markdown artifact per
`_shared/output-contract.md`, named `<client>-pursuit-brief.md`.

### Gate it

```bash
python3 scripts/check_pursuit_brief.py <client>-pursuit-brief.md
python3 scripts/check_pursuit_brief.py --before old.md --after new.md   # on updates
```

Exit 0 passes. Correct every reported brief defect.

## Mode B: the Upcoming Call Brief

Prepares ONE specific call. Start from the calendar event: when the call is, who is on the invite, who organized it. The attendee list is the stakeholder map and drives the audience partition below. If no event exists, ask who is in the room before researching.

### Required content

1. **Call objective**: the one or two things the call must produce.
2. **Desired decisions or outcomes**.
3. **Attendees and roles**, both sides.
4. **Known context**: what the record already establishes, sourced.
5. **Run of show**: a concise sequence of moves.
6. **Agenda with time allocation**.
7. **Questions**: tailored and ranked. When a discovery ledger exists (built by maintain-discovery-record), pull the ranked Column B questions from it rather than inventing a parallel list; add call-specific questions only where the ledger is silent, and say which are which.
8. **Risks and sensitivities**.
9. **Facts vs assumptions vs unknowns**, explicitly separated.
10. **Follow-up plan**.
11. **Relationship to the Pursuit Brief**: name the pursuit brief file, which of its recommended calls this one is, and what it should feed back.

Gate it with `python3 scripts/check_pursuit_brief.py --mode call <file>.md`.

### Evidence disciplines the call brief inherits

These four behaviors are load-bearing, not optional polish:

**Sections are earned by evidence, never required by a template.** A talk track requires a verbatim ask from a transcript. A Q&A bank requires questions the counterpart actually raised. A figure ledger requires reconciled figures. A section whose evidence is absent is omitted, and the gap is reported in chat. Four sections built entirely from the record beat ten where six were inferred.

**No figure without reconciliation.** Every number is written into an evidence ledger (`assets/evidence.schema.json`) and checked against every other source that mentions it:

```bash
python3 scripts/reconcile.py evidence.json
```

It fails on unsourced figures, unreconciled conflicts, and leaks of `never`-tagged material. Conflicts are surfaced, never silently resolved by picking the better-reading number: both values go in the brief with the disagreement named, and the presenter decides.

**No voice without a recording.** Spoken lines in a talk track are assembled from the presenter's own recorded phrasing: their analogies, their framings, their register, mined from transcripts where they speak. Absent such a transcript, produce intents only, say so in chat, and never simulate a voice from a job title.

**Every retrieved statement carries an audience tag.** `public` may appear anywhere; `internal` appears in the brief only, usually as a landmine or Q&A answer; `never` (a person assessing a named individual, for instance) is excluded from every artifact and may appear only as an explicit do-not-repeat instruction with no detail. The counterpart's statements about their own organization are `internal`: reflectable back to them, not portable to their colleagues.

**Gaps go in chat, never in the artifact.** After building, report: sections omitted and why, figures that could not be reconciled, stale evidence, and any decision the presenter must make before the call. The artifact stays clean; the user gets the honest picture.

## The research machinery, supporting both modes

Depth is set by the clock. Two hours means parallel research agents and the full pack. Twenty minutes means one research pass and a tight brief; say what you are cutting rather than half-building more.

**Harvest internal knowledge first.** Public research is commodity work any competitor can do. Search the authorized project sources and connected account relevant to this task, such as Slack, Drive, CRM and calendar. Do not broaden to other personal or employer accounts. A zero-result Salesforce search is itself a finding. Read transcripts verbatim, never summaries: a summary may omit the actor, mechanism or qualification that changes the decision. Preserve those details from the authorized source rather than inventing an example.

**Then public research, in parallel, with citation discipline.** Spawn two subagents in the same turn: Agent A on the business (how they make money, who pays them, financial condition, priorities), Agent B on the people and the field (attendees, absent deciders, competitors, platform landscape). Prompt templates are in `references/research-prompts.md`; the two demands worth preserving in any edit are the inline source URL next to every claim and the `[ASSUMPTION]` label with confidence on unverified reasoning. Write agent output to disk and read it there.

**Make the money flow a first-class object.** Who pays, through what instrument, how pricing moves over a deal's life, where revenue leaks. Then reconcile that against the client's operational pain; the collision between what their filings say and what their transcript says is where differentiated insight lives. The client's own filings usually describe the consequence of the operational problem they are about to describe to you.

**Find what nobody else has.** Vendor changes since the client last evaluated, whether a competitor's product literally applies, the org-chart diff since a past initiative died, numbers that moved since the client formed their opinion. Each must survive a hostile read as a plain fact with a source, or it goes to the assumptions register instead.

**Write the atomic knowledge base** when depth allows: topic-per-file Markdown, each independently footnoted, per `references/knowledge-base-spec.md`. Footnote types: `[^S1]` filings and company sources, `[^W1]` web, `[^I1]` internal, `[^A1]` assumptions. Flag conflicts rather than resolving them silently, and keep the assumptions register as its own file with a client-safety verdict column.

**Build the interactive HTML brief** when the call warrants it: `assets/brief-template.html` is the working shell (footnote popovers, assumption highlighting, money-flow explorer, drill mode); you fill in content, not mechanics, per `references/html-brief-spec.md`. Build and verify with:

```bash
python3 scripts/build_brief.py draft.html -o out.html --verify
```

It resolves the explicitly selected project brand profile (or neutral default), embeds declared assets, and verifies the result only in permitted browser infrastructure. Missing assets or unavailable rendering remain acceptance gaps. The file must stay fully self-contained, no CDN dependencies: these get opened on planes and in client parking lots. The HTML is secondary; the Markdown brief is the canonical record per `_shared/output-contract.md`.

## Landing the work

Deliver the artifact, register its location, update `client.profile` and
`client.relationships` with supported changes, and write session memory pointing
at the records rather than restating them.

Close with the top three facts, then the landmines. Then flag your biggest judgment call and argue the other side of it honestly. A brief presented as settled when it contains a real fork is the failure mode.

## Quality gates

- `scripts/check_pursuit_brief.py` for each Pursuit Brief and Call Brief, plus
  `--before/--after` when revising an existing Pursuit Brief.
- `scripts/reconcile.py` on the evidence ledger whenever a Mode B brief carries figures.
- **review-writing** owns writing review: run its bundled diagnostics on the prose. No em dashes, no buzzwords, no AI-construction patterns. Report the counts it prints.
- **brand-renderer** and `_shared/build-card.md` own any branded surface. Use `--profile` for an explicitly supplied profile; the renderer otherwise stays neutral and never discovers an employer brand from personal folders.

## Boundaries

- **maintain-discovery-record** owns post-call transcript ingestion, question closure,
  decision logging, and its two-column ledger. Mode B reads that record and
  carries supported post-call updates into the Pursuit Brief.
- NOT scope item creation, quote editing, or pricing. That is **scope-project** and the Pricing System.
- NOT post-sale delivery work, project status, or requirements sessions.
- Never invents stakeholder names, availability, commitments, or facts. Roles, not guessed people.

## What to skip when time is short

Cut in this order and say what you cut: drill-mode content, the full knowledge base (keep index, current-state, stakeholders, deal-strategy, assumptions), Agent A's deep financial history. Never cut: the internal harvest, the assumptions register, the landmines, citations, or the checkers.

## Files

- `scripts/check_pursuit_brief.py` · the gate for both brief modes and the human-marker idempotency check. Stdlib only; exits nonzero on failure.
- `scripts/check_pursuit_brief_selftest.py` · runs the gate against `scripts/fixtures/`.
- `scripts/reconcile.py` · the figure and evidence gate for Mode B ledgers.
- `scripts/reconcile_selftest.py` · its selftest.
- `scripts/build_brief.py` · inlines brand assets into the HTML brief and render-verifies it.
- `assets/evidence.schema.json` · the Mode B evidence ledger structure.
- `assets/brief-template.html` · the working interactive shell.
- `references/research-prompts.md` · prompt templates for the two research subagents.
- `references/knowledge-base-spec.md` · atomic file list, footnote conventions, assumptions register format.
- `references/html-brief-spec.md` · HTML section structure, content schemas, brand constraints.

## Release gate (required)

Before delivery, run the required gate. Complete it during production. Full spec in
[`release-gate.md`](_shared/release-gate.md).

1. Apply review-writing to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run brand-renderer on the branded artifact: palette, borders, radii, logo,
   footer.
3. Run review-deliverable before you call it final.

Do not present the artifact as finished until every check that applies has passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
