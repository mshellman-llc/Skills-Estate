---
name: "case-study-builder"
description: "Turn a piece of Megan's work into a sanitized, evidence-checked portfolio case study (working + publish copy) using her template and publish gate."
---

# Case Study Builder

Turn any project, product, or engagement of Megan's into a portfolio case study that is consistent, sanitized, and safe to publish. Produce two copies every time: a **working copy** (evidence labels and proof notes visible, for Megan) and a **publish copy** (clean first-person prose, for the site).

The split is the point. Evidence control lives in the working copy. The publish copy states what happened with confidence and contains no labels, caveat sentences, or status notes.

## Before you start
- Megan works independently through Live Laugh Code LLC. Use the current claims and rights ledger for reuse and publication decisions about Meridian, the Knowledge Hub, the skills architecture, and the playbooks. Client names, logos, client data, rate-card numbers, margins, and quote identifiers stay out.
- Use the current career numbers from `/Volumes/BeastMode/Career/` (the program records and evidence ledger). Don't invent or round past them.
- Never invent a fact, number, client, or quote to make a study read better. Missing detail: bracket it in the working copy and flag it to Megan in chat; do not fill the gap.

## Skeleton (fill for each study)
- **Title** — what she built or did, plain, no client name.
- **Client (sanitized)** — industry + size band only; never name, logo, or identifying detail. If it's her own product, say so.
- **Problem** — the business problem, one short paragraph.
- **What I did** — the approach and the system or artifacts she actually built.
- **How it works** — the mechanism (the differentiator; show the build, not just the result).
- **Outcome** — what happened, stated plainly.
- **My role** — what she personally did versus the team.
- **What it becomes** — the reusable method, offer, or skill it maps to.

Write each study in first person, as Megan. Do NOT add a closing "The point" / summary paragraph — it restates the piece, which she cuts every time.

## Evidence labels (working copy only)
- **[verified]** — source is showable (a record, a computed figure).
- **[reported]** — a real engagement figure not independently re-verified.
- **[estimated]** — a modeled/opportunity number.
- **[in progress]** — built, not yet in production use.
An untagged number does not ship.

## Resolving labels into the publish copy
Labels come off. Caveat sentences do not replace them.
- [verified] → state it.
- [estimated] → keep the single word inside the claim: "an estimated $660K–$1.07M." Nothing more.
- [reported] → use it only if Megan would say it plainly ("a colleague's scoped playbook went from two weeks to half a day"). Otherwise cut it. Never append "directional" or "not a controlled study."
- [in progress] → describe what she built and what it does. Do not add "not in production," "not verified," or "not claimed." Don't imply it runs live; just don't say either way.
- Lost or open deals → one word in the outcome ("lost," "open") when the outcome matters to the story. No status sentence.

Banned in the publish copy: "not verified," "unverified," "not claimed," "I don't claim," "does not prove," "directional," "not a controlled study," "Where it stood," "remained outside," "no sold deal was recorded," any sentence explaining what a number is not, and any state or publication note. These make Megan sound unsure and devalue her work. If a claim needs one of them to be safe, cut the claim.

## Voice — run the publish copy through megan-writing-style
The publish copy is Megan's own first-person voice, so gate it against the `megan-writing-style` skill before it ships. Her hard rules, applied here:
- Trust the reader — never restate a point or explain the previous sentence.
- No empty "builder" constructions ("I build systems that turn X into Y"). Name the actual thing: a deal-intelligence system, a discovery-to-requirements engine, the playbook catalog.
- No X-not-Y antithesis ("systems, not slideware"; "deprecate deliberately, not delete"). State the positive directly.
- No defensive disclaimers (rule 6).
- No origin-story throat-clearing; no banned phrases ("at the intersection of," "proven ability to," "whether it's X or Y," "at the end of the day," and the rest in her profile).
- Concrete nouns, real numbers, named systems in every sentence. Short sentences mixed with long. End flat and confident on the last true thing.

## Publish gate (all six before it goes public)
1. **Sanitized** — no client name, logo, stakeholder, internal identifier, or their dollar figures unless Megan cleared them.
2. **Owned** — methods and products she may show; no rate card or margin.
3. **Sourced** — every number in the working copy carries a label; nothing in the publish copy overstates its label.
4. **Separation** — no internal resourcing, rate card, margin, or staffing detail.
5. **In her voice and clean** — passes megan-writing-style; a scan for the banned disclaimer phrases returns nothing.
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
Deliver the study as a markdown file: metadata block, then working copy, then publish copy. Save durable versions to the project. Report bracketed gaps and figures that need Megan's confirmation in chat, not in the publish copy.