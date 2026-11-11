---
name: spec-writer
description: 'Rigorous feature specification process. Produces a self-contained HTML spec with rendered mockups, all UI states, complete file manifest (CREATE/UPDATE/DELETE/READ/MIGRATION), and verifiable done criteria. Use before writing any code for a non-trivial feature.'
---

# Spec Writer

> **Before writing: [`build-card.md`](../_shared/build-card.md) plus
> [`readout-brief.md`](../prose-pass/references/registers/readout-brief.md). Inputs, not a final pass.**

Produce a specification document before touching any code. The spec is approved by the user before implementation begins. No exceptions.

## When to use

- Any feature that touches more than 2 files
- Any feature that changes a route, API contract, or data model
- Any time you are about to build something and feel like you already know how it works, that feeling is the trigger

## The four phases

---

### Phase 1: Read everything before writing anything

This phase has one rule: **read the actual code, not your memory of it.**

For every file that is directly involved or plausibly tangentially related:

- Open it and read it
- Note what it does, what it calls, what it writes to, what props it takes
- Look for dependencies you didn't expect: interactive components, destructive writes, hard-coded foreign key requirements, deprecated patterns still in use

Document specific findings. "DecisionsSection is already interactive, it calls `/api/clients/[id]/decisions` PATCH and uses `useToast`" is a finding. "I checked the section components" is not.

**If a finding changes the design:** state it explicitly in Section 01 of the spec before proposing any solution.

**Common traps to check:**
- Does an existing function do DELETE+INSERT (destructive) instead of UPSERT? The chat's model update tool cannot call it.
- Does a route require a foreign key (e.g. `sessionId`) that won't be available in the new context?
- Are there components that look read-only but actually have interactive API calls?
- Does existing code use deprecated patterns (old brand colors, wrong auth helpers)? Note it, do not fix it in this spec unless it's blocking.

**Do not write the spec until Phase 1 is complete for all relevant files.**

---

### Phase 2: Write the spec as a self-contained HTML file

Save the spec as an `.html` file the user can open in a browser. Every section below is required.

#### Section 01: What we're building and why
- The problem being solved in 2–3 sentences
- What is explicitly NOT changing: list it, don't assume the user knows
- Any design corrections from Phase 1 research (things the initial plan got wrong, and why)

#### Sections 02–N: Mockups (one per key state)

Minimum states to show:
1. **Empty / first use.** No data, first time a user lands here
2. **Populated / active.** Real data, main interaction in progress
3. **Any secondary surface.** Panel open, modal active, split-pane variant

Each mockup is a **fully rendered HTML UI** embedded in the spec file:
- Inline styles only: no Tailwind, no external CSS
- Exact brand tokens (no approximations):

```
Deep Navy    #080F28    (hero bg, wordmark)
Navy Blue    #1E3070    (dark accents)
Teal         #1A6B6B    (CTAs, active states, primary accent)
Teal Pale    #E0F0F0    (surface fills, card borders)
Sand         #F7F5F0    (light backgrounds, page bg)
White        #FEFEFE    (card surfaces)
Steel Blue   #8A9BB8    (secondary text, labels, muted)
Body         #15161A    (primary body text)
Secondary    #585858    (secondary text)

Card border:    1px solid #E0F0F0
Card radius:    8px
Section header: 4px × 24px #1A6B6B teal left bar
Metric cards:   linear-gradient(135deg, #080F28 0%, #1E3070 100%)
Fonts:          Plus Jakarta Sans (primary), DM Mono (code/labels/IDs)
```

- Show real navigation: left rail, subnav, topbar, breadcrumb, whatever the app has
- Show real interactive states: active nav items, disabled buttons, streaming indicators, badge counts
#### Section: All UI states

Every state the component must handle. For each:
- What triggers it
- What renders
- What the user can do (or can't do)

Required minimum: empty, loading/streaming, populated, error, return visit (persistence check).

#### Section: Data model changes

- Additive only where possible: state explicitly if a column or table is being dropped
- Each new table: every column with type, constraints, defaults, FK targets
- Each new column on existing tables: table name, column name, type, constraint, why it's there
- RLS policies: who can read/write, what the policy clause is
- Note any UNIQUE constraints that affect upsert behavior

#### Section: API design

For every new route:
- Method, path, auth check (what happens if auth fails)
- Request body schema
- Response shape (success and error)
- Edge cases: what if the resource doesn't exist, what if a dependency is missing

For every modified route:
- What changes (be surgical: "add optional `conversationId` param alongside existing `sessionId`")
- What stays identical: name it so the reader knows the regression surface is bounded
- Regression risk: what could break if this change is wrong

#### Section: Complete file manifest

A table with columns: **Op | File path | What and why**

Operations:
- `CREATE`: new file, full purpose described
- `UPDATE`: existing file, exactly what changes and why (not "minor updates")
- `DELETE`: file being removed, what replaces it
- `READ`: files read to inform the design, no changes, but must be verified current before implementation
- `MIGRATION`: SQL migration with table/column changes described
- `CONFIG`: env var, Vercel setting, package.json change

End the manifest with an explicit statement: **"Files guaranteed not touched: [list them]."** If a file is not on the manifest, it will not be touched.

#### Section: Done criteria

Each criterion is a specific, observable, verifiable outcome. Format:

> [User action] → [observable result]. *Verified by: [exact confirmation method].*

Example:
> Click "Decisions" in subnav while on /chat → panel opens with DecisionsSection rendered. *Verified by: screenshot of split-pane + Supabase decisions row updated to 'resolved' after clicking Approve.*

"The code looks right" is never a valid verification method.

Always end with: `npm run verify` (tsc + vitest + next build) passes clean. *Verified by: command output.*

#### Section: Out of scope

Explicitly list what is NOT being built in this phase. Each item should note when it gets addressed (next spec, separate fix, future phase, post-MVP).

---

### Phase 3: Honesty requirements

State these explicitly in the spec or in conversation before approval:

**What can be guaranteed:**
- Visual design (colors, fonts, spacing, layout) translates 1:1 because they are inline styles using exact design tokens, no translation layer
- Navigation structure: routes, what renders where

**What cannot be guaranteed:**
- 100% functional fidelity, mockups are static, apps have dynamic states, real latency, real data shapes from the database, edge cases the mockup didn't show
- Behavior under error conditions not explicitly mocked

**The right approach:**
Build mockups as actual React component structure (not static HTML exported as an artifact to "translate from"). When the mockup IS the first draft of the component, the gap between spec and implementation collapses.

---

### Phase 4: Pre-presentation checklist

Run this before presenting the spec to the user:

- [ ] Did I read every file in the relevant area, including ones I didn't expect to matter?
- [ ] Did I find anything in Phase 1 that changes the design? If yes, is it documented in Section 01?
- [ ] Do the mockups show real brand colors and real navigation, not placeholder grays?
- [ ] Does the file manifest include files that IMPORT from files I'm changing?
- [ ] Are route handlers that call changed libraries on the manifest?
- [ ] Are the done criteria specific enough that someone other than me could run them?
- [ ] Is the out-of-scope section complete, does it capture everything that was discussed but not built?

If any item is "no," fix it before presenting.

---

## What makes a spec approvable

The user should be able to read the spec and answer yes to all of these:

1. I can see what it looks like, the mockups are real, not wireframes
2. I know exactly what files get touched, the manifest is exhaustive
3. I understand what could go wrong, the states section covers failure modes
4. I can verify it's done, the criteria are specific and observable
5. I know what's NOT in scope, there are no hidden assumptions about what gets built

If the user asks "what about X?" and X is not in the spec, that's a spec gap. Close it before starting implementation.

---

## Output format

Output path: `docs/specs/spec-[feature-name].html`

The file is self-contained HTML. No external dependencies except Google Fonts CDN for Plus Jakarta Sans and DM Mono. The user opens it in a browser to review.

Do not save intermediate planning files, notes, or drafts. One output: the spec HTML file.

---

## After approval

Do not start implementation until the user explicitly approves the spec. "Looks good" or "I approve" counts. "What do you think?" does not, that's a question, not approval.

When approved: implement one piece at a time, verify each piece before moving to the next, run `npm run verify` before claiming anything is done.

## Release gate (required)

Before you deliver, run the gate. This is a required step, not a suggestion. Full
spec in [`release-gate.md`](../_shared/release-gate.md).

1. Run prose-pass on the prose. It rewrites AI patterns and gates the result. For
   a final artifact it emits a receipt the quality gate requires.
2. Run quality-gate before you call it final.

Do not present the artifact as finished until both checks have passed.
