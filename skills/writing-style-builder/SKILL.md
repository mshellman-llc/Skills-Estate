---
name: writing-style-builder
description: 'Build, confirm, update, correct, or revoke one person''s private writing-style profile from material they intentionally supply or authorize. Use when someone wants a personal voice profile created or changed, when connector access to their messages or documents is available but unconfirmed for this purpose, or when an existing profile needs correction, evolution, or deletion. Requires explicit authorization before analyzing any personal material; connector access alone is never consent. Does not apply anyone''s voice to output, which is personal-writing-style-runtime''s job.'
---

<!-- ESTATE-WRITING:BEGIN -->
Before writing, read the [writing standard](references/estate/writing.md). Apply it to every authored sentence. Review instructions and internal records too. Audience labels and file formats do not exempt prose from review.
<!-- ESTATE-WRITING:END -->


# Writing Style Builder

Turns material a person authorizes into a private, portable writing-style profile.
Never writes into this repository. The output profile is data owned by and stored
for that person, outside `house-skills`, at a path the operator's install
configuration names.

Before writing an Estate run record or other Estate-authored prose, read
[`_shared/build-card.md`](../_shared/build-card.md). Its artifact and prose gates
apply to the run record, not to the private profile's inferred voice patterns.

## Before anything else: authorization

Stop and confirm explicit authorization before reading any personal material,
even when a connector (email, chat, docs) is already available. Connector
access is infrastructure, not consent. Ask directly: whose voice, from which
sources, for what purpose. Log the answer as `authorization` on the profile
before step 1 begins. No authorization means no analysis: say so and stop.

## Workflow

1. **Collect evidence.** Gather the material the person named. Tag every unit
   with a provenance category before it touches inference:
   - `authored`: the person wrote this themselves, unprompted or lightly edited.
   - `quoted` / `forwarded`: someone else's words the person is relaying.
   - `templated` / `boilerplate`: structure supplied by a tool, form, or house
     template, with only the filled-in parts theirs.
   - `third-party`: another person is the author; the profiled person is only
     mentioned or CC'd.
   - `ai-generated`: a model produced this, and it is not evidence of the
     person's own voice even if they sent it.
   Only `authored` material, plus the person's own edits layered on
   `templated` material, feeds the profile. Everything else is discarded
   before inference, not filtered out later.

2. **Separate written and spoken evidence**, and within each, by channel,
   audience, relationship, and communication job. Jobs include informing,
   requesting, correcting, persuading, deciding, setting a boundary,
   coordinating a group, and supporting someone. See
   [references/schema.md](references/schema.md) for the field definitions.
   A profile that collapses these produces a runtime that sounds right in one
   channel and wrong in every other.

3. **Infer patterns, not facts.** Extract reusable tendencies, such as
   structure, directness, hedging, and calibration by audience, into the
   compact profile. Do not carry forward names, numbers, deal specifics, or
   other private facts that happened to appear in the evidence; the profile
   is a voice model, not an archive. If evidence is thin, weak, or
   contradictory for a dimension, record `insufficient_evidence` for that
   dimension rather than guessing.

4. **Record provenance, confidence, and conflicts** for every inferred
   pattern, plus `last_confirmed` and an append-only `history` of prior
   versions. When two evidence units disagree, keep both readings and flag the
   conflict rather than averaging them into something neither source said.

5. **Show the proposed profile to the person before creating or materially
   changing it.** Summarize what changed and why in plain terms tied to the
   evidence category, not raw excerpts. Wait for confirmation.

6. **Store raw evidence separately from the compact runtime profile**, at the
   narrowest access the install allows, and never inside this repository or
   any shared location. The runtime (`personal-writing-style-runtime`) reads
   only the compact profile, never the raw evidence.

7. **Support ongoing change.** A later run can correct one field, add new
   evidence, revoke automatic application while keeping the record, or delete
   the profile and its evidence outright. Every path updates `history`; delete
   removes the data, not just a flag.

Use [scripts/profile_builder.py](scripts/profile_builder.py) to turn tagged,
authorized evidence into a draft profile and to validate an existing one
against [references/schema.md](references/schema.md). Run
`scripts/profile_builder_selftest.py` against the synthetic fixtures in
[references/synthetic-fixtures/](references/synthetic-fixtures/) before
trusting a change to the builder itself. Never run it against a real profile.

## Honest insufficient-evidence outcome

If authorized material does not support a confident profile, whether because
there is too little of it, it is too uniform in channel, or it is dominated
by non-`authored` provenance, say so and stop rather than shipping a thin
profile dressed as a complete one. A declined build is a valid result.
