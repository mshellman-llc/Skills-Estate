---
name: discovery-synthesis
description: 'Transforms raw discovery call content, notes, transcripts, Granola/Fathom recordings, or uploaded files into structured research outputs: JTBD statements, pain points with severity, opportunity areas, key verbatims, speaker-attributed insights, a TL;DR, and next steps. Outputs Markdown and .docx ready for NotebookLM, Claude Projects, or stakeholder sharing. Trigger when the user shares meeting content or says synthesize this call, pull insights from this transcript, map the pain points, extract JTBDs, or what did we learn; offer proactively when a transcript or discovery notes appear in context. For the deal discovery record, ranked ledger or open questions, select the maintain pursuit findings mode and read discovery-brief.'
---


# Discovery Synthesis

## Caller context and source boundary

Use only the current task's supplied or explicitly authorized account, project sources and destinations. Resolve record names such as `client.profile` within that confirmed context; they are logical slots, not a default personal store. Connector availability alone does not authorize searching another account. Organization-specific pricing, capability catalogs, approval roles and policies must be supplied or confirmed; absent material context remains an explicit gap. Keep reusable package files immutable during a client task and save client records outside them. Never populate an example with private source material.


> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Turn discovery calls into sourced research artifacts for the current project. Use its industry, participants and terminology.

## Boundary with the discovery brief

This skill is the pipeline: raw call content in, structured artifacts out (JTBD
statements, pain points, verbatims, a TL;DR, next steps, a .docx). It produces
shareable research, ready for NotebookLM, a Claude Project, or a stakeholder
readout. The primary workflow handles synthesis. The maintain pursuit findings
mode uses [discovery-brief](../discovery-brief/SKILL.md), which owns the ranked
two-column ledger and feeds the pursuit brief. Select that complete workflow
when the request is to update the deal's structured record or its open questions.
The portable Discovery package embeds both workflows; no separate installation
is needed for the ledger mode.

## Supported Input Types

| Input Type | How to Handle |
|---|---|
| Pasted text / typed notes | Use directly |
| Uploaded .txt / .md | Read file contents |
| Uploaded .docx | Use the `docx` skill to extract text first. Find it in your available skills; do not assume a path. |
| Uploaded .pdf | Use the `pdf` skill to extract text first. Find it in your available skills; do not assume a path. |
| Granola transcript | Pull it through the Granola MCP connector (`get_meeting_transcript`, `list_meetings`). There is no Granola skill. |
| Fathom transcript | Ask user to paste or export the transcript |
| Audio / video file | Inform user that direct audio processing isn't supported; ask them to paste a transcript or use Granola/Fathom to export it first |

---

## Step 1: Intake & Clarification

Before synthesizing, gather the following context, quickly, in one message if possible. If some of this is obvious from the content, skip asking and infer.

1. **Client name / industry** (if not in the transcript)
2. **Meeting type.** Discovery, assessment, stakeholder interview, etc.
3. **Who was in the room?.** Roles on both sides (consulting team and client)
4. **Any known focus area?.** E.g., CPQ, quoting process, order management, pricing

If the user is in a hurry, proceed with what you have and flag assumptions at the top of the output.

---

## Step 2: Synthesis Analysis

Read the supplied content completely. A summary is secondary evidence and cannot become a verbatim transcript. Keep uncertain speaker labels uncertain. Retain meaningful dissent and distinguish one person's observation from a shared pattern. Before generating output, internally map:

- **Speaker attribution.** Identify who is a consulting-team voice vs. a client voice. Client voices are the research signal. Consultant voices provide context and questions.
- **Signal types.** Distinguish between explicit pain statements ("we can't do X"), implicit friction ("it takes us 3 days to..."), aspirational statements ("what we really want is..."), and workarounds ("so we built a spreadsheet that...").
- **JTBD signals.** Look for statements about outcomes the client is trying to achieve, not features they want. Use the format: *When [situation], I want to [motivation], so I can [outcome].*
- **Severity indicators.** Words like "always", "never", "every time", "manual", "hours", "days", "can't", "broken", "nightmare" signal high severity. Vague frustration or one-off mentions signal low severity.

---

## Step 3: Generate Research Output

Produce the full artifact in this exact structure:

---

### 🗒️ SESSION SUMMARY

**Client:** [Name / Industry]
**Date:** [Date if available, otherwise "Not specified"]
**Meeting Type:** [Discovery / Assessment / Stakeholder Interview]
**Participants:** [Roles, flag if inferred]
**Synthesized by:** [Actual assistant or author]

**TL;DR:**
2–4 sentences. What is the core problem this client is trying to solve? What is the biggest opportunity? What is the most urgent pain?

---

### 🎯 JOBS TO BE DONE

Use the canonical JTBD format for each job:
> *When [situation/trigger], I want to [action/motivation], so I can [desired outcome].*

Group into functional categories if multiple jobs exist (e.g., Quoting, Pricing, Order Management, Approvals, Reporting). Aim for 3–8 JTBD statements. Don't pad, quality over quantity.

For each JTBD, add:
- **Source:** [Direct quote or paraphrased signal from transcript]
- **Speaker role:** [e.g., VP of Sales, Ops Manager, anonymized if names used]

---

### 🔥 PAIN POINTS

For each pain point:

**[Pain Point Title]**
- **Description:** What the problem is in plain language
- **Severity:** 🔴 High / 🟡 Medium / 🟢 Low
- **Frequency:** Always / Often / Occasionally / Once mentioned
- **Evidence:** Direct quote or paraphrased signal
- **Speaker role:** [Role]

Severity rubric:
- 🔴 **High.** Explicit, repeated, or described with urgency ("we can't", "it breaks every time", "someone has to manually...")
- 🟡 **Medium.** Mentioned with frustration but not blocking ("it's annoying", "we'd love to fix this")
- 🟢 **Low.** Mentioned once, vaguely, or as a nice-to-have

---

### 💡 OPPORTUNITY AREAS

Synthesized themes where the project team could create value. These are NOT feature requests, they are strategic opportunity spaces inferred from the pain points and JTBDs.

For each opportunity:
- **Opportunity:** [Name it concisely]
- **Why it matters:** [Link to specific pain points or JTBDs]
- **Potential approach:** [1–2 sentences on how this might be addressed, keep high-level]

Aim for 3–5 opportunity areas. These should feel distinct and non-overlapping.

---

### 💬 KEY VERBATIMS

5–10 direct quotes from client speakers that are the most revealing, emotionally resonant, or strategically significant. These are the "sticky" moments, the things you'd put on a slide to make a stakeholder lean forward.

Format:
> *"[Exact source quote]"*
> [Speaker role], [context if helpful]

Preserve the exact words and grammar of a quote with its speaker and timestamp or source location. Never invent a representative quote. Label a paraphrase as a paraphrase outside quotation marks. Select only useful quotes present in the source, even when fewer than five exist.

Do not include consultant quotes here unless they directly provoked a revealing client response.

---

### 👥 SPEAKER-ATTRIBUTED INSIGHTS

Brief profiles of each distinct client voice. Useful for stakeholder mapping.

**[Role / Name if provided]**
- **Apparent priorities:** [What they seemed to care most about]
- **Tone:** [e.g., frustrated, optimistic, skeptical, pragmatic]
- **Key concerns:** [Top 1–2 things they raised]
- **Influence signals:** [Did they seem like a decision-maker, influencer, or end user?]

---

### ✅ RECOMMENDED NEXT STEPS

Recommend specific follow-ups supported by the findings. Name the responsible project role when the source identifies it; otherwise leave ownership open.

Examples:
- "Follow up with [role] on [specific topic]. They seemed most receptive."
- "Validate assumption that [X]. It came up once and was not confirmed."
- "Map current quoting workflow, there are conflicting signals about step ownership"
- "Flag [Y] as a potential scope risk in the assessment"

---

## Step 4: Output Delivery

Use the user's requested format and length. The full structure above is the default when no narrower format is requested.

**Default delivery:**
1. The full structured artifact above, rendered in clean Markdown in-chat
2. A Markdown file in the project’s existing output folder when files can be saved; otherwise provide the complete content in chat.

**Also produce a .docx if the user requested it** (or offer it proactively):
- Use the `docx` skill to render the artifact as a formatted Word document. Find it in your available skills rather than assuming an install path.
- Apply clean heading hierarchy: H1 for section names, H2 for individual items
- Save the Word document beside the Markdown output in the project’s output folder.
- Link the saved files using the host’s supported attachment or file-link mechanism.

---

## Tone & Quality Standards

- Write in third person for pain points and JTBDs ("The client cannot..." not "You cannot...")
- Verbatims preserve exact source wording. Present paraphrases separately and label them; do not put reconstructed wording in quotation marks.
- Don't editorialize in pain points: describe what was said, not what you think they should do
- Opportunity areas are where you can add strategic thinking, be sharp and specific
- If the transcript is thin, say so explicitly rather than padding with weak inferences
- Flag gaps: if you needed information that wasn't in the transcript, note it under a **⚠️ Gaps & Assumptions** section at the end

---

## Integration Notes

**For NotebookLM:** The Markdown output can be used as a source document after an authorized upload is confirmed by the destination. The section headers and structured formatting help NotebookLM generate accurate summaries and Q&A.

**For Claude Projects:** Prepare a Markdown file suitable for the project. A local save does not upload it or establish future-session access. Use an authorized destination write when requested, then read back the saved record before claiming upload or availability.

**For project deliverables:** Use the requested document or research format. Connect opportunity areas to the project’s confirmed assessment framework when one exists.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion. Full
spec in [`release-gate.md`](../_shared/release-gate.md).

1. Apply writing-integrity to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run quality-gate before you call it final.

Do not present the artifact as finished until both checks have passed.
