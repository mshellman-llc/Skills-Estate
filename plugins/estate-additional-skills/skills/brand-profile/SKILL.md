---
name: brand-profile
description: Apply a confirmed project or client brand to an artifact, or use the estate neutral profile. Use for branded deliverables and brand profile creation or updates.
---


# Client brand

Read [the brand policy](references/estate/brand.md) before choosing visual values. It is generated from `policies/brand.md`, the only estate-wide branding authority. Do not copy its palette or type rules into this entrypoint or another skill.

Resolve the brand from the user's explicit choice or the current project's `brand.md`. If neither exists, use the neutral profile, which is Baseline. For a web page, dashboard or interactive artifact, read [the Baseline guide](baseline/GUIDE.md) and build from the bundled kit. State which profile governs. Read the profile and the assets it actually names; do not infer an identity from old templates.

When building a profile, record the source and date for colors, fonts, logos, layout, voice rules, and usage rights. Mark it draft until the user confirms it or explicitly authorizes its use for this artifact. Keep client assets beside the project profile. Never put them in this shared estate as defaults.

Apply the selected profile through the available rendering tool. Check the rendered result, metadata, notes, headers, and footers for mixed identities. Report the profile and any substitutions. The optional `tools/brand.py` in the estate checkout reads the profile's JSON block and emits CSS variables; a renderer still needs to use them.

## Shared standards

Apply the [shared workflow](references/estate/workflow.md) and [writing standard](references/estate/writing.md).
