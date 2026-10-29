# Skills to consolidate or maintain

The catalog has 54 task packages, 13 task modes, and 13 supporting modules. The map previously presented all 80 source workflows as peers. Modes and supporting modules usually arrive inside a task package; they are not 26 additional tasks to install.

This is a focused source review of overlapping workflows and stale guidance. The findings below are recommendations. No skill has been deleted or replaced, and no cross-host replacement benchmark has been run.

## Consolidation candidates

| Candidate | Recommendation | Capabilities to preserve | Evidence |
| --- | --- | --- | --- |
| Cross-platform skill release and Skill estate sync | Within Skills Estate, make account replacement and destination verification a maintainer mode. Preserve the generic release method for projects outside this estate. Retire the extra local front door only after both paths pass parity checks. | Non-estate source folders, private-account checks, complete ZIP inspection, prior-version recovery, ambiguous-upload handling, and invocation in each requested host. | [Release workflow](../skills/cross-platform-skill-release/SKILL.md), its [estate adapter](../skills/cross-platform-skill-release/references/estate-release.md), and [estate maintenance](../skills/skill-estate-sync/SKILL.md). The adapter delegates build and install mechanics to the same estate CLI. |
| Skill creation walkthrough | In Codex, use the installed system skill-creator for ordinary authoring. Keep the estate’s intake, scaffolder, and release-specific guidance as a maintainer adapter. Review other hosts before retiring their authoring entrypoint. | Governed intake, collision review, metadata scaffolding, supplied workflow preservation, and cross-platform packaging. | The [walkthrough](../skills/skill-creation-walkthrough/SKILL.md) repeats general skill anatomy and description guidance covered by the installed Codex creator. It also adds universal thresholds such as five repetitions and 200 words, and requires a first reference file regardless of the task. Its [scaffolder](../skills/skill-creation-walkthrough/scripts/scaffold_skill.py) and [intake](../skills/skill-creation-walkthrough/references/governed-intake.md) have estate-specific roles. |
| Code simplify | Consider moving the checklist into the development workflow if a separate invocation is not useful. This is a lower-priority convenience decision. | Behavior preservation, focused diff review, and relevant tests. | [Code simplify](../skills/code-simplify/SKILL.md) describes a code-review method and carries no separate implementation runtime. Source inspection does not establish that another host’s command produces equivalent results. |

## Repair stale guidance

**Formal architecture mode needs a wording and policy update.** It is already part of the `system-design` task package. Its entrypoint still requires an Estate logo, footer, fixed house voice, and a UI prose-check exemption. The current brand policy selects the project profile or neutral defaults, and the current writing standard covers UI text. Preserve its architecture templates and sourced technical-reference method while replacing those conflicting directions. See [architecture instructions](../skills/architecture-doc/SKILL.md), [brand policy](../policies/brand.md), and [writing standard](../policies/writing.md).

**The personal voice runtime contains an old description of prose-pass as house voice.** The current diagnostic module explicitly supplies tools and does not choose an author’s voice. Update that relationship wording; retain author selection, revocation, privacy, and scope rules. See [voice routing](../skills/personal-writing-style-runtime/SKILL.md) and [writing diagnostics](../skills/prose-pass/SKILL.md).

**The shared writing block is runtime guidance.** `tools/portable.py` inserts and validates the `ESTATE-WRITING` directive so packaged skills load the shared standard. It appears in the restored repository checkpoint `5095879`; that checkpoint alone does not establish its original author. The readable map now omits that block, source comments outside code, the repeated title, and the generic build-card preamble. Exact source and installable packages retain the runtime instructions.

## Already combined

The catalog already packages these as modes. They should remain visible as modes rather than competing installs:

| Task package | Included modes |
| --- | --- |
| `career-application` | Supporting application materials; resume figures and ATS wording |
| `deck-builder` | Scope decision deck |
| `discovery` | Maintain pursuit findings |
| `feature-spec` | Detailed UI and API specification |
| `project-scoping` | Rough estimate |
| `sales-process-mapping` | Review a sales journey or demo |
| `scope-options` | Interactive proposal or explorer |
| `service-offering` | Offering package planning; internal brief or external handout |
| `sf-devops-center` | Promote work items or stages |
| `statement-of-work` | Contract scope and obligation review |
| `system-design` | Formal architecture reference |

The source of this ownership is [the task catalog](../config/skill-catalog.json). Preserve complete mode workflows and their resources when simplifying the user-facing choice.

The current project-scoping workflow has a recent completeness repair: it preserves unestimated work and distinguishes estimated subtotals from complete project totals. Its reader guide was checked against that current entrypoint during this review. Its rough-estimate mode remains part of the same task package.

## Keep the distinct capabilities

| Workflows | Reason to keep them |
| --- | --- |
| Writing integrity and prose-pass | Writing integrity owns drafting and review. Prose-pass supplies executable diagnostics, figure tie-out, and review records. Keep its executable tools under the writing workflow. |
| Writing profile builder and personal voice runtime | One builds and confirms a private profile; the other chooses when that profile applies. The runtime template needs an author-specific installation adapter. |
| Megan’s writing style and generic writing review | The former is a personal profile. Retire its separate representation only after the replacement private profile preserves her confirmed rules and examples. |
| Product spec and detailed feature specification | They are already one task package. The detailed module preserves UI states, API contracts, persistence, and acceptance checks. |
| Process, sales process mapping, and journey mapping | An SOP or process improvement, sales ownership and record authority, and a person’s experience or service blueprint answer different questions. A newer map format does not replace all three methods. |
| Solution brief and system design | Solution brief assesses delivery feasibility through a validated solution graph and technical readiness path. System design explores architecture. Retain the different decisions and outputs. |
| Brand profile and brand renderer | One selects confirmed identity; the other implements rendering and checks the exported result. |
| Execution truth, org preflight, and quality gate | They check destination state, the Salesforce target, and deliverable readiness respectively. Shared wording can be shortened without removing those checks. |

The Salesforce deployment, DevOps Center, screenshot, and project-setup tasks belong in an optional domain group for people who need that stack. Their different targets and tools prevent a source-only conclusion that one supersedes the others. No live Salesforce host comparison was performed in this review.

## Internal workflows without a task package

Eight internal source modules have no containing task ZIP in the current dependency graph: `brain-work-item`, `execution-truth`, `github-repository-work`, `jtbd-framing`, `megan-writing-style`, `personal-writing-style-runtime`, `sf-headless-screenshot`, and `transcript-ingestion`. Their source descriptions and references do not establish whether a current host supplies them separately. Review their callers and actual host installation before treating them as redundant or promising their inclusion in a download.

For example, the current workspace routes material work to execution-truth, while the profile and project adapters have personal or host-specific roles. JTBD framing carries a methodology that a general process map does not supply. Keep these distinctions during any retirement decision.

## Recommended order

1. Keep the catalog’s task, mode, and supporting-module labels visible.
2. Repair the stale architecture and voice-runtime directions without removing their methods.
3. Combine release and estate-maintenance entrypoints after checking local installation, private account replacement, and failure recovery.
4. Reduce the general authoring tutorial to the estate-specific adapter after comparing representative creation, repair, and packaging tasks on each supported host.
5. Consider the code-review convenience entrypoint after the higher-overlap work.

Removal requires an inventory of callers, scripts, references, templates, failure handling, and accepted outputs. Check representative requests and one consequential failure path with the proposed replacement before retiring the old entrypoint. Preserve migration and rollback records.
