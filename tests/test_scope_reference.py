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
from test_capabilities import integration
class Markup(HTMLParser):
 def __init__(self):super().__init__();self.tags=[];self.text=[]
 def handle_starttag(self,t,a):self.tags.append((t,dict(a)))
 def handle_data(self,d):self.text.append(d)
class ScopeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name);self.pkg=self.base/'compare-scope-options';assemble(ROOT,'compare-scope-options',self.pkg,[])
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
class HoursOnlyTests(unittest.TestCase):
 build=ScopeTests.build
 def setUp(self):
  ScopeTests.setUp(self);self.source=json.loads((self.pkg/'examples/hours-only-source.json').read_text());self.plan=json.loads((self.pkg/'examples/hours-only-plan.json').read_text())
 def cell(self,html,item,quote):
  doc=Markup();start=html.index('data-item="'+item+'"');start=html.index('data-quote="'+quote+'"',start);end=html.index('</td>',start);doc.feed('<td '+html[start:end]+'</td>');return ''.join(doc.text),html[start:end]
 def test_hours_only_comparison_validates_and_builds_without_zero(self):
  p,out=self.build();self.assertEqual(p.returncode,0,p.stderr);html=out.read_text();doc=Markup();doc.feed(html);text=' '.join(doc.text)
  receipt=json.loads(out.with_suffix('.reconciliation.json').read_text())
  self.assertEqual(receipt['pricing'],'unpriced');self.assertEqual(receipt['unestimated'],{'Q-HOURS-001':0,'Q-HOURS-002':1})
  shown,markup=self.cell(html,'reminders','Q-HOURS-002')
  self.assertIn('data-estimate="unestimated"',markup);self.assertIn('data-hours=""',markup);self.assertIn('Not estimated',shown)
  self.assertIn('message provider',shown);self.assertNotRegex(shown,r'\d')
  self.assertIn('Range 24 to 48 h',self.cell(html,'calendar-sync','Q-HOURS-001')[0])
  for value in self.source['missing_inputs'].values():self.assertIn(value,text)
  self.assertIn('Inputs still needed',text);self.assertFalse(any(a.get('class')=='plans' for t,a in doc.tags))
  self.assertNotRegex(text,r'\b0 h\b|\bweeks\b|staffing hours|\bUSD\b|Active plan')
 def test_unpriced_and_unestimated_corruption_prevents_output(self):
  cases={
   'zero-hours':lambda s,p:p['matrix'][4]['cells']['Q-HOURS-002'].update(hours=0,status='estimated'),
   'dropped-status':lambda s,p:p['matrix'][4]['cells']['Q-HOURS-002'].pop('status'),
   'null-without-status':lambda s,p:s['quotes'][1]['full_items'][4].pop('status'),
   'unestimated-with-hours':lambda s,p:s['quotes'][1]['full_items'][4].update(hours=8),
   'no-discovery':lambda s,p:s['quotes'][1]['full_items'][4].pop('discovery'),
   'range-order':lambda s,p:s['quotes'][0]['full_items'][1].update(hours={'low':50,'expected':32,'high':48}),
   'range-display':lambda s,p:p['matrix'][1]['cells']['Q-HOURS-001'].update(hours={'low':24,'expected':30,'high':48}),
   'range-as-number':lambda s,p:p['matrix'][1]['cells']['Q-HOURS-001'].update(hours=32),
   'missing-timeline':lambda s,p:s['missing_inputs'].pop('timeline'),
   'source-snapshot':lambda s,p:s['quotes'][0].update(snapshots=[{'id':'x','label':'Team','currency':'USD','revenue':1,'weeks':1,'hours':1}],active_snapshot_id='x'),
   'display-snapshot':lambda s,p:p['options'][0].update(snapshots=[{'id':'x','label':'Team','currency':'USD','revenue':1,'weeks':1,'hours':1}]),
  }
  for kind,change in cases.items():
   s=copy.deepcopy(self.source);p=copy.deepcopy(self.plan);change(s,p)
   result,out=self.build(source=s,plan=p);self.assertEqual(result.returncode,2,kind);self.assertFalse(out.exists(),kind)
 def test_priced_quotes_stay_strict(self):
  s=json.loads((self.pkg/'examples/comparison-source.json').read_text());p=json.loads((self.pkg/'examples/comparison-plan.json').read_text())
  for kind in ('null-hours','unestimated','empty-snapshots','missing-inputs'):
   t=copy.deepcopy(s)
   if kind=='null-hours':t['quotes'][0]['full_items'][0]['hours']=None
   elif kind=='unestimated':t['quotes'][0]['full_items'][0].update(hours=None,status='unestimated',discovery='a sample export')
   elif kind=='empty-snapshots':t['quotes'][0]['snapshots']=[]
   else:t['missing_inputs']={'price':'a','staffing':'b','timeline':'c'}
   result,out=self.build(source=t,plan=p);self.assertEqual(result.returncode,2,kind);self.assertFalse(out.exists(),kind)
   if kind=='unestimated':self.assertIn('only an unpriced comparison',result.stderr)
 def test_rendered_prose_gate_reads_the_matrix_as_cells(self):
  p,out=self.build();self.assertEqual(p.returncode,0,p.stderr)
  checker=self.pkg/'_runtime/writing-diagnostics/scripts/writing_check.py'
  result=subprocess.run([sys.executable,str(checker),'--rendered','--json',str(out)],capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stdout+result.stderr)
 @integration('browser')
 def test_browser_check_and_pdf_text_keep_hours_as_digits(self):
  from pypdf import PdfReader
  for name in ('hours-only','comparison'):
   source=json.loads((self.pkg/f'examples/{name}-source.json').read_text());plan=json.loads((self.pkg/f'examples/{name}-plan.json').read_text())
   p,out=self.build(source,plan);self.assertEqual(p.returncode,0,p.stderr);plan_path=out.parent/'plan.json';check=out.parent/'check'
   result=subprocess.run(['node',str(self.pkg/'scripts/check_scope.mjs'),out.as_uri(),str(check),str(plan_path)],capture_output=True,text=True,timeout=180)
   self.assertEqual(result.returncode,0,result.stdout+result.stderr)
   text=''.join(page.extract_text() for page in PdfReader(check/'scope.pdf').pages)
   self.assertFalse([c for c in text if 0xE000<=ord(c)<=0xF8FF],name)
   for item in plan['matrix']:
    for cell in item['cells'].values():
     hours=cell['hours']
     if isinstance(hours,dict):self.assertIn('Range '+str(hours['low'])+' to '+str(hours['high'])+' h',text)
     elif hours is not None:self.assertIn(str(hours)+' h',text)
if __name__=='__main__':unittest.main()
