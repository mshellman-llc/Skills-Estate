# Typography production checks

Keep composition approval separate from production approval. Before preparing output, record intended dimensions, printer or vendor, cutter model, software version, material, finish, paper size, and cut method. Leave unknown fields unresolved rather than choosing an unsupported default.

## Size and edges

For Cricut Print Then Cut, verify the selected machine and paper profile; usable area also depends on design proportions. Maximum width and height do not describe a full rectangular packing area. — [Cricut sizing](https://help.cricut.com/hc/en-us/articles/360009429814-How-large-can-I-Print-Then-Cut).

Keep three dimensions distinct:

- **Safe margin:** protected distance from essential content to the cut boundary.
- **Offset:** visible backing shape or border around the artwork.
- **Bleed:** expendable printed color beyond the cut boundary.

Inspect the nearest serif, punctuation mark, and swash when assessing safe margin. Choose edge dimensions from the production profile and a material test. Existing generator defaults for sheet area or bleed must be checked against that profile; do not silently rewrite the generator. — [Cricut edge terminology](https://help.cricut.com/hc/en-us/articles/360009387274-How-to-Print-Then-Cut-in-Design-Space).

## Sources and exports

Retain editable text, font/face identity, line breaks, spacing, baseline adjustments, dimensions, and colors. Confirm that the specified font rendered without substitution. Create outlined exports from this master; preserve the master for later wording changes. Cricut requires imported SVG/DXF text to be converted to shapes. — [Cricut unsupported items](https://help.cricut.com/hc/en-us/articles/360009553213-Image-uploads-unsupported-items).

For raster output, calculate effective PPI from pixels divided by final inches. Transparent padding affects the relationship between assigned canvas size and visible artwork. Re-render from the master when more detail is needed.

Make the intended backing opaque and the outside transparent. Check the alpha channel against light and dark backgrounds. Inspect the imported silhouette so disconnected letters do not become separate cuts. For multilayer Cricut printing, use the intended flattened printable shape and verify its preview. — [Cricut Print Then Cut](https://help.cricut.com/hc/en-us/articles/360009387274-How-to-Print-Then-Cut-in-Design-Space).

## Physical acceptance

Print a ruler-checked proof at the intended size. Examine counters, thin strokes, punctuation, joins, reversed text, and reading order before testing the actual stock and cut. Record dimensions, settings, a photograph, and the observed result. Vendor minimums are profile-specific benchmarks, not universal typography guarantees. — [Example vendor requirements](https://www.stickermule.com/faqs/stickermule/what-are-your-artwork-requirements-for-stickers-and-labels).

## Font rights

Keep font identities and rights references with the source. Presence on a computer or an embedding flag alone does not establish redistribution rights. Distinguish rendered artwork from sharing font software. OFL permits graphics while imposing separate conditions on font redistribution; retain the applicable license when a permitted redistribution is actually requested. Do not bundle font binaries by default. — [OFL FAQ](https://openfontlicense.org/ofl-faq/).
