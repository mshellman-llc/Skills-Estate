# Hypercare triage and closeout report spec

Hypercare is the defined support window after go-live, typically two weeks, bounded by whatever the SOW says. Two disciplines carry it: every issue gets a stable identity and an honest disposition, and the line between hypercare-covered work and new scope is drawn early and out loud, because that line is where budget disputes are born.

## Triage log

One log for the whole window. Columns:

| ID | Severity | Reported | Reporter | Issue | Owner | Status | Resolution | Disposition |

- **ID**: `HC-001` upward, assigned at intake, never reused or renumbered. A defect carried in from UAT keeps its upstream ID in the Issue text (for example "carried from DEF-042") and still gets an HC-ID so the hypercare record is complete on its own.
- **Severity**: Sev 1 (production down or data corrupting, all hands), Sev 2 (core process blocked, no workaround), Sev 3 (impaired with workaround), Sev 4 (cosmetic or convenience). Severity is impact, not who reported it or how loudly.
- **Status**: open, in progress, fix deployed, verified, closed.
- **Resolution**: what was actually done, with the deploy or config reference.
- **Disposition**: one of the closed states below.

## No close without verified resolution

An issue closes only when the fix is verified working in production, by a named person, on a named date, recorded in the Resolution cell. "Redeployed" is not verified; "client AP lead ran a live quote through on 2026-08-19, terms block present" is. The closeout gate fails any row dispositioned Closed whose text does not state verification. Developer assertion is how regressions get discovered by the client.

## Dispositions

Every issue ends the window in exactly one of:

- `Closed: <fix> verified <by whom, when>`
- `Open, transferred: <to whom, with reference>` for issues that legitimately outlive the window and move to the ongoing support arrangement.
- `Change-order candidate: routed <date>` (see boundary below).
- `Withdrawn: <by whom, why>` for reports that turned out not to be issues. Withdrawn is the reporter's call or an agreed finding, never a way to make the log look clean.

## The hypercare boundary

Hypercare covers defects: the system not behaving as the co-signed design and the accepted scope say it should. It does not cover new requirements, scope that was descoped with sign-off, training beyond what the SOW includes, or "while you're in there" requests. The test is the scope baseline and the Solution Design Document, not how small the ask sounds; small asks compound.

When a request fails that test, say so in the log the day it arrives (disposition `Change-order candidate`), tell the client contact it is being routed rather than quietly absorbing it, and route it to delivery-status, where the Basis of Estimate framework and the change-order machinery live. This skill never prices the candidate, never estimates it, and never promises it. Absorbing change-order work inside hypercare is the failure mode: it burns the margin, trains the client that scope is free, and hides the demand signal the account team needs.

Ambiguous cases (the design is silent, or the requirement was arguably implied) go to the Program Lead with both readings stated. Do not resolve contract ambiguity by triage.

## Hypercare Closeout Report

A record document, not a signed one. It states what happened; nobody countersigns it. Drafted at the end of the window from the triage log and the acceptance tracker. Template: `assets/hypercare-closeout-template.md`. Sections, all always present (an empty section states why it is empty; never drop one):

1. **Header**: client, engagement, SOW ID, hypercare window (dates, and the SOW clause defining it), Go-Live Acceptance status carried from the tracker with its dates.
2. **Window summary**: issue counts by severity and disposition, computed from the log, not estimated. Print the counts.
3. **Hypercare issue log**: the full triage table, final state. This is the table the gate checks.
4. **Open transfers**: anything leaving the window still open, who now owns it, and the reference the client was given.
5. **Change-order candidates**: what was routed, when, and to whom. No pricing, no sizing.
6. **Actuals vs estimate**: see harvest-spec.md; the table lives here and feeds the harvest.
7. **What broke and why**: the honest paragraph per Sev 1 and Sev 2, cause not blame.
8. **Transition**: pointer to the transition documentation and the support arrangement that takes over.

## Transition documentation

Drafted for the client and whoever supports the system next: what was built (pointer to the Solution Design Document as-built version, not a restatement), environment and access inventory, integration and job schedule inventory with failure symptoms and first-response steps, known issues and accepted limitations (from the log, by HC-ID), the support contact model after the window, and where every engagement artifact lives. It transfers operation, it does not perform it: managed-services operation after transition is out of this skill's scope.
