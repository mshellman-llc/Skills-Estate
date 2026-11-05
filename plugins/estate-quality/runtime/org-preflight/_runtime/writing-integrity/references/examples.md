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

## Correct a mistaken category without making it the message

The source describes a scheduling tool for clinic staff: they book appointments, assign clinicians and handle schedule changes. The AI mistakenly framed it as a marketing tool. The user corrects that mistake.

This replacement still makes the AI’s mistake the subject:

> The experience includes scheduling and staffing, whether or not marketing activity exists. This review shows how operational work differs from promotion.

For the staff-facing opening, write:

> Book appointments, assign clinicians and manage schedule changes.

The reader needs to use the schedule. The former marketing interpretation adds nothing to that task. Do not carry it into headings, diagram branches or UI labels. Replacing “marketing” with a subtler distinction would leave the same defect.

## Keep a correction the reader needs

A published event notice gave Tuesday as the date. The confirmed date is Wednesday, and recipients may have planned around Tuesday. A corrected notice should say the event is on Wednesday and identify the changed date. The reader needs that correction to act.

If only an unpublished draft had the wrong date, the finished notice should give Wednesday without explaining the AI’s earlier misunderstanding. When the requester asks what changed, explain that separately. Do not remove a material correction notice merely to avoid mentioning an error.

## Select facts for the requested copy

Release notes are requested from these internal notes: saved filters are available to beta accounts from November 4; filter names must be unique for each person; time savings have not been measured.

A supported release note is:

> From November 4, beta accounts can save filters. Give each of your filters a unique name.

Keep the date, availability limit and per-person naming rule. Do not broaden uniqueness to the whole workspace. The measurement gap prevents a claim about time saved; it does not require a disclaimer when the release note makes no such claim.

If the request instead asks whether saved filters reduced search time, answer that time savings have not been measured. If a draft claims they save ten minutes, remove that unsupported claim. If the requested copy must include a legal disclosure or a material approval condition, retain it. Source selection does not authorize hiding information the reader needs.

## Name sections and agents for their work

A solution brief has “The Bet” above a recommendation to pilot intake routing and “The Call” above discovery call notes. Agent cards use “The Surveyor” for reviewing intake requests and “The Cartographer” for mapping handoffs. Navigation uses “THE Workspace” for shared project files and “THE Project” for the intake-routing pilot.

Supported labels are “Intake-routing pilot recommendation,” “Discovery call notes,” “Intake review agent,” “Handoff mapping agent,” “Project files” and “Intake-routing pilot.” Review the whole set. “Bet” and “Call” alone still leave readers guessing. If the source does not explain an agent's responsibility, flag the missing detail rather than inventing one.

Keep “The project owner approved v3; Priya has v2.” Both articles and version identifiers carry meaning. Keep a decision reference such as `DEC-014` when readers need it to find the record. A memorable description may accompany an identifier but cannot replace it. An invented card code with no reference or operational use can be removed.

Keep an informative heading such as “The cost of delayed approvals,” the proper name “The Atlantic,” and character names in an intentionally theatrical piece. The recurring naming formula warrants review; it does not justify stripping every article or renaming meaningful entities.
