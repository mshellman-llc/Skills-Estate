"""Observable candidate diagnostics and counterexamples across real input paths."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/prose-pass/scripts'
sys.path.insert(0, str(SCRIPTS))
from prose_check import check
from writing_check import authored_text

RULE = 'C24-formulaic-the-framing'


class FramingCandidateTests(unittest.TestCase):
    def candidates(self, text):
        return [f for f in check(text)[0] if f.rule == RULE]

    def test_prose_and_email(self):
        for text in [
            'The knot is that no one owns follow-up. The route is to assign an owner. The marker is a review date.',
            'The headline is that the review is complete. The lever is your approval of v3. The window is Friday.',
            'Our note says the promise is less waiting; the engine is routing.',
        ]:
            with self.subTest(text=text):
                findings = self.candidates(text)
                self.assertEqual(len(findings), 1)
                self.assertEqual(findings[0].severity, 'WARN')
                self.assertIn('review candidates', findings[0].message)

    def test_labels_names_headings_captions_and_unknown_vocabulary(self):
        for text in [
            '# The Bet\nPilot intake routing.\n# The Call\nDiscovery notes.',
            '**The Problem**\nMissing owner.\n**The Move:** Assign an owner.',
            'THE Workspace - shared files\nTHE Project - pilot',
            'The Spark: A request arrives.\nThe Relay: A coordinator assigns it.',
            'The Surveyor\nThe Cartographer\nThe Researcher',
            'The Origami\nThe Lantern\nThe Kaleidoscope',
            '| The Bet | Pilot |\n| The Call | Discovery |',
            '[The Bet](pilot.md)\n[The Call](notes.md)',
            '# The Bet\n' + 'Ordinary supporting content.\n' * 80 + '# The Call',
        ]:
            with self.subTest(text=text[:90]):
                self.assertEqual(len(self.candidates(text)), 1)

    def test_ordinary_grammar_specific_headings_names_and_identifiers(self):
        for text in [
            'The analyst checked the figures. The editor corrected the caption.',
            'The cat is black. The dog is brown. The bird is blue.',
            'The first trial used saline. The second trial used water.',
            'The time to listen is now. The time to act is now.',
            'The Witness speaks first. The Messenger answers.',
            'The Atlantic published an article about The Hague.',
            'The cost of delayed approvals\nThe role of intake routing',
            'The Bet\nThe Bet\nThe Bet',
            'The project owner approved v3; Priya has v2. Keep DEC-014.',
            'The v2\nThe v3\nThe DEC-014',
            '| The source says | The check grades form | The backlog is noise |',
            '“The Bet. The Call. The Win.”',
        ]:
            with self.subTest(text=text):
                self.assertEqual(self.candidates(text), [])

    def test_ambiguous_titles_are_candidates_not_automatic_errors(self):
        # Identical labels can be intentional character names. Text alone cannot
        # establish authorial purpose. Preserve them and request contextual review.
        finding = self.candidates('The Witness\nThe Messenger\nThe Keeper')[0]
        self.assertEqual(finding.severity, 'WARN')
        self.assertIn('not a verdict', finding.message)
        self.assertIn('exact quotations', finding.message)

    def test_authored_quotes_and_code_wrappers_cannot_hide_a_pattern(self):
        for text in ['> The Bet\n> The Call', '```text\nThe Bet\nThe Call\n```',
                     '`The Bet`\n`The Call`', '"The Bet"\n"The Call"']:
            self.assertTrue(self.candidates(text))

    def test_structured_and_document_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixtures = {
                'labels.json': json.dumps({'cards': [{'title': 'The Bet'}, {'title': 'The Call'}]}),
                'page.html': '<nav><a>The Bet</a><a>The Call</a></nav>',
                'ui.js': 'const cards = ["The Bet", "The Call"];',
                'labels.csv': 'label\nThe Bet\nThe Call\n',
                'notes.py': 'labels = ["The Bet", "The Call"]',
            }
            for name, body in fixtures.items():
                path = root / name; path.write_text(body)
                with self.subTest(name=name):
                    self.assertTrue(self.candidates(authored_text(path)))
            for suffix, member in [('docx', 'word/document.xml'), ('pptx', 'ppt/slides/slide1.xml'),
                                   ('xlsx', 'xl/sharedStrings.xml')]:
                path = root / ('labels.' + suffix)
                with zipfile.ZipFile(path, 'w') as z:
                    z.writestr(member, '<root><t>The Bet</t><t>The Call</t></root>')
                self.assertTrue(self.candidates(authored_text(path)))

    def test_legacy_entrypoints_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'labels.md'
            path.write_text('# The Bet\n# The Call\nKeep v2, v3 and DEC-014 exactly.\n')
            original = hashlib.sha256(path.read_bytes()).hexdigest()
            for script, args in [('writing_check.py', ['--json']), ('prose_check.py', ['--json']),
                                 ('scan.py', ['--input']), ('scan.py', ['audit'])]:
                run = subprocess.run([sys.executable, str(SCRIPTS/script), *args, str(path)],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 1, run.stderr)
                self.assertIn(RULE, run.stdout)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), original)

    def test_receipt_retention_is_explicit_narrow_and_hash_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cast.md'; receipt = Path(folder) / 'receipt.json'
            path.write_text('The Witness\nThe Messenger\nThe Keeper\n')
            command = [sys.executable, str(SCRIPTS/'prose_receipt.py'), 'emit', str(path),
                       '--out', str(receipt), '--no-change-justification',
                       'The established cast names must remain unchanged.']
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)  # A generic no-change claim is insufficient.
            run = subprocess.run(command + ['--retain-framing-reason', 'These are established cast names.',
                '--retention-source', 'Synthetic performance program, supplied cast list.'],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            data = json.loads(receipt.read_text())
            from prose_receipt import validate_receipt
            self.assertEqual(validate_receipt(data), [])
            sys.path.insert(0, str(ROOT/'skills/quality-gate/scripts'))
            from quality_gate import validate
            gate_record = {
                'artifact': {'path': str(path), 'narrative_final': True, 'client_prose': True,
                             'brand_render': False, 'contract_scope': False},
                'controls_selected': ['prose-pass'],
                'checks': [{'control': 'prose-pass', 'verdict': 'pass', 'receipt': str(receipt),
                            'citation': 'Synthetic cast list and hash-bound contextual retention.'}],
                'assertions': [], 'release': {'released': True},
                'hub_update': {'status': 'not_applicable'},
            }
            self.assertTrue(validate(gate_record, base_dir=Path(folder)).released)
            changed_engine = dict(data, checker_fingerprint='old-engine')
            self.assertIn('checker-mismatch', {code for code, _ in validate_receipt(changed_engine)})
            missing_engine = dict(data); del missing_engine['checker_fingerprint']
            self.assertIn('checker-missing', {code for code, _ in validate_receipt(missing_engine)})
            data['candidate_reviews'][0]['rule'] = 'house-banned-term'
            self.assertTrue(validate_receipt(data))
            data = json.loads(receipt.read_text()); data['candidate_reviews'][0]['source_ref'] = ''
            self.assertTrue(validate_receipt(data))
            data = json.loads(receipt.read_text()); path.write_text(path.read_text() + 'Changed.\n')
            self.assertIn('hash-mismatch', {code for code, _ in validate_receipt(data)})

    def test_candidate_retention_cannot_waive_another_finding(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cast.md'; receipt = Path(folder) / 'receipt.json'
            path.write_text('The Witness\nThe Messenger\nThe Keeper\nWe leverage synergy.\n')
            run = subprocess.run([sys.executable, str(SCRIPTS/'prose_receipt.py'), 'emit', str(path),
                '--out', str(receipt), '--no-change-justification', 'Keep cast names.',
                '--retain-framing-reason', 'Established cast names.', '--retention-source', 'Synthetic cast list.'],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 1)
            self.assertIn('house-banned-term', run.stdout)


if __name__ == '__main__':
    unittest.main()
