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

    def test_register_adds_rules_scoped_to_it_and_any_name_is_accepted(self):
        path = self.write('bio.md', 'She leads delivery, whether it is a migration or a rebuild.\n')
        self.assertEqual(self.check(path)[0], 0)
        code, result = self.check(path, '--register', 'author')
        self.assertEqual((code, result['findings'][0]['rule']), (1, 'author-only'))
        self.assertEqual(self.check(path, '--register', 'slack to a client sponsor')[0], 0)


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

    def setUp(self):
        super().setUp()
        self.path = self.write('page.md', self.TEXT)
        self.work = self.root / 'review'
        self.check(self.path, '--prepare', str(self.work))
        self.plan = json.loads((self.work / 'assignments.json').read_text())
        self.lines = [line for worker in self.plan['workers'] for line in worker['lines']]

    def verdicts(self, change=None):
        out = []
        for line in self.lines:
            v = {'id': line['id'], 'sha': line['sha'], 'section': line['section'], 'verdict': 'ok',
                 'portable': False, 'promise': False, 'tension': False}
            out.append(dict(v, **(change or {}).get(line['id'], {})))
        return self.save('verdicts.json', {'rules_sha256': self.plan['rules_sha256'], 'verdicts': out})

    def document_map(self, **change):
        data = {
            'text_sha256': self.plan['text_sha256'], 'rules_sha256': self.plan['rules_sha256'],
            'reader': {'who': 'The finance lead for renewals', 'must_decide_or_do': 'Approve the forecast for 14 accounts'},
            'sections': [{'id': s['id'], 'point': 'States the forecast scope', 'reader_acts': True} for s in self.plan['sections']],
            'headings': [{'id': i, 'matches': True} for i in self.plan['headings']],
            'repeated_facts': [], 'counts': [], 'recaps': [], 'terms': [], 'leftover_lines': [], 'provenance': [],
            'numbers': [dict(n, source='Synthetic renewal register') for n in self.plan['numbers']],
            'confidentiality': {'list': 'Synthetic fixture; no project list applies', 'hits': []},
        }
        data.update(change)
        return self.save('map.json', data)

    def save(self, name, data):
        path = self.work / name
        path.write_text(json.dumps(data))
        return str(path)

    def full(self, verdicts, document_map, *extra):
        return self.check(self.path, '--verdicts', verdicts, '--document-map', document_map, *extra)

    def step(self, result, name):
        return {s['step']: s['status'] for s in result['steps']}[name]

    def test_prepare_writes_parts_outline_and_workers(self):
        self.assertEqual(self.plan['lines_in_scope'], 5)
        self.assertEqual(self.plan['numbers'], [{'id': '0002', 'quote': '14'}])
        self.assertTrue((self.work / 'text' / 'part-001.md').read_text().startswith('[0001] L1: # Renewal forecast'))
        self.assertIn('[0004] L7: ## Next step', (self.work / 'outline.md').read_text())
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
        self.assertEqual(self.step(result, 'line pass'), 'not_run')

    def test_full_review_needs_both_passes(self):
        code, result = self.check(self.path, '--full')
        self.assertEqual(code, 2)
        self.assertEqual((self.step(result, 'line pass'), self.step(result, 'document pass')), ('failed', 'failed'))

    def test_every_line_needs_a_verdict(self):
        path = self.verdicts()
        data = json.loads(Path(path).read_text())
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

    def test_regression_lines_marked_fix_block_and_a_clean_review_passes(self):
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
        code, result = self.full(self.verdicts(), self.document_map())
        self.assertEqual((code, self.step(result, 'line pass'), self.step(result, 'document pass')), (0, 'ok', 'ok'))

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

    def test_document_map_findings_block(self):
        sections = [{'id': s['id'], 'point': 'States the forecast scope', 'reader_acts': s['id'] != '0004'}
                    for s in self.plan['sections']]
        code, result = self.full(self.verdicts(), self.document_map(
            sections=sections, provenance=[{'id': '0002', 'quote': 'The forecast covers'}],
            counts=[{'id': '0002', 'quote': '14 accounts', 'stated': 14, 'listed': 12}]))
        self.assertEqual(code, 1)
        self.assertEqual(len(result['findings']), 3)

    def test_spot_audit_miss_sends_the_review_back(self):
        verdicts, document_map = self.verdicts(), self.document_map()
        self.check(self.path, '--verdicts', verdicts, '--document-map', document_map, '--prepare', str(self.work))
        sample = json.loads((self.work / 'assignments.json').read_text())['audit']
        self.assertEqual(len(sample), 1)
        line = sample[0]
        base = {'id': line['id'], 'sha': line['sha'], 'section': line['section'],
                'portable': False, 'promise': False, 'tension': False}
        clean = self.save('audit.json', {'rules_sha256': self.plan['rules_sha256'], 'verdicts': [dict(base, verdict='ok')]})
        code, result = self.full(verdicts, document_map, '--audit', clean)
        self.assertEqual((code, self.step(result, 'spot audit')), (0, 'ok'))
        miss = dict(base, verdict='fix', rule='rule 3', quote=line['text'][:10], replacement='')
        code, result = self.full(verdicts, document_map, '--audit',
                                 self.save('audit.json', {'rules_sha256': self.plan['rules_sha256'], 'verdicts': [miss]}))
        self.assertEqual((code, self.step(result, 'spot audit')), (2, 'failed'))


if __name__ == '__main__':
    unittest.main()
