from pathlib import Path
import json, random, hashlib
r=Path(__file__).resolve().parent
load=lambda p:json.loads((r/p).read_text())
cases=load('rubric.json')
outs={}
for cond in ['maple','birch','willow']:
 for rep in ['one','two']:
  a=load('outputs/'+cond+'-'+rep+'.json')
  assert len(a)==5 and {x['id'] for x in a}=={x['id'] for x in cases}
  assert all(isinstance(x['output'],str) and x['output'].strip() for x in a)
  outs[(cond,rep)]={x['id']:x['output'] for x in a}
rng=random.Random(2026102202); triplets=[]; key={}
for rep in ['one','two']:
 for case in cases:
  tid='G'+str(len(triplets)+1).zfill(2); order=['maple','birch','willow'];rng.shuffle(order)
  pair={'triplet_id':tid,'case_id':case['id'],'task':case['task'],'criteria':case['criteria']}
  k={'case_id':case['id'],'replicate':rep}
  for label,cond in zip(['A','B','C'],order):pair[label]=outs[(cond,rep)][case['id']];k[label]=cond
  triplets.append(pair);key[tid]=k
rng.shuffle(triplets)
(r/'judging/triplets.json').write_text(json.dumps(triplets,ensure_ascii=False,indent=2)+'\n')
(r/'blind-key.json').write_text(json.dumps(key,indent=2)+'\n')
hashes=load('frozen-input-hashes.json')
assert all(hashlib.sha256((r/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
(r/'generation-hashes.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in list((r/'outputs').glob('*.json'))+[r/'judging/triplets.json']},indent=2)+'\n')
print('Prepared 10 blinded triplets, 30 outputs; frozen inputs unchanged.')
