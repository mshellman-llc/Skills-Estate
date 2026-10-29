---
name: sticker-sheets
description: Lay out Megan's PNG designs as Cricut Print Then Cut sheets using the current project generator. Use for sticker sizes, exact counts, sheet rebuilding, and physical print layouts.
---


# Sticker sheets

The current generator is maintained in `/Volumes/Stickers/0 Sticker Sheet Maker/sticker-sheets/skills/sticker-sheets/`. Read that project's skill and inspect `make_sheets.py --help` before using it. This estate entry is the shared adapter; it does not duplicate the project generator or brand assets. If the drive is unavailable, request the specific generator or source designs needed and do not pretend a local path is accessible in a cloud session.

Confirm physical paper dimensions separately from the permitted cut area. Preserve the exact requested designs, counts, sticker dimensions, and grouping. Use transparent-pixel bounds for sizing and pixel comparison for duplicate decisions; similar names do not prove duplicate images.

Read [the shared brand policy](references/estate/brand.md). Run the generator with `--no-brand` unless the user explicitly requests a maker mark and supplies or identifies its confirmed project profile. A generator's old default does not authorize adding branding. Preserve any specific instruction to keep all designs or disable duplicate removal.

Inspect the output manifest and contact sheet, check pixel dimensions and DPI against the physical format, and verify every requested design and count. Report skipped duplicates with their identity. Keep a printable paper canvas distinct from an image sized only to the cut area. Verify current Design Space limits when they affect the requested layout.
