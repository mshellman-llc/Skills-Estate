"""Behavioral checks for bounded retirement prerequisites; never use live services."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from catalog import entries,dependencies,apply_entrypoint
from portable import assemble,runtime_closure

class RemainingRepairs(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)

    def docx(self,body,extra=None):
        path=self.base/'source.docx'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+body+'</w:body></w:document>')
            for name,text in (extra or {}).items():z.writestr(name,text)
        return path

    def scanner(self):
        package=self.base/'contract'
        item=entries(ROOT)['statement-of-work']
        assemble(ROOT,item['source'],package,dependencies(ROOT,item,runtime_closure))
        apply_entrypoint(package,'statement-of-work',item)
        return package/'_runtime/sow-quality/scripts/slop_scan.py'

    def run_scan(self,script,path,*args):
        return subprocess.run([sys.executable,str(script),str(path),*args],cwd=self.base,
            env={**os.environ,'PATH':''},capture_output=True,text=True)

    def test_packaged_docx_extracts_split_runs_tables_and_header_without_external_binary(self):
        script=self.scanner()
        phrase='bills as the lower actual effort'
        path=self.docx('<w:p><w:r><w:t>| Literal prose remains.</w:t></w:r></w:p>'
            '<w:p><w:r><w:t>bills as the lower </w:t></w:r><w:r><w:t>actual effort</w:t></w:r></w:p>'
            '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>'+phrase+'</w:t></w:r></w:p></w:tc></w:tr></w:tbl>',
            {'word/header1.xml':'<w:hdr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>Contract header</w:t></w:r></w:p></w:hdr>'})
        before=path.read_bytes();result=self.run_scan(script,path,'--text')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout.count(phrase),2)
        self.assertIn('| Literal prose remains.',result.stdout);self.assertIn('Contract header',result.stdout)
        result=self.run_scan(script,path,'--verify')
        self.assertEqual(result.returncode,1,result.stderr);self.assertIn('2x  '+phrase,result.stdout)
        self.assertEqual(path.read_bytes(),before)

    def test_diagnostic_pass_is_distinct_from_extraction_failure(self):
        script=self.scanner();path=self.docx('<w:p><w:r><w:t>Client Lead retains the confirmed 10-hour scope cap.</w:t></w:r></w:p>')
        result=self.run_scan(script,path,'--verify');self.assertEqual(result.returncode,0,result.stderr)
        result=self.run_scan(script,path,'--text');self.assertIn('Client Lead',result.stdout);self.assertIn('10-hour',result.stdout)
        for content in [b'not a zip',b'']:
            path.write_bytes(content);result=self.run_scan(script,path,'--verify')
            self.assertNotEqual(result.returncode,0);self.assertNotIn('PASS',result.stdout);self.assertIn('Could not extract',result.stderr)
        self.docx('<w:p/>');result=self.run_scan(script,path,'--verify');self.assertNotEqual(result.returncode,0);self.assertIn('no readable Word text',result.stderr)

    def test_table_candidates_do_not_displace_prose_review(self):
        script=self.scanner();spec=importlib.util.spec_from_file_location('contract_scan',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        path=self.docx('<w:p><w:r><w:t>| A real paragraph.</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Table amount 2000</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
        full,prose=module.get_text(path);self.assertIn('Table amount 2000',full);self.assertNotIn('Table amount',prose);self.assertIn('| A real paragraph.',prose)

    def test_word_hyphens_and_symbols_cannot_silently_disappear(self):
        script=self.scanner()
        path=self.docx('<w:p><w:r><w:t>Confirmed 10</w:t><w:noBreakHyphen/>'
            '<w:t>hour cap. Re</w:t><w:softHyphen/><w:t>view Section </w:t>'
            '<w:sym w:font="Arial" w:char="00A7"/><w:t>4.</w:t></w:r></w:p>')
        result=self.run_scan(script,path,'--text')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('10\u2011hour',result.stdout);self.assertIn('Re\u00adview',result.stdout)
        self.assertIn('Section \u00a74.',result.stdout)
        result=self.run_scan(script,path,'--verify')
        self.assertEqual(result.returncode,1);self.assertIn('section-sign: 1',result.stdout)
        for font,char in [('Wingdings','F0A7'),('Arial','F0A7'),('Arial','not-hex')]:
            self.docx('<w:p><w:r><w:t>Obligation </w:t><w:sym w:font="'+font+'" w:char="'+char+'"/></w:r></w:p>')
            result=self.run_scan(script,path,'--verify')
            self.assertNotEqual(result.returncode,0);self.assertIn('unmappable Word symbol',result.stderr)
            self.assertNotIn('PASS',result.stdout)
        self.docx('<w:p><w:r><w:t>bills as the lower actual effort</w:t></w:r></w:p>'
            '<w:p><w:r><w:t>bills as the lower actual ef</w:t><w:softHyphen/>'
            '<w:t>fort</w:t></w:r></w:p>')
        before=path.read_bytes()
        result=self.run_scan(script,path,'--text');self.assertIn('ef\u00adfort',result.stdout)
        result=self.run_scan(script,path,'--verify')
        self.assertEqual(result.returncode,1);self.assertIn('2x  bills as the lower actual effort',result.stdout)
        self.assertEqual(path.read_bytes(),before)

    def test_planner_current_routes_resolve_without_changing_legacy_contract(self):
        # Compare with outputs captured from the prior real planner. The
        # fixture retains source provenance but needs no Git history at runtime.
        fixture=json.loads((ROOT/'tests/fixtures/playbook-plan-legacy.json').read_text())
        catalog=entries(ROOT)
        seen=set()
        for case in fixture['cases']:
            source=self.base/'manifest.json';source.write_text(json.dumps(case['input']))
            before=case['output']
            after=json.loads(subprocess.check_output([sys.executable,
                str(ROOT/'skills/playbook-suite/scripts/plan.py'),str(source)],cwd=self.base))
            for step in after['steps']:
                seen.add(step['artifact'])
                route=step['invocation']
                if route['skill'] is not None:
                    self.assertIn(route['skill'],catalog)
                    self.assertIn(route['mode'],['primary',*catalog[route['skill']].get('modes',{})])
                else:self.assertEqual(step['artifact'],9)
                del step['invocation']
            if after['next_step']:del after['next_step']['invocation']
            authority=after.pop('spec_authority')
            self.assertEqual(authority['status'],'unverified')
            self.assertFalse(authority['release_ready'])
            self.assertEqual(authority['checked_rules_version'],after['spec_version'])
            self.assertIn('stage_gate_workbook',authority['required_inputs'])
            self.assertEqual(before,after)
        self.assertEqual(seen,set(range(1,11)))

    def test_org_command_examples_require_explicit_targets(self):
        folder=ROOT/'skills/dx-devops-work-item-manage'
        count=0
        for path in [folder/'SKILL.md',folder/'references/cli-commands.md',folder/'examples/common-workflows.md']:
            text=path.read_text();self.assertNotIn('--set-default',text)
            for block in re.findall(r'```(?:bash|sh)\n(.*?)```',text,re.S):
                logical=re.sub(r'\\\n\s*',' ',block)
                for line in logical.splitlines():
                    if re.search(r'\bsf (?:org display|devops)\b',line) and '--json' in line:
                        count+=1;self.assertIn('--target-org',line,(str(path),line))
        self.assertGreater(count,30)

if __name__=='__main__':unittest.main()
