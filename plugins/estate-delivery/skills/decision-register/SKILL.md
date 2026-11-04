---
name: decision-register
description: Keep the client questions awaiting answers during release refinement as a decision register grouped by epic. Each question has an editable status and can carry an owner and saved answers; the register exports to the client's tracker as CSV or a decision log. Use to record questions from meeting notes, track which decisions are open or blocked, find questions without an owner, or export recorded answers. Do NOT use for discovery synthesis (discovery), recording decisions already made in the RAID log (delivery-status), or requirements capture (requirements-backlog).
---

# Decision register

The register is `content/questions.json`. Each question belongs to a group, usually an epic, and has a status. An owner, an answer and links to stories and tickets are optional. On the published Decisions page, people change a question's status, record answers and comment. The page saves those to the shared store for everyone.

## Record questions

Take questions from the sources the user supplied: refinement notes, ticket comments, the epic description or a meeting summary. Write each question as the decision it needs. Add one or two sentences of `context` that say what depends on it.

Fill in the other fields:

- `status`: one of Open, Proposed, Partly answered, Answered, Deferred, Blocked and Sandbox check.
- `owner`: only when the sources name one. Never assign an owner.
- `answer`: `Proposed answer` for the team's proposal, and `Answer` only for a decision the client recorded. Keep a recorded answer in the client's words.
- `stories` and `tickets`: the work that waits on the question.

A source that changes an answer supersedes the old answer only when it records the decision. A newer meeting summary that mentions a topic does not by itself close a question.

## Check

```bash
python3 scripts/decisions.py check --content <project>/content --tickets <project>/tracker/tickets.json
```

The check lists unknown groups, stories and tickets and any duplicate ids. It also counts questions by status and names the ones with no owner.

## Export answers

Read the `answers` collection from the published page with the artifact data tool and save it as JSON. Then run:

```bash
python3 scripts/decisions.py export --content <project>/content --saved answers.json --out <project>/exports
```

The export writes two files:

- `decisions.csv`: one row per question and ticket, for import as tracker comments.
- `decisions.md`: a decision log grouped by epic.

Saved statuses and answers from the page override the authored ones in both files. Ask the user before writing anything to the tracker. The export prepares the file; the import is the client's action or needs their approval.

## Page behavior

The page behavior follows rules R-DEC-1 and R-DEC-2 in [the review rules](_runtime/review-site-kit/references/review-rules.md). A closed card shows the question and its status. The owner, the answer, the context, linked work, the answer form and comments sit inside the card. Hide answered and No owner only filter the list. The epic list counts questions per group.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
