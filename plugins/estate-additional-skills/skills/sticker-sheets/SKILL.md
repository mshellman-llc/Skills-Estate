---
name: sticker-sheets
description: Lay out supplied PNG designs as Cricut Print Then Cut sheets using the current project generator. Use for sticker sizes, exact counts, sheet rebuilding, and physical print layouts.
---


# Sticker sheets

Resolve the sheet generator from an explicit caller-supplied project or the current project configuration. Read its skill and inspect the actual generator's `--help` before using it; `make_sheets.py` is a supported adapter filename, not proof that it is installed. This entry preserves the production workflow without embedding a private generator location or brand assets. If the project is unavailable, request the specific generator or source designs needed and do not treat a local path as accessible in a cloud session.

Confirm physical paper dimensions separately from the permitted cut area. Preserve the exact requested designs, counts, sticker dimensions, and grouping. Use transparent-pixel bounds for sizing and pixel comparison for duplicate decisions; similar names do not prove duplicate images.

Read [the shared brand policy](references/estate/brand.md). Run the generator with `--no-brand` unless the user explicitly requests a maker mark and supplies or identifies its confirmed project profile. A generator's old default does not authorize adding branding. Preserve any specific instruction to keep all designs or disable duplicate removal.

Inspect the output manifest and contact sheet, check pixel dimensions and DPI against the physical format, and verify every requested design and count. Report skipped duplicates with their identity. Keep a printable paper canvas distinct from an image sized only to the cut area. Verify current Design Space limits when they affect the requested layout.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
