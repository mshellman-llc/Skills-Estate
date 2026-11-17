#!/usr/bin/env python3
"""Exercise the bundled inputs and corrupted cells without external access."""
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
source=load(root/'examples/hours-only-source.json');plan=load(root/'examples/hours-only-plan.json')
result=reconcile(source,plan);assert result['pricing']=='unpriced' and result['unestimated']['Q-HOURS-002']==1
broken=copy.deepcopy(plan);cell=broken['matrix'][-1]['cells']['Q-HOURS-002'];cell.pop('status');cell['hours']=0
try:reconcile(source,broken)
except ValueError:pass
else:raise AssertionError('Zero hours accepted for unestimated work')
print('hours-only: unpriced input accepted; zero for unestimated work refused')
print('SELFTEST PASSED')
