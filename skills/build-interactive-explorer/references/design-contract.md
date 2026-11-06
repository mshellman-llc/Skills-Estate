# Explorer layout and behavior

| Area | Contract |
| --- | --- |
| Navigation | Fixed light sidebar; distinct active view; mobile menu at narrow widths. Topic at top, evidence context at bottom. |
| Header | Small breadcrumb and accurate access/status label. Never use a privacy badge as authentication. |
| Hero | Large plain-language title with an accent phrase, short introduction and useful actions. Use the side note to connect need, work and outcome. |
| Main paths | Small number of audience/process paths. Ordered stage cards have a title, one-sentence summary and explicit expansion affordance. |
| Stage detail | Reveal action, decision, handoff, reported finding, capability fit and open question. Hide deeper evidence/acceptance detail behind another disclosure. Closing restores focus to the stage. |
| People | Search role/audience cards. Native modal exposes context, triggers, jobs, information needs and research gaps. Link to the person's journey. |
| Journeys | One role and one unit of work. Each step exposes context, action, decision, handoff, acceptance direction and exceptions. Offer expand/collapse all. |
| Solution | Compact area list beside detail. Separate User experience, Design & records and Decisions & checks; adapt labels for other domains. |
| Roadmap | Drawn by the `build-roadmap` components from its plan, with tabs when there are several. Never restyle them per explorer. |
| Scope | Named categories with calculated counts. Include supported fallbacks and dependencies. Do not force January, MoSCoW or release commitments onto unrelated topics. |
| Sources | Consolidated IDs and links; text/category filters; visible contextual filter and clear reset. Original permissions still apply. |

Give stage cards a light tint of the accent that gets one shade darker per stage, and make the selected stage solid accent. Pure white cards on a white page made a process hard to follow in review. Use one text size inside a table, links and status labels included, and put long ticket or source lists behind a closed line in the row. Number circles keep one fixed size on every view.

Keep comfortable margins, restrained borders, light surfaces, navy/teal body text and cobalt accents. Reuse bundled typography and spacing; improve body sizes if density makes reading difficult. Avoid metric walls or repeated feature-card filler.

Use semantic buttons, headings and native disclosures. Keep visible focus, meaningful labels, Escape behavior, focus restoration, reduced-motion support and narrow-screen layouts. Escape generated content. Restrict source links to safe HTTP(S) URLs. Load nothing from the network. Add no trackers, client data writes, connector access or authentication bypasses to the presentation shell.
