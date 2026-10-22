# Editing examples

The inputs below are invented for these examples. They make no claims about a real project or person. An answer can use different words if it preserves the facts and conditions specified here.

## Answer a short question

The user asks, “The export finished. Where is the CSV?” The tool returned `/tmp/report.csv` and exit code 0.

“The CSV is saved at `/tmp/report.csv`” answers the question. Do not ask for a writing sample, echo the request, celebrate the result or add an offer. Review even a one-sentence reply.

## Report a build without implying a release

The local build passed. Deployment has not been attempted. The draft says:

> Great progress! This isn't just a build milestone—it's a major leap toward a seamless release. The result? Production-ready confidence.

Replace it with:

> The local build passed. Deployment has not been attempted.

Both states must survive. Do not claim production readiness or invent a next action. The distinction between a build and a deployment matters here.

## Keep a commercial approval condition

The source says, “The proposed option adds 24 hours at $180/hour. Work starts after written approval.” The draft replaces it with:

> Unlock effortless scale with a $4,320 investment, ensuring immediate momentum.

A supported revision is:

> The proposed option adds 24 hours at $180/hour, totaling $4,320. Work starts after written approval.

Keep proposed status, hours, rate and the approval condition. The total follows from the supplied figures. Shortening the sentence cannot remove the condition.

## Check a challenged claim

The user says, “You deleted the exclusions.” The current draft contains the exclusions in section 4. No reliable change history identifies who edited it.

After inspecting the document, an answer can say:

> The exclusions are present in section 4 of the current draft. I don't have records showing who changed that section.

The current file establishes what is present now. It cannot establish that the exclusions were never deleted. Do not invent an apology for deleting them, a memory of restoring them or a reason someone else changed them. “Put the exclusions earlier” is a preference and needs no historical proof.

## Preserve a direct objection

The source says:

> I don't want another status deck. I need to know who can approve the exception.

This edit changes the author's position:

> I appreciate the team's thoughtful reporting and would welcome enhanced visibility into decision-making ownership.

Keep the original. It identifies the objection and the needed decision. Added praise and abstract wording weaken both.

## Give advice the reader can act on

A form submits successfully, then displays an empty page with no next step. The draft says:

> Improve the experience by creating a more intuitive, user-centric journey.

Replace it with:

> After submission, the page is blank. Show a confirmation and the next step.

The recommendation must follow from the observed behavior. Do not invent an abandonment rate, customer emotion or measured conversion benefit.

## Preserve technical conditions

A parser now rejects a missing `account_id` before making an API request. The validation test passed locally. The draft says:

> This robust enhancement streamlines error handling, ensuring a seamless experience across the ecosystem.

A supported revision is:

> The parser rejects requests without `account_id` before calling the API. The validation test passed locally.

Keep the identifier, rejection condition, order and local test result. Do not claim the parser handles every invalid request or that the change is deployed.

## Keep a real list and useful punctuation

The interface supports exactly three formats. The source says:

> Choose one format—CSV, JSON, or XLSX.

Keep the sentence. The dash introduces a real list. A scanner match cannot justify deleting a format or turning the sentence into fragments.

## Check the citation and the whole draft

A study observed task completion in 12 participants. It did not measure revenue. The draft cites the study after a claim about revenue growth and repeats that claim in its conclusion.

Remove both instances of the unsupported revenue claim. Cite the study beside its task-completion finding and retain the sample size. Do not invent how many participants completed the task; retrieve that number if the answer needs it.

Review the source and the entire draft. Changing promotional words or moving the citation cannot repair an unsupported claim.

## Review the skill's own instructions

A skill description says:

> Audit or improve human-facing writing and presentation patterns across messages, documents, decks, websites, and UI while preserving voice, facts, uncertainty, scope, and format.

A clearer description says:

> Write and edit clear, specific prose in every response and deliverable. Remove formulaic AI writing while preserving facts, scope, uncertainty, and the author's voice. Also review existing drafts when asked.

Review the description, prompts and every instruction file. Replace phrases such as “resolve the governing layer” with the actual decision, such as “choose which voice rules apply.” Remove repeated explanations and decorative labels. Preserve the writing checks, exceptions, commands, examples and linked research.

Quoted examples of bad prose remain as examples. Instructions around those quotations must follow the skill's own rules.
