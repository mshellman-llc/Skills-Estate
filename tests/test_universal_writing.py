import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from portable import assemble, runtime_closure

BAD = 'It is worth noting that this robust ecosystem seamlessly empowers teams to leverage innovative solutions.'
GOOD = 'The import failed because row 12 has no account ID.'


class UniversalWritingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.package = self.base / 'isolated/org-preflight'
        assemble(ROOT, 'org-preflight', self.package, [])
        self.checker = self.package / '_runtime/prose-pass/scripts/writing_check.py'
        self.count = 0

    def scan(self, filename, body, expected):
        self.count += 1
        path = self.base / filename
        path.write_text(body)
        result = subprocess.run([sys.executable, str(self.checker), '--json', str(path)],
                                capture_output=True, text=True)
        (self.base / f'command-{self.count}.json').write_text(json.dumps({
            'file':filename, 'input':body, 'exit':result.returncode,
            'stdout':result.stdout, 'stderr':result.stderr}, indent=2))
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertEqual(path.read_text(), body)
        return result

    def test_all_entries_require_both_writing_runtimes_and_policy(self):
        entries = sorted((ROOT / 'skills').glob('*/SKILL.md'))
        self.assertEqual(len(entries), 78)
        for entry in entries:
            name = entry.parent.name
            deps = runtime_closure(ROOT, name)
            for required in ('writing-integrity', 'prose-pass'):
                self.assertIn(required, [name, *deps], name)
            self.assertIn('<!-- ESTATE-WRITING:BEGIN -->', entry.read_text(), name)
        self.assertTrue((self.package / 'references/estate/writing.md').is_file())
        self.assertTrue((self.package / '_runtime/writing-integrity/WORKFLOW.md').is_file())
        self.assertEqual(len(list(self.package.rglob('SKILL.md'))), 1)

    def test_internal_names_and_markdown_wrappers_cannot_hide_prose(self):
        for name, text in [('AGENTS.md', BAD), ('SKILL.md', BAD), ('internal-audit.md', BAD),
                           ('quoted.md', '> '+BAD), ('fenced.md', '```text\n'+BAD+'\n```'),
                           ('inline.md', '`'+BAD+'`')]:
            self.scan(name, text, 1)

    def test_structured_fields_and_source_comments_are_checked(self):
        self.scan('receipt.json', json.dumps({'internal': {'note': BAD}}), 1)
        self.scan('ledger.jsonl', json.dumps({'summary': BAD})+'\n', 1)
        self.scan('helper.py', '# '+BAD+'\nanswer = 42\n', 1)
        self.scan('page.html', '<input aria-label="'+BAD+'">', 1)
        self.scan('records.csv', 'note\n"'+BAD+'"\n', 1)

    def test_specific_rewrite_passes_without_rewriting_source_data(self):
        self.scan('internal-notes.md', GOOD, 0)
        self.scan('result.json', json.dumps({'note': GOOD, 'row': 12}), 0)
        self.scan('helper.py', '# '+GOOD+'\nrow = 12\n', 0)

    def test_legacy_commands_cannot_skip_quotes_or_structured_fields(self):
        path = self.base / 'internal.json'
        path.write_text(json.dumps({'note': '> '+BAD}))
        scripts = self.checker.parent
        for command in ([str(scripts/'prose_check.py'), str(path)],
                        [str(scripts/'scan.py'), 'audit', str(path)],
                        [str(scripts/'scan.py'), '--input', str(path)]):
            result = subprocess.run([sys.executable, *command], capture_output=True, text=True)
            print(result.stdout, result.stderr)
            self.assertEqual(result.returncode, 1)

    def test_configuration_cannot_relax_rules(self):
        path = self.base / 'note.md'
        path.write_text(BAD)
        for index, config in enumerate([{'banned_terms': []}, {'triad_enabled': False},
                {'flag_justification_tails': False}, {'em_dash_budget': 1000},
                {'allowed_repeated_phrases': [BAD]}]):
            cfg = self.base / ('override-%d.json' % index)
            cfg.write_text(json.dumps(config))
            result = subprocess.run([sys.executable, str(self.checker), '--config', str(cfg), str(path)],
                                    capture_output=True, text=True)
            print(result.stdout, result.stderr)
            self.assertNotEqual(result.returncode, 0)

    def test_receipt_cannot_excuse_internal_or_quoted_prose(self):
        path = self.base / 'internal.md'
        path.write_text('> '+BAD)
        result = subprocess.run([sys.executable, str(self.checker.parent/'prose_receipt.py'),
            'emit', str(path), '--out', str(self.base/'receipt.json'),
            '--no-change-justification', 'Internal AI instructions; quoted text does not need review.'],
            capture_output=True, text=True)
        print(result.stdout, result.stderr)
        self.assertEqual(result.returncode, 1)
        self.assertIn('hollow-justification', result.stdout)

    def test_css_syntax_is_separate_from_authored_css_text(self):
        syntax = '.x{border:1px solid var(--border);font-family:Arial,sans-serif;}' * 8
        self.scan('style.html', '<style>'+syntax+'</style><p>'+GOOD+'</p>', 0)
        self.scan('comment.css', '/* '+BAD+' */'+syntax, 1)
        self.scan('content.css', '.x::after{content:"'+BAD+'"}', 1)
        self.scan('comment.html', '<!-- '+BAD+' --><p>'+GOOD+'</p>', 1)
        self.scan('embedded.html', '<style>/* '+BAD+' */'+syntax+'</style>', 1)

    def test_unreadable_content_returns_error_not_clean(self):
        self.scan('bad.json', '{broken', 2)
        self.scan('binary.bin', '\x00raw', 2)


if __name__ == '__main__':
    unittest.main()
