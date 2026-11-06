from pathlib import Path
import tempfile
import unittest
import json
from hashlib import sha256
from zipfile import ZipFile
from xml.sax.saxutils import escape
from check_role_resume_readiness import check

class ResumeReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.master = root / 'master.docx'
        self.master.write_bytes(b'historical master fixture')
        self.prior = root / 'prior.docx'
        self.prior.write_bytes(b'historical variant fixture')
        self.ledger = root / 'ledger.md'
        self.ledger.write_text('source ledger')
        self.resume = root / 'tailored.docx'
        self.record = root / 'Role_Work_Record.md'
        self.review = root / 'content-review.json'
        self.body = 'Career progression from architect to practice lead. Led managers and client architecture decisions. Owned commercial scope and portfolio results.'
        self.write_docx(self.body)
        brief = dict(audience='hiring', purpose='resume', readerAction='Assess leadership mandate', voice='Direct and specific', risk='consequential')
        sources = [dict(id=name, path=str(p), sha256=sha256(p.read_bytes()).hexdigest(), revision=1) for name,p in [('master',self.master),('prior',self.prior),('ledger',self.ledger)]]
        self.receipt = dict(artifact_sha256=sha256(self.resume.read_bytes()).hexdigest(), brief=brief, source_files=sources, review=dict(brief=brief, bodyHash=sha256(self.body.encode()).hexdigest(), depth='deep', reviewer='fixture reviewer', sources=[dict(id=s['id'],revision=1,hash=s['sha256']) for s in sources], coverage=[dict(dimension=d,action='covered',quote=self.body,reason='Synthetic hiring coverage review.') for d in ['career-progression','leadership-scope','client-decision','commercial-ownership','major-results']], checks={k:dict(result='pass',notes='Synthetic completed direct review.') for k in ['accuracy','representation','writing','layout']}))
        self.write_record()
    def write_docx(self, body):
        with ZipFile(self.resume,'w') as z:
            z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'+escape(body)+'</w:t></w:r></w:p></w:body></w:document>')
    def write_record(self, revise='Adapted the leadership example.'):
        self.review.write_text(json.dumps(self.receipt))
        self.record.write_text('## Resume source review\n\n'+f'- Base master: `{self.master}`\n- Prior variants reviewed: `{self.prior}`\n- Retain: Career trajectory and mandate.\n- Revise: {revise}\n- Exclude: Irrelevant internal details.\n- Claim authority checked: `{self.ledger}`\n- Tailored resume: `{self.resume}`\n- Finished copy check: Directly reviewed the full draft and rendered pages.\n- Content review: `{self.review}`\n')
    def test_valid_bound_review_passes(self):check(self.record)
    def test_original_empty_document_regression_fails(self):
        self.write_docx('')
        with self.assertRaisesRegex(ValueError,'no readable'):check(self.record)
    def test_layout_only_file_change_invalidates_review(self):
        with ZipFile(self.resume,'a') as z:z.writestr('word/styles.xml','<styles/>')
        with self.assertRaisesRegex(ValueError,'exact DOCX'):check(self.record)
    def test_source_change_invalidates_review(self):
        self.ledger.write_text('corrected authority')
        with self.assertRaisesRegex(ValueError,'source changed'):check(self.record)
    def test_missing_master_foundation_fails(self):
        self.receipt['source_files'] = self.receipt['source_files'][1:]
        self.write_record()
        with self.assertRaisesRegex(ValueError,'foundation'):check(self.record)
    def test_narrow_handout_cannot_omit_progression(self):
        self.receipt['review']['coverage'][0].update(action='omitted',quote='',reason='Short handout')
        self.write_record()
        with self.assertRaisesRegex(ValueError,'career-progression'):check(self.record)
    def test_valid_selective_tailoring_can_omit_nonessential_dimension(self):
        self.receipt['review']['coverage'][-1].update(action='omitted',quote='',reason='Role asks for technical governance; commercial results covered in supporting case study.')
        self.write_record()
        check(self.record)
    def test_deep_review_cannot_be_light(self):
        self.receipt['review']['depth']='light'
        self.write_record()
        with self.assertRaisesRegex(ValueError,'depth'):check(self.record)
    def test_empty_field_fails(self):
        self.write_record(revise='')
        with self.assertRaisesRegex(ValueError,'Revise'):check(self.record)
    def test_missing_prior_file_fails(self):
        self.prior.unlink()
        with self.assertRaisesRegex(ValueError,'prior variant'):check(self.record)
    def test_corrupt_resume_fails(self):
        self.resume.write_text('not a docx')
        with self.assertRaisesRegex(ValueError,'valid DOCX'):check(self.record)

if __name__ == '__main__':unittest.main()
