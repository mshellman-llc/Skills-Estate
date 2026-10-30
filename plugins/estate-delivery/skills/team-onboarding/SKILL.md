---
name: team-onboarding
description: 'Design a structured first-three-month ramp for employees, contractors, and agency partners. Use for a new starter, team restructure, inconsistent onboarding process, or knowledge transfer from one critical person. Covers engineering, design, product, marketing, and operations roles. Do not use for performance management, technology-specific training, hiring, or commercial offering design.'
---


> **Before writing: [`build-card.md`](_shared/build-card.md) plus
> [Writing Integrity review](_runtime/writing-integrity/references/detailed-review.md). Inputs, not a final pass.**

A repeatable framework for building an onboarding plan that ramps new team members predictably without burning out the people training them.

## When to use

- An employee needs a written onboarding plan.
- An existing onboarding process is informal and inconsistent.
- A team is growing fast and onboarding is the bottleneck.
- An external team member needs to ramp quickly.
- A team member is leaving and their knowledge needs capturing.
- Onboarding currently takes too long and you want to reduce it.

## When NOT to use

- For ongoing performance management. That is a different problem.
- For training on a specific technology. Use targeted docs and tutorials.
- For general documentation strategy. That is a separate discipline.
- For role definition or hiring. That is a different upstream problem.

## Required inputs

- The role: what the person will do, what success looks like at 90 days.
- Existing artifacts: docs, runbooks, codebases, design files.
- The team: who will mentor, who will pair, who answers what kind of question.
- Tools and access: what accounts and systems the new person needs.
- Time budget: how much time team members can invest in onboarding.

## The framework

A good onboarding plan operates on 4 layers. Build all four.

### Layer 1: Belonging (Day 1 to Week 1)

The first week establishes belonging. Productivity follows once the person has access, relationships, and a safe way to ask questions.

- Welcome message before they start.
- Workspace and accounts ready before day 1. No "we will get to that".
- A buddy or onboarding partner assigned (someone other than the manager).
- Day 1 schedule with focused work and a small number of useful meetings.
- Introductions to the people they will work with regularly.
- A first-week rhythm: daily check-in with manager or buddy.

### Layer 2: Context (Week 1 to Week 4)

The next phase is context. The new person needs to understand the system before they can change it.

- The product or business: what we do, who we serve, why we exist.
- The team: who owns what, how decisions get made.
- The technical or operational landscape: the architecture diagram, the main tools, the key files.
- The recent past: major decisions, recent launches, current priorities.
- Active projects: what is in flight and how it fits.

A reading list is part of this. Keep it short. Annotated. Curated.

### Layer 3: Contribution (Week 2 to Week 6)

By week 2 or 3, they should make a real contribution. Early delivery exposes the context they still need.

- A first task that is small, scoped, and shippable in week 2.
- Pairing or shadowing on a real piece of work in week 3.
- Independent ownership of a small project by week 4 or 5.
- Code review, design critique, or equivalent peer feedback from the start.

The first task matters. Pick something that touches the main systems but cannot break anything important. Something that ships gives confidence and visibility.

### Layer 4: Mastery (Month 2 to Month 3)

By the end of 90 days, the person should be a full member of the team.

- Owning a project end to end.
- On-call or on-rotation if the team has one.
- Contributing to roadmap discussions and execution.
- Mentoring or supporting the next new hire.

At 90 days, document what worked and what was missing for the next person.

## The 30/60/90 plan

Every onboarding plan needs explicit milestones after the first, second, and third months.

### 30 days

- Workspace, tools, and access fully set up.
- Has met every team member.
- Understands the product, the team, and the recent context.
- Has shipped or contributed to at least one real piece of work.
- Has a clear picture of their first major project or area.

### 60 days

- Owns a project or area independently.
- Knows where to find answers without asking every time.
- Has formed working relationships beyond the immediate team.
- Has made at least one meaningful improvement to a process, doc, or codebase.

### 90 days

- Fully productive in the role.
- Participating in roadmap and planning discussions.
- Capable of training the next new hire on parts of the system.
- Comfortable raising concerns and pushing back.

If someone is significantly behind at these three checkpoints, address it directly. Either the plan is wrong, the support is wrong, or the role fit is wrong. Hoping it resolves itself does not work.

## The role-specific overlay

The four layers apply to every role, with different evidence of progress:

| Role | First contribution | Independent ownership |
|---|---|---|
| Engineering | Ship a small bug fix or refactor | Own a feature or component and join the on-call path |
| Design | Own a bounded surface such as a setting page | Lead a feature design and its review |
| Product | Write a discovery record or competitive analysis | Own a feature specification and roadmap area |
| Marketing or content | Ship a small content change | Own a campaign, channel, or complete content asset |

Use `references/onboarding-checklist.md` for the detailed role-specific sequence.

## Workflow

1. Start the plan before the new person arrives. Do not write it on day 1.
2. Pre-stage accounts, hardware, and access. This is the most common day-1 failure point.
3. Assign a buddy with written responsibilities.
4. Send the welcome message and the day-1 schedule before they start.
5. Use the first week to establish belonging and context.
6. Check in daily for the first week, weekly for the first month.
7. Run formal milestone check-ins after each month.
8. After 90 days, do a retrospective: what worked, what was missing.
9. Update the plan based on the retrospective. Onboarding is a living doc.

## Failure patterns

- **No plan.** Day 1 with no schedule, no laptop, no accounts. Sets a tone.
- **Drinking from a firehose.** 8 hours of meetings on day 1. People remember nothing.
- **No real work for too long.** Three weeks of "reading docs" is demoralizing. Ship something small early.
- **All buddy, no manager.** Buddies are great but cannot evaluate or advocate. Manager is still on the hook.
- **Tribal knowledge as gating.** "Just ask the one person who knows" works until that person is on vacation. Document the answers they keep giving.
- **No milestone evidence.** Busyness does not prove that the person can perform the role.
- **Generic plan for every role.** Engineering and marketing have different first-week needs. Use the role overlay.
- **No retrospective.** The same gaps catch every new hire because nobody updated the plan.
- **Buddy with no time.** Assigning a buddy who is also drowning is a recipe for poor onboarding and burnout. Protect their time.
- **Skipping the customer or product context.** Engineers without customer context build the wrong things. Marketers without product context write thin copy.

## Output format

Deliverables:

1. **Pre-day-1 checklist**: accounts, hardware, access, buddy assignment, welcome message.
2. **Day-1 schedule**: meeting list, intros, first deliverable.
3. **First-week reading list**: 5-10 curated, annotated docs.
4. **Three-month milestones**: the explicit checkpoints for this role.
5. **Buddy guide**: responsibilities for the onboarding partner.
6. **Manager check-in cadence**: scheduled 1:1s and milestone reviews.
7. **Retrospective template**: to fill out at 90 days for next-time improvement.

Deliver as chat output by default. Write files only if the user asks and a writable workspace exists; on an ephemeral or hosted filesystem, keep everything in the reply.

## Reference files

- [`references/onboarding-checklist.md`](references/onboarding-checklist.md): A day-by-day, week-by-week checklist for the first 30 days, with role-specific variants and a three-month review template.

## Release gate (required)

Before you deliver, run the required gate. Full
spec in [`release-gate.md`](_shared/release-gate.md).

1. Apply writing-integrity to the prose. Use the bundled diagnostic tools to check saved writing. For
   a final artifact it emits a receipt the quality gate requires.
2. Run quality-gate before you call it final.

Do not present the artifact as finished until both checks have passed.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
