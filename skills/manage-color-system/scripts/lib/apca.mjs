// APCA 0.0.98G-4g (SAPC), the contrast method in the WCAG 3 working draft. Returns Lc, signed.
export function sRGBtoY([r, g, b]) { const s = c => Math.pow(c / 255, 2.4); return 0.2126729 * s(r) + 0.7151522 * s(g) + 0.0721750 * s(b); }
export function APCAcontrast(txtY, bgY) {
  const blkThrs = 0.022, blkClmp = 1.414, loClip = 0.1, deltaYmin = 0.0005;
  const clamp = y => (y > blkThrs ? y : y + Math.pow(blkThrs - y, blkClmp));
  txtY = clamp(txtY); bgY = clamp(bgY);
  if (Math.abs(bgY - txtY) < deltaYmin) return 0;
  let out;
  if (bgY > txtY) { const s = (Math.pow(bgY, 0.56) - Math.pow(txtY, 0.57)) * 1.14; out = s < loClip ? 0 : s - 0.027; }
  else { const s = (Math.pow(bgY, 0.65) - Math.pow(txtY, 0.62)) * 1.14; out = s > -loClip ? 0 : s + 0.027; }
  return out * 100;
}
