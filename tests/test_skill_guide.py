import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from skill_guide import load, assessment, overview_excerpt, readable_body, report
from catalog import source_names

class ReaderGuideTests(unittest.TestCase):
    def test_every_workflow_has_a_hash_bound_guide(self):
        guides = load(ROOT)
        names = source_names(ROOT)
        self.assertEqual(set(guides), names)
        for name, guide in guides.items():
            with self.subTest(name=name):
                for field in ('what','when','inputs','outputs','example'):
                    self.assertTrue(guide[field].strip())
                    self.assertNotIn('ESTATE-WRITING', guide[field])
                self.assertRegex(guide['reviewedEntrypointSha256'], r'^[a-f0-9]{64}$')

    def test_shared_workflow_no_longer_assigns_personal_ownership(self):
        original = load(ROOT)['journey-mapping']
        # Simulate a current review only in this fixture to isolate shared-policy
        # classification. The production review and its stale-hash gate stay intact.
        guide = dict(original, reviewedEntrypointSha256=hashlib.sha256(
            (ROOT/'skills/journey-mapping/SKILL.md').read_bytes()).hexdigest())
        a = assessment(ROOT, 'journey-mapping', guide, [])
        self.assertEqual(original, load(ROOT)['journey-mapping'])
        self.assertEqual(a['audience'], 'general')
        self.assertNotEqual(a['readiness'], 'review')
        self.assertFalse(any(h['path']=='policies/workflow.md' for h in a['sharedReferences']))
        self.assertIn('brand-renderer', json.loads((ROOT/'config/runtime-dependencies.json').read_text())['journey-mapping'])

    def test_external_context_workflows_are_not_bound_to_the_original_author(self):
        guides = load(ROOT)
        for name in ('career-application', 'call-prep', 'author-writing-style'):
            with self.subTest(name=name):
                current = dict(guides[name], reviewedEntrypointSha256=hashlib.sha256(
                    (ROOT/'skills'/name/'SKILL.md').read_bytes()).hexdigest())
                self.assertEqual(assessment(ROOT, name, current, [])['audience'], 'general')
                stale = dict(current, reviewedEntrypointSha256='0'*64)
                self.assertEqual(assessment(ROOT, name, stale, [])['audience'], 'review')

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
        for source in [ROOT/'skills'/name/'SKILL.md' for name in source_names(ROOT)]:
            with self.subTest(skill=source.parent.name):
                view=readable_body(source.read_text())
                self.assertNotIn('ESTATE-WRITING:',view)
                self.assertNotIn('> **Before writing:',view)

    def test_report_matches_current_sources(self):
        self.assertEqual((ROOT/'browse/reuse-review.md').read_text(),report(ROOT))

if __name__=='__main__':unittest.main()
