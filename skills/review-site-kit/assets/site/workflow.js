/* Workflow page: steps by role with optional layers, and the today-versus-after
   table. The table uses one text size and keeps tickets behind a closed line (R-TYPE-1). */
(function () {
  'use strict';
  const {D, esc, ticket} = RS;
  const app = document.getElementById('app');
  const roles = D.journeys || [];
  const LAYERS = [['today', 'Today'], ['behind', 'Behind the scenes'], ['handoff', 'Handoff'], ['open', 'Still open']];
  let html = '';
  if (roles.length) {
    html += '<section id="journeys"><h2>Steps by role</h2><div class="tabs" role="tablist" aria-label="Role">' +
      roles.map((r, i) => '<button type="button" role="tab" id="tab-' + esc(r.id) + '" aria-controls="panel-' + esc(r.id) + '" aria-selected="' + (i === 0) + '">' + esc(r.label) + '</button>').join('') + '</div>';
    const used = LAYERS.filter(([k]) => roles.some(r => r.steps.some(s => s[k])));
    if (used.length) html += '<div class="controls"><span class="ctl">Also show</span>' + used.map(([k, l]) => '<label><input type="checkbox" data-layer-toggle="' + k + '"> ' + l + '</label>').join('') + '</div>';
    roles.forEach((r, i) => {
      const cols = 'grid-template-columns:120px repeat(' + r.steps.length + ',minmax(150px,1fr))';
      let grid = '<div class="bh"></div>' + r.steps.map((s, n) => '<div class="bh"><span class="num">' + (n + 1) + '</span>' + esc(s.label) + '</div>').join('');
      grid += '<div class="bl">The question</div>' + r.steps.map(s => '<div class="q-row">' + esc(s.question) + '</div>').join('');
      used.forEach(([k, l]) => {
        grid += '<div class="bl" data-layer="' + k + '" hidden>' + l + '</div>' + r.steps.map(s => '<div data-layer="' + k + '" hidden>' + esc(s[k] || '') + '</div>').join('');
      });
      html += '<div role="tabpanel" id="panel-' + esc(r.id) + '" aria-labelledby="tab-' + esc(r.id) + '"' + (i ? ' hidden' : '') + '>' +
        (r.lead ? '<p>' + esc(r.lead) + '</p>' : '') + '<div class="bp-scroll" tabindex="0"><div class="bp" style="' + cols + '">' + grid + '</div></div></div>';
    });
    html += '</section>';
  }
  if ((D.changes || []).length) {
    html += '<section id="changes"><h2>Today and after the release</h2><div class="tbl"><table><thead><tr><th scope="col">Area</th><th scope="col">Today</th><th scope="col">After the release</th></tr></thead><tbody>' +
      D.changes.map(c => '<tr><th scope="row">' + esc(c.area) + '</th><td class="dim">' + esc(c.today) + '</td><td>' + esc(c.after) +
        ((c.tickets || []).length ? '<details><summary class="meta">Tickets (' + c.tickets.length + ')</summary><ul class="tix">' + c.tickets.map(k => '<li>' + ticket(k) + '</li>').join('') + '</ul></details>' : '') +
        '</td></tr>').join('') + '</tbody></table></div></section>';
  }
  app.innerHTML = html;
  const tabs = [...app.querySelectorAll('[role=tab]')];
  tabs.forEach(t => t.addEventListener('click', () => {
    tabs.forEach(x => { x.setAttribute('aria-selected', String(x === t)); document.getElementById(x.getAttribute('aria-controls')).hidden = x !== t; });
  }));
  app.querySelectorAll('[data-layer-toggle]').forEach(box => box.addEventListener('change', () => {
    app.querySelectorAll('[data-layer="' + box.dataset.layerToggle + '"]').forEach(el => { el.hidden = !box.checked; });
  }));
})();
