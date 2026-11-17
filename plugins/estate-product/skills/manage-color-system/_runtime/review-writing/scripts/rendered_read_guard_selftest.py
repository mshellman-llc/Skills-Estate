#!/usr/bin/env python3
"""Self-test for rendered_read_guard.py, the PreToolUse hook for Claude Code and Codex."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).resolve().with_name('rendered_read_guard.py')


def decide(event):
    """Run the guard on one event and return its decision, or None when it allows the call."""
    raw = event if isinstance(event, str) else json.dumps(event)
    out = subprocess.run([sys.executable, str(GUARD)], input=raw, capture_output=True, text=True, check=True).stdout
    return json.loads(out)['hookSpecificOutput']['permissionDecision'] if out.strip() else None


class Guard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        cls.big = root / 'big page.html'
        cls.big.write_text('<p>text</p>\n' * 10_000)
        cls.wide = root / 'wide.html'
        cls.wide.write_text('<img src="data:image/png;base64,' + 'A' * 5_000 + '">\n<p>Hello</p>\n')
        cls.small = root / 'small.html'
        cls.small.write_text('<p>Hello</p>\n')
        cls.book = root / 'book.xlsx'
        cls.book.write_bytes(b'PK\x03\x04')
        cls.notes = root / 'notes.md'
        cls.notes.write_text('x' * 200_000)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def read(self, path, **extra):
        return decide({'tool_name': 'Read', 'tool_input': {'file_path': str(path), **extra}})

    def shell(self, command, tool='Bash'):
        key = 'cmd' if tool == 'exec_command' else 'command'
        return decide({'tool_name': tool, 'tool_input': {key: command}})

    def test_whole_reads_of_large_rendered_files_are_denied(self):
        for path in (self.big, self.wide, self.book):
            self.assertEqual(self.read(path), 'deny', path.name)

    def test_bounded_and_small_reads_pass(self):
        self.assertIsNone(self.read(self.big, offset=1, limit=100))
        self.assertIsNone(self.read(self.small))
        self.assertIsNone(self.read(self.notes))
        self.assertIsNone(self.read(Path(self.tmp.name) / 'missing.html'))

    def test_shell_whole_file_readers_are_denied(self):
        quoted = f"'{self.big}'"
        self.assertEqual(self.shell(f'cat {quoted}'), 'deny')
        self.assertEqual(self.shell(f'cd /tmp && less {quoted}', tool='exec_command'), 'deny')
        self.assertEqual(self.shell(f'nl -ba {quoted}'), 'deny')

    def test_filtered_ranged_and_redirected_shell_reads_pass(self):
        quoted = f"'{self.big}'"
        self.assertIsNone(self.shell(f'cat {quoted} | head -20'))
        self.assertIsNone(self.shell(f'sed -n 1,40p {quoted}'))
        self.assertIsNone(self.shell(f'cat {quoted} > /tmp/copy.html'))
        self.assertIsNone(self.shell(f'grep -n title {quoted}'))

    def test_denial_names_the_extractor(self):
        out = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(
            {'tool_name': 'Read', 'tool_input': {'file_path': str(self.big)}}), capture_output=True, text=True).stdout
        self.assertIn('extract_review_text.py', out)

    def test_other_tools_and_bad_input_pass(self):
        self.assertIsNone(decide({'tool_name': 'Write', 'tool_input': {'file_path': str(self.big)}}))
        self.assertIsNone(decide('not json'))
        self.assertIsNone(decide({'tool_name': 'Bash', 'tool_input': {'command': 'cat "unclosed'}}))


if __name__ == '__main__':
    unittest.main()
