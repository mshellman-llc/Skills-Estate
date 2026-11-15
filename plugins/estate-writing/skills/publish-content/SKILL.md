---
name: publish-content
description: "Take content from topic to publishable draft through a gated pipeline: scout viable topics, research, collect the owner's evidence, draft, remove AI writing patterns, fact-check and package blog posts, conversational pieces, guides, news, reviews, case studies and proposals, or rescue an AI-written draft. Reviewing one finished text against writing rules is the writing skill."
---

# Publish content

## When to use

Use this skill when someone wants a piece of content taken from idea to publishable draft: choosing topics worth writing, researching, collecting the owner's evidence, drafting, editing out AI patterns, fact-checking and packaging. It handles blogs, conversational pieces (newsletters, social posts, FAQs, scripts), expository guides, news stories, product reviews, proposals and case studies. Use rescue mode when the input is an existing AI-written draft that needs to become publishable, rebuilt, or retired.

## When not to use

- Reviewing or correcting a single finished piece against the owner's rules belongs to `writing` (or `review-writing` for prose review with learned corrections).
- Applying a client or project brand to an artifact belongs to `manage-brand-profile`.
- Interactive explorer sites belong to `build-interactive-explorer`; editorial charts on their own belong to `build-editorial-chart`; decks belong to `build-deck`.
- Synthesizing interviews into findings belongs to `synthesize-discovery`.
- Writing a statement of work belongs to `write-statement-of-work`.

## Inputs

1. The goal for the run, or the draft to rescue.
2. A filled owner profile ([owner-profile.md](references/owner-profile.md)), passed as a path. Without it, stop and ask for it.
3. The owner's writing rules folder, named in the profile. When it is missing, run with the general layers in the editor procedure and say that the owner's rules did not run.
4. Optional: seed topics, real demand data (Search Console exports, customer questions, keyword tool figures), existing drafts, the owner's data files, screenshots and photos.

## Workflow

Read [orchestrator.md](references/orchestrator.md) first; it holds the done criteria, the evidence rules, the run ledger and the standing rules. Each step below follows its procedure in [agents.md](references/agents.md).

| Step | Agent | Output | Gate |
| --- | --- | --- | --- |
| 1 | Scout | Ranked topic slate with scores and kill reasons | Owner picks topics |
| 2 | Researcher | Source register and question bank | Stop if no topic has an owner asset |
| 3 | Asset collector | Owner's answers, a thesis and opening the owner wrote or approved, writing samples, data and permissions | Owner supplies the evidence |
| 4 | Architect | Brief, genre contract and exhibit plan | Every section has a claim and an evidence ID |
| 5 | Writer | Draft | None |
| 5b | Visual producer | Exhibits built as code from cited data, with check results | Every exhibit passes its checks |
| 6 | Editor | Findings, revised draft, meaning diff | No blocking findings; stance unchanged |
| 7 | Fact checker | Claim table, quote diffs, link checks, recomputed exhibit values | A named person signs |
| 8 | Reader panel | Scores against the genre contract, weakest passages | Every criterion at 3 of 4 or higher |
| 9 | Publisher | Final package and approval packet | Owner signs off |

Two failed panels return the draft to the writer; a third returns it to the brief. Set no volume target, and publish nothing when no topic clears the scorer's threshold.

Run the deterministic checks at steps 6 and 9:

```sh
python3 scripts/evidence_scan.py --file DRAFT.md            # published copy
python3 scripts/evidence_scan.py --file DRAFT.md --data-piece  # numbers are the subject
python3 scripts/evidence_scan.py --file NOTES.md --internal    # internal working document
```

The scan flags paragraphs with more than two figures, sections denser than one figure per 40 words, text that claims its own sourcing, and production vocabulary in published copy. Then run the owner's writing check from their rules folder. Neither scan replaces the line-by-line editor pass.

For visual elements, follow [visual-elements.md](references/visual-elements.md). For rescue mode and engine upkeep, follow [rescue-and-maintenance.md](references/rescue-and-maintenance.md).

### Claude Code and Codex

Run each agent as its own subagent with only its procedure and inputs, so the editor and the panel never judge their own draft. Keep the run ledger as JSON beside the drafts. Use a judge from a different model family for the reader panel when one is available.

### Claude.ai and other single-agent hosts

Run the steps in order in one conversation, keeping each step's output under its own heading. State in the approval packet that the same model wrote and judged the draft.

## Failure handling

- A human gate with no answer: finish every step up to the gate, write the approval packet (the decision, the options, the evidence) and stop.
- No web research capability: the scout and researcher work only from owner-supplied material and say so in the slate.
- A claim with no source: the writer stops and reports it; the fact checker cuts it. Neither softens it to fit.
- A quote with no transcript or written statement: cut it.
- A refused release for a case study: disguise it with consent or retire it.

## Outputs

Per piece: the final draft, its exhibits, the claim table, the meaning diff, panel scores, the approval packet, and the run ledger entry. Across pieces: the defect log, whose top three recurring patterns feed the next writer run.

## Reference files

- [orchestrator.md](references/orchestrator.md): done criteria, evidence rules, pipeline, run ledger, standing rules, defect log.
- [agents.md](references/agents.md): one procedure per agent, including the genre contracts and the case study standard.
- [visual-elements.md](references/visual-elements.md): when a piece gets a chart, diagram, table or component, and what each must contain.
- [owner-profile.md](references/owner-profile.md): the profile template.
- [rescue-and-maintenance.md](references/rescue-and-maintenance.md): rescuing AI drafts and keeping the engine versioned.
- [sources.md](references/sources.md): the research behind each rule.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
