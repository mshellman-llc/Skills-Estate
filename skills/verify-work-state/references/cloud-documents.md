# Cloud documents

Identify the canonical document and account before editing. A local DOCX, PPTX,
PDF, or Markdown file is not a cloud document. Creating an upload request is not
proof that the destination stored it.

After a cloud write, read the document back through the destination service.
Verify its document ID, title, expected content, and applicable visual behavior.
Do not change sharing or permissions unless explicitly authorized. Report
permissions as unchanged unless the destination confirms a requested change.

Use `published` only when the intended cloud object exists and is readable at
its canonical location. Use `verified-live` only when the user-facing rendering
or workflow was checked there.
