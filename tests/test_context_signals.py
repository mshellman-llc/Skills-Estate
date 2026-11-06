"""Contextual scanner signals: observable evidence, legitimate cases and safe retention."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/writing-diagnostics/scripts'
sys.path.insert(0, str(SCRIPTS))
from context_signals import ACTION, REAFFIRM, TABLE, RULES, context_candidates, html_blocks
from prose_check import check
from writing_check import authored_text

TABLE_TEXT = '| Check | Result |\n| --- | --- |\n| Import | Passed |\n| Export | Failed |\n\nThe import passed. The export failed.'
REAFFIRM_TEXT = 'The scope excludes data migration. That exclusion still holds. The original boundary remains intact.'


class ContextSignalTests(unittest.TestCase):
    def rules(self, text):
        return {finding.rule for finding in check(text)[0] if finding.rule in RULES}

    def test_short_table_readout_with_and_without_divider(self):
        for text in [TABLE_TEXT, TABLE_TEXT.replace('| --- | --- |\n', ''),
                     '| Area | Jobs |\n| North | 18 |\n| South | 5 |\n\nNorth has eighteen jobs. South has five jobs.']:
            with self.subTest(text=text): self.assertIn(TABLE, self.rules(text))

    def test_useful_table_prose_and_long_display_summaries_are_not_readouts(self):
        table = TABLE_TEXT.split('\n\n')[0]
        for prose in ['Only the export failed.', 'The failed export blocks release under the signed policy.',
                      'The import passed, but export failed because its input was missing.',
                      'Run 4 measured a different outcome.', 'The results exclude the overnight batch.']:
            with self.subTest(prose=prose): self.assertNotIn(TABLE, self.rules(table + '\n\n' + prose))
        long_table = '| Item | State |\n| --- | --- |\n' + '\n'.join('| Item' + str(i) + ' | Passed |' for i in range(30))
        self.assertNotIn(TABLE, self.rules(long_table + '\n\nAll thirty checks passed.'))

    def test_accessible_and_standalone_summaries_without_adjacent_display(self):
        for text in ['Requests: April 12; May 14.', 'Backup passed; restore failed.',
                     'Completions rose 50% from Q1 to Q2.', 'Prices exclude tax.']:
            self.assertFalse(self.rules(text))

    def test_actual_user_heading_is_a_candidate_not_a_verdict(self):
        findings = [f for f in check('# What has to close to approve')[0] if f.rule == ACTION]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, 'WARN')
        self.assertIn('do not prove', findings[0].message)
        self.assertIn('supplied requirements', findings[0].message)

    def test_action_pressure_paraphrases_need_more_than_one_word(self):
        for text in ['Resolve these before sign-off.',
                     'We must act now to keep the decision window open.',
                     'Time is running out to stay informed. Turn on weekly digests today.',
                     '# Choose a route before the window closes']:
            with self.subTest(text=text): self.assertIn(ACTION, self.rules(text))
        for text in ['Choose a recovery method.', 'Approve now.', 'Complete the export today.',
                     'The open window admits fresh air.', 'Urgency was discussed at the meeting.']:
            with self.subTest(text=text): self.assertNotIn(ACTION, self.rules(text))

    def test_real_deadlines_conditions_and_explicit_basis_survive(self):
        for text in ['Obtain written owner approval before submission. Submit to the registrar by 17:00 UTC on 18 June 2027.',
                     'Upload by 21:30 UTC on 12 November for the 22:00 UTC batch. Later uploads run in the next batch.',
                     '# What has to close to approve\n\nThe signed release policy requires a passing export check and written owner approval.',
                     'Disconnect power before opening the enclosure.',
                     'Choose a recovery method. Use a backup code or request a recovery email.']:
            with self.subTest(text=text): self.assertFalse(self.rules(text))

    def test_reaffirmation_clusters_need_linked_claims_and_distinct_reassurances(self):
        self.assertIn(REAFFIRM, self.rules(REAFFIRM_TEXT))
        self.assertIn(REAFFIRM, self.rules('Offline synchronization is excluded.\n\nThat boundary remains in force.\n\nTo be clear, the exclusion continues to hold.'))
        self.assertNotIn(REAFFIRM, self.rules('The scope excludes data migration. That exclusion still holds.'))
        self.assertNotIn(REAFFIRM, self.rules('The scope excludes data migration. The latency limit remains unchanged. The budget remains intact.'))
        self.assertNotIn(REAFFIRM, self.rules('The scope excludes data migration. That exclusion still holds. That exclusion still holds.'))

    def test_new_verification_and_bounded_technical_claims_are_preserved(self):
        for text in ['The invariant holds for all 100 tested inputs. Untested inputs are not covered by this result.',
                     'The approved plan excludes partner accounts. The signed amendment also excludes them.',
                     'The scope excludes data migration. Revision 3 confirms that the exclusion still holds. The signed amendment keeps the scope unchanged.',
                     'Card A: Disconnect power before opening the enclosure.\n\nCard B: Disconnect power before opening the enclosure.']:
            self.assertNotIn(REAFFIRM, self.rules(text))

    def test_adjacent_html_and_office_tables_keep_order_and_locations(self):
        html = '<table><tr><th>Check</th><th>Result</th></tr><tr><td>Import</td><td>Passed</td></tr><tr><td>Export</td><td>Failed</td></tr></table><p>The import <em>passed</em>. The export failed.</p>'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); p = root/'report.html'; p.write_text(html)
            self.assertIn(TABLE, self.rules(authored_text(p)))
            self.assertNotIn(TABLE, self.rules(authored_text(self.write(root/'safe.html', html.replace('The import <em>passed</em>. The export failed.', 'Only the export failed.')))))
            for suffix, member in [('docx', 'word/document.xml'), ('pptx', 'ppt/slides/slide1.xml')]:
                p = root/('report.' + suffix)
                table = '<tbl>' + ''.join('<tr>' + ''.join('<tc><p><r><t>' + cell + '</t></r></p></tc>' for cell in row) + '</tr>' for row in [('Check','Result'),('Import','Passed'),('Export','Failed')]) + '</tbl>'
                with zipfile.ZipFile(p, 'w') as z: z.writestr(member, '<root>' + table + '<p><r><t>The import passed. The export failed.</t></r></p></root>')
                found = [f for f in check(authored_text(p))[0] if f.rule == TABLE]
                self.assertEqual(len(found), 1)
                self.assertTrue(any(member in sample for sample in found[0].samples))

    @staticmethod
    def write(path, text):
        path.write_text(text); return path

    def test_declared_html_accessible_description_is_not_redundant_narration(self):
        html = '<table aria-describedby="detail"><tr><th>Check</th><th>Result</th></tr><tr><td>Import</td><td>Passed</td></tr><tr><td>Export</td><td>Failed</td></tr></table><p id="detail">The import passed. The export failed.</p>'
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(Path(folder)/'accessible.html', html)
            self.assertNotIn(TABLE, self.rules(authored_text(path)))
            path.write_text(html.replace('<p id="detail">', '<div id="detail"><p>').replace('</p>', '</p></div>'))
            self.assertNotIn(TABLE, self.rules(authored_text(path)))
            # No broad suppression: the same words in an ordinary adjacent paragraph remain candidates.
            path.write_text(html.replace(' aria-describedby="detail"', ''))
            self.assertIn(TABLE, self.rules(authored_text(path)))

    def test_nested_html_tables_are_not_guessed(self):
        blocks = html_blocks('<table><tr><td>Outer<table><tr><td>Inner</td></tr></table></td></tr></table><p>Outer inner.</p>')
        self.assertTrue(any(b.kind == 'unstructured-table' for b in blocks))
        self.assertFalse(any(b.kind == 'table' for b in blocks))

    def test_cli_is_read_only_and_reports_candidate_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            p = self.write(Path(folder)/'test.md', TABLE_TEXT + '\n\n' + REAFFIRM_TEXT + '\n\nWhat has to close to approve?\nKeep v2, v3 and DEC-014.')
            before = p.read_bytes()
            result = subprocess.run([sys.executable,str(SCRIPTS/'writing_check.py'),'--json',str(p)],capture_output=True,text=True)
            self.assertEqual(result.returncode,1,result.stderr)
            value = json.loads(result.stdout)[str(p)]
            self.assertTrue(RULES <= {f['rule'] for f in value['findings']})
            self.assertIn('not semantic verdicts',value['context_signals']['mode'])
            self.assertEqual(p.read_bytes(),before)

    def test_candidate_retention_is_hash_bound_and_rule_specific(self):
        with tempfile.TemporaryDirectory() as folder:
            p = self.write(Path(folder)/'gate.md', 'What has to close to approve?')
            receipt = Path(folder)/'receipt.json'
            command=[sys.executable,str(SCRIPTS/'prose_receipt.py'),'emit',str(p),'--out',str(receipt),'--no-change-justification','The heading introduces externally supplied approval requirements.']
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,1)
            accepted=subprocess.run(command+['--retain-candidate',ACTION+'=This heading labels the supplied approval conditions.','--retention-source','Synthetic policy REV-2, requirements section.'],capture_output=True,text=True)
            self.assertEqual(accepted.returncode,0,accepted.stdout+accepted.stderr)
            from prose_receipt import validate_receipt
            data=json.loads(receipt.read_text());self.assertEqual(validate_receipt(data),[])
            data['candidate_reviews'][0]['rule']='C2-antithesis'
            self.assertTrue(validate_receipt(data))
            p.write_text('What has to close to approve? Different text.')
            self.assertTrue(validate_receipt(json.loads(receipt.read_text())))

    def test_large_inputs_fail_explicitly_instead_of_claiming_no_findings(self):
        with self.assertRaises(ValueError): context_candidates('x' * 4_000_001)

    def test_excess_candidates_fail_instead_of_omitting_later_rules(self):
        text = ('\n\n' + TABLE_TEXT + '\n\n') * 101 + '\n\nWhat has to close to approve?'
        with self.assertRaisesRegex(ValueError, '100 candidates'):
            context_candidates(text)
        with tempfile.TemporaryDirectory() as folder:
            path = self.write(Path(folder)/'large.md', text)
            run = subprocess.run([sys.executable, str(SCRIPTS/'writing_check.py'), '--json', str(path)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertIn('100 candidates', run.stdout + run.stderr)

    def test_separate_office_slides_do_not_invent_adjacency_or_reassurance(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'separate.pptx'
            table = '<tbl>' + ''.join('<tr>' + ''.join('<tc><p><t>' + cell + '</t></p></tc>' for cell in row) + '</tr>' for row in [('Check','Result'),('Import','Passed'),('Export','Failed')]) + '</tbl>'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('ppt/slides/slide1.xml', '<root>'+table+'<p><t>The scope excludes data migration.</t></p></root>')
                z.writestr('ppt/slides/slide2.xml', '<root><p><t>That exclusion still holds.</t></p></root>')
                z.writestr('ppt/slides/slide10.xml', '<root><p><t>The import passed. The export failed.</t></p><p><t>The original boundary remains intact.</t></p></root>')
            text = authored_text(path)
            self.assertNotIn(TABLE, self.rules(text))
            self.assertNotIn(REAFFIRM, self.rules(text))
            parts = [b.location for b in text.review_blocks if b.kind == 'boundary']
            self.assertEqual(parts, ['ppt/slides/slide1.xml', 'ppt/slides/slide2.xml', 'ppt/slides/slide10.xml'])

    def test_swapped_table_values_are_not_labeled_a_matching_readout(self):
        table = '| Area | Open |\n| --- | --- |\n| East | 16 |\n| West | 24 |'
        self.assertIn(TABLE, self.rules(table + '\n\nEast has 16 open and West has 24 open.'))
        self.assertNotIn(TABLE, self.rules(table + '\n\nEast has 24 open and West has 16 open.'))
        self.assertNotIn(TABLE, self.rules(table + '\n\nEast has 24 open with West at 16 open.'))

    def test_explicit_absence_of_a_requirement_does_not_suppress_gate_review(self):
        for basis in ['No policy, contract or requirement establishes this gate. These are optional ideas.',
                      "The policy doesn't require approval for these optional changes."]:
            self.assertIn(ACTION, self.rules('# What has to close to approve\n\n' + basis))


if __name__ == '__main__':
    unittest.main()
