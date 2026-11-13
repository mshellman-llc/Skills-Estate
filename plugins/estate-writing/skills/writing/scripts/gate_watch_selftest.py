#!/usr/bin/env python3
"""Self-test for gate_watch.py with a stand-in for Claude Code."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE / 'gate_watch.py'


class WatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.folder = root / 'to-review'
        self.folder.mkdir()
        self.agent = root / 'agent'
        self.calls = root / 'calls.txt'
        fake = root / 'claude'
        fake.write_text('#!/bin/sh\necho "$2" >> "%s"\necho \'{"result": "Gate ran.\\nPASS /Volumes/BeastMode/x.md"}\'\n'
                        % self.calls)
        fake.chmod(0o755)
        self.env = dict(os.environ, WRITING_AGENT_HOME=str(self.agent), CLAUDE_BIN=str(fake),
                        GATE_WATCH_QUIET='1', GATE_WATCH_SETTLE='0.1')

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), '--folder', str(self.folder), *args],
                              capture_output=True, text=True, env=self.env, timeout=60)

    def test_each_new_file_is_reviewed_once_per_version(self):
        (self.folder / 'proposal.md').write_text('A proposal for the client.\n')
        (self.folder / '.hidden.md').write_text('skip\n')
        (self.folder / 'photo.png').write_bytes(b'skip')
        self.assertEqual(self.run_tool().returncode, 0)
        calls = self.calls.read_text().splitlines()
        self.assertEqual(sum(1 for c in calls if c.startswith('/gate ')), 1)
        self.assertIn('proposal.md', calls[0])
        log = [json.loads(l) for l in (self.agent / 'gate-watch.jsonl').read_text().splitlines()]
        self.assertTrue(log[0]['result'].startswith('PASS'))
        self.run_tool()
        self.assertEqual(sum(1 for c in self.calls.read_text().splitlines() if c.startswith('/gate ')), 1)
        (self.folder / 'proposal.md').write_text('A proposal for the client, revised.\n')
        self.run_tool()
        self.assertEqual(sum(1 for c in self.calls.read_text().splitlines() if c.startswith('/gate ')), 2)

    def test_missing_folder_exits_cleanly(self):
        self.folder.rmdir()
        self.assertEqual(self.run_tool().returncode, 0)
        self.assertFalse(self.calls.exists())


if __name__ == '__main__':
    unittest.main(verbosity=1)
