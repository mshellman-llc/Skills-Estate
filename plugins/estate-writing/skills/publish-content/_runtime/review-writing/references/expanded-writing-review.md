# Paragraphs, claims and response habits

Read this alongside [patterns.md](patterns.md) for every writing task. Check how the argument develops, what each sentence adds and whether the voice suits the reader.

Research review date: October 21, 2026. The cited studies report results from the models and tasks they examined. The repairs and examples are editorial advice written for this skill. They are not quotations from the studies or tests of authorship.

## Grammar and voice

Reinhart and colleagues found noun-heavy prose and more frequent present-participle clauses in the instruction-tuned models they studied. Their results varied by model. Rallapalli and colleagues' 2026 preprint found substantial differences by genre. Review whether the sentence suits its reader; these findings do not justify banning nouns, passives or particular sentence lengths. [Reinhart et al.](https://arxiv.org/html/2410.16107v2), [Rallapalli et al., preprint](https://arxiv.org/abs/2604.14111)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Actions buried in nouns | “Completion of the validation of the submission” obscures who does what. Use the supported actor and verb, such as “The rep validates the submission.” Keep defined technical nouns where needed. |
| Stacked modifiers and abstractions | “Enterprise customer lifecycle enablement optimization” does not explain an action. Unpack the terms into the actual task; do not invent a new label for an existing concept. |
| Repeated trailing clauses | Sentences repeatedly end in “enabling,” “ensuring,” or “driving.” Check whether each clause supplies evidence, an actual consequence, or decoration. State a supported consequence separately; cut the rest. |
| Tone that ignores the reader | A short internal review reads like a policy paper, sales pitch, or motivational post. Match the recipient's knowledge and the decision they need to make. Do not add slang or typos as a repair. |

## Paragraph and document structure

Kim and colleagues found differences in discourse structure, with greater structural variability in human texts in their comparison. Russell and colleagues' annotators noticed formulaic organization, vague optimistic endings, and recurring quotation placement. [Kim et al.](https://aclanthology.org/2024.acl-long.298/), [Russell et al., appendix D.3](https://aclanthology.org/2025.acl-long.267.pdf)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Repeated explanation of the same point | One finding is restated in the opening and again throughout the body before returning in the conclusion. Keep the clearest version. Each remaining passage must advance the explanation with evidence or a consequence, or give the reader a usable next step. |
| Identical paragraph formulas | Every paragraph starts with a claim, gives one example, and ends with praise or a summary. Organize around the actual reasoning. Different findings may need different amounts of explanation. |
| Mechanical evidence placement | Every paragraph ends with a quote or citation regardless of the claim it supports. Attach evidence to the claim it establishes; verify quotations before using them. |
| Automatic optimistic endings | A missing workflow becomes a generic promise about future success. End on the unresolved task or supported recommendation. Do not manufacture reassurance. |
| Generic scene-setting | The introduction explains how fast the industry is changing before addressing the artifact. Start at the actual subject, task, or decision unless background is necessary to understand it. |

For prose beside a table or another display, compare the information in both.
Keep a useful synthesis, qualification or accessible alternative; remove a
row-by-row paraphrase that adds nothing. Across the full artifact, distinguish
an established fact repeated for reassurance from a new verification or a
reminder the reader needs. See [repetition and urgency in sentence patterns](patterns.md).

Verify the structure's own claims: counts must agree with the distinct items,
comparisons must use equivalent bases, and separate containers must serve a
reader purpose. Check heading/content agreement and evidence for even a single
assurance. Review restated figures and legend narration for added meaning while
preserving needed keys, accessible alternatives and standalone summaries. See
[heading and structural accuracy](patterns.md).

## Claims and usefulness

Wikipedia's editors describe vague relationships and conclusions that follow a challenge with automatic optimism. Those are editorial observations. The remaining checks below come from this skill; they make no claim about how often AI produces these patterns. [Wikipedia editors' guidance](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Vague relationships | “The platform is connected with customer success” leaves the relationship undefined. Name the supported action or dependency. In a system map, specify what passes between systems. |
| Advice that repeats the desired outcome | “Improve the journey by making it more customer-centric” gives the author nothing to change. Name the action the reader can take and the evidence or condition that makes it useful. For a workflow, identify the missing actor, screen or handoff. |
| Transitions that imply unsupported logic | “Therefore” or “as a result” joins two claims without establishing causation. Supply the mechanism if evidenced; otherwise state the facts separately. |
| Artificial balance | A fixed strengths-and-weaknesses format invents praise or treats unequal problems as equal. Preserve actual strengths and prioritize findings by their consequences. |
| Unsupported emotional interpretation | “Customers will feel empowered” asserts an experience without research. Report the observed response, or identify a hypothesis and how to test it. |
| Precision without a basis | A percentage, score, time estimate, or named framework makes a vague claim look established. Verify its definition and source; preserve legitimate estimates with their basis. |
| Source references used as decoration | A paragraph names research, authorities, or documents without explaining what they support. Check the source and attach it to the precise claim. Remove unsupported borrowed authority. |
| Unnecessary disclaimers repeated throughout | A source limitation appears without a claim or decision that needs it, or repeats after every finding. Omit it when irrelevant; otherwise state it where it affects interpretation. Keep qualifications required to preserve a claim’s meaning and relevant evidence gaps in an audit or status report. |
| A correction displaces the reader’s purpose | The revised opening, labels or flow revolve around rebutting the AI’s earlier misunderstanding, even without mentioning the AI. Rebuild the passage around the audience’s actual task and supported facts. Remove explanations that only make sense to someone who saw the correction conversation. Keep a correction notice only when the reader needs the change itself. |
| Assistant commentary inside the deliverable | Promises to help, praise for the user, editing narration, or offers to continue interrupt the requested copy. Deliver the finding or requested copy directly. |

Review headings and calls to action against the actual task and evidence. A
status update does not create an approval gate or deadline. Preserve real
requirements and useful instructions, with their original scope and conditions.

## Agreement and the author's voice

Sharma and colleagues documented assistants favoring agreement with a user's beliefs across several tasks. Baumler and colleagues found that participant editing moved generated drafts toward personal style, while the edited texts still retained stylistic differences from unassisted writing under their measures. Check agreement and voice separately from grammar. The table combines concerns raised by these studies with the user's instructions for replies and edits. [Sharma et al.](https://arxiv.org/abs/2310.13548), [Baumler et al.](https://aclanthology.org/2026.acl-long.2030/)

| Review signal | What to inspect and how to repair it |
| --- | --- |
| Agreement before inspection | “You're absolutely right” commits to the user's diagnosis before checking the artifact. Inspect the claim and state what the evidence supports. A user preference needs no factual verification. Do not disagree merely to demonstrate independence. |
| Unsolicited reinterpretation | “What you really mean” replaces the user's request with the assistant's preferred problem. Preserve the requested decision and scope. Ask only if the ambiguity changes the work. |
| Invented familiarity or responsibility | “I know exactly how you feel,” “we've all been there,” or an unsupported admission pretends to possess experience or authorship. Respond to the stated concern. Attribute actions only when records establish them. |
| Personal voice flattened by polishing | A direct objection becomes a diplomatic essay; distinctive wording becomes generic professional language. Preserve the writer's position and supported degree of certainty. Use the author's confirmed voice sources when available; generic friendliness is not a voice profile. |
| Prompt echo without a judgment | The response paraphrases every requested dimension but never answers the question or assesses the supplied evidence. Give the requested answer, decision or finding with its supporting evidence. Repeat the request only where needed to resolve scope or ambiguity. |
| A template dictates the amount of content | Every finding receives the same headings and length, even when one sentence would suffice. Use required fields as completeness checks. Keep only the structure needed to follow the evidence and repair. |

## Read the revision for new mistakes

For each suspected pattern, identify what it does to this passage before editing. Preserve quotations, required terms and stylistic choices that carry meaning. A dash, passive sentence or three-item list can be appropriate.

Compare the revision with the source. Preserve required findings, conditions, figures, sources and acceptance checks within the requested scope; a summary need not reproduce every source detail. If a sentence contains both filler and a necessary qualification, rewrite around the qualification. Do not add anecdotes, errors or arbitrary changes in sentence length.

Read the argument even when the scanner finds nothing. The text must support its claims and, when the task calls for one, end with a step the reader can act on. Check that editing has not erased approval conditions, created robotic fragments or replaced justified warmth with bluntness. Stop when the passage communicates its meaning in the required voice.
