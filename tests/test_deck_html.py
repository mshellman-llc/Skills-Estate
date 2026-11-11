import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from portable import assemble

class Markup(HTMLParser):
    def __init__(self):super().__init__();self.tags=[];self.text=[]
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
    def handle_data(self,data):self.text.append(data)

class DeckTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.pkg=self.base/'deck-builder'
        assemble(ROOT,'deck-builder',self.pkg,[])
        self.data=json.loads((self.pkg/'examples/reconciliation.json').read_text())
        self.counter=0
    def run_build(self,data=None,extra=(),output='deck.html'):
        self.counter+=1
        source=self.base/f'input-{self.counter}.json';source.write_text(json.dumps(self.data if data is None else data))
        dest=self.base/output
        proc=subprocess.run([sys.executable,str(self.pkg/'scripts/build_html.py'),str(source),str(dest),*extra],cwd=self.base,capture_output=True,text=True)
        (self.base/f'result-{self.counter}.json').write_text(json.dumps({'exit':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr},indent=2))
        return proc,dest
    def test_isolated_package_preserves_content_and_sources(self):
        p,d=self.run_build();self.assertEqual(p.returncode,0,p.stderr)
        doc=Markup();doc.feed(d.read_text())
        self.assertEqual(sum(t=='section' for t,a in doc.tags),14)
        for slide in self.data['slides']:
            self.assertIn(slide['title'],doc.text)
            if slide.get('lead'):self.assertIn(slide['lead'],doc.text)
        for source in self.data['sources'].values():self.assertIn(source,doc.text)
        self.assertEqual(sum(t=='h1' for t,a in doc.tags),1)
        self.assertNotIn('Aleysian',d.read_text())
    def test_authored_markup_is_escaped(self):
        data=copy.deepcopy(self.data);data['slides'][0]['lead']='<script>alert("test")</script>'
        p,d=self.run_build(data);self.assertEqual(p.returncode,0,p.stderr)
        doc=Markup();doc.feed(d.read_text());self.assertFalse(any(t=='script' for t,a in doc.tags))
        self.assertIn(data['slides'][0]['lead'],doc.text)
    def test_missing_evidence_and_bad_table_refuse_output(self):
        for change in ['source','table']:
            data=copy.deepcopy(self.data)
            if change=='source':data['slides'][0]['sources']=['missing']
            else:data['slides'][0]['blocks']=[{'type':'table','headers':['one','two'],'rows':[['one']]}]
            p,d=self.run_build(data,output=change+'.html');self.assertEqual(p.returncode,2);self.assertFalse(d.exists())
    def test_existing_output_is_preserved(self):
        dest=self.base/'deck.html';dest.write_text('previous deck')
        p,d=self.run_build();self.assertEqual(p.returncode,2);self.assertEqual(d.read_text(),'previous deck')
    def test_missing_profile_is_not_replaced_by_neutral(self):
        p,d=self.run_build(extra=['--profile',str(self.base/'missing.md')]);self.assertEqual(p.returncode,2);self.assertFalse(d.exists())
    def test_alternate_profile_changes_output(self):
        text=(ROOT/'policies/brand.md').read_text();start=text.index('```json\n')+8;end=text.index('\n```',start)
        profile=json.loads(text[start:end]);profile['name']='Synthetic alternate';profile['colors']['accent']='#704226';profile['type']['headings']='Georgia, serif'
        file=self.base/'alternate.md';file.write_text('```json\n'+json.dumps(profile)+'\n```')
        p,d=self.run_build(extra=['--profile',str(file)]);self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('--brand-accent:#704226',d.read_text());self.assertIn('--brand-font-headings:Georgia, serif',d.read_text())

if __name__=='__main__':unittest.main()
