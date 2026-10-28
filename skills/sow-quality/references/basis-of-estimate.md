# Basis of Estimate framework

The standard for handling volumetric assumptions in any Estate playbook SOW. It plugs into the SOW Assumptions sub-component and the DDOC Assumptions slide defined in the Playbook Process Guidelines. A SOW that states counts inline ("up to 1,000 product records") in the scope body reads as a commitment to that exact number, which is wrong for a Time-and-Materials engagement and dangerous if the real count differs.

## The core move

Move every volumetric number out of the scope body and into **Exhibit A: Basis of Estimate**, appended after the signature block and incorporated by reference. The scope body says what is in scope qualitatively ("product and pricing records are migrated and validated against source"); Exhibit A holds the quantitative footprint the estimate was built on.

Exhibit A is framed as the basis of the estimate, not a fixed quantity of work and not a guarantee of the client's current state. Because the engagement is T&M, effort below the assumed footprint bills as the lower actual effort. This framing protects both sides: the client is not overbilled for work that comes in light, and Estate is not locked to a count that discovery may contradict.

## The two-trigger taxonomy

Change Order triggers split into two kinds, and the SOW must treat them differently:

**Soft triggers (volumetric).** The footprint materially exceeds the Basis of Estimate, for example custom-automation volume or record counts well past those assumed. The word that does the work is "materially": small overages absorb into T&M, only material excess re-baselines. These are matters of degree.

**Hard triggers (binary workstream additions).** A second integration, a second org or an org split or merge, an additional platform migration. These are not matters of degree; any amount is a Change Order. They are listed in Exhibit A as "Change Orders regardless of size, independent of the footprint figures above." The "regardless of size" is a defended stricter term (see structural-deslop.md, Tell 2 exception), not slop.

Keeping these separate stops the SOW from treating "one extra integration" as if it were a volumetric overage to be negotiated by degree. It is binary; it triggers regardless.

## The inventory gate

The footprint is confirmed during the Analyze-phase inventory, and that confirmation is itself a gate: where the inventory shows the footprint materially exceeds the basis, Estate re-baselines through a Change Order before Build proceeds. Exhibit A can carry a "Confirmed in Analyze" checkbox column that doubles as the analysis sign-off log.

## Lines-of-code framing

Apex and line-of-code figures are Estate's estimation assumptions, confirmed during Analyze. They are explicitly NOT a quantity the client attests to before signing. State this in Exhibit A. Without it, the LOC figure reads as a client representation, which it is not and which the client cannot make accurately before discovery.

## Language that softens the contradiction

A 1:1 / like-for-like migration promise sits in tension with caps (for example a 10-class Apex cap). "Like-for-like" implies everything carries over; the cap says it does not. Resolve by softening "like-for-like" to "functional-parity migration for standard configurations." Parity of function, within the stated standard boundary, is honest; verbatim reproduction of everything is not, and the caps make that explicit.

## Where each piece lives

| Piece | Home |
|-------|------|
| Qualitative scope ("records migrated and validated") | Scope body (Section 2) |
| Quantitative footprint (counts, scale, LOC) | Exhibit A |
| Full basis-of-estimate + soft-trigger mechanic | Section 7.2 Key Assumptions |
| Hard triggers (binary additions) | Exhibit A, restated in Section 8.1 triggers |
| Inventory gate | Section 7.3 Protective Clauses, referenced from Exhibit A |

Section 1 and 2 may preview the basis-of-estimate idea in one sentence each, pointing to Section 7.2 and Exhibit A. They do not re-explain it. That preview-not-repeat rule is the cross-reference discipline; see section-ownership.md.
