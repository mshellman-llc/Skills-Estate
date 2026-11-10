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
  "source": "Estate default for artifacts with no selected brand",
  "colors": {
    "background": "#FFFFFF",
    "text": "#11141A",
    "muted": "#535559",
    "border": "#E2E2E3",
    "surface": "#F5F5F5",
    "accent": "#37437D",
    "chart-1": "#24265B",
    "chart-2": "#434D90",
    "chart-3": "#6577BD",
    "chart-4": "#8BA1DE",
    "chart-5": "#B5CAFA",
    "chart-6": "#535559",
    "status-good": "#18703F",
    "status-warning": "#96500A",
    "status-critical": "#C4302B"
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

The neutral profile has no logo, footer mark, cover imagery, gradients, or bundled fonts. Add a title, date, and author when the format needs them. Do not add colored side accents to cards, rows, badges or callouts.

`chart-1` to `chart-5` are a dark-to-light ramp of the profile's own color, and `chart-6` is a neutral for a sixth series. They color data series and the groups on boards, in that fixed order, and they are never used for text, buttons or page chrome. Do not use mixed hues, and keep a legend. A client profile replaces them with its own recorded chart colors; it does not inherit these.

`status-good`, `status-warning` and `status-critical` mark state (on track, at risk, blocked), never a group. A status color always appears with its text label. A client profile that records no status roles shows state through labels and neutral colors.

## Review the result

Inspect the rendered artifact for the selected colors, fonts, logo treatment, and readable contrast. Body text needs a contrast ratio of at least 4.5:1, and large text 3:1. Check file properties, speaker notes, headers, and footers for another identity. A profile or checker alone does not prove that a renderer applied it. Report the profile used and any substitutions.
