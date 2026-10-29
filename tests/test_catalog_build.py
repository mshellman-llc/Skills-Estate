"""Exercise consolidated task packages away from their source tree."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import estate
from catalog import entries, dependencies, apply_entrypoint
from portable import assemble, runtime_closure


class CatalogBuildTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def module(self, name, body):
        path = self.root / 'skills' / name
        path.mkdir(parents=True)
        (path / 'SKILL.md').write_text(
            '---\nname: ' + name + '\ndescription: Exercise the named task.\n---\n\n' + body)
        return path

    def catalog(self, record):
        directory = self.root / 'config'
        directory.mkdir(exist_ok=True)
        (directory / 'skill-catalog.json').write_text(json.dumps(record))

    def test_renamed_task_retains_and_executes_merged_mode(self):
        self.module('primary', 'Produce the primary report.\n')
        mode = self.module('detail', 'Run [the renderer](scripts/render.py).\n')
        (mode / 'scripts').mkdir()
        (mode / 'scripts/render.py').write_text('print("the requested detail output")\n')
        self.module('internal', 'Keep the shared source method.\n')
        self.catalog({'format': 1, 'entries': {'clear-task': {
            'source': 'primary', 'pack': 'core', 'modes': {'detailed output': 'detail'}}},
            'internal': ['internal']})
        (self.root / '.local').mkdir()
        manifest = estate.build(self.root)
        package = self.root / 'build/skills/clear-task'
        self.assertEqual(set(manifest['packages']), {'clear-task'})
        self.assertIn('name: clear-task', (package / 'SKILL.md').read_text())
        self.assertIn('Produce the primary report.', (package / 'SKILL.md').read_text())
        self.assertIn('_runtime/detail/WORKFLOW.md', (package / 'SKILL.md').read_text())
        self.assertEqual(len(list(package.rglob('SKILL.md'))), 1)
        result = subprocess.run([sys.executable, str(package / '_runtime/detail/scripts/render.py')],
                                cwd=self.tmp.name, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'the requested detail output')
        before = manifest['packages']['clear-task']['sha256']
        (mode / 'scripts/render.py').write_text('print("revised detail output")\n')
        after = estate.build(self.root)['packages']['clear-task']['sha256']
        self.assertNotEqual(before, after)

    def test_catalog_cannot_silently_drop_a_source_module(self):
        self.module('primary', 'Keep this workflow.\n')
        self.module('unique', 'Keep this other workflow.\n')
        self.catalog({'format': 1, 'entries': {'task': {
            'source': 'primary', 'pack': 'core', 'modes': {}}}, 'internal': []})
        with self.assertRaisesRegex(ValueError, 'coverage differs'):
            estate.validate(self.root)

    def test_catalog_rejects_duplicate_source_ownership(self):
        self.module('primary', 'Keep the primary workflow.\n')
        self.module('detail', 'Keep the detail workflow.\n')
        cases = [
            ({'one': {'source': 'primary'}, 'two': {'source': 'primary'}}, ['detail']),
            ({'one': {'source': 'primary', 'modes': {'detail': 'detail'}},
              'two': {'source': 'detail'}}, []),
            ({'one': {'source': 'primary', 'modes': {'first': 'detail', 'second': 'detail'}}}, []),
            ({'one': {'source': 'primary', 'modes': {'detail': 'detail'}}}, ['detail']),
            ({'one': {'source': 'primary'}}, ['detail', 'detail']),
        ]
        for public, internal in cases:
            with self.subTest(entries=public, internal=internal):
                self.catalog({'format': 1, 'entries': public, 'internal': internal})
                with self.assertRaisesRegex(ValueError, 'Duplicate catalog owner'):
                    estate.validate(self.root)

    def test_maintenance_package_scaffolds_a_mode_and_preserves_existing_destination(self):
        item = entries(ROOT)['skill-estate-sync']
        package = self.root / 'maintenance'
        assemble(ROOT, item['source'], package, dependencies(ROOT, item, runtime_closure))
        apply_entrypoint(package, 'skill-estate-sync', item)
        self.assertEqual(len(list(package.rglob('SKILL.md'))), 1)
        mode = package / '_runtime/skill-creation-walkthrough'
        release = package / '_runtime/cross-platform-skill-release'
        self.assertTrue((release / 'references/estate-release.md').is_file())
        self.assertTrue((mode / 'references/governed-intake.md').is_file())
        workflow = self.root / 'workflow.md'
        workflow.write_text('Read the supplied rows. Write a CSV retaining each row and its source line.\n')
        project = self.root / 'project'
        project.mkdir()
        command = [sys.executable, str(mode / 'scripts/scaffold_skill.py'), 'source-rows',
            '--root', str(project), '--display-name', 'Source rows',
            '--description', 'Extract supplied source rows into a CSV.',
            '--owner', 'Project maintainer', '--category', 'analysis', '--runtime', 'codex',
            '--workflow', str(workflow)]
        created = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(created.returncode, 0, created.stderr)
        entry = project / 'skills/source-rows/SKILL.md'
        self.assertIn(workflow.read_text().strip(), entry.read_text())
        original = entry.read_bytes()
        refused = subprocess.run(command, cwd=self.root, capture_output=True, text=True)
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(entry.read_bytes(), original)

    def test_real_scope_package_runs_both_output_modes_without_siblings(self):
        item = entries(ROOT)['scope-options']
        package = self.root / 'scope-options'
        assemble(ROOT, item['source'], package, dependencies(ROOT, item, runtime_closure))
        apply_entrypoint(package, 'scope-options', item)
        self.assertEqual(len(list(package.rglob('SKILL.md'))), 1)
        static = self.root / 'comparison.html'
        result = subprocess.run([sys.executable, str(package / 'scripts/build_scope.py'),
            str(package / 'examples/comparison-source.json'),
            str(package / 'examples/comparison-plan.json'), str(static)],
            cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('USD 34,950.25', static.read_text())
        interactive = self.root / 'explorer.html'
        module = package / '_runtime/interactive-proposal'
        result = subprocess.run([sys.executable, str(module / 'scripts/build_proposal.py'),
            str(module / 'fixtures/explorer.json'), '--output', str(interactive)],
            cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(interactive.is_file())
        self.assertIn('explorer', interactive.read_text().lower())


if __name__ == '__main__':
    unittest.main()
