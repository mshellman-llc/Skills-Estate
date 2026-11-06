# Candidate format

`priority_score.py` reads a JSON list of items, or an object with `items` and, for the weighted matrix, `criteria`. Use Requirement Numbers, epic prefixes, job IDs or roadmap card IDs as `id` so the ranking can be traced back.

```json
{
  "items": [
    {
      "id": "ONB",
      "title": "Guided setup",
      "problem": "New admins cannot tell which setup steps block their team",
      "job": "J1",
      "reach": 1200, "impact": 2, "confidence": 0.8, "effort": 3,
      "sources": {
        "confidence": "(synthetic example) Funnel: 41% of admins finish setup within 7 days (analytics export 2026-10-31)",
        "effort": "Sized by the platform lead in refinement on 2026-11-02"
      }
    }
  ]
}
```

| Framework | Required fields |
|---|---|
| `rice` | `reach`, `impact` (0.25, 0.5, 1, 2, 3), `confidence` (0 to 1 or a percentage), `effort` |
| `ice` | `impact`, `confidence`, `ease` |
| `opportunity` | `importance` (0 to 10), `satisfaction` (0 to 1; a 0 to 10 value is converted and flagged) |
| `odi` | `importance`, `satisfaction`, both 0 to 10 |
| `wsjf` | `business_value`, `time_criticality`, `risk_reduction`, `job_size` |
| `weighted` | `scores` with one value per criterion; top-level `criteria` as `[{"name": "...", "weight": 0.4}]` |

`sources` keys the tool reads: `confidence`, `effort` (also used for WSJF job size) and `importance`. Other keys are kept in the file for reviewers. `job` or `problem` links the item to the problem it addresses.
