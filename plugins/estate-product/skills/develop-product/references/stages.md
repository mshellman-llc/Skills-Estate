# Stage execution and readiness

Use the section for the requested stage and any unmet prerequisite. Required outputs describe content, not mandatory filenames. Link existing documents, workbooks, issues, and code that already supply that content. Split or combine artifacts to match project conventions.

Each applicable stage needs a recorded boundary and output links in the product home. Record its gate evidence and unresolved work beside the next action. `Complete` means that stage's stated boundary passed; it does not mean the entire product is complete.

## 1. Establish the working boundary

**Sequence:** confirm the current instructions and product home → identify supplied sources and authorized destinations → record protected records and current revisions → choose the requested stage and prerequisites.

**Required outputs:** a bounded work brief; source/authority map; current artifact index; stage applicability and readiness assessment. For an existing estate, add a reproducible source manifest and path-disposition ledger at the requested depth. Reuse a valid inventory and refresh changed areas.

**Historical handling:** inventory in-scope hidden files and links. Include Git refs and archive members that may hold relevant evidence; inspect nested containers as part of the archive boundary. Preserve all original locations. Record access errors and broken links. Archive dispositions retain encrypted members and extraction limits; file dispositions identify unsupported formats and exclusions. Do not silently follow links outside scope. Apply extraction size/depth limits and isolate outputs; a limit leaves an unresolved item. Exclude credentials and recovery material from content review. Inspect custom source exceptions before excluding dependency trees.

Bind substantive reads to content hashes or immutable revisions. Preserve the first manifest when a tree is moving. Compare later scans and retain added or removed items alongside changed content. Establish a stable snapshot for a full coverage claim, using consistent scans and pinned content or an immutable source snapshot. Scoped work may proceed on pinned items with instability recorded; it cannot certify coverage of the changing estate.

**Readiness:** the source and action boundaries are explicit; current authorities and protected work are identified; every enumerated path has a classification and review state. Classification is inventory evidence, not completed content review.

**Next action:** review the next in-scope source area, or capture the new product's problem and desired outcome when no historical estate exists.

## 2. Review the evidence

**Sequence:** select an unreviewed source area → group byte-identical content → review each unique relevant item in a suitable format → capture findings and conflicts → update source dispositions and coverage checkpoints.

**Required outputs:** reviewed source records with exact locators; duplicate/provenance links; coverage checkpoints; findings and contradiction/gap records. For historical builds, add a version inventory and behavior comparison when relevant to the requested reconstruction.

Read text completely in bounded parts. Extract supported documents and inspect diagrams, images, slides, workbooks, and interfaces with suitable viewers or renderers. A failed extraction or clipped read remains unresolved or unread. A filename, metadata scan, screenshot contact sheet, or generated summary cannot establish substantive review of its underlying items.

Keep availability separate from review scope. A supplied archive can contain an earlier bound revision even when its members remain unread. Before calling evidence missing, check its in-scope locator and matching hash; otherwise record that it was not reviewed within this boundary. A scoped comparison can read the relevant member without closing the wider archive checkpoint.

Preserve every duplicate location; identical bytes can inherit one substantive review only with a matching hash and a link to the reviewed content. Different versions need their own dispositions. Distinguish authored or simulated behavior from executable behavior. Inspect historical commands before running them; use isolated environments and synthetic fixtures when runtime review is authorized. Do not run unknown build scripts merely to close a checkpoint.

Full historical reconstruction needs a checkpoint for every source area and nested directory. Add a checkpoint for each archive chain and identified build/variant. Account for empty directories and excluded content. Each item needs a disposition; each checkpoint needs findings or an evidence-backed determination that no product findings apply. Close parent checkpoints only after child coverage and unresolved material pass. For a bounded task, checkpoints can follow the relevant logical areas; unrelated source families remain outside that closure claim.

**Readiness:** each item in the claimed review boundary is reviewed, linked to reviewed identical content, or excluded with evidence. Material unread or inaccessible items block complete coverage. Count physical paths, archive members, unique content, relevant product sources, and reviewed product sources separately; state the denominator behind any percentage.

**Next action:** reconstruct the supported behavior or resolve a specific review exception. Product synthesis may accumulate during review with its coverage limit recorded.

## 3. Reconstruct an existing product

This stage applies when historical intent, variants, or implementation must be recovered. It is inapplicable to a product without history.

**Sequence:** compare dated intent and observed behavior → map capabilities and relationships → crosswalk existing IDs → record chronology and contradictions → separate historical alternatives from current product decisions.

**Required outputs:** an evidence-linked capability catalogue; relevant chronology and variant behavior matrix; agent contracts when agents exist; contradiction register. Crosswalk existing requirement and feature IDs to their acceptance IDs. Retain capabilities outside the selected release.

**Readiness:** each derived behavior has exact evidence or a current user decision; conflicting variants remain visible; implementation claims identify the exercised layer. Full reconstruction readiness also requires stages 1–2 to pass for the entire authorized historical boundary. A working demonstration cannot establish the complete intended product.

**Next action:** derive the current product definition from supported findings and accepted direction. If the task only concerns a current journey, use its reconstruction subset without claiming estate-wide fidelity.

## 4. Define the product and its value

**Sequence:** identify supported audiences and problems → connect personas to jobs and journeys → map capabilities to outcomes and value → frame differentiation hypotheses → expose choices for the authorized decider.

**Required outputs:** a product brief with intended outcomes and scope; persona/job/journey map; capability relationships; value records with measurement proposals; differentiation hypotheses with alternatives and disconfirming evidence; unresolved product choices. For a new product these can be provisional.

Cover the lifecycle relevant to the product: first value, normal use, exceptions, support, maintenance, renewal, and exit where applicable. Do not invent a buyer, tenant, integration, agent, or subscription model. Distinguish buying roles from daily users when the evidence supports both.

Describe the current workaround and value mechanism. Record the adoption burden and delivery/maintenance cost when known. A score ranks a proposal; it cannot establish customer demand. Claims about market uniqueness or willingness to pay require current comparison research and appropriate customer evidence. Demand claims also need customer evidence. Research or outreach must stay within the request's authorization.

**Readiness:** the requested definition connects the affected audience and outcome to a complete applicable journey. It identifies supporting capabilities and material unknowns. Label whether it is ready for review or accepted product direction. Open validation hypotheses can remain; unresolved choices that change release behavior become decision gates.

**Next action:** obtain a material product decision or propose a named validation/release horizon. Do not select a stack from a product hypothesis alone.

## 5. Decide release scope and architecture

**Sequence:** name the horizon and outcome → propose release-specific MoSCoW → map dependencies and capacity/cost uncertainty → compare architecture options → run bounded technical proof where a choice requires it → record the accepted decisions.

**Required outputs:** release brief and release-item decisions; rationale and dependency order; linked acceptance criteria; applicable architecture views; decision records; dependency/risk treatments; estimates with their basis or explicit unknowns. Include proof and a cost envelope before committing to a material unproven architecture choice. Existing accepted architecture can satisfy this requirement if still applicable.

| Priority | Decision requirement for this horizon |
| --- | --- |
| Must | The agreed release outcome or obligation fails without the behavior. Name that outcome and its dependencies. |
| Should | The behavior improves the outcome and a stated acceptable workaround exists. |
| Could | The behavior adds value if higher priorities fit the horizon's capacity and risk limits. |
| Won't this horizon | Keep the deferred behavior in the catalogue. Record the reason and reconsideration trigger. |

Unassigned priority is valid before a decision. Record the horizon, decider, decision state, rationale, dependencies, acceptance IDs, and actual commitment date if accepted. Proposing Must does not create a commitment. Resolve dependency conflicts explicitly; do not average competing priorities or infer them from code volume.

Review the applicable architecture views in the capture contract. They cover the product workflow through its technical and operating responsibilities. Use unknown for missing evidence and inapplicable with a reason for absent dimensions. Diagrams explain interfaces and responsibilities; they do not prove implementation.

**Readiness:** the selected release behaviors and material design choices have accepted decisions by the authorized decider; critical prerequisites have executable treatments; acceptance outcomes and evidence destinations are defined. Record remaining estimates and nonblocking questions. A scope proposal can be ready for review while implementation remains gated.

**Next action:** design the selected journeys, resolve a named blocker, or perform the bounded architecture proof required for a decision.

## 6. Design complete applicable journeys

**Sequence:** select the accepted journey → map interactions, state, permissions, and handoffs → prototype the uncertain interactions → specify observable scenarios and recovery → review against the outcome and existing design conventions.

**Required outputs:** journey and interaction design; state/data/interface contracts; main-path and material exception scenarios; executable acceptance plan; agent evaluation plan if agents participate; open design decisions. Use `write-feature-spec` for a detailed specification when available and needed.

Design initial setup and the first useful outcome to the depth the journey requires. Cover ordinary work and failure handling; include lifecycle exit where applicable. Permissioned products need actor definitions and access boundaries. Agent contracts need tool grants and human override. Define their evaluation cases, cost limits, retry/rollback, and versioning. Request participant research only when needed; label an agent walkthrough as an inspection.

**Readiness:** the agreed actor can complete the specified outcome. Transitions and exceptions are reviewable. Material design decisions are accepted, and acceptance checks can distinguish success from failure at their destinations. A screenshot establishes appearance only.

**Next action:** implement the smallest authorized vertical slice that can produce acceptance evidence. If implementation was not requested, stop at the design finish line and retain that action as pending.

## 7. Implement and verify the accepted behavior

**Sequence:** confirm authorization and accepted scope → implement a bounded slice across the applicable surfaces → run the project's required checks → exercise journey and boundary cases → record receipts against exact versions → assess release readiness.

**Required outputs:** the implementation or linked repository change; acceptance-to-behavior trace; verification receipts; failed checks and residual risks; destination-specific completion state. For a release, add rollout, recovery, support, and release acceptance records to the extent required by that product.

Trace `release item → capability → job/journey → source or current decision → design/architecture → implementation → acceptance evidence`. Check denial and malformed inputs when they can defeat the agreed outcome. Exercise applicable dependency failures, retries, and recovery. Keep a separate receipt for each verification layer defined in the capture contract.

**Readiness:** the applicable accepted criteria pass against the intended version and environment; required gates and material residual risks have explicit dispositions. A local pass establishes local readiness. Release, installation, publication, and live verification each require evidence at their own destinations and the relevant authorization.

**Next action:** repair a failed criterion, prepare an authorized release, or stop at the requested local finish line. Do not deploy or contact users to make a local task appear complete.

## 8. Maintain the baseline and select the next increment

**Sequence:** capture a source, decision, implementation, or feedback change → trace affected records → mark dependent evidence stale → reassess the smallest affected stage → record a checkpoint and next action.

**Required outputs:** impact records; refreshed artifact/status index; unresolved work; release/feedback evidence; continuation checkpoint. Add a hub projection and readback receipt only if the optional adapter is authorized.

**Readiness:** current claims point to valid evidence; stale and pending states are visible; completed artifacts and open work can be found through one home; the next action has its inputs, target, evidence, and authorization state. Durable files do not establish automatic enforcement or recurring maintenance.

**Next action:** the nearest evidence refresh, decision, experiment, enhancement, or implementation that serves the requested product outcome. Schedule recurring work only when explicitly requested.
