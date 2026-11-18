# Material 3 color model

Notes for applying Material 3 color to any design system, written from the Material 3 color guidance (m3.material.io, styles/color) and the Material 2 color system pages, read 2026-11-17.

## From Material 2 to Material 3

Material 2 picked a primary and a secondary brand color with light and dark variants, plus surface, background and error, and on- colors for text placed on each. Accessibility came from checking swatches by hand against white or black text.

Material 3 keeps the on- pairing and replaces hand-picked variants with tonal palettes. A source color gives five key colors (primary, secondary, tertiary, neutral, neutral variant). Each becomes a palette of tones from 0 to 100. Roles then take fixed tones from those palettes, so contrast follows from tone distance: tones 50 apart give about 3:1, tones 70 apart give about 7:1.

## HCT

HCT describes a color by hue (0 to 360), chroma (0 to about 120) and tone (0 to 100, the CIELAB lightness). Changing hue or chroma leaves tone, and with it contrast, unchanged. HSL lightness does not map to tone; two colors with equal HSL lightness can differ widely in contrast.

Some hue and tone pairs cannot reach high chroma on screens. A palette's chroma drops at its light and dark ends for that reason.

## Roles

Surface roles: surface; surface-dim and surface-bright, which keep their relative brightness in both themes; five container tiers from lowest to highest, named by emphasis; on-surface and on-surface-variant for text and icons on any of them.

Accent roles: primary for the most important actions, secondary for less urgent elements and selected states, tertiary for small contrasting accents. Each has a container and on- partners. Containers are fills and never carry text.

Error roles stay static in dynamic schemes and still adapt to light and dark.

Outline marks important boundaries such as a text field edge. Outline-variant is for dividers and decoration and must not define a target's boundary.

Inverse roles reverse the surrounding UI, as on a snackbar. Fixed roles keep one tone in both themes and should not be used where contrast is required. Scrim dims content behind a modal.

## Contrast levels

Roles ship at standard, medium and high contrast. Medium aims at 3:1 minimums for people who find high contrast uncomfortable; high aims at 7:1. Custom components get these levels for free when they use role pairs.

## State layers

A state is an overlay in the content color at a fixed opacity: hover 8%, focus 10%, pressed 10%, dragged 16%. Disabled content uses 38%. One state layer applies at a time.

## Customization

A static baseline scheme can come from brand input colors. Color fidelity moves role tones toward the input color when the default tones would wash it out. Harmonization shifts a static semantic color's hue toward the primary hue, within limits that keep red reading as red; brand colors are not harmonized.

## Components

Material 3 groups components as buttons (button groups, buttons, extended FABs, FAB menu, FABs, icon buttons, segmented buttons, split buttons), date and time pickers, loading and progress indicators, navigation (bar, drawer, rail), sheets (bottom, side) and the rest: app bars, badges, cards, carousel, checkbox, chips, dialogs, divider, lists, menus, radio button, search, sliders, snackbar, switch, tabs, text fields, toolbars and tooltips. `component-roles.json` maps each to roles and to the LiveLaughCode component that plays its part.
