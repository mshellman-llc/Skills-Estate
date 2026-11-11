# Adapting this to a house style

The construction rules in `construction-rules.md` are general. They describe how generated prose is shaped, which does not vary much by organization.

Token-level rules do vary. Banned vocabulary, em dash policy, capitalization, and terminology are house decisions. This skill deliberately bakes in none of them. This file covers wiring yours on top.

## The two-layer split

Keep them separate. A house style that mixes `never use the word leverage` with "avoid balanced two-clause sentences" gets maintained as one undifferentiated list. The structural rules then drown in the vocabulary ones. They also fail differently. Token rules are exact-match and cheap; the other two need judgment and counting respectively.

A workable arrangement:

```
your-style-guide.md          <- house tokens, terminology, capitalization
prose-construction/          <- this skill, unchanged, updated from upstream
prose-house.json             <- budgets and house terms for the checker
```

Keeping this skill unmodified means you can pull improvements without re-merging your house rules every time.

## Configuring the checker

Budgets and extra banned terms come from a JSON file:

```json
{
  "em_dash_budget": 1,
  "balanced_clause_per_words": 200,
  "triad_per_words": 500,
  "banned_terms": ["delve", "tapestry", "leverage", "utilize", "seamless"],
  "allowed_repeated_phrases": [
    "statement of work",
    "return on investment"
  ]
}
```

```bash
python3 scripts/prose_structure_check.py --config prose-house.json DRAFT.md
```

Every field is optional; omitted fields keep the defaults.

`allowed_repeated_phrases` exempts strings that must match across documents by contract. C12 then leaves defined terms and legal language alone.

`em_dash_budget` accommodates houses that allow a small number. Set it to the count you actually permit rather than disabling the check.

## Wiring it into generation

The highest-value placement is wherever your prose gets produced, not wherever it gets reviewed.

**Human-facing generation.** Have producing instructions point at `SKILL.md` and
require the checker before returning a human-facing narrative. Do not apply the
checker to AI instructions, indexes, ledgers, schemas, or generated audit files.

**Repository conventions file.** If your team uses `CLAUDE.md`, `AGENTS.md`, or similar, reference this skill there so every session inherits it without being asked.

**CI.** The checker exits 1 on any finding, including WARN. Target an explicit
human-facing output directory or manifest selection, never every Markdown file:

```yaml
- name: Prose check
  run: python3 prose-construction/scripts/prose_structure_check.py --config prose-house.json deliverables/human-facing/*.md
```

Clean the existing corpus before enabling CI. A noisy gate teaches people to ignore the check.

## Tuning severity

The checker keeps FAIL and WARN labels as confidence metadata. Both labels block completion.

The label reflects confidence rather than importance. FAIL patterns have few legitimate uses. WARN patterns need more context, but the authored sentence still needs revision or a protected boundary.

Change rule severity one rule at a time. Repair matching files before changing its label.

## What not to adapt

Two things are worth keeping as-is.

**The replacement clauses.** Every rule specifies what goes in place of the banned construction. Dropping those turns the ruleset into a blocklist. A blocklist relocates constructions rather than removing them. That failure mode is the reason this skill exists.

**The density layer.** It is tempting to cut, since it needs tooling while the rest is prose you can read. It is also the layer that cannot be replaced by instructions, because a model drafting section seven has no view of sections one through six. Counting is the only way to see recurrence.
