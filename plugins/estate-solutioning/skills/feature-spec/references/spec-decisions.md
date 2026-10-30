# Spec decisions

## Choose the smallest useful document

A compact development brief suits a known audience and bounded behavior. Explain the current problem and requested change. Include the constraints that affect delivery and the checks that establish acceptance. Add an open decision only when one exists.

A feature spec suits work with several states, permissions, integration boundaries, or teams. Describe the user outcome and current behavior before the proposed behavior. State the required data and permission rules. Explain dependencies and failure handling, then give acceptance criteria for the required behavior. Add rollout and measurement requirements only when they are part of the request or necessary to assess the feature.

A bug report suits an observed mismatch. Record the affected version or environment and the reproduction steps. Describe the actual result with available evidence. Give the expected result and its authority. If the intended behavior is unknown, that is an open decision. Do not invent a frequency or business impact.

Use the user's required format or existing project template. These document types are choices about depth, not mandatory headings.

## Convert prose into acceptance checks

For each requirement, identify the starting state, action or trigger, and observable result. Specify the destination and necessary evidence when completion could otherwise be ambiguous.

For example, a supplied requirement that members can save drafts could become: “Given an authenticated member with an unfinished draft, saving preserves the entered fields. Reopening that draft in a new session restores those fields.” If the source does not define access permissions, mark that decision pending before specifying who else can reopen it.

Cover failure or boundary behavior where omission would affect the outcome: invalid input, unavailable integration, permission denial, repeated submission, or an interrupted save. Choose the applicable cases; do not append every case to a cosmetic change.

Keep a proposed metric separate from a release criterion. “Reduce support tickets” needs a definition, baseline, time window, and source before it can be checked. In their absence, describe the desired outcome and propose measurement work without asserting a target.

## Handle decisions without blocking the draft

Use the confirmed choice when present. Identify an assumption as an assumption and explain its effect only when material. Ask for clarification when different answers change the user's experience or an acceptance check. A missing launch date can remain pending while behavior is specified.

A document may be ready for review while unresolved decisions prevent implementation. Say which state the evidence supports. No template field should default to approved, implemented, or released.
