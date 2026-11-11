from pathlib import Path
import json,random,re,hashlib
p=Path('/tmp/writing-integrity-evaluation');cases=json.loads((p/'rubric.json').read_text());rng=random.Random(20261022)
pairs=[];key={};checks=[]
for rep in ['one','two']:
 outputs={c:{x['id']:x['output'] for x in json.loads((p/'outputs'/f'{c}-{rep}.json').read_text())} for c in ['cedar','amber']}
 assert all(set(x)=={c['id'] for c in cases} for x in outputs.values())
 for c in cases:
  pair=f'P{len(pairs)+1:02}';order=['cedar','amber'];rng.shuffle(order)
  pairdata={'pair_id':pair,'case_id':c['id'],'task':c['task'],'criteria':c['criteria']}
  key[pair]={'case_id':c['id'],'replicate':rep}
  for label,condition in zip(['A','B'],order):
   txt=outputs[condition][c['id']];pairdata[label]=txt;key[pair][label]=condition
   n=len(txt.split());result={'pair_id':pair,'label':label,'case_id':c['id'],'words':n,'failures':[]}
   cfg=c['checks']
   for lim,op in [('word_min',lambda n,v:n<v),('word_max',lambda n,v:n>v)]:
    if lim in cfg and op(n,cfg[lim]):result['failures'].append(f'{lim} {cfg[lim]}; observed {n}')
   for literal in cfg.get('required',[]):
    if literal not in txt:result['failures'].append('Required exact text absent: '+literal)
   if 'json_preserve' in cfg:
    clean=re.sub(r'^```(?:json)?\s*|\s*```$','',txt.strip())
    try:
     d=json.loads(clean)
     for k,v in cfg['json_preserve'].items():
      if d.get(k)!=v:result['failures'].append('Protected JSON field changed: '+k)
     if set(d)!=set(cfg['json_preserve'])|{'helper'}:result['failures'].append('JSON keys changed')
    except Exception as e:result['failures'].append('Invalid JSON')
   checks.append(result)
  pairs.append(pairdata)
rng.shuffle(pairs)
(p/'judging/pairs.json').write_text(json.dumps(pairs,ensure_ascii=False,indent=2))
(p/'judging/deterministic-checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
(p/'blind-key.json').write_text(json.dumps(key,indent=2))
hashes={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['conditions','outputs'] for f in (p/folder).rglob('*') if f.is_file()}
for name in ['cases.json','rubric.json','protocol.json','candidate.diff','judging/pairs.json']:hashes[name]=hashlib.sha256((p/name).read_bytes()).hexdigest()
(p/'frozen-input-hashes.json').write_text(json.dumps(hashes,indent=2))
print(json.dumps({'pairs':len(pairs),'outputs':len(checks),'constraint_failures':[x for x in checks if x['failures']]},ensure_ascii=False))
