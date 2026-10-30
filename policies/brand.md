# Brand policy

This file is the estate's branding authority. Edit it here, then run `python3 tools/estate.py sync`. The build copies this policy into each skill package that needs it. Generated copies are checked by hash and are never edited directly.

## Select the identity

Use the brand profile explicitly named by the user. Otherwise use the current project's `brand.md`. When neither exists, use the neutral profile below. A profile from another project or an earlier conversation does not govern this artifact.

A project profile uses the same JSON block format as this file. It records `name`, `status`, `source`, `colors`, `type`, `logo`, and optional `voice` and `layout` rules. A draft profile needs the user's authorization for the artifact before its values apply. Keep client profiles and licensed assets in their project, outside this repository.

Read exact values from the selected profile. Do not infer colors from a company name or reconstruct a logo. Use a supplied logo file only within its recorded usage rights. If a font is unavailable, use the profile's fallback and report the substitution. For a missing role, use that role's neutral value and record the substitution. Co-branding needs both profiles and the user's explicit instruction.

## Neutral profile

```json
{
  "name": "Baseline",
  "status": "confirmed",
  "source": "Baseline palette F, chosen by Megan as the default on 2026-10-30",
  "colors": {
    "background": "#FFFFFF",
    "text": "#11141A",
    "muted": "#535559",
    "border": "#E2E2E3",
    "surface": "#F5F5F5",
    "accent": "#37437D"
  },
  "type": {
    "body": "Inter, system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif",
    "headings": "Inter, system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif",
    "office": "Arial",
    "body_min_pt": 11,
    "screen_min_px": 16,
    "slide_min_pt": 18
  },
  "logo": null,
  "layout": {"border_px": 1, "radius_px": 6, "heading_case": "sentence"},
  "voice": "Use the author's confirmed voice profile when supplied; otherwise write plainly and preserve meaning."
}
```

The neutral profile is Baseline, Megan's default design system. Web pages, dashboards and interactive artifacts use its component kit in the `client-brand` skill: `baseline/baseline.css`, the Stockholm icons in `baseline/baseline-icons.svg` and `baseline/baseline-icons.json`, and the rules in `baseline/GUIDE.md`. Palette F, navy and pastel, is the default. Use palette E, ink and amber, only when requested, through `class="bl theme-ink"`.

The neutral profile has no logo, footer mark, cover imagery, gradients, or bundled fonts. Add a title, date, and author when the format needs them. Data charts use a dark-to-light ramp of the profile's own color: #24265B, #434D90, #6577BD, #8BA1DE, #B5CAFA. Do not use mixed hues, and keep a legend and a fixed series order. Do not add colored side accents to cards, rows, badges or callouts.

## Review the result

Inspect the rendered artifact for the selected colors, fonts, logo treatment, and readable contrast. Body text needs at least 4.5:1 contrast; large text needs at least 3:1. Check file properties, speaker notes, headers, and footers for another identity. A profile or checker alone does not prove that a renderer applied it. Report the profile used and any substitutions.
