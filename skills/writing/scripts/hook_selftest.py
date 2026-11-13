#!/usr/bin/env python3
"""Self-test for hook.py. Runs the hook as Claude Code and Codex would, against a temporary rules folder."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOK = HERE / 'hook.py'
CLEAN = ('The renewal report lists every account due in March with its owner and amount. '
         'Finance reads it on Monday and approves the forecast for each account before the call. '
         'Sales updates the close dates in the tracker the same day, and the team checks the totals twice.')
BAD = CLEAN + ' We delve into the forecast.'


class HookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.rules, self.home, self.work = root / 'rules', root / 'agent', root / 'work'
        for d in (self.rules, self.home, self.work):
            d.mkdir()
        (self.rules / 'rules.md').write_text('# Rules\n\n- R25. Use the plain word.\n')
        (self.rules / 'registers.md').write_text('# Registers\n\n### megan\n\nHer own voice.\n')
        (self.rules / 'patterns.json').write_text(json.dumps({
            'config': {'min_words': 40, 'hard_weight': 3, 'flag_density': 4},
            'rules': [{'id': 'delve', 'class': 'vocabulary', 'scope': 'general', 'status': 'active', 'weight': 3,
                       'pattern': r'\bdelve\b', 'repair': 'Say what you examine.'}]}))
        (self.home / 'gate.json').write_text(json.dumps({'include': [str(self.work) + '/*'], 'exclude': []}))
        self.env = dict(os.environ, WRITING_HOME=str(self.rules), WRITING_AGENT_HOME=str(self.home),
                        WRITING_RECEIPTS=str(self.home / 'receipts'))

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, event, tool='claude-code'):
        out = subprocess.run([sys.executable, str(HOOK), '--tool', tool], input=json.dumps(event),
                             capture_output=True, text=True, env=self.env, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        return json.loads(out.stdout) if out.stdout.strip() else None

    def stop(self, message, active=False, session='s1'):
        return self.run_hook({'hook_event_name': 'Stop', 'session_id': session,
                              'last_assistant_message': message, 'stop_hook_active': active})

    def test_clean_reply_passes(self):
        self.assertIsNone(self.stop(CLEAN))

    def test_blocking_reply_is_held_once(self):
        out = self.stop(BAD)
        self.assertEqual(out['decision'], 'block')
        self.assertIn('delve', out['reason'])
        self.assertIsNone(self.stop(BAD, active=True))
        carried = self.run_hook({'hook_event_name': 'UserPromptSubmit', 'session_id': 's1', 'prompt': 'next'})
        self.assertIn('delve', carried['hookSpecificOutput']['additionalContext'])

    def test_hits_record_the_tool(self):
        self.stop(BAD)
        line = (self.home / 'hits.jsonl').read_text().splitlines()[0]
        self.assertEqual(json.loads(line)['tool'], 'claude-code')

    def test_file_write_is_scanned(self):
        path = self.work / 'note.md'
        path.write_text(BAD)
        out = self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 's2', 'tool_name': 'Write',
                             'tool_input': {'file_path': str(path)}})
        self.assertEqual(out['decision'], 'block')

    def test_gate_holds_an_unreviewed_deliverable_then_releases(self):
        path = self.work / 'page.html'
        path.write_text('<p>' + CLEAN + '</p>')
        self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 's3', 'tool_name': 'Write',
                       'tool_input': {'file_path': str(path)}})
        out = self.stop(CLEAN, session='s3')
        self.assertEqual(out['decision'], 'block')
        self.assertIn('page.html', out['reason'])
        receipts = self.home / 'receipts'
        receipts.mkdir()
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        steps = [{'step': s, 'status': 'ok'} for s in ('line pass', 'document pass', 'spot audit')]
        (receipts / 'r.json').write_text(json.dumps({'sha256': sha, 'status': 'pass', 'steps': steps}))
        self.assertIsNone(self.stop(CLEAN, session='s3'))

    def test_gate_releases_after_the_block_limit(self):
        path = self.work / 'doc.md'
        path.write_text(CLEAN)
        self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 's4', 'tool_name': 'Edit',
                       'tool_input': {'file_path': str(path)}})
        self.assertEqual(self.stop(CLEAN, session='s4')['decision'], 'block')
        self.assertEqual(self.stop(CLEAN, session='s4')['decision'], 'block')
        out = self.stop(CLEAN, session='s4')
        self.assertIn('Not fully reviewed', out['systemMessage'])

    def test_codex_patch_paths(self):
        path = self.work / 'brief.md'
        path.write_text(BAD)
        patch = f'*** Begin Patch\n*** Update File: {path}\n@@\n-a\n+b\n*** End Patch\n'
        out = self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 's5', 'tool_name': 'apply_patch',
                             'tool_input': {'command': patch}, 'cwd': str(self.work)}, tool='codex')
        self.assertEqual(out['decision'], 'block')

    def test_correction_prompt_asks_for_a_log_row(self):
        out = self.run_hook({'hook_event_name': 'UserPromptSubmit', 'session_id': 's6',
                             'prompt': "don't use that phrase again"})
        self.assertIn('corrections.md', out['hookSpecificOutput']['additionalContext'])

    def test_session_start_names_recurring_habits(self):
        self.stop(BAD, session='s7')
        out = self.run_hook({'hook_event_name': 'SessionStart', 'session_id': 's8'})
        self.assertIn('delve', out['hookSpecificOutput']['additionalContext'])

    def test_unreadable_event_is_ignored(self):
        out = subprocess.run([sys.executable, str(HOOK)], input='not json', capture_output=True, text=True,
                             env=self.env, timeout=60)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout.strip(), '')


if __name__ == '__main__':
    unittest.main(verbosity=1)
