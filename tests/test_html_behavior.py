"""Exercise HTML builders from portable packages outside the source checkout."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from portable import assemble
from estate import runtime_dependencies


class HtmlBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='estate-html-isolated-')
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name).resolve()
        self.env = {k:v for k,v in os.environ.items() if k not in ('SKILLS_BRAND_PROFILE','PYTHONPATH')}
        self.count = 0

    def command(self, *args):
        self.count += 1
        result = subprocess.run([sys.executable, *map(str,args)], cwd=self.home,
                                env=self.env, text=True, capture_output=True)
        (self.home/f'command-{self.count}.json').write_text(json.dumps({
            'args':list(map(str,args)), 'exit':result.returncode,
            'stdout':result.stdout, 'stderr':result.stderr},indent=2))
        return result

    def package(self, name):
        package = self.home/name
        assemble(ROOT, name, package, runtime_dependencies(name))
        return package

    def profile(self, **updates):
        import re
        p = json.loads(re.findall(r'```json\s*\n(.*?)\n```', (ROOT/'policies/brand.md').read_text(), re.S)[0])
        p.update(updates)
        path = self.home/'selected-brand.md'
        path.write_text('```json\n'+json.dumps(p)+'\n```\n')
        return path

    def test_field_guide_isolated_neutral_and_selected_profile(self):
        package = self.package('assess-solution-delivery')
        self.assertEqual(1,len(list(package.rglob('SKILL.md'))))
        builder=package/'scripts/build_field_guide.py'
        template=package/'assets/field-guide.body.html'
        output=self.home/'guide-neutral.html'
        result=self.command(builder,template,'--output',output)
        self.assertEqual(0,result.returncode,result.stderr)
        html=output.read_text()
        self.assertNotIn('ExampleCo',html)
        self.assertNotIn('__LOGO__',html)
        self.assertIn('--brand-accent:#37437D',html)
        self.assertIn('var rates=',html)
        colors={'background':'#FFFFFF','text':'#202020','muted':'#555555',
                'border':'#CCCCCC','surface':'#FAF4EC','accent':'#7B321A'}
        selected=self.profile(name='Copper example',colors=colors)
        result=self.command(builder,template,'--output',self.home/'guide-copper.html','--profile',selected)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertIn('--brand-accent:#7B321A',(self.home/'guide-copper.html').read_text())
        preflight=self.command(package/'_runtime/brand-renderer/scripts/runtime_preflight.py','--json')
        self.assertEqual(0,preflight.returncode,preflight.stdout+preflight.stderr)
        report=json.loads(preflight.stdout)
        for key in ('prose_check','prose_receipt','quality_gate','brand_check','asset_resolver'):
            self.assertTrue(Path(report[key]).is_relative_to(package),report[key])

    def test_declared_logo_embedded_and_missing_asset_rejected(self):
        package=self.package('assess-solution-delivery')
        logo=self.home/'example-logo.svg'
        logo.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="90" height="20"><text x="0" y="16">Example</text></svg>')
        selected=self.profile(logo='example-logo.svg')
        builder=package/'scripts/build_field_guide.py'
        template=package/'assets/field-guide.body.html'
        output=self.home/'with-logo.html'
        result=self.command(builder,template,'--output',output,'--profile',selected)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertIn('data:image/svg+xml;base64,',output.read_text())
        selected=self.profile(logo='does-not-exist.svg')
        result=self.command(builder,template,'--output',self.home/'missing.html','--profile',selected)
        self.assertNotEqual(0,result.returncode)
        self.assertFalse((self.home/'missing.html').exists())
        self.assertIn('missing',result.stderr)

    def test_call_brief_isolated_and_missing_input_rejected(self):
        package=self.package('prepare-sales-pursuit')
        data=json.loads((ROOT/'examples/prepare-sales-pursuit/synthetic-call.json').read_text())
        source=self.home/'call.json'; source.write_text(json.dumps(data))
        output=self.home/'call.html'
        result=self.command(package/'scripts/build_brief.py',package/'assets/brief-template.html',
                            '--data',source,'--output',output)
        self.assertEqual(0,result.returncode,result.stderr)
        self.assertNotIn('ExampleCo',output.read_text())
        self.assertIn('Example Manufacturing',output.read_text())
        del data['drill']; source.write_text(json.dumps(data))
        result=self.command(package/'scripts/build_brief.py',package/'assets/brief-template.html',
                            '--data',source,'--output',self.home/'invalid.html')
        self.assertNotEqual(0,result.returncode)
        self.assertFalse((self.home/'invalid.html').exists())
        self.assertIn('Missing interaction registry',result.stderr)

if __name__ == '__main__':
    unittest.main()
