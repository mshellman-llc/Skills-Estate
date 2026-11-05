---
skill: skill-creation-walkthrough
title: Draft a new estate skill for customs hold responses
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: ee26692c205920fa87c71c04af6dcd814fc43606c2da4a7a1a74c154df3778a6
---

## Request

Our ops team keeps asking for help when a customs authority puts a hold on a shipment, and I want a proper skill for it in our estate checkout (~/src/Skills-Estate). My draft procedure and the current estate listing are attached; please create the draft skill, check it doesn't collide with what we already have, and tell me what still needs doing before it can be installed.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `skill-estate-sync` task package in its "create or repair an estate skill" mode. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### draft-procedure.md

#### Draft: customs hold response (Ops, Priya's team)

Who: import coordinators handling a hold notice from a customs authority.
Input: the hold notice text, the booking record (shipper, consignee, container ID, commodity, declared value), and the list of documents we hold.

Steps
1. Read the notice. Pull out: authority, reference number, hold type (documentary, inspection, valuation query, restricted goods), requested documents, response deadline.
2. Compare requested documents with the ones we hold. List what is present, missing, or inconsistent (for example declared value differs between invoice and booking).
3. If the commodity description looks mis-classified, flag it and suggest tariff-code-lookup. Do not change the classification ourselves.
4. Draft the reply to the broker: reference number, documents attached, documents still to be obtained and who holds them, a proposed deadline plan.
5. Draft a short internal note with storage-cost exposure per day if the container has a daily demurrage rate in the booking.
6. Never state a legal conclusion or promise release. Never invent a document number.

Output: broker reply draft, document gap table, internal note.
If the notice has no deadline or is unreadable: say so and ask for the original.
Example notice for testing: valuation query, ref HV-5521, invoice USD 18,400 vs booking USD 14,900, deadline 2026-11-10.

#### estate-listing.txt

Checkout: ~/src/Skills-Estate (Northgate Freight Services, fictional)
Steward: Priya Anand (ops tooling)   Date of listing: 2026-11-03

skills/ (name | description | status)
shipment-exception-triage | Classify a delayed, damaged or lost shipment from tracking events and route it to the right ops queue. Use when a shipment is late or flagged in the tracker. | released
carrier-claims-drafter | Draft a damage or loss claim to a carrier from the booking, proof of delivery and photos. | released
tariff-code-lookup | Suggest a tariff classification for a product description and cite the rule used. | released
customer-delay-notice | Write a customer-facing delay message from a confirmed cause and new ETA. | released
quality-gate | Shared control (runtime component). | released

config/plugin-bundles.json: plugin "estate-freight" v1.4.0 includes the first four skills above.
Hosts in use: claude-code, codex. No Knowledge Hub in this estate.
Connectors: none for customs systems. Staff read hold notices from PDF/email text pasted into chat.

Recent routing log (2026-10):
  "customs hold on container NGFU-204118, what do we send the broker?"  -> shipment-exception-triage (wrong: it only classified and queued)
  "authority wants commercial invoice and origin cert, draft the reply"  -> no skill loaded

## Output

### Draft skill: `customs-hold-response`

I wrote the draft as a new, separate skill, because none of your four existing skills owns it. It is a draft only. I couldn't run the scaffolder, and I haven't touched `~/src/Skills-Estate`, built anything or installed anything.

#### Collision decision: `separate`

| Closest skill | Why it isn't the owner |
| --- | --- |
| `shipment-exception-triage` | It classifies a shipment and routes it to a queue. It never reads an authority's document request. Your October log shows the container NGFU-204118 hold question landing there with nothing produced. |
| `tariff-code-lookup` | It is a hand-off target for step 3 (suspected mis-classification), not a merge candidate. |
| `carrier-claims-drafter`, `customer-delay-notice` | Different audience and different input (carrier or customer, not an authority). |

The job starts from an authority notice and ends at a broker-ready response, so its completion condition differs from triage. I did not make it a mode of triage. The retirement path in the intake allows folding it in later if it sees little use.

#### Final description

> Prepare the response to a customs authority hold notice: extract the notice terms, compare requested documents with the documents held, and draft the broker reply, a document gap table and an internal cost note. Use when staff paste a hold notice, ask what to send the broker for a held container, or need to answer a documentary, valuation, inspection or restricted-goods query. Also triggers on requests to reply to an authority's document request. Not for classifying a delayed or damaged shipment (shipment-exception-triage), carrier claims (carrier-claims-drafter), tariff codes (tariff-code-lookup) or customer delay messages (customer-delay-notice).

It runs to about 640 characters, under the 1,024 limit. It also covers the second failed routing in your log ("authority wants commercial invoice and origin cert, draft the reply"), which loaded no skill at all.

**Intended triggers:** a pasted hold notice, a question about what to send the broker, a documentary, valuation, inspection or restricted-goods query, a reply to a document request.
**Excluded:** delay or damage triage, carrier claims, classification, customer messages.

#### What I kept from your draft procedure

All six steps are preserved. I made three changes:
- The unreadable-notice rule now also covers a missing deadline.
- Unknown values are written as `[to be supplied]`, so the draft never invents a document number.
- Step 5 states "rate not in booking" when the booking has no demurrage rate, instead of estimating.

#### Resource plan

| File | Purpose |
| --- | --- |
| `SKILL.md` | The inputs, six-step procedure, three outputs and boundaries. It's short enough that no reference file is needed. |
| `skill.yaml` | Metadata: status `draft`, version 0.1.0, owner Priya Anand, runtimes `claude-code` and `codex`, no Knowledge Hub, no connectors. |
| `fixtures/governance.yaml` | The ten intake answers and the collision disposition. |

There is no script or template. Nothing in the procedure needs executable output.

#### Intake, with gaps

Answers 1–7 and 10 are filled in from your draft and the listing. Four fields are open:
- **Cost and efficiency:** `unknown`, with no receipt. Both stay that way until a dated run measures them.
- **Lifecycle approver:** `unknown`. Your inputs don't name one.
- **Review date:** `null`.
- **Customs-system submission:** recorded as unavailable on both hosts. The fallback is drafts only, with a statement that nothing was submitted.

#### Acceptance prompts and what I observed

I read the draft against these by hand. This is a reading of the instructions, not a run on either host, and it doesn't show how the host would route each prompt.

| Case | Prompt | Result by hand |
| --- | --- | --- |
| Positive | Your test notice: valuation query HV-5521, invoice USD 18,400 vs booking USD 14,900, deadline 2026-11-10 | The procedure yields a gap row "commercial invoice: inconsistent". The difference is USD 3,500, which is 23.5% of the booking value and 19.0% of the invoice value. The broker reply cites HV-5521 and a plan finishing before 10 November. The internal note says "rate not in booking", because your example has no demurrage rate. |
| Alternate | "Authority wants commercial invoice and origin cert, draft the reply" | The description's "document request" clause matches. With no notice text, step 1 asks for the original rather than drafting dates. |
| Negative | "Container NGFU-204118 is two weeks late, where does it go?" | The description names `shipment-exception-triage` as the owner, so it should stay there. |
| Failure | Notice with no deadline | Asks for the original notice; no dates drafted. |

**Not run:** host selection in Claude Code and Codex, the overlap-group routing check against the four neighbouring skills, and the isolated-package run.

#### Steps I did by hand

- **Scaffolder:** `scaffold_skill.py` writes the same three files and a creation receipt. I wrote the files directly to the structure of its templates. The equivalent command is below. There is no `fixtures/scaffold-receipt.json`, and no SHA-256 values were computed.
- **Writing check:** `writing_check.py` wasn't run. I did a reading pass of `SKILL.md` and the intake prose only.
- **`skill.yaml` triggers:** the scaffolder would copy the full description into `triggers`. I wrote a short pointer, so rerun the scaffolder, or replace it with the full description, before promotion.

```sh
python3 scripts/scaffold_skill.py customs-hold-response \
  --root ~/src/Skills-Estate --display-name "Customs hold response" \
  --description "<description above>" \
  --owner "Priya Anand" --category freight-operations \
  --runtime claude-code --runtime codex \
  --workflow /path/to/body-of-SKILL.md
```

Run it from the walkthrough module's directory. It refuses to overwrite an existing destination. The workflow file must be the body only, with no frontmatter and no `TODO`.

#### Remaining actions before installation

1. Copy `out/skills/customs-hold-response/` into the checkout, or run the scaffolder above. Register it in `config/plugin-bundles.json`, probably under `estate-freight`. That bump (1.4.0 to a new version) needs the release workflow's `plugin_version.py --record`. I haven't made it.
2. Name a lifecycle approver and a review date, then change the collision disposition and status from draft to candidate.
3. Run the host-selection tests on both hosts with the prompts above, plus an overlap-group check against `shipment-exception-triage`. If that skill still takes the hold question, narrow its description and name this skill as the owner.
4. Run `validate`, the changed-skill self-test, `build` and `bundle`. Install with the reviewed source hash only after review. Creating the draft doesn't authorise installation.
5. Have a coordinator try it on a real, redacted hold notice. Record cost and efficiency only from that dated run.

#### Files

- `out/skills/customs-hold-response/SKILL.md`: frontmatter with the description above, plus the inputs, six steps, three outputs and boundaries.
- `out/skills/customs-hold-response/skill.yaml`: draft metadata, with owner, runtimes and no dependencies.
- `out/skills/customs-hold-response/fixtures/governance.yaml`: the ten intake answers, with disposition `separate`, cost and efficiency `unknown`, and lifecycle approver `unknown`.
