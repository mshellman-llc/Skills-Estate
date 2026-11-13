#!/usr/bin/env python3
"""Self-test for extract_review_text.py.

Synthetic fixtures reproduce the structures that defeated whole-file review: a
base64 logo on a 31,700-character line, SVG swimlane labels, text built by
script templates, a JSON seed block and reader-facing attributes. They also
cover .xlsx, .docx and .pptx.

Real pages: set EXTRACT_REVIEW_TEXT_PAGES to a folder holding field-card.html,
review-console.html and assessment-page.html (the 2026 skills assessment suite).
Those pages hold private results, so they are read in place and never copied
into this repository. Without the variable those tests are skipped.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import tempfile
import unittest
import zipfile
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract_review_text', HERE / 'extract_review_text.py')
ert = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ert)

LOGO = 'data:image/png;base64,' + ('iVBORw0KGgoAAAANSUhEUgAA' * 1320)

PAGE = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Field Card</title>
<meta name="description" content="How the assessment runs, on one page.">
<style>.badge::after {{ content: "Draft copy"; }} .x{{color:red}}</style>
</head><body>
<nav aria-label="Pages in this suite"><a href="a.html">Assessment page</a><a href="b.html">Review console</a></nav>
<img src="{LOGO}" alt="Company logo">
<img src="{LOGO}">
<h1>The assessment on one page</h1>
<p>This card explains how the
assessment works, from the link to a result.</p>
<h2>What never to do, and why</h2>
<ul><li>Never edit questions on the page.</li><li>Never share a paper.</li></ul>
<table><tr><th>Term</th><th>Meaning</th></tr><tr><td>Anchor</td><td>A shared question.</td></tr></table>
<svg viewBox="0 0 100 100" aria-label="Swimlane diagram of the journey">
<path d="M0 0 L100 100 C 20 30 40 50 60 70 Z"/>
<text x="16" y="52">Respondent</text><text x="16" y="164">Grading job</text>
</svg>
<input type="text" placeholder="Search the terms">
<input type="submit" value="Send answers">
<button title="Back to the start">Start over</button>
<template id="row"><p>Template sentence for a row.</p></template>
<noscript>Turn on scripts to see the console.</noscript>
<!-- An HTML comment the reader never sees. -->
<script id="seed" type="application/json">{{"people":[{{"note":"Seed data sentence one."}},{{"note":"Second seed sentence."}}]}}</script>
<script>
"use strict";
// A code comment that is not reader text.
const re = /it's "quoted"/g;
const cls = "btn btn-primary";
const key = 'overallPct';
function row(p) {{
  return `<div class="card" title="Score for ${{p.name}}"><h3>Result for ${{p.name}}</h3>
  <p>${{p.done ? 'Every flagged answer is reviewed.' : "Some answers still need a reviewer."}}</p></div>`;
}}
const msg = 'The grading job runs every night.';
</script>
</body></html>
'''


def body_lines(md_path):
    return [l for l in Path(md_path).read_text(encoding='utf-8').splitlines() if re.match(r'\[\d{4}\] ', l)]


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ert.main(list(argv))
    return code, out.getvalue()


def make_zip(path, files):
    with zipfile.ZipFile(path, 'w') as z:
        for name, data in files.items():
            z.writestr(name, data)


class SyntheticHTML(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.page = self.tmp / 'site' / 'field-card.html'
        self.page.parent.mkdir()
        self.page.write_text(PAGE, encoding='utf-8')
        (self.tmp / 'build.py').write_text("open('site/field-card.html', 'w')\n", encoding='utf-8')
        self.out = self.tmp / 'text'

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def extract(self, *extra, out=None):
        return run('extract', str(self.page), '--out', str(out or self.out), '--root', str(self.tmp), *extra)

    def text(self):
        return (self.out / 'site-field-card-html.md').read_text(encoding='utf-8')

    def test_reader_text_and_attributes(self):
        code, _ = self.extract()
        self.assertEqual(code, 0)
        t = self.text()
        for want in ('[page title] Field Card', '[meta description] How the assessment runs',
                     '[aria-label] Pages in this suite', 'Assessment page', '[alt] Company logo',
                     '# The assessment on one page',
                     'This card explains how the assessment works, from the link to a result.',
                     '## What never to do, and why', '- Never edit questions on the page.',
                     '| Anchor', '[aria-label] Swimlane diagram of the journey', 'Respondent', 'Grading job',
                     '[placeholder] Search the terms', '[button] Send answers', '[title] Back to the start',
                     'Start over', 'Template sentence for a row.', 'Turn on scripts to see the console.',
                     '[css content] Draft copy'):
            self.assertIn(want, t)

    def test_skips_markup_data_and_code(self):
        self.extract()
        t = self.text()
        self.assertNotIn('iVBORw0KGgo', t)
        self.assertNotIn('M0 0 L100', t)
        self.assertNotIn('An HTML comment', t)
        self.assertNotIn('A code comment', t)
        self.assertNotIn('use strict', t)
        self.assertNotIn('btn-primary', t)
        self.assertNotIn('overallPct', t)
        self.assertNotIn('color:red', t)
        self.assertTrue(all(len(l) <= ert.MAX_LINE + 40 for l in t.splitlines()))

    def test_script_text_with_templates_json_and_regex(self):
        self.extract()
        t = self.text()
        self.assertIn('## Script text', t)
        self.assertIn('Seed data sentence one.', t)
        self.assertIn('Second seed sentence.', t)
        self.assertIn('[title] Score for …', t)
        self.assertIn('### Result for …', t)
        self.assertIn('Every flagged answer is reviewed.', t)
        self.assertIn('Some answers still need a reviewer.', t)
        self.assertIn('The grading job runs every night.', t)
        self.assertNotIn("it's", t)          # the regex literal is not text

    def test_source_line_numbers(self):
        self.extract()
        lines = PAGE.splitlines()
        for line in body_lines(self.out / 'site-field-card-html.md'):
            m = re.match(r'\[\d{4}\] L(\d+)(?::c\d+)?(?: \(cont\. \d+\))?: (?:\[[\w :-]+\] |#+ |- |\| )?(.*)', line)
            self.assertTrue(m, line)
            n, text = int(m.group(1)), m.group(2)
            first = re.split(r' … |…', text)[0].strip()[:18]
            window = '\n'.join(lines[n - 1:n + 2])
            self.assertIn(first.split(' ')[0], window, f'L{n} does not hold {text!r}')

    def test_generator_explicit_and_found(self):
        self.extract()
        self.assertIn('`build.py`', self.text())
        self.extract('--generator', f'{self.page}=src/make_card.py')
        self.assertIn('Generated by `src/make_card.py`', self.text())

    def test_parts_split_without_loss(self):
        code, _ = self.extract('--max-chars', '2600', '--max-lines', '40')
        m = json.loads((self.out / 'manifest.json').read_text())
        f = m['files'][0]
        self.assertGreater(len(f['parts']), 1)
        seen = []
        for p in f['parts']:
            path = self.out / p['file']
            self.assertLessEqual(len(path.read_text(encoding='utf-8')), 2600)
            seen += [l.split(']')[0][1:] for l in body_lines(path)]
        self.assertEqual(sorted(set(seen)), [r['id'] for r in f['records']])
        self.assertEqual(f['source_lines'], PAGE.count('\n'))

    def test_long_paragraph_wraps(self):
        self.page.write_text('<p>' + ' '.join(['word'] * 1500) + '</p>', encoding='utf-8')
        self.extract()
        lines = body_lines(self.out / 'site-field-card-html.md')
        self.assertGreater(len(lines), 1)
        self.assertIn('(cont. 2)', lines[1])
        self.assertTrue(all(len(l) <= ert.MAX_LINE + 40 for l in lines))

    def test_diff_and_receipt(self):
        before, after = self.tmp / 'before', self.tmp / 'after'
        self.extract(out=before)
        self.assertEqual(run('diff', str(before), str(before))[0], 0)
        code, _ = run('receipt', str(before), str(before))
        self.assertEqual(code, 1)                       # nothing read yet
        run('init-log', str(before))
        log_path = before / 'review-log.json'
        log = json.loads(log_path.read_text())
        part = next(iter(log['parts']))
        token = re.search(r'Read token: (\w+)', (before / part).read_text()).group(1)
        rec = next(r for r in json.loads((before / 'manifest.json').read_text())['files'][0]['records']
                   if 'What never to do' in r['text'])
        self.page.write_text(PAGE.replace('What never to do, and why', 'Rules'), encoding='utf-8')
        self.extract(out=after)
        code, out = run('diff', str(before), str(after))
        self.assertEqual(code, 1)
        self.assertIn(f"- [{rec['id']}] {rec['loc']}: ## What never to do, and why", out)
        self.assertIn('+ [', out)
        self.assertIn(': ## Rules', out)
        self.assertIn('1 lines changed', out)

        log['parts'][part] = 'wrongtoken'
        log_path.write_text(json.dumps(log))
        code, out = run('receipt', str(before), str(after))
        self.assertEqual(code, 1)
        self.assertIn('wrong token', out)

        log['parts'][part] = token
        log['findings'] = [{'file': part, 'id': rec['id'], 'loc': rec['loc'], 'issue': 'Vague heading',
                            'action': 'fixed', 'fix_at': 'site/field-card.html'}]
        log_path.write_text(json.dumps(log))
        receipt = self.tmp / 'receipt.json'
        code, out = run('receipt', str(before), str(after), '--out', str(receipt))
        self.assertEqual(code, 0, out)
        r = json.loads(receipt.read_text())
        self.assertTrue(r['complete'])
        self.assertEqual(r['totals']['lines_read'], r['totals']['extracted_lines'])
        self.assertEqual(r['totals']['lines_changed'], 1)
        self.assertEqual(r['files'][0]['changed_without_finding'], [])

        log['findings'] = []
        log_path.write_text(json.dumps(log))
        code, out = run('receipt', str(before), str(after))
        self.assertEqual(code, 1)
        self.assertIn('line changed without a finding', out)
        log['findings'] = [{'file': part, 'id': [rec['id']], 'action': 'fixed'}]
        log_path.write_text(json.dumps(log))
        self.assertEqual(run('receipt', str(before), str(after))[0], 0)

        log['findings'].append({'file': part, 'id': '0001', 'action': 'fixed'})
        log['findings'].append({'file': part, 'id': '0002', 'action': 'kept'})
        log_path.write_text(json.dumps(log))
        code, out = run('receipt', str(before), str(after))
        self.assertEqual(code, 1)
        self.assertIn('marked fixed but the line is unchanged', out)
        self.assertIn('needs a note', out)

        self.page.write_text(PAGE + '<p>Late edit.</p>', encoding='utf-8')
        log['findings'] = log['findings'][:1]
        log_path.write_text(json.dumps(log))
        code, out = run('receipt', str(before), str(after))
        self.assertEqual(code, 1)
        self.assertIn('source changed after the after-extraction', out)


W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
P = 'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
S = 'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
R = 'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'


class SyntheticOffice(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def extract(self, path):
        out = self.tmp / 'out'
        code, _ = run('extract', str(path), '--out', str(out), '--root', str(self.tmp), '--no-find-generators')
        self.assertEqual(code, 0)
        return ''.join(p.read_text() for p in sorted(out.glob('*.md')))

    def test_xlsx_shared_strings_map_to_cells(self):
        x = self.tmp / 'book.xlsx'
        make_zip(x, {
            'xl/workbook.xml': f'<workbook {S} {R}><sheets><sheet name="Questions" sheetId="1" r:id="rId1"/>'
                               f'<sheet name="Policy" sheetId="2" r:id="rId2"/></sheets></workbook>',
            'xl/_rels/workbook.xml.rels': '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                                          '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/>'
                                          '<Relationship Id="rId2" Target="/xl/worksheets/sheet2.xml"/></Relationships>',
            'xl/sharedStrings.xml': f'<sst {S}><si><t>Which object stores the answer?</t></si>'
                                    f'<si><r><t>Rich </t></r><r><t>text run.</t></r></si><si><t>Unused string here</t></si></sst>',
            'xl/worksheets/sheet1.xml': f'<worksheet {S}><sheetData><row r="2"><c r="B2" t="s"><v>0</v></c>'
                                        f'<c r="C2" t="s"><v>1</v></c><c r="D2"><v>4</v></c></row>'
                                        f'<row r="3"><c r="B3" t="s"><v>0</v></c></row></sheetData></worksheet>',
            'xl/worksheets/sheet2.xml': f'<worksheet {S}><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>An inline rule.</t></is></c>'
                                        f'</row></sheetData></worksheet>',
            'xl/comments1.xml': f'<comments {S}><commentList><comment ref="B2"><text><t>Check this key.</t></text></comment>'
                                f'</commentList></comments>',
        })
        t = self.extract(x)
        self.assertIn('[sheet] Questions', t)
        self.assertIn('s0 Questions!B2 +1: Which object stores the answer?', t)
        self.assertIn('s1 Questions!C2: Rich text run.', t)
        self.assertIn('s2 unused: Unused string here', t)
        self.assertIn('Policy!A1: An inline rule.', t)
        self.assertIn('comment B2: Check this key.', t)

    def test_docx_paragraphs_headings_and_header(self):
        d = self.tmp / 'memo.docx'
        make_zip(d, {
            'word/document.xml': f'<w:document {W}><w:body>'
                                 '<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>The folder and the job</w:t></w:r></w:p>'
                                 '<w:p><w:r><w:t xml:space="preserve">One grading </w:t></w:r><w:r><w:t>job runs.</w:t></w:r></w:p>'
                                 '<w:p><w:pPr><w:numPr/></w:pPr><w:r><w:t>A list item.</w:t></w:r></w:p>'
                                 '</w:body></w:document>',
            'word/header1.xml': f'<w:hdr {W}><w:p><w:r><w:t>Internal draft</w:t></w:r></w:p></w:hdr>',
        })
        t = self.extract(d)
        self.assertIn('document:p1: # The folder and the job', t)
        self.assertIn('document:p2: One grading job runs.', t)
        self.assertIn('document:p3: - A list item.', t)
        self.assertIn('header1:p1: Internal draft', t)

    def test_pptx_slides_notes_and_alt(self):
        p = self.tmp / 'deck.pptx'
        make_zip(p, {
            'ppt/slides/slide1.xml': f'<p:sld {P} {A}><p:cSld><p:spTree><p:pic><p:nvPicPr><p:cNvPr id="2" name="x" descr="Chart of results"/></p:nvPicPr></p:pic>'
                                     '<a:p><a:r><a:t>Results at a glance</a:t></a:r></a:p></p:spTree></p:cSld></p:sld>',
            'ppt/slides/slide2.xml': f'<p:sld {P} {A}><a:p><a:r><a:t>Next steps</a:t></a:r></a:p></p:sld>',
            'ppt/notesSlides/notesSlide1.xml': f'<p:notes {P} {A}><a:p><a:r><a:t>Say the date first.</a:t></a:r></a:p>'
                                               '<a:p><a:r><a:t>1</a:t></a:r></a:p></p:notes>',
        })
        t = self.extract(p)
        self.assertIn('slide1:p1: Results at a glance', t)
        self.assertIn('slide1: [alt] Chart of results', t)
        self.assertIn('slide2:p1: Next steps', t)
        self.assertIn('notes1:p1: Say the date first.', t)
        self.assertNotIn('notes1:p2', t)


class _Visible(HTMLParser):
    """An independent reading of visible text nodes, for a no-loss check."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.svg, self.svgtext, self.texts = 0, 0, 0, []

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'svg':
            self.svg += 1
        if tag in ('text', 'tspan'):
            self.svgtext += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
        if tag == 'svg':
            self.svg -= 1
        if tag in ('text', 'tspan'):
            self.svgtext -= 1

    def handle_data(self, data):
        t = re.sub(r'\s+', ' ', data).strip()
        if t and not self.skip and (not self.svg or self.svgtext):
            self.texts.append(t)


PAGES = os.environ.get('EXTRACT_REVIEW_TEXT_PAGES')


@unittest.skipUnless(PAGES and Path(PAGES).is_dir(), 'set EXTRACT_REVIEW_TEXT_PAGES to the assessment suite folder')
class RealPages(unittest.TestCase):
    """The pages whose review failed on 9 and 10 November 2026."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.root = Path(PAGES)
        cls.names = ['field-card.html', 'review-console.html', 'assessment-page.html']
        code, cls.log = run('extract', *[str(cls.root / n) for n in cls.names], '--out', str(cls.tmp),
                            '--root', str(cls.root), '--no-find-generators')
        assert code == 0, cls.log
        cls.manifest = json.loads((cls.tmp / 'manifest.json').read_text())
        cls.by = {f['source']: f for f in cls.manifest['files']}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def all_text(self, name):
        return '\n'.join(r['text'] for r in self.by[name]['records'])

    def test_every_part_fits_one_read(self):
        for f in self.manifest['files']:
            for p in f['parts']:
                text = (self.tmp / p['file']).read_text(encoding='utf-8')
                self.assertLess(len(text), ert.MAX_CHARS, p['file'])
                self.assertLess(text.count('\n'), 2000, p['file'])
                self.assertTrue(all(len(l) < 2000 for l in text.splitlines()), p['file'])
                self.assertNotRegex(text, r'[A-Za-z0-9+/]{200,}', p['file'])

    def test_source_line_counts(self):
        for n in self.names:
            raw = (self.root / n).read_text(encoding='utf-8')
            self.assertEqual(self.by[n]['source_lines'], raw.count('\n') + (0 if raw.endswith('\n') else 1))
            self.assertEqual(self.by[n]['sha256'], hashlib.sha256((self.root / n).read_bytes()).hexdigest())

    def test_no_visible_text_lost(self):
        for n in self.names:
            v = _Visible()
            v.feed((self.root / n).read_text(encoding='utf-8'))
            blob = re.sub(r'\s+', ' ', self.all_text(n))
            lost = [t for t in v.texts if len(t) > 2 and t not in blob]
            self.assertEqual(lost, [], n)

    def test_every_heading_present(self):
        for n in self.names:
            raw = (self.root / n).read_text(encoding='utf-8')
            heads = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', h)).strip()
                     for h in re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', raw, re.S)]
            blob = self.all_text(n)
            for h in heads:
                plain = re.sub(r'\$\{[^}]*\}', '…', __import__('html').unescape(h)).split('…')[0].strip()
                if plain and not plain.startswith('${') and not re.search(r"['\"]\s*\+", h):
                    self.assertIn(plain, blob, f'{n}: heading {h!r}')

    def test_field_card(self):
        t = self.all_text('field-card.html')
        for svg_label in ('Respondent', 'Grading job', 'Reviewers'):
            self.assertIn(svg_label, t)
        self.assertRegex(t, r'\[alt\] \S', 'the logo lost its alt text')
        self.assertNotIn('base64', t)
        self.assertEqual(len(self.by['field-card.html']['parts']), 1)

    def test_review_console_script_text(self):
        recs = self.by['review-console.html']['records']
        sections = {r['section'] for r in recs}
        self.assertIn('Script text', sections)
        self.assertIn('Script text (JSON data)', sections)
        t = self.all_text('review-console.html')
        self.assertIn('[placeholder] Your reason for this score', t)
        self.assertIn('Reviewer note: why this score', t)

    def test_assessment_page_script_text(self):
        t = self.all_text('assessment-page.html')
        for want in ('[placeholder] Answer the follow-up above.', '[aria-label] Go to item', 'Answer options',
                     'Submit take-home', 'This item has … parts.'):
            self.assertIn(want, t)
        self.assertGreater(len(self.by['assessment-page.html']['parts']), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
