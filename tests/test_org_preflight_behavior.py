"""Exercise preflight through isolated packages and a simulated Salesforce CLI."""
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
ORG='00D000000000001EAA'
OTHER='00D000000000002EAA'

class OrgTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='estate-org-preflight-')
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.package=self.folder/'org-preflight'
        assemble(ROOT,'org-preflight',self.package,runtime_dependencies('org-preflight'))
        self.cli=self.folder/'simulated-sf'
        self.cli.write_text('#!'+sys.executable+'\n'+'''import json, pathlib, sys
root=pathlib.Path(__file__).parent
(root/'invocation.json').write_text(json.dumps(sys.argv[1:]))
case=json.loads((root/'cli-response.json').read_text())
print(case['stdout'])
print(case.get('stderr',''),file=sys.stderr)
sys.exit(case['exit'])
''')
        self.cli.chmod(0o755)

    def response(self,org=ORG,sandbox=True):
        return {'status':0,'result':{'records':[{'Id':org,'Name':'Synthetic Test Org','IsSandbox':sandbox,'InstanceName':'TEST1'}]}}

    def run_gate(self,*args,name='attempt',payload=None,exit_code=0):
        receipt=self.folder/(name+'.json')
        if payload is not None:
            (self.folder/'cli-response.json').write_text(json.dumps({'exit':exit_code,'stdout':json.dumps(payload),'stderr':'SECRET_DIAGNOSTIC'}))
        command=[sys.executable,str(self.package/'scripts/preflight.py'),*args,'--receipt',str(receipt)]
        result=subprocess.run(command,cwd=self.folder,text=True,capture_output=True)
        (self.folder/(name+'.console.log')).write_text(result.stdout+result.stderr)
        return result,json.loads(receipt.read_text())

    def test_live_cli_query_binds_explicit_connection_and_exact_id(self):
        result,receipt=self.run_gate('--target-org','chosen-test','--sf',str(self.cli),'--expect',ORG,payload=self.response())
        self.assertEqual(0,result.returncode,result.stdout)
        self.assertEqual('live-cli-query',receipt['evidenceMode'])
        self.assertFalse(receipt['writePerformed']);self.assertFalse(receipt['authorizationGranted'])
        argv=json.loads((self.folder/'invocation.json').read_text())
        self.assertEqual(['data','query','--target-org','chosen-test','--query','SELECT Id, Name, IsSandbox, InstanceName FROM Organization','--json'],argv)

    def test_missing_org_does_not_invoke_cli_or_choose_default(self):
        result,receipt=self.run_gate('--sf',str(self.cli),'--expect',ORG)
        self.assertEqual(2,result.returncode)
        self.assertEqual('refused',receipt['state'])
        self.assertFalse((self.folder/'invocation.json').exists())

    def test_wrong_identity_and_kind_only_targets_refuse(self):
        for name,expected in [('wrong',OTHER),('kind','sandbox')]:
            result,receipt=self.run_gate('--target-org','chosen-test','--sf',str(self.cli),'--expect',expected,name=name,payload=self.response())
            self.assertEqual(2,result.returncode);self.assertEqual('refused',receipt['state'])

    def test_bad_cli_responses_and_failures_do_not_leak_diagnostics(self):
        cases=[({'status':1},0),({'result':{'records':[]}},0),(self.response(sandbox='false'),0),([],0),(self.response(),1)]
        for n,(payload,code) in enumerate(cases):
            result,receipt=self.run_gate('--target-org','chosen-test','--sf',str(self.cli),'--expect',ORG,name='bad'+str(n),payload=payload,exit_code=code)
            self.assertEqual(2,result.returncode);self.assertEqual('refused',receipt['state'])
            self.assertNotIn('SECRET_DIAGNOSTIC',result.stdout+result.stderr+json.dumps(receipt))

    def test_connector_evidence_is_not_mislabeled_live(self):
        evidence=self.folder/'source.json';evidence.write_text(json.dumps(self.response()))
        result,receipt=self.run_gate('--identity-json',str(evidence),'--expect',ORG[:15])
        self.assertEqual(0,result.returncode,result.stdout)
        self.assertEqual('caller-supplied-query-response',receipt['evidenceMode'])
        self.assertEqual(64,len(receipt['evidenceSha256']))

    def test_duplicate_registry_aliases_and_malformed_registry_refuse(self):
        for n,data in enumerate([[],{'orgs':[]},{'orgs':{ORG:{'alias':'test','kind':'sandbox'},OTHER:{'alias':'TEST','kind':'sandbox'}}}]):
            registry=self.folder/('registry'+str(n)+'.json');registry.write_text(json.dumps(data))
            result,_=self.run_gate('--live-id',ORG,'--is-sandbox','true','--expect',ORG,'--registry',str(registry),name='registry-check'+str(n))
            self.assertEqual(2,result.returncode)

    def test_production_acknowledgment_is_separate_from_authorization(self):
        for n,extra in enumerate([[],['--allow-production']]):
            result,receipt=self.run_gate('--live-id',ORG,'--is-sandbox','false','--expect',ORG,*extra,name='prod'+str(n))
            self.assertEqual(2 if n==0 else 0,result.returncode)
            self.assertFalse(receipt['authorizationGranted'])

    def test_bad_id_lengths_refuse(self):
        for size in (14,16,17,19):
            result,_=self.run_gate('--live-id','00D'+'0'*(size-3),'--is-sandbox','true','--expect',ORG,name='length'+str(size))
            self.assertEqual(2,result.returncode)

    def test_receipt_is_not_overwritten(self):
        result,receipt=self.run_gate('--live-id',ORG,'--is-sandbox','true','--expect',ORG)
        before=(self.folder/'attempt.json').read_bytes()
        result,_=self.run_gate('--live-id',OTHER,'--is-sandbox','true','--expect',OTHER)
        self.assertEqual(2,result.returncode)
        self.assertEqual(before,(self.folder/'attempt.json').read_bytes())

if __name__=='__main__':unittest.main()
