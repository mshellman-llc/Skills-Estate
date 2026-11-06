"""Check discovery, capability selection and failure reporting without a browser."""
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import run_tests
import test_capabilities as capabilities


class RunnerTests(unittest.TestCase):
    def cases(self):
        calls=[]
        class Fixture(unittest.TestCase):
            def test_default(self):calls.append('default')
            @capabilities.integration('browser')
            def test_browser(self):calls.append('browser')
            @capabilities.integration('loopback')
            def test_loopback(self):calls.append('loopback')
        return list(run_tests.flatten(unittest.defaultTestLoader.loadTestsFromTestCase(Fixture))),calls

    def test_default_never_preflights_or_executes_integration_bodies(self):
        tests,calls=self.cases()
        with patch.object(run_tests,'preflight',side_effect=AssertionError('Unexpected preflight')):
            with patch.dict(os.environ,{capabilities.ENVIRONMENT_KEY:'browser,loopback'}):
                report,code=run_tests.run(tests,stream=io.StringIO())
                self.assertEqual(os.environ[capabilities.ENVIRONMENT_KEY],'browser,loopback')
        self.assertEqual(code,0);self.assertEqual(calls,['default'])
        self.assertEqual(report['status'],'passed_with_deferred')
        self.assertEqual(report['deferred_count'],2)
        self.assertEqual(report['executed'],1)

    def test_explicit_browser_preflight_failure_is_an_error_not_a_skip(self):
        tests,calls=self.cases()
        with patch.object(run_tests,'preflight',side_effect=RuntimeError('Synthetic missing runtime')):
            report,code=run_tests.run(tests,['browser'],stream=io.StringIO())
        self.assertEqual(code,2);self.assertEqual(calls,[])
        self.assertEqual(report['status'],'preflight_failed')
        self.assertIn('Synthetic missing runtime',report['error'])

    def test_selected_integration_runs_and_failure_is_preserved(self):
        calls=[]
        class Fixture(unittest.TestCase):
            @capabilities.integration('loopback')
            def test_failure(self):
                calls.append('selected')
                self.fail('Synthetic assertion failure')
        tests=list(run_tests.flatten(unittest.defaultTestLoader.loadTestsFromTestCase(Fixture)))
        report,code=run_tests.run(tests,['loopback'],stream=io.StringIO())
        self.assertEqual(calls,['selected']);self.assertEqual(code,1)
        self.assertEqual(report['failures'],1);self.assertEqual(report['deferred_count'],0)

    def test_explicit_browser_body_receives_preflight_runtime_without_launching(self):
        calls=[]
        class Fixture(unittest.TestCase):
            @capabilities.integration('browser')
            def test_browser(self):
                calls.append(os.environ.get('PW_MODULE'))
                self.assertEqual(os.environ['ESTATE_NODE_MODULES'],'/synthetic/node_modules')
                self.assertTrue(os.environ['NODE_PATH'].startswith('/synthetic/node_modules'))
        tests=list(run_tests.flatten(unittest.defaultTestLoader.loadTestsFromTestCase(Fixture)))
        runtime={'node':'/synthetic/node','module_root':'/synthetic/node_modules',
                 'playwright_entry':'file:///synthetic/playwright/index.mjs'}
        with patch.object(run_tests,'preflight',return_value=runtime),patch.object(capabilities,'preflight',return_value=runtime):
            report,code=run_tests.run(tests,['browser'],stream=io.StringIO())
        self.assertEqual(code,0);self.assertEqual(report['status'],'passed')
        self.assertEqual(calls,[runtime['playwright_entry']])

    def test_unexpected_skip_reports_incomplete_and_nonzero(self):
        class Fixture(unittest.TestCase):
            def test_skipped(self):self.skipTest('Synthetic unavailable capability')
        tests=list(run_tests.flatten(unittest.defaultTestLoader.loadTestsFromTestCase(Fixture)))
        report,code=run_tests.run(tests,stream=io.StringIO())
        self.assertEqual(code,1);self.assertEqual(report['status'],'incomplete')
        self.assertEqual(report['deferred_count'],0)
        self.assertEqual(report['other_skips'][0]['reason'],'Synthetic unavailable capability')

    def test_browser_dependency_probe_contains_no_launch_and_rejects_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);entry=base/'playwright/index.mjs';entry.parent.mkdir();entry.write_text('// Synthetic module')
            with patch.dict(os.environ,{'ESTATE_NODE':'/synthetic/node','ESTATE_NODE_MODULES':str(base)}):
                with patch.object(capabilities.subprocess,'run',return_value=subprocess.CompletedProcess([],1,'','missing executable')) as run:
                    with self.assertRaisesRegex(RuntimeError,'before launch'):
                        capabilities.preflight('browser')
                    script=run.call_args.args[0][3]
                    self.assertNotIn('.launch(',script)
                    self.assertIn('.executablePath()',script)

    def test_missing_node_is_a_preflight_failure(self):
        with patch.dict(os.environ,{},clear=True),patch.object(capabilities.shutil,'which',return_value=None):
            with self.assertRaisesRegex(RuntimeError,'Node is missing'):
                capabilities.preflight('browser')

    def test_duplicate_discovery_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            (base/'test_duplicate_fixture.py').write_text(
                'import unittest\nclass First(unittest.TestCase):\n def test_one(self):pass\nSecond=First\n')
            with self.assertRaisesRegex(ValueError,'Duplicate test IDs'):
                run_tests.collect(base)

    def test_repository_discovery_has_unique_ids_and_expected_integration_categories(self):
        tests=run_tests.collect()
        self.assertEqual(len(tests),len({test.id() for test in tests}))
        categories={run_tests.requirement(test) for test in tests}
        self.assertEqual(categories,{None,'browser','loopback','generated-map','skill-toolchain'})
        visual=[test for test in tests if test.__class__.__module__=='test_deck_visuals']
        self.assertEqual(len(visual),5)
        self.assertTrue(all(run_tests.requirement(test) is None for test in visual))
