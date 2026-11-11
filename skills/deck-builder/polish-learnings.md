# Deck Polish Learnings

Accumulated fixes from past deck QA passes. **Read this before building any deck**
(GATE 2 step 1) and apply it as a pre-checklist. **Append to it** whenever a fix
recurs across decks — that is the whole point of this file.

Format: one bullet per learning. Keep it short and actionable. Note the trigger
("when X happens, do Y"). Delete a rule if it stops being true.

---

## Text

- (seed) Break body copy at meaning units, not at the edge of the box. Avoid a single orphaned word on its own line.
- (seed) Keep the one-message visible/implied on every content slide — if a slide doesn't ladder up to it, cut or repurpose it.

## Layout

- (seed) No giant empty white area. Lower/side whitespace gets a supporting diagram, decision criteria, or next-step cards — never decoration for its own sake.
- (seed) Thumbnail test: if a slide isn't legible as a thumbnail, the hierarchy is too weak. Fix before exporting.

## Icons / images

- (seed) Align an icon to the *visual* center of its background shape, not the bounding box. If it looks off, move the icon, not the background.
- (seed) Never bake real body text, prices, or claims into a raster image — keep them as editable text.

## Export

- (seed) Verify PDF/PNG export doesn't reflow or clip. Check the last slide and any dense table slide specifically.

<!-- Append new learnings above this line, under the right heading. Add headings as needed. -->
