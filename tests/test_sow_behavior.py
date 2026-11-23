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
from test_capabilities import configured
NODE=os.environ.get('ESTATE_NODE') or shutil.which('node')

class SowBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='estate-sow-isolated-')
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name).resolve()
        self.package=self.directory/'write-statement-of-work'
        assemble(ROOT,'write-statement-of-work',self.package,runtime_dependencies('write-statement-of-work'))
        self.contract=self.directory/'contract.json'
        shutil.copy2(ROOT/'examples/write-statement-of-work/contract.example.json',self.contract)
        self.model=json.loads((ROOT/'examples/write-statement-of-work/quote.example.json').read_text())
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
                model=self.model if variant in ('waterfall','agile') else json.loads((ROOT/'examples/write-statement-of-work/assessment.example.json').read_text())
                result,out,source=self.build(variant,model,name=variant)
                self.assertEqual(0,result.returncode,result.stderr)
                verification=self.verify(out,source,variant)
                self.assertEqual(0,verification.returncode,verification.stdout+verification.stderr)
                with zipfile.ZipFile(out) as archive:
                    xml=''.join(archive.read(n).decode() for n in archive.namelist() if n.endswith('.xml'))
                self.assertNotIn('ExampleCo',xml)
                self.assertNotIn('Plus Jakarta',xml)
                self.assertIn('Example Delivery LLC',xml)
                self.assertIn('Arial',xml)
                self.assertFalse(list(self.package.rglob('exampleco*')))
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
        model=json.loads((ROOT/'examples/write-statement-of-work/assessment.example.json').read_text())
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
                if member.filename=='word/document.xml':data=data.replace(b'Synthetic acceptance marker A',b'Synthetic acceptance marker X')
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
        contract['clauses']['DEEMED_ACCEPTANCE']=contract['clauses']['DEEMED_ACCEPTANCE'].replace('marker A', 'marker B')
        self.contract.write_text(json.dumps(contract))
        result,out,source=self.build()
        self.assertEqual(0,result.returncode,result.stderr)
        verification=self.verify(out,source)
        self.assertEqual(0,verification.returncode,verification.stdout)
        with zipfile.ZipFile(out) as archive: text=archive.read('word/document.xml').decode()
        self.assertIn('Synthetic acceptance marker B',text)
        self.assertNotIn('Synthetic acceptance marker A',text)

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

    # --- Proof defects 162 to 166 (synthetic names only) ---

    def document_text(self,path):
        import re
        with zipfile.ZipFile(path) as archive:xml=archive.read('word/document.xml').decode()
        return re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',xml.replace('</w:p>',' ')))

    def use_start_window_clause(self,days=45):
        contract=json.loads(self.contract.read_text())
        contract['clauses']['ELAPSED_PERIOD']='If the client does not start within {N} days of signature, dates are re-confirmed.'
        contract['startWindowDays']=days
        self.contract.write_text(json.dumps(contract))

    def failures(self,verification):
        import re
        return json.loads(re.search(r'\{.*\}',verification.stdout,re.S).group(0))

    def test_start_window_and_signing_date_come_from_their_own_fields(self):
        self.use_start_window_clause(45)
        model=copy.deepcopy(self.model)
        model['projectContext']['signingDate']='2026-10-20'
        self.assertEqual(4,model['projectSummary']['durationWeeks'])
        result,out,source=self.build(model=model)
        self.assertEqual(0,result.returncode,result.stderr)
        text=self.document_text(out)
        self.assertIn('within 45 days of signature',text)   # was "within 4 days" before the fix
        self.assertNotIn('within 4 days',text)
        self.assertIn('Synthetic fixture signature preamble. 2026-10-20',text)   # not returnBy, 2026-11-01
        verification=self.verify(out,source)
        self.assertEqual(0,verification.returncode,verification.stdout)
        # A document that fills the start window from the duration no longer passes.
        wrong=self.directory/'wrong-window.docx'
        with zipfile.ZipFile(out) as archive,zipfile.ZipFile(wrong,'w') as target:
            for member in archive.infolist():
                data=archive.read(member.filename)
                if member.filename=='word/document.xml':data=data.replace(b'>45<',b'>4<').replace(b'2026-10-20',b'2026-11-01')
                target.writestr(member,data)
        Path(str(wrong)+'.build.json').write_bytes(Path(str(out)+'.build.json').read_bytes())
        verification=self.verify(wrong,source)
        self.assertNotEqual(0,verification.returncode)
        self.assertIn('ELAPSED_PERIOD',verification.stdout);self.assertIn('SIGNATURE_PREAMBLE',verification.stdout)

    def test_absent_start_window_and_signing_date_are_visible_flags(self):
        self.use_start_window_clause(45)
        contract=json.loads(self.contract.read_text());del contract['startWindowDays'];self.contract.write_text(json.dumps(contract))
        model=copy.deepcopy(self.model);del model['projectContext']['signingDate']
        result,out,_=self.build(model=model)
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        self.assertIn('startWindowDays',result.stderr);self.assertIn('signing date',result.stderr)
        result,out,source=self.build(model=model,name='draft',extra=('--draft',))
        self.assertEqual(0,result.returncode,result.stderr)
        text=self.document_text(out)
        self.assertIn('[FLAG: startWindowDays',text);self.assertIn('[FLAG: signing date',text)
        report=self.failures(self.verify(out,source))
        self.assertIn('Unresolved input: {N} ',' '.join(f[:len('Unresolved input: {N} ')] for f in report['failures']))
        self.assertTrue(any(f.startswith('Unresolved input: {DATE}') for f in report['failures']))

    def test_invalid_start_window_is_rejected(self):
        self.use_start_window_clause(0)
        result,out,_=self.build()
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        self.assertIn('startWindowDays',result.stderr)

    def test_null_fields_are_unresolved_findings_and_checks_continue(self):
        result,out,source=self.build();self.assertEqual(0,result.returncode,result.stderr)
        baseline=self.failures(self.verify(out,source))
        self.assertTrue(baseline['passed'],baseline)
        def variant(name,change):
            model=copy.deepcopy(self.model);change(model)
            path=self.directory/(name+'.quote.json');path.write_text(json.dumps(model));return path
        # returnBy is the offer expiry; no token reads it, so a null there changes nothing the verifier checks.
        quote=variant('null-return',lambda m:m['projectContext'].__setitem__('returnBy',None))
        report=self.failures(self.verify(out,quote))
        self.assertFalse(any('None' in f or 'replace()' in f for f in report['failures']),report)
        for name,change,token in (
                ('null-date',lambda m:m['projectContext'].__setitem__('signingDate',None),'{DATE}'),
                ('null-total',lambda m:m['projectSummary'].__setitem__('totalValue',None),'{UPFRONT}'),
                ('null-legal',lambda m:m['projectContext'].__setitem__('clientLegalName',None),'{CLIENT}')):
            with self.subTest(name=name):
                verification=self.verify(out,variant(name,change))
                self.assertEqual(1,verification.returncode)
                report=self.failures(verification)
                self.assertGreater(report['checks'],50)   # earlier checks were all dropped
                self.assertTrue(any(f.startswith('Unresolved input: '+token) for f in report['failures']),report['failures'])
                self.assertFalse(any('NoneType' in f or 'replace()' in f for f in report['failures']),report['failures'])
        # A null total reports every token that needs it, each as its own finding.
        report=self.failures(self.verify(out,variant('null-total-2',lambda m:m['projectSummary'].__setitem__('totalValue',None))))
        tokens=[f.split(' ')[2] for f in report['failures'] if f.startswith('Unresolved input: {')]
        self.assertGreaterEqual(len(set(tokens)),2,report['failures'])

    def test_document_route_checks_a_draft_without_the_build_record(self):
        model=copy.deepcopy(self.model);del model['projectContext']['signingDate']
        result,out,source=self.build(model=model,name='draft',extra=('--draft',))
        self.assertEqual(0,result.returncode,result.stderr)
        Path(str(out)+'.build.json').unlink()
        default=self.failures(self.verify(out,source))
        self.assertIn('Missing build record',default['failures'])
        routed=self.run_command([sys.executable,self.package/'scripts/verify_contract.py',out,'--contract',self.contract,
            '--quote',source,'--variant','waterfall','--document-route'])
        report=self.failures(routed)
        self.assertEqual('document-route',report['mode'])
        self.assertFalse(any('build record' in f.lower() or 'Build hash' in f for f in report['failures']),report['failures'])
        self.assertTrue(any(f.startswith('Unresolved input: {DATE}') for f in report['failures']))
        self.assertGreater(report['checks'],50)
        # A complete document passes in this mode with no build record at all.
        result,clean,quote=self.build(name='clean');self.assertEqual(0,result.returncode,result.stderr)
        Path(str(clean)+'.build.json').unlink()
        routed=self.run_command([sys.executable,self.package/'scripts/verify_contract.py',clean,'--contract',self.contract,
            '--quote',quote,'--variant','waterfall','--document-route'])
        self.assertEqual(0,routed.returncode,routed.stdout)

    def test_client_legal_name_is_the_party_and_account_name_stays_for_display(self):
        model=copy.deepcopy(self.model)
        model['projectContext']['accountName']='Northwind Outfitters'
        model['projectContext']['clientLegalName']='Northwind Outfitters Holdings LLC'
        result,out,source=self.build(model=model)
        self.assertEqual(0,result.returncode,result.stderr)
        text=self.document_text(out)
        self.assertIn('Synthetic fixture preamble. Example Delivery LLC Northwind Outfitters Holdings LLC',text)
        self.assertIn('Prepared for Northwind Outfitters',text)
        self.assertGreaterEqual(text.count('Northwind Outfitters Holdings LLC'),3)   # parties, notices, signature block
        self.assertEqual(0,self.verify(out,source).returncode)
        log=next((out.parent/'_source').glob('*Resolution Log.md')).read_text()
        self.assertIn('| Parties | clientLegalName | Northwind Outfitters Holdings LLC | projectContext.clientLegalName |  |',log)

    def test_unknown_legal_entity_is_flagged_not_copied_from_the_trading_name(self):
        model=copy.deepcopy(self.model)
        model['projectContext']['accountName']='Northwind Outfitters';del model['projectContext']['clientLegalName']
        result,out,_=self.build(model=model);self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        self.assertIn('clientLegalName',result.stderr)
        result,out,source=self.build(model=model,name='draft',extra=('--draft',))
        self.assertEqual(0,result.returncode,result.stderr)
        text=self.document_text(out)
        self.assertIn('[FLAG: clientLegalName missing]',text)
        self.assertNotIn('Example Delivery LLC Northwind Outfitters',text)   # the old preamble named the trading name
        self.assertIn('Prepared for Northwind Outfitters',text)
        log=next((out.parent/'_source').glob('*Resolution Log.md')).read_text()
        self.assertIn('| Parties | clientLegalName | FLAGGED, not on quote | projectContext.clientLegalName | YES |',log)
        self.assertNotEqual(0,self.verify(out,source).returncode)

    def parity(self,*args):
        return self.run_command([sys.executable,self.package/'scripts/verify_render_parity.py',*args])

    def test_render_parity_names_a_table_row_missing_from_the_pages(self):
        import re
        result,out,_=self.build();self.assertEqual(0,result.returncode,result.stderr)
        with zipfile.ZipFile(out) as archive:xml=archive.read('word/document.xml').decode()
        rows=re.findall(r'<w:tr[ >].*?</w:tr>',xml,re.S)
        row=next(r for r in rows if 'Configure the queue and execute the agreed test cases.' in r)
        pages=self.directory/'pages.txt'
        text=re.sub(r'<[^>]+>','',re.sub(r'<w:br[^>]*/>','\n',xml).replace('</w:p>','\n').replace('</w:tc>','\n'))
        pages.write_text(__import__('html').unescape(text))
        self.assertEqual(0,self.parity(out,'--pdf-text',pages).returncode)
        # Wrapped lines and extra header and footer text do not matter.
        wrapped=self.directory/'wrapped.txt'
        wrapped.write_text(re.sub(r' +','\n',pages.read_text().replace('Configure the queue and','Configure the queue\nCONFIDENTIAL Page 3 of 9\nand')))
        verdict=self.parity(out,'--pdf-text',wrapped)
        self.assertEqual(0,verdict.returncode,verdict.stdout)
        # Delete one row's text from the extracted pages: the check names it.
        missing=pages.read_text().replace('Configure the queue and execute the agreed test cases.','')
        dropped=self.directory/'dropped.txt';dropped.write_text(missing)
        verdict=self.parity(out,'--pdf-text',dropped)
        self.assertEqual(1,verdict.returncode)
        self.assertIn('Configure the queue and execute the agreed test cases.',verdict.stdout)
        self.assertIn('"kind": "cell"',verdict.stdout)

    @configured('LibreOffice and pdftotext on PATH', lambda: bool(shutil.which('soffice') and shutil.which('pdftotext')))
    def test_render_parity_against_a_real_render_and_a_dropped_row(self):
        import re
        result,out,_=self.build();self.assertEqual(0,result.returncode,result.stderr)
        verdict=self.parity(out,'--output',self.directory/'parity.json')
        self.assertEqual(0,verdict.returncode,verdict.stdout+verdict.stderr)
        self.assertFalse(list(Path(tempfile.gettempdir()).glob('sow-parity-*')),'the temporary render folder must be removed')
        # Render a copy whose Word file lost one table row, then compare it with the intact file.
        altered=self.directory/'altered.docx'
        with zipfile.ZipFile(out) as archive,zipfile.ZipFile(altered,'w',zipfile.ZIP_DEFLATED) as target:
            for member in archive.infolist():
                data=archive.read(member.filename)
                if member.filename=='word/document.xml':
                    xml=data.decode()
                    row=next(r for r in re.findall(r'<w:tr[ >].*?</w:tr>',xml,re.S) if 'Configure the queue and execute the agreed test cases.' in r)
                    data=xml.replace(row,'',1).encode()
                target.writestr(member,data)
        home=self.directory/'lo-home';home.mkdir()
        render=subprocess.run([shutil.which('soffice'),'--headless','--convert-to','pdf','--outdir',str(self.directory),str(altered)],
            env=dict(self.env,HOME=str(home)),capture_output=True,text=True,timeout=300)
        self.assertEqual(0,render.returncode,render.stderr)
        verdict=self.parity(out,'--pdf',self.directory/'altered.pdf')
        self.assertEqual(1,verdict.returncode)
        self.assertIn('Configure the queue and execute the agreed test cases.',verdict.stdout)

if __name__=='__main__':unittest.main()
