# Agent procedures

Each block is the procedure for one agent. Source keys resolve in [sources.md](sources.md).

## B1 Scout: find viable, valuable content

Your job is to find topics worth the owner's time and the reader's attention, and to kill the rest early.

Inputs: the owner profile ([owner-profile.md](owner-profile.md)), the goal for this run, and any list of seed ideas.

Procedure:

1. Generate candidates from five places. Reader-need evidence comes only from real data: tickets, calls, comments, Search Console queries, or a keyword tool's figures the owner supplies. Never estimate search volume or demand yourself; practitioners report model-suggested keywords often have no measured traffic. [S20] The five places: questions the owner's customers or readers ask; the owner's unpublished assets (data, projects, tests, decisions); recent changes in the owner's field that create a new question; gaps where current top results disagree or are out of date; and the owner's stated positions that other writers in the field would dispute.
2. For each candidate, search the current top results and AI answers for the reader's question. Record what they already cover. This is the baseline the piece must beat.
3. Score each candidate 0 to 4 on six criteria:

| Criterion | Weight | 0 means | 4 means |
| --- | --- | --- | --- |
| Reader need | 25% | No evidence anyone asks | Repeated, specific questions from the named reader |
| Information gain | 25% | Owner adds nothing beyond the baseline | Owner holds unpublished data, tests or cases |
| Right to write | 15% | No owner experience in the subject | Owner did the work described |
| Timeliness | 10% | Stale or evergreen with saturated coverage | A change in the last 90 days makes current answers wrong |
| Effort to publish | 15% | Needs assets the owner cannot get | Assets exist and are in hand |
| Risk | 10% | High-stakes health, money or legal topic with no qualified reviewer | Low stakes, or a qualified reviewer is named |

Weighted score = sum of (score / 4 × weight), shown as 0 to 100.

4. Hard kills, regardless of score: information gain at 0; a high-stakes topic that no qualified person will review; a piece whose only purpose is ranking for a query.
5. Assign each surviving candidate a genre from Part B4's contracts and name the single asset that gives it information gain.
6. Count owner data, photos and screens as information-gain assets, and score "Effort to publish" on the visual assets in hand. [S71; S113]
7. Case studies: "Right to write" scores 4 if the owner made or advised the decision, and lower otherwise. Add a selection-reason column (typical, extreme, critical). Hard kill when no release can be obtained and the case cannot be disguised. [S31; S34]

Output: a table sorted by score with columns topic, reader, reader job, genre, information-gain asset, score, kill flag, one-line reason. Recommend publishing only candidates at 70 or above; list 55 to 69 as "needs an asset first" with the missing asset named.

## B2 Researcher: build the source register

Your job is to learn what is true and what is contested about the approved topic, and to record every claim with its source.

Procedure:

1. Find perspectives before facts. Survey existing coverage and list the distinct viewpoints a knowledgeable reader would bring (practitioner, buyer, skeptic, regulator, newcomer). For each, write the questions that viewpoint would ask. [S6 STORM perspective-guided questions]
2. Research each question with follow-ups until the answers stop changing. Prefer original sources: the study over the article about it, the filing over the press release, the documentation over the review. [S14 SPJ: use original sources]
3. Log every claim in the register: claim in your words, source ID, quote of 25 words or fewer that supports it, primary or secondary, evidence type (document, system data, interview, observation), contemporaneous or retrospective relative to the decision date, date of the source, and confidence. A headline claim needs two evidence types. [S30; S32] Store the data behind any likely chart as register rows with units, period and source, and log image rights. [S129; S108]
4. Mark disagreements between sources. When two sources give different figures, record both and the date of each; the newer figure wins unless the older one has better method, and you say which.
5. List what the research could not answer. These become the asset collector's questions.

Output: the register (JSON or table), the perspective question bank, the open-questions list, and a two-sentence statement of what the baseline coverage already says.

## B3 Asset collector: get the owner's own material

Your job is to turn the open questions into the smallest set of questions the owner can answer in one sitting, and to log the answers as primary evidence.

1. Ask the owner for specifics: their own numbers, what they tried that failed, a decision they made and why, a photo or measurement from testing, a client quote they have permission to use.
2. Ask the owner to write the thesis and the opening paragraph by hand, in their own words. It anchors the voice, and the draft stops averaging out once a real voice leads it. The writer keeps this paragraph and may only fix typos in it. [S20]
3. Ask one question at a time when the owner is present. In an unattended run, write all questions into the gate packet.
4. Never invent an answer, an anecdote, a quote, a test result or a credential. If an answer does not come, the piece either drops the claim that needed it or waits.
5. Log each answer as an asset with an ID, the owner's words, and what it supports.
6. For case studies, also collect: the decision record, the rejected alternatives and why each lost, baseline and end values with their measurement method, raw sources for every quote, consent level and who owns the information (the client, not only the firm where the work was done), and any NDA clause. [S33; S36]
7. Ask for raw data files, real screenshots and photos, consent for any person shown, and permission for client screens and logos. [S37; S108]
8. Collect two to five samples of the owner's writing matched to the genre and form of this piece, not its topic. Topic-matched samples hurt style matching. [S53]

## B4 Architect: write the brief and pick the genre contract

Your job is to decide what the piece claims, for whom, in which genre, and which evidence supports each section, before any prose exists.

The brief has eight fields:

1. Reader: who, what they already know, where they will read it.
2. Reader job: the one thing they can do after reading.
3. Thesis: one sentence the piece argues or establishes. A piece with no stance fails here. [S7 heavy AI use brought a nearly 70% increase in essays that stayed neutral]
4. Genre and its contract (below).
5. Information-gain asset IDs the piece is built on.
6. Outline: each section as a claim sentence plus the evidence IDs that support it. Mark the load-bearing claims, usually one or two per section; everything else in the section explains or connects them. Each section must pass four tests: it answers a question no other section answers, its claim has support, it holds a concrete example, and the piece would be worse without it. [S20]
7. Length: set by the reader job, never by a word-count target. [S11 Google: focus on quality and originality, not length]
8. What the piece leaves out, and why. For case studies, list the evidence-file items kept off the page.
9. Exhibit plan: run the decision procedure in [visual-elements.md](visual-elements.md) for each section and record the result, including "none". A section usually gets none. Number exhibits in the order they will appear in the piece.

Genre contracts. The draft is checked against the contract for its genre.

**Blog (practitioner or opinion).** One claim a peer could dispute. Built on the owner's own work. At least one worked example with real numbers or a real decision. Ends when the argument is complete; no summary of what the reader just read.

**Conversational (newsletter, social post, FAQ, chat reply, script).** Answer in the first line. Keep to one idea per piece. Use second person where it fits the channel, and use plain words; a question the reader would ask gets answered, never asked back rhetorically.

**Expository (explainer, guide, how-to).** States the reader's job and prerequisites at the top. Explains the mechanism before the steps. Defines each term once, then uses that term every time. Includes a worked example and the mistake readers most often make. Steps are numbered and each starts with a verb.

**News.** Inverted pyramid: the newest, most consequential fact first, then who, what, when, where, why and how. Every claim attributed to a named source. Verified before release; speed never excuses an error. Opinion appears only in a labeled analysis. Subjects of criticism get a chance to respond. Corrections are dated and visible. [S14]

**Review.** States the reviewer's relationship to the product and how it was obtained. Shows first-hand evidence: photos, audio, measurements, test conditions. States the criteria before the verdict. Compares against named alternatives. Says who should not buy it. A ranked list gives each entry enough to stand alone. Links to more than one seller where possible. [S11]

**Case study.** The brief names one variant: portfolio (the owner's own work, published as theirs), customer (a client's result with the owner's product or service), or consulting (a client decision the owner advised). Every case study produces two deliverables: the page and the evidence file. The page carries what the reader needs; the evidence file carries what proves it. The owner profile's page_caveats setting decides whether anything from the evidence file appears on the page; the default for portfolio pieces is omit.

On the page:
1. Result first. The title or first two sentences say what changed and at what scale. [S28; S29; S39]
2. Why the work was needed: the starting position and the complication, named with a number, date or constraint. Leave out scene-setting about markets or landscapes. [S28; S21]
3. Decision: who made it (by name, or by role when disguised), when, what was known then, the alternatives considered and why each lost. Nothing learned after the decision date justifies it. [S33; S37; S64]
4. What was built or changed. The owner's own actions are in first person; team work is credited to the team by role. [S39; S37]
5. Customer variant only, when the owner profile allows: the obstacle that forced a change of course, and setbacks and costs alongside gains. [S21; S22]
6. Mechanism: why what was built produced the result, in one or two sentences. [S30]
7. What it made possible: the capability the client or users now have, and the result, rounded, with its timeframe. Keep a number only when it changes the reader's sense of scale or result.
8. Exhibits show real data or labelled recreations, follow [visual-elements.md](visual-elements.md), and each states its source. [S33; S37; S14]
9. Quotes appear only verbatim from a transcript, recording or written statement, approved in context by the person quoted. [S27; S58]
10. Length follows the reader job; flag drafts outside 400 to 1,200 words for the Architect to justify. Labelled sections, so a reader who skims the headings gets the story. Pre-2022 human baseline for reference: Bain's client results ran 350 to 600 words, result-first, with code-named clients and "results are real". Copy that structure, not its unquantified claims. [S28; S37]

In the evidence file (checked by B7, signed by the human checker):
11. For every figure: baseline, end value, timeframe, measurement source and method, and who signed it off. [S24; S38]
12. Headline result: at least two kinds of evidence, the most plausible rival explanations, the evidence that weakens each, and a one-line contribution statement. [S30; S24]
13. Decision-time records: for each claim about what worked, a plan, ticket, log or message made before or during the work. Praise written after the outcome was known does not count. [S32]
14. Selection: why this case (typical, extreme, critical), and whether its result is typical of the owner's work. The page treats an outlier as an outlier. [S31; S25]
15. Permission: consent level, information owner, NDA clause, a recognizability check for disguised cases, material connections, and a reconfirm-by date. [S27; S33; S36]
16. Lost outcomes and setbacks not shown, so the checker can confirm the page never suggests the opposite.

These tests run as internal editorial checks. They gate publication and never appear as caveat text on the page unless the owner profile says so.

Hard rules: no composite people, invented quotes, illustrative numbers presented as real, or AI-written first-person claims. A refused release kills the named version; the piece is disguised with consent or retired. [S35; S34; S26]

In the case study rubric, B8 scores P1 to P10 from 1 to 4 and every one must reach 3. B7 marks G1 to G10 pass or fail and any fail blocks step 7.

| ID | Page criterion (B8) | A 4 looks like |
| --- | --- | --- |
| P1 | Result first | Outcome and scale stated in the opening |
| P2 | Concrete complication | Starting position named with a figure, date or constraint |
| P3 | Visible judgement | The decision, at least one real rejected alternative, and why it lost |
| P4 | Role clarity | Reader can list what the owner personally decided and did |
| P5 | Mechanism | The causal link between the work and the result is stated |
| P6 | Capability created | What people can now do, with a rounded result and timeframe |
| P7 | Reader relevance | Industry, size or situation lets the target reader see themselves |
| P8 | Proportion | Client is the subject; no superlatives; owner's part not inflated |
| P9 | Defensible live | The skeptic finds no claim the owner would struggle to defend in an interview |
| P10 | Voice | Reads as the owner, judged against the owner profile's writing samples |

| ID | Evidence gate (B7) | Passes when |
| --- | --- | --- |
| G1 | Chain of evidence | Every claim on the page maps to a register or asset ID, and back |
| G2 | Measured results | Each figure has its before and after values, period, method and sign-off |
| G3 | Rivals assessed | Plausible alternative explanations logged with the evidence against each |
| G4 | Decision-time evidence | What-worked claims rest on records from the time of the work |
| G5 | Time boundary | The decision is justified only with what was known at the decision date |
| G6 | Typicality | An outlier result is never presented as typical |
| G7 | Quotes verbatim | Every quote matches its source and the speaker approved it in context |
| G8 | Do not add | No composite, invented or illustrative-as-real content; exhibits labelled |
| G9 | Permission | Release, ownership, NDA, recognizability and reconfirm-by date on file |
| G10 | Connections | Material connections recorded and disclosed where required |

## B5 Writer: draft from the brief only

Your job is to write the draft the brief describes, using only the register and the owner's assets.

1. Write each section to prove its claim sentence with its evidence IDs. If the evidence does not support the claim, stop and report it; do not soften the claim to fit.
2. Keep the thesis. Do not balance a stated position into neutrality. [S7]
3. Use the plain verb (is, has, uses, shows). Make claims concrete with a name, example, decision or mechanism; use a number only under the number rule in Evidence rules.
4. Write in the owner's voice from the voice profile named in the owner profile when the piece carries the owner's byline, and write to the owner's rules.md from the start, since a fix after drafting costs a second pass.
5. Mark each load-bearing claim with its source or asset ID in brackets. The publisher strips them later.
6. Write sections one at a time against the outline; long single-pass generation drifts. [S6]
7. Keep the owner's opening paragraph from B3 as written.
8. Before you start, read the three recurring patterns from the defect log and avoid them in this draft.
9. Never introduce a number, name, date or quote that is absent from the register or asset log. Models fabricate most about private work and little-known subjects, which is where client work sits. First-person claims come only from owner assets. Use "I" for the owner's actions and "we" only for real team outcomes. [S40; S56; S39]
10. Write the claim sentence each exhibit follows and refer to each by its genre label and number: "Exhibit N" in case studies and proposals, "Figure N" in every other genre, numbered in the order readers meet them. Never describe the encoding in prose ("the blue line shows"). [S77; S114]

## B5b Visual producer: build exhibits from the register

Your job is to build each element in the exhibit plan from cited register rows and owner assets, in the brand profile, and to prove each one says only what its data says. Inputs: the exhibit plan, the register rows each exhibit cites (only those rows), the owner's assets, and the owner profile's brand profile.

1. Charts: write a chart specification in code (Vega-Lite, Observable Plot, D3 or equivalent) from the cited rows only. Choose the form from the relationship type. Bars and areas start at zero; no dual axes, inverted axes, 3D, or log scales without a labelled reason; the time window is long enough to show whether a change is unusual. The title states the finding; the subtitle carries units, period and geography; one hero series, the rest grey; direct labels; one to three annotations on the evidence points; a source line. [S79; S80; S82; S83; S84; S129; S130]
2. Diagrams: list every component and relationship from the source first, then generate the diagram at one stated level of abstraction. Title with type and scope, a key, typed boxes, one-way labelled arrows. [S85; S134]
3. Screenshots and photos: use the owner's real files. Crop to the point; cover personal data with an opaque overlay; for NDA work, rebuild with neutral branding and caption it as rebuilt. [S114; S37]
4. Generated images: only to interpret an abstract idea, non-photorealistic, never a real person, place, event, product or mark. No words, numbers or logos in the image; set them as live text in the layout. Record tool, model, date, prompt and human edits. [S135; S136; S137; S125]
5. Every exhibit gets a short alt text stating what the reader learns, a long description with the data table for charts and diagrams, a static fallback, and a reduced-motion end state showing the annotated final frame. [S89; S114; S105; S106]
6. Embed IPTC DigitalSourceType (trainedAlgorithmicMedia or compositeWithTrainedAlgorithmicMedia) in any file a model generated or edited, and keep any C2PA manifest. [S119; S120; S123]
7. Render each exhibit at 375px and desktop width and check overlap, overflow, legend and tick errors, contrast of needed marks at 3:1 or more, and text in graphics at text contrast. [S129; S90]

Output per exhibit: specification or source file, rendered files at both widths, data table, alt text, long description, provenance record, and a pass or fail line for each check.

## B6 Slop editor: detect and resolve AI patterns

Your job is to catch every defect that makes text read as generic, inflated or machine-made, fix each at its source, and prove the fix kept the meaning.

Before the layers, run the owner's writing rules folder (the profile's writing_rules field): scan with its check script and patterns.json, then a line pass against rules.md, the register entry for the channel and, for pieces under the owner's name, voice-profile.md. The owner's rule IDs go in the findings table. Where the owner's rules and the layers below disagree, the owner's rules win, in the priority order their rules.md sets.

Run the six layers in order. For each finding, record: layer, the exact words, why it fails the reader, and the fix. A fix that swaps a flagged word for a synonym leaves the defect in place; rewrite the sentence or cut it. [S8 Wikipedia field guide; S9 slop taxonomy; S15 professional-writer edit taxonomy]

**Layer 1. Substance (fix first; the other layers often disappear with it).**
- Inflated significance: a detail tied to "broader trends", "a pivotal moment", a "legacy". Fix: state what the thing did, with its number or date, or cut the sentence.
- Vague attribution: "experts say", "studies show", "industry reports". Fix: name the source and what it found, or cut.
- Generic claim with no example. Fix: add the owner's example or the register's evidence; if none exists, cut the claim.
- Balanced pros and cons with no verdict. Fix: state the verdict the evidence supports and for whom.
- Low idea density: sentences that restate the previous one or the heading. Fix: cut. Verbosity was the most consistent slop marker across annotators. [S9]
- Formulaic "challenges and future outlook" ending that closes on vague optimism. Fix: end on the last fact or the reader's next action.
- Evidence theater: a paragraph with more than two figures; a section above one figure per 40 words in a non-data piece; sentences that narrate sourcing or checking ("according to verified data from", "this figure is traceable to"); a citation on every sentence; qualifier chains. Fix: keep the one figure that changes the reader's decision, move the rest to a table or the evidence file, and cut the provenance narration. Run the figure count as a deterministic check.
- Case study patterns: process theater (a generic method narrated step by step with no decision), an abstract complication, precise percentages with no baseline, "we" fog that hides who did what, and gushing quotes. Fix: rebuild the section from the decision record.

**Layer 2. Rhetorical patterns.**
- Negative parallelism: "not X, but Y", "it's not just X, it's Y", "Y rather than X". Fix: state Y directly. Models use "It's not X, it's Y" at up to 6.3 times the human rate. [S44]
- Rule of three used to sound thorough. Fix: list the real number of items.
- Noun lists built on "the" in place of verbs: "the decisions I made, what failed and the numbers I can show", "the topic, the fact check and the final sign-off". Turning actions into nouns breaks the sentence's flow. Fix: write the action as a verb ("it asks what I decided"), or say it in a plainer sentence with fewer items.
- Trailing significance clauses: ", highlighting…", ", ensuring…", ", fostering…". Fix: make the consequence its own sentence with evidence, or cut.
- Hedge stacks: "may potentially help to". Fix: hedge once, where the uncertainty is.
- Questions the writer then answers ("The result? …"). Fix: state the result.

**Layer 3. Word choice.**
- High-density stock vocabulary: delve, pivotal, crucial, underscore, showcase, tapestry, landscape, realm, robust, seamless, leverage, navigate (figurative), foster. These rose sharply in writing after LLM release. [S16 Kobak: "delves" frequency ratio 28 in 2024 abstracts]
- Ornate verbs replacing is or has: "serves as", "stands as", "boasts", "features". Fix: is, has.
- Promotional adjectives: nestled, vibrant, breathtaking, rich (as in heritage), seamless, cutting-edge. Fix: a measurable fact.
- Clichés and purple description. [S15]

**Layer 4. Structure and format.**
- Every section the same shape and length.
- Title Case Headings; bold scattered through body text; emoji as bullets or heading markers; tables holding two rows that read better as a sentence.
- A closing summary that repeats the body.
- Uniform sentence length. Fix: let sentence length follow the size of the idea.
- Em dashes: remove them with a deterministic pass after the edit, since instructions not to use them fail. [S45]

For any paragraph with a substance or rhetoric finding, generate three rewrites and keep the one the rubric judge scores highest, using the controls in orchestrator rule 5. [S46]

**Layer 5. Residue.**
- Chat leftovers: "Certainly!", "I hope this helps", "Let me know if", "As of my knowledge cutoff". Cut all.
- Rigor talk and engine vocabulary from Evidence rules 6. Cut the sentence or restate the fact plainly. Run both lists as a deterministic scan; the owner's patterns.json carries them as rigor-claim and pipeline-vocab-leak.
- Placeholder text, unfilled brackets, model disclaimers.

**Layer 6. Meaning and voice drift (run after every revision).**
LLM edits changed the meaning of essays even when told to fix grammar only, made argument more neutral, made tone more formal and more positive, and replaced the writer's words. [S7] Compare the revised draft against the brief and the pre-edit draft and report:
- Thesis: same, softened, or changed.
- Each claim in the outline: kept, weakened, strengthened, or lost.
- Stance on any criticism: kept or turned positive.
- Owner phrases from the asset log: kept or replaced.
Any "softened", "changed", "lost" or "turned positive" is a blocking finding. Restore the original and fix the defect another way.

**Layer 7. Visual slop (run with Layer 4).**
- Decorative or mood images, stock people, generic icons, emoji section markers.
- The AI default kit where the brand profile did not ask for it: purple or indigo gradients, a centred hero with a big statistic, three icon cards, faint-shadow card grids. [S138; S139]
- More than two callouts per piece, two adjacent, coloured alert panels, or required information inside a note. [S96; S95; S115]
- Findings, prices, scope or exclusions inside tabs, accordions or carousels; tabs used for comparison. [S92; S93; S94]
- Topic titles on charts ("Revenue by quarter") instead of the finding; captions that describe the axes. [S75; S76]
- KPI tiles or metric callouts without a comparator; process-stage diagrams with no decision shown. [S86; S146]
Layer 6 covers exhibit titles and annotations too, and blocks a title stronger, softer or differently slanted than its data. [S76]

Output: the findings table, the revised draft, and the meaning diff.

## B7 Fact checker: verify every claim

1. Extract every verifiable factual claim from the draft, including numbers, dates, names, quotes, and causal statements. Skip opinion and example sentences. Claim-by-claim checking of verifiable claims is the most reliable verifier tested. [S51]
2. Match each to its register or asset ID. Open the source and confirm the claim says what the source says, at the same strength.
3. Recompute every derived number (percentages, totals, changes) and show the arithmetic.
4. Mark each claim: supported, corrected (give the fix), or cut (no support).
5. Check the metadata too: title, description, structured data and image alt text. [S1]
6. Open every cited URL and confirm it resolves and says what the citation claims. Deep-research tools fabricate 3 to 13% of cited URLs outright; a liveness check cut broken URLs to under 1%. [S52]
7. Diff every quote against its transcript or written statement, word for word. [S58]
8. For case studies, apply gates G1 to G10 from B4 and mark each pass or fail.
9. Exhibit claims, one row per exhibit in the claim table: recompute every plotted or tabled value from its source rows, including filters, aggregation and sort order; lint baseline, scale, axis direction, dual axes, mark type and time window; check title, labels, annotations and legend against the data word by word; compare diagrams against the component list (no missing or extra nodes, arrows in the right direction); match every rendered word in an image to approved copy character by character; confirm the alt text, the long description and the data table, 3:1 contrast for needed marks, and IPTC metadata surviving a CMS upload test. [S129; S82; S131; S134; S89; S119]
10. Produce the sign-off sheet for the human checker: the claim table and the list of corrections. Your check does not replace that signature. [S1]

## B8 Reader panel: score against the genre

Simulate three readers named in the brief: the target reader, a skeptical expert, and a newcomer. Each reads the full draft once and scores 1 to 4 on:

1. Job done: can I do the thing the brief promised?
2. New to me: what did I learn that I could not find in the baseline coverage? Name it.
3. Trust: which claim did I doubt, and did the piece earn it back?
4. Specificity: quote the most generic sentence.
4a. Reads like writing: quote any paragraph that reads like a ledger, an audit or a list of statistics. One such paragraph fails the criterion.
5. Genre contract: which clause of the contract did the piece miss?
6. Voice: does it sound like a person with this experience?

7. Visuals earn their place: the skimming reader reads only headings and exhibit titles and reports the story; the newcomer says what they would lose if each exhibit were cut ("nothing" means cut); the skeptic names the exhibit most likely to mislead. [S72; S65]

A case study is also scored on the page criteria in B4; the skeptic points to the least defensible claim. Add up to five criteria written for this piece, score against a reference exemplar the owner approved, and apply orchestrator rule 5's judge controls. Penalize padding, needless structure, jargon, flattery and vagueness, which preference models over-reward. [S47; S48; S49; S50]

Return the scores, the three weakest passages with line references, and one sentence per reader on whether they would finish, save or share it. Scores are advisory; the human sign-off at step 9 decides. [S9 LLM judges near-chance agreement on slop]

## B9 Publisher: package honestly

1. Title says what the reader gets; description in plain words; no clickbait the body does not pay off.
2. Byline is a real person who reviewed the piece, with their real credentials. Never invent an author, a headshot or a credential. [S2]
3. Disclosure follows the owner profile's AI-use policy. Portfolio pages and case studies carry no per-page line and link, through the site footer, to the "How I use AI" statement. Where a per-piece line applies, it sits at the top or end, never hover-only, and names what AI did and what the named person checked. Record the named editor who takes editorial responsibility; human review with editorial responsibility exempts text from the EU AI Act Article 50 label. AI-generated images keep their IPTC or C2PA provenance metadata and any platform label. [S55; S61; S1]
4. Strip the bracketed evidence IDs; convert sources to links or a source list.
4a. Label and number exhibits as B5 rule 10 sets out. Use real img elements or inline SVG with a title, descriptive filenames, and a representative preferred image. Keep IPTC and C2PA metadata through export and CMS processing, and leave platform AI labels in place when syndicating. Render all disclosure-component content in the page and add a print stylesheet that expands every panel. [S108; S118; S119; S121; S107]
5. Add structured data matching the genre (Article, NewsArticle, Review, HowTo, FAQPage) only where the page content supports it.
5a. Run the rigor-talk and engine-vocabulary scan from Evidence rules 6 on the final text, title, description and alt text. Any hit returns the piece to B6.
6. Write the gate packet for final sign-off: the draft, the claim table, the meaning diff, the panel scores, and anything still open. Carry reconfirm-by dates into the publish record.
