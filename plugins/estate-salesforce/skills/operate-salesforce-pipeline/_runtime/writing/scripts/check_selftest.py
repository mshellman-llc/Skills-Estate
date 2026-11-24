#!/usr/bin/env python3
"""Self-test for check.py. Every file and ledger is synthetic and lives in a temporary folder."""
import contextlib
import io
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import check

LEDGER = {
    'version': 1,
    'config': {'min_words': 40, 'density_floor_words': 250, 'flag_density': 4, 'repeat_limit': 3,
               'repeat_density': 1.5, 'hard_weight': 3, 'em_dash': False},
    'rules': [
        {'id': 'residue', 'class': 'chat', 'scope': 'general', 'status': 'active', 'weight': 3,
         'repair': 'Delete it.', 'pattern': r'\bI hope this helps\b'},
        {'id': 'marker', 'class': 'vocabulary', 'scope': 'general', 'status': 'active', 'weight': 1,
         'repair': 'Use the plain word.', 'terms': ['robust'], 'inflect': True},
        {'id': 'twice', 'class': 'format', 'scope': 'general', 'status': 'active', 'weight': 3, 'min_count': 2,
         'repair': 'Use it once.', 'terms': ['in short']},
        {'id': 'candidate', 'class': 'user', 'scope': 'general', 'status': 'candidate', 'weight': 3,
         'repair': 'Say it plainly.', 'terms': ['pending phrase']},
        {'id': 'author-only', 'class': 'voice', 'scope': 'author', 'status': 'active', 'weight': 3,
         'repair': 'Make the claim directly.', 'terms': ['whether it is']},
        {'id': 'three', 'class': 'construction', 'scope': 'general', 'status': 'active', 'weight': 3,
         'judge': 'line-pass', 'repair': 'Use the true count.', 'terms': ['intake, scoping and pricing']},
        {'id': 'retired', 'class': 'user', 'scope': 'general', 'status': 'retired', 'weight': 3,
         'repair': 'None.', 'terms': ['ledger entry']},
    ],
}
# Two lines from a failed review. No scanner pattern matches either one; the line pass must mark both.
REGRESSION = ['The company is adding products faster than its systems were built for.',
              'Revenue risk shows up while there is time to act.']


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='writing-check-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.rules = self.root / 'rules'
        self.rules.mkdir()
        self.ledger(LEDGER)
        (self.rules / 'rules.md').write_text('Synthetic rules file.\n')
        self.receipts = self.root / 'receipts'
        self.agent_home = self.root / 'agent-home'
        previous = os.environ.get('WRITING_AGENT_HOME')
        os.environ['WRITING_AGENT_HOME'] = str(self.agent_home)
        self.addCleanup(lambda: os.environ.pop('WRITING_AGENT_HOME') if previous is None
                        else os.environ.__setitem__('WRITING_AGENT_HOME', previous))

    def ledger(self, data):
        (self.rules / 'patterns.json').write_text(json.dumps(data))

    def write(self, name, text):
        path = self.root / name
        path.write_text(text, encoding='utf-8')
        return path

    def check(self, path, *extra, rules=True):
        argv = ['--file', str(path), '--json', '--receipt-dir', str(self.receipts), *extra]
        if rules:
            argv += ['--rules-dir', str(self.rules)]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = check.main(argv)
        return code, json.loads(out.getvalue())

    def receipt(self, result):
        return json.loads(Path(result['receipt']).read_text())


class Contract(Base):
    def test_scan_alone_reports_scan_pass_never_pass(self):
        code, result = self.check(self.write('note.md', '# Release note\n\nThe export job now writes one file per client.\n'))
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'scan-pass')
        self.assertEqual(result['coverage']['lines_total'], 2)
        self.assertEqual(result['coverage']['lines_reviewed'], 2)
        self.assertEqual(result['findings'], [])
        for key in ('status', 'coverage', 'findings', 'receipt'):
            self.assertIn(key, result)
        saved = self.receipt(result)
        self.assertEqual(saved['status'], 'scan-pass')
        self.assertEqual([s['status'] for s in saved['steps']][:3], ['ok', 'ok', 'ok'])
        self.assertEqual({s['step']: s['status'] for s in saved['steps']}['line pass'], 'not_run')

    def test_blocking_finding_exits_1_with_line_rule_text_and_fix(self):
        code, result = self.check(self.write('reply.md', 'The report is attached.\n\nI hope this helps.\n'))
        self.assertEqual(code, 1)
        self.assertEqual(result['status'], 'fail')
        finding = result['findings'][0]
        self.assertEqual((finding['line'], finding['rule'], finding['text'], finding['fix']),
                         (3, 'residue', 'I hope this helps', 'Delete it.'))

    def test_low_weight_hit_is_advisory_until_the_ledger_thresholds_are_met(self):
        code, result = self.check(self.write('one.md', 'The robust service restarts after a crash.\n'))
        self.assertEqual((code, result['advisories']), (0, 1))
        dense = ' '.join(['The robust queue holds forty jobs and the robust worker drains it nightly.'] * 6)
        code, result = self.check(self.write('many.md', dense + '\n'))
        self.assertEqual(code, 1)
        self.assertEqual({f['rule'] for f in result['findings']}, {'marker'})

    def test_min_count_candidate_and_retired_rules(self):
        code, result = self.check(self.write('a.md', 'In short, the job failed. The pending phrase and the ledger entry stay.\n'))
        self.assertEqual(code, 0)
        code, result = self.check(self.write('b.md', 'In short, the job failed.\n\nIn short, it ran twice.\n'))
        self.assertEqual([f['rule'] for f in result['findings']], ['twice', 'twice'])

    def test_register_adds_rules_scoped_to_it_and_a_new_name_is_recorded(self):
        path = self.write('bio.md', 'She leads delivery, whether it is a migration or a rebuild.\n')
        self.assertEqual(self.check(path)[0], 0)
        code, result = self.check(path, '--register', 'author')
        self.assertEqual((code, result['findings'][0]['rule']), (1, 'author-only'))
        (self.rules / 'registers.md').write_text('# Registers\n\n### client-email-scope\n\nOpen on the issue.\n')
        code, result = self.check(path, '--register', 'client-email-scope,author')
        self.assertEqual(code, 1)
        self.assertIn('register client-email-scope adds 0 rules', result['steps'][0]['detail'])
        code, result = self.check(path, '--register', 'slack to a client sponsor')
        self.assertEqual(code, 0)
        detail = result['steps'][0]['detail']
        self.assertIn('register slack to a client sponsor is new and added no rules (recorded in registers.md)', detail)
        self.assertIn('known names: author, client-email-scope, commit', detail)
        listing = (self.rules / 'registers.md').read_text()
        self.assertIn('### slack to a client sponsor', listing)
        self.assertIn('No rules yet', listing)
        self.assertIn(str(path), listing)
        code, result = self.check(path, '--register', 'slack to a client sponsor')
        self.assertIn('register slack to a client sponsor adds 0 rules', result['steps'][0]['detail'])
        self.assertEqual((self.rules / 'registers.md').read_text().count('### slack to a client sponsor'), 1)


class Scope(Base):
    def test_register_aliases_in_registers_md_run_the_names_they_point_to(self):
        (self.rules / 'registers.md').write_text(
            '# Registers\n\n### author\n\nHer own voice.\n\n### hiring\n\nHiring readers.\n\n'
            '### service-page\n\nA service page. Pass `author,hiring` with it.\n\n'
            '## Names first seen by the check\n\n### portfolio\n\nHiring-facing copy. Pass `author`.\n\n'
            '### internal\n\nSame register as `hiring`. Pass that name.\n\n'
            '### loop-a\n\nPass `loop-b`.\n\n### loop-b\n\nPass `loop-a`.\n')
        page = self.write('page.md', 'We decide whether it is worth the cost before the call.\n')
        code, result = self.check(page, '--register', 'portfolio')
        self.assertEqual(code, 1)
        self.assertEqual([f['rule'] for f in result['findings']], ['author-only'])
        saved = self.receipt(result)
        self.assertEqual(saved['register'], ['author'])
        self.assertEqual(saved['rules']['register_aliases'], {'portfolio': ['author']})
        self.assertIn('register portfolio is an alias', saved['steps'][0]['detail'])
        self.assertEqual(check.resolve_registers(['service-page'], self.rules)[0], ['service-page', 'author', 'hiring'])
        self.assertEqual(check.resolve_registers(['internal', 'hiring'], self.rules)[0], ['hiring'])
        self.assertEqual(check.resolve_registers(['loop-a'], self.rules)[0], ['loop-a'])
        self.assertNotIn('portfolio\n\nFirst seen', (self.rules / 'registers.md').read_text())

    def test_code_quotations_and_front_matter_are_exempt(self):
        text = ('---\ntitle: I hope this helps\n---\n# Setup\n\nRun `echo I hope this helps` first.\n\n'
                '```sh\necho "I hope this helps"\n```\n\n> I hope this helps\n\n'
                'The reviewer wrote "I hope this helps" in the ticket.\n\n<!-- I hope this helps -->\n')
        code, result = self.check(self.write('scope.md', text))
        self.assertEqual((code, result['findings']), (0, []))
        self.assertEqual(result['coverage']['lines_total'], 3)
        exempt = self.receipt(result)['coverage']['lines_exempt']
        self.assertEqual((exempt['metadata'], exempt['code'], exempt['quotation']), (4, 3, 1))

    def test_html_page_text_is_in_scope_and_markup_code_and_quotes_are_not(self):
        page = ('<html><head><title>Field card</title><style>p{color:red}</style></head><body>\n'
                '<h1>How grading runs</h1>\n<p>The job grades each paper at night. I hope this helps.</p>\n'
                '<pre>print("I hope this helps")</pre>\n<p>Run <code>I hope this helps</code> once.</p>\n'
                '<blockquote><p>I hope this helps</p></blockquote>\n'
                '<button aria-label="I hope this helps">Send</button>\n'
                '<script>const label = "I hope this helps, said the tooltip";</script></body></html>\n')
        code, result = self.check(self.write('card.html', page))
        self.assertEqual(code, 1)
        self.assertEqual(sorted(f['line'] for f in result['findings']), [3, 7, 8])
        exempt = self.receipt(result)['coverage']['lines_exempt']
        self.assertEqual((exempt['code'], exempt['quotation']), (1, 1))

    def test_commit_message_is_reviewed_and_trailers_are_not(self):
        folder = self.root / 'git'
        folder.mkdir()
        message = folder / 'COMMIT_EDITMSG'
        message.write_text('fix(export): write one file per client\n\nI hope this helps.\n\n'
                           'Co-Authored-By: Example <example@example.com>\n# Please enter the commit message\n')
        code, result = self.check(message)
        self.assertEqual((code, result['coverage']['lines_total'], result['findings'][0]['line']), (1, 2, 3))

    def test_commit_register_and_a_rule_line_are_not_front_matter(self):
        text = 'fix(export): write one file per client\n\nI hope this helps.\n# comment from git\n'
        code, result = self.check(self.write('message.txt', text), '--register', 'commit')
        self.assertEqual((code, result['coverage']['lines_total']), (1, 2))
        ruled = '---\n\nI hope this helps.\n\n---\n\nThe export job writes one file per client.\n'
        code, result = self.check(self.write('ruled.md', ruled))
        self.assertEqual((code, result['findings'][0]['line']), (1, 3))

    def test_json_content_file_strings_are_reviewed(self):
        path = self.write('content.json', json.dumps({'title': 'Grading schedule', 'body': 'I hope this helps.'}, indent=1))
        code, result = self.check(path)
        self.assertEqual((code, result['findings'][0]['line']), (1, 3))


class NeverSilent(Base):
    def long_file(self, lines=1000):
        body = [f'Paragraph {n} names job {n} and its owner.' for n in range(1, lines + 1)]
        body[949] = 'I hope this helps.'
        return self.write('long.md', '\n\n'.join(body) + '\n')

    def test_long_file_is_split_and_every_line_is_scanned(self):
        code, result = self.check(self.long_file())
        saved = self.receipt(result)
        self.assertEqual(code, 1)
        self.assertEqual(result['coverage'], {'lines_total': 1000, 'lines_reviewed': 1000, 'lines_exempt': 0})
        self.assertEqual(result['findings'][0]['line'], 1899)
        self.assertGreaterEqual(len(saved['parts']), 4)
        self.assertTrue(all(p['lines_in_scope'] <= check.PART_LINES for p in saved['parts']))
        self.assertEqual(sum(p['lines_reviewed'] for p in saved['parts']), 1000)

    def test_failed_part_is_retried_with_half_the_lines_then_reported_incomplete(self):
        real, calls = check.scan_chunk, []

        def flaky(chunk, rules):
            calls.append(len(chunk))
            if any(r['id'] == '0420' for r in chunk):
                raise RuntimeError('worker stopped')
            return real(chunk, rules)
        check.scan_chunk = flaky
        self.addCleanup(setattr, check, 'scan_chunk', real)
        code, result = self.check(self.long_file())
        self.assertEqual((code, result['status']), (2, 'incomplete'))
        self.assertLess(result['coverage']['lines_reviewed'], result['coverage']['lines_total'])
        missed = [x['id'] for x in result['not_reviewed']]
        self.assertIn('0420', missed)
        self.assertEqual(len(missed), result['coverage']['lines_total'] - result['coverage']['lines_reviewed'])
        self.assertLessEqual(len(missed), check.PART_LINES // 4 + 1)
        self.assertIn('worker stopped', result['reason'])
        self.assertEqual(result['findings'][0]['line'], 1899)

    def test_part_that_recovers_on_retry_completes(self):
        real, state = check.scan_chunk, {'failed': False}

        def once(chunk, rules):
            if not state['failed']:
                state['failed'] = True
                raise RuntimeError('first attempt')
            return real(chunk, rules)
        check.scan_chunk = once
        self.addCleanup(setattr, check, 'scan_chunk', real)
        code, result = self.check(self.long_file())
        self.assertEqual((code, result['coverage']['lines_reviewed']), (1, 1000))
        self.assertEqual(self.receipt(result)['parts'][0]['retries'], 1)

    def test_scan_that_skips_a_line_is_incomplete(self):
        real = check.scan_chunk

        def skimming(chunk, rules):
            result = real(chunk, rules)
            result['ids'] = result['ids'][:-1]
            return result
        check.scan_chunk = skimming
        self.addCleanup(setattr, check, 'scan_chunk', real)
        code, result = self.check(self.write('short.md', 'First line of the note.\n\nSecond line of the note.\n'))
        self.assertEqual((code, result['status']), (2, 'incomplete'))

    def test_unparsed_input_and_missing_rules_exit_2(self):
        cases = {
            'open.md': 'Intro line.\n\n```\ncode with no closing fence\n\nI hope this helps.\n',
            'bad.json': '{"title": ',
            'sheet.csv': 'a,b\n1,2\n',
            'broken.docx': 'not a zip archive',
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                code, result = self.check(self.write(name, text))
                self.assertEqual((code, result['status']), (2, 'incomplete'))
                self.assertTrue(result['reason'])
        self.assertEqual(self.check(self.root / 'absent.md')[0], 2)
        (self.root / 'image.md').write_bytes(b'\xff\xfe\x00\x01binary')
        self.assertEqual(self.check(self.root / 'image.md')[0], 2)

    def test_office_media_does_not_count_toward_the_size_limit(self):
        import zipfile
        deck = self.root / 'deck.pptx'
        slide = ('<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:p><a:r><a:t>'
                 'The pilot cut quote time for the sales team.</a:t></a:r></a:p></p:sld>')
        with zipfile.ZipFile(deck, 'w') as z:
            z.writestr('ppt/slides/slide1.xml', slide)
            z.writestr('ppt/media/image1.png', b'0' * 4000)
        big = self.write('big.md', 'A plain line of text.\n' * 200)
        original = check.MAX_BYTES
        check.MAX_BYTES = 2000
        try:
            code, result = self.check(deck)
            self.assertEqual(result['status'], 'scan-pass', result.get('reason'))
            self.assertEqual(result['coverage']['lines_reviewed'], 1)
            code, result = self.check(big)
            self.assertEqual((code, result['status']), (2, 'incomplete'))
        finally:
            check.MAX_BYTES = original

    def test_missing_or_broken_ledger_exits_2(self):
        path = self.write('note.md', 'The export job writes one file per client.\n')
        broken = dict(LEDGER, rules=LEDGER['rules'] + [{'id': 'bad', 'status': 'active', 'pattern': '(unclosed'}])
        self.ledger(broken)
        code, result = self.check(path)
        self.assertEqual(code, 2)
        self.assertIn('bad', result['reason'])
        (self.rules / 'patterns.json').unlink()
        self.assertEqual(self.check(path)[0], 2)
        empty = self.root / 'none'
        empty.mkdir()
        saved = {k: os.environ.pop(k, None) for k in ('WRITING_HOME', 'HUMANIZE_HOME', 'WRITING_POINTER')}
        os.environ.update(HUMANIZE_HOME=str(empty), WRITING_POINTER=str(empty / 'home'))
        try:
            self.assertEqual(self.check(path, rules=False)[0], 2)
        finally:
            for key in ('HUMANIZE_HOME', 'WRITING_POINTER'):
                os.environ.pop(key, None)
            os.environ.update({k: v for k, v in saved.items() if v is not None})

    def test_malformed_ledger_settings_fall_back_to_their_defaults_and_are_listed(self):
        path = self.write('reply.md', 'The report is attached.\n\nI hope this helps.\n')
        for key, value in (('hard_weight', '3'), ('hard_weight', None), ('min_words', [40]), ('flag_density', 0),
                           ('density_floor_words', 0), ('repeat_limit', True), ('repeat_density', 'x'),
                           ('em_dash', 'yes')):
            with self.subTest(**{key: value}):
                self.ledger(dict(LEDGER, config=dict(LEDGER['config'], **{key: value})))
                code, result = self.check(path)
                self.assertEqual((code, result['status']), (1, 'fail'))
                self.assertEqual([f['rule'] for f in result['findings']], ['residue'])
                self.assertEqual(len(result['config_ignored']), 1)
                self.assertIn(f'ledger setting "{key}"', result['config_ignored'][0])
                self.assertIn(f'ledger setting "{key}"', self.receipt(result)['steps'][0]['detail'])
        for config in ('strict', 7, ['hard_weight'], None):
            with self.subTest(config=config):
                self.ledger(dict(LEDGER, config=config))
                code, result = self.check(path)
                self.assertEqual(code, 1)
                self.assertIn('not an object', result['config_ignored'][0])
        self.ledger(LEDGER)
        self.assertNotIn('config_ignored', self.check(path)[1])
        no_config = {k: v for k, v in LEDGER.items() if k != 'config'}
        self.ledger(no_config)
        self.assertNotIn('config_ignored', self.check(path)[1])

    def test_malformed_rule_numbers_fall_back_and_unplaceable_rules_stop_the_run(self):
        path = self.write('reply.md', 'The report is attached.\n\nI hope this helps.\n')
        for key, value in (('weight', '3'), ('weight', None), ('min_count', 0), ('min_count', 1.5)):
            with self.subTest(**{key: value}):
                rules = [dict(LEDGER['rules'][0], **{key: value})] + LEDGER['rules'][1:]
                self.ledger(dict(LEDGER, rules=rules))
                code, result = self.check(path)
                self.assertNotEqual(result['status'], 'incomplete')
                self.assertIn(f'rule residue setting "{key}"', result['config_ignored'][0])
        for rules, words in (('all', 'not a list'), ({'id': 'x'}, 'not a list'), (['residue'], 'not an object'),
                             ([dict(LEDGER['rules'][0], id=None)], 'has no id'),
                             ([dict(LEDGER['rules'][0], scope=['general'])], 'scope'),
                             ([dict(LEDGER['rules'][0], registers='megan')], 'registers')):
            with self.subTest(rules=rules):
                self.ledger(dict(LEDGER, rules=rules))
                code, result = self.check(path)
                self.assertEqual((code, result['status']), (2, 'incomplete'))
                self.assertIn(words, result['reason'])
        self.ledger(['not', 'a', 'ledger'])
        code, result = self.check(path)
        self.assertEqual(code, 2)
        self.assertIn('not an object', result['reason'])

    def test_unreadable_command_line_still_returns_json_and_exit_2(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = check.main(['--file', 'note.md', '--json', '--no-such-option'])
        self.assertEqual((code, json.loads(out.getvalue())['status']), (2, 'incomplete'))

    def test_receipt_verifies_until_the_file_changes(self):
        path = self.write('note.md', 'The export job writes one file per client.\n')
        _, result = self.check(path)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check.main(['--verify-receipt', result['receipt']]), 0)
            path.write_text('The export job writes two files per client.\n')
            self.assertEqual(check.main(['--verify-receipt', result['receipt']]), 1)


class Review(Base):
    TEXT = ('# Renewal forecast\n\nThe forecast covers 14 accounts.\n\n' + REGRESSION[0] + '\n\n'
            '## Next step\n\n' + REGRESSION[1] + '\n')
    SOURCES = ['Synthetic renewal register', 'Synthetic call notes']

    def setUp(self):
        super().setUp()
        self.path = self.write('page.md', self.TEXT)
        self.work = self.root / 'review'
        self.sources = self.root / 'sources.json'
        self.sources.write_text(json.dumps(self.SOURCES))
        self.load_plan()
        self.policy = mock.patch.object(check.review_policy, 'validate', side_effect=lambda path, digest, docs, requested=None: {'round': requested or 1})
        self.policy.start()
        self.addCleanup(self.policy.stop)

    def check(self, path, *extra, **kwargs):
        if '--audience' not in extra:
            extra = (*extra, '--audience', 'external')
        if '--writer' not in extra:
            extra = (*extra, '--writer', 'writer-session')
        return super().check(path, *extra, **kwargs)

    def load_plan(self, *extra):
        self.check(self.path, '--prepare', str(self.work), '--sources', str(self.sources), *extra)
        self.plan = json.loads((self.work / 'assignments.json').read_text())
        self.lines = [line for worker in self.plan['workers'] for line in worker['lines']]

    def verdict(self, line, **change):
        first, last = check.edge_words(line['text'])
        v = {'id': line['id'], 'sha': line['sha'], 'section': line['section'], 'verdict': 'ok',
             'first_words': first, 'last_words': last,
             'portable': False, 'promise': False, 'tension': False,
             'claims': 'supported', 'source': self.SOURCES[0]}
        if line.get('flags'):
            v['flags'] = {f['rule']: False for f in line['flags']}
        return dict(v, **change)

    def verdicts(self, change=None, reviewer='independent reviewer'):
        out = [self.verdict(line, **(change or {}).get(line['id'], {})) for line in self.lines]
        return self.save('verdicts.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': reviewer, 'verdicts': out})

    def document_map(self, **change):
        data = {
            'reviewer': 'independent reviewer',
            'text_sha256': self.plan['text_sha256'], 'rules_sha256': self.plan['rules_sha256'],
            'reader': {'who': 'The finance lead for renewals', 'must_decide_or_do': 'Approve the forecast for 14 accounts'},
            'sections': [{'id': s['id'], 'point': 'States the forecast scope', 'reader_acts': True} for s in self.plan['sections']],
            'headings': [{'id': i, 'matches': True} for i in self.plan['headings']],
            'repeated_facts': [], 'counts': [], 'recaps': [], 'terms': [], 'leftover_lines': [], 'provenance': [],
            'numbers': [dict(n, source='Synthetic renewal register') for n in self.plan['numbers']],
            'confidentiality': {'list': 'Synthetic project list', 'retrieved': True, 'hits': []},
        }
        data.update(change)
        return self.save('map.json', data)

    def audit(self, verdicts, reviewer='independent reviewer', **change):
        self.check(self.path, '--verdicts', verdicts, '--prepare', str(self.work), '--sources', str(self.sources))
        sample = json.loads((self.work / 'assignments.json').read_text())['audit']
        return self.save('audit.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': reviewer,
                                        'verdicts': [self.verdict(line, **change) for line in sample]}), sample

    def save(self, name, data):
        path = self.work / name
        path.write_text(json.dumps(data))
        return str(path)

    def full(self, verdicts, document_map, *extra):
        return self.check(self.path, '--verdicts', verdicts, '--document-map', document_map,
                          '--sources', str(self.sources), *extra)

    def step(self, result, name):
        return {s['step']: s['status'] for s in result['steps']}[name]

    def detail(self, result, name):
        return {s['step']: s['detail'] for s in result['steps']}[name]

    def test_external_full_review_with_one_reviewer_and_no_child_processes(self):
        self.policy.stop()
        verdicts, document_map = self.verdicts(), self.document_map()
        audit, _ = self.audit(verdicts)
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual((code, result['status']), (0, 'pass'))
        self.assertEqual(self.receipt(result)['review_policy']['max_reviewers'], 1)
        changed = json.loads(Path(audit).read_text())
        changed['reviewer'] = 'second reviewer'
        Path(audit).write_text(json.dumps(changed))
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual((code, self.step(result, 'review policy')), (2, 'failed'))

    def test_prepare_writes_parts_outline_workers_and_a_prepare_receipt(self):
        self.assertEqual(self.plan['lines_in_scope'], 5)
        self.assertEqual(self.plan['numbers'], [{'id': '0002', 'quote': '14'}])
        self.assertEqual(self.plan['sources'], self.SOURCES)
        self.assertTrue((self.work / 'text' / 'part-001.md').read_text().startswith('[0001] L1: # Renewal forecast'))
        self.assertIn('[0004] L7: ## Next step', (self.work / 'outline.md').read_text())
        _, result = self.check(self.path, '--prepare', str(self.work))
        self.assertEqual(self.receipt(result)['purpose'], 'prepare')
        self.assertEqual(self.step(result, 'line pass'), 'not_run')
        long_path = self.write('long.md', '\n\n'.join(f'Line {n} names job {n}.' for n in range(1, 701)) + '\n')
        self.check(long_path, '--prepare', str(self.root / 'long-review'))
        plan = json.loads((self.root / 'long-review' / 'assignments.json').read_text())
        self.assertEqual(len(plan['parts']), 3)
        self.assertEqual(len(plan['workers']), 1)
        self.assertEqual(sum(len(w['lines']) for w in plan['workers']), 700)
        for name in plan['parts']:
            self.assertLessEqual(len((self.root / 'long-review' / 'text' / name).read_text().splitlines()), check.PART_LINES)

    def test_scan_alone_passes_the_regression_lines_and_says_what_did_not_run(self):
        code, result = self.check(self.path)
        self.assertEqual(code, 0)
        self.assertEqual((self.step(result, 'line pass'), self.step(result, 'claims check')), ('not_run', 'not_run'))

    def test_full_review_needs_every_pass(self):
        code, result = self.check(self.path, '--full')
        self.assertEqual(code, 2)
        self.assertEqual([self.step(result, s) for s in ('line pass', 'claims check', 'document pass')], ['failed'] * 3)

    def test_every_line_needs_a_verdict(self):
        data = json.loads(Path(self.verdicts()).read_text())
        data['verdicts'].pop()
        code, result = self.full(self.save('verdicts.json', data), self.document_map())
        self.assertEqual(code, 2)
        self.assertEqual(self.receipt(result)['line_pass']['no_verdict'], ['0005'])

    def test_yes_to_a_line_question_cannot_be_ok(self):
        code, result = self.full(self.verdicts({'0003': {'portable': True}}), self.document_map())
        self.assertEqual(code, 2)
        self.assertIn('needs a fix', self.receipt(result)['line_pass']['rejected'][0]['reason'])

    def test_quote_must_be_word_for_word(self):
        fix = {'verdict': 'fix', 'portable': True, 'rule': 'rule 3', 'quote': 'faster than systems', 'replacement': 'x'}
        code, result = self.full(self.verdicts({'0003': fix}), self.document_map())
        self.assertEqual(code, 2)
        self.assertIn('word for word', self.receipt(result)['line_pass']['rejected'][0]['reason'])

    def test_regression_lines_marked_fix_block(self):
        fixes = {
            '0003': {'verdict': 'fix', 'portable': True, 'rule': 'rule 3: fits any company',
                     'quote': 'adding products faster than its systems were built for',
                     'replacement': 'selling four product lines on a billing system configured for one'},
            '0005': {'verdict': 'fix', 'promise': True, 'rule': 'promised benefit', 'quote': REGRESSION[1], 'replacement': ''},
        }
        code, result = self.full(self.verdicts(fixes), self.document_map())
        self.assertEqual((code, result['status']), (1, 'fail'))
        self.assertEqual([f['id'] for f in result['findings']], ['0003', '0005'])
        self.assertEqual(result['findings'][1]['fix'], 'Cut these words.')
        self.assertEqual(self.step(result, 'spot audit'), 'not_run')

    def test_clean_round_passes_only_after_the_audit(self):
        verdicts, document_map = self.verdicts(), self.document_map()
        code, result = self.full(verdicts, document_map)
        self.assertEqual((code, self.step(result, 'line pass'), self.step(result, 'spot audit')), (2, 'ok', 'failed'))
        audit, sample = self.audit(verdicts)
        self.assertEqual(len(sample), 1)
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual((code, result['status'], self.step(result, 'spot audit')), (0, 'pass', 'ok'))
        self.assertIn('1 of the 5 lines marked ok', self.detail(result, 'spot audit'))
        self.assertFalse(self.receipt(result)['spot_audit']['independent'])

    def test_audit_by_the_same_reviewer_is_recorded_as_not_independent(self):
        verdicts, document_map = self.verdicts(reviewer='one agent'), self.document_map()
        audit, _ = self.audit(verdicts, reviewer='one agent')
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual(code, 0)
        self.assertIn('self-check by the same independent reviewer', self.detail(result, 'spot audit'))
        self.assertFalse(self.receipt(result)['spot_audit']['independent'])

    def test_audit_in_a_failed_round_says_what_it_covered(self):
        fix = {'0005': {'verdict': 'fix', 'promise': True, 'rule': 'promised benefit', 'quote': REGRESSION[1], 'replacement': ''}}
        verdicts, document_map = self.verdicts(fix), self.document_map()
        audit, sample = self.audit(verdicts)
        self.assertNotIn('0005', [line['id'] for line in sample])
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual((code, self.step(result, 'spot audit')), (1, 'ok'))
        self.assertIn('1 of the 4 lines marked ok', self.detail(result, 'spot audit'))
        self.assertIn('still fails on its 1 findings', self.detail(result, 'spot audit'))

    def test_spot_audit_miss_sends_the_review_back(self):
        verdicts, document_map = self.verdicts(), self.document_map()
        _, sample = self.audit(verdicts)
        miss = self.verdict(sample[0], verdict='fix', rule='rule 3', quote=sample[0]['text'][:10], replacement='')
        audit = self.save('audit.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': 'audit worker', 'verdicts': [miss]})
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual((code, self.step(result, 'spot audit')), (2, 'failed'))

    def test_verdicts_go_stale_when_a_line_or_the_rules_change(self):
        verdicts, document_map = self.verdicts(), self.document_map()
        self.path.write_text(self.TEXT.replace('14 accounts', '15 accounts'))
        code, result = self.full(verdicts, document_map)
        self.assertEqual(code, 2)
        rejected = {r['id'] for r in self.receipt(result)['line_pass']['rejected']}
        self.assertEqual(rejected, {'0002'})   # only the edited line goes back; its neighbours keep their verdicts
        self.assertEqual(self.step(result, 'document pass'), 'failed')
        self.path.write_text(self.TEXT)
        self.ledger(dict(LEDGER, version=2))
        self.assertEqual(self.full(verdicts, document_map)[0], 2)

    def test_prepare_carries_standing_verdicts_and_assigns_only_the_rest(self):
        verdicts = self.verdicts()
        self.path.write_text(self.TEXT.replace('14 accounts', '15 accounts'))
        self.load_plan('--verdicts', verdicts)
        self.assertEqual([line['id'] for line in self.lines], ['0002'])
        carried = json.loads((self.work / 'carried.json').read_text())
        self.assertEqual(sorted(v['id'] for v in carried['verdicts']), ['0001', '0003', '0004', '0005'])
        worker = self.save('verdicts-w1.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': 'worker 2',
                                                'verdicts': [self.verdict(line) for line in self.lines]})
        code, result = self.check(self.path, '--verdicts', str(self.work / 'carried.json'), worker,
                                  '--document-map', self.document_map(), '--sources', str(self.sources))
        self.assertEqual(self.step(result, 'line pass'), 'ok')

    def test_round_three_logs_style_findings_and_blocks_on_errors(self):
        style = {'0003': {'verdict': 'fix', 'severity': 'style', 'rule': 'R13: two words for one thing',
                          'quote': 'adding products', 'replacement': 'selling products'}}
        verdicts, document_map = self.verdicts(style), self.document_map()
        code, result = self.full(verdicts, document_map)
        self.assertEqual((code, [f['id'] for f in result['findings']]), (1, ['0003']))
        code, result = self.full(verdicts, document_map, '--round', '3')
        self.assertEqual((result['findings'], [f['id'] for f in result['logged']]), ([], ['0003']))
        error = {'0003': dict(style['0003'], severity='error')}
        code, result = self.full(self.verdicts(error), document_map, '--round', '3')
        self.assertEqual([f['id'] for f in result['findings']], ['0003'])

    def test_owner_decisions_block_and_are_counted_apart(self):
        ask = {'0003': {'verdict': 'fix', 'owner_call': True, 'claims': 'unsupported', 'rule': 'K2: no source',
                        'quote': 'adding products', 'replacement': ''}}
        code, result = self.full(self.verdicts(ask), self.document_map(), '--round', '3')
        self.assertEqual((code, result['owner_decisions']), (1, 1))
        self.assertTrue(result['findings'][0]['rule'].startswith('owner decision: '))

    def test_audit_miss_is_settled_by_a_rule_recheck(self):
        verdicts, document_map = self.verdicts(), self.document_map()
        _, sample = self.audit(verdicts)
        miss = self.verdict(sample[0], verdict='fix', rule='R6: fits any page', quote=sample[0]['text'][:10],
                            replacement='')
        audit = self.save('audit.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': 'audit worker',
                                         'verdicts': [miss]})
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertIn('--recheck', self.detail(result, 'spot audit'))
        sweep = {'rules_sha256': self.plan['rules_sha256'], 'reviewer': 'recheck worker', 'rules': ['R6'],
                 'verdicts': [{'id': line['id'], 'sha': line['sha'], 'verdict': 'ok',
                               'first_words': check.edge_words(line['text'])[0],
                               'last_words': check.edge_words(line['text'])[1]} for line in self.lines]}
        code, result = self.full(verdicts, document_map, '--audit', audit, '--recheck', self.save('recheck.json', sweep))
        self.assertEqual((code, self.step(result, 'spot audit')), (1, 'ok'))
        self.assertEqual([f['id'] for f in result['findings']], [sample[0]['id']])
        sweep['rules'] = ['R13']
        code, result = self.full(verdicts, document_map, '--audit', audit, '--recheck', self.save('recheck.json', sweep))
        self.assertEqual((code, self.step(result, 'spot audit')), (2, 'failed'))

    def test_claims_check_needs_a_source_list_and_an_answer_on_every_line(self):
        verdicts, document_map = self.verdicts(), self.document_map()
        code, result = self.check(self.path, '--verdicts', verdicts, '--document-map', document_map)
        self.assertEqual((code, self.step(result, 'claims check'), self.step(result, 'line pass')), (2, 'failed', 'ok'))
        cases = {'no answer': {'claims': None}, 'unlisted source': {'source': 'A memo nobody listed'},
                 'unsupported and ok': {'claims': 'unsupported'}}
        for name, change in cases.items():
            with self.subTest(name=name):
                code, result = self.full(self.verdicts({'0002': change}), document_map)
                self.assertEqual((code, self.step(result, 'claims check')), (2, 'failed'))
                self.assertEqual(self.receipt(result)['claims_check']['problems'][0]['id'], '0002')
        fix = {'claims': 'unsupported', 'verdict': 'fix', 'rule': 'K2: no listed source states it',
               'quote': '14 accounts', 'replacement': ''}
        code, result = self.full(self.verdicts({'0002': fix, '0001': {'claims': 'none', 'source': ''}}), document_map)
        self.assertEqual((code, self.step(result, 'claims check')), (1, 'ok'))

    def test_document_map_blocks_untraced_numbers_and_missing_sections(self):
        code, result = self.full(self.verdicts(), self.document_map(numbers=[]))
        self.assertEqual(code, 2)
        self.assertIn('14', self.receipt(result)['document_pass']['problems'][0])
        untraced = [dict(n, source='') for n in self.plan['numbers']]
        code, result = self.full(self.verdicts(), self.document_map(numbers=untraced))
        self.assertEqual((code, result['findings'][0]['rule']), (1, 'document-pass: number with no source'))
        code, result = self.full(self.verdicts(), self.document_map(sections=[]))
        self.assertEqual(code, 2)
        data = json.loads(Path(self.document_map()).read_text())
        del data['provenance']
        self.assertEqual(self.full(self.verdicts(), self.save('map.json', data))[0], 2)

    def test_confidentiality_list_must_be_retrieved_or_declared_not_to_apply(self):
        guessed = {'list': 'Rebuilt from a memo because the Hub returned nothing', 'retrieved': False, 'hits': []}
        code, result = self.full(self.verdicts(), self.document_map(confidentiality=guessed))
        self.assertEqual((code, self.step(result, 'document pass')), (2, 'failed'))
        self.assertIn('do not rebuild', self.receipt(result)['document_pass']['problems'][0])
        none = {'none_applies': 'Internal note with no client project', 'hits': []}
        code, result = self.full(self.verdicts(), self.document_map(confidentiality=none))
        self.assertEqual(self.step(result, 'document pass'), 'ok')

    def test_document_findings_block_and_one_fault_is_counted_once(self):
        sections = [{'id': s['id'], 'point': 'States the forecast scope', 'reader_acts': s['id'] != '0004'}
                    for s in self.plan['sections']]
        code, result = self.full(self.verdicts(), self.document_map(
            sections=sections, provenance=[{'id': '0002', 'quote': 'The forecast covers'}],
            counts=[{'id': '0002', 'quote': '14 accounts', 'stated': 14, 'listed': 12}]))
        self.assertEqual((code, len(result['findings'])), (1, 3))
        fix = {'0005': {'verdict': 'fix', 'promise': True, 'rule': 'F9: recaps the forecast', 'quote': REGRESSION[1], 'replacement': ''}}
        code, result = self.full(self.verdicts(fix), self.document_map(
            recaps=[{'id': '0005'}], terms=[{'terms': ['forecast', 'risk'], 'ids': ['0002', '0005'], 'merged_with': '0005'}]))
        self.assertEqual((code, len(result['findings'])), (1, 1))
        self.assertEqual(len(result['findings'][0]['also']), 2)
        code, result = self.full(self.verdicts(fix), self.document_map(
            terms=[{'terms': ['forecast', 'risk'], 'ids': ['0002', '0005']}]))
        self.assertEqual(len(result['findings']), 2)

    def numbers_page(self):
        self.path = self.write('plan.md', '# Rollout plan\n\nDraft for the board.\n\n## Scope\n\n'
                               'Phase 1 covers 14 accounts. Phases 2 and 3 follow, and step 4 is open.\n\n'
                               'Adding the last product took four separate projects.\n\n'
                               '## Roadmap\n\nThree phases run to 2028. Phase 1 covers 14 accounts.\n')
        self.work = self.root / 'plan-review'
        self.load_plan()

    def test_labels_are_not_numbers_and_number_words_need_a_source_or_a_count(self):
        self.numbers_page()
        self.assertEqual([(n['id'], n['quote']) for n in self.plan['numbers']],
                         [('0004', '14'), ('0007', '14'), ('0005', 'four'), ('0007', 'Three')])
        digits = [dict(n, source=self.SOURCES[0]) for n in self.plan['numbers'] if n.get('kind') != 'word']
        code, result = self.full(self.verdicts(), self.document_map(numbers=digits))
        self.assertEqual(code, 2)
        self.assertEqual(len(self.receipt(result)['document_pass']['problems']), 2)
        covered = digits + [{'id': '0005', 'quote': 'four separate projects', 'source': self.SOURCES[1]}]
        counted = [{'id': '0007', 'quote': 'Three phases', 'stated': 3, 'listed': 3}]
        code, result = self.full(self.verdicts(), self.document_map(numbers=covered, counts=counted))
        self.assertEqual(self.step(result, 'document pass'), 'ok')

    def test_title_section_needs_no_reader_action_and_a_declared_structure_repeat_does_not_block(self):
        self.numbers_page()
        numbers = [dict(n, source=self.SOURCES[0]) for n in self.plan['numbers']]

        def sections(title=True):
            out = [{'id': s['id'], 'point': 'States the rollout scope', 'reader_acts': True} for s in self.plan['sections']]
            out[0] = {'id': out[0]['id'], 'point': 'Names the page and marks it a draft', 'role': 'title'}
            if not title:
                out[1] = dict(out[1], role='title')
                del out[1]['reader_acts']
            return out
        repeat = [{'ids': ['0004', '0007'], 'quote': 'Phase 1 covers 14 accounts'}]
        code, result = self.full(self.verdicts(), self.document_map(numbers=numbers, sections=sections(), repeated_facts=repeat))
        self.assertEqual((code, result['findings'][0]['rule']), (1, 'document-pass: fact stated more than once'))
        declared = {'reason': 'Each scope item returns as a roadmap item', 'sections': ['0003', '0006']}
        # This page has 7 lines, so its one declared repeat covers two of them; the share limit has its own test.
        self.addCleanup(setattr, check, 'STRUCTURAL_SHARE', check.STRUCTURAL_SHARE)
        check.STRUCTURAL_SHARE = 3
        code, result = self.full(self.verdicts(), self.document_map(
            numbers=numbers, sections=sections(), structural_repeat=declared, repeated_facts=[dict(repeat[0], structural=True)]))
        self.assertEqual((self.step(result, 'document pass'), result['findings']), ('ok', []))
        self.assertEqual(len(self.receipt(result)['document_pass']['declared_repeats']), 1)
        code, result = self.full(self.verdicts(), self.document_map(
            numbers=numbers, sections=sections(), repeated_facts=[dict(repeat[0], structural=True)]))
        self.assertEqual(self.step(result, 'document pass'), 'failed')
        self.addCleanup(setattr, check, 'TITLE_SECTION_LINES', check.TITLE_SECTION_LINES)
        check.TITLE_SECTION_LINES = 2
        code, result = self.full(self.verdicts(), self.document_map(numbers=numbers, sections=sections(title=False)))
        self.assertIn('a title section has at most', self.receipt(result)['document_pass']['problems'][0])

    def test_scanner_flag_never_blocks_alone_and_is_answered_apart_from_the_fix(self):
        self.path = self.write('flag.md', 'The team owns intake, scoping and pricing for 14 accounts.\n')
        code, result = self.check(self.path)
        self.assertEqual((code, result['findings'], result['review']), (0, [], 1))
        self.work = self.root / 'flag-review'
        self.load_plan()
        line = self.lines[0]
        self.assertEqual(line['flags'], [{'rule': 'three', 'text': 'intake, scoping and pricing'}])
        document_map = self.document_map()

        def run(**change):
            verdict = self.verdict(line, **change)
            if change.get('flags') is None:
                verdict.pop('flags', None)
            return self.full(self.save('verdicts.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': 'worker',
                                                         'verdicts': [verdict]}), document_map)
        code, result = run(flags=None)
        self.assertIn('flags.three', self.receipt(result)['line_pass']['rejected'][0]['reason'])
        self.assertEqual(self.step(run(flags={'three': True})[1], 'line pass'), 'failed')
        self.assertEqual(self.step(run(flags={'three': False})[1], 'line pass'), 'ok')
        code, result = run(flags={'three': False}, verdict='fix', rule='K3: no source for the account count',
                           quote='14 accounts', replacement='the accounts in the renewal register')
        self.assertEqual((code, self.step(result, 'line pass'), result['findings'][0]['rule']),
                         (1, 'ok', 'line-pass: K3: no source for the account count'))

    def test_each_verdict_quotes_the_first_and_last_words_of_its_own_line(self):
        swapped = {'0003': {'first_words': 'Revenue risk shows'}}
        code, result = self.full(self.verdicts(swapped), self.document_map())
        self.assertEqual(code, 2)
        self.assertIn('do not match', self.receipt(result)['line_pass']['rejected'][0]['reason'])
        missing = {'0003': {'last_words': ''}}
        code, result = self.full(self.verdicts(missing), self.document_map())
        self.assertIn('first_words and last_words', self.receipt(result)['line_pass']['rejected'][0]['reason'])
        spaced = {'0003': {'first_words': '  The   company is '}}
        self.assertEqual(self.step(self.full(self.verdicts(spaced), self.document_map())[1], 'line pass'), 'ok')

    def test_verdicts_from_the_writer_are_rejected(self):
        verdicts, document_map = self.verdicts(reviewer='session-a'), self.document_map()
        code, result = self.full(verdicts, document_map, '--writer', 'session-a')
        self.assertEqual((code, self.step(result, 'line pass')), (2, 'failed'))
        self.assertIn('session that wrote the piece', self.detail(result, 'line pass'))
        unnamed = json.loads(Path(verdicts).read_text())
        unnamed['reviewer'] = ''
        code, result = self.full(self.save('verdicts.json', unnamed), document_map)
        self.assertIn('does not name its reviewer', self.detail(result, 'line pass'))
        # The hook's log names the session that wrote the piece and the one that wrote the verdict file.
        verdicts = self.verdicts(reviewer='worker 1')
        self.agent_home.mkdir(exist_ok=True)
        log = [{'session': 'writer-session', 'path': str(self.path.resolve())},
               {'session': 'reviewer-session', 'path': str(self.path.resolve())},
               {'session': 'writer-session', 'path': str(Path(verdicts).resolve())}]
        (self.agent_home / 'writers.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in log))
        code, result = self.full(verdicts, document_map)
        self.assertEqual(self.step(result, 'line pass'), 'failed')
        self.assertIn('writer-session', self.detail(result, 'line pass'))
        (self.agent_home / 'writers.jsonl').write_text(json.dumps(log[0]) + '\n' + json.dumps(log[1]) + '\n')
        self.assertEqual(self.step(self.full(verdicts, document_map)[1], 'line pass'), 'ok')
        audit, _ = self.audit(verdicts, reviewer='writer-session')
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual((code, self.step(result, 'spot audit')), (2, 'failed'))

    def write_log(self, *items):
        self.agent_home.mkdir(exist_ok=True)
        (self.agent_home / 'writers.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in items))

    def test_a_reviewer_who_later_rewrote_the_piece_is_rejected(self):
        verdicts, document_map = self.verdicts(reviewer='worker 1'), self.document_map()
        piece, current = str(self.path.resolve()), hashlib.sha256(self.path.read_bytes()).hexdigest()
        # The reviewer's session rewrote the piece after the writer, then wrote the verdict file.
        self.write_log({'session': 'writer-session', 'path': piece, 'sha256': '0' * 64},
                       {'session': 'reviewer-session', 'path': piece, 'sha256': current},
                       {'session': 'reviewer-session', 'path': str(Path(verdicts).resolve())})
        code, result = self.full(verdicts, document_map)
        self.assertEqual((code, self.step(result, 'line pass')), (2, 'failed'))
        self.assertIn('reviewer-session', self.detail(result, 'line pass'))
        self.assertEqual(self.receipt(result)['writers'], ['reviewer-session', 'writer-session'])
        # The same rewrite, with the reviewer named only by the session field of the verdict file.
        named = json.loads(Path(verdicts).read_text())
        named['session'] = 'reviewer-session'
        named_path = self.save('verdicts-named.json', named)
        self.write_log({'session': 'writer-session', 'path': piece, 'sha256': '0' * 64},
                       {'session': 'reviewer-session', 'path': piece, 'sha256': current})
        code, result = self.full(named_path, document_map)
        self.assertEqual((code, self.step(result, 'line pass')), (2, 'failed'))
        self.assertIn('reviewer-session', self.detail(result, 'line pass'))
        # A rewrite in the middle counts too: the reviewer edited, then the writer brought it to its current text.
        self.write_log({'session': 'writer-session', 'path': piece, 'sha256': '0' * 64},
                       {'session': 'reviewer-session', 'path': piece, 'sha256': '1' * 64},
                       {'session': 'writer-session', 'path': piece, 'sha256': current})
        self.assertEqual(self.step(self.full(named_path, document_map)[1], 'line pass'), 'failed')
        # An audit file from the session that rewrote the piece is rejected the same way.
        self.write_log({'session': 'writer-session', 'path': piece, 'sha256': '0' * 64},
                       {'session': 'auditor-session', 'path': piece, 'sha256': current})
        audit, _ = self.audit(verdicts, reviewer='auditor-session')
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual((code, self.step(result, 'spot audit')), (2, 'failed'))

    def test_prepare_never_carries_a_verdict_from_the_writer(self):
        named = json.loads(Path(self.verdicts(reviewer='worker 1')).read_text())
        named['session'] = 'writer-session'
        verdicts, document_map = self.save('verdicts.json', named), self.document_map()
        self.write_log({'session': 'writer-session', 'path': str(self.path.resolve())})
        self.assertEqual(self.step(self.full(verdicts, document_map)[1], 'line pass'), 'failed')
        self.path.write_text(self.TEXT.replace('14 accounts', '15 accounts'))
        self.write_log({'session': 'writer-session', 'path': str(self.path.resolve())})
        code, result = self.check(self.path, '--prepare', str(self.work), '--verdicts', verdicts,
                                  '--sources', str(self.sources))
        self.assertEqual((code, self.step(result, 'prepare')), (2, 'failed'))
        self.assertIn('writer-session', self.detail(result, 'prepare'))
        self.assertFalse((self.work / 'carried.json').exists())
        plan = json.loads((self.work / 'assignments.json').read_text())
        self.assertEqual(sum(len(w['lines']) for w in plan['workers']), 5)   # every line goes to a new reviewer
        self.assertNotIn('audit', plan)
        # Validation with what prepare left still returns incomplete.
        code, result = self.full(verdicts, document_map)
        self.assertEqual((code, result['status'], self.step(result, 'line pass')), (2, 'incomplete', 'failed'))

    def test_carried_verdicts_keep_the_reviewer_session_and_writer_history(self):
        named = json.loads(Path(self.verdicts(reviewer='worker 1')).read_text())
        named['session'] = 'reviewer-session'
        verdicts, document_map = self.save('verdicts.json', named), self.document_map()
        piece, verdict_file = str(self.path.resolve()), str(Path(verdicts).resolve())
        self.path.write_text(self.TEXT.replace('14 accounts', '15 accounts'))
        self.write_log({'session': 'writer-session', 'path': piece},
                       {'session': 'verdict-session', 'path': verdict_file})
        self.load_plan('--verdicts', verdicts)
        carried_path = self.work / 'carried.json'
        carried = json.loads(carried_path.read_text())
        self.assertEqual((carried['reviewer'], carried['session'], carried['verdict_writers']),
                         ('worker 1', 'reviewer-session', ['verdict-session']))
        worker = self.save('verdicts-w1.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': 'worker 2',
                                                'verdicts': [self.verdict(line) for line in self.lines]})
        code, result = self.check(self.path, '--verdicts', str(carried_path), worker,
                                  '--document-map', document_map, '--sources', str(self.sources))
        self.assertEqual(self.step(result, 'line pass'), 'ok')
        # The log later shows the reviewer's session and the verdict file's writer changing the piece. The
        # carried file still names both, so the merged set is rejected though the original files are gone.
        Path(verdicts).unlink()
        for session in ('reviewer-session', 'verdict-session'):
            self.write_log({'session': 'writer-session', 'path': piece}, {'session': session, 'path': piece})
            code, result = self.check(self.path, '--verdicts', str(carried_path), worker,
                                      '--document-map', document_map, '--sources', str(self.sources))
            self.assertEqual((code, result['status'], self.step(result, 'line pass')), (2, 'incomplete', 'failed'))
            self.assertIn(session, self.detail(result, 'line pass'))

    def test_unreadable_writer_log_and_an_unnamed_worker_file_make_the_review_incomplete(self):
        verdicts, document_map = self.verdicts(reviewer='worker 1'), self.document_map()
        self.agent_home.mkdir(exist_ok=True)
        (self.agent_home / 'writers.jsonl').mkdir()   # a log that exists but cannot be read
        code, result = self.full(verdicts, document_map)
        self.assertEqual((code, self.step(result, 'review policy')), (2, 'failed'))
        self.assertIn('writer log', self.detail(result, 'review policy'))
        (self.agent_home / 'writers.jsonl').rmdir()
        unnamed = self.save('verdicts-w2.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': '',
                                                 'verdicts': []})
        code, result = self.check(self.path, '--verdicts', verdicts, unnamed, '--document-map', document_map,
                                  '--sources', str(self.sources))
        self.assertEqual(self.step(result, 'line pass'), 'failed')
        self.assertIn('does not name its reviewer', self.detail(result, 'line pass'))

    def test_writers_count_up_to_the_content_under_review(self):
        verdicts, document_map = self.verdicts(reviewer='later-session'), self.document_map()
        piece, current = str(self.path.resolve()), hashlib.sha256(self.path.read_bytes()).hexdigest()
        # A write logged after the last one that produced the reviewed text did not write that text.
        self.write_log({'session': 'writer-session', 'path': piece, 'sha256': current},
                       {'session': 'later-session', 'path': piece, 'sha256': '2' * 64})
        code, result = self.full(verdicts, document_map)
        self.assertEqual(self.step(result, 'line pass'), 'ok')
        self.assertEqual(self.receipt(result)['writers'], ['writer-session'])
        # When no logged write matches the current text, every logged write counts.
        self.write_log({'session': 'writer-session', 'path': piece},
                       {'session': 'later-session', 'path': piece, 'sha256': '2' * 64})
        code, result = self.full(verdicts, document_map)
        self.assertEqual(self.step(result, 'line pass'), 'failed')
        self.assertIn('later-session', self.detail(result, 'line pass'))

    def test_map_that_marks_over_a_tenth_of_lines_structural_is_rejected(self):
        self.numbers_page()
        numbers = [dict(n, source=self.SOURCES[0]) for n in self.plan['numbers']]
        sections = [{'id': s['id'], 'point': 'States the rollout scope', 'reader_acts': True} for s in self.plan['sections']]
        declared = {'reason': 'Each scope item returns as a roadmap item', 'sections': ['0003', '0006']}
        repeat = [{'ids': ['0004', '0007'], 'quote': 'Phase 1 covers 14 accounts', 'structural': True}]
        code, result = self.full(self.verdicts(), self.document_map(
            numbers=numbers, sections=sections, structural_repeat=declared, repeated_facts=repeat))
        self.assertEqual(self.step(result, 'document pass'), 'failed')
        self.assertIn('structural repeats', self.receipt(result)['document_pass']['problems'][0])

    def test_receipt_claiming_pass_without_a_line_pass_does_not_verify(self):
        _, result = self.check(self.path)
        saved = self.receipt(result)
        saved['status'] = 'pass'
        Path(result['receipt']).write_text(json.dumps(saved))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(check.main(['--verify-receipt', result['receipt']]), 1)
        self.assertIn('scan-pass', out.getvalue())


if __name__ == '__main__':
    unittest.main()
