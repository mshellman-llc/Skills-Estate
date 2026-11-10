---
name: build-interactive-explorer
description: Build a polished interactive website that makes source material easy to explore through project-specific structure and expandable detail. Use for solution explorers, project or research hubs, discovery-to-design narratives, process guides, personas and JTBD, user journeys, and capability maps. Choose navigation, visual design and interactions to fit the audience, content and current request rather than reusing a fixed layout. Do not use it for a release review site built from tracker exports, which is build-review-site.
---

# Interactive Explorer

Turn source material into an explorable explanation. Use the supported site workflow to implement a design for this project. Keep the main view understandable before anything is expanded.

## Choose the representation

Name the reader's task and the relationship the artifact must explain. A service process may need stages that expose the responsible role, handoff and exception. A system explanation may need a diagram with labeled exchanges and ownership. A call rehearsal may need question, answer and follow-up prompts. Preserve these differences when selecting the workflow. Use `prepare-sales-pursuit` for a sales call brief and `build-review-site` for tracker-based release review. Keep a simple standalone visual in the requested format when a full website adds no useful capability.

Use an available renderer that supports the chosen representation, or implement and test the missing interaction explicitly. A set of selectable cards does not by itself explain a system relationship or provide a rehearsal exercise. When the user requests an existing layout, use their supplied reference and make its content serve the reader's task.

## Establish the subject and sources

- Use the current request and visible conversation to determine the topic, audience and purpose. Retrieve unseen prior decisions only when they materially affect this work.
- Resolve named documents through their owning source. Read selected sources rather than relying on search snippets or remembered summaries. Use connected read tools before asking for material they contain.
- Distinguish reported findings, analytical hypotheses, proposed behavior, approved decisions and verified implementation. Record source date and authority. Show newer scope decisions as a dated overlay when they do not replace the underlying design.
- Ask only for a missing fact that prevents a useful result; otherwise choose a reasonable structure and proceed.
- Never reuse another client's text, private links, pricing, transcripts, credentials or hosting identity.

## Organize the content

Read [the content guidance](references/content-model.md). Choose an information structure that supports what the reader needs to understand or do. There is no required schema or section list.

- Use paths and ordered stages only when the subject has meaningful sequences or distinct routes. A thematic collection, comparison, map or searchable reference may fit better. Do not invent paths to satisfy a layout.
- For planned work over time, use `build-roadmap` and its validated snapshot plan. Embed its components through the supported roadmap workflow, keeping its brand settings consistent with the project. Keep sequence separate from scope priorities.
- Offer additional angles such as people and jobs, journeys, capabilities, priorities and open decisions only when supported by useful content.
- Adapt labels and depth to the domain. Keep the initial view concise and place supporting detail near the claim it explains.
- Keep raw reference IDs in a consolidated source index when useful. Show human-readable titles elsewhere and link details to the relevant evidence.
- Let the evidence determine counts. Do not invent roles, research, quotations, metrics, emotions, approvals or current system behavior to fill the layout.

## Design the experience

Read [design and interaction guidance](references/design-contract.md). Choose the layout, navigation, typography, colors, spacing and disclosure patterns for this project's audience, content and brand. Resolve branding through the shared brand policy and the confirmed project profile; use the estate neutral profile when none is supplied. Follow a user-supplied reference or established project design system when requested.

Do not default to a fixed sidebar, hero, palette, path switcher or card arrangement. Use only interactions that make the content easier to understand. Make the reader's next action clear where the material supports one.

## Create the website

In Codex, use the current Sites skill for site creation, source preparation and hosting. In Claude Code, use an available supported Artifact workflow; if it is unavailable, deliver the local website and state the publication limit. Build with the appropriate supported project workflow; no bundled template, content JSON format or generator is required. Keep task-specific content and implementation outside this skill directory.

Register a fresh Site and repository for a new subject. Keep new hosted explorers private; never make one public without explicit approval. Preserve an existing Site's identity and audience unless the user requests a change. The privacy label describes access; hosting controls enforce it. Set that label only to a confirmed state.

For local-only work, follow the requested destination and skip deployment. Use the applicable artifact/storage workflow for other requested deliverables. Do not deploy a demonstration merely to test this skill.

## Validate and finish

- Run the checks appropriate to the implementation, including build or syntax checks where applicable. Check counts, links, empty states, escaping and unresolved references.
- Check that the overview and navigation fit the topic. Verify that any sequences, roles, findings, actions and handoffs reflect the source material. Remove placeholder content and unsupported sections.
- Walk through a concrete reader question using the output. The initial view should explain the relationship; opening detail should add the mechanism, example or next action needed to answer it. Preserve explanatory depth when shortening overview copy.
- Check semantic structure, keyboard operability, focus handling, contrast and narrow-screen behavior. Exercise the interactions actually implemented rather than requiring a standard set of widgets.
- Use browser checks when explicitly requested or needed for an observed UI issue. Do not add automatic browser sessions or extensive testing by default. Follow Sites/browser guidance when used.
- Report explorer checks separately from real-world process/system validation. A functioning website does not prove implementation.
- Confirm terminal private-deployment success and access before returning a URL. State material verification limits. Never broaden the audience as a workaround.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
