// Resolve the shared policy in source, standalone and embedded module layouts.
const fs = require('node:fs');
const path = require('node:path');
const candidates = [
  path.join(__dirname, '../_runtime/brand-renderer/scripts/browser_launch_policy.cjs'),
  path.join(__dirname, '../../brand-renderer/scripts/browser_launch_policy.cjs')
];
const selected = candidates.find(file => fs.existsSync(file));
if (!selected) throw new Error('Browser policy is missing. Rebuild the package with its declared brand runtime.');
module.exports = require(selected);
