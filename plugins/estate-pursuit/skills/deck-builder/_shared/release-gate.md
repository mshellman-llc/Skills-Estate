# Release gate

Before delivering a produced artifact, verify that it performs the requested
job. Packaging checks and a completion report do not establish that behavior.

## Required checks

1. **Capability:** run the producing workflow with representative inputs and
   inspect the actual result against its acceptance criteria. Test required
   modes, routes, calculations, handoffs, and error recovery. An installed skill
   must resolve its resources without relying on the author's source checkout.
2. **Evidence:** reconcile claims, figures, scope, and decisions with the stated
   sources. Separate assumptions from confirmed information. Never infer
   authorization, publication, installation, or deployment from a generated file.
3. **Prose:** review all authored writing, including instructions and indexes,
   for meaning and the applicable writing policy. Read every title with its body and remove abstract instructions that leave the actual task unstated. For narrative artifacts, run
   `prose-pass` and its receipt tool when required by the producer's workflow.
   Machine schemas and raw quoted evidence need structural and accuracy checks.
4. **Brand and presentation:** resolve the selected canonical brand profile and
   run `brand-renderer` for styled artifacts. Its colors, typography, assets, and
   layout rules come from that profile. Render and inspect the actual output;
   a literal-color scan cannot establish legibility, layout, or completeness.
5. **Quality:** use `quality-gate` to check the assembled evidence and applicable
   receipts. Resolve failures in the artifact or implementation before release.
   A passing receipt cannot override a visibly broken or incomplete result.

## Run the checks explicitly

Locate the installed `brand-renderer/scripts/runtime_preflight.py` and run it
with `--json` to resolve its local validators and selected assets. Use the
returned paths. A package must include or explicitly configure the dependencies
needed for its supported workflows.

Do not assume Claude Code, Codex, or a hosted surface has a post-write hook.
Only describe a hook as installed after inspecting its configuration and testing
its invocation. Even when a hook exists, run the applicable checks on the final
output and retain their results.

## Release evidence

Follow [the output contract](output-contract.md). Retain the current test outputs and minimal failure evidence, and record the
exact package or source version used.
Verify the installed candidate through realistic tasks before publishing a
corrected release. If a workflow needs manual rescue, fix the skill or its
dependencies and repeat the task.

Release claims must name the surface actually exercised. A local test of a
connector adapter does not prove that its live service accepted an operation.
