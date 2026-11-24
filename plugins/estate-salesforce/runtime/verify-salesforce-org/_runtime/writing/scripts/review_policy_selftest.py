#!/usr/bin/env python3
"""Review allocation tests use synthetic files and never start a model."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import hook
import install_local
import review_policy as policy


class PolicyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.env = mock.patch.dict(os.environ, {'WRITING_AGENT_HOME': str(self.root / 'agent')})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.file = self.root / 'external.md'
        self.file.write_text('The support lead approves the release note.')

    def prepare(self, folder='review', digest='first', **kw):
        return policy.prepare(self.file, self.root / folder, digest, ['writer'], **kw)

    def test_internal_artifact_never_requests_an_independent_review(self):
        with mock.patch.object(hook, 'gate_config', return_value=dict(hook.DEFAULT_GATE, include=['*'])), \
                mock.patch.object(hook, 'scan_text', return_value=('scan-pass', [])), \
                mock.patch.object(hook, 'untold', return_value=[]), contextlib.redirect_stdout(io.StringIO()) as out:
            hook.on_stop({'last_assistant_message': 'The draft is saved.'}, mock.Mock(tool='codex', register='megan'),
                         {'deliverables': [str(self.file)]})
        self.assertEqual(out.getvalue(), '')

    def test_new_folders_and_internal_reclassification_do_not_reset_budget(self):
        self.assertEqual(self.prepare()['round'], 1)
        self.assertEqual(self.prepare('review-again')['round'], 2)
        policy.internal(self.file)
        with self.assertRaisesRegex(policy.PolicyError, 'budget is exhausted'):
            self.prepare('round-one-again')

    def test_repeat_preparation_for_an_audit_does_not_consume_a_round(self):
        self.prepare()
        self.assertEqual(self.prepare()['round'], 1)
        self.assertEqual(self.prepare(requested=2)['round'], 2)
        with self.assertRaises(policy.PolicyError):
            self.prepare(requested=1)

    def test_changed_bytes_consume_the_final_round_without_a_round_flag(self):
        self.prepare()
        self.assertEqual(self.prepare(digest='changed')['round'], 2)
        with self.assertRaises(policy.PolicyError):
            self.prepare(digest='changed-again')

    def test_one_reviewer_supplies_every_pass(self):
        self.prepare()
        doc = {'reviewer': 'reviewer', 'session': 'reviewer-session'}
        result = policy.validate(self.file, 'first', [doc, doc, doc])
        self.assertEqual((result['round'], result['reviewer']), (1, 'reviewer'))
        with self.assertRaisesRegex(policy.PolicyError, 'Only one'):
            policy.validate(self.file, 'first', [doc, {'reviewer': 'another'}])
        with self.assertRaisesRegex(policy.PolicyError, 'original reviewer'):
            policy.validate(self.file, 'first', [{'reviewer': 'replacement'}])

    def test_writer_cannot_be_the_reviewer(self):
        self.prepare()
        with self.assertRaisesRegex(policy.PolicyError, 'cannot be the writer'):
            policy.validate(self.file, 'first', [{'reviewer': 'writer'}])

    def test_third_round_flag_is_refused(self):
        self.prepare()
        with self.assertRaises(policy.PolicyError):
            policy.validate(self.file, 'first', [{'reviewer': 'reviewer'}], requested=3)

    def test_internal_and_nested_delegation_are_denied_on_both_hosts(self):
        for name, data in [('Agent', {'prompt': 'Review this internal note.'}),
                           ('spawn_agent', {'message': 'Review this internal note.'}),
                           ('Bash', {'command': 'claude -p "Review this internal note"'}),
                           ('functions.exec_command', {'cmd': 'codex exec "Review this internal note"'})]:
            event = {'session_id': 'writer', 'tool_name': name, 'tool_input': data}
            reason = hook.on_pre_tool(event, mock.Mock(tool='codex'), {})
            self.assertIn('Internal work stays', reason)

    def test_only_one_launch_and_one_resume_for_the_external_file(self):
        plan = self.prepare()
        request = str(self.file)
        self.assertEqual(policy.authorize_launch('writer', request), plan['reviewer_session'])
        with self.assertRaisesRegex(policy.PolicyError, 'already has'):
            policy.authorize_launch('writer', request)
        policy.authorize_launch('writer', request, resume=plan['reviewer_session'])
        with self.assertRaisesRegex(policy.PolicyError, 'one follow-up'):
            policy.authorize_launch('writer', request, resume=plan['reviewer_session'])
        with self.assertRaises(policy.PolicyError):
            policy.authorize_launch(plan['reviewer_session'], request)

    def test_batch_launch_is_refused_before_consuming_the_one_reviewer(self):
        self.prepare()
        text = f'for n in 1 2 3; do claude -p "Review {self.file}"; done'
        request = hook.delegation_request({'tool_name': 'Bash', 'tool_input': {'command': text}})
        self.assertTrue(request[2])
        with self.assertRaisesRegex(policy.PolicyError, 'batches'):
            policy.authorize_launch('writer', *request)
        self.assertEqual(policy.read(self.file)['launches'], 0)

    def test_private_artifact_gets_only_a_scan_but_publish_stays_guarded(self):
        with mock.patch.object(hook, 'scan_file', return_value=('scan-pass', [])), \
                mock.patch.object(hook, 'reviewed', return_value=False):
            internal = {'tool_name': 'Artifact', 'tool_input': {'content': 'A private working draft.'}}
            self.assertIsNone(hook.on_pre_tool(internal, mock.Mock(tool='claude-code', register='megan'), {}))
            external = {'tool_name': 'mcp__site__publish_page',
                        'tool_input': {'content': 'A public page.', 'audience': 'internal'}}
            self.assertIn('no passing full review', hook.on_pre_tool(external, mock.Mock(tool='codex'), {}))

    def test_installer_preserves_other_hooks_and_is_idempotent_on_both_hosts(self):
        for relative in ('.claude/settings.json', '.codex/hooks.json'):
            target = self.root / relative
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps({'env': {'KEEP': 'value'}, 'hooks': {
                'PreToolUse': [{'matcher': 'Read', 'hooks': [{'type': 'command', 'command': 'keep'}]}]}}))
        with mock.patch.object(install_local, 'HOME', self.root), \
                mock.patch.object(install_local, 'BIN', self.root / 'bin'):
            self.assertEqual(len(install_local.install_host_hooks(False)), 2)
            self.assertEqual(install_local.install_host_hooks(False), [])
        for relative in ('.claude/settings.json', '.codex/hooks.json'):
            data = json.loads((self.root / relative).read_text())
            self.assertEqual(data['env'], {'KEEP': 'value'})
            self.assertEqual(data['hooks']['PreToolUse'][0]['matcher'], 'Read')
            self.assertEqual(len(data['hooks']['PreToolUse']), 2)

    def test_missing_state_does_not_restart_a_stop_loop(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            hook.on_stop({'stop_hook_active': True}, mock.Mock(tool='codex'), {})
        self.assertNotIn('"decision": "block"', out.getvalue())

    def test_plain_python_checks_do_not_look_like_model_launches(self):
        self.assertIsNone(hook.delegation_request({'tool_name': 'Bash', 'tool_input': {
            'command': 'python3 check.py --file external.md --json'}}))


if __name__ == '__main__':
    unittest.main(verbosity=1)
