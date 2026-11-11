"""SOW behavior against synthetic contract/quote inputs and adversarial edits."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from portable import assemble
from estate import runtime_dependencies
NODE=os.environ.get('ESTATE_NODE') or shutil.which('node')

class SowBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='estate-sow-isolated-')
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name).resolve()
        self.package=self.directory/'sow'
        assemble(ROOT,'sow',self.package,runtime_dependencies('sow'))
        self.contract=self.directory/'contract.json'
        shutil.copy2(ROOT/'examples/sow/contract.example.json',self.contract)
        self.model=json.loads((ROOT/'examples/sow/quote.example.json').read_text())
        self.env={k:v for k,v in os.environ.items() if k not in ('SKILLS_BRAND_PROFILE','PYTHONPATH')}
        self.commands=0
        self.assertTrue(NODE,'Node is required for the SOW behavior tests')

    def run_command(self,args):
        self.commands+=1
        result=subprocess.run(list(map(str,args)),cwd=self.directory,env=self.env,capture_output=True,text=True)
        (self.directory/f'command-{self.commands}.json').write_text(json.dumps({'args':list(map(str,args)),
            'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2))
        return result

    def build(self,variant='waterfall',model=None,name='output',extra=()):
        source=self.directory/(name+'.quote.json');source.write_text(json.dumps(model or self.model))
        output=self.directory/(name+'.docx')
        result=self.run_command([NODE,self.package/'scripts/generate_sow.js',source,variant,
            '--contract',self.contract,'--output',output,'--example',*extra])
        return result,output,source

    def verify(self,output,quote,variant='waterfall'):
        return self.run_command([sys.executable,self.package/'scripts/verify_contract.py',output,
            '--contract',self.contract,'--quote',quote,'--variant',variant])

    def test_all_variants_preserve_selected_inputs_in_isolated_package(self):
        for variant in ('waterfall','agile','assess','loe'):
            with self.subTest(variant=variant):
                model=self.model if variant in ('waterfall','agile') else json.loads((ROOT/'examples/sow/assessment.example.json').read_text())
                result,out,source=self.build(variant,model,name=variant)
                self.assertEqual(0,result.returncode,result.stderr)
                verification=self.verify(out,source,variant)
                self.assertEqual(0,verification.returncode,verification.stdout+verification.stderr)
                with zipfile.ZipFile(out) as archive:
                    xml=''.join(archive.read(n).decode() for n in archive.namelist() if n.endswith('.xml'))
                self.assertNotIn('Aleysian',xml)
                self.assertNotIn('Plus Jakarta',xml)
                self.assertIn('Example Delivery LLC',xml)
                self.assertIn('Arial',xml)
                self.assertFalse(list(self.package.rglob('aleysian*')))
                if variant!='loe':
                    with zipfile.ZipFile(out) as archive:
                        document=ET.fromstring(archive.read('word/document.xml'))
                    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                    attribute='{'+ns['w']+'}'
                    targets={item.get(attribute+'name') for item in document.findall('.//w:bookmarkStart',ns)}
                    links=[item.get(attribute+'anchor') for item in document.findall('.//w:hyperlink',ns) if item.get(attribute+'anchor')]
                    self.assertGreater(len(links),10)
                    self.assertTrue(set(links)<=targets)

    def test_invalid_dates_and_discount_are_rejected(self):
        for label in ('reversed','impossible','expiry','discount'):
            model=copy.deepcopy(self.model);band=model['timeline']['bands'][0]
            if label=='reversed':band['endDate']='2026-01-01'
            elif label=='impossible':band['startDate']='2026-02-30'
            elif label=='expiry':model['projectContext']['returnBy']='2027-01-01'
            else:band['resources'][0]['discountAmount']=-1
            result,out,_=self.build(model=model,name=label)
            self.assertNotEqual(0,result.returncode,result.stderr)
            self.assertFalse(out.exists())

    def test_offsetting_phase_errors_are_rejected(self):
        model=copy.deepcopy(self.model)
        model['timeline']['bands'][0]['resources'][0]['hoursByPhase']['Build']+=5
        model['timeline']['bands'][0]['resources'][1]['hoursByPhase']['Build']-=5
        result,out,_=self.build(model=model)
        self.assertNotEqual(0,result.returncode)
        self.assertFalse(out.exists())
        self.assertIn('phase hours differ',result.stderr)

    def test_assessment_uses_quoted_stages_and_responsibilities(self):
        model=json.loads((ROOT/'examples/sow/assessment.example.json').read_text())
        model['timeline']['bands'][0]['phases'][0]['purpose']='Interview the named workflow owner about assignment decisions.'
        result,out,source=self.build('assess',model)
        self.assertEqual(0,result.returncode,result.stderr)
        verification=self.verify(out,source,'assess')
        self.assertEqual(0,verification.returncode,verification.stdout)
        with zipfile.ZipFile(out) as archive:text=archive.read('word/document.xml').decode()
        self.assertIn('Interview the named workflow owner about assignment decisions.',text)
        self.assertNotIn('Stakeholder sessions and information gathering across the in-scope areas.',text)
        self.assertNotIn('Rates are in Section 9.',text)

    def test_offsetting_revenue_errors_are_rejected(self):
        model=copy.deepcopy(self.model)
        model['timeline']['bands'][0]['resources'][0]['totalRevenue']+=100
        model['timeline']['bands'][0]['resources'][1]['totalRevenue']-=100
        result,out,_=self.build(model=model)
        self.assertNotEqual(0,result.returncode)
        self.assertFalse(out.exists())
        self.assertIn('differs from revenue',result.stderr)

    def test_quote_total_mismatch_is_not_rendered(self):
        model=copy.deepcopy(self.model);model['projectSummary']['totalValue']+=1
        result,out,_=self.build(model=model)
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        self.assertTrue(Path(str(out)+'.build.json').exists())

    def test_missing_context_needs_explicit_draft(self):
        model=copy.deepcopy(self.model);del model['projectContext']['clientAddress']
        result,out,_=self.build(model=model)
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        result,out,source=self.build(model=model,name='draft',extra=('--draft',))
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertNotEqual(0,self.verify(out,source).returncode)

    def test_altered_clause_fails_even_when_other_anchors_survive(self):
        result,out,source=self.build();self.assertEqual(0,result.returncode,result.stderr)
        altered=self.directory/'altered.docx'
        with zipfile.ZipFile(out) as archive,zipfile.ZipFile(altered,'w') as target:
            for member in archive.infolist():
                data=archive.read(member.filename)
                if member.filename=='word/document.xml':data=data.replace(b'five (5) business days',b'forty (40) business days')
                target.writestr(member,data)
        receipt=json.loads(Path(str(out)+'.build.json').read_text())
        # Even a copied receipt whose artifact hash is refreshed cannot conceal changed clause text.
        receipt['artifactSha256']=hashlib.sha256(altered.read_bytes()).hexdigest()
        Path(str(altered)+'.build.json').write_text(json.dumps(receipt))
        verification=self.verify(altered,source)
        self.assertNotEqual(0,verification.returncode)
        self.assertIn('DEEMED_ACCEPTANCE',verification.stdout)

    def test_changed_contract_profile_controls_the_rendered_wording(self):
        contract=json.loads(self.contract.read_text())
        contract['clauses']['DEEMED_ACCEPTANCE']=contract['clauses']['DEEMED_ACCEPTANCE'].replace('five (5)', 'seven (7)')
        self.contract.write_text(json.dumps(contract))
        result,out,source=self.build()
        self.assertEqual(0,result.returncode,result.stderr)
        verification=self.verify(out,source)
        self.assertEqual(0,verification.returncode,verification.stdout)
        with zipfile.ZipFile(out) as archive: text=archive.read('word/document.xml').decode()
        self.assertIn('seven (7) business days',text)
        self.assertNotIn('five (5) business days',text)

    def test_profile_font_palette_and_logo_aspect_ratio(self):
        import re,struct,zlib
        policy=(ROOT/'policies/brand.md').read_text()
        profile=json.loads(re.search(r'```json\s*\n(.*?)\n```',policy,re.S).group(1))
        profile['colors']['accent']='#7B321A';profile['type']['office']='Georgia'
        def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',20,10,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\x00'+bytes([20,30,40])*20)*10))+chunk(b'IEND',b'')
        (self.directory/'logo.png').write_bytes(png)
        profile['logo']='logo.png'
        selected=self.directory/'brand.md';selected.write_text('```json\n'+json.dumps(profile)+'\n```\n')
        result,out,_=self.build(extra=('--profile',str(selected)))
        self.assertEqual(0,result.returncode,result.stderr)
        with zipfile.ZipFile(out) as archive:text=archive.read('word/document.xml').decode()
        self.assertIn('Georgia',text);self.assertIn('7B321A',text)
        extents=re.findall(r'<wp:extent cx="(\d+)" cy="(\d+)"',text)
        self.assertTrue(extents)
        self.assertTrue(all(abs(int(w)/int(h)-2)<0.001 for w,h in extents))

    def test_existing_output_is_preserved(self):
        result,out,_=self.build();self.assertEqual(0,result.returncode,result.stderr)
        before=out.read_bytes();result,_,_=self.build()
        self.assertNotEqual(0,result.returncode);self.assertEqual(before,out.read_bytes())

if __name__=='__main__':unittest.main()
