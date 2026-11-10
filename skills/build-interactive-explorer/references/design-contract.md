# Design and interaction guidance

Design for the current audience, content, reading context and brand. Use an existing project design system or an explicitly requested reference when available. Resolve branding through the shared policy and confirmed project profile, falling back to the estate neutral profile. Choose a coherent project-specific visual direction; no fixed sidebar, hero, colors, typography or card composition is required.

## Make the information navigable

Show the relationship the reader needs to understand explicitly. Selectable cards alone do not establish a causal explanation, system interaction or rehearsal exercise. Choose a representation that can express it.

- Choose navigation for the content's size and relationships. Use in-page anchors, top navigation, search, a sidebar or another suitable pattern only when it serves the reader.
- Establish a clear hierarchy and readable density. Use meaningful headings, comfortable spacing and clear labels. Avoid decorative metrics and repeated card filler.
- Keep the initial view understandable. Reveal supporting detail near its context with clear controls and a way back. Do not hide essential conclusions behind unnecessary interactions.
- Use stage expansion, dialogs, accordions, tabs or filters only where they fit the content. If filtering is present, show its current state and offer a clear reset and useful empty state.
- Provide contextual source links and, where useful, a consolidated source view. Preserve source access restrictions.
- Show an access or status label only when verified. Never use a privacy badge as authentication.

## Preserve accessibility and safe behavior

- Use semantic headings, landmarks, buttons and links. Prefer native disclosures where suitable.
- Keep controls keyboard-operable, focus visible and labels meaningful. For dialogs, support Escape, appropriate focus management and focus restoration on close.
- Make selected and expanded states perceivable beyond color. Maintain readable contrast and text sizes.
- Support narrow screens and reduced motion. Avoid hover-only access to essential information.
- Keep presentation assets local and load nothing from the network. Use the `build-roadmap` components for optional roadmaps without restyling their internals.
- Escape untrusted content and restrict source links to safe HTTP(S) URLs. Do not introduce trackers, client data writes, connector access or authentication bypasses merely to present the content.

Validate the interactions and responsive states actually implemented. Keep the depth of testing proportionate to the request and disclose unverified behavior.
