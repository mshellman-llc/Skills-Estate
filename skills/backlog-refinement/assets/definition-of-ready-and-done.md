# Definition of ready and definition of done

A starting point for the team's own lists. Mark the lists proposed until the team adopts them, then record the adopted version and its date in the engagement or team folder.

## Definition of ready

An item is ready when every line is true:

- [ ] The Name says what the item delivers, not "implement X".
- [ ] The So That statement names the outcome for the user or the business.
- [ ] The I Want To statement describes the need, not the build.
- [ ] Acceptance criteria are Gherkin scenarios describing outcomes a user or tester can observe, including the main failure path.
- [ ] `readiness_check.py` grades it READY.
- [ ] Every dependency is a D-### entry in the RAID log, or the item has none.
- [ ] Design material is linked, or the gap has an owner and a date.
- [ ] The people who will build it have estimated it.
- [ ] No open question blocks estimation or the build.
- [ ] Stakeholders have reviewed it (Status is Reviewed or Approved).

If a line fails, the item is not ready. Fix it in this session or defer it.

## Definition of done

An item is done when every line is true:

- [ ] Every acceptance scenario passes in the deployed test environment.
- [ ] The change is merged to the release branch the project uses.
- [ ] Automated tests cover the changed paths.
- [ ] Another engineer reviewed and approved the change.
- [ ] QA passed, or the separate QA function signed off.
- [ ] Help, runbook and API documentation are updated where the change affects them.
- [ ] The feature flag is configured, or a release-notes entry is drafted.
- [ ] Telemetry needed to measure the outcome is firing.
- [ ] User-facing screens pass the project's accessibility check (WCAG 2.2 AA unless the project states otherwise).
- [ ] The Product Owner accepted the item.

Done is binary. An item missing a line moves to the next sprint.

On a client engagement, done is not acceptance. Client acceptance happens in `uat-validation` against the co-signed requirements.

## By item type

| Type | Ready | Done |
|---|---|---|
| Feature | The full list above | The full list above |
| Defect | Steps to reproduce, severity, a root-cause hypothesis or "to be investigated", and a scenario stating the defect no longer reproduces | The full list, with a regression test |
| Spike | One-sentence question, a timebox of one to three days, and the answer that ends the spike | A written finding and a recommended next step; no merge required |
| Technical debt | The user-facing measure that improves; work with none is tracked as engineering upkeep outside the requirements backlog | The full list |

## Sixty-minute refinement session

| Time | Activity | Lead | Result |
|---|---|---|---|
| 0:00 to 0:05 | Review last session's items | Product Owner | Rework caught |
| 0:05 to 0:10 | Pull the next 8 to 12 candidates in priority order | Product Owner | Candidate list |
| 0:10 to 0:20 | Run the check and triage at about a minute each | Team | READY, REFINE and DISCOVERY groups |
| 0:20 to 0:50 | Fix two to four REFINE items | Team | Splits, rewritten scenarios, RAID entries |
| 0:50 to 0:57 | Estimate the fixed items | Engineers | Estimates recorded |
| 0:57 to 1:00 | Re-run the check and save the report | Product Owner | Readiness report for sprint planning |

Use a visible timer. Pre-split the largest items before the session rather than during it.

## Grading card

```
Independent  Can it ship without waiting on another item?
Negotiable   Does it state the need and leave the build open?
Valuable     Who benefits if this is the only item that ships?
Estimable    Would two engineers estimate it within a factor of two?
Small        Can a pair finish it within the team's limit (default 5 days)?
Testable     How would a tester show it is done?

6 or 5 with an estimate and a complete scenario: READY
3 or 4: REFINE
0 to 2, or three sessions without becoming ready: DISCOVERY
```
