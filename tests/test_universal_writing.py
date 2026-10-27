import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

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
        self.assertEqual(path.read_bytes(), body.encode())
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

    def test_javascript_code_is_separate_from_strings_templates_and_comments(self):
        syntax = '''const re = /["']/g;
const cell = el("div", `cell ${extra || r.style || ""}${r.basis === "hypothesis" ? " hypothesis" : ""}`, t === null ? (r.label === "Opportunities" ? "None proposed" : "Not captured") : t);
const ratio = (value - 1) / 4;'''
        self.scan('syntax.html', '<script>'+syntax+'</script>', 0)
        self.scan('string.js', 'const label = '+json.dumps(BAD)+';', 1)
        self.scan('comment.js', '// '+BAD+'\nconst row=12;', 1)
        self.scan('template.js', 'const label = `<p>'+BAD+' ${name}</p>`;', 1)
        self.scan('expression.js', 'const label = `${ok ? '+json.dumps(BAD)+' : "Ready"}`;', 1)
        self.scan('json-data.html', '<script>const MAP = '+json.dumps({'note': BAD})+';</script>', 1)
        self.scan('event.html', '<button onclick=\'alert('+json.dumps(BAD)+')\'>Open</button>', 1)
        self.scan('broken.js', 'const label = `unfinished ${name;', 2)

    def test_structured_cells_keep_boundaries_and_citations_keep_all_other_checks(self):
        self.scan('cells.json', json.dumps({'cells': ['Identify the account.', 'Obtain the ID.']}), 0)
        self.scan('fragments.json', json.dumps({'cells': ['Instant progress. Effortless success.']}), 1)
        citation = 'Patron B interview concerning reserved library books, 23 October 2026'
        data = {'emotionLabels': [{'text':'Annoyed at the counter', 'basis':'reported', 'source':citation},
                                  {'text':'Relieved at handover', 'basis':'reported', 'source':citation}]}
        self.scan('citations.json', json.dumps(data), 0)
        data['emotionLabels'][0]['source'] = BAD
        data['emotionLabels'][1]['source'] = BAD
        self.scan('bad-citation.json', json.dumps(data), 1)
        self.scan('redundancy.json', json.dumps({'cells': ['Collect the parcel; inferred from the pickup task',
                                                        'Confirm delivery; inferred from the pickup task']}), 1)

    def test_repetition_does_not_bridge_dates_or_table_columns(self):
        self.scan('questions.md', 'Ask whether the book can be collected. Check whether the book can be found.', 1)
        self.scan('ledger.md', '| L2, interview, 23 October 2026 | reported |\n| L3, walkthrough, 23 October 2026 | reported |', 0)
        self.scan('repeat.md', 'The library updates the dispatch queue overnight. The library updates the dispatch queue overnight.', 1)
        self.scan('dates.md', 'The audit is dated 2026-10-23. Scores use 1 to 5.', 0)


    def test_review_regressions_preserve_repetition_and_template_boundaries(self):
        repeated = 'Check whether it has been returned.'
        self.scan('aux-repeat.md', repeated+' '+repeated, 1)
        reason = 'Inferred from the pickup task because no patron was interviewed'
        self.scan('hypothesis.json', json.dumps({'emotionLabels': [
            {'text':'Annoyed', 'basis':'hypothesis', 'source':reason},
            {'text':'Relieved', 'basis':'hypothesis', 'source':reason}]}), 1)
        self.scan('unrelated-source.json', json.dumps({'rows': [
            {'basis':'reported', 'source':reason}, {'basis':'reported', 'source':reason}]}), 1)
        self.scan('dated-repeat.md', 'Interviewed 23 October 2026 at the counter. Interviewed 23 October 2026 at the counter.', 1)
        self.scan('pipe-repeat.json', json.dumps({'note':'The library | updates the dispatch | queue overnight. The library | updates the dispatch | queue overnight.'}), 1)
        self.scan('regex-arrow.js', "const test = s => /'/.test(s); const other = typeof /'/;", 0)
        self.scan('templates.html', '<script>const first = `<td>No log access.</td>`; const next = `<td>Priority not set.</td>`;</script>', 0)
        result = self.scan('inline-fragments.html', '<script>const first = `<p>Priority <b>not set</b>. History split across tools.</p>`;</script>', 1)
        self.assertIn('C6-fragment-stacking', [f['rule'] for f in json.loads(result.stdout)[str(self.base/'inline-fragments.html')]['findings']])
        self.scan('bare-script.html', '<script type>const row = 12;</script>', 0)
        self.scan('html-template.html', '<script type="text/template"><p>'+BAD+'</p></script>', 1)
        self.scan('crlf.js', 'const label = "Row'+'\\'+'\r\n'+'saved";', 0)


    def test_extracted_reasons_cannot_be_page_furniture(self):
        reason = 'Inferred from the pickup task because no patron was interviewed'
        rows = [{'text':name, 'basis':'hypothesis', 'source':reason} for name in ['Annoyed', 'Unsure', 'Relieved']]
        for filename,body in [('three.json', json.dumps({'emotionLabels':rows})),
                              ('three.html', '<script>const MAP = { emotionLabels: '+json.dumps(rows)+'};</script>')]:
            result = self.scan(filename, body, 1)
            self.assertIn('C12-verbatim-recycling', [f['rule'] for f in json.loads(result.stdout)[str(self.base/filename)]['findings']])
        self.scan('label-notes.json', json.dumps({'metadata':{'sourceLabels':[{'note':reason},{'note':reason}]}}), 1)
        self.scan('distinct-dates.md', 'Patron A was interviewed on 21 October 2026. Patron B was interviewed on 22 October 2026.', 0)
        self.scan('increment.js', 'n=i++/2;t='+json.dumps(BAD)+';r=a/b;', 1)
        self.scan('decrement.js', 'n=i--/2;t='+json.dumps(BAD)+';r=a/b;', 1)
        self.scan('prefix.js', 'n=++i/2;t='+json.dumps(BAD)+';r=a/b;', 1)
        result = self.scan('only-fragments.json', json.dumps({'note':'Priority not set. History split across tools.'}), 1)
        self.assertIn('C6-fragment-stacking', [f['rule'] for f in json.loads(result.stdout)[str(self.base/'only-fragments.json')]['findings']])
        self.scan('template-syntax.html', '<script type="text/template">'+('<span class="plain" data-extra="value">Ready</span>'*2)+'</script>', 0)


    def test_extracted_cells_and_comments_never_become_furniture(self):
        reason = 'Inferred from the pickup task because no patron was interviewed'
        cases = [
            ('reasons.csv', 'feeling,basis,source\n'+''.join(name+',hypothesis,'+reason+'\n' for name in ['Annoyed','Unsure','Relieved'])),
            ('reasons.tsv', 'feeling\tbasis\tsource\n'+''.join(name+'\thypothesis\t'+reason+'\n' for name in ['Annoyed','Unsure','Relieved'])),
            ('strings.py', '\n'.join('reason%d = %s' % (n,json.dumps(reason)) for n in range(3))),
            ('comments.py', ('# '+reason+'\n')*3),
            ('cells.html', '<table><tr>'+''.join('<td>'+reason+'</td>' for n in range(3))+'</tr></table>'),
            ('comments.css', ('/* '+reason+' */\n')*3)]
        for filename,body in cases:
            result = self.scan(filename,body,1)
            self.assertIn('C12-verbatim-recycling', [f['rule'] for f in json.loads(result.stdout)[str(self.base/filename)]['findings']])
        path=self.base/'cells.xlsx'
        with zipfile.ZipFile(path,'w') as archive:
            archive.writestr('xl/worksheets/sheet1.xml','<worksheet><sheetData>'+''.join('<row><c t="inlineStr"><is><t>'+reason+'</t></is></c></row>' for n in range(3))+'</sheetData></worksheet>')
        result=subprocess.run([sys.executable,str(self.checker),'--json',str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,1,result.stdout+result.stderr)
        self.assertIn('C12-verbatim-recycling',[f['rule'] for f in json.loads(result.stdout)[str(path)]['findings']])
        citation='Synthetic Patron B interview, 23 October 2026'
        self.scan('label-list.json',json.dumps({'emotionLabels':[{'text':'Annoyed','basis':'reported','source':citation},{'text':'Relieved','basis':'reported','source':citation}], 'metadata':{'sourceLabels':[citation]}}),0)
        for kind in ['text/x-template','text/x-handlebars-template','text/ng-template']:
            self.scan('other-template.html','<script type="'+kind+'">'+('<span class="plain" data-extra="value">Ready</span>'*2)+'</script>',0)
        result=self.scan('inline-cell.html','<table><tr><td>Priority <b>not set</b>. History split across tools.</td></tr></table>',1)
        self.assertIn('C6-fragment-stacking',[f['rule'] for f in json.loads(result.stdout)[str(self.base/'inline-cell.html')]['findings']])


    def test_fragment_paragraphs_survive_markup_and_python_extraction(self):
        cases=[
            ('breaks.html','<table><tr><td>Priority not set.<br>History split across tools.</td></tr></table>'),
            ('paragraphs.html','<table><tr><td><p>Priority not set.</p><p>History split across tools.</p></td></tr></table>'),
            ('comment-paragraph.py','# Priority not set.\n# History split across tools.\n'),
            ('comment-paragraph.js','// Priority not set.\n// History split across tools.\n'),
            ('fstring.py','msg = f"Priority not set. {owner} History split across tools."')]
        for filename,body in cases:
            result=self.scan(filename,body,1)
            self.assertIn('C6-fragment-stacking',[f['rule'] for f in json.loads(result.stdout)[str(self.base/filename)]['findings']])
        self.scan('docstring.py','"""Fields:\n- Patron name.\n- Pickup date.\n"""',0)
        for kind in ['text/x-handlebars','text/x-jquery-tmpl','text/x-tmpl']:
            self.scan('legacy-template.html','<script type="'+kind+'">'+('<span class="plain" data-extra="value">Ready</span>'*2)+'</script>',0)
        self.scan('optional-cell.html','<table><tr><td>Priority not set.</table><p>History split across tools.</p>',0)


    def test_comment_decoration_and_docstring_indentation_preserve_prose(self):
        comment = '/**\n * Priority not set.\n * History split across tools.\n */'
        cases = [('decorated.js',comment), ('decorated.css',comment),
                 ('wrapped.md','<!-- Priority not set. History split across tools. -->'),
                 ('wrapped.js','const note = "<!-- Priority not set. History split across tools. -->";'),
                 ('indented.py','def f():\n    """Fields:\n    - Patron name.\n    - Pickup date.\n\n    Priority not set. History split across tools.\n    """'),
                 ('block-paragraph.js','/* Priority not set. */\n/* History split across tools. */'),
                 ('nested-cell.html','<table><tr><td>Priority not set.<table><tr><td>The audit recorded 24 reservations.</td></tr></table>History split across tools.</td></tr></table>')]
        for filename,body in cases:
            result=self.scan(filename,body,1)
            self.assertIn('C6-fragment-stacking',[f['rule'] for f in json.loads(result.stdout)[str(self.base/filename)]['findings']])
        self.scan('annotations.py','TIMEOUT = 30  # Request timeout in seconds.\nRETRIES = 3  # Maximum retry count.\n',0)
        self.scan('comment-list.js','/**\n * Fields:\n * - Patron name.\n * - Pickup date.\n */',0)
        self.scan('indented-list.py','def f():\n    """Fields:\n    - Patron name.\n    - Pickup date.\n    """',0)


    def test_paragraphs_after_lists_remain_visible_in_every_extracted_context(self):
        cases=[
            ('list-comments.js','// Fields:\n// - Patron name.\n// - Pickup date.\n//\n// Priority not set. History split across tools.'),
            ('list-template.js','const help = `Fields:\n  - Patron name.\n\n  Priority not set. History split across tools.`;'),
            ('placeholder-template.js','const help = `Fields:\n  - Patron name.\n\n  ${status}${owner}. Priority not set. History split across tools.`;'),
            ('list-block.js','/* Fields:\n  - Patron name.\n\n  Priority not set. History split across tools. */'),
            ('list-comment.html','<!-- Fields:\n  - Patron name.\n\n  Priority not set. History split across tools. -->'),
            ('list-comments.css','/* Fields:\n- Patron name. */\n/* Priority not set. History split across tools. */'),
            ('placeholder.py','def f():\n    return f"""Fields:\n    - Patron name.\n\n    {status}. Priority not set. History split across tools.\n    """'),
            ('placeholders.py','def f():\n    return f"""Fields:\n    - Patron name.\n\n    {status}{owner}. Priority not set. History split across tools.\n    """')]
        for filename,body in cases:
            result=self.scan(filename,body,1)
            self.assertIn('C6-fragment-stacking',[f['rule'] for f in json.loads(result.stdout)[str(self.base/filename)]['findings']])
        self.scan('list-only.js','// Fields:\n// - Patron name.\n// - Pickup date.',0)
        self.scan('star-list.js','/*\n  Fields:\n  * Pickup date.\n  * Branch code.\n*/',0)
        self.scan('star-list.css','/*\n  Fields:\n  * Pickup date.\n  * Branch code.\n*/',0)
        self.scan('trailing.js','const T = 30; // Request timeout in seconds.\n// Maximum retry count.',0)
        self.scan('marker.md','<!-- ESTATE-WRITING:BEGIN -->\n\nPriority not set.',0)
        self.scan('marker-prose.md','<!-- ESTATE-WRITING:BEGIN -->\nPriority not set. History split across tools.',1)


    def test_mixed_comment_styles_preserve_relative_indent(self):
        bad='/*\nFields:\n- Patron name.\n*/\n// Priority not set. History split across tools.'
        cases=[('mixed.js',bad),('mixed.html','<script>'+bad+'</script>'),
               ('uneven.js','/**\n * Priority not set.\n * History split across tools.\n   See ticket 12.\n */'),
               ('uneven.css','/**\n * Priority not set.\n * History split across tools.\n   See ticket 12.\n */')]
        for filename,body in cases:
            result=self.scan(filename,body,1)
            self.assertIn('C6-fragment-stacking',[f['rule'] for f in json.loads(result.stdout)[str(self.base/filename)]['findings']])
        self.scan('first-bullet.js','/* - Patron name.\n     Optional. Not shown. */',0)
        self.scan('first-bullet.css','/* - Patron name.\n     Optional. Not shown. */',0)
        self.scan('first-template.js','const help = `- Patron name.\n     Optional. Not shown.`;',0)
        self.scan('first-python.py','help = """- Patron name.\n     Optional. Not shown."""',0)
        self.scan('python-wrap.py','# - Patron name.\n#     Optional. Not shown.',0)


    def test_list_items_cannot_hide_prose_and_hash_comments_are_checked(self):
        bad='- Pickup date.\n  - Branch code.\n\n  Priority not set. History split across tools.'
        cases=[('first-list.js','/* '+bad+' */'),
               ('first-list-template.js','const help = `'+bad+'`;'),
               ('first-list.py','help = """'+bad+'"""'),
               ('hashes.py','## Priority not set.\n## History split across tools.'),
               ('bullet-prose.md','- Priority not set. History split across tools.'),
               ('continuation.md','- Pickup date.\n  Priority not set. History split across tools.'),
               ('paragraph-after.md','- Pickup date.\n\nPriority not set. History split across tools.')]
        for filename,body in cases:
            result=self.scan(filename,body,1)
            self.assertIn('C6-fragment-stacking',[f['rule'] for f in json.loads(result.stdout)[str(self.base/filename)]['findings']])
        self.scan('nested-labels.md','- Pickup date.\n  - Branch code.\n- Counter number.',0)
        self.scan('good-continuation.md','- Pickup date.\n  The date is optional and stays hidden until the patron requests collection.',0)


    def test_list_label_and_following_paragraph_have_separate_contexts(self):
        prefix='- Patron name.\n- Pickup date.\n\n'
        self.scan('next-step.md',prefix+'Next step. The branch confirms the date by email.',0)
        self.scan('next-section.md',prefix+'## Status\nNext step. The branch confirms the date by email.',0)
        for name,body in [('bad-next.md',prefix+'Priority not set. History split across tools.'),
                          ('bad-section.md',prefix+'## Status\nPriority not set. History split across tools.'),
                          ('bad-paragraphs.md','Priority not set.\n\nHistory split across tools.'),
                          ('bad-indented.md',prefix+'  Priority not set. History split across tools.')]:
            result=self.scan(name,body,1)
            self.assertIn('C6-fragment-stacking',[f['rule'] for f in json.loads(result.stdout)[str(self.base/name)]['findings']])


if __name__ == '__main__':
    unittest.main()
