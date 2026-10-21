# Repair examples and acceptance checks

These miniature cases use invented inputs for illustration. They do not establish facts about a real person or project. Read them when choosing a repair or evaluating whether this skill preserves meaning. Equivalent wording is acceptable; the evidence and constraints determine whether an answer passes.

## Ordinary chat without a draft

Request: “The export finished. Where is the CSV?” Available evidence: the tool returned `/tmp/report.csv` and exit code 0.

Acceptable answer: “The CSV is saved at `/tmp/report.csv`.”

The response must give the location. It must not ask the user for a writing sample, echo the request, celebrate the result or add an offer to continue. A one-sentence answer still receives review.

## A progress update that preserves the unfinished work

Evidence: the local build passed; deployment has not been attempted.

Before: “Great progress! This isn't just a build milestone—it's a major leap toward a seamless release. The result? Production-ready confidence.”

After: “The local build passed. Deployment has not been attempted.”

The repair must retain both states. It must not imply a release, promise production readiness or invent a next action. Necessary status distinctions are meaningful contrasts.

## A conditional commercial claim

Source: “The proposed option adds 24 hours at $180/hour. Work starts after written approval.”

Before: “Unlock effortless scale with a $4,320 investment, ensuring immediate momentum.”

After: “The proposed option adds 24 hours at $180/hour, totaling $4,320. Work starts after written approval.”

The repair must retain proposed status, hours, rate and approval condition. The total is derived from the supplied figures. The editor must not trade a decision condition for a shorter sentence.

## A challenged claim

User: “You deleted the exclusions.” Evidence: the current draft contains the exclusions in section 4; no reliable change history identifies who edited it.

Acceptable response: “The exclusions are present in section 4 of the current draft. I don't have records showing who changed that section.”

Inspect the document before accepting or rejecting the factual claim. Do not invent an apology for deleting it, a recollection of restoring it or a reason another person changed it. A preference such as “put the exclusions earlier” needs no historical proof.

## A personal position that should survive editing

Source: “I don't want another status deck. I need to know who can approve the exception.”

Bad repair: “I appreciate the team's thoughtful reporting and would welcome enhanced visibility into decision-making ownership.”

Acceptable result: retain the source wording. It already names the objection and the needed decision. Do not soften the position, add praise or substitute abstractions for the approver.

## Advice with an actual action

Evidence: a form submits successfully, then displays an empty page; no next step is shown.

Before: “Improve the experience by creating a more intuitive, user-centric journey.”

After: “After submission, the page is blank. Show a confirmation and the next step.”

The repair must connect the observed behavior to a usable recommendation. It must not invent an abandonment rate, customer emotion or measured conversion benefit.

## Technical copy with precise conditions

Evidence: a parser now rejects a missing `account_id` before making an API request. The validation test passed locally.

Before: “This robust enhancement streamlines error handling, ensuring a seamless experience across the ecosystem.”

After: “The parser rejects requests without `account_id` before calling the API. The validation test passed locally.”

The repair must name the behavior, preserve the identifier and retain the local test boundary. It must not claim that every invalid request is handled or the change is deployed.

## Preserve meaningful punctuation and real lists

Source: “Choose one format—CSV, JSON, or XLSX.” The interface supports exactly those three formats.

Acceptable result: retain the sentence. Its dash introduces a real list, and all three items are supported. A scanner match alone does not justify deleting a format or replacing the sentence with fragments.

## Evidence and repetition across paragraphs

Evidence: a study observed task completion in 12 participants. It did not measure revenue. A draft cites it after a paragraph promising revenue growth and repeats that promise in its conclusion.

Required repair: remove the unsupported revenue claim and its repetition. Attach the citation to the supported task-completion finding, with the sample limit. Do not invent the number who completed the task. If that number is necessary, retrieve it from the study before writing it.

Passing this case requires reviewing the source-to-claim relationship and the complete draft. Swapping promotional words or moving the citation cannot fix it.
