# Build the static reference

Build the option overview and matrix from reconciled records. The reference should let a reader inspect every option without selecting a tab. Keep all staffing variants visible in the page and its print output.

## Brand and runtime

Run `brand-renderer/scripts/runtime_preflight.py --json` from the packaged dependency. Use an explicit profile, the configured project profile or the estate neutral profile in that order. The profile owns fonts, colors, borders and logo requirements. Declared assets must exist. A missing explicitly selected profile is an error, not permission to substitute a neutral identity.

The bundled builder uses Python's standard library and the packaged brand runtime. It embeds the selected assets in the HTML and needs no server. Pass `--profile /project/brand.md` when selecting an explicit identity.

```bash
python3 scripts/build_scope.py examples/comparison-source.json examples/comparison-plan.json scope.html
```

Use a new output path. The command saves a reconciliation receipt beside the HTML.

## Composition

The header names the decision and client. A source date identifies the quote revision the reader is considering. Synthetic examples carry that label.

Each option summary explains the scope difference supported by its actual items. The pricing table shows every requested staffing plan, marking the active plan and retaining its own duration and hours. A single quote receives one summary panel. Included, optional and available counts remain separate.

The grouped scope matrix uses one column per quote. Each cell displays a written status and its own item hours; color is supplementary. An absent item has no hours. The item description stays visible because another option may include that work. A legend defines the states without suggesting that a deselected addition is free.

The scope conditions follow the matrix. Include material exclusions and dependencies from the captured source. Do not invent a benefit, recommendation or licensing fact to fill empty space. Additional diagrams belong only when they explain a source-supported boundary that the matrix cannot show.

## Staffing and price rules

A snapshot price covers its staffing plan. The matrix intentionally contains no per-item currency allocation. Use exact figures unless the user requests rounding. A rounded headline includes the exact quote beneath it so a reader can distinguish the two.

Different options and staffing variants may have different hours or weeks. Never label the hours constant without checking every relevant record. The builder places option-specific hours in the cells and leaves staffing hours in the pricing tables.

## Browser and print review

Run `scripts/check_scope.mjs` with the local HTML URL, a new output directory, and the presentation JSON path. The test environment needs Node.js and Playwright with a Chromium browser. `PW_MODULE` can point to the installed Playwright module; `PW_CHROMIUM` can select a Chromium executable.

The checker captures desktop and narrow views, checks overflow outside the scrollable matrix, verifies that the matrix can be scrolled, blocks remote requests and exports a landscape A4 PDF. PDF tables may continue across pages with repeated headers. Do not shrink the full scope into a single unreadable page.

Inspect all printed pages and compare the displayed figures with the reconciliation receipt. Confirm that every item appears and that status labels survive printing. The browser test cannot judge whether the summary accurately describes an option.

## Delivery record

Save the source capture and presentation JSON with the HTML, receipt, PDF and review evidence. Run the writing and canonical-brand checks on the final output. Retain failed renderings in separate attempt folders. Link the finished files using the current host's supported file links; no particular cloud output directory is required.
