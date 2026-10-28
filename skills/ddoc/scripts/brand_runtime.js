"use strict";
const fs = require("fs");
const path = require("path");
const candidates = [
  path.join(__dirname, "..", "_runtime", "brand-renderer", "brand", "tokens.js"),
  path.join(__dirname, "..", "..", "brand-renderer", "brand", "tokens.js"),
];
const selected = candidates.find(file => fs.existsSync(file));
if (!selected) throw new Error("The deck package is missing its brand runtime. Rebuild the package with its declared dependencies.");
module.exports = require(selected);
