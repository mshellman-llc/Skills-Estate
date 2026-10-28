"""Exercise actual portable handout PDFs, content preservation and failure modes."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from portable import assemble
from estate import runtime_dependencies


class PlaybookPdfTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='estate-playbook-isolated-')
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name).resolve()
        self.package=self.folder/'playbook-onepager'
        assemble(ROOT,'playbook-onepager',self.package,runtime_dependencies('playbook-onepager'))
        self.spec=json.loads((ROOT/'examples/playbook-onepager/synthetic-offering.json').read_text())
        self.env={k:v for k,v in os.environ.items() if k not in ('SKILLS_BRAND_PROFILE','PYTHONPATH')}

    def render(self,spec=None,extra=(),name='output',md=None):
        source=self.folder/('input.json' if md is None else 'input.md')
        source.write_text(json.dumps(self.spec if spec is None else spec) if md is None else md)
        out=self.folder/name
        args=[sys.executable,str(self.package/'scripts/render_playbook.py')]
        args+=['--json',str(source)] if md is None else ['--md',str(source),'--all']
        args+=['--out',str(out),*extra]
        result=subprocess.run(args,cwd=self.folder,env=self.env,capture_output=True,text=True,timeout=180)
        (self.folder/(name+'.command.json')).write_text(json.dumps({'args':args,'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2))
        return result,out

    def test_real_rich_pdfs_preserve_content_and_page_counts(self):
        from pypdf import PdfReader
        result,out=self.render()
        self.assertEqual(0,result.returncode,result.stderr)
        for kind,count in [('internal-brief',2),('external-onepager',1)]:
            pdf=out/f'service-intake-review-{kind}.pdf'
            reader=PdfReader(pdf);self.assertEqual(count,len(reader.pages))
            text=' '.join(' '.join(p.extract_text().split()) for p in reader.pages)
            # Linux PDF fonts may extract presentation ligatures as single characters.
            text=text.translate(str.maketrans({'ﬀ':'ff', 'ﬁ':'fi', 'ﬂ':'fl',
                                             'ﬃ':'ffi', 'ﬄ':'ffl', 'ﬅ':'st', 'ﬆ':'st'}))
            selected=self.spec['internal' if count==2 else 'external']
            for key in (('s1','s2','s3','s4') if count==2 else ('intro','how')):
                self.assertIn(selected[key],text)
            for key in (('qualifiers','disqualifiers','included_list','not_included','steps') if count==2 else ('what_you_get',)):
                for item in selected[key]:self.assertIn(item,text)
            for key in (('tracks','callouts') if count==2 else ('columns',)):
                for item in selected[key]:
                    self.assertIn(item['k'].casefold(),text.casefold());self.assertIn(item['v'],text)
            report=json.loads(pdf.with_suffix('.checks.json').read_text())
            self.assertEqual([],report['failures'])
            self.assertNotIn('Aleysian',text)
        self.assertEqual(2,len(json.loads((out/'render-manifest.json').read_text())['artifacts']))

    def test_missing_required_json_content_fails(self):
        spec=copy.deepcopy(self.spec);del spec['internal']['s1']
        result,out=self.render(spec)
        self.assertNotEqual(0,result.returncode)
        self.assertFalse(list(out.glob('*.pdf')))
        self.assertIn('Missing required text: s1',result.stderr)

    def test_overflow_retains_failed_pdf_and_rejects_it(self):
        spec={'external':copy.deepcopy(self.spec['external'])}
        spec['external']['intro']='An oversized source paragraph must not silently disappear. '*150
        result,out=self.render(spec)
        self.assertNotEqual(0,result.returncode)
        reports=list(out.glob('*.checks.json'));self.assertEqual(1,len(reports))
        self.assertTrue(json.loads(reports[0].read_text())['failures'])
        self.assertTrue(list(out.glob('*.pdf')),'Retain the failed output for diagnosis')
        self.assertFalse((out/'render-manifest.json').exists())

    def test_source_html_cannot_load_files_or_remote_images(self):
        spec=copy.deepcopy(self.spec);spec['external']['intro']='<img src="file:///etc/passwd">'
        spec.pop('internal')
        result,out=self.render(spec)
        self.assertNotEqual(0,result.returncode)
        self.assertIn('Unsupported source HTML tag',result.stderr)
        self.assertFalse(list(out.glob('*.pdf')))

    def test_alternate_profile_controls_palette_and_font(self):
        profile=json.loads(re.search(r'```json\s*\n(.*?)\n```',(ROOT/'policies/brand.md').read_text(),re.S).group(1))
        profile['colors']['accent']='#7B321A';profile['type']['body']='Georgia, serif'
        profile['type']['headings']='Verdana, sans-serif'
        path=self.folder/'brand.md';path.write_text('```json\n'+json.dumps(profile)+'\n```')
        result,out=self.render(extra=('--profile',str(path)))
        self.assertEqual(0,result.returncode,result.stderr)
        html=next(out.glob('*.html')).read_text()
        self.assertIn('--brand-accent:#7B321A;',html)
        self.assertIn('--font-sans:Georgia, serif;',html)
        self.assertNotIn('logos/aleysian',html)
        for checks in out.glob('*.checks.json'):
            typography=json.loads(checks.read_text())['typography']
            self.assertEqual('verdana, sans-serif',typography['expectedHeadingStack'])
            self.assertTrue(all('Verdana' in font for font in typography['headingFonts']))

    def test_declared_missing_logo_fails(self):
        profile=json.loads(re.search(r'```json\s*\n(.*?)\n```',(ROOT/'policies/brand.md').read_text(),re.S).group(1))
        profile['logo']='absent.png'
        path=self.folder/'brand.md';path.write_text('```json\n'+json.dumps(profile)+'\n```')
        result,out=self.render(extra=('--profile',str(path)))
        self.assertNotEqual(0,result.returncode)
        self.assertFalse(list(out.glob('*.pdf')))

    def test_markdown_catalog_and_unknown_label(self):
        module_spec=importlib.util.spec_from_file_location('legacy_parser_test',self.package/'scripts/render_playbook_selftest.py')
        module=importlib.util.module_from_spec(module_spec)
        sys.path.insert(0,str(self.package/'scripts'))
        try:module_spec.loader.exec_module(module)
        finally:sys.path.pop(0)
        result,out=self.render(md=module.ENTRY)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertEqual(2,len(list(out.glob('*.pdf'))))
        bad=module.ENTRY.replace('**What is it**','**Unexpected source heading**',1)
        result,_=self.render(md=bad,name='bad-label')
        self.assertNotEqual(0,result.returncode)
        self.assertIn('unrecognised label',result.stderr)

    def test_previous_output_is_not_replaced(self):
        result,out=self.render()
        self.assertEqual(0,result.returncode,result.stderr)
        before={p.name:p.read_bytes() for p in out.glob('*.pdf')}
        result,_=self.render()
        self.assertNotEqual(0,result.returncode)
        self.assertEqual(before,{p.name:p.read_bytes() for p in out.glob('*.pdf')})

if __name__=='__main__':
    unittest.main()
