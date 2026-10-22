# Visual argument

Choose a representation for the question it answers. A visual earns its place
when the audience can inspect a relationship or follow an explanation through it.
The brand profile supplies identity; it does not supply that reasoning.

## Choose the narrative

For an executive decision, state the recommendation early. Establish its evidence,
compare credible alternatives and explain the conditions that could change the
choice. End with the decision and responsible owner.

A sales deck starts with the buyer's evidenced problem. Show the consequence and
demonstrate the proposed improvement. Address objections with relevant evidence
before presenting the commercial choice. A feature tour cannot establish fit.

A technical deck establishes required behavior and constraints. Explain the
failure mechanism, then trace a concrete example through the proposed design.
Show how failure and recovery affect the decision. Define what validation must
establish before claiming the design works.

In a research readout, explain the question and enough method to judge the
evidence. Give findings visual support. Preserve uncertainty and competing
explanations when drawing implications.

These are starting structures. Let the audience's unanswered questions determine
the final order. Write the reason for each transition in the storyboard.

## Make the visual do the work

| Relationship | Candidate form | Required meaning |
| --- | --- | --- |
| Exact comparison | Table | Stable criteria and comparable entries; expose the material difference. |
| Measured difference | Bar or dot chart | Honest units and scale; include the relevant baseline. |
| Change over time | Line chart or slopegraph | Show when change occurs and its magnitude. Do not imply unsupported causation. |
| Handoff or branching process | Flow diagram or swimlane | Label decisions and show where work goes after each outcome. |
| Interaction or recovery | Sequence diagram | Keep actor identity stable. Show what each actor knows at the failure point. |
| Operating state | State diagram | Name transition conditions and the actor authorized to trigger them. |
| System responsibility | Context or boundary diagram | Identify included components and label interfaces crossing the boundary. |
| User behavior or record detail | Annotated screenshot or specimen | Point to the actual control or field that supports the explanation. |
| Delivery dependency | Dependency map | Show the prerequisite and what cannot proceed without it. |

Reuse a representation when it helps comparison. Do not impose a quota of visual
types or change the layout only to create variety. A table is appropriate when
the reader needs exact values. A diagram must define what its arrows mean.

Distinguish an implemented behavior from a proposed design. If an API contract is
unknown, show the dependency and investigate it before asserting the behavior.
Keep synthetic record identifiers visibly within a synthetic example. Never
create a plausible metric merely because a chart would look stronger.

## Plan each slide

Record the audience question and the answer supported by the evidence. State what
the body must explain beyond the title. Specify the visual relationship and the
evidence location. Write why the next slide follows.

For example, a retry slide needs more than a requirement to avoid duplicates.
Show an accepted request whose response is lost. Identify the original request
and the receipt that establishes its outcome. Keep an inconclusive lookup on a
separate branch; it does not establish that no posting exists.

Labels belong beside the objects they explain. Emphasis should locate the
relevant difference or exception. Remove a decorative object when it makes no
claim and supplies no needed context.

A live talk can pace a complex explanation across successive views. A reading
edition must retain the explanation without a presenter. Put necessary detail
in an appendix when it would interrupt the main argument; do not discard it to
reach an arbitrary slide count.

## Review the finished content

Answer the storyboard questions from the rendered slides. Name the element that
supplies each answer and note any inference the reader must invent. Check the
source behind each conclusion. Review the order separately from the typography.

For a mechanism, trace a concrete case through every relevant branch. For a
comparison, identify the same criterion in each option. For a quantitative
claim, reconcile the numbers and scale with the source. Check whether a label
overlap changes an arrow's apparent destination.

Automated checks can detect missing endpoints and out-of-bounds labels. They
cannot establish that the argument is useful. A clean render with an unexplained
mechanism fails this review.

## Research basis

The assertion-evidence experiment supports combining message headlines with
visual evidence in technical education. It does not isolate headline wording as
the cause or establish sales conversion effects. [Original study](https://www.ijee.ie/articles/Vol29-6/23_ijee2791ns.pdf).

Mayer and Fiorella describe research on signaling and spatial contiguity, including
placing labels near their graphics. [Chapter summary](https://doi.org/10.1017/CBO9781139547369.015).

Duarte distinguishes reading documents from projected slides. Its executive
guidance places the requested decision early. [Slidedocs](https://www.duarte.com/resources/books/slidedocs/), [executive presentations](https://www.duarte.com/blog/how-to-craft-and-nail-your-upcoming-executive-presentation/).

Storytelling with Data shows how alternative chart forms expose different
comparisons in the same data. [Worked comparison](https://www.storytellingwithdata.com/blog/2017/10/13/novel-vs-the-boring-old-bar-chart).
