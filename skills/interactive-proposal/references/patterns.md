# Interaction patterns

One self-contained HTML file. Inline CSS, inline JS, inline SVG icons. No CDN of any kind: the
delivery path is an email attachment and a CDN dependency breaks the page in the room where it
matters. Brand tokens and declared assets come from the selected shared profile at build time. Do not restate
hex codes here from memory.

## Page skeleton

```
masthead        optional profile logo, client, opportunity, prepared by, date, status
hero            version tabs + the version panel (the star), using profile surface colors
<main>
  scope         per-version scope tracks, re-rendered on switch
  architecture  system-of-record split and interfaces, where relevant
  decisions     open questions with named owners, where relevant
  phase band    the paid next step, using profile surface colors
  disclosures   assumptions, boundaries with routes, sources and audit table
  next steps    named steps
</main>
footer          confidentiality line
```

The `<main>` landmark is load-bearing. The parity gate's default `requiredSelectors` is
`["main","h1"]`, so a page without it fails as a structural error.

## Assets

The builder calls the packaged `brand-renderer` HTML runtime. It resolves the selected profile, embeds declared local assets, and removes the logo slot when the profile has no logo. Keep project assets outside the reusable skill. Missing declared assets are build errors.

## Version-switcher hero

The packaged builder switches instantly and supports arrow keys, Home and End. The optional animation pattern below is for custom layouts; verify the final displayed value and reduced-motion behavior before using it.

Tabs select a version. The panel re-skins with a short blur-out and blur-in so the switch reads as
the page re-rendering. It is all text, so switches are instant.

```css
.vpanel{transition:opacity .3s ease, filter .3s ease}
.vpanel.swap{opacity:.45;filter:blur(9px)}
```

```js
function select(k){
  if (k === current) return;
  var prev = current, p = document.getElementById('vpanel');
  var from = prev === null ? V[k].metric : V[prev].metric;
  current = k;
  p.classList.add('swap');
  setTimeout(function(){ render(k); p.classList.remove('swap'); }, prev === null ? 0 : 170);
  tween(from, V[k].metric);
}
```

Swap the text mid-blur, not before it. Rendering before the blur shows the reader the change
happening twice.

## Tweened numbers

The tween animates between two fixed source values and lands exactly on the target. No other
arithmetic lives on the page.

```js
function tween(from, to){
  var el = document.getElementById('vnum'), start = null, dur = 420;
  if (from === to) { el.textContent = to; return; }
  function step(ts){
    if (start === null) start = ts;
    var t = Math.min((ts - start) / dur, 1);
    var e = 1 - Math.pow(1 - t, 3);              // ease out cubic
    el.textContent = Math.round(from + (to - from) * e);
    if (t < 1) requestAnimationFrame(step); else el.textContent = to;   // land exact
  }
  requestAnimationFrame(step);
}
```

Set `font-variant-numeric: tabular-nums` on the figure so the tween does not jitter.

## Scope sections, and showing what is excluded

Render each version's scope tracks as cards. Keep item names verbatim from the source; tighten
descriptions, never extend them with new claims.

Excluded scope stays on the page and goes dashed. Hiding it makes a lean version look like a
rendering fault and invites the question you did not want. Showing it labels the tradeoff as
deliberate, which is the argument the page is making.

```css
.item.out{background:transparent;border-style:dashed}
```

```js
document.querySelectorAll('.item').forEach(function(el){
  var inV = el.dataset.keys.indexOf(k) > -1;
  el.classList.toggle('out', !inV);
  el.querySelector('.pill').textContent = inV ? 'In this version' : 'Not in this version';
});
```

Every card carries a visible source line. On a page with no price on it, provenance is the thing
doing the persuading.

## Disclosures

```html
<details class="disclose">
  <summary>Assumptions and what is not included</summary>
  <div class="inner">
    <!-- basis-of-estimate list, then not-included items each with its route -->
  </div>
</details>
```

Present but demoted. Three disclosures earn their place: assumptions, boundaries with routes, and
sources with the audit table. Load-bearing assumptions protect the price; the routes turn every
boundary into a next conversation.

## Visual defaults

- Shared profile tokens; every colour on the surface is a palette
  token. Never more than 3 type weights on one surface.
  Sentence case headings. Body copy left-aligned, only titles centered.
- Icons: small inline SVGs drawn in the file, 1.75px stroke, teal on light surfaces.
- Bullet marker: `·` middle dot, not a disc.
- No decorative rule under titles, no bouncy easing, no scale transforms on hover. All three are
  brand-forbidden and all three are common AI tells.
- Generous whitespace. Do not fill the page.

## Print

```css
@media print{
  .tabs{display:none}
  .item.out{display:none}
  details:not([open]) .inner{display:block}
  .mast,.hero,footer{background:var(--brand-surface) !important;print-color-adjust:exact}
}
```

The selected version prints as a clean document. Excluded scope drops out, disclosures print open,
profile colors are preserved.

## Responsive

Collapse the version panel grid, scope grid, and step grid to one column below 900px. The two
things that break first are the version tabs and the metric figure. Check both at 390px.
