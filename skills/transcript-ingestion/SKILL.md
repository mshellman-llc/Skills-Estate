---
name: transcript-ingestion
description: "Preserve, normalize, and index a supplied transcript for a confirmed project, client, opportunity, or engagement."
---

# Transcript ingestion

Read [shared workflow](references/estate/workflow.md). For a rendered or branded artifact, read [brand policy](references/estate/brand.md) before choosing visual values. These references are generated from the canonical policies when the estate builds.

Identify the meeting, date, source, participants, destination context, and stable transcript ID. If the destination context is ambiguous, resolve it before writing; do not attach a meeting to a client based solely on a matching name.

Preserve the raw input and its hash. Normalize a separate copy for encoding, speaker labels, and timestamps without changing the words. Keep uncertain speakers uncertain. Do not convert an AI summary into a verbatim transcript.

Check for an existing source ID or hash before ingestion. Make repeated ingestion idempotent and preserve revisions when the source changes. Record the raw and normalized locations, provenance, and index entry.

Use the storage system's authorized write path and verify the indexed record can be retrieved. Pass findings to discovery-synthesis or discovery-brief when requested; ingestion alone does not approve claims or update scope.
