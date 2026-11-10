---
name: build-interactive-explorer
description: Build a polished interactive website that organizes source material into clear paths, clickable stages and expandable detail. Use for solution explorers, project or research hubs, discovery-to-design narratives, process guides, personas and JTBD, user journeys, capability maps, or requests to reuse this explorer layout for a different subject. When this layout fits the reader’s task, retain its sidebar, calm visual hierarchy and consolidated source references while adapting content and labels to the topic. Do not use it for a release review site built from tracker exports, which is build-review-site.
---

# Build interactive explorer

Turn a source package into an explorable explanation. Choose the representation for the reader’s task first. When this shell fits, preserve its layout and progressive disclosure while adapting the subject, paths, labels and evidence. Keep the main view understandable before anything is expanded.

## Check the fit before using the shell

Name the reader's task and the relationship the artifact must explain. Use this shell when ordered paths and focused detail support that task. A request for interactive elements does not by itself establish that a sidebar and stage cards are the right form.

For example, a service process may need stages that expose the responsible role, handoff and exception. A system explanation may need a diagram with labeled exchanges and ownership. A call rehearsal may need question, answer and follow-up prompts. Preserve these differences when selecting the workflow. Use the existing prepare-sales-pursuit workflow for a sales call brief and build-review-site for tracker-based release review. Keep a simple standalone visual in the requested format when a full explorer adds no useful capability.

The bundled schema supports paths, details and references; it has no dedicated graph or rehearsal engine. If the requested explanation needs another representation, use a suitable available renderer or make an explicit implementation change and test it. Do not claim that filling stage cards creates that capability. When the user specifically requests this explorer layout, retain it and make its content serve the reader's task.

## Establish the subject and sources

- Use the current request and visible conversation to determine the topic. Retrieve unseen prior decisions only when they materially affect this work.
- Resolve named documents through their owning source. Read selected sources rather than relying on search snippets or remembered summaries. Use connected read tools before asking for material they contain.
- Distinguish reported findings, analytical hypotheses, proposed behavior, approved decisions and verified implementation. Record source date and authority. Show newer scope decisions as a dated overlay when they do not replace the underlying design.
- Ask only for a missing fact that prevents a useful result; otherwise choose a reasonable structure and proceed.
- Never reuse another client's text, private links, pricing, transcripts, credentials or hosting identity. Replace the bundled fictional example with task-specific content.

## Choose paths and layers

The remaining schema, generator and shell-preservation steps apply when the task-fit check selects this explorer. For another representation, follow the selected renderer and the shared visual workflow; do not force its content into this schema.

Read [the schema](references/content-model.md) and use `assets/site/content.example.json` as the executable shape.

- Start with 1–3 meaningful paths, each with a short sequence of ordered stages. Make each stage explain what happens, the decision, handoff, supporting capability and open question.
- Offer additional angles only when supported: people and jobs, role journeys, solution or capability design, priorities, and open decisions. Empty optional sections disappear automatically.
- Adapt labels to the domain. Research can use Perspectives, Research paths, Findings and Next questions; service design can use Audiences, Journeys, Capabilities and Rollout scope.
- Keep raw reference IDs in the consolidated Sources view. Show human-readable titles elsewhere. Link detail panels to contextual subsets of the source index.
- Add a roadmap when the sources describe planned work over time. Read the `build-roadmap` skill, write its plan JSON, and place it in `roadmaps`. Use the roadmap for sequence and `priorities` for scope categories.
- Let the evidence determine counts. Do not invent roles, research, quotations, metrics, emotions, approvals or current system behavior to fill the layout.

## Compose the experience

Read [layout and interaction rules](references/design-contract.md). When the bundled shell fits or the user requests it, generate from its HTML/CSS/JS. For a UI/UX redesign, inspect the supplied reference patterns and reconsider the composition before retaining that shell.

For explicit reuse of this shell, preserve its left navigation, compact context header, hero, switchable paths and stage cards. Size the introduction so the main explanation remains within reach. Selected stages reveal a focused detail panel. Retain persona dialogs, journey accordions, solution tabs, roadmap views, scope filters and searchable consolidated sources when applicable. Make the next action and handoff legible.

Apply the selected brand profile and its component tokens. The shell's historical teal/cobalt styling does not override current project or workspace defaults. Avoid inline technical identifiers, dense overview tables and decorative metrics.

## Create the website

Write task-specific content JSON outside the skill directory. Run with absolute paths:

```bash
python3 <skill-directory>/scripts/create_explorer.py \
  --content <absolute-content.json> \
  --output <absolute-new-project-directory>
```

The generator validates references, copies the application into `dist/`, writes `data.js`, and creates a static hosting manifest without a project ID. It requires a new or empty output directory. Use `--validate-only` to check content without generating a site.

In Codex, use the current Sites skill for registration, source preparation and hosting. In Claude Code, publish `dist/` with the Artifact tool, private by default. Preserve this copied application; do not initialize another starter over it. Register a fresh Site and repository for a new subject. Keep new hosted explorers private; never make one public without explicit approval. Preserve an existing Site's identity and audience unless the user requests a change. The privacy label describes access; hosting controls enforce it. Set that label only to a confirmed state.

For local-only work, follow the requested destination and skip deployment. Use the applicable artifact/storage workflow for other requested deliverables. Do not deploy a demonstration merely to test this skill.

## Validate and finish

- Run the content validator and `node --check` on generated JavaScript. Check counts, links, empty states, escaping and unresolved references.
- Check that the overview fits the topic; distinguish the stage's finding, action, handoff and open decision. Confirm sample material is replaced and optional sections have substance.
- Walk through a concrete reader question using the output. The initial view should explain the relationship; opening detail should add the mechanism, example or next action needed to answer it. Clicking through paraphrases of the overview is insufficient. Preserve explanatory depth when shortening overview copy.
- Use browser checks when explicitly requested or needed for an observed UI issue. Do not add automatic browser sessions or extensive testing by default. Follow Sites/browser guidance when used; exercise path switching, stage expansion/closure, persona-to-journey navigation, tabs, source filters and keyboard focus at desktop and narrow widths.
- Assess the UI/UX separately from content and working controls: inspect whether the main relationship is immediately legible, selection keeps its context, changed states show consequences, and narrow-screen use preserves the task. Use the supplied examples as comparison evidence and record user acceptance separately.
- Report explorer checks separately from real-world process/system validation. A functioning website does not prove implementation.
- Confirm terminal private-deployment success and access before returning a URL. State material verification limits. Never broaden the audience as a workaround.

## Resources

- `assets/site/`: reusable layout and interactions, plus fictional example content.
- `scripts/create_explorer.py`: standard-library-only validator and generator.
- [Content model](references/content-model.md): schema, evidence rules and domain mappings.
- [Design contract](references/design-contract.md): visual structure, disclosure and accessibility.
