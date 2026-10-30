---
name: skill-creation-walkthrough
description: Create or repair a governed Skills Estate workflow with focused triggers, preserved resources, intake metadata and tested packaging. Use when adding a workflow to this estate or repairing its selection and output behavior.
---

Run this module's relative commands from the directory containing this WORKFLOW.md. Resolve that directory to an absolute path first. A command that explicitly names another working directory keeps that requirement. This file is a supporting workflow, not another installed skill entrypoint.


# Estate skill authoring

Use this mode for the estate-specific intake, collision review, scaffolder and release contract. In Codex, use the installed system `skill-creator` for general authoring guidance when available. On another host, use its supported authoring instructions or the method below. Host tooling is optional; preserve the same workflow and resources across supported hosts.

## Decide what to add

Identify the requested outcome, intended users, actual inputs and available tools. Inspect the closest existing workflows before creating another entrypoint. Extend an existing mode when it already owns the task. A repeated count, word count or reference-file quota does not decide whether a workflow belongs in a skill.

Use a skill when a bounded, reusable procedure needs task-specific instructions or resources. Use a saved prompt for a one-off request and the assistant's global instructions for behavior required in every conversation. A skill cannot replace an unavailable tool. Record the missing capability, the affected step and an available fallback; leave that step unverified when no fallback works.

Collect the task, intended audience and trigger situations, existing workflow files, and representative inputs and good outputs. Mark an unavailable example as a gap rather than inventing source evidence.

Keep local sketches outside canonical `skills/`. For a repository draft, complete [governed-intake.md](references/governed-intake.md). Before candidate status, identify the closest skills and record the collision decision, capability fallback and intended hosts. Keep cost and efficiency `unknown` until dated execution evidence measures them.

Inventory the original workflow's decisions, examples, templates, scripts, assets, failure handling and checks before rewriting. Preserve those capabilities or record each deliberate change. Do not replace a working implementation with general prose.

## Update an existing skill

Read its current entrypoint and the references and resources used by the affected behavior. Preserve dirty work. Edit the maintained source in place; do not run the new-skill scaffolder or create another entrypoint for the same job. Reproduce the reported defect, make the smallest complete correction, and compare the resulting output with the original requirements. Run changed-skill checks, plus overlap-group checks when trigger selection changes. Refresh the package and obtain the required review before installation.

## Write the focused workflow

The description controls trigger selection. Name the task and its meaningful selection conditions. Use failed selection tests to refine it; avoid catchalls that pull in adjacent tasks. Read [description-cookbook.md](references/description-cookbook.md) when the selection problem needs examples.

Use progressive disclosure: keep the essential procedure in `SKILL.md`, and link detailed references only where needed. [skill-template.md](references/skill-template.md) provides optional section guidance. A small skill may need no supporting reference. For example:

```markdown
---
name: example-workflow
description: Extract decisions from supplied meeting notes.
---

## When to use
Use for the defined task.

## When NOT to use
Route a neighboring task to its existing owner.

## Workflow
Follow the actual domain procedure and preserve its acceptance checks.

## Reference files
Link only the resources this workflow needs.
```

Read [methodology-vs-implementation.md](references/methodology-vs-implementation.md) when separating a general method from a host adapter. Keep environment choices configurable and bundle required implementations. Do not imply a tool exists because the old instructions name it.

## Scaffold a repository draft

Run the bundled scaffolder from this module's directory with an explicit project root and the actual workflow body:

```sh
python3 scripts/scaffold_skill.py example-skill \
  --root /path/to/project --display-name "Example skill" \
  --description "Prepare an account brief from supplied project evidence." \
  --owner "Project maintainer" --category analysis --runtime codex \
  --workflow /path/to/complete-workflow.md
```

The command creates `skills/example-skill/` and refuses an existing destination. Add `--reference /path/to/file.md` only for a required resource. Repeat `--runtime` for intended hosts. It defaults to no Knowledge Hub dependency; use `--knowledge-hub required` or `optional` only with a completed read/write contract.

The output includes the supplied workflow, metadata, governance intake and creation receipt. Finish the intake before promotion. Register the source, mode ownership and runtime dependencies in the existing catalog without replacing unrelated entries.

## Exercise and release

Test a realistic positive request, a relevant alternate request and a nearby request that should keep its existing owner. Inspect the actual output, source preservation and a consequential failure path such as a missing dependency. Record a host-selection observation separately from a local script test.

Use changed-skill checks for a narrow repair, overlap-group checks when routing changes, and the full estate checks for shared assembly or release changes. Apply [the skill release standard](references/estate/skill-standard.md). Validate, assemble and extract the portable package; execute its required resources away from sibling source folders. Preserve exact package and test receipts.

Diagnose failed selection from the observed request: add a missing selection condition when the skill fails to load, and narrow an ambiguous condition when it takes a neighboring task. Name that task's owner. Generic output needs a more specific procedure or example, not a broader description. Remove duplicated reference content and split long material at a useful decision boundary. Check adjacent examples so a correction does not merely fit one case. Recheck affected outputs and routing when dependencies change.

Use the containing maintenance workflow for build, installation, rollback and requested account replacement. Creating a draft does not install it. A source or packaging check does not establish discovery or execution in another host.

Deliver the complete workflow and required files in the requested repository. When file access is unavailable, provide the complete labeled file contents through the supported host. Include the trigger decisions, intake, validation evidence and actual remaining action; no reference file is required merely to fill a template.

Include the final description, intended and excluded trigger situations, the resource plan with each file's purpose, and the positive, alternate and negative acceptance prompts with their observed results. Keep unrun cases explicit. These outputs are required where relevant; fixed sentence, repetition and reference-file quotas are not acceptance criteria.
