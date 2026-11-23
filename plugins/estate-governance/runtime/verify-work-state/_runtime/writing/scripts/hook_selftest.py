#!/usr/bin/env python3
"""Self-test for hook.py. Runs the hook as Claude Code and Codex would, against a temporary rules folder."""
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
HOOK = HERE / 'hook.py'
sys.path.insert(0, str(HERE))
import hook  # noqa: E402   in-process tests patch its paths to the temporary folder
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
                       'pattern': r'\bdelve\b', 'repair': 'Say what you examine.'},
                      {'id': 'list-bold-label', 'class': 'formatting', 'scope': 'general', 'status': 'active',
                       'weight': 3, 'rule': 'F8', 'pattern': r'(?m)^\s*(?:[-*+]|\d+[.)])\s+\*\*[^*\n]+\*\*',
                       'repair': 'Write the list item as a sentence without a bold label.'}]}))
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

    def test_failed_rewrites_stay_blocked_until_the_reply_is_clean(self):
        for active in (False, True, True):
            out = self.stop(BAD, active=active)
            self.assertEqual(out['decision'], 'block')
            self.assertIn('delve', out['reason'])
        self.assertIsNone(self.stop(CLEAN, active=True))

    def test_bold_labels_block_short_replies_and_rewrites_on_both_hosts(self):
        for host in ('claude-code', 'codex'):
            for attempt, text in enumerate(('- **Owner:** Maya checks the forecast.',
                                          '1. **Next step:** Maya checks the forecast.',
                                          '- **Status:** Maya checked the forecast.')):
                with self.subTest(host=host, attempt=attempt):
                    out = self.run_hook({'hook_event_name': 'Stop', 'session_id': 'bold-' + host,
                                         'last_assistant_message': text, 'stop_hook_active': attempt > 0}, host)
                    self.assertEqual(out['decision'], 'block')
                    self.assertIn('list-bold-label', out['reason'])
            clean = self.run_hook({'hook_event_name': 'Stop', 'session_id': 'bold-' + host,
                                   'last_assistant_message': '- Maya checked the forecast.',
                                   'stop_hook_active': True}, host)
            self.assertIsNone(clean)

    def test_reply_stays_blocked_when_its_hits_log_cannot_be_written(self):
        args = mock.Mock(tool='codex', register='megan')
        with mock.patch.object(hook, 'scan_text', return_value=('fail', [{'rule': 'list-bold-label',
                                                                        'text': '**Owner:**'}])), \
                mock.patch.object(hook, 'log_hits', side_effect=OSError('read-only log')), \
                mock.patch.object(hook, 'gate_config', return_value=hook.DEFAULT_GATE), \
                mock.patch.object(hook, 'untold', return_value=[]), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            hook.on_stop({'last_assistant_message': BAD, 'stop_hook_active': True}, args, {})
        self.assertEqual(json.loads(output.getvalue())['decision'], 'block')

    def test_failed_reply_blocks_before_an_unreadable_deliverable_is_checked(self):
        path = self.work / 'unreadable.html'
        path.write_text(CLEAN)
        args = mock.Mock(tool='codex', register='megan')
        with mock.patch.object(hook, 'scan_text', return_value=('fail', [{'rule': 'list-bold-label',
                                                                        'text': '**Owner:**'}])), \
                mock.patch.object(hook, 'log_hits'), \
                mock.patch.object(hook, 'file_sha', side_effect=PermissionError('unreadable')) as hash_file, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            hook.on_stop({'last_assistant_message': BAD, 'stop_hook_active': True}, args,
                         {'deliverables': [str(path)]})
        self.assertEqual(json.loads(output.getvalue())['decision'], 'block')
        hash_file.assert_not_called()

    def test_failed_reply_block_cannot_be_lost_to_a_state_write_error(self):
        event = {'hook_event_name': 'Stop', 'session_id': 'retry-read-only-state',
                 'last_assistant_message': '- **Owner:** Maya checks the forecast.', 'stop_hook_active': True}
        with mock.patch.object(sys, 'stdin', io.StringIO(json.dumps(event))), \
                mock.patch.object(hook, 'scan_text', return_value=('fail', [{'rule': 'list-bold-label',
                                                                        'text': '**Owner:**'}])), \
                mock.patch.object(hook, 'log_hits'), \
                mock.patch.object(hook, 'write_json', side_effect=PermissionError('read-only state')) as save, \
                mock.patch.object(hook, 'untold', side_effect=OSError('unreadable settings')), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(hook.main(['--tool', 'codex']), 0)
        self.assertEqual(json.loads(output.getvalue())['decision'], 'block')
        save.assert_not_called()

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

    def test_each_written_file_is_logged_with_its_session(self):
        path = self.work / 'verdicts.json'
        path.write_text('{}')
        self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 's3', 'tool_name': 'Write',
                       'tool_input': {'file_path': str(path)}})
        logged = [json.loads(x) for x in (self.home / 'writers.jsonl').read_text().splitlines()]
        self.assertEqual([(x['session'], x['path']) for x in logged], [('s3', str(path.resolve()))])
        self.assertEqual(logged[0]['sha256'], hashlib.sha256(b'{}').hexdigest())

    def publish(self, tool_input, tool='Artifact'):
        return self.run_hook({'hook_event_name': 'PreToolUse', 'session_id': 's4', 'tool_name': tool,
                              'tool_input': tool_input})

    def test_publish_is_denied_until_the_exact_bytes_have_a_full_review(self):
        page = self.work / 'page.html'
        page.write_text('<p>' + CLEAN + '</p>')
        out = self.publish({'file_path': str(page)})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('no passing full review', out['hookSpecificOutput']['permissionDecisionReason'])
        self.assertEqual(self.publish({'content': page.read_text()})['hookSpecificOutput']['permissionDecision'], 'deny')
        receipts = self.home / 'receipts'
        receipts.mkdir()
        steps = [{'step': s, 'status': 'ok'} for s in ('scan', 'line pass', 'document pass', 'spot audit')]
        scan_only = [dict(s, status='not_run') if s['step'] != 'scan' else s for s in steps]
        sha = hashlib.sha256(page.read_bytes()).hexdigest()
        (receipts / 'scan.json').write_text(json.dumps({'sha256': sha, 'status': 'scan-pass', 'steps': scan_only}))
        self.assertIsNotNone(self.publish({'file_path': str(page)}))
        (receipts / 'full.json').write_text(json.dumps({'sha256': sha, 'status': 'pass', 'steps': steps}))
        self.assertIsNone(self.publish({'file_path': str(page)}))
        self.assertIsNone(self.publish({'content': page.read_text()}))
        page.write_text('<p>' + CLEAN + ' One more line.</p>')
        self.assertIsNotNone(self.publish({'file_path': str(page)}))

    def test_publish_with_unresolved_content_is_denied_and_says_what_it_could_not_read(self):
        reason = lambda out: out['hookSpecificOutput']['permissionDecisionReason']
        out = self.publish({'url': 'https://example.com'})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('names no file (file_path, path, file, source_path)', reason(out))
        self.assertIn('no text content (content, html, markdown, body, text, source)', reason(out))
        missing = self.work / 'gone.html'
        out = self.publish({'file_path': str(missing)}, tool='mcp__site__publish_page')
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn(f'the file {missing} named in file_path, which does not exist', reason(out))
        unreadable = self.work / 'locked.html'
        unreadable.write_text('<p>' + CLEAN + '</p>')
        unreadable.chmod(0)
        try:
            if not os.access(unreadable, os.R_OK):  # root can read any file
                out = self.publish({'path': str(unreadable)})
                self.assertIn(f'the file {unreadable} named in path', reason(out))
        finally:
            unreadable.chmod(0o644)
        logged = [json.loads(x) for x in (self.home / 'hits.jsonl').read_text().splitlines()]
        self.assertIn('publish-unresolved', {x['rule'] for x in logged})
        # In scan mode, bytes the check cannot read are denied the same way.
        (self.home / 'gate.json').write_text(json.dumps({'include': [str(self.work) + '/*'], 'exclude': [],
                                                         'publish_requires': 'scan'}))
        binary = self.work / 'page.bin'
        binary.write_bytes(b'\x00\x01\x02')
        out = self.publish({'file_path': str(binary)}, tool='mcp__site__publish_page')
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn(f'could not read {binary}', reason(out))

    def test_publish_errors_while_reading_the_content_deny_the_call(self):
        reason = lambda out: out['hookSpecificOutput']['permissionDecisionReason']
        # A file name longer than the file system allows: is_file raises instead of returning False.
        long_name = self.work / ('x' * 300 + '.html')
        out = self.publish({'file_path': str(long_name), 'content': CLEAN})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('File name too long', reason(out))
        self.assertIn(str(long_name), reason(out))
        # A folder the hook cannot enter: is_file raises PermissionError.
        locked = self.work / 'locked'
        locked.mkdir()
        (locked / 'page.html').write_text('<p>' + CLEAN + '</p>')
        locked.chmod(0)
        try:
            if not os.access(locked, os.X_OK):   # root can enter any folder
                out = self.publish({'file_path': str(locked / 'page.html'), 'content': CLEAN})
                self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
                self.assertIn('PermissionError', reason(out))
        finally:
            locked.chmod(0o755)
        # A scan whose working file cannot be created: the source suffix makes its name too long.
        (self.home / 'gate.json').write_text(json.dumps({'include': [], 'exclude': [], 'publish_requires': 'scan'}))
        odd = self.work / ('p.' + 'h' * 250)
        odd.write_text('<p>' + CLEAN + '</p>')
        out = self.publish({'file_path': str(odd)}, tool='mcp__site__publish_page')
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('could not set up the scan', reason(out))

    def test_publish_is_denied_when_the_hook_itself_fails(self):
        reason = lambda out: out['hookSpecificOutput']['permissionDecisionReason']
        # gate.json that is JSON but not an object: every setting falls back to its default and the call is held.
        (self.home / 'gate.json').write_text('[1]')
        out = self.publish({'content': CLEAN})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('no passing full review', reason(out))
        self.assertIn('holds [1], not a JSON object', reason(out))
        # The hits log and the session state cannot be written: the denial still goes out, once, with exit 0.
        (self.home / 'gate.json').write_text(json.dumps({'include': [], 'exclude': []}))
        (self.home / 'hits.jsonl').unlink(missing_ok=True)
        (self.home / 'hits.jsonl').mkdir()
        (self.home / 'state').write_text('not a folder')
        out = self.publish({'url': 'https://example.com'})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIsNone(self.publish({'content': CLEAN}, tool='Write'))

    def test_publish_scan_mode_and_other_tools(self):
        self.assertIsNone(self.publish({'content': BAD}, tool='Write'))
        (self.home / 'gate.json').write_text(json.dumps({'include': [str(self.work) + '/*'], 'exclude': [],
                                                         'publish_requires': 'scan'}))
        out = self.publish({'content': BAD}, tool='mcp__site__publish_page')
        self.assertIn('delve', out['hookSpecificOutput']['permissionDecisionReason'])
        self.assertIsNone(self.publish({'content': CLEAN}, tool='mcp__site__publish_page'))

    # -- gate.json settings of the wrong type or shape ------------------------------------------------------

    def gate(self, **settings):
        base = {'include': [str(self.work) + '/*'], 'exclude': []}
        base.update(settings)
        (self.home / 'gate.json').write_text(json.dumps(base))

    def assert_denied_with_note(self, out, key, kind='no passing full review'):
        decision = out['hookSpecificOutput']
        self.assertEqual(decision['permissionDecision'], 'deny')
        self.assertIn(kind, decision['permissionDecisionReason'])
        self.assertIn(f'gate.json setting "{key}" was ignored', decision['permissionDecisionReason'])

    def test_malformed_publish_tools_fall_back_to_the_default_list(self):
        for value in ('Artifact', 7, ['Artifact', 3], None, [], ['Artifact', '']):
            with self.subTest(publish_tools=value):
                self.gate(publish_tools=value)
                self.assert_denied_with_note(self.publish({'content': CLEAN}), 'publish_tools')
                self.assert_denied_with_note(self.publish({'content': CLEAN}, tool='mcp__site__publish_page'),
                                             'publish_tools')
                self.assertIsNone(self.publish({'content': CLEAN}, tool='Write'))
        # Content the hook cannot read is still denied for its own reason, with the note.
        self.gate(publish_tools=7)
        self.assert_denied_with_note(self.publish({'url': 'https://example.com'}), 'publish_tools',
                                     kind='could not read what Artifact sends')

    def test_a_valid_publish_tools_list_is_used_as_written(self):
        self.gate(publish_tools=['mcp__site__ship'])
        self.assertIsNone(self.publish({'content': CLEAN}))   # Artifact is not on this list
        out = self.publish({'content': CLEAN}, tool='mcp__site__ship')
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertNotIn('ignored', out['hookSpecificOutput']['permissionDecisionReason'])

    def test_malformed_publish_requires_falls_back_to_full(self):
        for value in ('Scan', 5, ['scan'], None):
            with self.subTest(publish_requires=value):
                self.gate(publish_requires=value)
                out = self.publish({'content': CLEAN}, tool='mcp__site__publish_page')
                self.assert_denied_with_note(out, 'publish_requires')

    def test_unreadable_gate_json_is_reported(self):
        (self.home / 'gate.json').write_text('{"publish_tools": ')
        out = self.publish({'content': CLEAN})
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('could not be read (JSONDecodeError', out['hookSpecificOutput']['permissionDecisionReason'])

    def test_malformed_gate_numbers_and_lists_keep_the_gate_working(self):
        # max_blocks_per_file as a string once raised inside the Stop handler and released every deliverable.
        for value in ('2', True, 0, None, 1.5):
            with self.subTest(max_blocks_per_file=value):
                session = f'blocks-{value}'
                self.gate(max_blocks_per_file=value)
                path = self.work / 'page.html'
                path.write_text('<p>' + CLEAN + '</p>')
                wrote = self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': session, 'tool_name': 'Write',
                                       'tool_input': {'file_path': str(path)}})
                self.assertIn('gate.json setting "max_blocks_per_file" was ignored',
                              wrote['hookSpecificOutput']['additionalContext'])
                first = self.stop(CLEAN, session=session)
                self.assertEqual(first['decision'], 'block')
                self.assertNotIn('ignored', first['reason'])   # told once per session
                self.assertEqual(self.stop(CLEAN, session=session)['decision'], 'block')
                self.assertIn('Not fully reviewed', self.stop(CLEAN, session=session)['systemMessage'])
        # extensions holding a non-string: the default suffixes apply, so the page is still a deliverable.
        self.gate(extensions=['.html', 5])
        path = self.work / 'brief.html'
        path.write_text('<p>' + CLEAN + '</p>')
        out = self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 'ext', 'tool_name': 'Write',
                             'tool_input': {'file_path': str(path)}})
        self.assertIn('gate.json setting "extensions" was ignored', out['hookSpecificOutput']['additionalContext'])
        self.assertEqual(self.stop(CLEAN, session='ext')['decision'], 'block')
        # exclude as a number once raised before the file scan ran; include as a string matched single characters.
        self.gate(exclude=7, include=str(self.work) + '/*')
        note = self.work / 'note.md'
        note.write_text(BAD)
        out = self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 'excl', 'tool_name': 'Write',
                             'tool_input': {'file_path': str(note)}})
        self.assertEqual(out['decision'], 'block')
        self.assertIn('delve', out['reason'])
        self.assertIn('gate.json setting "exclude" was ignored', out['reason'])
        self.assertIn('gate.json setting "include" was ignored', out['reason'])

    def test_session_start_tells_the_session_which_settings_were_ignored(self):
        self.gate(publish_tools='Artifact')
        out = self.run_hook({'hook_event_name': 'SessionStart', 'session_id': 'start'})
        self.assertIn('"publish_tools" was ignored', out['hookSpecificOutput']['additionalContext'])
        self.assertIn('"publish_tools" was ignored', out['systemMessage'])
        self.assertIsNone(self.stop(CLEAN, session='start'))   # already told

    def test_a_malformed_ledger_setting_is_told_and_the_scan_still_blocks(self):
        ledger = json.loads((self.rules / 'patterns.json').read_text())
        ledger['config']['hard_weight'] = '3'
        (self.rules / 'patterns.json').write_text(json.dumps(ledger))
        out = self.stop(BAD, session='ledger')
        self.assertEqual(out['decision'], 'block')
        self.assertIn('delve', out['reason'])
        self.assertIn('ledger setting "hard_weight"', out['reason'])

    def test_receipts_of_the_wrong_shape_are_skipped(self):
        page = self.work / 'page.html'
        page.write_text('<p>' + CLEAN + '</p>')
        sha = hashlib.sha256(page.read_bytes()).hexdigest()
        receipts = self.home / 'receipts'
        receipts.mkdir()
        (receipts / 'list.json').write_text('[1, 2]')
        (receipts / 'steps.json').write_text(json.dumps({'sha256': sha, 'status': 'pass', 'steps': 'all ok'}))
        (receipts / 'items.json').write_text(json.dumps({'sha256': sha, 'status': 'pass', 'steps': ['ok', 3]}))
        out = self.publish({'file_path': str(page)})
        self.assertIn('no passing full review', out['hookSpecificOutput']['permissionDecisionReason'])
        self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 'rcpt', 'tool_name': 'Write',
                       'tool_input': {'file_path': str(page)}})
        self.assertEqual(self.stop(CLEAN, session='rcpt')['decision'], 'block')

    # -- the error path, in process -----------------------------------------------------------------------

    def in_process(self, event, **patches):
        paths = {'GATE_CONFIG': self.home / 'gate.json', 'HITS': self.home / 'hits.jsonl',
                 'RECEIPTS': self.home / 'receipts'}
        out = io.StringIO()
        with contextlib.ExitStack() as stack:
            for name, value in {**paths, **patches}.items():
                stack.enter_context(mock.patch.object(hook, name, value))
            stack.enter_context(contextlib.redirect_stdout(out))
            code = hook.pre_tool(event, mock.Mock(tool='claude-code', register='megan'), {})
        self.assertEqual(code, 0)
        return json.loads(out.getvalue()) if out.getvalue().strip() else None

    def test_any_error_on_a_default_publish_call_denies(self):
        def broken(*_):
            raise TypeError('boom')
        event = {'hook_event_name': 'PreToolUse', 'tool_name': 'Artifact', 'tool_input': {'content': CLEAN}}
        for value in (7, 'Artifact', ['Artifact', None], None):
            with self.subTest(publish_tools=value):
                self.gate(publish_tools=value)
                out = self.in_process(event, on_pre_tool=broken)
                self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
                self.assertIn('TypeError: boom', out['hookSpecificOutput']['permissionDecisionReason'])
        # Even when loading the settings fails, the built-in list decides, and a non-publish call is let through.
        out = self.in_process(event, on_pre_tool=broken, gate_config=broken, load_gate=broken)
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIsNone(self.in_process(dict(event, tool_name='Write'), on_pre_tool=broken, gate_config=broken,
                                          load_gate=broken))
        # A configured publish tool outside the built-in list is denied on error too.
        self.gate(publish_tools=['mcp__site__ship'])
        out = self.in_process(dict(event, tool_name='mcp__site__ship'), on_pre_tool=broken)
        self.assertEqual(out['hookSpecificOutput']['permissionDecision'], 'deny')
        # A tool name that is not a string never raises.
        self.assertIsNone(self.in_process(dict(event, tool_name=['Artifact']), on_pre_tool=broken))
        self.assertTrue(hook.may_publish({'tool_name': 'Artifact'}))
        self.assertFalse(hook.may_publish({'tool_name': 7}))
        self.assertFalse(hook.may_publish(None))

    def test_a_write_the_log_cannot_record_is_reported(self):
        (self.home / 'writers.jsonl').mkdir(parents=True)   # the log path cannot be opened for append
        path = self.work / 'verdicts.json'
        path.write_text('{}')
        out = self.run_hook({'hook_event_name': 'PostToolUse', 'session_id': 's4', 'tool_name': 'Write',
                             'tool_input': {'file_path': str(path)}})
        self.assertEqual(out['decision'], 'block')
        self.assertIn('could not record that this session wrote verdicts.json', out['reason'])
        self.assertIn('--writer', out['reason'])

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
