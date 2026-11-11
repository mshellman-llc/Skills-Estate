---
name: prose-pass
description: 'Apply a confirmed author or project voice profile to writing intended for people, including messages, reviews, tickets, UI copy, emails, proposals, decks, reports, and narrative artifacts. Use while drafting or rewriting human-facing prose and when gating a final human-facing file. Do not use for AI instructions, indexes, ledgers, schemas, generated audit records, raw evidence, logs, code syntax, machine-readable data, quotations, or text that must remain verbatim. A file extension never selects this skill. Supersedes the retired de-ai and prose-check skills. For brand canon and artifact release gates use brand-renderer.'
---

# prose-pass

Use the confirmed author or project voice profile when supplied. Otherwise use the plain-writing defaults below. Draft in that voice, repair unclear or repetitive prose, and check the saved result before delivery. Preserve quoted material and the meaning of every source claim.

- **Generating:** use the voice rules for every human-facing sentence, including conversation,
  commentary, review findings, tickets, UI labels, and code comments. Do not
  wait for a document or a named writing task.
- **Rewriting:** preserve the source's meaning and genuine voice, remove generated patterns, then
  gate the result when it is persisted.
- **Gating:** check a finished supported human-facing file and rewrite until it has no findings.

Read [`references/surface-policy.md`](references/surface-policy.md) when deciding what text is in
scope, what must remain verbatim, or how much proof a surface requires. The short rule is simple:
if the artifact is written for a person, prose-pass governs it. A file extension does not decide.

The checker is deterministic and lives in `scripts/prose_check.py`. It is dependency-free and
reads `.md`, `.txt`, `.html`, `.docx`, and `.pptx`. A clean checker run proves the mechanical and
structural tells are gone. A person still judges whether the writing is good.

## The one idea that makes this work: the relocation trap

A ban with no replacement regenerates the banned shape in new punctuation. Ban the em dash and
the model still needs to say "two related things in one breath", so it reaches for the next
connector: `, and`. One real audit found a deck with zero em dashes and twelve balanced
two-clause sentences across ten slides. The punctuation changed. The rhythm a reader hears did
not.

So every rule here states what *replaces* the construction, not just what to avoid. When you
rewrite, do the same, or you get residue instead of a fix. This is why rewriting slop into
non-slop is harder than not generating it: the underlying rhythm survives paraphrase unless you
deliberately break it.

## Three layers

| Layer | Governs | Where it lives |
|---|---|---|
| 1 · Tokens | Word and character choices | `house.json` (default vocabulary, em-dash policy, hedge openers) |
| 2 · Constructions | Sentence and section shapes | the checker (18 construction rules) + `references/construction-rules.md` |
| 3 · Density | How often an allowed shape recurs | the checker (budgets counted across the whole file) |

Layer 3 is the one you cannot do by intention. No single balanced clause is wrong; a document
reads as generated because one shape recurs. A model drafting slide seven has no view of slides
one through six. Recurrence has to be measured, which is what the checker is for.

## Gating: run the checker

```bash
python3 scripts/prose_check.py --config house.json FILE [FILE ...]
python3 scripts/prose_check.py --config house.json --json deck.pptx    # machine-readable
```

Exit 0 means the checker found nothing. Exit 1 means at least one WARN or FAIL. Exit 2 is a bad invocation or
an unreadable file. Quoted material (fenced code, inline code, blockquotes) is excluded, so a
document can cite bad prose as an example without failing on it.

Every finding blocks completion. Rewrite the sentence that triggered it, then run the checker
again. Do not dispose, waive, override, or explain a finding away. Quoted and protected material
must use the supported boundaries so the checker can exclude it instead of leaving a standing
finding.

## Sweeping a tree, and measuring density: `scan.py`

`prose_check.py` judges one file against the house register. `scan.py` answers the two questions it
cannot: where is the slop across a whole directory, and how heavy is this draft compared to that
one.

```bash
python3 scripts/scan.py audit docs "*.md"       # walk a tree, exit 1 on any finding
python3 scripts/scan.py score draft.md          # trope density per 1,000 words
python3 scripts/scan.py score draft.md --json   # compare two runs
python3 scripts/scan.py --input FILE            # gate one input, no path prefix
```

`audit` reports every match as `path:line:col: category: message` and gates a commit or a build.
`score` is informational and always exits 0. Both strip fenced and inline code before matching, so
reported positions still point at the source. For non-prose source files, the `score` command extracts comments and scores them as prose.

It reports and gates. It never rewrites. To clean a single input, edit at the reported positions,
then re-run `prose_check.py` for the register judgment.

**One vocabulary, one home.** `deai_scan.py` holds the house word and phrase lists.
`wordlists/vocabulary.txt` and `wordlists/flowery-phrases.txt` are generated from it by
`scripts/sync_wordlists.py` and carry a do-not-edit header. Edit `deai_scan.py` to add or retire a
term. Then re-run the generator. The selftest fails if the two fall out of step, which is what keeps this
from becoming a second vocabulary that quietly disagrees with the first. The weighted lists
(`marketing-verbs.txt`, `soft-phrasing.txt`) carry per-term weights `deai_scan.py` has no equivalent
for, so those stay hand-maintained.

## Rewriting: plain-writing defaults

The target is **a tenured expert who has walked in the client's shoes**. Direct, confident,
specific.

- **Lead with the outcome.** The result first, then the how. "Quote cycle dropped 40 percent.
  Here is how," not "We implemented X, which resulted in Y."
- **Own the recommendation.** Active voice, "we" and "our team". "The delivery team configures the model,"
  not "the model can be configured."
- **Carry a specific in every sentence.** A real number, a named system or person, a concrete
  consequence, or a clear opinion. Readers do not catch AI, they catch generic, and they rate the
  sender as less capable when they do. Scrubbing buzzwords is necessary and not sufficient: a
  sentence that loses `leverage` and gains nothing specific has failed.
- **Break the rhythm on purpose.** Mix three-word sentences with 25-word ones. Repeat the
  clearest word instead of cycling synonyms. Let a rough edge stand.
- **State constraints without inflating them.** Do not oversell risk to justify scope.

Read `references/patterns.md` on any full rewrite because it contains the durable structural rules.
For a substantial or decision-bearing surface, also read exactly one register playbook from
`references/registers/`. Use `general.md` for conversation, tickets, UI copy, code comments,
skill text, and any surface without a narrower register.

### Never strip these

Genuine epistemic language is not a tell. Confirmed, Inferred, Unknown, "estimated", ranges, "we
don't know", "not priced", "blocked", "at risk" all stay. A voice fix must never soften a
protected caveat, a figure, a conflict, or a conclusion. Never invent a specific to replace a
generic one: if the text is too vague to sharpen, ask, do not fabricate. An invented capability
is worse than a generic sentence.

### Figure safety

When a rewrite touches numbers, reconcile them against the source:

```bash
python3 scripts/deai_scan.py --tie-out SOURCE REWRITE
```

A number in the rewrite that is not in the source is a hard fail (invention). A source number
missing from the rewrite is a warning (confirm the cut was intentional).

## Money rule

Use the confirmed quote or versioned estimate as the authority for commercial figures. Attribute a client-stated figure to the client. Attribute a rough estimate to its source and preserve its uncertainty, for example "180 hours, estimated in the working scope; not an approved quote." Do not invent prices or confidence percentages. A writing pass cannot approve a commercial figure.

## Workflow

1. Decide the mode: generation, rewrite, or gate.
2. During generation, write in the voice above from the first sentence. For ephemeral prose, read it once
   for specifics, rhythm, and protected uncertainty before returning it. Do not create a receipt.
3. Rewriting: apply the voice above while you write (not as a post-pass), reading `patterns.md`
   and one register playbook for a full pass. Reconcile figures with `--tie-out`.
   Rewriting includes growing thin prose: a placeholder sentence or a generic
   claim gets expanded into specific, sourced prose by pulling the specifics
   from the artifact's evidence, never by inventing them.
4. Gate a persisted human-facing file: `python3 scripts/prose_check.py --config house.json FILE`.
5. Fix every finding and re-run the checker until it reports `clean`. Then ship.
6. For a narrative artifact being finalized, emit the receipt (below). The
   quality gate refuses a final narrative artifact without one.

## Receipts: proof the pass ran

Running the checker is not running prose-pass. The checker is the floor, and
every mechanism that stops at it has quietly rerouted the rewrite job into a
lint. The receipt closes that gap: it is a machine-checkable record that the
rewrite pass ran, what it protected, what it found, what it changed, and what
it deliberately left standing.

```bash
python3 scripts/prose_receipt.py emit FILE --out receipt.json \
    --before-file PRE_REWRITE_COPY \
    --protected "figures: Q-0417 totals" \
    --change "specificity: replaced generic claims with sourced figures" \
    --added-figure "41:rating API launch report"
python3 scripts/prose_receipt.py validate receipt.json
```

The validator re-derives every measurable claim: the artifact's hash, the
checker's findings, the figure tie-out against the before copy. A byte-identical
result with no justified no-change assessment fails. A no-change claim on prose the checker still fails also fails. A number the rewrite added without naming its
source fails. Sound prose left alone with a justification passes; the receipt
never demands arbitrary edits.

Receipts are for narrative deliverables. Never emit one for raw evidence,
transcripts, ledgers, or machine-readable files, and never rewrite those at all.

## Adapting to another house

Layers 2 and 3 are general. Layer 1 is house-specific and lives entirely in `house.json`; see
`references/house-overlay.md` to wire in a different vocabulary, budget, or CI step. Everything
in this skill is self-contained: the checker finds its config and word data beside itself, with
no dependency on any other installed skill.

## A warning about applying this to yourself

These shapes are what fluent generation produces by default, and knowing the rule does not exempt
you from it. When this skill's own reference material was first drafted it failed the balanced-
clause and triad rules repeatedly. Run the checker on your own output, including output that is
about writing quality. If you are producing a rewrite, a review, or a style guide, gate it before
you hand it over.
