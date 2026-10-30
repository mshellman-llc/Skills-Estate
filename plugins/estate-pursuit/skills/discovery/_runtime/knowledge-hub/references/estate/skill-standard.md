# Skill release standard

An estate skill must perform its stated task with the resources available on its declared host. A valid folder or successful packaging command does not establish that capability.

## Authoring and ownership

Use a distinct lowercase hyphenated name. Describe the user request that selects the skill and distinguish adjacent workflows when confusion is likely. Keep the procedure in `SKILL.md` and load longer references when the task needs them.

Preserve working scripts. Keep the templates and adapters that the workflow uses. A portable skill may include a concrete implementation. Resolve branding through a profile. Keep account names and source locations configurable so the procedure can run elsewhere. Brand requirements come from the shared brand policy and selected profile.

The authoring intake records the job and its boundaries, then the input/output contract and selection examples. It also names the skill relationships and required capabilities. Risk controls and stewardship have their own fields. Costs and efficiency remain unknown until a dated run measures them. Drafts can contain incomplete intake records. A released skill cannot rely on unfinished workflow instructions or a missing required component.

## Release checks

| Check | Required evidence |
|---|---|
| Resources | Every promised local file and executable dependency exists in an isolated package. |
| Behavior | A representative task produces the intended result; meaningful failure cases behave as described. Retain the inputs with their outputs. Preserve errors from each attempt. |
| Selection | Requests for the skill route to it; adjacent requests keep their intended workflow. |
| Content | Compare generated material with the controlling inputs. A render or syntax check is insufficient. |
| Presentation | Inspect the actual pages or interface when layout affects use. |
| Overlap | Record whether the job belongs in a separate skill, mode, component, reference, adapter, alias or existing skill. |
| Host and sync | Test the declared invocation on the intended host. Compare installed files with the packaged source. Report cloud publication separately from local installation. |

When a dependency is unavailable, test a substitute against the requested result. A supported mode can also provide useful work within a stated boundary. For example, Salesforce metadata preparation can work offline; Salesforce deployment still requires an authorized org. Do not turn a simulated deployment result into a live success claim.

## Scope and publication

An internal repair needs checks for the changed behavior and affected dependents. Changes to routing also need adjacent-request checks. Changes to shared packaging or installers need the estate checks. Run those checks for a release as well.

Keep original source archives separate from the reusable release. Remove company-specific defaults and private sample data without discarding the workflows they illustrate. Use synthetic fixtures for reusable examples.

Use the repository's current build and sync tools. Their receipts must identify the exact source and destination state. Existing local edits must be reconciled before installation replaces them. Keep the test transcript and Git commit as distinct records. Record the upload separately from a verified host invocation.
