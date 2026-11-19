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

    def instruction_setup(self):
        built = self.ctx / 'generated'
        shared = '# Working with Megan\n\n## Act\n\nAct on the current request.\n'
        for rel, extra in (('claude-code/CLAUDE.md', ''), ('codex/AGENTS.md', '\nStart every Codex chat in its project folder.\n')):
            path = built / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('<!-- MEGAN-AI-CONTEXT:BEGIN -->\n' + shared + extra + '<!-- MEGAN-AI-CONTEXT:END -->\n')
        home = Path(self.tmp.name) / 'home'
        (home / '.claude').mkdir(parents=True)
        (home / '.codex').mkdir(parents=True)
        (home / '.claude' / 'CLAUDE.md').write_text('<!-- MEGAN-OS:BEGIN -->\nOld rules.\n<!-- MEGAN-OS:END -->\n\n# Local notes\n\nKeep me.\n')
        return home

    def test_instructions_init_builds_both_hosts_from_one_source(self):
        home = self.instruction_setup()
        out = self.run_tool('instructions', '--init', '--home', str(home), '--json')
        self.assertEqual(out.returncode, 1, out.stderr)   # home files differ until installed
        source = (self.ctx / 'instructions.md').read_text()
        self.assertEqual(source.count('Act on the current request.'), 1)
        self.assertIn('<!-- only: codex -->', source)
        claude = (self.ctx / 'generated' / 'claude-code' / 'CLAUDE.md').read_text()
        codex = (self.ctx / 'generated' / 'codex' / 'AGENTS.md').read_text()
        self.assertIn('sources sha256', claude)
        self.assertNotIn('Codex chat', claude)
        self.assertIn('Start every Codex chat in its project folder.', codex)
        self.assertNotIn('only:', codex)
        self.assertEqual((home / '.claude' / 'CLAUDE.md').read_text().count('Old rules.'), 1)   # not installed

    def test_instructions_install_replaces_the_block_and_keeps_other_text(self):
        home = self.instruction_setup()
        self.run_tool('instructions', '--init', '--home', str(home))
        out = self.run_tool('instructions', '--install', '--home', str(home), '--json')
        self.assertEqual(out.returncode, 0, out.stderr)
        claude = (home / '.claude' / 'CLAUDE.md').read_text()
        self.assertNotIn('Old rules.', claude)
        self.assertNotIn('MEGAN-OS', claude)
        self.assertTrue(claude.startswith('<!-- MEGAN-AI-CONTEXT:BEGIN -->'))
        self.assertIn('# Local notes\n\nKeep me.', claude)
        codex = (home / '.codex' / 'AGENTS.md').read_text()
        self.assertIn('Start every Codex chat', codex)
        backups = sorted((self.agent / 'backups').glob('*.md'))
        self.assertTrue(any('Old rules.' in b.read_text() for b in backups))
        receipt = json.loads(sorted((self.agent / 'backups').glob('claude-code-*.json'))[0].read_text())
        self.assertEqual(receipt['target'], str(home / '.claude' / 'CLAUDE.md'))
        again = self.run_tool('instructions', '--install', '--home', str(home), '--json')
        self.assertFalse(any(row.get('receipt') for row in json.loads(again.stdout)['hosts'].values()))
        self.assertEqual(claude, (home / '.claude' / 'CLAUDE.md').read_text())

    def test_instructions_install_with_home_keeps_backups_under_that_home(self):
        home = self.instruction_setup()
        self.run_tool('instructions', '--init', '--home', str(home))
        env = {k: v for k, v in self.env.items() if k != 'WRITING_AGENT_HOME'}
        out = subprocess.run([sys.executable, str(TOOL), 'instructions', '--install', '--home', str(home), '--json'],
                             capture_output=True, text=True, env=env, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        receipt = json.loads(out.stdout)['hosts']['claude-code']['receipt']
        self.assertTrue(receipt.startswith(str(home / '.agents' / 'writing' / 'backups')), receipt)

    def test_instructions_check_finds_a_stale_build(self):
        home = self.instruction_setup()
        self.run_tool('instructions', '--init', '--home', str(home))
        source = self.ctx / 'instructions.md'
        source.write_text(source.read_text() + '\n## Finish\n\nState completion exactly.\n')
        result = json.loads(self.run_tool('check', '--json').stdout)
        self.assertIn(str(self.ctx / 'generated' / 'codex' / 'AGENTS.md'),
                      [o['path'] for o in result['outdated_copies']])

    def test_instructions_reject_an_unknown_host_block(self):
        (self.ctx / 'instructions.md').write_text('Shared.\n<!-- only: chatgpt -->x<!-- /only -->\n')
        out = self.run_tool('instructions', '--home', str(Path(self.tmp.name) / 'home'))
        self.assertNotEqual(out.returncode, 0)
        self.assertIn('unknown hosts: chatgpt', out.stderr)

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

    def test_build_mirrors_rules_word_for_word_and_check_finds_drift(self):
        mirror = Path(self.tmp.name) / 'Claude outputs' / 'chatgpt-writing-project'
        mirror.mkdir(parents=True)
        out = self.run_tool('build')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(len(json.loads(out.stdout)['mirrored']), 2)
        self.assertEqual((mirror / 'rules.md').read_text(), RULES)
        self.assertEqual((mirror / 'voice-profile.md').read_text(), '# Voice\n\nFirst person.\n')
        self.assertEqual(self.run_tool('check', '--living', str(self.living)).returncode, 0)
        (mirror / 'voice-profile.md').write_text('# Voice\n\nAn old copy.\n')
        bad = json.loads(self.run_tool('check', '--json', '--living', str(self.living)).stdout)
        self.assertEqual([c['path'] for c in bad['outdated_copies']], [str(mirror / 'voice-profile.md')])

    def test_build_skips_a_mirror_folder_that_does_not_exist(self):
        out = self.run_tool('build')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout)['mirrored'], [])
        self.assertFalse((Path(self.tmp.name) / 'Claude outputs').exists())

    def test_nightly_reports_weekly_counts(self):
        self.run_tool('build')
        (self.agent / 'hits.jsonl').write_text(json.dumps({'d': '2999-01-01', 'tool': 'codex', 'src': 'reply',
                                                           'rule': 'x'}) + '\n')
        (self.agent / 'gate.json').write_text(json.dumps({'include': [str(self.ctx) + '/nothing/*']}))
        (self.agent / 'state').mkdir()
        (self.agent / 'state' / 'keep-current.json').write_text(json.dumps(
            {'current': False, 'checked_at': '2026-11-16T14:00:00-05:00', 'main_version': '0.4.36',
             'errors': ['codex marketplace upgrade: offline'], 'actions': []}))
        out = self.run_tool('nightly', '--weekly', '--living', str(self.living))
        self.assertEqual(out.returncode, 0, out.stderr)
        report = json.loads(out.stdout)
        self.assertEqual(report['weekly']['hits_per_tool'], {'codex': 1})
        self.assertTrue(report['copies']['ok'])
        self.assertFalse(report['tools_current']['current'])
        self.assertEqual(report['tools_current']['errors'], ['codex marketplace upgrade: offline'])


if __name__ == '__main__':
    unittest.main(verbosity=1)
