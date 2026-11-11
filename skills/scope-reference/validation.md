# Validation: reconciling the artifact 1:1 against live quotes

The rule: nothing renders until every item name, hour value, and per-option state
in the assembled set reconciles exactly against the live scope-hierarchy pulls.
This file gives the method and a reusable checker.

## Why this exists

Scope items get renamed, re-houred, activated, and deactivated between sessions.
A doc that was correct last week is not assumed correct today. This step is the
difference between "read from Salesforce" and "looks like Salesforce."

## Method

1. Assemble your intended item set as structured data: for each item, its `name`,
   `hours`, and state per option (`in` / `available` / `optional` / `out`).
2. Build the "truth" set the same way, directly from the live pulls:
   - full pull (`activeOnly: false`) gives presence and hours,
   - active-only pull separates `available` (present, inactive) from `in`,
   - optional flags come from the phase/flag marking (e.g. `[Phase 1 - Optional]`).
3. Name-match with a normalizer that ignores punctuation and known prefix
   differences (e.g. the app may store `Salesforce Maps — X` while your table
   reads `Maps: X`). Do not let a cosmetic name difference read as a mismatch,
   and do not let it hide a real one — normalize, then compare the substantive
   fields.
4. Compare hours (exact) and each per-option state. Report every discrepancy.
5. Report item counts per option (present = in + available + optional) so the
   card labels tie out.

## Reusable checker

The check is bundled as `scripts/scope_reference_validate.py` (importable) with a
selftest beside it. Import `validate` and `present_counts` rather than
re-deriving the logic per build. Adapt `prefix_aliases` to the client's naming.
Feed it two dicts keyed by item name.

```python
import re

def normalize(name, prefix_aliases=None):
    n = name.lower()
    for a, b in (prefix_aliases or {}).items():
        n = n.replace(a, b)
    return re.sub(r'[^a-z0-9]', '', n)

def validate(file_items, sf_items, prefix_aliases=None):
    """
    file_items / sf_items: dict[name] -> {"hours": float,
                                          "states": {"OptA": state, ...}}
    Returns (ok: bool, issues: list[str]).
    """
    f = {normalize(k, prefix_aliases): (k, v) for k, v in file_items.items()}
    s = {normalize(k, prefix_aliases): (k, v) for k, v in sf_items.items()}
    issues = []

    for k, (name, _) in f.items():
        if k not in s:
            issues.append(f"[FILE ONLY] {name} — in file, not in any live quote")
    for k, (name, _) in s.items():
        if k not in f:
            issues.append(f"[SF ONLY]   {name} — in live quote, missing from file")

    for k in sorted(set(f) & set(s)):
        fname, fv = f[k]; _, sv = s[k]
        if float(fv["hours"]) != float(sv["hours"]):
            issues.append(f"[HOURS] {fname}: file={fv['hours']} sf={sv['hours']}")
        for opt in set(fv["states"]) | set(sv["states"]):
            a = fv["states"].get(opt); b = sv["states"].get(opt)
            if a != b:
                issues.append(f"[STATE] {fname} [{opt}]: file={a} sf={b}")

    return (len(issues) == 0, issues)

# Usage:
# ok, issues = validate(file_items, sf_items,
#                       prefix_aliases={"salesforce maps": "maps"})
# print("1:1 MATCH" if ok else "\n".join(issues))
```

## Reporting

Report exactly one of:

- **`1:1 match`** plus the per-option counts (e.g. `18 / 22 / 24`), or
- the specific discrepancies, each as one line, and **stop**. Do not render an
  unreconciled table. Fix the source of the discrepancy (usually a stale
  assumption in your set) and re-run.

A cosmetic false positive from the normalizer (a Maps name prefix, say) is not a
pass — fix the normalizer and re-run so the check is real.
