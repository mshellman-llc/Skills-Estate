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
    return '<div class="card-wrap" data-q="' + esc(q.id) + '"><span class="st-wrap"><button type="button" class="tag" aria-haspopup="menu" aria-expanded="false" data-orig="' + esc(q.status) + '"></button></span>' +
      '<details class="card" id="' + esc(q.id) + '" data-owner="' + (q.owner ? '1' : '') + '"><summary><span class="q">' + esc(q.text) + '</span></summary>' +
      '<div class="inner">' + (q.owner ? '<p class="owner">Owner: ' + esc(q.owner) + '</p>' : '') +
      (q.answer ? '<div class="answer-box"><b>' + esc(q.answer.label) + '</b>' + esc(q.answer.text) + '</div>' : '') +
      (q.context ? '<p>' + esc(q.context) + '</p>' : '') + (rel.length ? '<div class="rel">' + rel.join('') + '</div>' : '') +
      '<form class="form" data-id="' + esc(q.id) + '"><h4>Answer</h4><div class="row"><label>State <select name="state"><option value="">Not answered</option>' +
      '<option>Answered</option><option>Proposal accepted</option><option>Needs follow-up</option></select></label></div>' +
      '<label>Answer<textarea name="answer" rows="2"></textarea></label><label>Conditions and notes<textarea name="conditions" rows="2"></textarea></label>' +
      '<div class="row"><button type="submit" class="btn pri">Save</button><span class="meta saved" aria-live="polite"></span></div></form>' +
      '<div class="comments" data-id="' + esc(q.id) + '"><h4>Comments</h4><ul class="clist"></ul><form class="row cform">' +
      '<input type="text" aria-label="Add a comment" placeholder="Add a comment" style="flex:1 1 260px"><button class="btn" type="submit">Post</button></form></div></div></details></div>';
  }

  const cards = [...app.querySelectorAll('details.card')];
  const pillOf = id => document.querySelector('.card-wrap[data-q="' + CSS.escape(id) + '"] > .st-wrap > .tag');
  function current(id) {
    const s = saved[id] || {};
    return s.status || pillOf(id).dataset.orig;
  }
  function paint(id) {
    const pill = pillOf(id);
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
  function closeMenu(focusPill) {
    if (!menu) return;
    const open = menu;
    menu = null;  // cleared first: removing the menu moves focus and fires focusout
    const pill = open.parentNode.querySelector('.tag');
    open.remove();
    pill.parentNode.classList.remove('open');
    pill.setAttribute('aria-expanded', 'false');
    if (focusPill) pill.focus();
  }
  async function choose(id, status) {
    saved[id] = Object.assign({}, saved[id], {status});
    paint(id);
    try { await store.set(D.store.answers, id, saved[id]); } catch (err) { document.getElementById('note').textContent = 'Status not saved: ' + (err.code || err.message); }
  }
  function openMenu(pill) {
    const wrap = pill.parentNode, id = pill.closest('.card-wrap').dataset.q;
    menu = document.createElement('div');
    menu.className = 'st-menu';
    menu.setAttribute('role', 'menu');
    menu.setAttribute('aria-label', 'Status');
    menu.innerHTML = D.statuses.map(s => '<button type="button" role="menuitemradio" tabindex="-1" aria-checked="' + (s === pill.dataset.st) + '" data-st="' + esc(s) + '">' + statusTag(s) + '</button>').join('') +
      (pill.dataset.st !== pill.dataset.orig ? '<button type="button" role="menuitem" tabindex="-1" class="reset" data-st="' + esc(pill.dataset.orig) + '">Reset to ' + esc(pill.dataset.orig) + '</button>' : '');
    const items = [...menu.querySelectorAll('button')];
    menu.addEventListener('click', ev => {
      const o = ev.target.closest('button[data-st]');
      if (!o) return;
      closeMenu(true);
      choose(id, o.dataset.st);
    });
    menu.addEventListener('keydown', ev => {
      const i = items.indexOf(document.activeElement);
      if (ev.key === 'ArrowDown' || ev.key === 'ArrowUp') {
        ev.preventDefault();
        items[(i + (ev.key === 'ArrowDown' ? 1 : items.length - 1)) % items.length].focus();
      } else if (ev.key === 'Home' || ev.key === 'End') {
        ev.preventDefault();
        items[ev.key === 'Home' ? 0 : items.length - 1].focus();
      } else if (ev.key === 'Escape') {
        ev.preventDefault();
        closeMenu(true);
      } else if (ev.key === 'Tab') {
        closeMenu(false);
      }
    });
    menu.addEventListener('focusout', ev => { if (menu && !menu.contains(ev.relatedTarget) && ev.relatedTarget !== pill) closeMenu(false); });
    wrap.appendChild(menu);
    wrap.classList.add('open');
    pill.setAttribute('aria-expanded', 'true');
    (menu.querySelector('[aria-checked=true]') || items[0]).focus();
  }
  app.querySelectorAll('.st-wrap > .tag').forEach(pill => {
    pill.addEventListener('click', () => {
      const wasOpen = menu && menu.parentNode === pill.parentNode;
      closeMenu(false);
      if (!wasOpen) openMenu(pill);
    });
    pill.addEventListener('keydown', ev => {
      if (ev.key === 'ArrowDown' && !menu) { ev.preventDefault(); openMenu(pill); }
    });
  });
  document.addEventListener('click', e => { if (menu && !menu.parentNode.contains(e.target)) closeMenu(false); });

  app.querySelectorAll('form.form').forEach(f => f.addEventListener('submit', async e => {
    e.preventDefault();
    const id = f.dataset.id, out = f.querySelector('.saved');
    const state = f.state.value;
    const status = state === 'Answered' || state === 'Proposal accepted' ? 'Answered' : state === 'Needs follow-up' ? 'Open' : (saved[id] || {}).status;
    saved[id] = Object.assign({}, saved[id], {state, status, answer: f.answer.value.trim(), conditions: f.conditions.value.trim()});
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
    try { await store.add(D.store.comments, {question: id, text}); input.value = ''; }
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
    cards.forEach(c => { c.parentNode.hidden = (hide && current(c.id) === 'Answered') || (noOwner && c.dataset.owner === '1'); });
    app.querySelectorAll('.grp').forEach(s => { s.hidden = s.dataset.navHidden === '1' || [...s.querySelectorAll('.card-wrap')].every(c => c.hidden); });
  }
  document.getElementById('hide-ans').addEventListener('change', applyFilters);
  document.getElementById('no-owner').addEventListener('change', applyFilters);
  document.getElementById('expand').addEventListener('click', () => cards.forEach(c => { if (!c.parentNode.hidden) c.open = true; }));
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
    // One subscription for every question: the store limits how many a page may hold open.
    store.list(D.store.comments, async docs => {
      const people = await store.names([...new Set(docs.map(d => d.by).filter(Boolean))]);
      cards.forEach(c => {
        const mine = docs.filter(d => d.question === c.id);
        c.querySelector('.clist').innerHTML = mine.map(d => '<li><b>' + esc((people[d.by] && people[d.by].name) || 'Someone') + '</b> <span class="meta">' + esc((d.at || '').slice(0, 10)) + '</span><br>' + esc(d.text) + '</li>').join('');
      });
    });
  });
})();
