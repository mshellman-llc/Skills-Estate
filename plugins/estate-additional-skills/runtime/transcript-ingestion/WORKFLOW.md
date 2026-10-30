---
name: transcript-ingestion
description: 'Preserve, normalize, identify, and index a consulting meeting transcript for a confirmed client opportunity or engagement. Use when a transcript, call recording export, meeting notes file, VTT, or plain-text conversation must enter the Knowledge Hub. Do not use for call preparation, general meeting summarization, or unsupported promotion of an AI summary into canonical truth.'
---


# Transcript ingestion

Turn one meeting record into a durable, searchable source without loading every
transcript into later AI sessions.

## Required identity

Confirm the client and the opportunity or engagement before filing. Use a stable
context ID beginning with `opp-` or `eng-`. Stop when the meeting could belong to
more than one record.

## Ingest

1. Preserve the raw source without changing its bytes.
2. Create a normalized Markdown copy with transcript ID, client ID, context ID,
   context type, meeting date, title, participants, source hash, raw-file
   location, and ingestion time.
3. Add or update one entry in `transcripts.index` with topics, decisions, actions,
   and the normalized file location.
4. Register the raw transcript in `evidence.sources`.
5. Extract facts, decisions, commitments, actions, and open questions as proposed
   claims. Keep the transcript locator and relevant passage with each proposal.
6. Send proposed claims through `evidence-core` before promoting them into a
   lifecycle record.

An AI summary is navigation, not evidence. Preserve the raw transcript and cite
it when a claim matters.

## Available tools

Use `scripts/normalize_transcript.py` on a local surface. It accepts Markdown,
plain text, and VTT; preserves the source; creates Markdown; and refuses to
overwrite an existing transcript. Run its selftest after changes.

On Cowork, Claude.ai, or another surface without the script, apply the same
record contract with available file tools. If files cannot be persisted, return
the normalized Markdown and exact intended Hub targets. State `patch-returned`.

## Boundaries

- Never guess client or engagement identity from a participant name alone.
- Never delete or replace the raw transcript.
- Never copy a transcript into several client folders.
- Never treat a generated summary as a meeting quote.
- Never promote an unsupported interpretation into canonical client knowledge.
- Search `transcripts.index` before opening transcript bodies in later work.

Return the resolved identity, raw and normalized locations, source hash, index
change, proposed claim count, evidence result, and persistence state. Format the
durable run record with [`output-contract.md`](_shared/output-contract.md).

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
