#!/usr/bin/env python3
"""Review regressions. The kit case requires the standalone package; a runtime
WORKFLOW.md is not an installable writing-integrity ZIP. Other cases run in both forms.
All profiles and kits are disposable.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
import zipfile
import learning
import build_kit
from learning_selftest import review

HERE=Path(__file__).resolve().parents[1]

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.store=learning.Store(self.root/'store',create=True);self.addCleanup(self.store.close)
        self.store.init('Example owner','example','codex','session',True)

    def bundle(self,rules):
        payload={'version':1,'owner':'Example owner','profile':'example','created':'2026-10-28','rules':rules,'events':[]}
        return {'payload':payload,'sha256':learning.digest(payload)}

    def rule(self):
        return {'id':'synthetic-rule','pattern':'direct-claim','scope':'general','scope_id':'',
                'instruction':'State the result directly.','exception':'','tags':['general'],
                'evidence':[],'revision':1,'status':'active'}

    def test_disabled_learning_rejects_checkpoints_and_dismissal(self):
        self.store.init('Example owner','example','codex','session',False)
        for operation in [lambda: self.store.finish(None,'test-session'), lambda: self.store.dismiss(None,'missing','Ignore this example.')]:
            with self.assertRaisesRegex(ValueError,'Learning is not enabled'):operation()
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM finishes').fetchone()[0],0)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM reviews').fetchone()[0],0)

    def test_capture_and_import_reject_invalid_project_and_tags(self):
        event={'id':'synthetic-event','session':'test-session','pattern':'direct-claim','host':'codex','kind':'user-correction',
               'before':'The result? Saved.','after':'The file is saved.','reason':'State the outcome.','source_ref':'Synthetic test.',
               'project':'','tags':['general'],'created':'2026-10-28'}
        cases=[{'project':bad} for bad in [None,0,[],{},'invalid project']] + [{'tags':bad} for bad in [None,[],['Invalid Tag'],42]]
        for change in cases:
            with self.subTest(change=change):
                incoming=dict(event,**change)
                with self.assertRaises(ValueError):self.store.capture(None,incoming)
                bundle=self.bundle([]);bundle['payload']['events']=[incoming];bundle['sha256']=learning.digest(bundle['payload'])
                with self.assertRaises(ValueError):self.store.import_data(None,bundle,'Example owner')
                self.assertEqual(self.store.status()['events'],0)
                self.assertEqual(self.store.transfers(),[])

    def test_deep_json_cli_returns_error_without_traceback_or_output(self):
        source=self.root/'nested.json';source.write_text('['*2000+'0'+']'*2000);output=self.root/'nested-out.json'
        result=subprocess.run(['/usr/bin/python3',str(HERE/'scripts/learning.py'),'--store',str(self.root/'store'),'seal',str(source),'--out',str(output)],capture_output=True,text=True)
        self.assertEqual(result.returncode,2);self.assertNotIn('Traceback',result.stderr);self.assertFalse(output.exists())

    def test_non_object_rule_rejects_whole_import(self):
        for bad in [None,[],True,42,'rule']:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):self.store.import_data(None,self.bundle([self.rule(),bad]),'Example owner')
                self.assertEqual(self.store.transfers(),[])
                self.assertEqual(self.store.status()['active_rules'],0)

    def test_non_object_seal_returns_exit_two_without_traceback_or_output(self):
        for number,bad in enumerate([[],None,7,'payload',{'payload':[]},{'payload':None}]):
            with self.subTest(bad=bad):
                source=self.root/f'bad-{number}.json';source.write_text(json.dumps(bad));output=self.root/f'out-{number}.json'
                result=subprocess.run(['/usr/bin/python3',str(HERE/'scripts/learning.py'),'--store',str(self.root/'store'),'seal',str(source),'--out',str(output)],capture_output=True,text=True)
                self.assertEqual(result.returncode,2);self.assertNotIn('Traceback',result.stderr);self.assertFalse(output.exists())

    def test_sealed_owner_string_cannot_activate_without_confirmation(self):
        imported=self.store.import_data(None,self.bundle([self.rule()]),'Example owner')
        proposal=self.rule();proposal['review']=review('owner-transfer');proposal['review']['transfer_id']=imported['transfer_id']
        with self.assertRaises(ValueError):self.store.promote(None,proposal)
        self.assertEqual(self.store.status()['active_rules'],0)

    def test_confirmation_and_limits_survive_in_activation_record(self):
        imported=self.store.import_data(None,self.bundle([self.rule()]),'Example owner')
        self.assertFalse(imported['owner_provenance']['identity_verified'])
        proposal=self.rule();proposal['review']=review('owner-transfer');proposal['review']['transfer_id']=imported['transfer_id']
        proposal['review']['owner_confirmation']={'statement':'The synthetic owner asked to adopt this supplied profile.','source_ref':'Synthetic request, test fixture.'}
        result=self.store.promote(None,proposal)
        provenance=result['rule']['owner_provenance'];self.assertFalse(provenance['identity_verified'])
        self.assertEqual(provenance['confirmation'],proposal['review']['owner_confirmation'])
        logged=json.loads(self.store.db.execute('SELECT body FROM reviews WHERE action="activate"').fetchone()['body'])
        self.assertEqual(logged['owner_provenance'],provenance)

    @unittest.skipUnless((HERE / 'SKILL.md').is_file(),
                         'Setup-kit fixture requires the standalone writing-integrity package')
    def test_library_uses_checked_zip_even_when_source_reference_changes(self):
        mirror=self.root/'source';shutil.copytree(HERE,mirror,ignore=shutil.ignore_patterns('__pycache__'))
        package=self.root/'skill.zip'
        with zipfile.ZipFile(package,'w') as archive:
            for file in mirror.rglob('*'):
                if file.is_file():archive.write(file,str(Path('writing-integrity')/file.relative_to(mirror)))
        reference=mirror/'references/patterns.md';original=reference.read_text();reference.write_text(original+'\nUNVERIFIED SOURCE SENTINEL\n')
        previous=build_kit.HERE;build_kit.HERE=mirror
        try:build_kit.build(package,self.root/'kit','Example owner','example')
        finally:build_kit.HERE=previous
        library=(self.root/'kit/review-library.md').read_text()
        self.assertIn('Sentence patterns',library);self.assertNotIn('UNVERIFIED SOURCE SENTINEL',library)
        manifest=json.loads((self.root/'kit/manifest.json').read_text())
        self.assertEqual(manifest['skill_zip_sha256'],hashlib.sha256(package.read_bytes()).hexdigest())

if __name__=='__main__':unittest.main(verbosity=2)
