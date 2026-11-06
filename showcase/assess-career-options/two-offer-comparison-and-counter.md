---
skill: assess-career-options
title: Comparing two architect offers and drafting a base-salary counter
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 4bd8a9469889eee41a03eb6f90e7ffe10879a96556796192538206db652571b0
---

## Request

I have two written offers and haven't decided between them. Compare them against my criteria in the profile, and draft a counter email and call script for Halden asking for £118,000 base. I'm not disclosing my current pay.

## Inputs

Run of the built `assess-career-options` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so.

#### offers.md

#### Offer A: Halden Freight Systems, Principal Platform Architect (written offer letter, 2 Nov 2026)

- Base £108,000. Posted range for the role: £100,000–£120,000 (job posting, accessed 28 Oct 2026).
- Target bonus 10% of base. Recruiter said payouts were 60–80% of target in the last three years (verbal).
- 20,000 options, strike £2.10. Last funding round valued shares at £4.00. Four-year vest, one-year cliff. Private company, no liquidity date.
- Signing bonus £5,000.
- Employer pension 6% of base.
- Hybrid, 2 office days a week in Manchester. No travel stated.
- Reports to VP Engineering.
- Letter says the role "owns reference architecture decisions for the freight platform (about 40 services)".
- Billability: not stated. Role is an internal platform team.
- Promotion: nothing in the letter. Recruiter said a level review "at about 12 months" (verbal).
- Impact: posting says the role leads the move off the legacy dispatch system. No target stated.

#### Offer B: Kestrel Data Consulting, Lead Solutions Architect (written offer letter, 4 Nov 2026)

- Base £102,000. Target bonus 15%. Attainment history not given.
- No equity. No signing bonus.
- Employer pension 4% of base.
- Remote with up to 30% client travel.
- Letter states 60% expected utilisation (billable time).
- Reports to Director of Delivery.
- Letter says the role "leads solution design on client engagements".
- Letter says: "eligible for consideration for Principal at the 12-month review." Review date is written; promotion is not promised.
- In interview the Director said the role would shape the firm's reference patterns (not in the letter).

#### profile.md

#### Candidate profile: Priya Anand

- Location: Manchester, UK. Currency GBP.
- Path: senior individual contributor (principal architect). No people management wanted.
- Compensation: minimum base £95,000; target base £110,000.
- Billability: at most 20% of time billable to clients. Exactly 20% passes.
- Scope history: current role is staff platform engineer. Sets architecture for 35 services across 4 teams, no budget, no direct reports. Target is wider technical decision authority.
- Matrix weights (out of 10): technical scope 3, decision authority 3, impact 2, sponsorship 1, advancement 1.
- Past pay: do not disclose.
- Writing: no confirmed style profile supplied.
- Offer deadline pressure: Halden asked for an answer by Friday 13 November 2026. Kestrel by Friday 20 November 2026.

## Output

Halden scores higher on your criteria and pays more cash. Kestrel fails your billability gate as written. I haven't picked for you; the decision is yours.

#### Gates

| Gate | Halden | Kestrel |
|---|---|---|
| Minimum base £95,000 | Pass (£108,000) | Pass (£102,000) |
| Target base £110,000 | £2,000 short | £8,000 short |
| Billability, at most 20% | Unresolved: the letter is silent | **Fail**: letter states 60% |
| Senior IC path | Pass | Partial: IC role, mostly client delivery |
| Scope vs your 35 services / 4 teams | About 40 services, similar size. Wider only if authority crosses team lines | Unresolved: authority is per engagement |

#### Money

Base is shown apart from the rest. Assumptions: flat base, bonus at 70% of target for both, options at the £4.00 round price against a £2.10 strike. Halden's 60–80% attainment is verbal. Kestrel gave no history, so 70% is a placeholder.

| | Halden yr 1 | Halden 4 yrs | Kestrel yr 1 | Kestrel 4 yrs |
|---|---|---|---|---|
| Base | 108,000 | 432,000 | 102,000 | 408,000 |
| Bonus | 7,560 | 30,240 | 10,710 | 42,840 |
| Signing | 5,000 | 5,000 | 0 | 0 |
| **Cash** | **120,560** | **467,240** | **112,710** | **450,840** |
| Pension (separate) | 6,480 | 25,920 | 4,080 | 16,320 |
| Options on paper (separate) | 9,500 | 38,000 | 0 | 0 |

Halden is ahead by £7,850 in cash in year one and £16,400 over four years. The options are in a private company with no liquidity date, so treat them as possibly worth nothing.

#### Progression matrix

Your weights: scope 3, authority 3, impact 2, sponsorship 1, advancement 1. Verified = 2, inferred = 1, unknown = 0.

| Criterion | Halden | Kestrel |
|---|---|---|
| Technical scope | Verified (letter) | Inferred |
| Decision authority | Verified (letter) | Inferred |
| Impact | Verified (posting: leads legacy dispatch migration, no target) | Verified (interview remark only) |
| Sponsorship | Inferred (VP Engineering) | Inferred (Director of Delivery) |
| Advancement | Unknown (12-month review is verbal) | Verified (letter names the review; no promotion promised) |
| **Score of 20** | **17** | **13** |
| Verified / inferred / unknown | 3 / 1 / 1 | 2 / 3 / 0 |

The score does not offset Kestrel's failed gate.

#### Strongest case for each

- **Halden:** your two heaviest criteria are in writing, base is £6,000 higher, cash leads in every period, and the role is an internal platform team.
- **Kestrel:** the only written review process, a 15% bonus target, fully remote, and a wider client mix.

#### Open questions

- **Halden:** the billable share, if any; whether authority reaches other teams; whether the 12-month review can go in the letter; the migration success target; the option agreement terms on leaving and exercise.
- **Kestrel:** whether 60% utilisation is fixed; whether the "reference patterns" remark can go in the letter; real bonus attainment; a travel cap.

#### Halden counter at £118,000 (draft; you send it)

£118,000 is £10,000 (9.3%) above the offer and inside Halden's posted £100,000–£120,000 range (job posting, accessed 28 Oct 2026). No web search was available, so that range is the only market evidence. Your past pay is not mentioned. Asks run in order: base, then the written 12-month review, then a line confirming no billable client work.

**Email**

Subject: Principal Platform Architect offer

Hello [recruiter name],

Thank you for the offer. I want to take the role, and the scope in the letter, owning reference architecture for the freight platform, is what I was looking for.

I'm asking for a base of £118,000. The posted range runs to £120,000, and the work in the letter, architecture decisions across about 40 services and the move off legacy dispatch, sits at the senior end of it.

Two things I would like in the letter as well. First, the 12-month level review you described, with its criteria written down. Second, a line confirming the role has no billable client delivery.

If we can agree on those, I can give you my answer before your Friday 13 November deadline.

Priya

**Call script**

- Open: "Thanks for the offer. I'd like to say yes, and I have three points to settle first."
- Base: "I'm looking for £118,000. The range you posted goes to £120,000 and this role owns the platform's architecture decisions. Can you get there?"
- Written terms: "I'd like the 12-month level review and its criteria in the letter, plus a line that the role has no billable client work."
- "This is our best offer": "I understand. Is the base the part that's fixed, or the total? If base is fixed, I'd want the level review in writing and a signing bonus that closes part of the gap."
- "The band is fixed": "Your posting runs to £120,000, so £118,000 is inside the band. Which part of the band does the role map to, and what would move it up?"
- "We need an answer by Friday": "Friday 13 November works if we settle the base and the written review by Wednesday. Can you get me a revised letter by then?"

#### Limits

- No spreadsheet tool was available, so the full tables and calculations are in the Markdown file below.
- The tracker and role work records were not supplied, so none were updated. Add a pointer to the file from each role folder. Statuses stay as they are until you say otherwise.
- No style profile was supplied. I checked the drafts by reading them; no scanner ran.

**Changed:** a new comparison file. **Verified:** every figure comes from the two offer letters, the posting and your profile. **Unchanged:** tracker rows and statuses. **Next action:** ask Halden whether the role has any billable work, then send the counter before Friday 13 November. Kestrel's deadline is Friday 20 November.

#### File

- `out/offer_comparison.md`: gates, base-apart year-one and four-year tables, matrix with counts, strongest cases, open questions, counter email and call script.

### File: offer_comparison.md

#### Offer comparison: Halden (A) and Kestrel (B)

Candidate: Priya Anand. Prepared 4 Nov 2026 from the two offer letters and the profile. Status of both roles unchanged until Priya says otherwise.

##### Gates

| Gate | Halden | Kestrel |
|---|---|---|
| Minimum base £95,000 | Pass (£108,000) | Pass (£102,000) |
| Target base £110,000 | Below by £2,000 | Below by £8,000 |
| Billability, at most 20% (20% passes) | Unresolved. Letter is silent; internal platform team does not prove zero | Fail. Letter states 60% |
| Senior IC path | Pass. Owns architecture decisions, no reports | Partial. IC role, but most time is client delivery |
| Scope against history (35 services, 4 teams) | Letter says about 40 services. Similar size; wider only if the authority reaches beyond the current team split | Unresolved. Authority is per engagement; firm-wide reach rests on an interview remark |
| Alignment flags | None raised | None raised |

##### Base, apart from everything else

| | Halden | Kestrel |
|---|---|---|
| Base | £108,000 | £102,000 |
| Employer pension | 6% = £6,480 a year | 4% = £4,080 a year |

##### Year one and four years

Assumptions: base flat for four years (no raises promised in either letter); bonus at 70% of target for both (Halden's 60–80% is a verbal figure; Kestrel gave no history, so 70% is a placeholder); options valued at the last round price of £4.00 against £2.10 strike, so £1.90 a share.

| Line | Halden year 1 | Halden 4 years | Kestrel year 1 | Kestrel 4 years |
|---|---|---|---|---|
| Base | 108,000 | 432,000 | 102,000 | 408,000 |
| Bonus (target 10% / 15%, at 70%) | 7,560 | 30,240 | 10,710 | 42,840 |
| Signing | 5,000 | 5,000 | 0 | 0 |
| **Cash total** | **120,560** | **467,240** | **112,710** | **450,840** |
| Pension (separate) | 6,480 | 25,920 | 4,080 | 16,320 |
| Options on paper (separate) | 9,500 (5,000 vested at cliff) | 38,000 | 0 | 0 |

Halden leads on cash by £7,850 in year one and £16,400 over four years. The options are private, have no liquidity date and could be worth zero. With the pension and options added, the four-year gap is £16,400 + £9,600 + £38,000 = £64,000 on paper; cash alone is the reliable figure.

Not supplied: relocation (none stated for either), other benefits differences beyond pension.

##### Progression matrix

Weights are Priya's (total 10). Verified = 2, inferred = 1, unknown = 0.

| Criterion (weight) | Halden | Kestrel |
|---|---|---|
| Technical scope (3) | Verified: letter, about 40 services | Inferred: letter covers engagement-level design only |
| Decision authority (3) | Verified: letter, "owns reference architecture decisions" | Inferred: "leads solution design on client engagements" |
| Impact (2) | Verified: posting says role leads the move off legacy dispatch (no target stated) | Verified: Director said in interview the role shapes reference patterns (not in letter) |
| Sponsorship (1) | Inferred: reports to VP Engineering | Inferred: reports to Director of Delivery |
| Advancement (1) | Unknown: 12-month review is verbal only | Verified: letter names a 12-month review and Principal consideration (no promise of promotion) |
| **Weighted score (of 20)** | **17** | **13** |
| Verified / inferred / unknown | 3 / 1 / 1 | 2 / 3 / 0 |

Halden's score comes from its letter on the two heaviest criteria. Kestrel's rests more on inference. The score does not offset Kestrel's failed billability gate; the gate stands on its own.

##### Strongest case for each

- **Halden:** the highest-weighted criteria are in writing, base is £6,000 higher, cash is higher in every period, and the role is an internal platform team on the IC path. Posted range tops out at £120,000, so £118,000 sits inside it.
- **Kestrel:** advancement is the only written review process, bonus target is higher (15%), the role is fully remote, and the client mix may give wider exposure than one platform.

##### Open questions

Halden
1. What share of time, if any, is billable or client-facing? (gate unresolved)
2. Does decision authority cover other teams' services, or only the platform team's?
3. Can the 12-month level review be put in the offer letter, with the criteria?
4. Which success target applies to the dispatch migration, and who judges it?
5. What do the option terms say on leaving, exercise window and tax treatment? Request the option agreement.

Kestrel
1. Is 60% utilisation fixed, and could it fall to 20% or below? As written the role fails the billability gate.
2. Can the interview remark about reference patterns go into the letter?
3. What attainment have staff in this role had on the 15% bonus?
4. Does remote work with 30% travel have a stated cap in the contract?

##### Halden counter (draft only; Priya sends or says it)

Number: £118,000 base, supplied by Priya. That is £10,000 (9.3%) above the offer and £2,000 under the top of the posted £100,000–£120,000 range (job posting, accessed 28 Oct 2026). Target bonus would rise to £11,800 and employer pension to £7,080. No past pay is disclosed. No web search was available; the only market evidence is Halden's own posted range.

Order of asks: base first, then a written 12-month level review, then written confirmation that the role carries no billable client obligation. Signing bonus is left alone unless Halden holds base.

###### Email

Subject: Principal Platform Architect offer

Hello [recruiter name],

Thank you for the offer. I want to take the role, and the scope in the letter, owning reference architecture for the freight platform, is what I was looking for.

I'm asking for a base of £118,000. The posted range runs to £120,000, and the work in the letter, architecture decisions across about 40 services and the move off legacy dispatch, sits at the senior end of it.

Two things I would like in the letter as well. First, the 12-month level review you described, with its criteria written down. Second, a line confirming the role has no billable client delivery.

If we can agree on those, I can give you my answer before your Friday 13 November deadline.

Priya

###### Call script

Open: "Thanks for the offer. I'd like to say yes, and I have three points to settle first."

1. Base: "I'm looking for £118,000. The range you posted goes to £120,000 and this role owns the platform's architecture decisions. Can you get there?"
2. Written terms: "I'd like the 12-month level review and its criteria in the letter, plus a line that the role has no billable client work."

If they say "this is our best offer": "I understand. Is the base the part that's fixed, or is it the total? If base is fixed, I'd want the level review in writing and a signing bonus that closes part of the gap."

If they say "the band is fixed": "Your posting runs to £120,000, so £118,000 is inside the band. Which part of the band does the role map to, and what would move it up?"

If they say "we need an answer by Friday": "Friday 13 November works if we settle the base and the written review by Wednesday. Can you get me a revised letter by then?"

Close: "Thank you. I'll wait for the revised letter."

##### Export and records

No spreadsheet tool was available, so this file holds the full tables and calculations. The tracker (`03_Tracker/`) and role work records were not supplied, so nothing was updated there; the Halden and Kestrel rows should link to this file. Status values `offer` or `closed` change only on Priya's word. No style profile was supplied; the drafts were checked by reading and no scanner ran.
