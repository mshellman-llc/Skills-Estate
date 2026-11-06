/* Shared helpers for every build-review-site page: escaping, ticket links, tags and
   the shared store. The store uses the artifact runtime's db when the page is
   published with the db capability, and this browser's storage otherwise. */
(function () {
  'use strict';
  const D = window.RS_DATA || {};
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  const T = D.tickets || {};
  const CLASS = D.classes || {};
  const STATUS_CLASS = {'Open': 't-open', 'Proposed': 't-prop', 'Sandbox check': 't-prop', 'Partly answered': 't-done',
    'Answered': 't-done', 'Deferred': '', 'Blocked': 't-block'};

  function ticket(key, opts) {
    const t = T[key];
    if (!t) return '<span>' + esc(key) + '</span>';
    const label = (opts && opts.label) || t.summary;
    const link = t.url ? '<a href="' + esc(t.url) + '" target="_blank" rel="noopener" data-ticket="' + esc(key) + '">' + esc(label) + '</a>'
      : '<span data-ticket="' + esc(key) + '">' + esc(label) + '</span>';
    if (opts && opts.nostatus) return link;
    return link + ' <span class="jst" data-status-of="' + esc(key) + '">' + esc(t.status) + '</span>';
  }
  function cls(c) { return '<span class="cls c-' + esc(c) + '">' + esc((CLASS[c] || {}).label || c) + '</span>'; }
  function statusTag(s) { return '<span class="tag ' + (STATUS_CLASS[s] || '') + '">' + esc(s) + '</span>'; }
  function marker(category) {
    return '<span class="mk m-' + esc(category) + '" aria-hidden="true"></span>';
  }
  function storyById(id) { return (D.stories || []).find(s => s.id === id); }
  function story(id) {
    const s = storyById(id);
    if (!s) return esc(id);
    const home = (D.pages || []).find(p => p.id === 'scope');
    const href = home ? home.file + '#' + encodeURIComponent(s.id) : '#';
    return cls(s.class) + ' <a href="' + href + '">' + esc(s.label) + '</a>';
  }
  function questionLink(qid) {
    const page = (D.pages || []).find(p => p.id === 'decisions');
    const q = (D.questions || []).find(x => x.id === qid);
    if (!q) return esc(qid);
    return page ? '<a href="' + page.file + '#' + encodeURIComponent(qid) + '">' + esc(q.text) + '</a>' : esc(q.text);
  }
  function fold(id, title, body) {
    return '<details class="fold" id="' + esc(id) + '" data-fold><summary>' + esc(title) + '</summary><div class="inner">' + body + '</div></details>';
  }
  function openFromHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id) return null;
    const el = document.getElementById(id);
    if (el && el.tagName === 'DETAILS') { el.open = true; el.scrollIntoView(); }
    return el;
  }

  const store = {
    db: null, uid: '', ready: null, local: {},
    init() {
      if (this.ready) return this.ready;
      try { this.local = JSON.parse(localStorage.getItem('rs-store') || '{}'); } catch (e) { this.local = {}; }
      this.ready = (async () => {
        if (!(window.claude && claude.use)) return;
        try { this.db = await claude.use('db'); } catch (e) { this.db = null; }
        try { const u = await claude.use('user'); if (u) this.uid = await u.id(); } catch (e) { this.uid = ''; }
      })();
      return this.ready;
    },
    saveLocal() { try { localStorage.setItem('rs-store', JSON.stringify(this.local)); } catch (e) { /* storage blocked */ } },
    async set(collection, id, value) {
      await this.init();
      const record = Object.assign({}, value, {at: new Date().toISOString(), by: this.uid || ''});
      if (this.db) { await this.db.doc(collection + '/' + id).set(record); return 'shared'; }
      (this.local[collection] = this.local[collection] || {})[id] = record;
      this.saveLocal();
      return 'local';
    },
    async watch(collection, onChange) {
      await this.init();
      Object.entries(this.local[collection] || {}).forEach(([id, v]) => onChange(id, v));
      if (this.db) this.db.collection(collection).onSnapshot(q => q.docs.forEach(d => onChange(d.id, d.data())), () => {});
    },
    async add(collection, value) {
      await this.init();
      if (!this.db) throw new Error('Comments need the shared store');
      return this.db.collection(collection).add(Object.assign({}, value, {at: new Date().toISOString(), by: this.uid || ''}));
    },
    async list(collection, onChange) {
      await this.init();
      if (this.db) this.db.collection(collection).orderBy('at').onSnapshot(q => onChange(q.docs.map(d => d.data())), () => {});
    },
    async names(ids) {
      try { const u = await claude.use('user'); return await u.profiles(ids); } catch (e) { return {}; }
    }
  };

  window.RS = {D, esc, ticket, cls, statusTag, marker, story, storyById, questionLink, fold, openFromHash, store, STATUS_CLASS};
})();
