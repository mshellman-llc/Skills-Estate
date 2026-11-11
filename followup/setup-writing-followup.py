from pathlib import Path
import json, shutil, hashlib
root=Path('/tmp/writing-integrity-followup'); root.mkdir(exist_ok=False)
old=Path('/Volumes/BeastMode/40-skills/work/writing-integrity-evaluation')
for name,src in [('maple','cedar'),('birch','amber')]:shutil.copytree(old/'conditions'/src,root/'conditions'/name)
(root/'outputs').mkdir(); (root/'judging').mkdir()
prior=Path('/Volumes/BeastMode/Codex/2026-10-22/task-3/review-candidate')
data=json.loads((prior/'meridian-journey-data.json').read_text())
personas=data['personas'][:2]
parts=['# Meridian personas and user journeys','The proposed Meridian experience includes developing the firm’s methods and offerings, researching organizations and maintaining account knowledge. These activities continue whether or not a client engagement exists. The journeys also show how that knowledge informs a potential engagement and how delivery findings update it.']
for p in personas:
 parts+=['## '+p['name'],p['context'],p['job'],'Design proposal: '+p['decision'],'Validation: '+p['validation']]
 for s in p['steps']:
  parts+=['### '+s['name'],'Goal: '+s['goal'],'Proposed: '+s['proposed'],'Decision: '+s['decision'],'Handoff: '+s['handoff'],'Recovery: '+s['recovery']]
draft='\n\n'.join(parts)
charter=Path('/Volumes/BeastMode/30-projects/meridian/context/product-framework/docs/01-project-charter.md')
charter_text=charter.read_text()
baseline=Path('/Volumes/BeastMode/30-projects/meridian/context/product-framework/rebuild-spec/00-decisions-and-sources.md')
c18=next(line for line in baseline.read_text().splitlines() if line.startswith('| C18 |'))
sources={'meridian_draft':'Extracted verbatim from existing review-candidate opening and first two persona records; layout reduced to text. Proposed fields used; stale current-behavior claims excluded.','charter_path':str(charter),'charter_sha256':hashlib.sha256(charter.read_bytes()).hexdigest(),'direction_path':str(baseline),'direction_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'direction_excerpt':c18,'other_cases':'New synthetic editorial fixtures; not user research or actual client records.'}
cases=[{
'id':'F01','category':'Meridian review correction','origin':'Actual artifact excerpt and actual user complaint, replayed with current product direction. Skill examples may already contain this known failure.',
'task':'''Please revise this review text for Meridian.

The earlier headline was “Understand the firm and the account before deciding there is work.” I responded: “uh what the fuck does ‘Understand the firm and the account before deciding there is work.’ actually mean”. The assistant explained that research and knowledge-building are already work and that it meant a potential client engagement. I then said “still pretty trash”. The replacement opening below also did not work for me.

Current project source:
'''+charter_text.split('## Confirmed product direction')[0]+ '\nLatest recorded direction:\n'+c18+'''

The roles and journeys below are proposals, not interview findings. The active product is a local interactive walkthrough: agent responses are simulated and saved work lives in the browser. This task edits the review text only.

Review text:
'''+draft,
'criteria':[
 {'tag':'reader_purpose','question':'Does the revised opening give the intended audience a useful product purpose, rather than describe the review contents or rehearse the earlier work/engagement confusion?','failure':'An opening primarily organized around what the experience/journeys include or repeated assurances about no engagement.'},
 {'tag':'fidelity','question':'Does it preserve research, shared expertise, account understanding, potential engagements and delivery learning without turning them into a sales-only funnel or a mandatory sequence?','failure':'Omitted material product purpose, added unsupported production claims or invented user research.'},
 {'tag':'scope','question':'Do substantive proposed persona decisions, handoffs and recoveries survive unless a supported correction requires changing them?','failure':'A copy correction replaces the journeys with a generic feature list or invents new system behavior.'},
 {'tag':'current_direction','question':'Does it respect the latest functional terminology and flexible workspace context?','failure':'Treats firm or a single consulting business model as a required product structure despite C18.'}
 ]},
{'id':'F02','category':'Sponsor recommendation from a working proposal','origin':'Synthetic, new domain and longer mixed-purpose source.',
'task':'''Our sponsor needs a short recommendation for tomorrow's planning meeting. Write it from these working notes.

The archive team has 18,000 scanned inspection reports. A search upgrade would let analysts find the reports by equipment number and inspection date. The notes below came from the planning document and the last technical review.

Option A keeps the current archive and adds a searchable index. Proposed fixed fee: $24,000. Estimated delivery: four weeks after written approval and access to the archive export. Those two prerequisites have not been completed. The scope includes indexing the equipment number and date already present in document metadata. It excludes extracting missing fields from scans and correcting inaccurate metadata. The archive remains the source of record. The team could use the upgrade during the November review cycle if those prerequisites arrive in time; no completion date has been promised.

Option B replaces the archive with a new document system. Proposed implementation fee: $78,000, excluding the new system's annual subscription, which has not been quoted. Estimated implementation: twelve weeks after the same prerequisites. This option adds retention workflows, reviewer assignments and version comparison. The analysts have not requested these capabilities for the November review cycle. Migration of historical annotations is not included in that estimate. Legal has not assessed retention requirements for the new system.

In a sample of 120 reports, 97 had both required metadata fields. We do not know whether that sample represents the entire archive. Analysts currently search folder names and ask colleagues where reports were saved. No baseline for search time has been measured. The sponsor's priority this quarter is finding existing records during the review cycle, rather than replacing the archive. They can consider a separate metadata cleanup after seeing the missing-field report. An index would not make a report with missing metadata searchable by that missing field.

Review administration: the technical review lasted 55 minutes. Nina facilitated. Arjun took notes. The sample folder contains 120 reports in eight subfolders. The planning document is version 0.6. It was exported at 17:42 on Tuesday. The appendix lists 63 document naming conventions. The team intends to discuss the proposal at 09:30 tomorrow. Finance has requested a recommendation, not a purchase order. The sponsor has not approved either option.
''',
'criteria':[
 {'tag':'reader_purpose','question':'Does it make a concise decision recommendation around this quarter’s search need, rather than reproducing source administration or an indiscriminate checklist?','failure':'No clear recommendation or incidental meeting/file details swamp the decision.'},
 {'tag':'fidelity','question':'Does the retained recommendation preserve proposed price, estimate, prerequisites and the material missing-metadata limitation?','failure':'Turns estimate into deadline, implies approval, guarantees all records searchable or omits a material prerequisite.'},
 {'tag':'selection','question':'Does it select the material option tradeoff and omit irrelevant source details?','failure':'Copies every figure/name to comply with preservation rules or erases a material cost/scope distinction.'},
 {'tag':'reader_purpose','question':'Are caveats included only where needed to interpret the recommended action?','failure':'Unmeasured search time becomes a prominent disclaimer despite making no measured time-saving claim.'}
 ]},
{'id':'F03','category':'Customer update from engineering notes','origin':'Synthetic new release, with behavior facts and internal context mixed together.',
'task':'''Write the product update for the in-app What's new page from these engineering notes.

Release: saved filters for the shipment table. Available now to paid-workspace users on the web app. Users can set a combination of status, destination and planned dispatch date, then choose Save filter and give it a name. Saved filters appear in that person's filter menu. Selecting one reapplies its saved values. A user can rename or delete their own saved filters. Saved filters are personal; there is no team-wide sharing in this release. They do not change anyone else's table or alter shipment records.

The existing table can still be filtered without saving. Dates in a saved filter are fixed calendar dates, not a rolling interval. A saved filter for 1–7 November continues to use those dates next week. The mobile app does not yet support saved filters. The web release completed at 14:20 yesterday. Feature flag sf_web_v2 is enabled for eligible workspaces. Eleven automated checks passed. Two internal testers used the feature on staging. There is no adoption study, no measured productivity improvement and no measured retention impact. No user has been interviewed about this release. Support will review questions after launch.

Implementation notes: saves are keyed by user ID and workspace ID. A uniqueness check prevents duplicate names within that person's workspace. Failed saves leave the active filter in place and show an error, so the person can retry. We have a separate engineering ticket for variable date ranges, but no release date. The initial ticket was called Shared Views even though the shipped feature is personal saved filters. The marketing draft “Your entire team now works in perfect sync” was rejected in review. There is no need for users to reload their browser to see the change.
''',
'criteria':[
 {'tag':'reader_purpose','question':'Does the update explain the new behavior and how to use it without importing internal measurements, test receipts, tickets or drafting history?','failure':'Copies no-adoption/no-interview disclaimers, feature-flag names, QA counts or the rejected marketing claim into the release copy.'},
 {'tag':'fidelity','question':'Does it preserve paid web availability, personal scope and fixed-date behavior where relevant to use?','failure':'Promises team sharing, mobile availability, rolling dates or measured outcomes.'},
 {'tag':'actionability','question':'Can a user understand what changed and how to save/use a filter?','failure':'Feature praise or a source-inventory list replaces useful instructions.'}
 ]},
{'id':'F04','category':'Correcting information already sent','origin':'Synthetic customer notice; checks that audience-relevant corrections survive.',
'task':'''Draft the email to the workshop registrants from these notes.

The workshop is on 12 November. The calendar invitation we emailed yesterday says Room 204 at North Hall. That room is wrong. The workshop is in Room 402 at North Hall, at the same 10:00–12:00 time. The corrected invitation is attached. The registration itself is valid and no one needs to register again. The entrance and building are unchanged. The meeting link in the invitation is unchanged for remote participants.

Operations notes: the room booking spreadsheet had 402 throughout. The calendar template had 204. We do not know who copied that value into the invite. The team has corrected the template and asked the venue coordinator to check the sign outside 402. The coordinator has not replied. No apology or correction has been sent to registrants yet. Twenty-eight people registered, including six remote participants. The organizer had considered cancelling when the room error was first noticed; that is no longer being considered. The workshop facilitator and agenda are unchanged.
''',
'criteria':[
 {'tag':'necessary_correction','question':'Does it clearly supersede yesterday’s wrong room and tell the affected recipients which invitation/room to use?','failure':'Hides the correction, leaves conflicting rooms unexplained or changes time/date.'},
 {'tag':'fidelity','question':'Does it retain relevant unchanged details and avoid inventing causes, blame or confirmed signage?','failure':'Invented attribution or operational confirmation.'},
 {'tag':'reader_purpose','question':'Does the email omit internal template history, cancellation discussion and registration counts that recipients do not need?','failure':'An internal incident report displaces the short actionable correction.'}
 ]},
{'id':'F05','category':'Light edit with voice and technical relationships','origin':'Synthetic internal handoff draft with one unsupported promotional passage.',
'task':'''Give this internal handoff note a light edit.

I know yesterday was a slog. Thank you for sticking with it. The import is finished, and the review file is in the shared folder. It has 8,460 rows. We have not checked the totals yet. Mira can send it to finance after that check.

The client retries a failed read up to three times because the provider sometimes returns a stale replica just after a write. It does not retry writes. Keep that distinction in the handoff: a timeout on a write still needs investigation before someone sends the request again. The new retry setting does not change the timeout value.

For tomorrow, I suggest we check the totals first, then spot-check the 37 records whose dates were converted from text. Those records are marked in the review file. The source dates remain in the adjacent column. I do not yet know whether the two records without an equipment ID are missing IDs in the source or were lost during the import; Jo is checking that now. Please leave those two records in the review file while we resolve it.

This pivotal milestone proves that our world-class process has eliminated the friction that held the organization back.

If you run out of time, leave me a note about where you stopped. We can pick it up together in the morning. No one needs to stay late to finish this tonight.
''',
'criteria':[
 {'tag':'voice','question':'Does it preserve the humane tone and useful general reassurance without adding invented deadlines or flattening the voice?','failure':'Deletes warmth solely for lacking specific facts or rewrites into a rigid audit/checklist.'},
 {'tag':'fidelity','question':'Does it preserve counts, distinct unresolved checks, read/write behavior and the finance-send condition?','failure':'Lost qualifiers, changed technical meaning or invented resolution.'},
 {'tag':'scope','question':'Is the edit proportional to a light edit, removing unsupported promotion while retaining effective causal relationships and useful structure?','failure':'Unnecessary wholesale rewrite, fragmented causal explanation, or unsupported promotional claim retained.'}
 ]}
]
for c in cases:
 (root/(c['id']+'.json')).write_text(json.dumps({k:c[k] for k in ['id','task']},ensure_ascii=False,indent=2)+'\n')
(root/'cases.json').write_text(json.dumps([{k:c[k] for k in ['id','task']} for c in cases],ensure_ascii=False,indent=2)+'\n')
(root/'rubric.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
(root/'source-provenance.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n')
protocol={'conditions':{'maple':'existing skill frozen from prior run','birch':'same proposed revision as prior run','willow':'no additional Writing Integrity skill loaded'},'cases':5,'replicates':2,'outputs':30,'design':'Six fresh writer agents with no parent conversation, one condition and five tasks per agent. Two blinded reviewers grade randomized triplets. Fixed rubric before generation. Shared model/platform instructions remain; no-skill is not an instruction-free model.','rating':{'pass':'Meets reader purpose and material constraints without an identified substantive defect','minor':'Usable but has a specific unnecessary addition, omission, or over-edit','fail':'Materially fails reader purpose, factual meaning, scope or requested action'},'reader_purpose_rule':'Factual but irrelevant qualifications and internal correction narrative count as defects even when short. Preserve corrections that recipients need. Score material behavior, not exact preferred wording.','limits':['Synthetic cases except actual Meridian artifact/correction replay','Meridian case is known and may overlap the skill examples','Same model family and shared system/developer instructions','Five cases batched per writer; not isolated per-case contexts','Two replicates diagnostic only','No timing or token-efficiency comparison','The no-skill condition is absence of the explicit skill, not removal of shared writing preferences']}
(root/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
(root/'frozen-input-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print('Prepared',root,'with',len(cases),'cases')
