# Section ownership and cross-reference discipline

Every mechanic in a SOW has exactly one section that owns it. Owning means: the full statement of the mechanic lives there, and nowhere else. Every other section that needs to invoke the mechanic points to the owner in one sentence. This is the single rule that prevents repetition-as-thoroughness.

## The standard CPQ SOW ownership map

This map reflects the Tier 1 Lift & Shift structure and should hold for Tier 2 (Remediate & Migrate) and Tier 3 (Re-Arch & Migrate) with additions, not relocations.

| Mechanic | Owner | Allowed elsewhere |
|----------|-------|-------------------|
| Basis-of-estimate logic + T&M billing + soft trigger | Section 7.2 Key Assumptions | One-sentence preview in 1.1 and 2.1, pointing to 7.2 |
| Quantitative footprint figures | Exhibit A | Referenced (not restated) from 2.2, 7.2, 7.3 |
| Hard triggers (binary additions) | Exhibit A | Restated once in Section 8.1 trigger list |
| Phase gates / exit criteria | Section 3 Delivery Methodology | Named once in 1.1 as "Section 3 states the phase gates" |
| Change Order process | Section 8.2 | Referenced wherever a trigger is named |
| Defect severity + in-scope definition | Section 10.1 | Referenced from 7.2 UAT assumption |
| Integration scope (one re-point) | Section 2.2 in-scope bullet | Discovery exception in 7.3, trigger in 8.1 |
| Subscription flat-migration limit | Section 2.2 bullet + one callout | Exclusion cross-ref in 2.3 |
| Timeline-adjustment / late-access | Section 7.2 assumption | Referenced from 7.1 responsibilities |

## How to apply it during a de-slop pass

1. List every mechanic that appears more than once (the slop scan gives you candidates by counting distinctive phrases).
2. For each, pick the owner from the map above. If the mechanic is new to Tier 2/3, assign an owner using the same logic: assumptions logic goes to 7.2, figures go to Exhibit A, process goes to Section 8, protective gates go to 7.3.
3. State it fully in the owner. Reduce every other instance to a pointer or cut it.
4. A preview in an early section (1.1, 2.1) is allowed as exactly one sentence that points forward. It is not a second full statement.

## The preview-versus-repeat distinction

A preview orients the reader and points forward: "The estimate is built on the footprint documented in Exhibit A, confirmed during Analyze." One sentence, no mechanics explained.

A repeat re-explains the whole mechanic: "Because the engagement is Time and Materials, work below the footprint bills as lower actual effort; where the inventory shows the footprint materially exceeds it, Aleysian re-baselines through a Change Order before Build proceeds." That is the owner's job, and it should appear only in the owner.

If an early section contains the second kind, it is a repeat. Cut it to the first kind.

## Why this matters beyond style

Drift. When the same mechanic is written in full in five places, the five versions will not stay identical through edits. One says "before Build proceeds," another says "before downstream phases proceed." A client's counsel reads the difference as ambiguity and asks which controls. One authoritative home means one version means no drift.
