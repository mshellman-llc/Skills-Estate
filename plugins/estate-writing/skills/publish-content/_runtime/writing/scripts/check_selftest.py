#!/usr/bin/env python3
"""Self-test for check.py. Every file and ledger is synthetic and lives in a temporary folder."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest

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
    def test_pass_has_the_agreed_shape_and_a_receipt(self):
        code, result = self.check(self.write('note.md', '# Release note\n\nThe export job now writes one file per client.\n'))
        self.assertEqual(code, 0)
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['coverage']['lines_total'], 2)
        self.assertEqual(result['coverage']['lines_reviewed'], 2)
        self.assertEqual(result['findings'], [])
        for key in ('status', 'coverage', 'findings', 'receipt'):
            self.assertIn(key, result)
        saved = self.receipt(result)
        self.assertEqual(saved['status'], 'pass')
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
            self.assertEqual(result['status'], 'pass', result.get('reason'))
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

    def load_plan(self, *extra):
        self.check(self.path, '--prepare', str(self.work), '--sources', str(self.sources), *extra)
        self.plan = json.loads((self.work / 'assignments.json').read_text())
        self.lines = [line for worker in self.plan['workers'] for line in worker['lines']]

    def verdict(self, line, **change):
        v = {'id': line['id'], 'sha': line['sha'], 'section': line['section'], 'verdict': 'ok',
             'portable': False, 'promise': False, 'tension': False,
             'claims': 'supported', 'source': self.SOURCES[0]}
        if line.get('flags'):
            v['flags'] = {f['rule']: False for f in line['flags']}
        return dict(v, **change)

    def verdicts(self, change=None, reviewer='line-pass worker'):
        out = [self.verdict(line, **(change or {}).get(line['id'], {})) for line in self.lines]
        return self.save('verdicts.json', {'rules_sha256': self.plan['rules_sha256'], 'reviewer': reviewer, 'verdicts': out})

    def document_map(self, **change):
        data = {
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

    def audit(self, verdicts, reviewer='audit worker', **change):
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
        self.assertTrue(all(len(w['lines']) <= check.WORKER_LINES for w in plan['workers']))
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
        self.assertEqual((code, self.step(result, 'spot audit')), (0, 'ok'))
        self.assertIn('1 of the 5 lines marked ok', self.detail(result, 'spot audit'))
        self.assertTrue(self.receipt(result)['spot_audit']['independent'])

    def test_audit_by_the_same_reviewer_is_recorded_as_not_independent(self):
        verdicts, document_map = self.verdicts(reviewer='one agent'), self.document_map()
        audit, _ = self.audit(verdicts, reviewer='one agent')
        code, result = self.full(verdicts, document_map, '--audit', audit)
        self.assertEqual(code, 0)
        self.assertIn('not independent', self.detail(result, 'spot audit'))
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
        self.assertEqual(rejected, {'0001', '0002', '0003'})
        self.assertEqual(self.step(result, 'document pass'), 'failed')
        self.path.write_text(self.TEXT)
        self.ledger(dict(LEDGER, version=2))
        self.assertEqual(self.full(verdicts, document_map)[0], 2)

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
            return self.full(self.save('verdicts.json', {'rules_sha256': self.plan['rules_sha256'], 'verdicts': [verdict]}), document_map)
        code, result = run(flags=None)
        self.assertIn('flags.three', self.receipt(result)['line_pass']['rejected'][0]['reason'])
        self.assertEqual(self.step(run(flags={'three': True})[1], 'line pass'), 'failed')
        self.assertEqual(self.step(run(flags={'three': False})[1], 'line pass'), 'ok')
        code, result = run(flags={'three': False}, verdict='fix', rule='K3: no source for the account count',
                           quote='14 accounts', replacement='the accounts in the renewal register')
        self.assertEqual((code, self.step(result, 'line pass'), result['findings'][0]['rule']),
                         (1, 'ok', 'line-pass: K3: no source for the account count'))


if __name__ == '__main__':
    unittest.main()
