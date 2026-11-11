# Sales workspace current and proposed journeys

Journey records UJ01–UJ06, revision 1, product [PRODUCT-ID], proposed for review. The current-state column is a reconstruction from [planning workbook] planning statements, not observed user behavior. Proposed interactions are design hypotheses linked to requirements and tests. All permissions must be tested against the final [decision ref] matrix.

## UJ01 Assess and work a site opportunity

Actors P01/P03, jobs J01/J07. Trigger: a manual pursuit or a candidate from an approved rule. Preconditions: site and indication identified, permitted territory access; required parent relationship resolved.

| Step | Current evidence | Proposed interaction, state and handoff | Exception and recovery |
| --- | --- | --- | --- |
| Find next work | Separate legacy [legacy record types] opportunities and monthly fields are described in [story ref] | Site workspace lists existing pursuits and source of creation; rep inspects why a generated candidate exists | Missing/inaccessible site routes to data/access review; do not create a duplicate as a workaround |
| Assess potential | [question ref] assigns [operations team] maintenance and [potential-market fields] validation | Read [market data source] and provenance; validate permitted fields; stamp validator and time; Discovery remains until required facts exist | Missing metrics creates/reuses an exception record. Conflicting estimate sources remain explicit. Rep cannot bypass FLS |
| Classify pursuit | [question ref]/[answer ref]/[story ref] consolidate reason and types | Choose Category → Type → Reason, indication and allowed products. First value: one justified, valid pursuit | [decision ref] determines uniqueness. Competing pursuit is shown with link and permitted attach/skip path; simultaneous submissions yield one result |
| Plan work | [story ref] proposes Action Plans; templates deferred | Show next action, owner role and parent contract context; task routing follows approved template | Missing template is an actionable error, not an empty “successful” plan |
| Progress or postpone | [planning workbook] stage rows and [question ref] | Record stage evidence and Delay Reason when date moves later; surface missing fields near the action | Stage-specific validation explains unmet gate and preserves input |
| Close and learn | [question ref]/[story ref] and parking first-dose request | Capture win/loss reason and Other notes; invalid generated record closes Lost with special reason; pending revenue moves only under approved actual-dose matching | A late or unmatched dose is held for review; a closed record is not silently reopened. Reversal policy [decision ref] remains open |

Readiness: [requirement refs] are designed as scenarios, but [decision ref] prevent final acceptance. Tests: corresponding acceptance-criteria IDs, especially duplicate and unauthorized-edit cases.

## UJ02 Coordinate a contract and its sites

Actors P02/P07/P01/P06, jobs J02/J07. Trigger: new contract, amendment or Realignment (semantics [decision ref]), on a Contracting Entity. Preconditions: authorized contract territory/access, target products and eligible child-site facts.

| Step | Current evidence | Proposed interaction, state and handoff | Exception and recovery |
| --- | --- | --- | --- |
| Open contract pursuit | [question ref] replaces separate [strategic record type]-to-[legacy record type] creation with parent/child coordination | Create contract opportunity, select product scope, preview all child sites and existing pursuits | No children or ambiguous site parent produces a review list; no silent creation under another entity |
| Associate sites | [question ref] requires every child site; [question ref] supports two contracts if products differ | Preview create/attach/conflict counts. Select or confirm associations under [decision ref]; display exact product coverage | Existing opportunity with conflicting coverage stays unchanged; operations are idempotent and errors show which site failed |
| Develop terms | Contract Solution stage requires linked Schedule Terms | Create/link terms and show version; hand off pricing review in Negotiate | Missing Product Terms or mismatched variants blocks economic approval |
| Evaluate price | [question ref]/[story ref] bypass or pricing committee review | Show price class mix, gross/net revenue, margins and applicable rule version; record bypass or approval | Missing threshold cannot imply approval; revised pricing invalidates stale approval per proposed policy |
| Execute and synchronize | [question ref] | Only contract won + signed/executed terms (Active interpretation [decision ref]) + eligible site/product can move children to Pending Revenue | Lost parent leaves children open. Replayed/out-of-order events are safe; held events retry after facts resolve |
| Maintain economics | [question ref]/[story ref] | Reprice eligible Commercial lines; preserve VA/340B and previous values; roll up child figures for contract context | Missing price keeps prior/list price and exception; closed-child policy requires [decision ref] |

First value: a contract pursuit with an explainable site/product coverage map. Exit: lifecycle complete with linked terms and child outcome audit. Source-only contract roll-ups are contextual and excluded from site forecast totals.

## UJ03 Estimate product mix and review the forecast

Actors P01/P03/P05, jobs J03/J04. Trigger: initial annual brand estimate or a changed estimate/price. Preconditions: validated product mapping, business-day calendar, price-class mix and governed rates.

1. Rep enters an annual **brand-level** quantity while viewing site [market data source] ([question ref]). If no mix exists, prompt for estimated Commercial/340B/VA shares; record that basis.
2. Preview the 12-month allocation using approved business-day metadata and product mix. Show annual total, class totals and monthly subtotals before save. Missing or invalid mix/calendar blocks generation with specific correction.
3. Save monthly facts under the selected [decision ref] option. Rep edits permitted product-line values; show whether an edit pins the month or redistributes the remainder. Preserve a before/after summary. Do not overwrite edits on regeneration without an approved policy.
4. Calculate [question ref] gross/net revenue and gross/net margin; display missing fee/COGS inputs as incomplete rather than zero. Show formula inputs and effective dates to permitted reviewers.
5. Finance selects period, brand/product, territory and net measure. Site facts roll up once to region/US; contract value is a separate contextual view. Gross view is a desired optional alternative, not an accepted toggle implementation.
6. Drill into differences. Correct mapping or source values through their steward, regenerate only impacted facts and preserve audit. No quota means no attainment percentage; target period/basis requires [decision ref].

Current evidence: legacy monthly fields cannot support the multi-product cycle ([story ref]); the source does not establish a currently functioning net forecast. First value: one complete reconciled estimate. Acceptance: [requirement refs] plus [requirement ref], with [decision ref] gating build.

## UJ04 Review and activate opportunity generation

Actors P04/P03, job J05. Current evidence: [data gate] gates remain unstarted; [question ref] values are placeholders; [question ref] replaces the fallback with missing-metrics logs.

| State | Proposed work and output | Failure/recovery |
| --- | --- | --- |
| Draft rule | Select immutable rule version, look-back, effective product mapping and threshold bands | Unknown thresholds remain draft; do not interpret dry-run acceptance as production approval |
| Dry run | Produce candidate ledger with reason, metrics, proposed action and duplicate disposition; no opportunity inserts | Missing metrics log tied to site/run; missing actuals distinguished from confirmed zero |
| Reconciled | Compare validated seed and candidate set by inclusion/exclusion, changed population and source freshness | Count equality alone insufficient; explain every discrepancy and get disposition |
| Approved | [data gate] evidence, owner/date completion and Sales Ops sign-off bind to exact rule/configuration version | Any material rule/source change returns to review; no approval copied to a new version |
| Active | Authorized activation enables insert/attach/skip and Action Plans in bounded batches | Error isolation, retry keys and kill switch prevent repeats; monitoring receipt records outcomes |
| Suspended | Disable further creation while investigating affected run and record lineage | Correct source/config, rehearse replay, obtain required renewed approval and resume |

First value: an explainable candidate list is useful before production activation. [story ref] launch generation and [story ref] gap/capacity rules share duplicate/idempotency controls; launch does not bypass [data gate]. [requirement refs] discovery remains outside active rules.

## UJ05 Renew or record product loss

Actors P02/P07/P01, job J06. Trigger: Active non-base terms approach 120-day renewal point ([question ref]/[story ref]), expire without equivalent coverage, or have an earlier end date ([question ref]/[story ref]).

1. Preview/source job identifies the terms and exact product coverage. Create/reuse one renewal; record terms identity and source event.
2. Link appropriate site opportunities under [decision ref] and show expiration, terms scope and Action Plan.
3. If a successor activates, compare covered products, not merely presence of a successor. A complete renewal can win; partial renewal separates covered and uncovered products without double counting.
4. Non-renewal/early termination records loss and assigns reason follow-up. Existing child selling opportunities remain open.
5. If dates or coverage are corrected, route to the authorized reviewer using original event lineage. Do not manufacture an additional lost opportunity each daily run.

First value: a timely renewal with product-specific exposure. Current job implementation and backlog run semantics are unverified. [requirement refs] acceptance needs boundary-day, missed-run, repeated-event and partial-product fixtures.

## UJ06 Align territories and cut over

Actors P04/P03/P05, job J08. Current evidence: [question ref] describes monthly minor changes and ad hoc model replacement; [story ref] identifies legacy flows and fields.

1. Preview changed account territories, access memberships and primary forecast assignments separately. Unresolved [strategic record type] mapping blocks that cohort.
2. Compare old/new visibility and totals. Authorized users retain intended edit rights; unrelated users do not gain access. Open opportunities move; closed-history handling follows approved reporting policy.
3. Rehearse migration and cutover using immutable extracts, field/value crosswalks and dependencies. Validate EMEA/APAC and CLM as distinct regression populations.
4. At approved cutover, close [legacy record type] records per source decision; handle [strategic record type] with a separately approved disposition. Change shared probabilities only at the accepted time.
5. Freeze/deactivate legacy writers only after parity and downstream sign-off. Retain old fields read-only until consumers and retention allow removal.
6. If reconciliation or access fails, stop generation, restore the approved prior configuration and replay/compensate data through the migration ledger; recheck forecast and permissions before reopening.

First value: a tested transition plan with visible affected records. This package executes none of these steps. Test destinations and required receipts are in the delivery plan.
