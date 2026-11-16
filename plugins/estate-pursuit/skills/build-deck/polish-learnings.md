# Deck Polish Learnings

Accumulated fixes from past deck QA passes. **Read this before building any deck**
(GATE 2 step 1) and apply it as a pre-checklist. **Append to it** whenever a fix
recurs across decks; that is the purpose of this file.

Format: one bullet per learning. Keep it short and actionable. Note the trigger
("when X happens, do Y"). Delete a rule if it stops being true.

---

## Text

- (seed) Break body copy at meaning units, not at the edge of the box. Avoid a single orphaned word on its own line.
- (seed) Keep the one-message visible/implied on every content slide. If a slide doesn't ladder up to it, cut or repurpose it.

## Layout

- Use the space the explanation needs. Add content only when it answers an audience question; whitespace does not require a card.
- Check hierarchy and sequence from slide titles and heading levels in the extracted text. Read every diagram label and table from the DOM.

## Icons / images

- (seed) Align an icon to the *visual* center of its background shape rather than its bounding box. If it sits off center, move the icon and leave the background.
- (seed) Keep real body text, prices, and claims as editable text, never baked into a raster image.

- Keep an edge label clear of its endpoint shapes. A shape drawn later can conceal the label even when both fit the page.
- Draw requests and receipts in their actual directions. A combined interface label can hide the return path.

## Export

- (seed) Verify PDF/PNG export doesn't reflow or clip. Check the last slide and any dense table slide specifically.

<!-- Append new learnings above this line, under the right heading. Add headings as needed. -->
