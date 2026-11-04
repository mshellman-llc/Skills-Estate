# Capture structures

Use stable records in the product's current format. [The template bank](../assets/record-templates.json) supplies field shapes for a product without them. It is a capture aid, not a schema validator or a populated product baseline. Merge the common envelope with the selected record body. Keep the envelope fields when adapting it to Markdown, a workbook, an issue tracker, or another store.

## Shared fields and links

Every record needs a unique ID within its product and a record type. Bind it to the product ID; give it a title and revision. Capture an owner or decider only when known. Record time when the event occurs; do not estimate decision dates from file modification time. `null` means unknown; an empty array means no entries have been captured. Neither proves that the real product has none.

Evidence entries contain a claim, its basis, source/decision/verification IDs, and an exact locator. A locator can be a physical path, archive member chain, page, slide, cell range, code symbol/lines, or rendered interaction state. Bind it to a hash or exact revision. A decision entry cites the accepted direction and its scope; it does not need a fictional source file.

Use these evidence bases: `user_direction`, `source_reported`, `code_observation`, `test_observation`, `rendered_observation`, `live_observation`, `inference`, or `proposal`. State confidence with its reason and validation gap. Do not turn a numeric confidence score into evidence.

Links identify their target ID and relationship, such as supports, depends on, supersedes, implements, or verifies. Preserve external project IDs in crosswalk entries with the scheme and authoritative location. Verify links resolve within the home or an explicitly linked authority. Record the dependency versions needed for readiness.

Use currentness states `not_assessed`, `current`, or `stale`. They describe whether a record's evidence still applies. Source-review completion has its own state. Product acceptance and implementation evidence also remain independent. Each applicable gate needs an ID and scope. Record its assessment with evidence bindings; link blockers and the action that can satisfy the gate.

## Record catalogue

Read the rows needed for the current stage. The fields are required when that dimension applies; an inapplicable record/view needs a reason, not invented content.

| Record | Capture content |
| --- | --- |
| Source | Every retained location and archive chain; hash/revision; source family and supported date/version; authority role; content classification; review method/receipt; disposition; duplicate link; access/extraction exceptions. |
| Coverage checkpoint | Exact logical/directory/archive/build boundary; parent and child IDs; snapshot bindings; item-ledger links and denominators; findings/capability links; exclusions; unresolved items; review receipts; closure evidence. |
| Capability | Outcome and behavior; inputs/outputs; entities and transitions; failure/recovery paths; feature relationships; evidence; should-do decisions; can-do behavior observations; release-item links for will-do; persona/job/journey/value links; architecture/agent/dependency/risk/acceptance links; ID crosswalk. |
| Business value | Audience; problem and workaround; frequency/severity basis; mechanism; expected outcome; time/revenue/risk impact when supported; adoption burden; delivery and maintenance cost; metric definition/population/window; baseline/target basis; measurement method; validation and counter-evidence. |
| Persona | Role and customer segment; buyer/user/operator relationship when relevant; goals; permission needs; constraints; workaround; evidence basis; supported observations versus persona hypotheses. |
| Job | Actor; trigger and starting context; desired outcome; current workaround; constraints; completion measure; capability and journey links. |
| Journey | Actors; trigger and preconditions; ordered interactions/decisions; handoffs and records; state changes; permission rules; first value; exception/recovery paths; relevant maintenance and exit; outcome and acceptance links. |
| Architecture | Applicable view; responsibility and component; capability mapping; interfaces; state/data ownership; identities; deployment/recovery; dependencies; version; evidence and decision state. |
| Agent or pattern | Job/trigger; available context/memory; permitted tools/data; input/output contract; deterministic/model responsibilities; approval and override; evaluation cases; version and dependencies; retry/failure/recovery; cost controls; compatibility/rollback; change owner; evolution/retirement and sharing boundary where relevant. |
| Dependency | Dependent and prerequisite IDs; dependency type; required version/condition; evidence; readiness state; failure impact; workaround; known owner; action and receipt to satisfy it. |
| Risk, contradiction, or gap | Kind; competing claims or missing behavior; affected records; consequence and severity basis; treatment/options; known owner or decider; decision point; resolution evidence; retained alternatives. |
| Enhancement | Trigger and evidence; affected capability/journey; proposed outcome and behavior change; value hypothesis; dependencies/risks; effort uncertainty; candidate horizon; decision state; acceptance proposal. Keep it separate from a release commitment. |
| Differentiation hypothesis | Customer/outcome; proposed mechanism; comparison alternatives and dates; supporting evidence; counter-evidence; disconfirming test; research/customer-validation states; next experiment; hypothesis status. |
| Product decision | Exact choice/options; authority and scope; evidence; decision state; actual decider/date if accepted; rationale; consequences; supersession links; unresolved conditions. |
| Release | Named horizon and agreed outcome; authority; constraints/capacity/cost basis; release-item IDs; readiness gates; acceptance and rollout/recovery/support requirements when applicable. |
| Release item | Release and capability IDs; MoSCoW choice; rationale; decision/decider; dependencies; workaround or reconsideration trigger; owner/date if committed; acceptance IDs; effort/cost uncertainty. |
| Acceptance criterion | Requirement/release/capability/journey/design links; given state; action; observable expected result; permission and failure boundaries; required evidence layer/destination; fixtures/check method; decision state; verification IDs. |
| Verification | Exact checked behavior/criterion; source/build/configuration/model versions; environment and date; check type; fixture; expected/observed results; pass/fail/blocked status; receipt location/hash; limitations; assessor. |
| Artifact | Location; revision/hash; content boundary; source/decision bindings; saved/committed/installed/released/live state with destination receipt; completed work and remaining limitations. |
| Change impact | Input's old/new bindings; cause; direct and transitive dependents; invalidated claims/gates/receipts; re-review/retest work; resolution receipts. |
| Continuation checkpoint | Work boundary; instructions; bound inputs; stage/gates; completed artifacts; open work; findings/corrections; running state; exact next action and stop condition. |

## State rules

Source review uses `not_reviewed`, `reviewed`, `identical_to_reviewed`, `excluded_with_reason`, or `unresolved`. A duplicate disposition cites the reviewed hash and preserves its own locations. A checkpoint can close only with substantive item/child dispositions and resolved material blockers.

Product decisions use `unassigned`, `proposed`, `accepted`, `rejected`, or `superseded`. Accepted means an authorized decision exists for that scope. Keep distinct release-item records when one capability has different priorities in different horizons. `Won't this horizon` retains a reason and reconsideration trigger.

Each observed capability behavior uses `unknown`, `intended`, `static_demo`, `code_present`, `tested_locally`, `rendered_locally`, `deployed_unverified`, or `verified_live`. Attach verification IDs and limitations to the specific behavior. Several layers may coexist; rendering a screen does not erase the need to exercise its record writes or permission checks.

Verification checks can be `static`, `local_runtime`, `rendered_ui`, `agent_evaluation`, `deployment`, `live_behavior`, or `customer_observation`. Their result is `not_run`, `pass`, `fail`, or `blocked`. Customer observation identifies the supplied research and its boundary; an agent inspection is not a customer observation. Implementation verification cannot prove business value without outcome evidence.

Architecture views can cover product, technical, data, integration, security, design, or solution/operations. Use multiple records when responsibilities differ. Architecture choices and agent patterns carry their own product decision state and implementation evidence. A pattern version change can invalidate its evaluation evidence even when the surrounding capability is unchanged.

## Minimum trace for the next action

A proposed product brief can link a capability to a hypothesis and an experiment. A build-ready release item needs an accepted scope, a linked journey, applicable design/architecture, resolved critical dependencies, and observable criteria. A verified behavior additionally needs a passing receipt at the required layer and version. Preserve partial traces as open work rather than fabricating missing links.
