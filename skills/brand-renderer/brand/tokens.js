/** Renderer token API backed by the selected Markdown brand profile. */
"use strict";
const profile = require("./brand_profile.js");
const TOKENS_PATH = profile.resolveProfile();
const raw = profile.compileTokens(profile.loadProfile(TOKENS_PATH), TOKENS_PATH);

const hex = {};        // { navy: "#080F28", ... }
const bare = {};       // { navy: "080F28", ... }  docx/pptx form
const byHex = {};      // { "#080f28": {key, name, role, brand, group} }
for (const [key, v] of Object.entries(raw.colors)) {
  hex[key] = v.hex;
  bare[key] = v.hex.replace(/^#/, "");
  byHex[v.hex.toLowerCase()] = { key, ...v };
}

// Semantic aliases. The CSS owns the values; these own the names the producers
// say out loud, so a CSS variable rename touches only the alias map instead of
// every renderer.
const aliases = {};
for (const [name, target] of Object.entries(raw.aliases || {})) {
  if (name.startsWith("$") || !raw.colors[target]) continue;
  aliases[name] = target;
  hex[name] = raw.colors[target].hex;
  bare[name] = raw.colors[target].hex.replace(/^#/, "");
}

/** Every canonical hex, lowercased, for lint checks. */
const allowedHexes = new Set(Object.keys(byHex));

/** Hexes this system used to emit and must never emit again. */
const retiredHexes = {};
for (const [group, spec] of Object.entries(raw.retired || {})) {
  if (!spec || !spec.hexes) continue;
  for (const h of spec.hexes) {
    retiredHexes[h.toLowerCase()] = {
      group,
      replacedBy: (spec.replacedBy || {})[h] || (spec.replacedBy || {})[h.toLowerCase()] || null,
      reason: spec.reason || "",
    };
  }
}

/** Brand colors that count toward the per-surface limit, by group. */
function brandGroup(hexValue) {
  const t = byHex[String(hexValue).toLowerCase()];
  return t && t.brand ? t.group : null;
}

module.exports = {
  tokensPath: TOKENS_PATH,
  provenance: raw.provenance,
  colors: raw.colors,
  rules: raw.rules,
  type: raw.type,
  logo: raw.logo,
  retired: raw.retired,
  hex,
  bare,
  byHex,
  aliases,
  allowedHexes,
  retiredHexes,
  brandGroup,
};
