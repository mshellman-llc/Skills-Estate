---
name: portfolio-case-study
description: "Turn a piece of the candidate's work into a sanitized, evidence-checked portfolio case study (working + publish copy) using the candidate’s template and publish gate."
---


# Case Study Builder

Use only the candidate identity, career records, thresholds, author profile and destinations explicitly supplied or authorized for this task. Record names below describe a suggested source map; resolve them under the confirmed career root or accept equivalent supplied records. None is a bundled personal default. Missing optional context does not block a bounded draft from supplied facts.

Turn any project, product, or engagement of the candidate's into a portfolio case study that is consistent, sanitized, and safe to publish. Produce two copies every time: a **working copy** (evidence labels and proof notes visible, for the candidate) and a **publish copy** (clean first-person prose, for the site).

The split is the point. Evidence control lives in the working copy. The publish copy states what happened with confidence and contains no labels, caveat sentences, or status notes.

## Before you start
- Confirm the subject, ownership and publication authority from the current claims and rights ledger supplied for this task. A historical employer relationship does not itself authorize reuse. Client names, logos, data, rate-card numbers, margins and quote identifiers require explicit disclosure authority.
- Use the candidate’s supplied program records and evidence ledger for figures. Do not invent or round beyond their supported precision.
- Never invent a fact, number, client, or quote to make a study read better. Missing detail: bracket it in the working copy and flag it to the candidate in chat; do not fill the gap.

## Skeleton (fill for each study)
- **Title** — what the candidate built or did, plain, no client name.
- **Client (sanitized)** — industry + size band only; never name, logo, or identifying detail. If it's the candidate’s own product, say so.
- **Problem** — the business problem, one short paragraph.
- **What I did** — the approach and the system or artifacts the candidate actually built.
- **How it works** — the mechanism (the differentiator; show the build, not just the result).
- **Outcome** — what happened, stated plainly.
- **My role** — what the candidate personally did versus the team.
- **What it becomes** — the reusable method, offer, or skill it maps to.

Write each study in first person, as the candidate. Use the confirmed author profile for voice and structure. Omit a closing summary when it merely repeats the case; retain a conclusion when it advances the requested decision.

## Evidence labels (working copy only)
- **[verified]** — source is showable (a record, a computed figure).
- **[reported]** — a real engagement figure not independently re-verified.
- **[estimated]** — a modeled/opportunity number.
- **[in progress]** — built, not yet in production use.
An untagged number does not ship.

## Resolving labels into the publish copy
Labels come off. Caveat sentences do not replace them.
- [verified] → state it.
- [estimated] → keep the single word inside the claim: "an estimated $20K–$30K in this synthetic example." Nothing more.
- [reported] → use it only if the candidate would say it plainly ("a synthetic review process fell from six hours to two hours"). Otherwise cut it. Never append "directional" or "not a controlled study."
- [in progress] → describe what the candidate built and what it does. Do not add "not in production," "not verified," or "not claimed." Don't imply it runs live; just don't say either way.
- Lost or open deals → one word in the outcome ("lost," "open") when the outcome matters to the story. No status sentence.

Banned in the publish copy: "not verified," "unverified," "not claimed," "I don't claim," "does not prove," "directional," "not a controlled study," "Where it stood," "remained outside," "no sold deal was recorded," any sentence explaining what a number is not, and any state or publication note. Preserve material uncertainty and necessary qualifications. If a claim cannot be stated accurately for its audience, omit it rather than concealing the qualification.

## Voice — use the confirmed author profile
The publish copy is the candidate's own first-person voice, so gate it against the `author-writing-style` with an explicitly supplied confirmed profile skill before it ships. Apply confirmed author preferences alongside these general review checks:
- Trust the reader — never restate a point or explain the previous sentence.
- No empty "builder" constructions ("I build systems that turn X into Y"). Name the actual thing: a deal-intelligence system, a discovery-to-requirements engine, the playbook catalog.
- No X-not-Y antithesis ("systems, not slideware"; "deprecate deliberately, not delete"). State the positive directly.
- No defensive disclaimers (rule 6).
- No origin-story throat-clearing; no banned phrases ("at the intersection of," "proven ability to," "whether it's X or Y," "at the end of the day," and the rest in the candidate’s profile).
- Concrete nouns, real numbers, named systems in every sentence. Short sentences mixed with long. End flat and confident on the last true thing.

## Publish gate (all six before it goes public)
1. **Sanitized** — no client name, logo, stakeholder, internal identifier, or their dollar figures unless the candidate cleared them.
2. **Owned** — methods and products the candidate may show; no rate card or margin.
3. **Sourced** — every number in the working copy carries a label; nothing in the publish copy overstates its label.
4. **Separation** — no internal resourcing, rate card, margin, or staffing detail.
5. **In the candidate’s voice and clean** — passes `author-writing-style` with an explicitly supplied confirmed profile; a scan for the banned disclaimer phrases returns nothing.
6. **Two versions** — working copy (labels, proof notes) + publish copy (clean prose).

## Metadata block (top of the working copy only)
```
Study:            <name>
Maps to offer:    <offer / skill>
Evidence status:  <verified | mostly reported | mostly estimated>
Sanitization:     <done | pending>
Ownership check:  <clear | needs generic rebuild>
Publish-ready:    <yes | no — blocked on: ...>
```
The metadata block never appears in the publish copy.

## Output
Deliver the study as a markdown file: metadata block, then working copy, then publish copy. Save durable versions to the project. Report bracketed gaps and figures that need the candidate's confirmation in chat, not in the publish copy.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
