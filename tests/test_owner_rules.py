"""Owner rules win over template formatting: the checks and skills a proof run tripped on.

Each test reproduces a fictional case from issues 129, 131, 132, 133, 135 and 136.
"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/writing-diagnostics/scripts'
BRAND_CHECK = ROOT / 'skills/brand-renderer/scripts/brand_check.py'
sys.path.insert(0, str(SCRIPTS))
from prose_check import check  # noqa: E402
from prose_receipt import validate_receipt  # noqa: E402
from record_ids import RULE as RECORD_ID_RULE  # noqa: E402
from writing_check import authored_text  # noqa: E402

CAPS = 'all-caps-block'
REPEAT = 'C12-verbatim-recycling'


def rules_of(path):
    return {finding.rule for finding in check(authored_text(path))[0]}


class WritingCheckerOwnerRules(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owner-rules-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def write(self, name, text):
        path = self.base / name
        path.write_text(text, encoding='utf-8')
        return path

    def test_identifier_only_html_cell_is_not_all_caps_prose(self):
        # Issue 129: a bakery pickup plan's Source cell lists only IDs.
        html = self.write('plan.html', '<h1>Pickup measures</h1><table><tr><th>Decision</th><th>Source</th></tr>'
                          '<tr><td>Track pickup wait time</td><td>KPI-01; RQ-02, ACC-03</td></tr></table>')
        markdown = self.write('plan.md', '# Pickup measures\n\n| Decision | Source |\n| --- | --- |\n'
                              '| Track pickup wait time | KPI-01; RQ-02, ACC-03 |\n')
        self.assertNotIn(CAPS, rules_of(html))
        self.assertNotIn(CAPS, rules_of(markdown))

    def test_id_shaped_tokens_are_not_all_caps_but_shouting_still_is(self):
        # Issue 133: a field guide's cells list requirement IDs.
        html = self.write('guide.html', '<table><tr><td>Stock list</td><td>SKU-01, SKU-02, SKU-03</td></tr></table>')
        markdown = self.write('guide.md', 'Stock list requirements:\n\n- SKU-01, SKU-02, SKU-03\n')
        self.assertNotIn(CAPS, rules_of(html))
        self.assertNotIn(CAPS, rules_of(markdown))
        self.assertIn(CAPS, {f.rule for f in check('READ THIS NOTICE BEFORE YOU ORDER')[0]})
        # C28 still sees the cluster of IDs a reader has to decode.
        self.assertIn(RECORD_ID_RULE, rules_of(html))

    def test_second_person_fact_is_not_deference(self):
        self.assertNotIn('C10-deference', {f.rule for f in check(
            'The guide summarises your two interviews with the shop staff.')[0]})
        self.assertIn('C10-deference', {f.rule for f in check(
            'Here are answers to your three questions about pickup.')[0]})

    def test_quoted_question_is_not_an_authored_quantifier(self):
        quoted = 'The interviewer asked "How many visits do most customers make each week?" and recorded the answer.'
        self.assertNotIn('C15-unsourced-quantifier', {f.rule for f in check(quoted)[0]})
        self.assertIn('C15-unsourced-quantifier', {f.rule for f in check(
            'Most customers make two visits each week.')[0]})
        # Quoting new wording does not hide it from the vocabulary rules.
        self.assertIn('house-banned-term', {f.rule for f in check(
            'The team said "we leverage the pickup data" in the review.',
            {**__import__('prose_check').DEFAULT_CONFIG, 'banned_terms': ['leverage']})[0]})

    def emit(self, path, *extra):
        receipt = self.base / (path.stem + '-receipt.json')
        command = [sys.executable, str(SCRIPTS / 'prose_receipt.py'), 'emit', str(path), '--out', str(receipt),
                   '--no-change-justification', 'The repeated wording names one thing with one term.', *extra]
        return subprocess.run(command, capture_output=True, text=True), receipt

    def test_repeated_phrase_and_all_caps_accept_a_recorded_reason(self):
        # Issue 129: a heading restated once in a sentence keeps one term for one thing.
        page = self.write('decisions.md', '# Decisions and the measure for each\n\n'
                          'This page lists the decisions and the measure for each one we agreed.\n')
        self.assertIn(REPEAT, rules_of(page))
        refused, _ = self.emit(page)
        self.assertEqual(refused.returncode, 1, refused.stdout)
        accepted, receipt = self.emit(page, '--retain-candidate', REPEAT + '=The heading names the table it introduces.',
                                      '--retention-source', 'Synthetic bakery plan, decisions section.')
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        data = json.loads(receipt.read_text())
        self.assertEqual(validate_receipt(data), [])
        data['candidate_reviews'][0]['rule'] = 'C2-antithesis'
        self.assertTrue(validate_receipt(data))

        sign = self.write('sign.md', 'The shop door shows the sign:\n\nOPEN DAILY FROM NINE\n')
        self.assertIn(CAPS, rules_of(sign))
        accepted, _ = self.emit(sign, '--retain-candidate', CAPS + '=The sign text is the shop\'s required wording.',
                                '--retention-source', 'Synthetic shop signage brief.')
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)


def brand_check(path):
    # Run outside the checkout so the packaged neutral profile applies.
    return subprocess.run([sys.executable, str(BRAND_CHECK), str(path)], capture_output=True, text=True,
                          cwd=path.parent, timeout=60)


def workbook(path, fill, font='Arial'):
    """A minimal two-cell workbook whose header cell uses one fill and font."""
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    styles = (f'<styleSheet xmlns="{ns}"><fonts count="2"><font><name val="Arial"/></font>'
              f'<font><b val="1"/><color rgb="FF111111"/><name val="{font}"/></font></fonts>'
              f'<fills count="3"><fill><patternFill/></fill><fill><patternFill patternType="gray125"/></fill>'
              f'<fill><patternFill patternType="solid"><fgColor rgb="FF{fill}"/></patternFill></fill></fills>'
              f'<borders count="1"><border/></borders><cellXfs count="2"><xf fontId="0" fillId="0" borderId="0"/>'
              f'<xf fontId="1" fillId="2" borderId="0"/></cellXfs>'
              f'<colors><indexedColors><rgbColor rgb="00FF0000"/></indexedColors></colors></styleSheet>')
    sheet = (f'<worksheet xmlns="{ns}"><sheetData><row r="1"><c r="A1" s="1" t="inlineStr"><is><t>Requirement</t></is></c>'
             f'</row><row r="2"><c r="A2" t="inlineStr"><is><t>Show pickup time</t></is></c></row></sheetData></worksheet>')
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('xl/styles.xml', styles)
        archive.writestr('xl/worksheets/sheet1.xml', sheet)
    return path


class BrandCheckOwnerRules(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owner-brand-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)

    def test_palette_shown_as_page_text_is_content(self):
        # Issue 132: a Northwind Tools explorer documents its draft palette in a table.
        page = self.base / 'palette.html'
        page.write_text('<!doctype html><html><head><style>body{color:#111111;background:#FFFFFF}</style></head>'
                        '<body><h1>Draft palette</h1><table><tr><th>Role</th><th>Value</th></tr>'
                        '<tr><td>Primary</td><td>#2A4B7C</td></tr></table><pre>--primary: #2A4B7C;</pre>'
                        '</body></html>')
        result = brand_check(page)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_styles_and_svg_paint_still_fail_off_palette(self):
        for body in ('<p style="color:#2A4B7C">Pickup</p>', '<svg><rect fill="#2A4B7C" width="4" height="4"/></svg>',
                     '<style>.x{color:#2A4B7C}</style><p>Pickup</p>'):
            with self.subTest(body=body):
                page = self.base / 'styled.html'
                page.write_text('<!doctype html><html><body>' + body + '</body></html>')
                result = brand_check(page)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('OFF_PALETTE', result.stdout)

    def test_workbook_fills_and_fonts_are_checked(self):
        # Issue 135: a Crumb and Co requirements workbook with no confirmed brand.
        neutral = brand_check(workbook(self.base / 'requirements.xlsx', 'F5F5F5'))
        self.assertEqual(neutral.returncode, 0, neutral.stdout)
        self.assertNotIn('UNSUPPORTED', neutral.stdout)
        navy = brand_check(workbook(self.base / 'navy.xlsx', '1F4E79'))
        self.assertEqual(navy.returncode, 1, navy.stdout)
        self.assertIn('#1f4e79', navy.stdout)
        font = brand_check(workbook(self.base / 'font.xlsx', 'F5F5F5', font='Comic Sans MS'))
        self.assertEqual(font.returncode, 0, font.stdout)
        self.assertIn('OFFICE_FONT', font.stdout)


class SkillTextOwnerRules(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding='utf-8')

    def test_shared_workflow_lets_owner_rules_win(self):
        text = self.read('policies/workflow.md')
        self.assertIn("the owner's rules win", text)
        for form in ('a table for a monospace block', 'a separate record of sources',
                     'plain indentation for bold labels', 'quality record'):
            self.assertIn(form, text)

    def test_capture_requirements_follows_host_and_neutral_profile(self):
        # Issue 135: Claude Code has neither the question tool nor the Artifacts panel.
        skill = self.read('skills/capture-requirements/SKILL.md')
        self.assertNotIn('\U0001F4CE', skill)
        self.assertNotIn('**Business Need:**', skill)
        self.assertNotIn('Use `ask_user_input_v0`', skill)
        self.assertIn('plain text with numbered options', skill)
        self.assertIn('Claude Code', skill)
        self.assertNotIn('blue/white', skill)
        workbook_format = self.read('skills/capture-requirements/references/excel-workbook-format.md')
        self.assertNotIn('1F4E79', workbook_format)
        self.assertIn('neutral profile', workbook_format)

    def test_architecture_reference_accepts_table_schema_and_source_record(self):
        # Issue 136: Harbor Tide's owner bans monospace and keeps sources out of finished copy.
        templates = self.read('skills/write-architecture-reference/references/architecture-templates.md')
        checklist = templates.split('## Pre-ship checklist', 1)[1]
        self.assertIn('separate record of sources', checklist)
        self.assertIn('schema block or as a table', checklist)
        self.assertIn('| Table | Keys | Isolation key | Invariant |', templates)

    def test_explorer_review_has_a_single_agent_fallback(self):
        # Issue 131: an agent with no subagent tool builds a co-op onboarding explorer.
        review = self.read('skills/build-interactive-explorer/references/deliverable-review.md')
        section = review.split('## When the host cannot start a separate reviewer', 1)[1].split('\n## ', 1)[0]
        for phrase in ('single-agent review', 'pending', 'Queue the independent review',
                       'compare its text with the controlling sources'):
            self.assertIn(phrase, section)


if __name__ == '__main__':
    unittest.main()
