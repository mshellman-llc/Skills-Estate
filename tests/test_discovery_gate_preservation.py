"""Preserve installed discovery gate contracts at the isolated package boundary."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import catalog
from portable import assemble, runtime_closure

class DiscoveryGatePreservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name).resolve()
        cls.package = cls.base / 'discovery'
        item = catalog.entries(ROOT)['discovery']
        assemble(ROOT, item['source'], cls.package, catalog.dependencies(ROOT, item, runtime_closure))
        catalog.apply_entrypoint(cls.package, 'discovery', item)
        cls.gate = cls.package / '_runtime/discovery-brief/scripts/check_brief.py'
    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()
    def run_ledger(self, data):
        path = self.base / 'fictional-ledger.json'
        path.write_text(json.dumps(data))
        return subprocess.run([sys.executable, str(self.gate), str(path)], cwd=self.base, capture_output=True, text=True)
    def ledger(self):
        return {'known': [{'claim':'The speaker said “hold—then review.”','source':'fictional transcript line 2','confidence':'Inferred'}], 'open':[]}
    def test_explicit_completion_preserves_empty_question_state_and_quote_punctuation(self):
        data=self.ledger();data['discovery_complete']=True
        result=self.run_ledger(data)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_truthy_text_does_not_grant_completion(self):
        data=self.ledger();data['discovery_complete']='true'
        result=self.run_ledger(data)
        self.assertEqual(result.returncode,1);self.assertIn('Column B is empty',result.stdout)
    def test_malformed_open_rows_cannot_hide_behind_completion(self):
        data=self.ledger();data.update(discovery_complete=True,open=[17,None,'question'])
        result=self.run_ledger(data)
        self.assertEqual(result.returncode,1);self.assertIn('entries must be objects',result.stdout)
    def test_wrong_field_types_return_diagnostics_without_traceback(self):
        data={'known':[{'claim':17,'source':['s'],'confidence':True}],'open':[{'id':{},'question':44,'rank':[],'unblocks':False}]}
        result=self.run_ledger(data)
        self.assertEqual(result.returncode,1);self.assertIn('must be text',result.stdout);self.assertNotIn('Traceback',result.stderr)
    def test_unsourced_claim_and_unranked_question_remain_failures(self):
        data={'known':[{'claim':'Unsupported fact','source':'','confidence':'Unknown'}],'open':[{'question':'What is missing?','rank':'','unblocks':''}]}
        result=self.run_ledger(data)
        self.assertEqual(result.returncode,1);self.assertIn('no source token',result.stdout);self.assertIn('no scope line named',result.stdout)
    def test_packaged_selftest_executes_without_neighboring_checkout(self):
        result=subprocess.run([sys.executable,str(self.gate.with_name('check_brief_selftest.py'))],cwd=self.base,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=='__main__':unittest.main()
