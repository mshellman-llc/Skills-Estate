---
name: skill-creation-walkthrough
description: 'Step-by-step guide for creating your own Claude Skills: deciding whether a skill fits, writing the SKILL.md file, structuring reference material, and making it trigger reliably. Use when you want to package a workflow or repeated task into a reusable Skill, when an existing skill is not triggering or loading the right context, when you are auditing an underperforming skill, or when you want to publish a skill for others. Also triggers on how do I make a skill or what makes a good skill.'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

## When to use

- Package a repeated workflow or framework for reuse or publication.
- Repair a skill that triggers poorly or loads the wrong context.
- Review a skill using the [skill release standard](references/estate/skill-standard.md).

## When NOT to use

- For one-off prompts (just write the prompt).
- For information that should live in system context, not progressive disclosure.
- For changing Claude's general behavior across all conversations (use your assistant's global settings or a system prompt, not a skill).
- For replacing tool calls (skills are instructions, not tools).

## Required inputs

- The task or workflow you want to encode.
- The audience: who will trigger this skill, in what kind of conversation.
- Existing artifacts: prompts you have used, docs you have written, examples of good output.

## The framework: how skills work

A Skill is a folder with a `SKILL.md` file. The SKILL.md has YAML frontmatter (name and description) and a body with instructions. It can also include reference files, scripts, or templates that get loaded when needed.

The key property: **progressive disclosure**. Claude does not read every skill on every turn. The skill description lives in the system prompt. The SKILL.md body and references load only when the skill is triggered. This permits a larger estate without loading every body into context.

What this means for you:

- The **description** helps the host select the skill. Test selection on each intended host; descriptions alone do not prove routing.
- The **SKILL.md body** is for the workflow itself.
- The **references** are for content that does not need to be in every invocation: long checklists, templates, examples, deep reference material.

## Workflow

### Phase 1: Decide if a skill is the right shape

Not everything should be a skill. Run this test:

| Sign it should be a skill | Sign it should not be |
| --- | --- |
| You repeat the same workflow 5+ times. | You used it once. |
| The output benefits from a consistent structure. | Each output is bespoke. |
| The task has a clear trigger (a question shape, a file type, a domain). | The task is part of every conversation already. |
| The instructions exceed 200 words. | A one-line system instruction would do. |
| Templates or reference material would help. | Pure prose is enough. |
| Other people might benefit from the same workflow. | Only relevant to your single project. |

If most of your answers are in the left column, build a skill. Otherwise, use a saved prompt or a system instruction.

Keep local sketches outside canonical `skills/`. For a repository draft, answer the ten questions
in [`references/governed-intake.md`](references/governed-intake.md). Drafts may retain explicit
unknowns. Before candidate status, name the closest skills and record the collision disposition.

### Phase 2: Define the trigger

Before writing anything, ask: when should this skill load?

Be concrete. Write down the exact phrases or situations that should trigger it. Examples:

- "When someone requests a creative brief, kickoff doc, or project brief."
- "When the user uploads a CSV and wants tabular analysis."
- "When someone asks 'how do I rank for X', 'should I add schema', or anything SEO-related."
- "When the user mentions they want to pick a vendor or compare tools."

The trigger is your description's job. If you cannot articulate the trigger crisply, the skill will not load reliably.

### Phase 3: Write the description

The most important two sentences in the skill. It is what the model sees when deciding whether to
load anything, so triggering is its entire job.

Four parts: what it does, when to use it, "Also triggers when..." for the non-obvious cases, and
who it is for. The commonest failure is a description that says what the skill does and never
says when to load it.

> Bad: "Helps with SEO."
>
> Good: "Audit on-page SEO of a single URL or a small set of pages. Use if the user requests a
> page audit, wants to optimize titles and meta descriptions, asks 'why is this page not ranking',
> or shares a URL and asks what is wrong with it. Also triggers when the user mentions Core Web
> Vitals, internal linking, or schema markup."

Use the examples from failed selection tests to refine the description. Avoid adding broad catchalls. Full formula, patterns by skill
type, and anti-patterns in [`references/description-cookbook.md`](references/description-cookbook.md).

### Phase 4: Structure the SKILL.md body

A consistent structure makes skills readable, maintainable, and AI-friendly. Start with this pattern:

```
---
name: [your-skill-name]
description: [your description]
---

[One-sentence purpose statement]

## When to use
[Bulleted list of trigger situations]

## When NOT to use
[Bulleted list, ideally redirecting to sibling skills]

## Required inputs
[What Claude needs from the user to run this skill]

## The framework
[The durable IP: the model, the steps, the dimensions, the layers]

## Workflow
[Numbered steps Claude follows]

## Failure patterns
[Common mistakes to avoid or push back on]

## Output format
[What the deliverable looks like]

## Reference files
[List of files in the references/ folder with descriptions]
```

Not every skill needs every section. Some skills are pure how-to and skip "framework". Some skills are heavy on examples and add an "Examples" section. Use the structure as a starting point, adapt as needed. The annotated blank version is [`references/skill-template.md`](references/skill-template.md).

### Phase 5: Add references for what does not belong in SKILL.md

References are the second tier of progressive disclosure. They load when Claude reads them, not by default.

Use references for:

- Long checklists (a 100-item audit checklist).
- Templates with worked examples.
- Detailed playbooks for specific scenarios.
- Reference material like spec links, glossaries, decision tables.
- Anything over 100 lines that not every invocation needs.

Each reference should be standalone. A reader (or Claude) should be able to use it without reading the SKILL.md first, given the context the skill provides.

Naming patterns that work:

- `references/[noun]-template.md` for templates.
- `references/[noun]-checklist.md` for checklists.
- `references/[noun]-playbook.md` for end-to-end runbooks.
- `references/example-[scenario].md` for worked examples.

Reference your reference files from the SKILL.md "Reference files" section with a one-line description of each.

### Phase 6: Deliver or write the skill

Where the skill lands depends on the surface you are running on. Detect it, do not assume:

- **When you can write files** (a local or mounted filesystem is available): create the `your-skill-name/` folder, write `SKILL.md`, and write the `references/` files. The folder is the skill.
- **When the filesystem is ephemeral, hosted, or absent** (chat-only surfaces, sandboxes that reset, no writable path): deliver the full contents in chat as labeled code blocks, one per file, with the intended path as a heading, so the user can save them wherever their skills live. Do not silently drop files into a scratch directory that will not persist.

Either way, the deliverable is the same set of files. The only question is whether you write them or hand them over.

For a repository draft, run the bundled scaffolder from this skill directory. Supply the actual workflow body; the command does not invent a domain procedure or claim every host is supported.

```bash
python3 scripts/scaffold_skill.py example-skill \
  --root /path/to/project --display-name "Example skill" \
  --description "Perform the named workflow when the user requests its output." \
  --owner "Project maintainer" --category analysis --runtime codex \
  --workflow /path/to/complete-workflow.md
```

The command creates `skills/example-skill/` beneath the explicit project root and refuses an existing destination. Add `--reference /path/to/file.md` for a required reference, and repeat `--runtime` only for intended hosts. It defaults to no Knowledge Hub dependency. A workflow that needs the hub can declare `--knowledge-hub required` or `optional`; complete the actual read/write contract in its metadata.

The result is a draft containing the supplied workflow, metadata, a governance intake and a creation receipt. Finish the intake and run the skill on realistic inputs before installation or publication. Keep cost and efficiency `unknown` until a dated fixture receipt measures them.

### Phase 7: Test and iterate

Skills do not work the first time. Plan to iterate.

Testing checklist:

- [ ] Trigger test: in a fresh conversation, write the trigger phrase. Does the skill load? If not, the description is too narrow or wrong.
- [ ] Edge case test: write something that should trigger via the "Also triggers when..." clause. Does it fire?
- [ ] False positive test: write something close but not actually relevant. Does the skill avoid loading? If it always loads, your description is too broad.
- [ ] Output test: run the skill on a real task. Is the output what you expected?
- [ ] Release test: apply the [skill release standard](references/estate/skill-standard.md). Inspect the actual outputs as well as packaging results.
- [ ] Scope test: use changed-skill checks for internal repairs, overlap-group checks for behavior
      changes, and the full estate for shared machinery or a release candidate.

Common fixes: not triggering means broaden the description and add phrases; triggering too often means narrow it and add "Do not trigger when"; generic output means the framework needs specifics; an overwhelming reference wants splitting.

## Failure patterns

- **Description too narrow.** Never fires, because it needs phrases nobody says.
- **Description too broad.** Fires constantly, including on unrelated work.
- **No trigger phrases.** Names the action but omits the selection situations.
- **References that duplicate the body.** If a reference repeats the body, prune one.
- **No "When NOT to use".** Overlapping siblings load ambiguously. Name them.
- **Optimizing for one example.** Written around a single case, fails the adjacent ones.
- **Hardcoded stack or surface assumptions.** A general skill teaches methodology: frameworks,
  decision criteria, taxonomies, anti-patterns. Bundle working implementations when they serve
  the requested outcome. Put host-specific choices behind documented configuration or adapters. See
  [`references/methodology-vs-implementation.md`](references/methodology-vs-implementation.md).
- **Shipped once, never revisited.** Re-run capability and routing checks when dependencies or requested outputs change.

## Output format

When using this skill to create another skill, deliver:

1. **Trigger analysis**: a short list of phrases and situations that should fire the skill.
2. **Description draft**: the 2-4 sentence description for the YAML frontmatter.
3. **SKILL.md body**: the full body of the skill, following the standard structure.
4. **Reference plan**: a list of reference files to create with one-line descriptions.
5. **First reference file**: at least one reference written end to end as a starting point.
6. **Test plan**: 3-5 test prompts that should trigger the skill, plus 2-3 that should not.
7. **Governance intake**: the ten answers, collision disposition, capability fallback, and an
   evidence-backed cost and efficiency receipt or explicit `unknown` values.

## Reference files

- [`skill-template.md`](references/skill-template.md) a blank SKILL.md with annotated section guidance.
- [`description-cookbook.md`](references/description-cookbook.md) description patterns by skill type, with worked examples.
- [`methodology-vs-implementation.md`](references/methodology-vs-implementation.md) what belongs in a general skill, what stays internal, and the audit pattern for keeping one methodology-pure.
- [`governed-intake.md`](references/governed-intake.md) the ten answers, promotion boundary,
  collision decisions, capability fallbacks, and validation scopes.
