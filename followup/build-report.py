from pathlib import Path
import json, hashlib, html, re, collections
R=Path(__file__).resolve().parent
OLD=Path('/Volumes/BeastMode/40-skills/work/writing-integrity-evaluation')
def load(p):return json.loads((R/p).read_text())
def e(v):return html.escape(str(v))
def paras(v):return ''.join('<p>'+e(x).replace('\n','<br>')+'</p>' for x in v.split('\n\n'))
cases=load('rubric.json'); key=load('blind-key.json'); protocol=load('protocol.json')
outputs={n:{x['id']:x['output'] for x in load('outputs/'+n+'.json')} for n in ['maple-one','maple-two','birch-one','birch-two','willow-one','willow-two']}
reviews={n:{x['triplet_id']:x for x in load('judging/reviewer-'+n+'.json')} for n in ['one','two']}
for hf in ['frozen-input-hashes.json','generation-hashes.json']:
 assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in load(hf).items())
counts={}; preferences={}; disagreements=[]
for name,rev in reviews.items():
 assert len(rev)==10 and set(rev)==set(key)
 count={c:collections.Counter() for c in ['maple','birch','willow']};rank=collections.Counter()
 for tid,row in rev.items():
  k=key[tid]
  assert sorted(l for group in row['ranking'] for l in group)==['A','B','C']
  for l in ['A','B','C']:
   assert row[l]['rating'] in ['pass','minor','fail']
   count[k[l]][row[l]['rating']]+=1
   for finding in row[l]['findings']:assert finding['quote'] in outputs[k[l]+'-'+k['replicate']][k['case_id']]
  idx={k[l]:i for i,g in enumerate(row['ranking']) for l in g}
  rank['proposed_preferred' if idx['birch']<idx['maple'] else 'existing_preferred' if idx['birch']>idx['maple'] else 'tie']+=1
 counts[name]={c:dict(v) for c,v in count.items()};preferences[name]=dict(rank)
for tid,k in key.items():
 for l in ['A','B','C']:
  if reviews['one'][tid][l]['rating']!=reviews['two'][tid][l]['rating']:
   disagreements.append({'case':k['case_id'],'replicate':k['replicate'],'condition':k[l],'one':reviews['one'][tid][l]['rating'],'two':reviews['two'][tid][l]['rating']})
summary={'cases':5,'outputs':30,'counts':counts,'proposed_vs_existing':preferences,'rating_disagreements':disagreements,'hashes_verified':True,'quoted_findings_verified':True,'installed_changes':False}
(R/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
old=(OLD/'writing-integrity-comparison.html').read_text()
css=re.search(r'<style>(.*?)</style>',old,re.S)[1]
css+='\n.casegrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.casegrid .sample{min-width:0}.casegrid .sample p{font-size:14px}.grade{font-weight:600;color:var(--teal)}.finding{padding:12px;background:var(--sand)}#initial{margin-top:48px} @media(max-width:1000px){.casegrid{grid-template-columns:1fr}} @media print{.casegrid{grid-template-columns:1fr}.casegrid .sample p{font-size:11px}}'
body='''<main><header class="result"><div class="eyebrow">Writing Integrity · focused follow-up · 22 October 2026</div><h1>The revision helped some edits but regressed on Meridian.</h1><p class="lead">Both blinded reviewers preferred the proposed revision in four of ten comparisons with the existing skill. They preferred the existing skill in one and tied five. The proposed revision repeated the Meridian opening problem in one run; the existing skill avoided it in both.</p><p>The broad revision remains staged. These mixed results do not justify replacing the existing skill, which already includes the standing reader-purpose preference.</p><p class="meta">5 tasks · 2 runs per condition · 30 responses · existing skill, proposed revision and no additional writing skill</p></header><nav aria-label="Follow-up sections"><a href="#comparison">Results</a><a href="#examples">What changed</a><a href="#method">Method and limits</a><a href="#responses">All responses</a><a href="#initial">Initial comparison</a></nav>
<section id="comparison"><h2>The revision had fewer minor defects, with a regression on the motivating case</h2><table><thead><tr><th scope="col">Reviewer rating</th><th scope="col">Existing</th><th scope="col">Proposed</th><th scope="col">No added skill</th></tr></thead><tbody>'''
for rev,label in [('one','Reviewer one'),('two','Reviewer two')]:
 for rating in ['pass','minor','fail']:
  body+='<tr><th scope="row">'+label+' · '+rating+'</th>'+''.join('<td>'+str(counts[rev][c].get(rating,0))+'</td>' for c in ['maple','birch','willow'])+'</tr>'
body+='''</tbody></table><p>Each condition generated ten responses. A minor rating means the response was usable but contained a specific avoidable addition, omission or over-edit. No response received a fail rating. These are judgments of this sample, not estimates of everyday reliability.</p><p>The reviewers agreed on 29 of 30 response ratings. They disagreed about whether the first no-skill Meridian rewrite lost the distinct option to pause guidance. Both sets of findings are retained below.</p></section>
<section id="examples"><h2>The Meridian regression was the same kind of framing you rejected</h2><div class="cols"><div><h3>Existing skill · first run</h3><blockquote>'''+paras(outputs['maple-one']['F01'].split('\n\n')[1])+'''</blockquote><p class="review">Both reviewers: pass. The opening explains the intended product use and carries knowledge into later decisions.</p></div><div><h3>Proposed revision · first run</h3><blockquote>'''+paras(outputs['birch-one']['F01'].split('\n\n')[1])+'''</blockquote><p class="review">Both reviewers: minor. The second sentence describes what the journeys contain, bringing document framing back into the opening.</p></div></div>
<h2>All three conditions retained an irrelevant measurement caveat</h2><p>Every sponsor recommendation added a sentence such as “Search-time savings have not been measured.” None had claimed a measured time saving. Both reviewers marked this as unnecessary in all six responses.</p><p>The existing skill and no-skill responses also repeated “this recommendation is not a purchase order.” The proposed revision omitted that administrative disclaimer in both runs, which is why reviewers preferred it on this task. It still retained the measurement caveat.</p>
<h2>The product update exposed a separate meaning problem</h2><p>The source said saved filter names must be unique for a particular person within a workspace. Both existing-skill responses shortened that to uniqueness “within your workspace,” which can imply a shared namespace. Both reviewers flagged the ambiguity. The proposed and no-skill responses omitted the naming restriction and passed.</p><p>All six product updates omitted internal measurement, test-count and feature-flag notes. All six correction emails kept the wrong-room correction recipients needed. All six light edits preserved warmth, technical causality and unresolved checks while removing unsupported promotion.</p>
<div class="note"><h2>Keep the current skill; do not install this broad rewrite</h2><p>The proposed revision improved some details but did not consistently prevent the original failure. The no-skill condition also showed that several successful behaviors occurred without explicitly loading Writing Integrity. The experiment does not isolate a particular skill rule as the cause of the remaining defects.</p><p>The demonstrated issue is selective use of source material: a fact can constrain what may be claimed without belonging in the finished copy. That distinction needs to be applied when reviewing the actual deliverable. Adding more universal prose rules is not supported by this result.</p><p>The installed skill, shared instructions and live Meridian files were not changed during this follow-up. The generated Meridian rewrites are test outputs.</p></div></section>
<section id="method"><h2>The test used source material with less editorial coaching</h2><p>Five tasks replaced the short first-round prompts: a real Meridian review correction, a sponsor recommendation, an in-app product update, a correction email and a light edit. The last four are synthetic fixtures, not client records. Writers received the user request and source notes, without the grading criteria or an intended answer.</p><p>The Meridian fixture extracts the actual rejected opening and the first two proposed persona journeys. It includes the real earlier complaint and current project direction, including the newer terminology decision. Layout was reduced to text, and stale implementation descriptions were excluded. It is a replay with current context, not a byte-for-byte recreation of the original conversation.</p><p>Six fresh writer agents each handled five tasks, with two agents per condition. The existing and candidate skill snapshots were identical to those used in the first round. Two fresh reviewers saw randomized A/B/C triplets and criteria fixed before generation. They could tie outputs and were required to quote each defect. All quoted findings were checked against the actual responses.</p><ul><li>“No added skill” means Writing Integrity was not explicitly loaded. The common model, platform instructions and writing preferences remained in effect.</li><li>All agents used the same model family. The two reviewers are separate model judgments, not human validation.</li><li>Tasks were batched five per writer, not run in thirty isolated contexts. Two repeats are too few for reliability estimates.</li><li>The author of the revision also prepared the fixtures and criteria. Blinding reduces knowledge of condition identity but does not remove that design bias.</li><li>Meridian is a known case and may overlap examples in the skill. The other four fixtures were new.</li><li>The rubric was stricter about irrelevant qualifications than the first round. Scores from the two rounds should not be pooled or compared as a trend.</li></ul><p>All frozen inputs and outputs retained their recorded hashes. Canonical, Codex and Claude installed skill files remained unchanged.</p></section>
<section id="responses"><h2>Inspect the source, responses and findings</h2><p>Each case contains the original task, criteria and two runs for all three conditions. Open a response to read its complete text and both reviewers’ findings. Original output formatting is represented as text; wording is unchanged.</p>'''
names={'maple':'Existing skill','birch':'Proposed revision','willow':'No added skill'}
for case in cases:
 cid=case['id'];body+=f'<details id="{cid}"><summary>{e(case["category"])} <small>· {cid}</small></summary><p class="meta">{e(case["origin"])}</p><details><summary>Task and source material</summary><div class="task">{paras(case["task"])}</div></details><details><summary>Criteria fixed before generation</summary><ul>'
 for cr in case['criteria']:body+='<li>'+e(cr['question'])+'<br><small>'+e(cr['failure'])+'</small></li>'
 body+='</ul></details>'
 for rep,num in [('one',1),('two',2)]:
  tid=next(t for t,k in key.items() if k['case_id']==cid and k['replicate']==rep)
  body+=f'<h3>Run {num}</h3><div class="casegrid">'
  for cond,label in names.items():
   l=next(l for l in ['A','B','C'] if key[tid][l]==cond)
   a,b=reviews['one'][tid][l],reviews['two'][tid][l]
   body+=f'<div class="sample"><h4>{label}</h4><p class="grade">{e(a["rating"])} / {e(b["rating"])} <small>· reviewers 1 / 2</small></p><details><summary>Read response</summary>{paras(outputs[cond+"-"+rep][cid])}</details>'
   for rev,rnum in [('one',1),('two',2)]:
    row=reviews[rev][tid][l];body+=f'<p class="review">Reviewer {rnum}: {e(row["reason"])}</p>'
    for f in row['findings']:body+='<div class="finding"><blockquote>'+paras(f['quote'])+'</blockquote><p class="review">'+e(f['effect'])+'</p></div>'
   body+='</div>'
  body+='</div><details><summary>Comparison reasoning</summary>'
  for rev,rnum in [('one',1),('two',2)]:body+=f'<p>Reviewer {rnum}: {e(reviews[rev][tid]["ranking_reason"])}</p>'
  body+='</details>'
 body+='</details>'
body+='</section>'
prior=re.search(r'<main>(.*)</main>',old,re.S)[1].replace('<h1>','<h2>').replace('</h1>','</h2>')
body+='<details id="initial"><summary>Initial comparison: 18 tasks, 72 responses</summary>'+prior+'</details>'
body+='''<footer><p class="meta">Evidence: followup/results.json · protocol.json · source-provenance.json · rubric.json · outputs/*.json · judging/reviewer-one.json · judging/reviewer-two.json · blind-key.json · frozen-input-hashes.json · generation-hashes.json</p><p class="meta">The evidence archive includes both rounds and the exact candidate diff. Browser screenshots are retained locally for inspection and excluded from the Library archive.</p></footer></main>'''
(R/'writing-integrity-comparison.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Writing Integrity — focused follow-up</title><style>'+css+'</style></head><body>'+body+'</body></html>')
manifest={'manifestVersion':'1.0','artifactId':'writing-integrity-followup','decisionJob':'Compare current, candidate and no-skill conditions','requiredPhrases':['The revision helped some edits but regressed on Meridian.','The reviewers agreed on 29 of 30 response ratings.','Keep the current skill; do not install this broad rewrite','The generated Meridian rewrites are test outputs.'],'forbiddenPhrases':[],'requiredEvidenceReferences':['source-provenance.json','generation-hashes.json'],'protectedClaims':[],'requiredSelectors':['main','h1','#responses','#method'],'requiredViews':['desktop','narrow','expanded comparisons','print']}
(R/'parity-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(summary,indent=2))
