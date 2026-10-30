---
name: discovery
description: "Synthesize supplied interviews and meeting notes into supported findings, or maintain a pursuit discovery ledger and ranked unanswered questions. Preserve exact quotations and distinguish research from proposed actions."
---

## Choose the requested task

Use the primary workflow below unless the request matches a mode in this table. For a matching mode, read its complete linked workflow and required references, then produce that mode's output. Preserve its calculations, failure handling and acceptance checks. One request does not require every mode.

| Requested mode | Complete workflow |
| --- | --- |
| maintain pursuit findings | [discovery-brief](_runtime/discovery-brief/WORKFLOW.md) |



# Discovery Synthesis

> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [`readout-brief.md`](_runtime/prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Turn discovery calls into sourced research artifacts for the current project. Use its industry, participants and terminology.

## Boundary with the discovery brief

This skill is the pipeline: raw call content in, structured artifacts out (JTBD
statements, pain points, verbatims, a TL;DR, next steps, a .docx). It produces
shareable research, ready for NotebookLM, a Claude Project, or a stakeholder
readout. It does not maintain the deal's discovery record. That is
`discovery-brief`, which owns the ranked two-column ledger and feeds the pursuit
brief. Run this to turn a transcript into research; run `discovery-brief` to keep
the deal's structured record and its open questions.

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

Read the full content carefully. Before generating output, internally map:

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
> *"[Exact or near-exact quote]"*
> [Speaker role], [context if helpful]

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

**Always produce:**
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
- Verbatims should be as close to exact wording as possible, flag if paraphrased: *(paraphrased)*
- Don't editorialize in pain points: describe what was said, not what you think they should do
- Opportunity areas are where you can add strategic thinking, be sharp and specific
- If the transcript is thin, say so explicitly rather than padding with weak inferences
- Flag gaps: if you needed information that wasn't in the transcript, note it under a **⚠️ Gaps & Assumptions** section at the end

---

## Integration Notes

**For NotebookLM:** The Markdown output is designed to be uploaded directly as a source document. The section headers and structured formatting help NotebookLM generate accurate summaries and Q&A.

**For Claude Projects:** Save the Markdown output as a project file. Future sessions in the same project will have the synthesis in context automatically.

**For project deliverables:** Use the requested document or research format. Connect opportunity areas to the project’s confirmed assessment framework when one exists.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion. Full
spec in [`release-gate.md`](_shared/release-gate.md).

1. Apply writing-integrity to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run quality-gate before you call it final.

Do not present the artifact as finished until both checks have passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
