---
name: prepare-session-handoff
description: 'Produce a structured end-of-session handoff so a fresh agent can resume without re-explanation. Use when the user says session handoff, wrap up session, hand off, or summarize before I clear, or signals a /clear or new chat. Also use proactively under context pressure: an auto-compact warning, running low on context, or a long session about to be interrupted. Covers provenance, decisions, shipped changes, rejected approaches, user corrections, key files, running state, and open questions. Do not use for status reports written for humans, retrospectives, PR descriptions, commit messages, or memory consolidation.'
---


# Prepare session handoff

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`email-slack.md`](../writing-diagnostics/references/registers/email-slack.md). Inputs, not a final pass.**

Produce a handoff so the user can clear context and start a fresh agent without losing continuity. The next agent should be able to resume by reading this alone.

This is a **context-handoff artifact**, not a status report. The audience is a future instance of you, not a stakeholder. Write it the way a competent engineer hands off at end of shift: paths, commands, decisions, and the things that will otherwise be rediscovered the hard way.

## Two forms

**Full form.** End of session, before `/clear`, or when context is nearly exhausted. Use the complete template below. This is the default.

**Short form.** A mid-session pivot, where the user is moving to unrelated work in the same chat and just needs something pasteable. Five to eight lines: what was done, where it lives, what's left, pick up here. No file written unless asked. Offer this rather than the full template when the session is being *redirected* rather than *ended*.

If it isn't obvious which is wanted, produce the full form. It's cheaper to have too much handoff than too little.

## Step 1. Stamp the provenance

Run this once, first. It is the only filesystem lookup this skill performs:

```bash
date -u '+%Y-%m-%d %H:%M UTC'; pwd; git branch --show-current 2>/dev/null; git rev-parse --short HEAD 2>/dev/null; git status --porcelain 2>/dev/null | wc -l
```

Why this matters more than it looks: a handoff is a **snapshot**, and multi-session or parallel-agent work is common. Without a timestamp and commit, the next agent has no way to tell whether your "deferred work" list is still true or whether another session already shipped half of it. Trusting a stale list means duplicated work or a clobbered tree. The stamp converts "trust me" into "diff me."

This is a narrow exception to the no-auditing rule below. Capture HEAD; do not go reading logs or diffing.

## Step 2. Gather from the session, not the disk

Pull state from these, in order:

- **Plan or spec files** referenced this session. Name the path the user or you actually used. Do not guess at a conventional location; if no plan file drove the session, say so.
- **Task/todo list state**, whatever the harness calls it. Any in-progress or pending items.
- **Background processes** you started. Their IDs are load-bearing and the next agent cannot recover them.
- **Files created or modified** this session. You know what you touched; don't grep to rediscover.
- **Memory files** written or updated, at whatever memory directory this environment provides.
- **Corrections the user made to you.** The most expensive thing to lose, because a fresh agent will cheerfully repeat the mistake.
- **Approaches tried and abandoned**, and why.
- **Unresolved questions.** Things you asked that never got a clear answer, or things the user asked that got deflected.

**Do not audit the filesystem.** Beyond the provenance stamp: no `git log`, no broad `Glob` sweeps, no re-reading files to check your work. This is synthesis of what happened in THIS session. If you didn't touch it this session, it doesn't belong here.

## Step 3. Output template

Use this structure, every time:

```
# Session Handoff: <one-line title of what this session was about>

Written: <UTC timestamp> | <branch> @ <short SHA> | tree <clean|N files dirty> | cwd <absolute path>

## Where it started
<2-3 sentences: what the user asked for, key framing or constraints that emerged>

## Decisions locked + what shipped
- <decision or change>. <why, and where it lives (absolute path if a file)>
- Tried and rejected: <approach>. <why it failed, so it isn't retried>
- Corrected by user: <what you had wrong>. <what's actually true>

## Key files for next session
- `<absolute path>`. <why the next agent should read this first>
- Plan/spec file: `<path>` (if one drove the session). List this first
- Memory files touched: `<paths>`

## Running state
- Background processes: <IDs + what they are + how to kill>, or "none"
- Dev servers / ports: <url + port>, or "none"
- Worktrees / branches: <absolute path>, <live | merged | abandoned>, or "none"
- Uncommitted work in the tree: <what, and whether it's yours>, or "none"

## Verification: how to confirm things still work
- `<command>`. <expected outcome>

## Deferred + open questions
- Deferred: <item>. <why pushed>. Touches: `<paths>`
- Open: <question needing the user's input>. <context>

## Pick up here
<1-2 sentences: the single most likely next action for a fresh agent>
<If any deferred item touches files, add: "Re-verify the deferred list against HEAD before acting. It was true at the stamp above, not necessarily now.">
```

## Step 4. Deliver it

**Always print the full handoff in chat.** That is the primary channel and it is never skipped.

**Also write it to a file, by default.** The filename is always:

```
handoff-<YYYY-MM-DD-HHMM>-<short-kebab-topic>.md
```

The directory is whichever of these the environment actually provides, in order. Resolve it, do
not assume it:

1. A handoffs directory the user or the project has already named. If one exists, it wins.
2. A persistent handoffs location explicitly supplied by the current harness or its configuration. Do not derive one from a host name, a conventional home directory, or another account's previous session.
3. No persistent location. Then write nothing and say so in one line.

Create the directory if it does not exist. Say the resolved path in one line after the chat
output. Do not narrate the write.

Skip the file if the user says "chat only", if this is the short form, or if the filesystem is absent or ephemeral. Ephemeral matters: some hosted environments give you a writable sandbox that disappears when the session ends, so a file written there is worse than no file, because it looks saved and is not. If you can't tell whether the path persists, say so in one line and rely on the chat output, which is the channel that always works.

Never write the handoff anywhere other than the handoffs directory, and never update memory from this skill; memory is a separate concern with its own rules.

## Hard rules

1. **Never invent state.** If a section has nothing to report, write "none". Do not omit the section. Structure stability is the whole point: the next agent learns where to look and can trust that a missing item means nothing happened, not that you forgot.
2. **Absolute paths always.** The next agent may have a different working directory.
3. **If a plan or spec file drove the session, name it first** in Key files, so it gets read before anything else.
4. **Background process IDs are critical.** Without them in Running state, with the kill command, the next agent cannot find those processes at all.
5. **No emojis, no hype, no "great progress today".** Terse and concrete: paths, commands, IDs, decisions.
6. **The handoff is a snapshot and should say so.** Deferred work especially. Never write the deferred list as if it were current truth.

## Anti-patterns

- Summarizing the last three turns and calling it a handoff. Review the whole session.
- Relative paths.
- Skipping "Running state" because nothing is running. Write "none".
- Writing the file anywhere other than the handoffs directory, or quietly updating memory.
- A retrospective. "What went well / what went poorly" is not wanted. **This is different from "Tried and rejected".** Recording a failed approach so it isn't repeated is essential; grading the session's vibe is noise. Keep the former, drop the latter.
- Recommending next steps beyond the single "Pick up here" line. The next agent decides.
- Padding thin sections to look thorough. A short honest handoff beats a long speculative one.
