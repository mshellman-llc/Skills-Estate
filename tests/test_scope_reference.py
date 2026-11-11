import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from portable import assemble
class Markup(HTMLParser):
 def __init__(self):super().__init__();self.tags=[];self.text=[]
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_data(self,d):self.text.append(d)
class ScopeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name);self.pkg=self.base/'scope-reference';assemble(ROOT,'scope-reference',self.pkg,[])
  self.source=json.loads((self.pkg/'examples/comparison-source.json').read_text());self.plan=json.loads((self.pkg/'examples/comparison-plan.json').read_text());self.n=0
 def build(self,source=None,plan=None,extra=(),name=None):
  self.n+=1;attempt=self.base/str(self.n);attempt.mkdir();a=attempt/'source.json';b=attempt/'plan.json';a.write_text(json.dumps(self.source if source is None else source));b.write_text(json.dumps(self.plan if plan is None else plan));out=self.base/name if name else attempt/'scope.html'
  p=subprocess.run([sys.executable,str(self.pkg/'scripts/build_scope.py'),str(a),str(b),str(out),*extra],capture_output=True,text=True,cwd=self.base);(attempt/'result.json').write_text(json.dumps({'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2));return p,out
 def test_packaged_comparison_ties_out(self):
  p,out=self.build();self.assertEqual(p.returncode,0,p.stderr);doc=Markup();doc.feed(out.read_text())
  self.assertEqual(sum('data-item' in a for t,a in doc.tags),8);self.assertEqual(sum('data-snapshot' in a for t,a in doc.tags),6)
  self.assertIn('USD 34,950.25',doc.text);self.assertNotIn('999,999',out.read_text())
  for item in self.plan['matrix']:self.assertIn(item['name'],doc.text);self.assertIn(item['description'],doc.text)
  receipt=json.loads(out.with_suffix('.reconciliation.json').read_text());self.assertEqual(receipt['counts']['Q-DEMO-001'],{'in':4,'optional':2,'available':1,'out':1})
 def test_single_preserves_deselected_work(self):
  s=json.loads((self.pkg/'examples/single-source.json').read_text());p=json.loads((self.pkg/'examples/single-plan.json').read_text())
  result,out=self.build(s,p);self.assertEqual(result.returncode,0,result.stderr);doc=Markup();doc.feed(out.read_text());self.assertIn('Available',doc.text);self.assertIn('Operational alerts',doc.text);self.assertIn('Optional',doc.text)
  self.assertEqual(json.loads(out.with_suffix('.reconciliation.json').read_text())['mode'],'single-option')
 def test_corruption_prevents_output(self):
  for kind in ('hours','state','name','missing','extra','revenue','weeks','staff-hours','currency','active-snapshot','description','rounding'):
   p=copy.deepcopy(self.plan)
   if kind=='hours':p['matrix'][0]['cells']['Q-DEMO-001']['hours']=25
   elif kind=='state':p['matrix'][0]['cells']['Q-DEMO-001']['state']='out'
   elif kind=='name':p['matrix'][0]['name']='Invented item'
   elif kind=='missing':p['matrix'].pop()
   elif kind=='extra':p['matrix'].append(copy.deepcopy(p['matrix'][0]))
   elif kind in ('revenue','weeks','currency'):p['options'][0]['snapshots'][0][kind]='CAD' if kind=='currency' else 999
   elif kind=='staff-hours':p['options'][0]['snapshots'][0]['hours']=999
   elif kind=='active-snapshot':p['options'][0]['snapshots']=p['options'][0]['snapshots'][1:]
   elif kind=='rounding':p['rounding']=True
   else:p['matrix'][0]['description_basis']['quote_id']='missing'
   result,out=self.build(plan=p);self.assertEqual(result.returncode,2,kind);self.assertFalse(out.exists(),kind)
 def test_bad_source_rejected(self):
  for kind in ('duplicate','unknown-active','nonfinite','negative','optional','identity','timestamp'):
   s=copy.deepcopy(self.source)
   if kind=='duplicate':s['quotes'][0]['full_items'].append(copy.deepcopy(s['quotes'][0]['full_items'][0]))
   elif kind=='unknown-active':s['quotes'][0]['active_item_ids'].append('missing')
   elif kind=='nonfinite':s['quotes'][0]['full_items'][0]['hours']=float('nan')
   elif kind=='negative':s['quotes'][0]['snapshots'][0]['revenue']=-1
   elif kind=='optional':s['quotes'][0]['full_items'][0]['optional']='false'
   elif kind=='identity':s['quotes'][1]['full_items'][0]['name']='Different item'
   else:s['captured_at']='2026-10-21'
   result,out=self.build(source=s);self.assertEqual(result.returncode,2,kind);self.assertFalse(out.exists(),kind)
 def test_optional_flag_takes_precedence_over_active_membership(self):
  s=copy.deepcopy(self.source);s['quotes'][0]['active_item_ids'].append('training')
  result,out=self.build(source=s);self.assertEqual(result.returncode,0,result.stderr)
  self.assertEqual(json.loads(out.with_suffix('.reconciliation.json').read_text())['counts']['Q-DEMO-001']['optional'],2)
 def test_rounded_price_retains_exact_amount(self):
  p=copy.deepcopy(self.plan);p['rounding']=1000;result,out=self.build(plan=p);self.assertEqual(result.returncode,0,result.stderr);self.assertIn('About USD 35,000',out.read_text());self.assertIn('Exact quote: USD 34,950.25',out.read_text())
 def test_escape_authored_markup(self):
  p=copy.deepcopy(self.plan);p['intro']='<script>alert(1)</script>';result,out=self.build(plan=p);self.assertEqual(result.returncode,0,result.stderr);doc=Markup();doc.feed(out.read_text());self.assertFalse(any(t=='script' for t,a in doc.tags));self.assertIn(p['intro'],doc.text)
 def test_missing_profile_and_existing_output_preserved(self):
  result,out=self.build(extra=['--profile',str(self.base/'absent.md')]);self.assertEqual(result.returncode,2);self.assertFalse(out.exists())
  (self.base/'keep.html').write_text('keep');result,out=self.build(name='keep.html');self.assertEqual(result.returncode,2);self.assertEqual(out.read_text(),'keep')
 def test_alternate_profile_changes_identity(self):
  raw=(ROOT/'policies/brand.md').read_text();s=raw.index('```json\n')+8;e=raw.index('\n```',s);profile=json.loads(raw[s:e]);profile['colors']['accent']='#704226';profile['type']['headings']='Georgia, serif';path=self.base/'brand.md';path.write_text('```json\n'+json.dumps(profile)+'\n```')
  result,out=self.build(extra=['--profile',str(path)]);self.assertEqual(result.returncode,0,result.stderr);self.assertIn('--brand-accent:#704226',out.read_text());self.assertIn('--brand-font-headings:Georgia, serif',out.read_text())
 def test_legacy_normalizer_does_not_hide_collisions(self):
  command='from scope_reference_validate import validate; a={"A-B":{"hours":1,"states":{"x":"in"}},"AB":{"hours":1,"states":{"x":"in"}}}; assert not validate(a,a)[0]'
  result=subprocess.run([sys.executable,'-c',command],cwd=self.pkg/'scripts',capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)
if __name__=='__main__':unittest.main()
