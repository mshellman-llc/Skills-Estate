# Sprint plan format

`sprint_check.py` reads one JSON file per sprint. Item IDs are the Requirement Numbers from capture-requirements, so the gate can match them to the readiness report.

```json
{
  "sprint_name": "Sprint 14",
  "dates": "2026-11-09 to 2026-11-20",
  "goal": "A new admin can finish guided setup without a support ticket",
  "definition_of_done": ["code reviewed", "tests added", "telemetry in staging", "docs updated"],
  "capacity": {
    "sprint_days": 10,
    "hours_per_day": 8,
    "focus_factor": 0.7,
    "commit_target_pct": 80,
    "stretch_pct": 15,
    "team_members": [
      {"name": "Ana", "pto_days": 0, "meeting_hours": 10, "on_call_hours": 0, "interrupt_hours": 6},
      {"name": "Raj", "pto_days": 1, "meeting_hours": 10, "on_call_hours": 12, "interrupt_hours": 6},
      {"name": "Kim", "available_hours": 20, "notes": "half allocated to support"}
    ]
  },
  "velocity_history_points": [28, 34, 31],
  "items": [
    {
      "id": "ONB-001",
      "title": "Setup checklist",
      "type": "commit",
      "estimated_hours": 30,
      "estimated_points": 5,
      "assignee": "Ana",
      "dependencies": [
        {"raid_id": "D-004", "description": "Auth scope from Platform", "owner": "Platform lead", "needed_by": "2026-11-11", "confirmed": true}
      ],
      "risks": [{"description": "Design not final", "mitigation": "Review on day 2", "owner": "Ana"}],
      "dod_items": ["code reviewed", "tests added", "telemetry in staging", "docs updated"]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `capacity.team_members[]` | One row per person. `available_hours` overrides the calculation when the person's hours are known directly. Otherwise the gate computes `(working_days - pto_days) x hours_per_day`, subtracts `meeting_hours`, `on_call_hours` and `interrupt_hours`, and multiplies by `focus_factor`. A person-level value overrides the team default. |
| `capacity.total_available_hours` | Used only when there are no per-person rows, with a warning. |
| `items[].type` | `commit` or `stretch`. |
| `items[].dependencies[].raid_id` | The D-### entry in the RAID log. With `--raid-log`, an ID missing from the log fails the gate. |
| `items[].refined` | Read only when no readiness report is supplied. |
| `definition_of_done` | The team's list. Each item's `dod_items` is compared with it. |
