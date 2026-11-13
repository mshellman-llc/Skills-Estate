#!/usr/bin/env python3
"""Self-test for writing_system.py against a temporary rules folder."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / 'writing_system.py'
PREFS = '# Preferences\n\n## Writing\n\n1. Open with the answer.\n2. Name the source.\n\n## Other\n\nNot this.\n'
RULES = '# Writing rules\n\n- R1. Open with the answer.\n- R16. Write no slogans.\n'
CORRECTIONS = ('| Date | What she corrected | Channel | Rule | Pattern | Tool |\n| --- | --- | --- | --- | --- | --- |\n'
               '| 2026-11-06 | "What good looks like:" as a coaching line | Call guide | R16 | none | ledger |\n'
               '| 2026-11-13 | R16 read as "every line needs a fact" | All | R16 | none | chat |\n')


class SystemTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.ctx = root / '05-ai-context'
        self.rules = self.ctx / 'writing'
        self.rules.mkdir(parents=True)
        (self.ctx / 'preferences.md').write_text(PREFS)
        (self.rules / 'rules.md').write_text(RULES)
        (self.rules / 'corrections.md').write_text(CORRECTIONS)
        (self.rules / 'voice-profile.md').write_text('# Voice\n\nFirst person.\n')
        (self.rules / 'patterns.json').write_text(json.dumps({'config': {}, 'rules': []}))
        (self.rules / 'retired-wording.json').write_text(json.dumps([{'text': 'Give every sentence a specific',
                                                                      'replaced_by': 'R5'}]))
        self.living = root / 'CLAUDE.md'
        self.living.write_text('3. Make each claim concrete.\n')
        self.agent = root / 'agent'
        self.agent.mkdir()
        self.env = dict(os.environ, WRITING_HOME=str(self.rules), WRITING_AGENT_HOME=str(self.agent))

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=self.env,
                              timeout=120)

    def test_build_writes_stamped_copies(self):
        out = self.run_tool('build')
        self.assertEqual(out.returncode, 0, out.stderr)
        core = (self.ctx / 'generated' / 'core' / 'core.md').read_text()
        self.assertIn('sources sha256', core)
        self.assertIn('Open with the answer', core)
        self.assertNotIn('Not this', core)
        self.assertIn('What good looks like:', core)
        self.assertNotIn('every line needs a fact', core)
        skill = (self.ctx / 'generated' / 'claude-ai-skill' / 'megan-writing-style' / 'SKILL.md').read_text()
        self.assertTrue(skill.startswith('---\nname: megan-writing-style'))
        self.assertIn('R16. Write no slogans', skill)
        self.assertIn('First person', skill)

    def test_chatgpt_boxes_fill_in_order_within_the_limits(self):
        many = '# Writing rules\n\n' + ''.join(f'- R{i}. Rule number {i} keeps one plain habit out of the copy.\n'
                                                 for i in range(1, 121))
        (self.rules / 'rules.md').write_text(many)
        (self.rules / 'voice-profile.md').write_text('# Voice\n\n- V1. Lead with the decision.\n')
        (self.ctx / 'chatgpt-about.md').write_text('---\nname: chatgpt-about\n---\n\nI am the owner.\n')
        out = self.run_tool('build')
        self.assertEqual(out.returncode, 0, out.stderr)
        left = json.loads(out.stdout)['chatgpt_left_out']
        text = (self.ctx / 'generated' / 'chatgpt' / 'custom-instructions.txt').read_text()
        box1 = text.split('=== Box 1: More about you ===')[1].split('=== Box 2')[0].strip()
        box2 = text.split('=== Box 2: Custom instructions ===')[1].strip()
        self.assertEqual(box1, 'I am the owner.')
        self.assertLessEqual(len(box2), 5000)
        self.assertIn('R1. Rule number 1 keeps', box2)
        kept = [i for i in range(1, 121) if f'R{i}. Rule number {i} keeps' in box2]
        self.assertEqual(kept, list(range(1, len(kept) + 1)))
        self.assertEqual(left, [f'R{i}' for i in range(len(kept) + 1, 121)] + ['V1'])
        outdated = json.loads(self.run_tool('check', '--json', '--living', str(self.living)).stdout)['outdated_copies']
        self.assertFalse([c for c in outdated if c['path'].endswith('custom-instructions.txt')])
        (self.ctx / 'chatgpt-about.md').write_text('x' * 1600)
        self.assertNotEqual(self.run_tool('build').returncode, 0)

    def test_check_passes_then_finds_drift(self):
        self.run_tool('build')
        ok = self.run_tool('check', '--living', str(self.living))
        self.assertEqual(ok.returncode, 0, ok.stdout)
        (self.rules / 'rules.md').write_text(RULES + '- R17. State the fact.\n')
        self.living.write_text('3. Give every sentence a specific: a name.\n')
        bad = self.run_tool('check', '--living', str(self.living), '--json')
        self.assertEqual(bad.returncode, 1)
        result = json.loads(bad.stdout)
        self.assertEqual(len(result['retired_wording']), 1)
        self.assertTrue(result['outdated_copies'])

    def test_nightly_reports_weekly_counts(self):
        self.run_tool('build')
        (self.agent / 'hits.jsonl').write_text(json.dumps({'d': '2999-01-01', 'tool': 'codex', 'src': 'reply',
                                                           'rule': 'x'}) + '\n')
        (self.agent / 'gate.json').write_text(json.dumps({'include': [str(self.ctx) + '/nothing/*']}))
        out = self.run_tool('nightly', '--weekly', '--living', str(self.living))
        self.assertEqual(out.returncode, 0, out.stderr)
        report = json.loads(out.stdout)
        self.assertEqual(report['weekly']['hits_per_tool'], {'codex': 1})
        self.assertTrue(report['copies']['ok'])


if __name__ == '__main__':
    unittest.main(verbosity=1)
