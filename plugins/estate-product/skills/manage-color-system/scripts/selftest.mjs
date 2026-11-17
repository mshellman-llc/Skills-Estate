#!/usr/bin/env node
// Self-test: audits the Bearing fixtures and the v2 recipe, and checks the findings that must appear and the pairs that must pass.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { audit, judge, apca } from './color-steward.mjs';
const here = path.dirname(fileURLToPath(import.meta.url));
const read = p => fs.readFileSync(path.join(here, '..', p), 'utf8');
let failed = 0; const check = (ok, what) => { console.log(`${ok ? 'pass' : 'FAIL'}  ${what}`); if (!ok) failed++; };

const before = audit(read('fixtures/bearing-tokens.css'), [{ name: 'bundle.css', css: read('fixtures/bearing-bundle-colors.css') }], read('fixtures/bearing-tokens-source.json'));
const codes = new Set(before.findings.map(f => f.code));
for (const c of ['PAIR_FAILS', 'PRIMITIVE_DRIFT', 'STALE_BUILD', 'TOKEN_SHADOWED', 'LITERAL_OFF_SYSTEM', 'APCA_WEAK', 'ROLE_MISSING', 'HUE_NAME_LIES', 'HOVER_LOWERS_CONTRAST'])
  check(codes.has(c), `before v2: finds ${c}`);
check(before.pairs.some(p => p.fg === 'on-action' && p.theme === 'dark' && !p.pass.body), 'before v2: primary button text fails on Night');

const source = audit(read('fixtures/bearing-tokens-source.json'));
check(!source.findings.some(f => f.code === 'CLAIM_WRONG'), 'source notes: no false ratio alarms');

const { execFileSync } = await import('node:child_process');
const out = path.join(fs.mkdtempSync(path.join((await import('node:os')).tmpdir(), 'cs-')), 'v2.css');
execFileSync(process.execPath, [path.join(here, 'propose.mjs'), path.join(here, '..', 'recipes', 'bearing-v2.json'), '--out', out]);
const after = audit(fs.readFileSync(out, 'utf8'));
check(after.pairs.length >= 100 && after.pairs.every(p => p.pass[p.use]), `v2: all ${after.pairs.length} pairs pass`);
check(after.findings.length === 0, `v2: no findings (${after.findings.length})`);

check(Math.abs(judge('#000000', '#ffffff').wcag - 21) < 0.01, 'WCAG: black on white is 21:1');
check(Math.abs(apca('#a5a8b5', '#161824') + 54.147) < 0.01, 'APCA: #a5a8b5 on #161824 is Lc -54.15');
console.log(failed ? `${failed} failed` : 'all passed');
process.exit(failed ? 1 : 0);
