# House format spec

This file is the **normative** definition of the entry structure and the field list. `play-entry-template.md` and the summary in SKILL.md restate it for convenience. If they ever disagree, this file wins and the other two get corrected in the same pass.

Every catalog entry has the same shape. This lets a reader scan any entry and know where to look, lets sales lift the one-pagers directly, and lets delivery read the scope block. Reproduce it exactly. If an existing catalog uses a different style, match that instead.

## Entry skeleton

```
## NN · [Offering name] ([free] / [paid] / [tier label])

**In scope**
- ...

**Out of scope**
- ...

**Deliverables promised**
- ...

**Business value**
- ...

**Target buyer**
- ...

### Tldr
[One or two sentences. What it is and what it leads to.]

### Eli5
[Plain language. A concrete metaphor is welcome. No jargon, no acronyms.]

### Internal one-pager
**What is it**
...
**Who is it for**
...
**Why should they care**
...
**Why should we care**
...
**What's included**
- ...
**What's not included**
- ...
Each boundary is the on-ramp to a paid next step.
**How do we deliver it**
...

### External one-pager
**What is it**
...
**Who is it for**
...
**Why should you care**
...
**What's included**
- ...
**What's not included**
- ...
**How we deliver it**
...
```

## The five fact blocks

`In scope`, `Out of scope`, `Deliverables promised`, `Business value`, `Target buyer` are the source of truth. Everything below them restates these facts; it must not introduce a new one. Keep them bulleted and concrete.

- `In scope` / `Out of scope`: activities and boundaries. Each out-of-scope line should route somewhere (a paid next step, an adjacent play, a change order). If a boundary was implied but never stated, you may add it and mark it `(inferred)`.
- `Deliverables promised`: the artifacts the client receives. Name them.
- `Business value`: mix client value and commercial value here; the one-pagers will split them.
- `Target buyer`: posture and situation, plus segment where it changes what converts.

## Tldr and Eli5

- **Tldr**: one or two sentences, for a colleague skimming the catalog. What it is, and what it converts to.
- **Eli5**: plain language for a non-expert. A metaphor is encouraged. This is a comprehension test: if you cannot explain it simply, the definition is not sharp yet.

## Internal vs external one-pager

Both restate the same facts. The difference is audience.

- **Internal** keeps all seven questions, including **Why should we care** (our commercial intent, the conversion, the handoff, the "this is our training ground" logic). It can name internal guardrails (capacity caps, "two gears", bench notes) and route explicitly to other play numbers.
- **External** drops **Why should we care** entirely and reframes the rest in the client's second person ("Why should you care", "How we deliver it"). Soften internal guardrails into client language: an internal "time-capped to protect capacity" becomes an external "a single short session." Never expose internal-only intent (pipeline, IP harvesting, margin logic) in the external version.

Lead both one-pagers with **What is it** (presentation order), even though you reasoned Who-first.

## Numbering

- Use the catalog's existing scheme (`## 01`, `## 02`, ...). New entries take the next number unless the ladder position argues for insertion.
- If more than one numbering scheme touches the catalog (catalog numbers, internal/CRM IDs, worksheet numbers), do not silently reconcile them. Flag the collision as a decision and note which scheme is canonical.
