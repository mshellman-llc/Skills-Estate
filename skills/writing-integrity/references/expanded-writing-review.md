# Expanded writing review

Use this reference whenever applying writing-integrity, including ordinary responses and new drafts. The short checklist in SKILL.md is not exhaustive. Review how the argument develops, what each sentence contributes, and whether the voice suits its reader.

Research reviewed October 21, 2026. Sources distinguish measured tendencies from editorial observations. The repairs and miniature examples below are authored editorial guidance, not quotations or validated detection rules. No single construction establishes authorship.

## Grammar and voice

Reinhart and colleagues found noun-heavy prose and more frequent present-participle clauses in the instruction-tuned models they studied. Their results also varied by model. Rallapalli and colleagues' 2026 preprint found substantial genre effects. Apply these findings to audience fit and readability; do not impose a universal ban on nouns, passives, or sentence lengths. [Reinhart et al.](https://arxiv.org/html/2410.16107v2), [Rallapalli et al., preprint](https://arxiv.org/abs/2604.14111)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Actions buried in nouns | “Completion of the validation of the submission” obscures who does what. Use the supported actor and verb, such as “The rep validates the submission.” Keep defined technical nouns where needed. |
| Stacked modifiers and abstractions | “Enterprise customer lifecycle enablement optimization” does not explain an action. Unpack the terms into the actual task; do not invent a new label for an existing concept. |
| Repeated trailing clauses | Sentences repeatedly end in “enabling,” “ensuring,” or “driving.” Check whether each clause supplies evidence, an actual consequence, or decoration. State a supported consequence separately; cut the rest. |
| Tone that ignores the reader | A short internal review reads like a policy paper, sales pitch, or motivational post. Match the recipient's knowledge and the decision they need to make. Do not add slang or typos as a repair. |

## Paragraph and document structure

Kim and colleagues found differences in discourse structure, with greater structural variability in human texts in their comparison. Russell and colleagues' annotators noticed formulaic organization, vague optimistic endings, and recurring quotation placement. These findings justify reviewing relationships across paragraphs as well as individual sentences. [Kim et al.](https://aclanthology.org/2024.acl-long.298/), [Russell et al., appendix D.3](https://aclanthology.org/2025.acl-long.267.pdf)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Repeated explanation of the same point | One finding is restated in the opening and again throughout the body before returning in the conclusion. Keep the clearest version. Each remaining passage must advance the explanation with evidence or a consequence, or give the reader a usable next step. |
| Identical paragraph formulas | Every paragraph starts with a claim, gives one example, and ends with praise or a summary. Organize around the actual reasoning. Different findings may need different amounts of explanation. |
| Mechanical evidence placement | Every paragraph ends with a quote or citation regardless of the claim it supports. Attach evidence to the claim it establishes; verify quotations before using them. |
| Automatic optimistic endings | A missing workflow becomes a generic promise about future success. End on the unresolved task or supported recommendation. Do not manufacture reassurance. |
| Generic scene-setting | The introduction explains how fast the industry is changing before addressing the artifact. Start at the actual subject, task, or decision unless background is necessary to understand it. |

## Claims and usefulness

Wikipedia's editors document vague relationships and rigid challenge-to-optimism conclusions in their own review work. Treat these as editorial observations. The other checks in this section are this skill's quality criteria; they are not claims of measured AI prevalence. [Wikipedia editors' guidance](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Vague relationships | “The platform is connected with customer success” leaves the relationship undefined. Name the supported action or dependency. In a system map, specify what passes between systems. |
| Advice that repeats the desired outcome | “Improve the journey by making it more customer-centric” gives the author nothing to change. Name the action the reader can take and the evidence or condition that makes it useful. For a workflow, identify the missing actor, screen or handoff. |
| Transitions that imply unsupported logic | “Therefore” or “as a result” joins two claims without establishing causation. Supply the mechanism if evidenced; otherwise state the facts separately. |
| Artificial balance | A fixed strengths-and-weaknesses format invents praise or treats unequal problems as equal. Preserve actual strengths and prioritize findings by their consequences. |
| Unsupported emotional interpretation | “Customers will feel empowered” asserts an experience without research. Report the observed response, or identify a hypothesis and how to test it. |
| Precision without a basis | A percentage, score, time estimate, or named framework makes a vague claim look established. Verify its definition and source; preserve legitimate estimates with their basis. |
| Source references used as decoration | A paragraph names research, authorities, or documents without explaining what they support. Check the source and attach it to the precise claim. Remove unsupported borrowed authority. |
| Unnecessary disclaimers repeated throughout | The same source limitation appears after every finding. State it once where it affects interpretation. Keep any qualifier required to preserve a specific claim's meaning. |
| Assistant commentary inside the deliverable | Promises to help, praise for the user, editing narration, or offers to continue interrupt the requested copy. Deliver the finding or requested copy directly. |

## Response behavior and preservation of voice

Sharma and colleagues documented assistants favoring agreement with a user's beliefs across several tasks. Baumler and colleagues found that participant editing moved generated drafts toward personal style, while the edited texts still retained stylistic differences from unassisted writing under their measures. These studies support checking agreement and voice separately from grammar. The checks below translate those findings and the user's working requirements into response and editing practice. [Sharma et al.](https://arxiv.org/abs/2310.13548), [Baumler et al.](https://aclanthology.org/2026.acl-long.2030/)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Agreement before inspection | “You're absolutely right” commits to the user's diagnosis before checking the artifact. Inspect the claim and state what the evidence supports. A user preference needs no factual verification. Do not disagree merely to demonstrate independence. |
| Unsolicited reinterpretation | “What you really mean” replaces the user's request with the assistant's preferred problem. Preserve the requested decision and scope. Ask only if the ambiguity changes the work. |
| Invented familiarity or responsibility | “I know exactly how you feel,” “we've all been there,” or an unsupported admission pretends to possess experience or authorship. Respond to the stated concern. Attribute actions only when records establish them. |
| Personal voice flattened by polishing | A direct objection becomes a diplomatic essay; distinctive wording becomes generic professional language. Preserve the writer's position and supported degree of certainty. Use the author's confirmed voice sources when available; generic friendliness is not a voice profile. |
| Prompt echo without a judgment | The response paraphrases every requested dimension but never answers the question or assesses the supplied evidence. Give the requested answer, decision or finding with its supporting evidence. Repeat the request only where needed to resolve scope or ambiguity. |
| A template dictates the amount of content | Every finding receives the same headings and length, even when one sentence would suffice. Use required fields as completeness checks. Keep only the structure needed to follow the evidence and repair. |

## What the existing review still covers

Retain the full writing-integrity review alongside this reference:

| Existing coverage | Patterns |
| --- | --- |
| Manufactured drama | Staged reversals; insider reveals; scripted questions and answers; dramatic label-and-reveal openings; slogans. |
| Authority and interpretation | Unnamed consensus; inflated importance; reader-direction phrases; decorative interpretation. |
| Generic language | Portable filler; inflated helper verbs; synonym rotation; performed warmth; hedge piles. |
| Mechanical form | Fragment stacks; repetitive cadence; automatic triads; stock transitions; decorative formatting; punctuation used to manufacture a voice. |

## Apply the review without introducing new defects

For each suspected pattern, locate the passage and explain its effect on this reader before choosing a repair. Preserve quotations verbatim and retain necessary domain terminology. Keep a contrast or an author's stylistic choice when it carries meaning. An em dash, a passive sentence, or a three-item list can be appropriate. Check repetition and purpose across the whole piece.

Preserve every supported finding, condition, number, source, and acceptance check. If removing a construction would erase required meaning, rewrite the sentence around that meaning. Do not create fake anecdotes, deliberate errors, arbitrary sentence-length variation, or a detector score target.

The scanner covers only part of this review. Read the argument against its evidence and check whether the reader can understand the point and act on it when action is required. A text can avoid every flagged word and still contain generic or unusable advice.

Use a second reading to check for damage introduced by editing. Concision must preserve decision conditions and approval state. Do not replace formulaic enthusiasm with robotic fragments, blanket negativity, or unnecessary bluntness. Keep genuine warmth when the relationship and message support it. Stop revising once the passage communicates its supported meaning in the required voice; do not cycle through synonyms to chase a lower score.
