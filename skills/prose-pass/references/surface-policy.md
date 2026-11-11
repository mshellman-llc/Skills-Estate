# Surface policy

Prose-pass governs authored language wherever a person reads it. The governing question is who
reads the words, not which application stores them.

## In scope

- Conversation responses, progress updates, clarifying questions, and handoffs.
- Pull requests, code reviews, issue and ticket bodies, commit messages, release notes, and code
  comments written for maintainers.
- Human-facing README files, runbooks, notes, and decision records.
- UI labels, validation messages, tooltips, onboarding copy, alt text, and generated help text.
- Email, Slack, outreach, proposals, SOWs, decks, reports, pages, workbooks, and PDFs.

Apply the voice while drafting. A later cleanup is a recovery path, not the normal authoring model.

## Protected material

Do not rewrite text whose value depends on exact preservation:

- Raw evidence, transcripts, logs, exports, ledgers, and source-system values.
- Code syntax, commands, identifiers, schemas, serialized keys, and machine-readable data.
- Direct quotations, legal language, defined terms, and client wording that must remain verbatim.
- Generated or vendored files whose source owns the text.
- AI instructions, agent guidance, indexes, registers, ledgers, schemas, and generated audit records.

For a mixed surface, apply prose-pass to the authored prose and leave the protected spans intact.
Fenced code, inline code, and blockquotes provide that boundary in Markdown.

## Proof by surface

| Surface | Required proof |
|---|---|
| Ephemeral conversation or status | Apply the rules while writing; read once for generic filler, uniform rhythm, and weakened uncertainty. |
| Ordinary email or Slack | Hold the voice while drafting; read once against the email and Slack register. No checker run, no receipt. |
| Consequential email or Slack | Treat as a final narrative artifact: full rewrite, checker, receipt. See below. |
| Persisted human-facing prose supported by the checker | Run `prose_check.py`; rewrite until it reports no findings. |
| Final narrative artifact | Run the full rewrite and checker; emit and validate a prose receipt. |
| AI-facing, protected evidence, or machine text | Use structural and accuracy checks; do not run prose-pass or emit a receipt. |

The checker supports a finite set of file formats. Unsupported storage does not waive the voice
rule; it changes the proof from a script run to a reading pass.

## What makes a message consequential

Weight follows what the message decides, not how long it is or which application sends it. A short
Slack line that approves a number is heavier than a page of context that approves nothing. Elevate
an email or a Slack message to the full pass when it carries any of:

- **A financial figure.** A price, a rate, a range, a budget, a variance.
- **Contract scope.** What is in, out, optional, or deferred.
- **An approval status.** Granted, withheld, conditional, or pending.
- **A commitment.** A date, a deliverable, an owner, a headcount.
- **A go or no-go conclusion.** Any decision a reader will act on.

The first four map to the fail-closed assertion classes in `quality-gate/scripts/quality_gate.py`,
so one message is elevated by the same test that fails a release record. Deciding twice, in two
vocabularies, is how the two drift apart.

When a message is elevated, the qualifier travels with the figure. A rate quoted without its
"estimated", a date without its "subject to", or a scope line without its exclusion is a defect the
voice pass must not introduce and must not remove.
