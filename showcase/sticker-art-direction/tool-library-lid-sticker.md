---
skill: sticker-art-direction
title: Two type directions for a volunteer tool library bucket sticker
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: dcdd4dd6bb05db06865fc642b5d0eb269386f09c5a87bf2a31168f49b62cdf4f
---

## Request

We're a volunteer tool library and I need a sticker for the lids of our loan buckets that says "Return it better than you found it." Can you give me a couple of distinct directions and tell me which one to print? Brief, fonts we have and our cutter details are attached.

## Inputs

**Dry run.** This skill normally works on live systems or its owner's own setup. Here the system state is invented in the inputs below, and nothing was changed anywhere. Run of the built `sticker-art-direction` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `directions-source.svg`.

#### brief.md

#### Loan bucket sticker brief

Organisation: Alder Row Tool Library (volunteer-run, lends hand tools in grey 10-litre buckets).

Copy (supplied, keep as written): Return it better than you found it.

Use: one sticker per bucket lid, read at arm's length when someone is dropping a bucket off. Borrowers are neighbours, ages 16 to 80. Tone: warm, direct, a little dry. It is a house rule, not a joke.

Colours: no brand guide. Lid is mid-grey plastic. Prefer two inks plus the sticker paper white.

No logo on this sticker. Do not change the wording.

Open questions from the committee: someone suggested all caps "BETTER" as the loud word. Someone else thinks that sounds like a scolding.

Size: 3 in wide, round or rounded rectangle, either is fine.

#### fonts-and-cutter.txt

Fonts installed on the library laptop (font manager export, 4 Nov 2026)
Fraunces  v1.000 variable (opsz, wght, SOFT, WONK)   licence file: OFL.txt present
Archivo   v2.001 variable (wdth 62-125, wght 100-900)  licence file: OFL.txt present
Space Mono Regular/Bold v1.100                         licence file: OFL.txt present
Inter     v4.0 variable                                licence file: OFL.txt present
Gill Sans MT  (came with Office)                       no licence file; rights unknown

Production
Cutter: Cricut Explore 3 (Design Space, version not recorded)
Material: printable white sticker paper, matte, 8.5 x 11 in
Printer: office inkjet, colour (model not recorded)
Method: Print Then Cut
Previous sticker: cut ran about 1 mm off to the left on the first test sheet
No proof printed yet for this design.

## Output

### Bucket lid sticker: two directions, and which to print

**Recommendation: print Direction A (the stacked version) as the first proof.** It reads at arm's length, keeps "better" as the one emphasised word without shouting it, and the line breaks follow how people say the sentence. Direction B is the warmer fallback if the committee prefers a badge feel, but its smallest words are too small for lid-at-arm's-length reading.

Neither direction has been rendered or looked at yet. I could only write the editable source, not run a renderer, so everything below about how they look is intent plus size arithmetic. The first job is to open the file, see whether the fonts loaded, and judge it by eye.

#### Working brief (from your notes)

- Copy kept exactly: "Return it better than you found it."
- Function: a house rule, warm and dry, not a joke and not a scolding.
- Read at arm's length on a mid-grey lid, by borrowers aged 16 to 80.
- No brand guide, so the type and colour below are a **proposal for this sticker only**: ink green #1F3A2E and amber #B25E09 on white paper. Both pass 4.5:1 against white by a wide margin (the green is very dark; I estimated the amber at roughly 5:1 and it should be checked in a contrast tool).

#### The caps question

I'd keep sentence case. In "Return it better than you found it", the stress falls on "better", and the committee's worry is right: capitals on that word would make the rule read as a telling-off. A is built so "better" wins on size and weight alone, which is firmer than B's italic but still polite.

#### Direction A: stacked house rule

- **Structure:** left-aligned, four lines: *Return it / **better** / than you / found it.* Reading order is top to bottom with the eye landing on "better", then falling to "found it."
- **Type:** Archivo (installed v2.001, OFL), medium weight for the plain lines at 40 units (about 29 pt on a 3 in sticker), extra bold at 60 units for "better" in amber. One family, so hierarchy comes from weight, size and colour only.
- **Shape:** 3 x 3 in rounded square, 0.30 in corner radius.
- **Why:** plain and sturdy, like a label on a tool you trust. Breaking at "than you / found it." keeps the comparison in one breath.
- **Risk to check:** "better" at 60 units is estimated to be about 2.1 in wide against about 2.3 in of usable width, which is tight. If it crowds the right edge in the proof, drop it to 56 rather than stretching or condensing the letters.

#### Direction B: one even sentence in a badge

- **Structure:** centred, two lines: *Return it **better** / than you found it.* No size change; the only emphasis is amber italic on "better".
- **Type:** Fraunces (installed v1.000, OFL), medium weight, 24 units (about 17 pt).
- **Shape:** 3 in circle with a thin inner ring.
- **Why:** reads as a single friendly sentence, closer to a shop-door plaque. It's the softer tone.
- **Risks:** at about 17 pt the small words may be hard to read from arm's length on a grey lid; Fraunces at a small size also needs its optical-size axis checked, since a display cut shrunk down can look spindly. The second line is nearly as wide as the circle allows at that height, so edge clearance is tight.

These two differ in silhouette, alignment, typographic voice and emphasis, so they are real alternatives, not font swaps. No further variants are worth making until you've seen one of these on paper.

#### Research status

I haven't studied outside reference artifacts yet, so this is an early brief, not a researched direction. Questions to answer before expanding to other buckets or a set: how do hand-tool labels and workshop signs handle a stacked rule with one emphasised word, and how do community lending libraries mark loan items? I'd look at real examples and cite them before developing a family of stickers. The centred-versus-flush-left choice follows Butterick's guidance that centring is an option, not a default.

#### Before you print

1. Open `directions-source.svg` and confirm Archivo and Fraunces rendered, not a fallback. Look at A and B at full screen, then at 3 in on screen.
2. Print A on plain paper at exactly 3 in, check it with a ruler, and view it from arm's length against a grey lid or a grey card.
3. Then do a Print Then Cut test on the sticker paper. Your last cut ran about 1 mm left, so I've asked for at least 1.5 mm of clear space between the type and the cut line on this first test. Safe margin, offset and bleed are not set yet; they should come from this test, not from a guess.
4. Convert text to shapes only in the export for Design Space (it needs outlines). Keep the SVG here as the editable master.

#### Gaps and assumptions

- Design Space version and printer model weren't recorded, so I haven't chosen any print settings.
- Gill Sans MT is installed but has no licence file, so I left it out. Archivo and Fraunces both have OFL files on the laptop. I haven't bundled font files with anything.
- Nothing has been published, ordered or uploaded.

#### Files

- `out/directions-source.svg`: editable source for both directions, live text, units of 100 per inch. A is a 300 x 300 rounded rectangle with lines at 40 / 60 / 40 / 40 units; B is a 300-unit circle with two centred lines at 24 units. Unrendered.
- `out/decision-record.md`: copy, palette, font versions and licences, production details, and what remains open (render check, actual-size print, cut test).

### File: decision-record.md

#### Decision record: bucket lid sticker, v0.1

**Copy (supplied, unchanged):** Return it better than you found it.
No wording or punctuation changes proposed. Sentence case kept; the final full stop is in the supplied copy.

| Item | Value | Status |
|---|---|---|
| Size | 3.00 in wide; A is 3.00 x 3.00 in, B is a 3.00 in circle | proposed |
| Palette | ink #1F3A2E, amber #B25E09, white paper | proposal, no brand guide supplied |
| Fonts | A: Archivo v2.001 (OFL). B: Fraunces v1.000 (OFL) | installed, licence files present; not bundled |
| Gill Sans MT | not used; rights unknown | excluded |
| Cutter | Cricut Explore 3, Print Then Cut | Design Space version, printer model unrecorded |
| Material | matte printable white sticker paper | |
| Proof | none printed | open |

Spacing: font metrics and kerning unchanged. No tracking applied.
Edges (to be set from a test, not assumed): safe margin, offset and bleed unresolved. The last cut drifted about 1 mm left, so the first proof should carry at least 1.5 mm of clear space between the type and the cut line until a test sheet shows the real drift.

Not yet done: render check of either direction; actual-size print; cut test.
