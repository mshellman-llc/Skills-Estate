---
skill: sticker-sheets
title: Two Letter Print Then Cut sheets with exact sticker counts
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: 1b464817a7997c722c9ce4b4ea92ffda707eb21f6aceee9a70aecc3491c02c38
---

## Request

I need Print Then Cut sheets for my Cricut Joy Explore on US Letter: 3 each of monstera_01 and monstera_02 at 2.5 inches, 12 cactus at 1.5 inches, and 2 watering cans at 3 inches wide. Keep every design even if two look alike, and put the monsteras on their own sheet. The project is in inputs/ (generator help and design inventory).

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `sticker-sheets` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `spec.json`.

#### design-inventory.md

#### Design inventory: Fernlight Plant Co. sticker project

Folder: designs/ (PNG, transparent background). Pixel hashes are SHA-1 of decoded RGBA data.

| File | Canvas px | Transparent-trimmed bounds px | Aspect | Pixel hash |
|---|---|---|---|---|
| monstera_01.png | 1800 x 1800 | 1500 x 1500 | 1:1 | 3f9a1c07 |
| monstera_02.png | 1800 x 1800 | 1500 x 1500 | 1:1 | b72e55d4 |
| cactus.png | 1200 x 1200 | 1000 x 1000 | 1:1 | 0c41ae92 |
| watering_can.png | 2400 x 1600 | 2100 x 1400 | 3:2 | d58810fb |
| fern_spare.png | 1800 x 1800 | 1500 x 1500 | 1:1 | 3f9a1c07 |

Notes
- fern_spare.png is not part of this order. It has the same pixel hash as monstera_01.png.
- monstera_01 and monstera_02 have different hashes (different leaf cut-outs), so they are separate designs.
- Project brand file: none present. No maker mark was requested.

#### generator-help.txt

$ python3 tools/make_sheets.py --help   (project: fernlight-stickers)
usage: make_sheets.py [-h] --spec SPEC [--paper {letter,a4}] [--canvas {paper,cutarea}]
                      [--dpi DPI] [--gap GAP_IN] [--no-brand] [--no-dedupe]
                      [--out DIR]

  --spec        JSON list of {file, width_in, count, sheet}
  --paper       physical paper (letter = 8.5 x 11 in)
  --canvas      paper: full printable page PNG; cutarea: image sized only to the cut area
  --dpi         default 300
  --gap         spacing between stickers, default 0.25 in
  --no-brand    do not add a maker mark (default adds the project mark)
  --no-dedupe   keep designs whose pixels match another design
  --out         writes sheet_N.png, manifest.json, contact_sheet.png

Project config (project.toml)
  letter_cut_area_in = [9.25, 6.75]   # last edited 2025-03; Design Space limit not re-verified
  orientation = landscape

## Output

Both sheets fit on US Letter with the counts you gave. I have not rendered them. The generator isn't available to me here, so I worked the layout out by hand from its `--help` and your design inventory. Run the command below to produce the PNGs, then check the output against the numbers here.

#### What I checked

- **Duplicates.** `monstera_01` (hash 3f9a1c07) and `monstera_02` (hash b72e55d4) have different pixels, so they are two designs. You asked to keep every design, so I'm passing `--no-dedupe` anyway. `fern_spare.png` has the same hash as `monstera_01`, but it isn't in your order and stays out of the spec.
- **Branding.** You didn't ask for a maker mark and the project has no brand file, so the command uses `--no-brand`. The help says the generator adds its project mark by default.
- **Sizes.** Sizes come from the transparent-trimmed bounds, not the canvas. The watering can is 2100 x 1400 px trimmed, which gives 3.0 x 2.0 in.
- **Paper and cut area.** Paper is Letter, 8.5 x 11 in. The cut area is a separate limit. `project.toml` sets it to 9.25 x 6.75 in, landscape, last edited 2025-03. I couldn't check Design Space's current limit, so confirm it before you print. If it has changed, the layouts below need to be redone.

#### Command

```
python3 tools/make_sheets.py --spec spec.json --paper letter --canvas paper \
  --dpi 300 --gap 0.25 --no-brand --no-dedupe --out out/
```

I used `--canvas paper` so you get a full printable page. A `cutarea` image would be only 2775 x 2025 px and isn't a Letter page. Spec file: `out/spec.json`.

#### Layout (inches from the top-left of the cut area, 0.25 in gaps)

**Sheet 1: monsteras, 6 stickers, using 8.0 x 5.25 in**

| Row | y | Stickers (x position) |
|---|---|---|
| 1 | 0 | monstera_01 at 0, 2.75, 5.5 |
| 2 | 2.75 | monstera_02 at 0, 2.75, 5.5 |

**Sheet 2: cactus and watering cans, 14 stickers, using 8.5 x 6.75 in**

| Row | y | Stickers (x position) |
|---|---|---|
| A | 0 | cactus at 0, 1.75, 3.5, 5.25, 7.0 |
| B | 1.75 | cactus at 0, 1.75, 3.5, 5.25, 7.0 |
| C | 3.5 | watering can (3.0 x 2.0) at 0 and 3.25 |
| Right column | 3.5 and 5.25 | cactus at x = 6.5, two stacked |

Cactus total: 5 + 5 + 2 = 12. Watering cans: 2. Sheet 2 reaches the full 6.75 in height, so it has no spare room vertically. Its width is 8.5 of 9.25 in.

#### Pixel checks at 300 DPI

| Item | Printed size | Pixels | Source pixels (trimmed) |
|---|---|---|---|
| Monstera | 2.5 x 2.5 in | 750 x 750 | 1500 x 1500 |
| Cactus | 1.5 x 1.5 in | 450 x 450 | 1000 x 1000 |
| Watering can | 3.0 x 2.0 in | 900 x 600 | 2100 x 1400 |
| Letter canvas, landscape | 11 x 8.5 in | 3300 x 2550 | |
| Cut area | 9.25 x 6.75 in | 2775 x 2025 | |

All sources are larger than their print size, so nothing is upscaled.

#### Still to check once the PNGs exist

1. Open `manifest.json` and confirm 3 + 3 on sheet 1 and 12 + 2 on sheet 2.
2. Check `contact_sheet.png` for overlaps and that no sticker crosses the cut area.
3. Confirm each sheet is 3300 x 2550 px at 300 DPI and the artwork sits inside the cut area.
4. Confirm the Design Space cut-area limit for Letter.
5. Confirm there is no maker mark on either sheet.

#### Files

- `out/spec.json`: the generator spec with the four lines above (monstera_01 x3, monstera_02 x3 on sheet 1; cactus x12, watering_can x2 on sheet 2).
- `out/answer.md`: this reply.

No sheet images were created.
