/* Scope page: MoSCoW story map, story panel with class review, critical path,
   and the secondary sections, which start closed (R-FOLD-1). */
(function () {
  'use strict';
  const {D, esc, ticket, cls, marker, questionLink, fold, store} = RS;
  const app = document.getElementById('app');
  const classes = ['must', 'should', 'could', 'wont'];
  const stories = D.stories || [];
  const CHECK_LABEL = {acceptance: 'Acceptance criteria', estimate: 'Estimate', no_open_questions: 'No open questions',
    no_blocked_dependency: 'No blocked or unticketed dependency', ticketed: 'In the tracker'};
  const STATUS_LEGEND = [['done', 'Done'], ['wip', 'In progress or in review'], ['todo', 'Not started'],
    ['untracked', 'Not in the tracker yet'], ['blocked', 'Blocked']];
  const reviews = {};

  const epics = [...new Set(stories.map(s => s.computed.epic).filter(Boolean))];
  const sprints = [...new Set(stories.map(s => s.computed.sprint).filter(Boolean))];
  const epicName = k => (D.tickets[k] && D.tickets[k].summary) || k;

  let html = '<section id="map-section"><h2>MoSCoW story map</h2>';
  html += '<ul class="legend" aria-label="Build status">' + STATUS_LEGEND.map(([c, l]) => '<li>' + marker(c) + ' ' + esc(l) + '</li>').join('') +
    '<li><span class="qm" aria-hidden="true">?</span> Has open questions</li></ul>';
  html += '<div class="controls" role="group" aria-label="Map filters">';
  if ((D.roles || []).length) {
    html += '<div><span class="ctl" id="lbl-role">Role</span><span class="seg" role="group" aria-labelledby="lbl-role">' +
      '<button type="button" data-role="" aria-pressed="true">All</button>' +
      D.roles.map(r => '<button type="button" data-role="' + esc(r.id) + '" aria-pressed="false">' + esc(r.label) + '</button>').join('') + '</span></div>';
  }
  const count = fn => stories.filter(fn).length;
  html += '<label><span class="ctl">Epic</span><select id="f-epic"><option value="">All epics</option>' +
    epics.map(e => '<option value="' + esc(e) + '">' + esc(epicName(e)) + ' (' + count(s => s.computed.epic === e) + ')</option>').join('') + '</select></label>';
  html += '<label><span class="ctl">Sprint</span><select id="f-sprint"><option value="">All sprints</option>' +
    sprints.map(p => '<option value="' + esc(p) + '">' + esc(p) + ' (' + count(s => s.computed.sprint === p) + ')</option>').join('') +
    '<option value="none">No sprint yet (' + count(s => !s.computed.sprint) + ')</option></select></label>';
  html += '<label><span class="ctl">Readiness</span><select id="f-ready" title="Ready to build: ' +
    esc((D.readiness_rules || []).map(r => CHECK_LABEL[r]).join(', ')) + '"><option value="">All stories</option>' +
    '<option value="not">Not ready to build (' + count(s => !s.computed.ready) + ')</option>' +
    '<option value="ready">Ready or done (' + count(s => s.computed.ready) + ')</option></select></label></div>';

  html += '<div class="map" role="region" aria-label="Stories by workflow step and class"><div class="hd"></div>' +
    classes.map(c => '<div class="hd"><b>' + esc(D.classes[c].label) + '</b>' + (D.classes[c].definition ? '<span>' + esc(D.classes[c].definition) + '</span>' : '') + '</div>').join('');
  (D.steps || []).forEach((step, i) => {
    html += '<div class="step"><span class="num">' + (i + 1) + '</span><h3>' + esc(step.label) + '</h3></div>';
    classes.forEach(c => {
      const here = stories.filter(s => s.step === step.id && s.class === c);
      html += '<div class="cell ' + c + '" data-label="' + esc(D.classes[c].label) + '">' + here.map(s =>
        '<button type="button" class="chip" id="chip-' + esc(s.id) + '" data-id="' + esc(s.id) + '" aria-pressed="false">' +
        marker(s.computed.status.category) + '<span>' + esc(s.label) +
        (s.computed.open_questions.length ? '<span class="qm" title="Open questions">?</span>' : '') + '</span></button>').join('') + '</div>';
    });
  });
  html += '</div><div id="panel" class="panel" hidden tabindex="-1"></div></section>';

  if (D.critical_path && D.critical_path.nodes.length + D.critical_path.untracked.length) {
    html += '<section id="critical-path"><h2>Critical path</h2><ul class="key"><li><i></i>Blocks</li>' +
      '<li><i class="back"></i>Blocks a story in an earlier sprint</li><li><i class="box"></i>Outside the story map</li>' +
      '<li><i class="off"></i>Canceled blocker</li></ul><div class="cp-wrap">' + D.critical_path.svg + '</div></section>';
  }
  let folds = '';
  if ((D.next_actions || []).length) {
    folds += fold('next', 'Next actions', '<ul class="next">' + D.next_actions.map(a => '<li><span>' + esc(a.text) + '</span>' +
      (a.story ? '<button type="button" class="btn" data-open="' + esc(a.story) + '">Open story</button>' :
        a.href ? '<a class="btn" href="' + esc(a.href) + '">Open</a>' : '') + '</li>').join('') + '</ul>');
  }
  if ((D.unclassed || []).length) {
    folds += fold('unclassed', 'Not yet classed', '<div class="tbl"><table><thead><tr><th scope="col">Ticket</th><th scope="col">Epic</th><th scope="col">Status</th></tr></thead><tbody>' +
      D.unclassed.map(u => '<tr><th scope="row">' + ticket(u.key, {nostatus: true}) + '</th><td>' + esc(epicName(u.epic)) + '</td><td>' + esc(u.status) + '</td></tr>').join('') + '</tbody></table></div>');
  }
  if ((D.sources || []).length) {
    folds += fold('sources', 'Sources', '<ul>' + D.sources.map(s => '<li><b>' + esc(s.title) + '</b> ' + esc(s.text) + '</li>').join('') + '</ul>');
  }
  if (folds) html += '<section id="more">' + folds + '</section>';
  app.innerHTML = html;

  const panel = document.getElementById('panel');
  function render(s) {
    const c = s.computed;
    const r = reviews[s.id];
    const epic = c.epic ? (D.tickets[c.epic] ? ticket(c.epic) : esc(c.epic)) : 'None';
    let h = '<h3>' + esc(s.label) + '</h3><p>' + cls(s.class) + ' <span class="jst">' + esc(c.status.label) + '</span></p><dl>' +
      '<dt>Epic</dt><dd>' + epic + '</dd>' +
      '<dt>Tickets</dt><dd>' + ((s.tickets || []).length ? '<ul class="tix">' + s.tickets.map(k => '<li>' + ticket(k) + '</li>').join('') + '</ul>' : 'None yet') + '</dd>' +
      '<dt>Sprint</dt><dd>' + esc(c.sprint || 'No sprint yet') + (c.points != null ? ' · ' + c.points + ' points' : ' · no estimate') + '</dd>' +
      (s.what ? '<dt>What it does</dt><dd>' + esc(s.what) + '</dd>' : '') +
      (s.interim ? '<dt>Until it\'s built</dt><dd>' + esc(s.interim) + '</dd>' : '') + '</dl>';
    h += '<h4>Acceptance criteria</h4>' + (c.acceptance.length ? '<ul>' + c.acceptance.map(a => '<li>' + esc(a.trim()) + '</li>').join('') + '</ul>' : '<p>None in the tracker yet.</p>');
    h += '<h4>Ready to build</h4><ul>' + Object.entries(c.checks).map(([k, ok]) => '<li>' + (ok ? 'Yes: ' : 'No: ') + esc(CHECK_LABEL[k]) + '</li>').join('') + '</ul>';
    if (c.questions.length) h += '<h4>Questions</h4><ul>' + c.questions.map(q => '<li>' + questionLink(q) + '</li>').join('') + '</ul>';
    h += '<h4>Class decision</h4><div class="review" role="group" aria-label="Class decision">' +
      '<button type="button" class="btn" data-class="' + esc(s.class) + '">Agree</button>' +
      classes.filter(k => k !== s.class).map(k => '<button type="button" class="btn" data-class="' + k + '">' + esc(D.classes[k].label) + '</button>').join('') +
      '<input type="text" id="rv-note" placeholder="Note" aria-label="Note" style="flex:1 1 200px"></div>' +
      '<p class="meta" id="rv-saved">' + (r ? 'Decided: ' + esc(D.classes[r.class] ? D.classes[r.class].label : r.class) + (r.note ? ' · ' + esc(r.note) : '') + (r.at ? ' · ' + esc(r.at.slice(0, 10)) : '') : '') + '</p>';
    panel.innerHTML = h;
    panel.querySelectorAll('[data-class]').forEach(b => b.addEventListener('click', async () => {
      const note = panel.querySelector('#rv-note').value.trim();
      try {
        const where = await store.set(D.store.reviews, s.id, {class: b.dataset.class, note});
        reviews[s.id] = {class: b.dataset.class, note, at: new Date().toISOString()};
        render(s);
        if (where === 'local') panel.querySelector('#rv-saved').textContent += ' · saved in this browser only';
      } catch (e) { panel.querySelector('#rv-saved').textContent = 'Not saved: ' + (e.code || e.message); }
    }));
  }
  function open(id, scroll) {
    const s = RS.storyById(id);
    if (!s) return;
    document.querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', String(c.dataset.id === id)));
    panel.hidden = false;
    render(s);
    if (scroll) panel.scrollIntoView({block: 'nearest'});
    history.replaceState(null, '', '#' + encodeURIComponent(id));
  }
  app.querySelectorAll('.chip').forEach(c => c.addEventListener('click', () => {
    if (c.getAttribute('aria-pressed') === 'true') { c.setAttribute('aria-pressed', 'false'); panel.hidden = true; return; }
    open(c.dataset.id, true);
  }));
  app.querySelectorAll('[data-open]').forEach(b => b.addEventListener('click', () => {
    const chip = document.getElementById('chip-' + b.dataset.open);
    if (chip) chip.scrollIntoView({block: 'center'});
    open(b.dataset.open, false);
  }));

  let role = '';
  function filter() {
    const epic = document.getElementById('f-epic').value, sprint = document.getElementById('f-sprint').value,
      ready = document.getElementById('f-ready').value;
    stories.forEach(s => {
      const c = s.computed;
      const show = (!role || (s.roles || []).includes(role)) && (!epic || c.epic === epic) &&
        (!sprint || (sprint === 'none' ? !c.sprint : c.sprint === sprint)) &&
        (!ready || (ready === 'ready') === c.ready);
      document.getElementById('chip-' + s.id).hidden = !show;
    });
  }
  app.querySelectorAll('[data-role]').forEach(b => b.addEventListener('click', () => {
    role = b.dataset.role;
    app.querySelectorAll('[data-role]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    filter();
  }));
  ['f-epic', 'f-sprint', 'f-ready'].forEach(id => document.getElementById(id).addEventListener('change', filter));
  document.querySelectorAll('a[href^="#"]').forEach(a => a.addEventListener('click', () => setTimeout(RS.openFromHash, 0)));

  store.watch(D.store.reviews, (id, v) => {
    reviews[id] = v;
    const s = RS.storyById(id);
    if (s && !panel.hidden && document.getElementById('chip-' + id).getAttribute('aria-pressed') === 'true') render(s);
  });
  const hash = decodeURIComponent(location.hash.slice(1));
  if (hash && RS.storyById(hash)) open(hash, true); else RS.openFromHash();
})();
