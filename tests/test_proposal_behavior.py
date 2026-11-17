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
from test_capabilities import integration


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

    def per_version_sources(self):
        data=json.loads((self.examples/'explorer.json').read_text())
        data['sources'].append({'id':'workshop','title':'Example scope workshop','reference':'WORKSHOP-EXAMPLE-002','revision':'2'})
        data['versions'][2]['scope_sections'][0]['items'][0]['source']='workshop'
        return data

    def test_shared_item_cites_each_versions_source(self):
        result,out=self.build(self.per_version_sources(),name='sources')
        self.assertEqual(0,result.returncode,result.stderr)
        html=out.read_text()
        self.assertIn('"_item_sources": {"R1": "workshop"',html)
        self.assertIn('"_item_sources": {"R1": "requirements"}',html)
        self.assertIn('v._item_sources[scope.id]',html)
        data=self.per_version_sources();data['versions'][2]['scope_sections'][0]['items'][0]['description']='Different promise.'
        result,out=self.build(data,name='conflict')
        self.assertNotEqual(0,result.returncode);self.assertIn('conflicting wording',result.stderr)

    def test_missing_inputs_replace_the_generic_line(self):
        data=json.loads((self.examples/'explorer.json').read_text())
        result,out=self.build(data,name='missing')
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertIn('"missing_inputs": [',out.read_text());self.assertIn('id="missing-section"',out.read_text())
        for value in ([],[''],'Price'):
            bad=copy.deepcopy(data);bad['missing_inputs']=value
            result,out=self.build(bad,name='bad-missing')
            self.assertNotEqual(0,result.returncode);self.assertFalse(out.exists())
        proposal=json.loads((self.examples/'proposal.json').read_text());proposal['missing_inputs']=['No rate card is supplied.']
        result,out=self.build(proposal,name='priced-missing',quote=json.loads((self.examples/'quote.json').read_text()))
        self.assertNotEqual(0,result.returncode);self.assertIn('missing_inputs belongs to explorer mode',result.stderr)

    def test_rendered_prose_gate_reads_the_page_not_its_code(self):
        result,out=self.build(json.loads((self.examples/'explorer.json').read_text()),name='prose')
        self.assertEqual(0,result.returncode,result.stderr)
        checker=self.package/'_runtime/writing-diagnostics/scripts/writing_check.py'
        rendered=subprocess.run([sys.executable,str(checker),'--rendered','--json',str(out)],capture_output=True,text=True)
        self.assertEqual(0,rendered.returncode,rendered.stdout+rendered.stderr)
        source=subprocess.run([sys.executable,str(checker),'--json',str(out)],capture_output=True,text=True)
        self.assertIn('Roadmap Kit v2 renderer',source.stdout)

    def test_browser_wrapper_runs_its_script_in_place(self):
        # A stand-in for Node records the script path; no browser starts.
        fake=self.folder/'fake-node';modules=self.folder/'modules/playwright';modules.mkdir(parents=True)
        (modules/'index.mjs').write_text('')
        fake.write_text('#!'+sys.executable+'\nimport json,pathlib,sys\nscript=pathlib.Path(sys.argv[1])\n'
                        'policy=script.parent.parent/"_runtime/brand-renderer/scripts/browser_launch_policy.cjs"\n'
                        'print(json.dumps({"checks":{"policy":policy.is_file()},"failures":[] if policy.is_file() else ["Browser policy is missing"],"script":str(script)}))\n')
        fake.chmod(0o755)
        page=self.folder/'wrapper.html';page.write_text('<!doctype html><title>t</title>')
        env={**os.environ,'ESTATE_NODE':str(fake),'ESTATE_NODE_MODULES':str(self.folder/'modules')}
        result=subprocess.run([sys.executable,str(self.package/'scripts/qa_proposal.py'),str(page),'--output',str(self.folder/'qa')],
                              cwd=self.folder,env=env,capture_output=True,text=True)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        report=json.loads(result.stdout[:result.stdout.rindex('Saved browser attempt')])
        self.assertEqual(str((self.package/'scripts/qa_proposal.mjs').resolve()),report['script'])
        self.assertEqual({'policy':True},report['checks'])

    @integration('browser')
    def test_fixture_explorer_passes_packaged_browser_qa(self):
        result,out=self.build(self.per_version_sources(),name='qa')
        self.assertEqual(0,result.returncode,result.stderr)
        qa=subprocess.run([sys.executable,str(self.package/'scripts/qa_proposal.py'),str(out),'--output',str(self.folder/'qa')],
                          cwd=self.folder,capture_output=True,text=True,timeout=300)
        self.assertEqual(0,qa.returncode,qa.stdout+qa.stderr)
        report=json.loads(qa.stdout[:qa.stdout.rindex('Saved browser attempt')])
        self.assertEqual([],report['failures'])
        self.assertTrue(report['checks']['C source R1']);self.assertTrue(report['checks']['A no generic confirmation line'])
        texts={view['version']:view['text'] for view in report['views'] if view['width']!=390}
        card='Route requests into one queue with a named owner.\n\nSource: '
        self.assertIn(card+'Example scope workshop',texts['C']);self.assertIn(card+'Example requirements',texts['B'])

if __name__=='__main__':unittest.main()
