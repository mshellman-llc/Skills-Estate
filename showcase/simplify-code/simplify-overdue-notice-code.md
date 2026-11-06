---
skill: simplify-code
title: Simplify a new overdue-notice module before commit
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: d43d7322867e6d4267530420631be0734b629ddcbf6d0037685ec09c3cea5ac4
---

## Request

I'm about to commit the new overdue-notice code in inputs/overdue.py. Can you run a simplify pass on it, apply the safe edits, and tell me what you left alone? The project rules are in inputs/AGENTS.md and the tests are in inputs/test_overdue.py.

## Inputs

Run of the built `simplify-code` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `overdue.py`.

#### AGENTS.md

#### Project rules

- Python 3.11, standard library only.
- Money is always integer cents. Display text comes from `lib/money.py`:
  `format_cents(cents: int) -> str` returns `"$12.05"` for 1205 and `"$0.00"` for 0.
  Do not format money by hand.
- Notice dicts are consumed by the mailer service. Keys and value types are a contract:
  `member_id` (str), `title` (str), `days_overdue` (int), `fine_cents` (int), `fine_text` (str).
- Notices are sorted by fine, highest first, then by `member_id`.
- Run tests with `python -m pytest tests/test_overdue.py`.
- Code comments only for non-obvious reasons.

#### overdue.py

from datetime import date

from lib.money import format_cents

GRACE_DAYS = 3
FINE_PER_DAY_CENTS = 25
MAX_FINE_CENTS = 1000


def days_overdue(due, today):
    if today > due:
        return (today - due).days
    else:
        return 0


def calc_fine(loan, today):
    d = days_overdue(loan["due"], today)
    if d <= GRACE_DAYS:
        return 0
    else:
        fine = (d - GRACE_DAYS) * FINE_PER_DAY_CENTS
        if fine > MAX_FINE_CENTS:
            fine = MAX_FINE_CENTS
        return fine


def build_notices(loans, today):
    notices = []
    total = 0
    for loan in loans:
        if loan["returned"] is None:
            fine = calc_fine(loan, today)
            if fine > 0:
                days = days_overdue(loan["due"], today)
                text = "$" + str(fine // 100) + "." + str(fine % 100).zfill(2)
                notices.append({
                    "member_id": loan["member_id"],
                    "title": loan["title"],
                    "days_overdue": days,
                    "fine_cents": fine,
                    "fine_text": text,
                })
                total += fine
    notices.sort(key=lambda n: (-n["fine_cents"], n["member_id"]))
    return notices

#### test_overdue.py

from datetime import date

from overdue import build_notices, calc_fine

TODAY = date(2026, 11, 4)


def loan(member, due, returned=None):
    return {"member_id": member, "title": "T-" + member, "due": due, "returned": returned}


def test_grace_period_has_no_fine():
    assert calc_fine(loan("a", date(2026, 11, 1)), TODAY) == 0


def test_fine_after_grace():
    assert calc_fine(loan("a", date(2026, 10, 28)), TODAY) == 4 * 25


def test_fine_is_capped():
    assert calc_fine(loan("a", date(2026, 1, 1)), TODAY) == 1000


def test_returned_loans_skipped():
    assert build_notices([loan("a", date(2026, 1, 1), returned=date(2026, 2, 1))], TODAY) == []


def test_sorted_by_fine_then_member():
    loans = [loan("b", date(2026, 10, 20)), loan("a", date(2026, 10, 20)), loan("c", date(2026, 1, 1))]
    assert [n["member_id"] for n in build_notices(loans, TODAY)] == ["c", "a", "b"]

## Output

I simplified `overdue.py` and saved the result to `out/overdue.py`. I did not run the tests: nothing could be executed here, and `lib/money.py` was not supplied. I traced each of the five tests in `test_overdue.py` by hand against the new code and all five still hold. Please run `python -m pytest tests/test_overdue.py` before you commit.

#### Scope

The target was the one file you named, `overdue.py`. I read `AGENTS.md` and `test_overdue.py` first. There was no git history to diff, so the whole file counts as the change. `test_overdue.py` is unchanged.

#### Edits applied

1. **Hand-built money text replaced with `format_cents`.** `AGENTS.md` says money text must come from `lib/money.py`. The old line `"$" + str(fine // 100) + "." + str(fine % 100).zfill(2)` is what that rule rules out. For positive integer cents, `format_cents` returns the same string, for example `$10.00` for the 1000-cent cap and `$1.00` for 100. This rests on the `format_cents` contract in `AGENTS.md`, not on a run.
2. **Unused `total` removed.** It was summed inside the loop and never read or returned.
3. **Unused `from datetime import date` removed.** Nothing in the module referenced it.
4. **`days_overdue` reduced to `max((today - due).days, 0)`.** The old branch returned 0 whenever `today <= due`. In that case the day count is zero or negative, so `max` gives the same answer.
5. **`calc_fine` flattened.** It now computes billable days after the grace period, returns 0 if there are none, and otherwise returns `min(billable_days * FINE_PER_DAY_CENTS, MAX_FINE_CENTS)`. A loan 3 days overdue gives 0, 4 days gives 25, and 44 days or more gives the 1000 cap, as before. The vague name `d` is gone.
6. **Nesting in `build_notices` reduced.** Two nested `if` blocks became two `continue` guards. A returned loan and a zero fine are still skipped, and the order the notices are built in is unchanged.
7. **Single-use local variables inlined.** `days` and `text` were each used once, so they now sit in the dict.

#### Behavior check

- The notice keys (`member_id`, `title`, `days_overdue`, `fine_cents`, `fine_text`) and their types are the same, which matters because the mailer service consumes them.
- The sort is still highest fine first, then `member_id`.
- The function names, signatures and the three constants are unchanged.

#### Left alone

- **`days_overdue` is computed twice per overdue loan** (once inside `calc_fine`, once for the notice). Removing that means changing `calc_fine`'s signature, which the tests call directly. The cost is one date subtraction, so I kept the tested interface.
- **Renaming `calc_fine` or the `fine_cents` key** would read slightly better but changes either the public name or the mailer contract. Not applied.
- **No test asserts `fine_text`.** A case such as `build_notices([loan("c", date(2026, 1, 1))], TODAY)[0]["fine_text"] == "$10.00"` would pin edit 1. I left the test file alone because you asked for a pass on the module.

#### File

- `out/overdue.py`, the simplified module, 34 lines against 47 before.

```python
from lib.money import format_cents

GRACE_DAYS = 3
FINE_PER_DAY_CENTS = 25
MAX_FINE_CENTS = 1000


def days_overdue(due, today):
    return max((today - due).days, 0)


def calc_fine(loan, today):
    billable_days = days_overdue(loan["due"], today) - GRACE_DAYS
    if billable_days <= 0:
        return 0
    return min(billable_days * FINE_PER_DAY_CENTS, MAX_FINE_CENTS)


def build_notices(loans, today):
    notices = []
    for loan in loans:
        if loan["returned"] is not None:
            continue
        fine = calc_fine(loan, today)
        if fine == 0:
            continue
        notices.append({
            "member_id": loan["member_id"],
            "title": loan["title"],
            "days_overdue": days_overdue(loan["due"], today),
            "fine_cents": fine,
            "fine_text": format_cents(fine),
        })
    notices.sort(key=lambda n: (-n["fine_cents"], n["member_id"]))
    return notices
```
