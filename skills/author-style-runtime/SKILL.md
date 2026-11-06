---
name: author-style-runtime
description: 'Generic template that applies one person''s confirmed private writing-style profile when they are the intended author or speaker. Not a runnable skill on its own; an install names a specific profile path and person, producing a thin per-person adapter. Does not build or change a profile; that is manage-writing-profile. Do not apply a personal profile to output written on behalf of another person, to quoted or verbatim material, or where organizational, legal, or contractual voice governs.'
---


# Author style runtime

A routing template, not a voice. Every install points it at exactly one
confirmed profile (see [manage-writing-profile](../manage-writing-profile/SKILL.md)
schema) and one person. This file describes the routing and precedence logic
every such adapter runs; it carries no one's actual voice.

Use the confirmed author profile and the current project’s brand requirements.

## Route before applying anything

Determine, from the request and available context:

1. **Authorship.** Is the profiled person the author or speaker, an
   organizational voice, or someone else?
2. **Mode.** Written or spoken.
3. **Surface.** Chat, email, document, brief, deck, talk track, call, or other.
4. **Audience.** Peer, internal group, leadership, client, prospect, public.
5. **Relationship.** New, transactional, established, close.
6. **Communication job.** Informing, requesting, correcting, persuading,
   deciding, setting a boundary, coordinating a group, or supporting someone.

Apply the profile only when authorship resolves to the profiled person.
Explicit invocation, such as being asked to write something in the person's
voice, still requires authorship to resolve correctly. It skips ambiguity
about whether the person wants voice applied at all; it does not override
authorship.

## Do not apply the profile when

- another named person is the author, even if the profiled person asked for
  the draft;
- the text is a quotation or verbatim excerpt of someone else's words;
- the artifact requires organizational, brand, legal, contractual, or
  regulatory voice that overrides personal style;
- the routed surface, audience, or job has no confirmed profile entry, in
  which case fall back to plain, unstyled drafting rather than extrapolating
  a pattern the profile does not contain (see the profile's
  `insufficient_evidence_for` list);
- the profile's `revoked` field is true.

## Precedence

1. Verified facts, legal meaning, and explicit user instruction.
2. Surface, audience, and communication job.
3. Governing organizational or artifact requirements.
4. The confirmed personal profile.
5. Prose and quality checks the artifact's surface already requires.

A voice adjustment never weakens a scope boundary, changes a fact, or
overrides a format-specific requirement ranked above it.

## Progressive disclosure and context budget

Load only what the current step needs. Approximate costs below are for
planning purposes, not measured per-token guarantees; a specific install
should confirm against its own profile size.

| Level | What loads | When | Rough cost |
|---|---|---|---|
| Routing metadata | `routing` block only: modes, surfaces, audiences, relationships, jobs | Every request, to decide whether to apply the profile at all | 50 to 150 tokens |
| Base profile | `base_profile.<mode>.core_tendencies` for the resolved mode | Routing resolves to this person as author | 200 to 800 tokens depending on profile size |
| Channel overlay | One `channel_overlays` entry matching surface, audience, and job | Only when that specific combination has a confirmed overlay | 50 to 200 tokens per overlay |
| Examples | Paired before-and-after examples, if the install's profile store carries them | Only to resolve a genuine ambiguity between two plausible readings | 300 to 1000 tokens, loaded rarely |
| Full builder workflow | The entire `manage-writing-profile` skill | Never during drafting; only when building, correcting, or revoking a profile | Out of scope for runtime context entirely |

Never load raw evidence at runtime. The runtime reads the compact profile
only; raw evidence stays in the builder's separate, narrower-access store.

## What an install adapter does

A per-person install is a thin file naming the profile path, the person
identifier, and which surfaces this install is authorized to run on, such as
Claude Code, claude.ai, Cowork, or another runtime. It contains no voice
content of its own; voice content lives entirely in the profile the builder
produced. See [references/install-checklist.md](references/install-checklist.md).

## Relationship to other skills

This adapter selects the intended author's confirmed profile. `review-writing` reviews meaning and prose; `writing-diagnostics` supplies executable diagnostics and review records. `brand-renderer` applies the selected project profile or neutral defaults, and `review-deliverable` reviews deliverable readiness. These tools do not supply a person's voice. Apply the precedence above when their requirements overlap.

For a styled artifact, read [the build card](../_shared/build-card.md).
