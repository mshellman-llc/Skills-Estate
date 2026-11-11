# Before / after examples

All drawn from the Tier 1 CPQ Lift & Shift SOW de-slop pass. Each shows the tell, the cut, and why.

## Repetition-as-thoroughness

**Before (Section 2.1, repeating what Section 7.2 owns):**
> This is a functional-parity migration for standard configurations, with no remediation or re-architecture: a single-level product hierarchy, one transactional system integration re-pointed, standard RCA document rendering, and subscriptions migrated as flat assets. The quantitative footprint the estimate is built on (integration count, custom-automation volume, catalog and pricing scale, and record counts) is documented in the Basis of Estimate (Exhibit A), incorporated into this Statement of Work by reference, and confirmed during the Analyze-phase inventory. Because the engagement is Time and Materials, work that comes in below that footprint bills as the lower actual effort; where the inventory shows the footprint materially exceeds it, Aleysian re-baselines the estimate and timeline through a Change Order before Build proceeds.

**After:**
> This is a functional-parity migration with no remediation or re-architecture: a single-level product hierarchy, one transactional system integration re-pointed, standard RCA document rendering, and subscriptions migrated as flat assets. The footprint the estimate assumes is documented in Exhibit A and confirmed during Analyze; the basis-of-estimate and Change Order mechanics are stated in Section 7.2.

Why: the boundary list stays (2.1 is a fine home for it). The full T&M mechanic is cut to a pointer because Section 7.2 owns it. Across the document this took the full mechanic from three statements to one.

## Clause-justification, cut

**Before (Section 7.1):**
> Provide current product and pricing record counts via production query before SOW execution, so the basis of estimate can be confirmed.

**After:**
> Provide current product and pricing record counts via production query before SOW execution.

Why: the obligation stands alone. The why-tail explained a purpose the client did not need stated.

## Clause-justification, kept (the exception)

**Kept as written (Section 10.2):**
> One exception applies: the data-migration reconciliation report carries a 3-business-day validation window, because cutover sequencing depends on it.

Why: the justification defends an exception to the standard 10-day window. Cut "because cutover sequencing depends on it" and the shorter window reads as arbitrary, inviting pushback. The reason earns its place.

## Rule-of-three verb pile

**Before (Section 1.1):**
> This is a functional-parity migration for the Client's standard CPQ configuration: the Client transacts on RCA with the same core quote-to-order process it runs today, within the boundaries in Section 2. The engagement does not remediate, re-architect, or add capability the source CPQ does not already have. Current-state elements beyond the standard boundary (...) are not reproduced one-for-one and are addressed through a Change Order or a higher tier.

**After:**
> This is a functional-parity migration: the Client transacts on RCA with the same core quote-to-order process it runs today, within the boundaries in Section 2. Current-state elements beyond that boundary (...) are addressed through a Change Order, not reproduced under this SOW.

Why: the "does not remediate, re-architect, or add" verb pile and the following sentence both restated the same boundary that Section 2 owns. Collapsed to one clean statement.

## Meta-commentary, deleted

**Before (Section 6 team intro):**
> The staffing model reflects the delivery plan for this engagement. Junior resources are full-time when active; senior resources run part-time as oversight. The Solution Architect leads discovery solo in weeks 1 to 3 before the Business Analyst and Developer join at Design. Senior-architect oversight beyond the Solution Architect line is enabling and non-billable; there is no separate senior-architect line in the price.

**After:**
> The Solution Architect leads discovery in weeks 1 to 3; the Business Analyst and Developer join at Design. Roles and allocations are below.

Why: the client does not need to be told what is not in the price or how Aleysian thinks about billable versus enabling time. That is internal reasoning. The one fact worth keeping (SA leads discovery early) stayed.

## Phase-gate duplication

**Before:** Section 1.1 said "Each phase has named exit criteria that gate progression to the next." Section 3 said "Each phase has named activities and exit criteria that gate progression."

**After:** Section 1.1 says "The engagement runs across seven phases (...). Section 3 states the phase gates." Section 3 keeps the full gate list.

Why: one owner (Section 3), one pointer (Section 1.1).
