# Brand policy

This file is the estate's branding authority. Edit it here, then run `python3 tools/estate.py sync`. The build copies this policy into each skill package that needs it. Generated copies are checked by hash and are never edited directly.

## Select the identity

Use the brand profile explicitly named by the user. Otherwise use the current project's `brand.md`. When neither exists, use the neutral profile below. A profile from another project or an earlier conversation does not govern this artifact.

A project profile uses the same JSON block format as this file. It records `name`, `status`, `source`, `colors`, `type`, `logo`, and optional `voice` and `layout` rules. A draft profile needs the user's authorization for the artifact before its values apply. Keep client profiles and licensed assets in their project, outside this repository.

Read exact values from the selected profile. Do not infer colors from a company name or reconstruct a logo. Use a supplied logo file only within its recorded usage rights. If a font is unavailable, use the profile's fallback and report the substitution. For a missing role, use that role's neutral value and record the substitution. Co-branding needs both profiles and the user's explicit instruction.

## Neutral profile

```json
{
  "name": "Neutral",
  "status": "confirmed",
  "source": "Estate neutral defaults, established 2026-10-19",
  "colors": {
    "background": "#FFFFFF",
    "text": "#1A1A1A",
    "muted": "#5F6368",
    "border": "#D9DCE1",
    "surface": "#F5F6F7",
    "accent": "#2F5D8A",
    "chart-1": "#2A78D6",
    "chart-2": "#EB6834",
    "chart-3": "#1BAF7A",
    "chart-4": "#EDA100",
    "chart-5": "#E87BA4",
    "chart-6": "#008300"
  },
  "type": {
    "body": "system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif",
    "headings": "system-ui, -apple-system, Segoe UI, Helvetica, Arial, sans-serif",
    "office": "Arial",
    "body_min_pt": 11,
    "screen_min_px": 16,
    "slide_min_pt": 18
  },
  "logo": null,
  "layout": {"border_px": 1, "radius_px": 4, "heading_case": "sentence"},
  "voice": "Use the author's confirmed voice profile when supplied; otherwise write plainly and preserve meaning."
}
```

The neutral profile has no logo, footer mark, cover imagery, gradients, decorative icons, or bundled fonts. Add a title, date, and author when the format needs them.

`chart-1` to `chart-6` are a chart palette, not brand colors. They color data series and the groups on boards, in that fixed order. They are the first six categorical colors of the colorblind-checked data visualization palette (light theme), and they are never used for text, buttons or page chrome. A client profile replaces them with its own recorded chart colors; it does not inherit these.

## Review the result

Inspect the rendered artifact for the selected colors, fonts, logo treatment, and readable contrast. Body text needs at least 4.5:1 contrast; large text needs at least 3:1. Check file properties, speaker notes, headers, and footers for another identity. A profile or checker alone does not prove that a renderer applied it. Report the profile used and any substitutions.
