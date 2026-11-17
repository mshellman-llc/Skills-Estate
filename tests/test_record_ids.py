"""C28: record IDs and sentence locators in reader prose, with system-facing text left out."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/writing-diagnostics/scripts'
sys.path.insert(0, str(SCRIPTS))
from prose_check import check
from record_ids import RULE, html_reader_prose, markdown_reader_prose, record_id_finding
from writing_check import authored_text, strict_config

DENSE = ('PER-01 asked for restricted delivery in S1. DEC-02 settled the sender, and RI-09 tracks the risk. '
         'PER-01 repeated the request in S2, citing I1.s24 and I1.s31. CAP-15 depends on VAL-02 and DEC-02.')
NAMED = ('Megan asked for restricted email delivery in her first interview. The email-sender decision (DEC-02) '
         'settled who sends, and the delivery risk stays open. She repeated the request in the second interview.')


class RecordIdTests(unittest.TestCase):
    def finding(self, text):
        found = [f for f in check(text)[0] if f.rule == RULE]
        return found[0] if found else None

    def write(self, folder, name, content):
        path = Path(folder) / name
        path.write_text(content, encoding='utf-8')
        return path

    def test_id_dense_prose_is_flagged_with_a_naming_instruction(self):
        finding = self.finding(DENSE)
        self.assertIsNotNone(finding)
        self.assertEqual(finding.severity, 'FAIL')
        self.assertIn('Name the thing in plain words', finding.message)
        self.assertIn('budget 2.0', finding.message)

    def test_plain_names_with_one_id_beside_a_name_pass(self):
        self.assertIsNone(self.finding(NAMED))
        self.assertIsNone(self.finding('Restricted email delivery (CAP-15) ships first.'))

    def test_ids_opening_sentences_rows_or_repeated_count(self):
        self.assertEqual(record_id_finding('DEC-02 settled it. RI-09 stays open. CAP-15 waits.')[0], 3)
        rows = '| ID | Item |\n| --- | --- |\n| R-001 | Sandbox access |\n| R-002 | Data volume |\n| R-003 | Legal review |'
        self.assertEqual(record_id_finding(rows)[0], 3)
        renamed = '| Item | ID |\n| --- | --- |\n| Sandbox access | R-001 |\n| Data volume | R-002 |\n| Legal review | R-003 |'
        self.assertIsNone(record_id_finding(renamed))

    def test_a_sentence_carrying_three_ids_counts_each(self):
        self.assertEqual(record_id_finding('The page cites S1, S2 and S3 for this claim.')[0], 3)

    def test_source_index_sections_code_and_link_targets_are_system_facing(self):
        text = (NAMED + '\n\n## Source index\n\n' + DENSE + '\n\n## Next steps\n\nSend the brief.\n\n'
                '```json\n{"id": "PER-01", "refs": ["S1", "S2", "S3"]}\n```\n\nRun `check DEC-02 RI-09 CAP-15`. '
                'See [the decision](records.md#DEC-02).')
        self.assertIsNone(self.finding(text))
        prose = markdown_reader_prose(text)
        self.assertNotIn('PER-01', prose)
        self.assertIn('Send the brief.', prose)

    def test_standards_quarters_and_versions_are_not_records(self):
        self.assertIsNone(self.finding('Q1 revenue rose. Q2 held. Hash with SHA-256 and store UTF-16 text. '
                                       'Q3 follows ISO-27001 work. Version v1.2 shipped; Q4 waits.'))

    def test_json_code_and_spreadsheet_inputs_are_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            data = self.write(folder, 'records.json', json.dumps({'note': DENSE, 'items': [{'id': 'PER-01'}]}))
            script = self.write(folder, 'tool.py', '"""' + DENSE + '"""\n')
            for path in (data, script):
                with self.subTest(path=path.name):
                    self.assertNotIn(RULE, {f.rule for f in check(authored_text(path))[0]})

    def test_html_rows_labelled_by_ids_are_flagged(self):
        rows = ''.join(f'<tr><td>R-00{n}</td><td>Risk {n}</td></tr>' for n in range(1, 7))
        page = f'<html><body><h1>Status</h1><p>Six risks are open.</p><table>{rows}</table></body></html>'
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, 'status.html', page)
            self.assertIn(RULE, {f.rule for f in check(authored_text(path))[0]})

    def test_html_source_index_tooltips_and_code_are_skipped(self):
        rows = ''.join(f'<tr><td>R-00{n}</td><td>Risk {n}</td></tr>' for n in range(1, 7))
        page = ('<html><body><h1>Status</h1><p>The <span title="DEC-02 RI-09 CAP-15">email-sender decision</span> '
                'is settled. <code>DEC-02 RI-09 CAP-15</code></p>'
                f'<table data-source-index>{rows}</table>'
                f'<h2>Sources</h2><table>{rows}</table><h2>Next</h2><p>Send the page.</p></body></html>')
        prose = html_reader_prose(page)
        self.assertNotIn('R-001', prose)
        self.assertNotIn('DEC-02', prose)
        self.assertIn('Send the page.', prose)
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(folder, 'status.html', page)
            self.assertNotIn(RULE, {f.rule for f in check(authored_text(path))[0]})

    def test_budget_grows_with_reader_words(self):
        filler = ' '.join(['The team reviewed the delivery plan with the client today.'] * 60)
        openers = ' DEC-02 settled it. RI-09 stays open. CAP-15 waits.'
        self.assertIsNotNone(self.finding(openers))
        self.assertIsNone(record_id_finding(filler + openers))
        long_dense = record_id_finding(filler + openers * 3)
        self.assertEqual(long_dense[0], 9)
        self.assertGreater(long_dense[1], 3)
        self.assertGreater(long_dense[2], 600)

    def test_configuration_cannot_relax_the_budget(self):
        with tempfile.TemporaryDirectory() as folder:
            config = self.write(folder, 'loose.json', json.dumps({'record_id_per_words': 1000}))
            with self.assertRaises(ValueError):
                strict_config(config)


if __name__ == '__main__':
    unittest.main()
