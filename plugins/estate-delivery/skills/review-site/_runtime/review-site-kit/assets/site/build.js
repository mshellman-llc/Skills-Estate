/* Build page: each process as tinted step tiles that get darker step by step
   (R-TINT-1). Clicking a step opens its tickets, open questions and acceptance
   criteria; the technical design sections start closed (R-FOLD-1). */
(function () {
  'use strict';
  const {D, esc, ticket, fold, questionLink} = RS;
  const app = document.getElementById('app');
  const lanes = D.lanes || [];
  const storyOf = {};
  (D.stories || []).forEach(s => (s.tickets || []).forEach(k => { if (!storyOf[k]) storyOf[k] = s; }));
  let html = '';
  if (lanes.length) {
    html += '<section id="how"><h2>How each process works</h2><div class="seg" role="group" aria-label="Process">' +
      lanes.map((l, i) => '<button type="button" data-lane="' + esc(l.id) + '" aria-pressed="' + (i === 0) + '">' + esc(l.label) + '</button>').join('') + '</div>';
    lanes.forEach((l, i) => {
      const n = l.steps.length;
      html += '<div class="lane" data-lane="' + esc(l.id) + '"' + (i ? ' hidden' : '') + '>' + (l.lead ? '<p class="meta" style="margin-top:12px">' + esc(l.lead) + '</p>' : '') +
        '<ol class="flow" style="margin-top:12px">' + l.steps.map((s, k) => '<li><button type="button" class="tile" aria-expanded="false" data-step="' + esc(s.id) + '" style="--t:' +
          (5 + (n > 1 ? k * 13 / (n - 1) : 0)).toFixed(1) + '%"><span class="num">' + (k + 1) + '</span>' + esc(s.label) + '</button></li>').join('') +
        '</ol><div class="step-detail" hidden></div></div>';
    });
    html += '</section>';
  }
  if ((D.design || []).length) {
    html += '<section id="design"><h2>Technical design</h2>' + D.design.map((d, i) => fold('design-' + i, d.title,
      '<div class="tbl"><table><tbody>' + d.rows.map(r => '<tr><th scope="row">' + esc(r.label) + '</th><td>' + esc(r.text) + '</td></tr>').join('') + '</tbody></table></div>')).join('') + '</section>';
  }
  app.innerHTML = html;

  function detail(step) {
    const keys = step.tickets || [];
    const qs = (D.questions || []).filter(q => (q.tickets || []).some(k => keys.includes(k)) || (q.stories || []).some(id => keys.some(k => storyOf[k] && storyOf[k].id === id)));
    let h = '<h3>' + esc(step.label) + '</h3><p>' + esc(step.text) + '</p>';
    if (keys.length) {
      h += '<h4>Tickets for this step</h4><div class="tbl"><table><thead><tr><th scope="col">Ticket</th><th scope="col">Class</th><th scope="col">Status</th><th scope="col">Sprint</th><th scope="col">Questions</th></tr></thead><tbody>' +
        keys.map(k => {
          const t = D.tickets[k] || {}, s = storyOf[k];
          const open = s ? s.computed.open_questions.length : 0;
          return '<tr><th scope="row">' + ticket(k, {nostatus: true}) + '</th><td>' + (s ? esc(D.classes[s.class].label) : '') + '</td><td>' + esc(t.status || '') + '</td><td>' +
            esc(t.sprint || 'No sprint') + (t.points != null ? ' · ' + t.points + ' points' : '') + '</td><td>' + (open ? open + ' open' : '') + '</td></tr>';
        }).join('') + '</tbody></table></div>';
    }
    if (qs.length) h += '<h4>Questions</h4><ul>' + qs.map(q => '<li>' + questionLink(q.id) + ' <span class="jst">' + esc(q.status) + '</span></li>').join('') + '</ul>';
    const withAc = keys.filter(k => (D.tickets[k] || {}).acceptance && D.tickets[k].acceptance.length);
    if (withAc.length) h += '<h4>Acceptance criteria</h4>' + withAc.map(k => '<details><summary>' + esc(D.tickets[k].summary) + '</summary><ul>' +
      D.tickets[k].acceptance.map(a => '<li>' + esc(a.trim()) + '</li>').join('') + '</ul></details>').join('');
    return h;
  }
  app.querySelectorAll('.tile').forEach(b => b.addEventListener('click', () => {
    const lane = b.closest('.lane'), box = lane.querySelector('.step-detail');
    const wasOpen = b.getAttribute('aria-expanded') === 'true';
    lane.querySelectorAll('.tile').forEach(x => x.setAttribute('aria-expanded', 'false'));
    if (wasOpen) { box.hidden = true; return; }
    b.setAttribute('aria-expanded', 'true');
    const l = lanes.find(x => x.id === lane.dataset.lane);
    box.innerHTML = detail(l.steps.find(s => s.id === b.dataset.step));
    box.hidden = false;
  }));
  app.querySelectorAll('[data-lane]').forEach(b => {
    if (b.tagName !== 'BUTTON') return;
    b.addEventListener('click', () => {
      app.querySelectorAll('button[data-lane]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      app.querySelectorAll('.lane').forEach(l => { l.hidden = l.dataset.lane !== b.dataset.lane; });
    });
  });
})();
