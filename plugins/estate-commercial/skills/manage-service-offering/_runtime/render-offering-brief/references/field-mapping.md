# Field mapping and JSON schema

## House format to template slots

When you render with `--md`, each entry's `### Internal one-pager` and `### External one-pager` sections map straight to the templates. Required slots are marked; everything else is optional and simply omitted when absent.

### Internal brief

| Template slot | House-format source |
|---|---|
| title (required) | the play name (heading, minus number and tier) |
| descriptor | the play's `### Tldr` |
| 01 What is it (required) | internal **What is it** |
| 02 Who is it for (required) | internal **Who is it for** |
| qualifiers / disqualifiers boxes | JSON only (not parsed from prose) |
| 03 Why should they care (required) | internal **Why should they care** |
| talking-tracks table | JSON only |
| 04 Why should we care (required) | internal **Why should we care** |
| 05 What's included | internal **What's included** (bullets become chips) |
| 06 What's not included (required) | internal **What's not included** (bullets become chips) |
| boundary line | trailing non-bullet line in **What's not included**, else omitted |
| 07 How do we deliver it (required) | internal **How do we deliver it** (prose) |
| delivery bar / numbered steps / callouts | JSON only |
| footer line | derived from tier (free vs paid) |

### External one-pager

| Template slot | House-format source |
|---|---|
| eyebrow | play name, uppercased |
| title (required) | play name (or JSON `title` for a real headline) |
| subtitle | first sentence of external **Why should you care** |
| intro | external **What is it** |
| What you get (required) | external **What's included** (bullets become cards) |
| two-column band | external **Who is it for** and **Why should you care** |
| How it works (required) | external **How we deliver it** |
| kicker (top-right) | JSON only |
| center note under columns | JSON only |
| footer line + note | derived from tier |

## JSON spec schema

Top level: `{ "internal": {...}, "external": {...} }`. Either may be omitted to render only one artifact. All fields optional unless the template marks them required above. Only inline `span`, `strong`, `b`, `em`, `i`, and `br` tags are accepted. Attributes are forbidden except `class="hl"` on a span. Wrap emphasis in `<span class="hl">...</span>` for the teal highlight.

```json
{
  "internal": {
    "eyebrow": "INTERNAL PLAYBOOK",
    "dept": "SALES ENABLEMENT",
    "title": "Offering name",
    "descriptor": "One-line Tldr under the title.",
    "s1": "What is it (prose).",
    "s2": "Who is it for (prose).",
    "qualifiers": ["...", "..."],
    "disqualifiers": ["...", "..."],
    "s3": "Why should they care (prose).",
    "tracks": [{"k": "Business leaders", "v": "..."}, {"k": "IT leaders", "v": "..."}],
    "s4": "Why should we care (prose).",
    "included_list": ["chip", "chip"],
    "s5": "used only if included_list is absent",
    "not_included": ["chip", "chip"],
    "boundary": "Each boundary is the on-ramp to a paid next step.",
    "deliver_bar": "About <span class=\"hl\">6 hours</span> of our time.",
    "steps": ["step one", "step two"],
    "callouts": [{"k": "Positioning", "v": "..."}, {"k": "Two gears", "v": "..."}],
    "s7": "used only if steps is absent",
    "footer_line": "The free front door to our <span class=\"hl\">practice</span>."
  },
  "external": {
    "kicker": "VENDOR-NEUTRAL · OUTCOME-FIRST",
    "eyebrow": "OFFERING NAME",
    "title": "A punchy client headline",
    "subtitle": "The value promise in one teal line.",
    "intro": "Framing paragraph.",
    "what_you_get": ["...", "...", "...", "..."],
    "columns_heading": "Built for both sides of the table",
    "columns": [{"k": "For business leaders", "v": "..."}, {"k": "For IT leaders", "v": "..."}],
    "center_note": "One shared picture line.",
    "how": "How it works paragraph, with <span class=\"hl\">the time commitment highlighted</span>.",
    "footer_line": "What it costs: nothing. <span class=\"hl\">It is how we start.</span>",
    "footer_note": "Contact the offering owner to begin."
  }
}
```

## Rules

- Text fields restate the playbook's facts. Do not add a claim, metric, price, or duration that the playbook does not contain.
- `steps` and `included_list` replace their prose counterparts (`s7`, `s5`) when present. Provide one or the other.
- Keep copy tight. If a section overflows the page, revise the wording without losing meaning, then render a new attempt.

## Label tolerance (--md mode)

The parser resolves these bold labels to the same slot, so ordinary source drift does not empty a panel:

| Slot | Accepted labels |
|---|---|
| what_is_it | What is it, What it is |
| who_for | Who is it for, Who it is for, Who it's for |
| they_care | Why should they care |
| you_care | Why should you care |
| we_care | Why should we care |
| included | What's included, Whats included, What is included |
| not_included | What's not included, Whats not included, What is not included |
| deliver | How do we deliver it, How we deliver it, How is it delivered |

A trailing `?` or `:` is stripped. Any bold label outside this table fails strict parsing. Diagnostic `--no-strict` mode warns and omits that field; its output needs repair before delivery. Required slots are `what_is_it, who_for, they_care, we_care, included, not_included, deliver` (internal) and `what_is_it, included, deliver` (external); an empty one stops the run.

The external subtitle takes the first sentence of **Why should you care** and the "Why it matters" column takes the remainder, so the same sentence does not print twice on one page. If the answer is a single sentence, the column repeats it rather than rendering empty.

Entry headings parse with any separator: `01 · Name`, `01 - Name`, `01 – Name`, `01: Name`, `01. Name`, `01 Name`. The number is stripped from the title, the eyebrow and the slug.
