---
skill: manage-brand-profile
title: Client brand profile and holiday-hours web notice
source: fictional
model: claude-sonnet-5-5
date: 2026-11-04
skillSha256: c6d5ac41111ea61ab2c36ce3f75bb6233f4e9e3ea3d3df205f8033a5120c9e1c
---

## Request

Fernhill Veterinary Cooperative sent their brand notes and the text for a holiday-hours notice. Please set up their brand profile and build the notice as a one-page web page in their brand; I authorise using the draft profile for this page.

## Inputs

Run of the built `manage-brand-profile` task package. The recording session invented this scenario, the request and the inputs below before running the skill. It had no connectors, accounts or network access and could not execute scripts, so any scripted step was done by hand and the answer says so. Other files it produced, not shown here: `holiday-notice.html`.

#### brand-notes.md

#### Fernhill Veterinary Cooperative: brand notes

Source: brand sheet v2, sent by Priya Raman (communications lead), Sep 12, 2026. Priya says the sheet is not yet signed off by the board.

##### Colors
- Fern green: #2F5D50 (primary, headings, buttons)
- Cream: #F6F1E7 (page background)
- Clay: #B5532F (accent, used sparingly)
- Ink: #1E2A26 (body text)
- Light sage: #DDE6DF (panels)
- No chart colors or status colors defined.

##### Type
- Headings: Lora (licensed through the co-op's web font account; the files are not included here)
- Body: Source Sans 3 (same account)
- If unavailable: Georgia for headings, Arial for body

##### Logo
- A fern-leaf mark with the words "Fernhill Veterinary Cooperative". The file will follow from Priya. It may be used on the co-op's own pages and notices only.

##### Voice
- Warm and direct. "We" for the co-op, "you" for the pet owner. No exclamation marks. Say "pets" rather than "patients".

##### Layout
- Rounded corners of 8 px, thin 1 px sage borders, headings in sentence case.

#### holiday-notice.txt

Holiday hours notice, December 2026

Both clinics (Fernhill Road and Marsh Lane) change their hours over the holidays.

Dec 24: open 8:00 am to 1:00 pm, both clinics.
Dec 25 and Dec 26: closed. Emergency cases go to Northgate Animal Emergency, 24 hours, phone 555-0142.
Dec 27 to Dec 30: normal hours, 8:00 am to 6:00 pm.
Dec 31: open 8:00 am to 3:00 pm, both clinics.
Jan 1: closed. Emergency cases go to Northgate Animal Emergency.
Jan 2: normal hours resume.

Prescription refills: please request by Dec 19 so we can prepare them before the closures. Request through refills@example.com or the form at example.com/refills.

Contact for questions: reception@example.com.

## Output

I wrote the Fernhill brand profile and built the holiday-hours notice as a one-page web page. Both are saved locally and neither has been published. I have not rendered the page in a browser. I checked the markup and the contrast figures by reading and by hand calculation.

**Governing profile:** Fernhill Veterinary Cooperative, status **draft**. The brand sheet (v2, from Priya Raman, Sep 12, 2026) is not board-approved. Your instruction authorises these values for this notice only. The Baseline kit was not used, because a project profile was selected instead.

#### What the page contains

- Title "Holiday hours", with "Fernhill Veterinary Cooperative · December 2026" beneath it.
- An opening paragraph that says both clinics change hours and gives Northgate Animal Emergency (24 hours, 555-0142) for care while closed.
- A date table in a scrolling box, so it stays readable on a phone:
  - Dec 24: 8:00 am to 1:00 pm
  - Dec 25 and 26: closed
  - Dec 27 to 30: 8:00 am to 6:00 pm
  - Dec 31: 8:00 am to 3:00 pm
  - Jan 1: closed
  - Jan 2: normal hours resume
- A refills panel: request by Dec 19, with a button to example.com/refills and the address refills@example.com.
- A questions line with reception@example.com.

Copy follows the sheet's voice rules: "we" and "you", no exclamation marks, "pets" rather than "patients". Closed days carry the word "Closed" in bold, because the sheet defines no status colors and state is shown by label.

#### Brand values applied

| Role | Value |
|---|---|
| Background | Cream #F6F1E7 |
| Text | Ink #1E2A26 |
| Headings and links | Fern green #2F5D50, in Lora |
| Panels and table header | Light sage #DDE6DF |
| Button | Clay #B5532F with white text |
| Body type | Source Sans 3 at 16 px |
| Corners and borders | 8 px radius, 1 px sage |

#### Substitutions and gaps

- **Logo omitted.** The file has not arrived. I did not redraw the fern mark. The sheet limits it to the co-op's own pages, which this page is.
- **Fonts.** No font files were supplied and the page makes no network request. It names Lora and Source Sans 3 first, then the sheet's fallback of Georgia and Arial. Readers without those fonts installed will see the fallback. Add the licensed files from the co-op's font account to show the real faces.
- **Muted text color.** The sheet has none, so I used Baseline's neutral #535559 (6.6:1 on cream).
- **Charts and status colors.** The sheet defines none and the page uses none.

#### Contrast

- Ink on cream: above 12:1.
- Fern green on cream: 6.7:1.
- Fern green on sage: 5.9:1.
- White on clay (button): 4.9:1.
- **Clay on cream is 4.4:1, below the 4.5:1 minimum for body text.** The page never sets clay as small text on cream. It appears only as the button fill and as the keyboard focus ring. The profile records this restriction for later work.

Metadata check: the page title, the `lang` attribute and the footer area carry only Fernhill. There are no speaker notes, headers or other identities. All addresses use example.com.

#### Writing check

`writing_check.py` could not be run here, so I read the page copy and profile notes by hand against the writing standard. I found no filler, stock transitions or exclamation marks.

#### Decisions for you

1. Ask Priya Raman to confirm board approval of the sheet, or to confirm that the draft may be used elsewhere. Until then the profile applies to this notice only.
2. Ask Priya for the logo file and the web font files. With them I can add the mark to the header and reproduce the headings and body text in the brand fonts.
3. The source gives no year for the notice's dates other than "December 2026". Jan 1 and Jan 2 are shown without a year, as in the source.

#### Files

- `out/brand.md`: the draft profile with the JSON block (name, status, source, colors, type, logo, layout, voice), a substitutions table, and contrast notes.
- `out/holiday-notice.html`: the single-file page described above, with its styles inline and the profile colors as CSS variables.
- `out/answer.md`: this reply.

### File: brand.md

#### Fernhill Veterinary Cooperative brand profile

Status: draft. The brand sheet is not yet signed off by the board. The requester authorised these values for the December 2026 holiday-hours notice only. Confirm with Priya Raman before reusing them elsewhere.

```json
{
  "name": "Fernhill Veterinary Cooperative",
  "status": "draft",
  "source": "Brand sheet v2 from Priya Raman, communications lead, Sep 12, 2026. Recorded Nov 4, 2026.",
  "colors": {
    "background": "#F6F1E7",
    "text": "#1E2A26",
    "muted": "#535559",
    "border": "#DDE6DF",
    "surface": "#DDE6DF",
    "accent": "#2F5D50",
    "accent-secondary": "#B5532F"
  },
  "type": {
    "body": "Source Sans 3, Arial, sans-serif",
    "headings": "Lora, Georgia, serif",
    "office": "Arial",
    "body_min_pt": 11,
    "screen_min_px": 16,
    "slide_min_pt": 18
  },
  "logo": {
    "file": null,
    "description": "Fern-leaf mark with the words Fernhill Veterinary Cooperative",
    "rights": "The co-op's own pages and notices only",
    "note": "File not yet received from Priya Raman. Do not reconstruct."
  },
  "layout": {"border_px": 1, "radius_px": 8, "heading_case": "sentence"},
  "voice": "Warm and direct. We for the co-op, you for the pet owner. No exclamation marks. Say pets, not patients."
}
```

##### Substitutions and gaps

| Role | Treatment | Reason |
|---|---|---|
| muted | #535559 from the Baseline neutral profile | The sheet defines no muted color |
| chart colors | none | The sheet defines none; no chart is used |
| status colors | none; state shown by text label and neutral styling | The sheet defines none |
| fonts | Lora and Source Sans 3 named first; Georgia and Arial as the sheet's fallback | Font files were not supplied |
| logo | omitted | File not received |

##### Contrast notes

Computed from the hex values. Clay (#B5532F) on cream is 4.4:1, under the 4.5:1 body-text minimum. Use it for large text, rules, or as a button fill with white text (4.9:1), never for small text on cream. Fern green on cream is 6.7:1, ink on cream is well above 12:1.
