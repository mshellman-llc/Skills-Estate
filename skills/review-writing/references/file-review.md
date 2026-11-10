# Review a rendered or generated file

Use this procedure when a review covers a saved file whose raw form holds more markup or data than reader text: HTML and SVG pages, pages built by scripts, workbooks, Word documents and slide decks. Review the extracted text. Raw markup, inline CSS and encoded images can make a page with a few hundred lines of text too large to read in one pass, and a partial read leaves the rest to scanner output.

A scanner checks only its own patterns. This procedure is a full reading of every reader-facing line, with a receipt that shows which lines were read and which changed.

## 1. Extract

Run from this skill's folder, or call the script by its absolute path. Use the project root so names and generator search are relative to the project.

```sh
python3 scripts/extract_review_text.py extract PAGE.html BOOK.xlsx --out REVIEW/before --root PROJECT
python3 scripts/extract_review_text.py init-log REVIEW/before
```

`REVIEW` is a working folder for this review, such as the project's `work/review-text/`. A folder argument extracts every supported file inside it. Supported files are `.html`, `.htm`, `.svg`, `.js`, `.mjs`, `.cjs`, `.xlsx`, `.docx`, `.pptx`, `.md` and `.txt`.

Each source becomes one Markdown file, or numbered parts of at most 60,000 characters and 1,500 lines. Each line reads `[ID] LOCATOR: text`:

| Locator | Where the text lives |
| --- | --- |
| `L87` | Source line 87 |
| `L83:c4521` | Line 83, column 4521, for data packed on one long line |
| `s12 Questions!B4 +3` | Shared string 12, first used in cell B4 of the Questions sheet and in three more cells |
| `Policy!A1` | An inline cell string |
| `document:p14`, `header1:p1` | Paragraph 14 of the document body, or of a header |
| `slide3:p2`, `notes3:p1` | Paragraph 2 of slide 3, or of its speaker notes |

The extraction keeps text nodes, headings (`#`), list items (`-`), table cells (`|`), SVG `<text>`, `<template>` and `<noscript>` content, CSS `content:` strings, and the `title`, `alt`, `aria-label`, `placeholder` and related attributes. It lists strings from `<script>` blocks under "Script text", including template literals, where `…` marks an interpolated value, and JSON data blocks. It skips code comments, CSS rules, SVG path data, base64 images, URLs, identifiers and class lists.

The header names the generator when one builds the file. Pass it with `--generator PAGE.html=src/build_page.py`. Without that, the header lists project scripts that name the output file; check whether one of them writes it.

## 2. Read every line

Read each part to its end and copy the read token from its last line into `review-log.json` under that part's name. Review every line against the writing rules, not only the lines a scanner flags. Read headings, labels and buttons as claims: a heading must describe its content, and a count or plural must match the page.

Record each finding in `findings`:

```json
{"file": "outputs-field-card-html.md", "id": "0042", "loc": "L87",
 "issue": "Heading promises plural folders and jobs; the page has one grading job.",
 "action": "fixed", "fix_at": "src/build_field_card.py:120"}
```

`action` is `fixed`, `kept` or `deferred`. A kept or deferred finding needs a `note` giving the reason, such as a required literal, a quoted source or a fact the author must confirm. When one fix changes several lines, such as a repeated template, give `id` as a list of every line ID it changes.

## 3. Fix at the source

Make each fix where the text originates. For a static page, edit the HTML at the locator line. For a generated page, edit the generator or the data it reads, then rebuild. For a workbook string, change the workbook or the script that writes it. An edit to the rendered output alone is overwritten by the next build. After each fix, search the rest of the piece for the same failure and repair every instance.

Preserve facts, figures, names, literals, qualifiers, scope and approval conditions while repairing the prose.

## 4. Re-extract and compare

```sh
python3 scripts/extract_review_text.py extract PAGE.html BOOK.xlsx --out REVIEW/after --root PROJECT
python3 scripts/extract_review_text.py diff REVIEW/before REVIEW/after
```

The diff compares the text, so moved line numbers do not hide or invent changes. Read every changed line in its new form. A line that changed without a finding means a fix reached more text than recorded; review that line and add its ID to a finding. Inserted lines have no earlier ID; read them in the diff.

## 5. Write the receipt

```sh
python3 scripts/extract_review_text.py receipt REVIEW/before REVIEW/after --out REVIEW/receipt.json
```

The receipt records, for each file: its hash, source lines, extracted lines, parts, parts read, lines read and lines changed, with findings by action. It lists gaps: a missing or wrong read token, a changed line with no finding, a finding marked fixed on a line that did not change, an unfixed finding with no note, and a source that changed after the final extraction. The command exits 0 and prints `COMPLETE` only when no gap remains.

Report coverage from the receipt. A read token shows the part was opened to its end; it does not prove attention to every line, factual accuracy or editorial quality. State that limit when the review is consequential. Keep the receipt and log with the project's review records, outside the reader-facing copy.
