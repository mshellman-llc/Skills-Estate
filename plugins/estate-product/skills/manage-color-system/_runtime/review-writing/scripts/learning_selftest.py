#!/usr/bin/env python3
"""Exercise learning state with synthetic text and disposable profiles."""
import json
from pathlib import Path
import tempfile
import unittest
import learning as m


def review(basis='user-correction'):
    return {'basis': basis, 'standard_ref': 'Write the point; use a necessary contrast only.',
            'meaning': 'Both versions keep the same outcome.', 'scope': 'The rule applies to ordinary status replies.',
            'valid_example': 'The valid contrast remains unchanged.', 'cases': [
                {'kind': 'repair', 'input': 'The result? Saved.', 'output': 'The file is saved.', 'assessment': 'States the result directly.', 'result': 'pass'},
                {'kind': 'keep', 'input': 'Choose CSV or JSON.', 'output': 'Choose CSV or JSON.', 'assessment': 'Keeps the actual alternatives.', 'result': 'pass'}]}


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = m.Store(self.root/'a', create=True); self.addCleanup(self.store.close)
        self.store.init('Example owner', 'example', 'codex', 'persistent', True)

    def event(self, pattern='direct-claim', **changes):
        value = {'session': 'session-1', 'pattern': pattern, 'host': 'codex', 'kind': 'user-correction',
                 'before': 'The result? Saved.', 'after': 'The file is saved.', 'reason': 'State the outcome directly.',
                 'source_ref': 'Synthetic conversation, correction 1', 'tags': ['general']}
        value.update(changes)
        return self.store.capture(None, value)['event']

    def proposal(self, event, **changes):
        value = {'pattern': event['pattern'], 'instruction': 'State the outcome directly.',
                 'exception': 'Keep questions that the reader needs answered.', 'tags': ['general'],
                 'evidence': [event['id']], 'review': review()}
        value.update(changes); return value

    def activate(self, pattern='direct-claim', **changes):
        event = self.event(pattern); return self.store.promote(None, self.proposal(event, **changes))['rule']

    def test_owner_is_explicit_and_cannot_be_overwritten(self):
        with self.assertRaises(ValueError): self.store.init('Different owner', 'example', 'codex', 'persistent', True)
        self.assertEqual(self.store.profile()['owner'], 'Example owner')

    def test_learning_requires_opt_in(self):
        self.store.init('Example owner', 'example', 'codex', 'persistent', False)
        with self.assertRaises(ValueError): self.event()

    def test_capture_survives_a_new_connection(self):
        event = self.event(); other=m.Store(self.root/'a')
        try: self.assertEqual(other.examples(None,'direct-claim')[0]['id'],event['id'])
        finally: other.close()

    def test_duplicate_capture_is_idempotent(self):
        first=self.event(); second=self.event()
        self.assertEqual(first['id'],second['id']); self.assertEqual(self.store.status()['events'],1)

    def test_new_session_keeps_separate_evidence(self):
        self.event(); self.event(session='session-2'); self.assertEqual(self.store.status()['events'],2)

    def test_ai_edit_is_a_candidate_not_a_preference(self):
        event=self.event(kind='ai-repair')
        with self.assertRaises(ValueError): self.store.promote(None,self.proposal(event))
        self.assertEqual(self.store.status()['active_rules'],0)
        self.assertEqual(self.store.pending()[0]['count'],1)

    def test_ai_repair_can_be_reviewed_against_core_standard(self):
        event=self.event(kind='ai-repair'); result=self.store.promote(None,self.proposal(event,review=review('writing-standard')))
        self.assertEqual(result['action'],'activated')

    def test_promotion_requires_meaning_and_valid_example_reviews(self):
        event=self.event(); proposal=self.proposal(event); del proposal['review']['valid_example']
        with self.assertRaises(ValueError): self.store.promote(None,proposal)

    def test_failed_regression_case_prevents_activation(self):
        event=self.event(); proposal=self.proposal(event); proposal['review']['cases'][0]['result']='fail'
        with self.assertRaises(ValueError): self.store.promote(None,proposal)

    def test_a_rule_does_not_need_an_invented_exception(self):
        rule=self.activate(exception='')
        self.assertEqual(rule['exception'],'')
        other=self.other(); other.import_data(None,self.store.export(None),'Example owner')
        self.assertEqual(len(other.transfers()[0]['rules']),1)

    def test_reinforcement_does_not_add_another_rule(self):
        first=self.activate(); second=self.event(session='session-2'); result=self.store.promote(None,self.proposal(second))
        self.assertEqual(result['action'],'reinforced'); self.assertEqual(result['rule']['id'],first['id'])
        self.assertEqual(len(result['rule']['evidence']),2); self.assertEqual(len(self.store.rules('example')),1)

    def test_changed_instruction_needs_expected_revision(self):
        old=self.activate(); event=self.event(session='session-2'); proposal=self.proposal(event,instruction='Put the saved path first.',supersedes=[old['id']],expected_revision=99)
        with self.assertRaises(ValueError): self.store.promote(None,proposal)
        self.assertEqual(self.store.rules('example')[0]['instruction'],old['instruction'])

    def test_reviewed_replacement_keeps_old_rule_history(self):
        old=self.activate(); event=self.event(session='session-2'); self.store.promote(None,self.proposal(event,instruction='Put the saved path first.',supersedes=[old['id']],expected_revision=1))
        self.assertEqual(len(self.store.rules('example')),1); self.assertEqual(len(self.store.rules('example',False)),2)

    def test_compaction_merges_evidence_without_broadening_scope(self):
        a=self.activate('direct-claim'); b=self.activate('remove-setup'); e=self.event('direct-answer')
        result=self.store.promote(None,self.proposal(e,supersedes=[a['id'],b['id']]))
        self.assertEqual(len(result['rule']['evidence']),3); self.assertEqual(len(self.store.rules('example')),1)

    def test_merge_cannot_turn_a_project_rule_into_a_global_rule(self):
        old=self.activate(scope='project',scope_id='example-project'); e=self.event('direct-answer')
        with self.assertRaises(ValueError): self.store.promote(None,self.proposal(e,supersedes=[old['id']]))

    def test_rule_budget_preserves_the_candidate_and_existing_rules(self):
        for number in range(12): self.activate('pattern-'+str(number))
        e=self.event('pattern-overflow')
        with self.assertRaises(ValueError): self.store.promote(None,self.proposal(e))
        self.assertEqual(len(self.store.rules('example')),12); self.assertEqual(self.store.status()['events'],13)

    def test_word_budget_refuses_long_rules(self):
        for number in range(5): self.activate('pattern-'+str(number),instruction=' '.join(['Describe']*55))
        event=self.event('long-pattern')
        with self.assertRaises(ValueError): self.store.promote(None,self.proposal(event,instruction=' '.join(['Describe']*55)))

    def test_context_filters_host_project_and_tags(self):
        self.activate('global-rule')
        self.activate('claude-rule',scope='host',scope_id='claude-code')
        self.activate('project-rule',scope='project',scope_id='project-one')
        self.activate('resume-rule',tags=['resume'])
        context=self.store.context(host='codex',project='project-two')
        self.assertEqual(len(context['active_rule_ids']),1)
        self.assertLessEqual(len(context['active_markdown'].split()),m.MAX_WORDS)
        self.assertNotIn('claude-rule',context['active_markdown'])
        self.assertEqual(len(self.store.context(host='claude-code',project='project-one',tags=['resume'])['active_rule_ids']),4)

    def test_examples_are_bounded(self):
        for number in range(7): self.event(session='session-'+str(number))
        self.assertEqual(len(self.store.examples(None,'direct-claim')),2)
        with self.assertRaises(ValueError): self.store.examples(None,'direct-claim',100)

    def test_concurrent_duplicate_capture_retains_one_event(self):
        from concurrent.futures import ThreadPoolExecutor
        source=self.event()
        with self.store.db: self.store.db.execute('DELETE FROM events')
        def capture_again(_):
            store=m.Store(self.root/'a')
            try:
                event={k:v for k,v in source.items() if k not in {'id','installation','created','profile'}}
                return store.capture(None,event)['event']['id']
            finally: store.close()
        with ThreadPoolExecutor(max_workers=4) as pool:
            ids=list(pool.map(capture_again,range(8)))
        self.assertEqual(len(set(ids)),1); self.assertEqual(self.store.status()['events'],1)

    def test_session_export_does_not_copy_unrelated_history(self):
        self.event(); target=self.event(session='other-session')
        result=self.store.export(None,True,session='other-session')
        self.assertEqual([e['id'] for e in result['payload']['events']],[target['id']])

    def test_malformed_transfer_does_not_mutate_store(self):
        with self.assertRaises(ValueError): self.store.import_data(None,[], 'Example owner')
        self.assertEqual(self.store.status()['events'],0)

    def test_default_export_omits_raw_samples(self):
        self.activate(); bundle=self.store.export(None)
        self.assertEqual(bundle['payload']['events'],[])
        self.assertNotIn('The result? Saved.',json.dumps(bundle))

    def other(self):
        other=m.Store(self.root/'b',create=True); self.addCleanup(other.close)
        other.init('Example owner','example','claude-code','persistent',True); return other

    def test_import_is_idempotent_and_never_activates_rules(self):
        self.activate(); bundle=self.store.export(None,True); other=self.other()
        self.assertEqual(other.import_data(None,bundle,'Example owner')['imported_events'],1)
        self.assertEqual(other.import_data(None,bundle,'Example owner')['imported_events'],0)
        self.assertEqual(other.status()['active_rules'],0)
        self.assertEqual(len(other.transfers()),1)

    def test_owner_confirmed_transfer_requires_a_new_review(self):
        rule=self.activate(); other=self.other(); result=other.import_data(None,self.store.export(None),'Example owner')
        proposal={k:rule[k] for k in ['pattern','instruction','exception','scope','scope_id','tags']}
        proposal['review']=review('owner-transfer'); proposal['review']['transfer_id']=result['transfer_id']
        proposal['review']['owner_confirmation']={'statement':'The synthetic owner requested adoption of this supplied profile.','source_ref':'Synthetic owner request, test fixture.'}
        self.assertEqual(other.promote(None,proposal)['action'],'activated')

    def test_wrong_owner_and_tampering_are_rejected(self):
        bundle=self.store.export(None); other=self.other()
        with self.assertRaises(ValueError): other.import_data(None,bundle,'Different owner')
        bundle['payload']['owner']='Different owner'
        with self.assertRaises(ValueError): other.import_data(None,bundle,'Example owner')

    def test_self_import_deduplicates_existing_local_evidence(self):
        self.event(); self.assertEqual(self.store.import_data(None,self.store.export(None,True),'Example owner')['imported_events'],0)

    def test_retired_rules_leave_active_context_but_retain_history(self):
        rule=self.activate(); self.store.retire(None,rule['id'],'This rule caused an unnecessary edit.')
        self.assertEqual(len(self.store.rules('example')),0); self.assertEqual(len(self.store.rules('example',False)),1)

    def test_retired_evidence_does_not_return_as_a_new_candidate(self):
        rule=self.activate(); self.store.retire(None,rule['id'],'The preference no longer applies.')
        self.assertEqual(self.store.pending(),[])

    def test_dismissed_candidate_is_retained_but_not_requeued(self):
        event=self.event(kind='ai-repair'); self.store.dismiss(None,event['id'],'The original contrast was necessary.')
        self.assertEqual(self.store.pending(),[]); self.assertEqual(self.store.status()['events'],1)

    def test_checkpoint_does_not_claim_a_background_hook(self):
        self.event(); result=self.store.finish(None,'session-1')
        self.assertEqual(result['captured_this_session'],1); self.assertFalse(result['background_hook'])

    def test_invalid_identifiers_do_not_escape_profile_store(self):
        with self.assertRaises(ValueError): self.event(pattern='../another-owner')


if __name__=='__main__':
    unittest.main(verbosity=2)
