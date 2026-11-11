# Ownership and Growth

This document records the 2026-09-18 architecture decision. It separates current evidence from proposed migration so a local draft is not mistaken for an installed or retired system.

## Decision

Keep the existing capabilities. Consolidate ownership and shared rules, not every file.

| Component | Owns | Current provenance | Decision |
|---|---|---|---|
| `writing-integrity` | General tells, structural repairs, protected meaning, surface rules, and cross-surface evaluation | Saved locally in this output folder; validated; not installed or governed by the skill estate | Grow into the neutral core |
| `writing-style` | Megan's confirmed personal voice, routing, and audience calibration | Private Git source at `/Volumes/Meridian/Skills/personal-writing-style`, commit `4973564a9d330fad5640f3443a4b84ebdd561b78`; Claude and Codex copies are byte-identical to its six-file source tree | Keep; govern changes from the private source and defer runtime migration until builder evidence is sufficient |
| `writing-style-builder` | Authorized evidence collection, provenance labels, confidence, conflicts, history, correction, and revocation | Governed `AI-Skills/house-skills` source with identical local mirrors | Keep as the only profile-growth workflow |
| `personal-writing-style-runtime` | Generic routing template for one confirmed private profile | Governed `AI-Skills/house-skills` source with identical local mirrors | Keep; use as the future base for the thin Megan adapter |
| `prose-pass` | Aleysian house voice, token overlay, registers, construction and density checks, figure tie-out, and prose receipts | Governed `AI-Skills/house-skills` source with identical local mirrors; all current self-tests passed | Keep; make thinner only after a shared core exists |
| `brand-renderer` | Aleysian visual identity, assets, tokens, parity, accessibility, rendered inspection, and release gates | Governed `AI-Skills/house-skills` source with identical local mirrors; all current self-tests passed | Keep separate |

The canonical `AI-Skills` checkout was four commits behind `origin/main` during this audit. The four remote commits did not change `writing-style`, `prose-pass`, `brand-renderer`, or `skill-estate-sync`, so this decision is current for those paths without modifying the working tree.

The estate audit also reported an unmounted `build-graph` skill and five unrelated content skills that do not load the shared build card. Those findings are outside this writing-system decision and were not changed.

## Layering model

One component owns each question:

| Question | Owner |
|---|---|
| What facts, figures, scope, status, and qualifiers must survive? | Source evidence plus `writing-integrity` protected-meaning lock |
| Does this read like a generated template, and what structural repair fixes it? | `writing-integrity` general core |
| How does Megan sound in this relationship, channel, and communication job? | Confirmed private profile through `writing-style` |
| How does Aleysian sound, and did the prose pass its deterministic gate? | `prose-pass`, only when house voice is opted in |
| Does the Aleysian artifact use the real identity and survive rendering? | `brand-renderer` |
| Does the website, email, deck, or document fit its surface? | `writing-integrity` surface rule plus the relevant artifact tool |
| Can the result be released, published, or sent? | The applicable quality or release owner; never implied by a prose pass |

Do not serialize several rewrites. Resolve authorship and governing voice, produce one integrated revision, then run the applicable deterministic and rendered gates. If a post-gate edit changes copy, rerun every parity or figure check that the edit could affect.

## What to fold into the neutral core

The general core may own patterns that remain useful across people, companies, and surfaces:

- construction shape and recurrence;
- structural symmetry, fragment stacks, empty cards, and template rhythm;
- unsupported attribution, invented precision, vague quantifiers, and status inflation;
- replacement logic that says what to write instead of merely banning a form;
- protected spans, figure tie-out, and cross-surface meaning checks; and
- neutral surface rules for websites, email, decks, UI, and documents.

Do not fold these into the neutral core:

- Megan's raw examples, private facts, or inferred personal profile;
- Aleysian vocabulary, money authority, brand colors, fonts, logos, or publishing gates;
- legal, contractual, regulatory, or client-specific wording; or
- a copied executable from another skill without a declared source, owner, license, and test history.

The general construction and density code currently lives in `prose-pass`. Do not copy it into `writing-integrity` and create two engines. If deterministic tooling is added later, choose one authoritative code home, migrate tests with it, and make `prose-pass` a house configuration and register layer over that core. That refactor is proposed, not built.

## Tell registry

Every maintained tell should be a record rather than an accumulating paragraph. Use these fields:

- `id`: stable identifier;
- `name`: plain-language pattern name;
- `layer`: token, construction, density, visual composition, interaction, or evidence integrity;
- `surfaces`: where the tell applies and where it does not;
- `signal`: observable condition;
- `repair`: the replacement construction or design move;
- `protected_cases`: legitimate uses and verbatim boundaries;
- `false_positive_risk`: low, medium, or high with the reason;
- `provenance`: authorized correction, observed failure, maintained source, or research reference;
- `owner`: general core, private profile, Aleysian prose, brand, or a named artifact system;
- `tests`: positive case, clean negative case, and cross-surface regression cases;
- `status`: candidate, active, deprecated, or retired; and
- `added`, `last_confirmed`, and `version`.

Lexical tells decay quickly. Construction, density, evidence, and composition rules usually last longer. Keep those layers separate so a dated word list can change without destabilizing the structural engine.

## Growth workflow

1. **Capture only with permission.** A user's correction may guide the current edit. Storing the source, before-and-after pair, or inferred preference requires explicit authorization.
2. **Classify the evidence.** Mark it authored, templated, quoted, third-party, or AI-generated. Only authored language and the person's own edits support a personal profile.
3. **Assign the right owner.** A personal habit goes to the private profile. An Aleysian convention goes to `prose-pass` or `brand-renderer`. A surface-only behavior goes to the surface reference. A recurring cross-context failure is a candidate for the general core.
4. **Write the repair.** A ban without a replacement relocates the tell. Record the underlying communication job and the better construction or design move.
5. **Add behavioral evidence.** Create a synthetic positive case, a clean negative case, and relevant cross-surface cases. Keep private examples outside shared skill code.
6. **Test the affected class.** If one deck exposes repeated card symmetry, inspect the whole deck and the deck fixtures. If one website exposes decorative fake controls, inspect every visible action and state.
7. **Promote deliberately.** A safety or truth invariant may promote after one conclusive failure. A style preference should remain a candidate until repeated evidence shows that it generalizes without flattening valid human writing.
8. **Release by state.** Source change, local validation, commit, merge, bundle, installation, cloud upload, and verified behavior are separate events.

## Regression matrix

Maintain at least these classes:

- personal quick message, consequential email, and spoken talk track;
- organizational email and client-facing proposal;
- clean human writing that should remain nearly unchanged;
- website hero, feature area, workflow, error state, and mobile view;
- deck claim slide, comparison, timeline, financial slide, and presenter note;
- document with figures, qualifiers, quotations, and legal or defined terms;
- prompt-injection text embedded inside content; and
- the same approved source adapted across email, website, and deck without forcing one template onto all three.

For important cases, run more than once and fail any result that changes meaning, invents proof, applies the wrong voice, or produces a different answer merely to satisfy a pattern count.

## Retirement gates

A skill is retired only after all of these are true:

1. Every unique responsibility has a named successor.
2. Callers, links, hooks, bundles, and release gates point to that successor without a loop.
3. The successor passes the retired skill's positive, negative, and cross-surface cases.
4. Private data and organizational code remain in their approved stores.
5. The source change is committed and merged where governance requires it.
6. Local mirrors are reinstalled and read back as identical.
7. Cloud copies are removed or replaced and recorded; a ledger entry is not live verification.
8. Real behavior is checked on every required surface before the old name is declared gone.

## Current private source and future migration

The editable-source gap is closed. `/Volumes/Meridian/Skills/personal-writing-style` is the private Git source, and the original archive remains the recovery baseline. The source commit and both installed runtime copies are byte-identical for the six skill files. See [writing-style-archive-audit.md](writing-style-archive-audit.md) for the archive inspection record.

The original handoff and raw authorized evidence are still unavailable. The private repository therefore records an honest builder boundary: it does not invent a schema-compliant `profile.json`, authored-source counts, or provenance labels from the compiled skill. The current self-contained skill remains active.

Future migration sequence:

1. Name and authorize the material that may support a profile change.
2. Use `writing-style-builder` to propose provenance, confidence, conflicts, history, and any insufficient-evidence fields; confirm the proposal with Megan before writing it.
3. Build a thin Megan adapter from `personal-writing-style-runtime` only after the compact profile is valid and confirmed.
4. Run the current `writing-style` evaluation set, including important cases twice, and compare against approved outputs.
5. Install the adapter into Claude and Codex and verify both copies against the committed private source.
6. Retire the self-contained copies only after parity is proven and any cloud copies are separately resolved.

Until that sequence is complete, the current `writing-style` remains the governed runtime. Source restoration is complete; schema migration is deliberately pending.
