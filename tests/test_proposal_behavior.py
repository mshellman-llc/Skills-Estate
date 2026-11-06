"""Portable proposal generation with source mismatches and unsafe inputs."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from portable import assemble
from estate import runtime_dependencies


class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='estate-proposal-isolated-')
        self.addCleanup(self.temp.cleanup);self.folder=Path(self.temp.name).resolve()
        self.package=self.folder/'build-interactive-proposal'
        assemble(ROOT,'build-interactive-proposal',self.package,runtime_dependencies('build-interactive-proposal'))
        self.examples=ROOT/'examples/build-interactive-proposal'

    def build(self,data,name='page',quote=None):
        source=self.folder/(name+'.json');source.write_text(json.dumps(data))
        out=self.folder/(name+'.html')
        args=[sys.executable,str(self.package/'scripts/build_proposal.py'),str(source),'--output',str(out)]
        if quote is not None:
            qp=self.folder/(name+'.quote.json');qp.write_text(json.dumps(quote));args+=['--quote',str(qp)]
        result=subprocess.run(args,cwd=self.folder,env={k:v for k,v in os.environ.items() if k!='SKILLS_BRAND_PROFILE'},text=True,capture_output=True)
        (self.folder/(name+'.console.log')).write_text(result.stdout+result.stderr)
        return result,out

    def test_both_modes_build_from_isolated_package(self):
        for mode in ('explorer','proposal'):
            data=json.loads((self.examples/(mode+'.json')).read_text())
            quote=json.loads((self.examples/'quote.json').read_text()) if mode=='proposal' else None
            result,out=self.build(data,name=mode,quote=quote)
            self.assertEqual(0,result.returncode,result.stderr)
            html=out.read_text()
            self.assertIn('<main>',html);self.assertIn('--brand-accent:',html)
            self.assertNotIn('__LOGO__',html)
            self.assertTrue(out.with_suffix('.build.json').exists())

    def test_wrong_quote_amount_or_scope_is_rejected(self):
        quote=json.loads((self.examples/'quote.json').read_text())
        for kind in ('total','scope'):
            data=json.loads((self.examples/'proposal.json').read_text())
            if kind=='total':data['versions'][0]['total']+=1
            else:data['versions'][0]['scope_sections'][0]['items'][0]['description']='Different promise.'
            result,out=self.build(data,name=kind,quote=quote)
            self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())

    def test_explorer_rejects_currency_and_unconfirmed_staffing(self):
        for key,value in [('total',10),('team',[]),('duration_weeks',2),('tagline','Costs $100')]:
            data=json.loads((self.examples/'explorer.json').read_text());data['versions'][0][key]=value
            result,out=self.build(data,name=key)
            self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())

    def test_explorer_count_is_recomputed_from_unique_ids(self):
        data=json.loads((self.examples/'explorer.json').read_text());data['versions'][0]['metric']=99
        result,out=self.build(data)
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        self.assertIn('count of distinct included scope IDs',result.stderr)

    def test_excluded_item_requires_a_route(self):
        data=json.loads((self.examples/'explorer.json').read_text());data['versions'][0]['not_included']=[]
        result,out=self.build(data)
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        self.assertIn('Excluded scope needs a route',result.stderr)

    def test_source_markup_stays_in_json(self):
        data=json.loads((self.examples/'explorer.json').read_text());data['meta']['client']='</script><script>alert(1)</script>'
        result,out=self.build(data)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertNotIn('</script><script>alert(1)',out.read_text())
        self.assertIn('\\u003c/script\\u003e',out.read_text())

    def test_duplicate_version_is_rejected(self):
        data=json.loads((self.examples/'explorer.json').read_text());data['versions'].append(copy.deepcopy(data['versions'][0]))
        result,out=self.build(data)
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())

    def test_ambiguous_quote_and_invalid_financial_metadata_are_rejected(self):
        for kind in ('duplicate','currency','duration','team','timeline'):
            data=json.loads((self.examples/'proposal.json').read_text())
            quote=json.loads((self.examples/'quote.json').read_text())
            if kind=='duplicate':
                quote['versions'].append(copy.deepcopy(quote['versions'][0]))
            elif kind=='currency':
                data['meta']['currency']=quote['currency']='dollars'
            else:
                field='duration_weeks' if kind=='duration' else kind
                value=float('inf') if kind=='duration' else []
                data['versions'][0][field]=quote['versions'][0][field]=value
            result,out=self.build(data,name=kind,quote=quote)
            self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())

    def test_scope_ids_are_safe_for_dom_lookup(self):
        data=json.loads((self.examples/'explorer.json').read_text())
        data['versions'][0]['scope_sections'][0]['items'][0]['id']='broken"]'
        result,out=self.build(data)
        self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        self.assertIn('Scope IDs',result.stderr)

if __name__=='__main__':unittest.main()
