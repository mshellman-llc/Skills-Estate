# Release gate

Run these checks on every statement of work before it leaves the building, in this order. Keep each attempt's reports, including failures.

## 1. Contract and quote check

```bash
python3 scripts/verify_contract.py OUT.docx --contract contract.json --quote quote.json \
  --variant waterfall --output verification.json
```

Add `--document-route` for a document built with the document tool, or any draft with no `OUT.docx.build.json`. Without it the verifier expects the generator's build record.

The document-route mode checks clause text, both identities, the client display name, the quote total and the scope. It skips the build record (input and artifact hashes, the reconciliation result and the variant) and the example label, because only the generator writes those. A document the generator builds from an example profile carries the label "Synthetic example for skill testing", and the default mode checks for it.

A null or absent field is unresolved. The verifier reports each unresolved token as its own finding, for example `Unresolved input: {DATE}`, and keeps running every other check, so one gap does not hide the rest. The wording around an unresolved token is still checked.

## 2. Render parity

```bash
python3 scripts/verify_render_parity.py OUT.docx --output parity.json
```

The script renders the Word file with LibreOffice, extracts the PDF text with `pdftotext`, and fails when any Word sentence or table cell is missing from the render. It normalises whitespace, line wraps, smart quotes and dashes first. A missing table row is the failure this check exists to catch: a render can drop rows that the Word file holds, and reading the pages by eye missed three of them in one run.

Pass `--pdf RENDER.pdf` to compare a PDF you already rendered, or `--pdf-text TEXT.txt` for text you already extracted. Exit code 2 means the check could not run because `soffice` or `pdftotext` is missing; report the check as pending, never as passed.

A parity pass does not show that the layout is usable. It also does not replace reading the pages.

## 3. Read and prose

Read every rendered page's extracted text, and check the contents links, tables, signatures and scoped assumptions. Take no page screenshots or images. Then run the writing check named in the skill.

Record a written disposition for each of the three checks. Creating a document does not approve, send or execute it.
