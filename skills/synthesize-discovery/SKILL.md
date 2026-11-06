---
name: synthesize-discovery
description: 'Synthesize supplied discovery calls, interview notes, transcripts or Granola and Fathom exports into sourced findings: job statements, pain points with severity, exact verbatims, speaker-attributed insights, a TL;DR, open questions and next steps. Use when the user shares meeting content and asks what was learned, to pull insights from a transcript, map pain points or extract JTBDs. For the deal discovery record, ranked ledger or open questions, select the maintain pursuit findings mode and read maintain-discovery-record.'
---


# Synthesize discovery

## Caller context and source boundary

Use only the current task's supplied or explicitly authorized account, project sources and destinations. Resolve record names such as `client.profile` within that confirmed context; they are logical slots, not a default personal store. Connector availability alone does not authorize searching another account. Organization-specific pricing, capability catalogs, approval roles and policies must be supplied or confirmed; absent material context remains an explicit gap. Keep reusable package files immutable during a client task and save client records outside them. Never populate an example with private source material.


> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../writing-diagnostics/references/registers/readout-brief.md). Inputs, not a final pass.**

Turn discovery calls into sourced research findings for the current project. Use its industry, participants and terminology.

## Boundary with the discovery brief

This skill is the synthesis pass: raw call content in, sourced findings out. The
maintain pursuit findings mode uses [maintain-discovery-record](../maintain-discovery-record/SKILL.md),
which owns the deal's ranked two-column ledger, its open questions and the feed
into the pursuit brief. Select that complete workflow when the request is to
update the deal's structured record or ask what is still unknown about the
account. A synthesis can supply new findings to that ledger; it does not replace
it. The portable Discovery package embeds both workflows; no separate installation
is needed for the ledger mode.

## Supported input types

| Input type | How to handle |
|---|---|
| Pasted text or typed notes | Use directly |
| Uploaded .txt or .md | Read the file contents |
| Uploaded .docx | Use the `docx` skill to extract text first. Find it in your available skills; do not assume a path. |
| Uploaded .pdf | Use the `pdf` skill to extract text first. Find it in your available skills; do not assume a path. |
| Granola transcript | Pull it through the Granola MCP connector (`get_meeting_transcript`, `list_meetings`). There is no Granola skill. |
| Fathom transcript | Ask the user to paste or export the transcript |
| Audio or video file | Direct audio processing is not supported. Ask for a transcript or a Granola or Fathom export. |

## Workflow

1. Confirm the client, meeting type, who attended on each side and any known focus area. Infer what the content makes obvious and ask once for the rest. When the user wants speed, proceed and state the assumptions at the top.
2. Read the supplied content completely. A summary is secondary evidence and cannot become a verbatim transcript. Keep uncertain speaker labels uncertain.
3. Separate client voices from consulting-team voices. Client statements are the research signal; consultant questions are context.
4. Record each finding with its source location and speaker role. Keep one person's observation distinct from a pattern several people share, and retain meaningful dissent.
5. Rate severity from the source wording. Blocking, repeated or urgent statements are high. Frustration without a block is medium. A single vague mention is low. State the reason for each rating.
6. Write the output in the format and length the user asked for. Without a narrower request, cover the sections below in plain headings.
7. Run the release gate.

## What the synthesis covers

The TL;DR gives the core problem, the most urgent pain and the largest opportunity in two to four sentences, with the session details it draws on.

Job statements use *When [situation], I want to [motivation], so I can [outcome].* Write a job statement only where the source shows the outcome the client wants. Cite the signal and the speaker role for each one. `frame-jobs-to-be-done` holds the bar these statements must meet.

Pain points state what was said in plain language, with severity, frequency, evidence and speaker role. Describe the problem; recommendations belong elsewhere.

Opportunity areas are the team's inference from the pain points and job statements. Label them as proposed and link each one to the findings it rests on.

Verbatims are exact quotations from client speakers. Preserve the exact words and grammar of a quote with its speaker and timestamp or source location. Never invent a representative quote. Label a paraphrase as a paraphrase outside quotation marks. Select only useful quotes present in the source, even when there are few. Include a consultant quote only when it provoked a revealing client response.

Speaker-attributed insights describe each distinct client voice: apparent priorities, key concerns and influence signals, each tied to what the person said.

Open questions and next steps name what the session left unconfirmed, the follow-up that would answer it and the responsible project role when the source identifies one; otherwise leave ownership open. Send questions that belong to the deal record to the maintain pursuit findings mode.

Gaps and assumptions list information the analysis needed but the source did not contain. When the transcript is thin, say so instead of padding with weak inferences.

## Output delivery

Render the synthesis in Markdown in chat. Save a Markdown file in the project's existing output folder when files can be saved; otherwise provide the complete content in chat. When the user asks for a Word document, use the `docx` skill from your available skills and save it beside the Markdown file. Link saved files through the host's supported file-link mechanism.

A local save does not upload a file to NotebookLM or a Claude Project. Upload only to an authorized destination the user requests, and read back the saved record before claiming it is available there. When the project has a confirmed assessment framework, connect opportunity areas to it.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion. Full
spec in [`release-gate.md`](../_shared/release-gate.md).

1. Apply review-writing to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run review-deliverable before you call it final.

Do not present the artifact as finished until both checks have passed.
