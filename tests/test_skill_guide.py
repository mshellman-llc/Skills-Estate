import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from skill_guide import load, assessment, overview_excerpt, readable_body, report

class ReaderGuideTests(unittest.TestCase):
    def test_every_workflow_has_a_hash_bound_guide(self):
        guides = load(ROOT)
        names = {p.parent.name for p in (ROOT/'skills').glob('*/SKILL.md')}
        self.assertEqual(set(guides), names)
        for name, guide in guides.items():
            with self.subTest(name=name):
                for field in ('what','when','inputs','outputs','example'):
                    self.assertTrue(guide[field].strip())
                    self.assertNotIn('ESTATE-WRITING', guide[field])
                self.assertRegex(guide['reviewedEntrypointSha256'], r'^[a-f0-9]{64}$')

    def test_shared_cleanup_is_visible_on_general_methods(self):
        a = assessment(ROOT, 'journey-mapping', load(ROOT)['journey-mapping'], [])
        self.assertEqual(a['audience'], 'general')
        self.assertEqual(a['readiness'], 'cleanup')
        self.assertTrue(any(h['path']=='policies/workflow.md' and 'Megan' in h['text'] for h in a['sharedReferences']))
        self.assertIn('brand-renderer', json.loads((ROOT/'config/runtime-dependencies.json').read_text())['journey-mapping'])

    def test_examples_and_personal_dependencies_are_distinct(self):
        guides=load(ROOT)
        a=assessment(ROOT,'call-prep',guides['call-prep'],[])
        self.assertEqual(a['audience'],'general')
        self.assertTrue(a['references'])
        self.assertTrue(all(h['kind']=='example-or-test' for h in a['references']))
        b=assessment(ROOT,'career-application',guides['career-application'],[])
        self.assertEqual(b['audience'],'megan')
        self.assertTrue(any(h['kind']=='workflow-or-reference' for h in b['references']))

    def test_overview_does_not_repeat_shared_writing_block(self):
        source='<!-- ESTATE-WRITING:BEGIN -->\nBefore writing, read the standard.\n<!-- ESTATE-WRITING:END -->\n\n# Test\n\n> **Before writing: build-card.md**\n\nThe task starts here.\n\n## Use\n\nUse it for this task.'
        result=overview_excerpt(source)
        self.assertEqual(result,['The task starts here.','Use it for this task.'])

    def test_changed_entrypoint_cannot_keep_a_reusable_label(self):
        guide=dict(load(ROOT)['journey-mapping'],reviewedEntrypointSha256='0'*64)
        a=assessment(ROOT,'journey-mapping',guide,[])
        self.assertEqual(a['audience'],'review')
        self.assertEqual(a['readiness'],'review')
        self.assertEqual(a['label'],'Needs review')

    def test_readable_instructions_hide_policy_blocks_and_keep_task_rules(self):
        source='<!-- ESTATE-WRITING:BEGIN -->\nRead the standard.\n<!-- ESTATE-WRITING:END -->\n\n# Task\n\n> **Before writing: build-card.md plus\n> readout-brief.md.**\n\nPreserve the customer’s approval conditions.\n\n```text\n<!-- a literal code example -->\n```'
        view=readable_body(source)
        self.assertNotIn('ESTATE-WRITING',view)
        self.assertNotIn('build-card.md',view)
        self.assertNotIn('# Task',view)
        self.assertIn('Preserve the customer’s approval conditions.',view)
        self.assertIn('<!-- a literal code example -->',view)

    def test_removing_a_route_preserves_the_substantive_rule_after_it(self):
        text='Before drafting, read [the build card](../_shared/build-card.md). Preserve exact scope and reconcile the authorized price.'
        self.assertEqual(readable_body(text),'Preserve exact scope and reconcile the authorized price.')

    def test_every_readable_entrypoint_omits_the_managed_preamble(self):
        for source in (ROOT/'skills').glob('*/SKILL.md'):
            with self.subTest(skill=source.parent.name):
                view=readable_body(source.read_text())
                self.assertNotIn('ESTATE-WRITING:',view)
                self.assertNotIn('> **Before writing:',view)

    def test_report_matches_current_sources(self):
        self.assertEqual((ROOT/'browse/reuse-review.md').read_text(),report(ROOT))

if __name__=='__main__':unittest.main()
