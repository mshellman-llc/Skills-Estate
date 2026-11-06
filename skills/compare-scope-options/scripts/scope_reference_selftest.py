#!/usr/bin/env python3
"""Exercise both bundled inputs and a corrupted cell without external access."""
import copy
from pathlib import Path
from scope_reference_validate import load,reconcile
root=Path(__file__).resolve().parents[1]
for mode in ('comparison','single'):
 source=load(root/f'examples/{mode}-source.json');plan=load(root/f'examples/{mode}-plan.json')
 result=reconcile(source,plan);assert result['ok']
 assert result['counts']['Q-DEMO-001']['available']==1
 broken=copy.deepcopy(plan);broken['matrix'][0]['cells']['Q-DEMO-001']['hours']=999
 try:reconcile(source,broken)
 except ValueError:pass
 else:raise AssertionError('Changed hours accepted')
 print(mode+': valid input accepted; altered hours refused')
print('SELFTEST PASSED')
