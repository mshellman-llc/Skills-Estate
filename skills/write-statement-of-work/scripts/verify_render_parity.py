#!/usr/bin/env python3
"""Check that the rendered PDF carries every sentence and table cell of the Word file.

The manual read of rendered pages missed three table rows (an acceptance test among
them) that a PDF render dropped while the Word file held them. This check compares
the two texts mechanically:

  1. Extract the Word text from word/document.xml, in document order. Each
     paragraph outside a table is split into sentences; each table cell is one unit.
  2. Extract the PDF text with pdftotext, rendering the Word file with LibreOffice
     first when no PDF is given.
  3. Normalise both: smart quotes and dashes, non-breaking and soft hyphens,
     ligatures, whitespace and line wraps.
  4. Look for every Word unit in the PDF text. A unit is present when its words
     appear in order within a window that tolerates a page header or footer, a
     bullet or a neighbouring column between them. Each PDF word can satisfy only
     one unit, so a row dropped from a table of identical rows is still found.
  5. Fail on any unit that is missing, and name it. A cell that is missing is
     reported with the sentences inside it that are missing.

Usage:
    verify_render_parity.py OUT.docx [--pdf RENDER.pdf | --pdf-text TEXT.txt] [--output report.json]

With neither --pdf nor --pdf-text, the script renders OUT.docx itself in a temporary
folder, with a temporary HOME for LibreOffice that it removes afterwards. A short unit
made only of words that occur elsewhere (for example "Draft") can be matched by
another copy of those words; the check is built to catch dropped rows, sentences and
cells, and it does not replace reading the rendered pages.

Exit 0 when every unit is present, 1 when any is missing, 2 when the check could not
run (no soffice or pdftotext, an unreadable file). Standard library only.
"""
import argparse
import bisect
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
SENTENCE_END=re.compile(r'(?<=[.!?])\s+(?=\S)')
DASHES=dict.fromkeys(map(ord,'‐‑‒–—―−'),'-')
QUOTES={ord('‘'):"'",ord('’'):"'",ord('‚'):"'",ord('“'):'"',ord('”'):'"',ord('„'):'"'}

class CannotRun(Exception):
    pass

def normalize(text):
    text=unicodedata.normalize('NFKC',text).translate(DASHES).translate(QUOTES)
    text=text.replace('­','').replace('​','').replace(' ',' ')
    return re.sub(r'\s+',' ',text).strip()

def tokens(text):
    return normalize(text).split(' ') if normalize(text) else []

def paragraph_text(paragraph):
    parts=[]
    def visit(node,hidden=False):
        for child in node:
            tag=child.tag
            if tag==W+'r':
                properties=child.find(W+'rPr')
                if properties is not None and properties.find(W+'vanish') is not None:continue
                visit(child,hidden)
            elif tag==W+'t':parts.append(child.text or '')
            elif tag in (W+'tab',W+'br',W+'cr'):parts.append(' ')
            elif tag==W+'noBreakHyphen':parts.append('-')
            elif tag in (W+'del',W+'pPr',W+'rPr'):continue
            else:visit(child,hidden)
    visit(paragraph)
    return normalize(''.join(parts))

def word_units(document):
    """(kind, text) in document order: 'sentence' for body paragraphs, 'cell' for table cells."""
    with zipfile.ZipFile(document) as archive:
        root=ET.fromstring(archive.read('word/document.xml'))
    units=[]
    def walk(container):
        for child in container:
            if child.tag==W+'p':
                for sentence in SENTENCE_END.split(paragraph_text(child)):
                    if re.search(r'\w',sentence):units.append(('sentence',sentence))
            elif child.tag==W+'tbl':
                for row in child.findall(W+'tr'):
                    for cell in row.findall(W+'tc'):
                        text=normalize(' '.join(paragraph_text(p) for p in cell.findall(W+'p')))
                        if re.search(r'\w',text):units.append(('cell',text))
                        walk([c for c in cell if c.tag in (W+'tbl',W+'sdt')])
            elif child.tag==W+'sdt':
                content=child.find(W+'sdtContent')
                if content is not None:walk(content)
            elif child.tag==W+'body':walk(child)
    walk(root)
    return units

class Pool:
    """PDF words, each usable once, searched as an in-order subsequence inside a window."""
    def __init__(self,text):
        self.words=tokens(text)
        self.positions={}
        for index,word in enumerate(self.words):self.positions.setdefault(word,[]).append(index)
        self.used=[False]*len(self.words)

    def _next(self,word,after,limit):
        places=self.positions.get(word)
        if not places:return None
        i=bisect.bisect_right(places,after)
        while i<len(places) and places[i]<=limit:
            if not self.used[places[i]]:return places[i]
            i+=1
        return None

    def take(self,unit):
        needed=unit.split(' ')
        window=len(needed)*2+40
        for start in self.positions.get(needed[0],[]):
            if self.used[start]:continue
            found=[start];limit=start+window
            for word in needed[1:]:
                place=self._next(word,found[-1],limit)
                if place is None:break
                found.append(place)
            else:
                for place in found:self.used[place]=True
                return True
        return False

def compare(units,pdf_text):
    pool=Pool(pdf_text)
    missing=[]
    for kind,text in units:
        if pool.take(text):continue
        item={'kind':kind,'text':text if len(text)<=300 else text[:300]+'...'}
        if kind=='cell':
            # Name the sentences inside the cell that the render lacks.
            inside=Pool(pdf_text)
            item['missing_sentences']=[s for s in SENTENCE_END.split(text) if re.search(r'\w',s) and not inside.take(s)]
        missing.append(item)
    return missing

def render_pdf_text(document,pdf=None):
    if not shutil.which('pdftotext'):raise CannotRun('pdftotext is not installed')
    work=None
    try:
        if pdf is None:
            soffice=shutil.which('soffice') or shutil.which('libreoffice')
            if not soffice:raise CannotRun('soffice is not installed; render the PDF and pass --pdf')
            work=Path(tempfile.mkdtemp(prefix='sow-parity-'))
            (work/'home').mkdir()
            environment=dict(os.environ,HOME=str(work/'home'))
            result=subprocess.run([soffice,'--headless','--convert-to','pdf','--outdir',str(work),str(document)],
                capture_output=True,text=True,env=environment,timeout=300)
            pdf=work/(Path(document).stem+'.pdf')
            if result.returncode or not pdf.exists():raise CannotRun('LibreOffice did not render the file: '+result.stderr.strip()[:300])
        result=subprocess.run(['pdftotext','-enc','UTF-8',str(pdf),'-'],capture_output=True,text=True)
        if result.returncode:raise CannotRun('pdftotext failed: '+result.stderr.strip()[:300])
        return result.stdout
    finally:
        if work:shutil.rmtree(work,ignore_errors=True)

def parity(document,pdf=None,pdf_text_file=None):
    units=word_units(document)
    if pdf_text_file:text=Path(pdf_text_file).read_text(encoding='utf-8')
    else:text=render_pdf_text(document,pdf)
    missing=compare(units,text)
    return {'document':str(document),'units':len(units),'cells':sum(1 for k,_ in units if k=='cell'),
            'missing':missing,'passed':bool(units) and not missing,
            'note':'' if units else 'The Word file has no text to compare.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('document',type=Path)
    source=parser.add_mutually_exclusive_group()
    source.add_argument('--pdf',type=Path,help='a rendered PDF of the document')
    source.add_argument('--pdf-text',type=Path,help='text already extracted from the rendered pages')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:report=parity(args.document,args.pdf,args.pdf_text)
    except CannotRun as exc:
        print('Cannot run the render parity check: '+str(exc),file=sys.stderr);return 2
    except (OSError,zipfile.BadZipFile,ET.ParseError,KeyError) as exc:
        print('Cannot read the input: '+str(exc),file=sys.stderr);return 2
    rendered=json.dumps(report,indent=2)+'\n'
    print(rendered)
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(rendered)
    return 0 if report['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
