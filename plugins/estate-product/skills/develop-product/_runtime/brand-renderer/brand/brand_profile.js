"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

function resolveProfile(explicit, cwd = process.cwd(), anchor = __filename) {
  const selected = explicit || process.env.SKILLS_BRAND_PROFILE;
  if (selected) {
    const file = path.resolve(selected);
    if (!fs.existsSync(file) || !fs.statSync(file).isFile())
      throw new Error(`Selected brand profile does not exist: ${file}`);
    return fs.realpathSync(file);
  }
  const project = path.join(cwd, "brand.md");
  if (fs.existsSync(project) && fs.statSync(project).isFile()) return fs.realpathSync(project);
  for (let parent = path.dirname(path.resolve(anchor));;) {
    for (const suffix of ["references/estate/brand.md", "policies/brand.md"]) {
      const file = path.join(parent, suffix);
      if (fs.existsSync(file) && fs.statSync(file).isFile()) return fs.realpathSync(file);
    }
    const next = path.dirname(parent);
    if (next === parent) break;
    parent = next;
  }
  throw new Error("No brand policy found. Supply a profile or SKILLS_BRAND_PROFILE.");
}

function loadProfile(file) {
  const blocks = [...fs.readFileSync(file, "utf8").matchAll(/```json\s*\n([\s\S]*?)\n```/g)];
  if (blocks.length !== 1) throw new Error("A profile needs exactly one JSON block");
  const p = JSON.parse(blocks[0][1]);
  if (p.status !== "confirmed") throw new Error("This renderer requires a confirmed profile");
  if (!p.name || !p.source) throw new Error("A profile needs a name and source");
  for (const role of ["background", "text", "muted", "border", "surface", "accent"])
    if (!/^#[0-9a-fA-F]{6}$/.test((p.colors || {})[role] || ""))
      throw new Error(`Missing or invalid color: ${role}`);
  for (const [role, value] of Object.entries(p.colors))
    if (!/^[a-z][a-z0-9-]*$/.test(role) || !/^#[0-9a-fA-F]{6}$/.test(value))
      throw new Error(`Invalid color token: ${role}`);
  for (const role of ["body", "headings"])
    if (!/^[a-zA-Z0-9 ,"'-]+$/.test((p.type || {})[role] || ""))
      throw new Error(`Invalid font stack: ${role}`);
  for (const key of ["border_px", "radius_px"]) {
    const value = (p.layout || {})[key];
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 100)
      throw new Error(`Missing or invalid layout value: ${key}`);
  }
  return p;
}

function contrast(a, b) {
  function luminance(value) {
    return [1, 3, 5].map(i => parseInt(value.slice(i, i + 2), 16) / 255)
      .map(x => x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4)
      .reduce((sum, c, i) => sum + c * [0.2126, 0.7152, 0.0722][i], 0);
  }
  const x = luminance(a), y = luminance(b);
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}

function compileTokens(p, file) {
  const mapping = JSON.parse(fs.readFileSync(path.join(__dirname, "token-roles.json"), "utf8"));
  const palette = p.colors, colors = {};
  const color = role => ({hex: palette[role].toUpperCase(), role,
    cssVar: "--brand-" + role, brand: role === "accent", group: role});
  for (const [key, role] of Object.entries(mapping.roles)) colors[key] = color(role);
  for (const role of Object.keys(palette)) if (!colors[role]) colors[role] = color(role);
  const radius = p.layout.radius_px;
  return {
    provenance: {source: fs.realpathSync(file),
      sourceSha256: crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"),
      mode: "authoritative", guidelines: p.name},
    colors, aliases: mapping.aliases,
    rules: {
      warmAccentsAllowed: true, warmSurfacesAllowed: [],
      borderWidthPx: p.layout.border_px, borderNeverBlack: false,
      borderColorsBySurface: {light: palette.border, sand: palette.border},
      radius: {allowedPx: [radius], defaultPx: radius, smallPx: radius, capPx: radius,
        pillPx: 999, pillUsage: "avatars and status indicators"},
      headingCase: p.layout.heading_case || "sentence",
      labelTrackingEm: p.layout.label_tracking_em || 0, bodyAlign: "left", titleUnderline: false,
      footer: {required: false, convention: false}, markAndLockupTogether: false,
      shadow: {allowed: false, maxOffsetPx: 0},
      eyebrow: {brandHex: palette.muted, defaultHex: palette.muted,
        brandContrastOnWhite: Math.round(contrast(palette.muted, palette.background) * 100) / 100,
        defaultContrastOnWhite: Math.round(contrast(palette.muted, palette.background) * 100) / 100,
        wcagLargeTextMin: 3, onDarkHex: palette.background}
    },
    type: {...p.type, family: p.type.body, numerals: "tabular", monospaceInBodies: false},
    logo: p.logo || null, blocked: {}
  };
}
module.exports = {resolveProfile, loadProfile, compileTokens, contrast};
