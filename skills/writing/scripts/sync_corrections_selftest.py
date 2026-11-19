#!/usr/bin/env python3
"""Self-test for sync_corrections.py on a synthetic Hub database and rules folder."""
import contextlib
import io
import json
import os
import re
import shlex
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import sync_corrections as sync

SKILL = Path(__file__).resolve().parent.parent

LOG = """---
updated: 2026-11-01
---

# Corrections

## Log

| Date | What she corrected | Channel and audience | Rule | Pattern | Tool |
| --- | --- | --- | --- | --- | --- |
| 2026-11-10 | A bold label on each list item | Document | F8 | `list-bold-label` | Scanner ledger |
| 2026-11-18 | A site shipped with no check (Hub decision 3) | Site | R16 | candidate | Claude.ai |

## Review misses

- none
"""


class SyncCorrections(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sync-corrections-')
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.rules = root / 'rules'
        self.rules.mkdir()
        (self.rules / 'corrections.md').write_text(LOG, encoding='utf-8')
        self.db = root / 'hub.sqlite'
        with sqlite3.connect(self.db) as conn:
            conn.execute('CREATE TABLE updates (id INTEGER PRIMARY KEY, project_id TEXT, kind TEXT, body TEXT, '
                         'source TEXT, actor TEXT, at TEXT, supersedes_id INTEGER)')
            conn.execute('CREATE TABLE receipts (key TEXT PRIMARY KEY, actor TEXT, status TEXT, record_table TEXT, '
                         'record_id INTEGER, detail TEXT, at TEXT)')
            rows = [
                (3, 'ai-context', 'decision', 'Site shipped unchecked. Rules: R16.', 'writing-correction:2026-11-18:site'),
                (5, 'telix', 'decision', 'Before: "moves faster". After: the queue change. Rules R6 and F4. '
                    'Channel and audience: executive page | leadership. Tool: claude.ai.', 'writing-correction:2026-11-19:faster'),
                (6, 'telix', 'status', 'A status, not a correction.', 'writing-correction:2026-11-19:status'),
                (7, 'ai-context', 'decision', 'A decision about something else.', 'decision:2026-11-19:other'),
                (8, 'portfolio-site', 'decision', 'Older key form with no channel.', 'writing-correction-the-noun-lists-2026-11-13'),
            ]
            for uid, project, kind, body, key in rows:
                conn.execute('INSERT INTO updates VALUES (?, ?, ?, ?, NULL, ?, ?, NULL)',
                             (uid, project, kind, body, 'client-test', '2026-11-19T01:00:00Z'))
                conn.execute('INSERT INTO receipts VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (key, 'client-test', 'saved', 'updates', uid, '', '2026-11-19T01:00:00Z'))

    def run_sync(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = sync.main(['--rules-dir', str(self.rules), '--hub-db', str(self.db), '--json', *extra])
        return code, json.loads(out.getvalue())

    def test_dry_run_lists_new_corrections_and_writes_nothing(self):
        before = (self.rules / 'corrections.md').read_bytes()
        code, report = self.run_sync()
        self.assertEqual(code, 0)
        self.assertEqual([c['hub_id'] for c in report['would_add']], [5, 8])
        self.assertIn(3, report['already_copied'])   # named as "Hub decision 3" in the log
        self.assertEqual((self.rules / 'corrections.md').read_bytes(), before)

    def test_apply_adds_rows_to_the_log_table_once(self):
        self.run_sync('--apply')
        text = (self.rules / 'corrections.md').read_text()
        log = text.split('## Log')[1].split('## Review misses')[0]
        rows = [line for line in log.splitlines() if line.startswith('| 2026')]
        self.assertEqual(len(rows), 4)
        added = rows[2]
        self.assertTrue(added.startswith('| 2026-11-19 | Before: "moves faster".'))
        self.assertIn('| executive page / leadership |', added)
        self.assertIn('| F4, R6 | candidate |', added)
        self.assertIn('Hub decision 5 (claude.ai) hub:5 |', added)
        self.assertTrue(rows[3].startswith('| 2026-11-13 |'))
        self.assertIn('| see the Hub record | none yet |', rows[3])
        self.assertIn('updated: ', text.splitlines()[1])
        self.assertNotIn('2026-11-01', text.splitlines()[1])
        _, again = self.run_sync('--apply')
        self.assertEqual(again['added'], [])
        self.assertEqual(text, (self.rules / 'corrections.md').read_text())

    def test_seed_marks_corrections_copied_by_hand(self):
        _, report = self.run_sync('--seed', '5', '8', '--apply')
        self.assertEqual(report['added'], [])
        self.assertEqual(json.loads((self.rules / '.hub-corrections.json').read_text())['copied'], [5, 8])
        _, report = self.run_sync()
        self.assertEqual(report['would_add'], [])

    def test_seed_without_apply_saves_the_ids_and_leaves_corrections_md(self):
        before = (self.rules / 'corrections.md').read_bytes()
        self.run_sync('--seed', '5')
        self.assertEqual(json.loads((self.rules / '.hub-corrections.json').read_text())['copied'], [5])
        self.assertEqual((self.rules / 'corrections.md').read_bytes(), before)

    def test_the_documented_seed_command_leaves_the_seed_saved(self):
        readme = (SKILL / 'README.md').read_text(encoding='utf-8')
        found = re.search(r'`(python3 scripts/sync_corrections\.py --seed [0-9 ]+)`', readme)
        self.assertIsNotNone(found, 'the README documents the seed command')
        command = shlex.split(found.group(1))
        ids = [int(x) for x in command[command.index('--seed') + 1:]]
        home = Path(self.temp.name) / 'home'
        home.mkdir()
        env = dict(os.environ, HOME=str(home), WRITING_HOME=str(self.rules), HUB_DB_FILE=str(self.db))
        command[0] = sys.executable
        result = subprocess.run(command, cwd=SKILL, env=env, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.rules / '.hub-corrections.json').read_text())['copied'], ids)

    def test_the_hub_database_is_opened_read_only(self):
        self.run_sync('--apply')
        with sqlite3.connect(self.db) as conn:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM updates').fetchone()[0], 5)
        with self.assertRaises(sqlite3.OperationalError):
            uri = self.db.resolve().as_uri() + '?mode=ro'
            with sqlite3.connect(uri, uri=True) as conn:
                conn.execute("INSERT INTO updates VALUES (9, 'x', 'decision', 'x', NULL, 'x', 'x', NULL)")

    def test_a_long_correction_is_cut_at_a_sentence(self):
        body = 'First sentence states the fault. ' * 20
        self.assertTrue(sync.summary(body).endswith('(continues in the Hub)'))
        self.assertLessEqual(len(sync.summary(body)), sync.SUMMARY_CHARS + 30)


if __name__ == '__main__':
    unittest.main()
