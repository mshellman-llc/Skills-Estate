/* Decisions page: one card per question, grouped by epic. A closed card shows
   the question and its status only; owner and answer sit inside (R-DEC-1).
   The status tag is editable and saves to the shared store (R-DEC-2). */
(function () {
  'use strict';
  const {D, esc, ticket, story, statusTag, store, STATUS_CLASS} = RS;
  const app = document.getElementById('app');
  const groups = D.groups || [], questions = D.questions || [];
  const saved = {};

  let nav = '<nav class="ep-nav" aria-label="Groups"><span class="ctl">Epics</span><a href="#all" data-g="" aria-current="true"><span>All questions</span><span>' + questions.length + '</span></a>' +
    groups.map(g => '<a href="#' + esc(g.id) + '" data-g="' + esc(g.id) + '" aria-current="false"><span>' + esc(g.nav_label || g.label) + '</span><span>' +
      questions.filter(q => q.group === g.id).length + '</span></a>').join('') + '</nav>';
  let main = '<div class="controls"><button type="button" class="btn" id="expand">Expand all</button><button type="button" class="btn" id="collapse">Collapse all</button>' +
    '<label><input type="checkbox" id="hide-ans"> Hide answered</label><label><input type="checkbox" id="no-owner"> No owner only</label><span id="note" class="meta"></span></div>';
  groups.forEach(g => {
    const qs = questions.filter(q => q.group === g.id);
    if (!qs.length) return;
    const head = g.ticket && D.tickets[g.ticket] ? ticket(g.ticket, {label: g.label}) : esc(g.label);
    main += '<section class="grp" id="' + esc(g.id) + '" data-g="' + esc(g.id) + '"><h2>' + head + '</h2>' + qs.map(card).join('') + '</section>';
  });
  app.innerHTML = '<div class="dlayout">' + nav + '<div>' + main + '</div></div>';

  function card(q) {
    const rel = [];
    if ((q.stories || []).length) rel.push('<div><h4>Stories</h4><ul>' + q.stories.map(s => '<li>' + story(s) + '</li>').join('') + '</ul></div>');
    if ((q.tickets || []).length) rel.push('<div><h4>Tickets</h4><ul>' + q.tickets.map(k => '<li>' + ticket(k) + '</li>').join('') + '</ul></div>');
    return '<details class="card" id="' + esc(q.id) + '" data-owner="' + (q.owner ? '1' : '') + '"><summary><span class="q">' + esc(q.text) + '</span>' +
      '<span class="st-wrap"><button type="button" class="tag" aria-haspopup="menu" data-orig="' + esc(q.status) + '"></button></span></summary>' +
      '<div class="inner">' + (q.owner ? '<p class="owner">Owner: ' + esc(q.owner) + '</p>' : '') +
      (q.answer ? '<div class="answer-box"><b>' + esc(q.answer.label) + '</b>' + esc(q.answer.text) + '</div>' : '') +
      (q.context ? '<p>' + esc(q.context) + '</p>' : '') + (rel.length ? '<div class="rel">' + rel.join('') + '</div>' : '') +
      '<form class="form" data-id="' + esc(q.id) + '"><h4>Answer</h4><div class="row"><label>State <select name="state"><option value="">Not answered</option>' +
      '<option>Answered</option><option>Proposal accepted</option><option>Needs follow-up</option></select></label></div>' +
      '<label>Answer<textarea name="answer" rows="2"></textarea></label><label>Conditions and notes<textarea name="conditions" rows="2"></textarea></label>' +
      '<div class="row"><button type="submit" class="btn pri">Save</button><span class="meta saved" aria-live="polite"></span></div></form>' +
      '<div class="comments" data-id="' + esc(q.id) + '"><h4>Comments</h4><ul class="clist"></ul><form class="row cform">' +
      '<input type="text" aria-label="Add a comment" placeholder="Add a comment" style="flex:1 1 260px"><button class="btn" type="submit">Post</button></form></div></div></details>';
  }

  const cards = [...app.querySelectorAll('details.card')];
  function current(id) {
    const s = saved[id] || {};
    const pill = document.querySelector('#' + CSS.escape(id) + ' .tag');
    return s.status || (s.state === 'Answered' || s.state === 'Proposal accepted' ? 'Answered' : '') || pill.dataset.orig;
  }
  function paint(id) {
    const pill = document.querySelector('#' + CSS.escape(id) + ' .tag');
    if (!pill) return;
    const st = current(id);
    pill.className = 'tag ' + (STATUS_CLASS[st] || '');
    pill.dataset.st = st;
    pill.innerHTML = esc(st) + '<span class="caret" aria-hidden="true"></span>';
    pill.setAttribute('aria-label', 'Status: ' + st + '. Change status');
    const f = document.querySelector('form.form[data-id="' + CSS.escape(id) + '"]');
    const s = saved[id] || {};
    if (f && !f.contains(document.activeElement)) { f.state.value = s.state || ''; f.answer.value = s.answer || ''; f.conditions.value = s.conditions || ''; }
    applyFilters();
  }
  cards.forEach(c => paint(c.id));

  let menu = null;
  const closeMenu = () => { if (menu) { menu.remove(); menu = null; } };
  app.querySelectorAll('.st-wrap > .tag').forEach(pill => pill.addEventListener('click', e => {
    e.preventDefault(); e.stopPropagation();
    const wrap = pill.parentNode, id = pill.closest('details').id;
    const wasOpen = menu && menu.parentNode === wrap;
    closeMenu();
    if (wasOpen) return;
    menu = document.createElement('div');
    menu.className = 'st-menu';
    menu.setAttribute('role', 'menu');
    menu.innerHTML = D.statuses.map(s => '<button type="button" role="menuitemradio" aria-checked="' + (s === pill.dataset.st) + '" data-st="' + esc(s) + '">' + statusTag(s) + '</button>').join('') +
      (pill.dataset.st !== pill.dataset.orig ? '<button type="button" class="reset" data-st="">Reset to ' + esc(pill.dataset.orig) + '</button>' : '');
    menu.addEventListener('click', async ev => {
      ev.preventDefault(); ev.stopPropagation();
      const o = ev.target.closest('button[data-st]');
      if (!o) return;
      closeMenu();
      saved[id] = Object.assign({}, saved[id], {status: o.dataset.st});
      paint(id);
      try { await store.set(D.store.answers, id, saved[id]); } catch (err) { document.getElementById('note').textContent = 'Status not saved: ' + (err.code || err.message); }
      pill.focus();
    });
    wrap.appendChild(menu);
    (menu.querySelector('[aria-checked=true]') || menu.querySelector('button')).focus();
  }));
  document.addEventListener('click', e => { if (menu && !menu.contains(e.target)) closeMenu(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && menu) { const b = menu.parentNode.querySelector('.tag'); closeMenu(); b.focus(); } });

  app.querySelectorAll('form.form').forEach(f => f.addEventListener('submit', async e => {
    e.preventDefault();
    const id = f.dataset.id, out = f.querySelector('.saved');
    saved[id] = Object.assign({}, saved[id], {state: f.state.value, answer: f.answer.value.trim(), conditions: f.conditions.value.trim()});
    try {
      const where = await store.set(D.store.answers, id, saved[id]);
      out.textContent = where === 'shared' ? 'Saved for everyone' : 'Saved in this browser only';
    } catch (err) { out.textContent = 'Not saved: ' + (err.code || err.message); }
    paint(id);
  }));
  app.querySelectorAll('.cform').forEach(f => f.addEventListener('submit', async e => {
    e.preventDefault();
    const id = f.closest('.comments').dataset.id, input = f.querySelector('input'), text = input.value.trim();
    if (!text) return;
    try { await store.add(D.store.comments + '/' + id + '/items', {text}); input.value = ''; }
    catch (err) { input.setCustomValidity('Not posted: ' + err.message); input.reportValidity(); setTimeout(() => input.setCustomValidity(''), 2500); }
  }));

  const links = [...app.querySelectorAll('.ep-nav a')];
  function showGroup(g) {
    links.forEach(a => a.setAttribute('aria-current', String(a.dataset.g === g)));
    app.querySelectorAll('.grp').forEach(s => { s.dataset.navHidden = g && s.dataset.g !== g ? '1' : ''; });
    applyFilters();
  }
  links.forEach(a => a.addEventListener('click', e => { e.preventDefault(); showGroup(a.dataset.g); history.replaceState(null, '', a.dataset.g ? '#' + a.dataset.g : location.pathname); }));
  function applyFilters() {
    const hide = document.getElementById('hide-ans').checked, noOwner = document.getElementById('no-owner').checked;
    cards.forEach(c => { c.hidden = (hide && current(c.id) === 'Answered') || (noOwner && c.dataset.owner === '1'); });
    app.querySelectorAll('.grp').forEach(s => { s.hidden = s.dataset.navHidden === '1' || [...s.querySelectorAll('details.card')].every(c => c.hidden); });
  }
  document.getElementById('hide-ans').addEventListener('change', applyFilters);
  document.getElementById('no-owner').addEventListener('change', applyFilters);
  document.getElementById('expand').addEventListener('click', () => cards.forEach(c => { if (!c.hidden) c.open = true; }));
  document.getElementById('collapse').addEventListener('click', () => cards.forEach(c => { c.open = false; }));

  const hash = decodeURIComponent(location.hash.slice(1));
  if (hash && groups.some(g => g.id === hash)) showGroup(hash); else RS.openFromHash();

  store.watch(D.store.answers, (id, v) => { saved[id] = v; paint(id); });
  store.init().then(() => {
    if (!store.db) {
      app.querySelectorAll('.comments').forEach(c => { c.hidden = true; });
      if (window.claude) document.getElementById('note').textContent = 'Answers save in this browser only.';
      return;
    }
    cards.forEach(c => store.list(D.store.comments + '/' + c.id + '/items', async docs => {
      const ul = c.querySelector('.clist');
      const people = await store.names([...new Set(docs.map(d => d.by).filter(Boolean))]);
      ul.innerHTML = docs.map(d => '<li><b>' + esc((people[d.by] && people[d.by].name) || 'Someone') + '</b> <span class="meta">' + esc((d.at || '').slice(0, 10)) + '</span><br>' + esc(d.text) + '</li>').join('');
    }));
  });
})();
