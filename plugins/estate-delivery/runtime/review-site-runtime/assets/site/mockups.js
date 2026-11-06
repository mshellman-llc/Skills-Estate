/* Mockups page: each supplied mockup file in a framed view, one at a time. */
(function () {
  'use strict';
  const {D, esc} = RS;
  const app = document.getElementById('app');
  const items = D.mockups || [];
  if (!items.length) { app.innerHTML = '<p>No mockups were supplied.</p>'; return; }
  app.innerHTML = (items.length > 1 ? '<div class="tabs" role="group" aria-label="Mockup">' + items.map((m, i) =>
    '<button type="button" aria-pressed="' + (i === 0) + '" data-i="' + i + '">' + esc(m.title) + '</button>').join('') + '</div>' : '') +
    '<iframe class="mock" title="' + esc(items[0].title) + '" src="' + esc(items[0].file) + '" sandbox="allow-scripts"></iframe>';
  const frame = app.querySelector('iframe');
  app.querySelectorAll('[data-i]').forEach(t => t.addEventListener('click', () => {
    app.querySelectorAll('[data-i]').forEach(x => x.setAttribute('aria-pressed', String(x === t)));
    const m = items[+t.dataset.i];
    frame.src = m.file;
    frame.title = m.title;
  }));
})();
