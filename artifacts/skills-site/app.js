/* Skills Estate map. Every control and record below is a window.LLC component; page.css only lays them out. */
(function () {
  var D = JSON.parse(document.getElementById('estate-data').textContent);
  var L = window.LLC, R = window.React, h = R.createElement;
  var useState = R.useState, useEffect = R.useEffect, useMemo = R.useMemo, useRef = R.useRef;

  var SK = {}, WF = {}, PL = {}, FAM = {};
  D.skills.forEach(function (s) { SK[s.id] = s; });
  D.workflows.forEach(function (w) { WF[w.id] = w; });
  D.plugins.forEach(function (p) { PL[p.id] = p; });
  D.families.forEach(function (f) { FAM[f.id] = f; });
  var byTitle = {}; D.skills.forEach(function (s) { byTitle[s.title] = s.id; });
  var wfByTitle = {}; D.workflows.forEach(function (w) { wfByTitle[w.title] = w.id; });
  var famCount = {}; D.skills.forEach(function (s) { famCount[s.family] = (famCount[s.family] || 0) + 1; });
  var usedIn = {}; D.workflows.forEach(function (w) { w.steps.forEach(function (st) { (usedIn[st.skill] = usedIn[st.skill] || []).push(w.id); }); });

  var KINDS = [['all', 'Any'], ['task', 'Task package'], ['mode', 'Task mode'], ['support', 'Supporting module']];
  var KIND_NAME = { task: 'Task package', mode: 'Task mode', support: 'Supporting module' };
  var WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve'];
  function word(n) { return WORDS[n] || String(n); }
  function plural(n, one, many) { return n + ' ' + (n === 1 ? one : many); }
  function cmd(s) { return !D.publicMap && s.plugin ? '/' + s.plugin + ':' + s.id : ''; }
  function kindText(s) {
    if (s.kind === 'mode' && s.modeOf && s.modeOf[0]) return 'Mode of ' + SK[s.modeOf[0]].title;
    return KIND_NAME[s.kind];
  }
  function longDate(iso) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || ''); if (!m) return iso || '';
    var M = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    return +m[3] + ' ' + M[+m[2] - 1] + ' ' + m[1];
  }
  function words(v) { return v.toLowerCase().trim().split(/\s+/).filter(Boolean); }
  function hay(s) { return [s.title, s.id, s.what, s.when, s.inputs, s.outputs, s.example, s.overview, s.plugin, kindText(s), FAM[s.family].title].join(' ').toLowerCase(); }
  var HAY = {}; D.skills.forEach(function (s) { HAY[s.id] = hay(s); });
  function wfHay(w) { return [w.title, w.desc, w.prompt, w.inputs, w.outcome, w.kind].concat(w.steps.map(function (st) { return SK[st.skill].title; })).join(' ').toLowerCase(); }

  function copy(text) {
    try { if (navigator.clipboard) return navigator.clipboard.writeText(text).catch(function () {}); } catch (e) {}
  }

  // Route: #skill-<id>, #workflow-<id>, #plugin-<id>, #family-<id>, #workflows, #plugins (plain names pass through the claude.ai frame).
  function parse() {
    var x = decodeURIComponent(location.hash.replace(/^#/, ''));
    var m = /^(skill|workflow|plugin|family)[\/-](.+)$/.exec(x);
    if (m && m[1] === 'skill' && SK[m[2]]) return { view: 'skills', sel: m[2] };
    if (m && m[1] === 'workflow' && WF[m[2]]) return { view: 'workflows', wsel: m[2] };
    if (m && m[1] === 'plugin' && PL[m[2]]) return { view: 'plugins', psel: m[2] };
    if (m && m[1] === 'family' && FAM[m[2]]) return { view: 'skills', family: m[2] };
    if (x === 'workflows') return { view: 'workflows' };
    if (x === 'plugins') return { view: 'plugins' };
    if (x === 'skills') return { view: 'skills' };
    return { view: 'home' };
  }

  function useSmall() {
    var mq = window.matchMedia('(max-width: 900px)');
    var st = useState(mq.matches);
    useEffect(function () { function on() { st[1](mq.matches); } mq.addEventListener('change', on); return function () { mq.removeEventListener('change', on); }; }, []);
    return st[0];
  }

  function Links(p) {
    return h('span', { className: 'se-links' }, p.ids.map(function (id) {
      var label = p.kind === 'workflow' ? WF[id].title : p.kind === 'plugin' ? id : SK[id].title;
      return h('button', { key: id, type: 'button', className: 'se-link', onClick: function () { p.go(p.kind, id); } }, label);
    }));
  }
  function Names(list, go) {
    return h('span', { className: 'se-links' }, list.map(function (c, i) {
      return c.skill ? h('button', { key: i, type: 'button', className: 'se-link', onClick: function () { go('skill', c.skill); } }, SK[c.skill].title) : h('span', { key: i }, (i ? ', ' : '') + c.text);
    }));
  }
  function row(label, value) { return value ? { label: label, value: value } : null; }
  function section(label, rows) { rows = rows.filter(Boolean); return rows.length ? { label: label, rows: rows } : null; }
  function CodeBlock(p) { return h('pre', { className: 'llc-pg llc-codeblock' + (p.prompt ? ' se-prompt' : '') }, h('button', { type: 'button' }, 'Copy'), p.text); }

  function SkillDetail(p) {
    var s = SK[p.id], go = p.go;
    var c = cmd(s), parent = s.modeOf && SK[s.modeOf[0]];
    var runRow = c ? row('Command', h(CodeBlock, { text: c }))
      : parent && parent.plugin ? row('Command', h(R.Fragment, null, h(CodeBlock, { text: cmd(parent) }), h('span', null, 'Runs through ' + parent.title + (s.modeName ? '. Ask for the ' + s.modeName + '.' : '.'))))
      : row('Command', 'It has no command. It installs with the task packages listed under Ships inside.');
    var sections = [
      !D.publicMap && section('Run it', [runRow, s.example ? row('Example request', h(CodeBlock, { text: s.example, prompt: true })) : null]),
      section('What it does', [row('How it works', s.overview), row('Use it when', s.when), row('Give it', s.inputs), row('You get', s.outputs)]),
      section('Before you start', [row('Prepare', s.where), row('If something is missing', s.missing), row('Requires', s.requires),
        row('Setup', s.setup), s.needs ? row('Needs', Names(s.needs, go)) : null, s.optional ? row('Works with', Names(s.optional, go)) : null,
        s.prepSkills ? row('Run first', h(Links, { ids: s.prepSkills, kind: 'skill', go: go })) : null]),
      section('Connections', [
        row('Kind', kindText(s)),
        s.plugin ? row('Plugin', h(Links, { ids: [s.plugin], kind: 'plugin', go: go })) : null,
        parent ? row('Runs inside', h(Links, { ids: s.modeOf, kind: 'skill', go: go })) : null,
        s.modes ? row('Its modes', h(Links, { ids: s.modes, kind: 'skill', go: go })) : null,
        s.usedBy ? row('Ships inside', h(Links, { ids: s.usedBy, kind: 'skill', go: go })) : null,
        s.uses ? row('Draws on', h(Links, { ids: s.uses, kind: 'skill', go: go })) : null,
        usedIn[s.id] ? row('In workflows', h(Links, { ids: usedIn[s.id], kind: 'workflow', go: go })) : null,
        s.examples ? row('Recorded examples', plural(s.examples, 'run', 'runs') + ' in the repository') : null])
    ].filter(Boolean);
    return h(L.DetailPanel, { kicker: FAM[s.family].title, title: s.title, subtitle: s.what, sections: sections },
      h('div', { className: 'se-actions' },
        h('div', { className: 'se-row' }, s.downloadUrl ? h(L.Button, { variant: 'ghost', size: 'sm', href: s.downloadUrl, icon: 'file-text' }, 'Download SKILL.md') : !D.publicMap && h(L.Button, { variant: 'ghost', size: 'sm', href: s.src, icon: 'file-text' }, 'SKILL.md on GitHub'),
          h(L.Button, { variant: 'ghost', size: 'sm', icon: 'send', onClick: function () { copy((D.pageUrl && D.pageUrl.charAt(0) === '/' ? location.origin + D.pageUrl : D.pageUrl || location.href.split('#')[0]) + '#skill-' + s.id); p.toast('Link to ' + s.title + ' copied'); } }, 'Copy link'))));
  }

  function StepSeq(p) {
    var ref = useRef(null), w = WF[p.id];
    useEffect(function () { if (window.LLCInteractions) window.LLCInteractions.init(ref.current); }, [p.id]);
    var n = w.steps.length;
    var marks = [];
    w.steps.forEach(function (st, i) { if (i) marks.push(h('u', { key: 'u' + i })); marks.push(h('span', { key: 'n' + i, className: 'ix-nm' + (i === 0 ? ' is-on' : '') }, i + 1)); });
    return h('div', { className: 'ix se-steps', ref: ref }, h('div', { className: 'ix-card ix-x' }, h('div', { className: 'ix-stp', style: { display: 'grid', gap: '14px' } },
      h('div', { className: 'ix-st' }, marks),
      h('div', { className: 'ix-well ix-st-v' }, w.steps.map(function (st, i) {
        var s = SK[st.skill];
        return h('div', { key: i, className: i === 0 ? 'is-on' : '' }, h('small', null, 'Step ' + (i + 1) + ' of ' + n), h('strong', null, s.title), h('p', null, st.why),
          cmd(s) ? h('small', null, cmd(s)) : null,
          h('span', { className: 'se-links' }, h('button', { type: 'button', className: 'se-link', onClick: function () { p.go('skill', s.id); } }, 'Open ' + s.title)));
      })),
      h('div', { className: 'ix-st-n' }, h('button', { className: 'ix-pillbtn', 'data-d': '-1', disabled: true }, 'Back'), h('button', { className: 'ix-pillbtn is-on', 'data-d': '1' }, 'Next')))));
  }

  function WorkflowDetail(p) {
    var w = WF[p.id];
    var plugins = []; w.steps.forEach(function (st) { var pl = SK[st.skill].plugin || (SK[st.skill].modeOf && SK[SK[st.skill].modeOf[0]].plugin); if (pl && plugins.indexOf(pl) < 0) plugins.push(pl); });
    return h(L.DetailPanel, { kicker: w.kind, title: w.title, subtitle: w.desc, sections: [
      section('Ask Claude', [row('Request to paste', h(CodeBlock, { text: w.prompt, prompt: true }))]),
      section('Skills', [row('Run them in this order', h(StepSeq, { key: w.id, id: w.id, go: p.go }))]),
      section('Bring', [row('Start with', w.inputs), row('You get', w.outcome), row('Note', w.note),
        !D.publicMap && plugins.length ? row('Install', h(Links, { ids: plugins, kind: 'plugin', go: p.go })) : null])].filter(Boolean) });
  }

  function PluginDetail(p) {
    var pl = PL[p.id];
    return h(L.DetailPanel, { kicker: 'Plugin', title: pl.id, subtitle: pl.desc, sections: [!D.publicMap && section('Install', [row('In Claude Code', h(CodeBlock, { text: '/plugin install ' + pl.id + '@skills-estate' }))]),
      section('Contents', [row(plural(pl.skills.length, 'skill', 'skills'), h(Links, { ids: pl.skills, kind: 'skill', go: p.go }))])].filter(Boolean) },
      h('div', { className: 'se-actions' },
        h('div', { className: 'se-row' }, h(L.Button, { variant: 'secondary', size: 'sm', onClick: function () { p.showPlugin(pl.id); } }, 'Show these skills in the list'))));
  }

  function App() {
    var small = useSmall();
    var init = parse();
    var s_view = useState(init.view), view = s_view[0];
    var s_fam = useState(init.family || 'all'), family = s_fam[0];
    var s_q = useState(''), q = s_q[0];
    var s_kind = useState('all'), kind = s_kind[0];
    var s_pl = useState(null), plugin = s_pl[0];
    var s_order = useState('family'), order = s_order[0];
    var s_sel = useState(init.sel || null), sel = s_sel[0];
    var s_wsel = useState(init.wsel || null), wsel = s_wsel[0];
    var s_psel = useState(init.psel || null), psel = s_psel[0];
    var s_wkind = useState('all'), wkind = s_wkind[0];
    var s_wfam = useState(null), wfam = s_wfam[0];
    var s_sheet = useState(!!(init.sel || init.wsel || init.psel)), sheet = s_sheet[0];
    var s_toast = useState(null), toast = s_toast[0];
    var s_menuKey = useState(0), menuKey = s_menuKey[0];
    var s_reset = useState(0), resetKey = s_reset[0];
    var s_theme = useState(function () { try { return localStorage.getItem('se-theme') || 'dark'; } catch (e) { return 'dark'; } }), theme = s_theme[0];
    var rootRef = useRef(null);

    function say(t) { s_toast[1](t); clearTimeout(say.t); say.t = setTimeout(function () { s_toast[1](null); }, 1800); }
    function notifyHost() { if (parent !== window && D.pageUrl) parent.postMessage({ type: 'skills-site-hash', hash: location.hash }, location.origin); }
    function setHash(x) { if (x) { if (location.hash !== '#' + x) location.hash = x; } else if (location.hash) history.replaceState(null, '', location.pathname + location.search); notifyHost(); }

    function go(kind, id) {
      if (kind === 'skill') { s_view[1]('skills'); s_sel[1](id); s_sheet[1](true); var s = SK[id]; if (family !== 'all' && s.family !== family) s_fam[1]('all'); setHash('skill-' + id); }
      if (kind === 'workflow') { s_view[1]('workflows'); s_wsel[1](id); s_sheet[1](true); setHash('workflow-' + id); }
      if (kind === 'plugin') { s_view[1]('plugins'); s_psel[1](id); s_sheet[1](true); setHash('plugin-' + id); }
      setTimeout(function () { var d = document.querySelector('.se-inline'); if (d) { var r = d.previousElementSibling || d; r.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); } }, 60);
    }
    function closeDetail() {
      if (view === 'skills') s_sel[1](null); else if (view === 'workflows') s_wsel[1](null); else s_psel[1](null);
      setHash(view === 'skills' ? (family !== 'all' ? 'family-' + family : 'skills') : view);
    }
    function setView(v, keepWfam) { if (!keepWfam) s_wfam[1](null); s_view[1](v); s_sheet[1](false); setHash(v === 'home' ? '' : v === 'skills' ? (family !== 'all' ? 'family-' + family : 'skills') : v); window.scrollTo(0, 0); }
    function setFamily(f) { s_view[1]('skills'); s_fam[1](f); s_pl[1](null); s_sheet[1](false); setHash(f === 'all' ? 'skills' : 'family-' + f); }
    function clearAll() { s_q[1](''); s_kind[1]('all'); s_pl[1](null); s_fam[1]('all'); s_wkind[1]('all'); s_wfam[1](null); s_reset[1](resetKey + 1); }
    function showPlugin(id) { clearAll(); s_pl[1](id); s_view[1]('skills'); s_sheet[1](false); setHash('skills'); window.scrollTo(0, 0); }

    useEffect(function () {
      function on() { var r = parse(); s_view[1](r.view); if (r.sel) s_sel[1](r.sel); if (r.wsel) s_wsel[1](r.wsel); if (r.psel) s_psel[1](r.psel); if (r.family) s_fam[1](r.family); s_sheet[1](!!(r.sel || r.wsel || r.psel)); }
      addEventListener('hashchange', on); addEventListener('hashchange', notifyHost);
      if (init.sel || init.wsel || init.psel) setTimeout(function () { var d = document.querySelector('.se-inline'); if (d && d.previousElementSibling) d.previousElementSibling.scrollIntoView({ block: 'start' }); }, 150);
      function key(e) {
        if (e.key === '/' && !/input|textarea|select/i.test((document.activeElement || {}).tagName)) { var i = document.querySelector('.mer-filters-search input'); if (i) { e.preventDefault(); i.focus(); } }
        if (e.key === 'Escape') { if (document.querySelector('.se-inline')) document.querySelector('.se-inline-close button').click(); s_menuKey[1](function (k) { return k + 1; }); }
      }
      addEventListener('keydown', key);
      function outside(e) { if (!e.target.closest('.mer-menu') && document.querySelector('.mer-menu-list')) s_menuKey[1](function (k) { return k + 1; }); }
      document.addEventListener('pointerdown', outside);
      return function () { removeEventListener('hashchange', on); removeEventListener('hashchange', notifyHost); removeEventListener('keydown', key); document.removeEventListener('pointerdown', outside); };
    }, []);

    // Lock the page behind the phone sheet.


    // Each view keeps its own search: the field remounts empty when the view changes, so the query does too.
    useEffect(function () { s_q[1](''); }, [view]);

    // Theme: Night by default, Day on request; the choice is remembered in this browser only.
    useEffect(function () { document.documentElement.setAttribute('data-theme', theme); try { localStorage.setItem('se-theme', theme); } catch (e) {} }, [theme]);

    // Wire the page components (code block copy) and make table rows reachable by keyboard after every render.
    // Sidebar items get the design system's own icon files (Icons asset group), drawn inline so they take the text color.
    useEffect(function () {
      rootRef.current.querySelectorAll('.se-facts .mer-fact').forEach(function (f) {
        var t = f.querySelector('dt').textContent, k = FACT_KIND[t];
        var zero = f.querySelector('dd strong').textContent === '0';
        if (zero) { f.removeAttribute('tabindex'); f.setAttribute('aria-disabled', 'true'); } else { f.tabIndex = 0; f.removeAttribute('aria-disabled'); }
        f.setAttribute('role', 'button');
        f.setAttribute('aria-pressed', (k ? view === 'skills' && kind === k : view === 'workflows') ? 'true' : 'false');
      });
      rootRef.current.querySelectorAll('.mer-sidebar a').forEach(function (a) {
        var pin = a.querySelector('i.mer-pin'), label = a.querySelector('span'); if (!pin || !label) return;
        var t = label.textContent, key = D.icons._map[t] || D.icons._map[(D.families.filter(function (f) { return f.title === t; })[0] || {}).id];
        if (key && pin.getAttribute('data-ico') !== key) { pin.innerHTML = D.icons[key]; pin.setAttribute('data-ico', key); pin.classList.add('se-ico'); }
      });
      if (window.LLCPage) window.LLCPage.init(rootRef.current);
      rootRef.current.querySelectorAll('.mer-table tbody tr:not(.mer-group)').forEach(function (tr) { tr.tabIndex = 0; });
    });

    // Skills list
    var visible = useMemo(function () {
      var w = words(q);
      return D.skills.filter(function (s) {
        return (family === 'all' || s.family === family) && (kind === 'all' || s.kind === kind) && (!plugin || s.plugin === plugin || (s.modeOf && SK[s.modeOf[0]].plugin === plugin))
          && w.every(function (x) { return HAY[s.id].indexOf(x) >= 0; });
      });
    }, [q, family, kind, plugin]);
    var wvisible = useMemo(function () {
      var w = words(q);
      return D.workflows.filter(function (x) { return (wkind === 'all' || x.kind === wkind) && (!wfam || x.steps.some(function (st) { return SK[st.skill].family === wfam; })) && w.every(function (t) { return wfHay(x).indexOf(t) >= 0; }); });
    }, [q, wkind, wfam]);

    // The plugin lives in each skill's detail and on the Plugins page; the list shows what a person scans for.
    var cols = [{ key: 'name', label: 'Skill' }, { key: 'kind', label: 'Kind', width: small ? '34%' : '26%' }];
    function skillRow(s) { return { id: s.id, name: s.title, sub: s.what, plugin: s.plugin || '', kind: kindText(s) }; }
    var tableProps;
    if (view === 'skills') {
      if (order === 'family') {
        tableProps = { columns: cols, groups: D.families.map(function (f) { return { label: h(R.Fragment, null, h('span', { className: 'se-gico', 'aria-hidden': true, dangerouslySetInnerHTML: { __html: D.icons[D.icons._map[f.id]] || '' } }), h('span', { className: 'se-gtitle' }, f.title)), rows: visible.filter(function (s) { return s.family === f.id; }).map(skillRow) }; }).filter(function (g) { return g.rows.length; }) };
      } else {
        tableProps = { columns: cols, rows: visible.slice().sort(function (a, b) { return a.title.localeCompare(b.title); }).map(skillRow) };
      }
      tableProps.selected = sel;
    } else if (view === 'workflows') {
      var kinds = []; D.workflows.forEach(function (w) { if (kinds.indexOf(w.kind) < 0) kinds.push(w.kind); });
      tableProps = { columns: [{ key: 'name', label: 'Workflow' }, { key: 'n', label: 'Skills', numeric: true, width: '84px' }],
        groups: kinds.map(function (k) { return { label: k, rows: wvisible.filter(function (w) { return w.kind === k; }).map(function (w) { return { id: w.id, name: w.title, sub: w.desc, n: w.steps.length }; }) }; }).filter(function (g) { return g.rows.length; }), selected: wsel };
    } else {
      tableProps = { columns: [{ key: 'name', label: 'Plugin' }, { key: 'n', label: 'Skills', numeric: true, width: '84px' }],
        rows: D.plugins.map(function (p) { return { id: p.id, name: p.id, sub: p.desc, n: p.skills.length }; }), selected: psel };
    }
    tableProps.selectable = true;

    function onTable(e) {
      var tr = e.target.closest('tbody tr'); if (!tr || tr.classList.contains('mer-group')) return;
      if (e.type === 'keydown') { if (e.key !== 'Enter' && e.key !== ' ') return; e.preventDefault(); }
      var cell = tr.querySelector('.mer-cell-main') || tr.querySelector('th'); var name = cell && cell.textContent;
      var id = view === 'skills' ? byTitle[name] : view === 'workflows' ? wfByTitle[name] : PL[name] ? name : null; if (!id) return;
      if (id === (view === 'skills' ? sel : view === 'workflows' ? wsel : psel)) { closeDetail(); return; }
      go(view === 'skills' ? 'skill' : view === 'workflows' ? 'workflow' : 'plugin', id);
    }

    var count = view === 'skills' ? visible.length + ' of ' + D.skills.length + ' skills' : view === 'workflows' ? wvisible.length + ' of ' + D.workflows.length + ' workflows' : D.plugins.length + ' plugins';
    var anySet = q || kind !== 'all' || plugin || (view === 'skills' && family !== 'all') || wkind !== 'all' || (view === 'workflows' && wfam);

    function menu(label, items, current, pick) {
      return h('div', { key: label + menuKey, onClick: function (e) {
        var b = e.target.closest('[role=menuitem]'); if (!b) return;
        var t = b.querySelector('b').textContent; items.forEach(function (it) { if (it[1] === t) pick(it[0]); }); s_menuKey[1](menuKey + 1);
      } }, h(L.Menu, { label: label + ': ' + current, items: items.map(function (it) { return { label: it[1], icon: it[1] === current ? 'check' : undefined, hint: it[2] }; }) }));
    }

    var tools = h('div', { className: 'se-tools' },
      h('div', { className: 'se-grow', key: 'fb' + resetKey + view, onInput: function (e) { if (e.target.tagName === 'INPUT') s_q[1](e.target.value); },
        onClick: function (e) { if (e.target.closest('.mer-filters-clear')) clearAll(); } },
        h(L.FilterBar, { search: view === 'skills' ? 'Search skills: discovery, scope, writing' : view === 'workflows' ? 'Search workflows: interviews, release, resume' : undefined, count: count, clearable: !!anySet,
          filters: plugin && view === 'skills' ? [{ label: 'Plugin', value: plugin, set: true }] : wfam && view === 'workflows' ? [{ label: 'Family', value: FAM[wfam].title, set: true }] : [] })),
      view === 'skills' ? menu('Kind', KINDS.map(function (k) { return [k[0], k[1], k[0] === 'task' ? 'Install one and ask for it' : k[0] === 'mode' ? 'Runs inside another skill' : k[0] === 'support' ? 'Ships inside task packages' : '']; }),
        KINDS.filter(function (k) { return k[0] === kind; })[0][1], function (v) { s_kind[1](v); }) : null,
      view === 'skills' ? menu('Order', [['family', 'By family'], ['az', 'A to Z']], order === 'family' ? 'By family' : 'A to Z', function (v) { s_order[1](v); }) : null,
      view === 'workflows' ? menu('Kind of work', [['all', 'Any']].concat(kindsOf()), wkind === 'all' ? 'Any' : wkind, function (v) { s_wkind[1](v); }) : null);
    function kindsOf() { var k = []; D.workflows.forEach(function (w) { if (!k.some(function (x) { return x[0] === w.kind; })) k.push([w.kind, w.kind]); }); return k; }

    var detailId = view === 'skills' ? sel : view === 'workflows' ? wsel : psel;
    var detail = detailId
      ? (view === 'skills' ? h(SkillDetail, { key: detailId, id: detailId, go: go, toast: say }) : view === 'workflows' ? h(WorkflowDetail, { key: detailId, id: detailId, go: go }) : h(PluginDetail, { key: detailId, id: detailId, go: go, showPlugin: showPlugin }))
      : null;

    var list = (view === 'skills' && !visible.length) || (view === 'workflows' && !wvisible.length)
      ? h(L.EmptyState, { title: view === 'skills' ? 'No skills match' : 'No workflows match', action: h(L.Button, { variant: 'secondary', size: 'sm', onClick: clearAll }, 'Clear filters') }, 'Try fewer words, or clear the filters to see the whole list.')
      : h('div', { className: 'se-list', onClick: onTable, onKeyDown: onTable }, chunks().map(function (c, i) {
          return c.detail ? h('div', { key: 'detail', className: 'se-inline', role: 'region', 'aria-label': 'Details' }, h('div', { className: 'se-inline-close' }, h(L.IconButton, { icon: 'close', label: 'Close details', size: 'sm', onClick: closeDetail })), c.detail)
            : h('div', { key: i, className: 'se-chunk' + (c.split ? ' is-split' : '') }, h(L.DataTable, Object.assign({ key: view + order + i + (c.sel || '') + small, columns: tableProps.columns, selectable: true, selected: c.sel }, c.groups ? { groups: c.groups } : c.group ? { groups: [c.group] } : { rows: c.rows })));
        }));
    // Split the list at the selected row so its detail opens directly beneath it.
    function chunks() {
      var out = [], selId = tableProps.selected, groups = tableProps.groups || [{ label: null, rows: tableProps.rows }];
      var run = null; // consecutive whole groups share one table
      groups.forEach(function (g) {
        var at = -1; g.rows.forEach(function (r, i) { if (r.id === selId) at = i; });
        if (at < 0) { if (!g.label) { out.push({ rows: g.rows }); run = null; return; } if (!run) { run = { groups: [] }; out.push(run); } run.groups.push(g); return; }
        run = null;
        var head = g.rows.slice(0, at + 1), tail = g.rows.slice(at + 1);
        out.push(g.label ? { group: { label: h(R.Fragment, null, g.label, h('span', { className: 'se-gcount' }, g.rows.length)), rows: head }, sel: selId, split: true } : { rows: head, sel: selId });
        out.push({ detail: detail });
        if (tail.length) out.push({ rows: tail });
      });
      return out;
    }

    var heads = {
      home: ['Skills Estate', D.publicMap ? D.skills.length + ' skills published for this site. Pick a family or a kind of skill to see its list.' : D.skills.length + ' skills for sales pursuits, scoping, delivery, Salesforce development, product work, writing and job applications, installed as ' + word(D.plugins.length) + ' plugins from one marketplace. Pick a kind of skill or a family to see its list.'],
      skills: ['Find the skill for a job', family !== 'all' ? FAM[family].title + ': ' + plural(famCount[family] || 0, 'skill', 'skills') + '. ' + FAM[family].desc : D.skills.length + ' skills, sorted by the work they do and installed as ' + word(D.plugins.length) + ' plugins. Search by the job in plain words, or pick a family.'],
      workflows: ['Run skills in order for a job', 'Each workflow names what to bring, the request to paste into Claude and the skills that run. Run only the steps your work needs.'],
      plugins: D.publicMap ? ['Plugins', 'Browse the skills in each plugin.'] : ['Install the plugins', 'Skills install in ' + word(D.plugins.length) + ' plugins from the Skills Estate marketplace. Install a plugin, then ask for the work in plain words or run its command. In Codex on a Mac, python3 tools/estate.py update installs them from a Skills Estate checkout.']
    };

    var viewLabel = { home: 'Overview', skills: 'Skills', workflows: 'Workflows', plugins: 'Plugins' };
    var crumbs = view === 'home' ? ['Skills Estate'] : ['Skills Estate', viewLabel[view]]; if (view === 'skills' && family !== 'all') crumbs.push(FAM[family].title);

    var sidebar = h('div', { onClick: function (e) {
      var a = e.target.closest('a'); if (!a) return; e.preventDefault();
      var t = a.querySelector('span').textContent;
      if (t === 'Overview') { clearAll(); setView('home'); } else if (t === 'Skills') setFamily('all'); else if (t === 'Workflows') setView('workflows'); else if (t === 'Plugins') setView('plugins');
      else if (t === 'All skills') setFamily('all'); else D.families.forEach(function (f) { if (f.title === t) setFamily(f.id); });
    }, style: { display: 'contents' } }, h(L.Sidebar, { groups: [
      { items: [{ label: 'Overview', current: view === 'home' }, { label: 'Skills', count: D.skills.length, current: view === 'skills' }, { label: 'Workflows', count: D.workflows.length, current: view === 'workflows' }, { label: 'Plugins', count: D.plugins.length, current: view === 'plugins' }] },
      { label: 'Families', items: [{ label: 'All skills', count: D.skills.length, current: view === 'skills' && family === 'all' }].concat(D.families.map(function (f) { return { label: f.title, count: famCount[f.id] || 0, current: view === 'skills' && family === f.id }; })) }] }));

    var mobile = view === 'home' ? null : h('div', { className: 'se-mobile' },
      h('div', { key: 'seg' + view, onClick: function (e) { var b = e.target.closest('button'); if (b) setView(b.textContent.toLowerCase()); } }, h(L.Segmented, { items: ['Skills', 'Workflows', 'Plugins'], defaultValue: viewLabel[view], label: 'View' })),
      view === 'skills' ? h('div', { key: 'fam' + family, onChange: function (e) { var i = e.target.selectedIndex; setFamily(i === 0 ? 'all' : D.families[i - 1].id); } },
        h(L.Field, { label: 'Family', as: 'select', options: ['All families (' + D.skills.length + ')'].concat(D.families.map(function (f) { return f.title + ' (' + (famCount[f.id] || 0) + ')'; })),
          defaultValue: family === 'all' ? 'All families (' + D.skills.length + ')' : FAM[family].title + ' (' + famCount[family] + ')' })) : null);

    // The headline facts are filters: a kind narrows the skill list (press again to clear), Workflows opens that view.
    var FACT_KIND = { 'Task packages': 'task', 'Task modes': 'mode', 'Supporting modules': 'support' };
    // On a family, the facts count that family's skills and the workflows that use them.
    var scopeFam = view === 'skills' ? (family !== 'all' ? family : null) : view === 'workflows' ? wfam : null, inFamily = !!scopeFam;
    function scopeCount(k) { return D.skills.filter(function (s) { return s.kind === k && (!inFamily || s.family === scopeFam); }).length; }
    var scopeWorkflows = D.workflows.filter(function (w) { return !inFamily || w.steps.some(function (st) { return SK[st.skill].family === scopeFam; }); }).length;
    function pickFact(e) {
      var f = e.target.closest('.mer-fact'); if (!f || f.getAttribute('aria-disabled') === 'true') return;
      if (e.type === 'keydown') { if (e.key !== 'Enter' && e.key !== ' ') return; e.preventDefault(); }
      var t = f.querySelector('dt').textContent;
      if (t === 'Workflows') { if (view === 'workflows') return; s_wfam[1](scopeFam); setView('workflows', true); return; }
      var k = FACT_KIND[t]; if (!k) return;
      if (view === 'skills' && kind === k) s_kind[1]('all'); else { s_kind[1](k); if (view !== 'skills') { s_fam[1](scopeFam || 'all'); s_view[1]('skills'); s_sheet[1](false); setHash(scopeFam ? 'family-' + scopeFam : 'skills'); window.scrollTo(0, 0); } }
    }
    var facts = view === 'home' || !small ? h('div', { className: 'se-facts' + ((view === 'skills' && kind !== 'all') || view === 'workflows' ? ' se-picking' : ''), onClick: pickFact, onKeyDown: pickFact }, h(L.FactBand, { facts: [
      { label: 'Task packages', value: scopeCount('task'), note: 'Install one and ask for it directly' },
      { label: 'Task modes', value: scopeCount('mode'), note: 'Run inside another skill' },
      { label: 'Supporting modules', value: scopeCount('support'), note: 'Ship inside the packages that use them' },
      { label: 'Workflows', value: scopeWorkflows, note: inFamily ? 'Workflows that use these skills' : 'Skills matched to a job, in order' }] })) : null;

    var familyGrid = view === 'home' ? h('section', { className: 'se-fams', 'aria-label': 'Families' }, h('h2', null, 'Families'),
      h('div', { className: 'se-grid' }, D.families.map(function (f) {
        return h('button', { key: f.id, type: 'button', className: 'se-cell', onClick: function () { setFamily(f.id); window.scrollTo(0, 0); } },
          h('span', { className: 'se-cell-ico', 'aria-hidden': true, dangerouslySetInnerHTML: { __html: D.icons[D.icons._map[f.id]] || '' } }),
          h('strong', null, f.title), h('span', { className: 'se-cell-desc' }, f.desc), h('span', { className: 'se-cell-n' }, plural(famCount[f.id] || 0, 'skill', 'skills')));
      }))) : null;

    var install = view === 'plugins' ? h(R.Fragment, null, h(L.Callout, { title: 'Add the Skills Estate marketplace once', icon: 'plus' },
      'In the Claude app, open Customize, then Plugins, then Add, and add mshellman-llc/Skills-Estate with automatic sync on. In Claude Code, run the command below.'),
      h(CodeBlock, { text: '/plugin marketplace add mshellman-llc/Skills-Estate' })) : null;

    var famNote = false ? h('p', { className: 'se-foot', style: { fontSize: '14px', lineHeight: '22px' } }, FAM[family].desc) : null;

    return h('div', { ref: rootRef, style: { display: 'contents' } },
      sidebar,
      h('div', { className: 'se-main' },
        h('div', { onClick: function (e) { var a = e.target.closest('.br-bc a'); if (!a) return; e.preventDefault(); if (a.textContent === 'Skills Estate') { clearAll(); setView('home'); } else if (a.textContent === 'Skills') setFamily('all'); else setView(view); } },
          h(L.TopBar, { lead: h(L.Breadcrumb, { items: crumbs }) }, h(L.IconButton, { icon: theme === 'dark' ? 'sun' : 'moon', label: theme === 'dark' ? 'Switch to Day' : 'Switch to Night', size: 'sm', onClick: function () { s_theme[1](theme === 'dark' ? 'light' : 'dark'); } }), !D.publicMap && h('span', { className: 'se-hide-sm' }, h(L.Button, { variant: 'secondary', size: 'sm', href: 'https://github.com/mshellman-llc/Skills-Estate', icon: 'file-text' }, 'Repository on GitHub')))),
        h('main', { className: 'se-body' },
          h('div', { className: 'se-head' }, h('span', { className: 'se-rule', 'aria-hidden': true }), h('h1', null, heads[view][0]), h('p', null, heads[view][1])),
          facts, familyGrid, mobile, install, view === 'home' || view === 'plugins' ? null : tools, famNote,
          view === 'home' ? null : list,
          h('p', { className: 'se-foot' }, D.publicMap ? 'Updated ' + longDate(D.date) : h(R.Fragment, null, 'Skills Estate main at ', h('a', { href: D.commitUrl }, 'commit ' + D.commit), ', ' + longDate(D.date) + '.'))),
        toast ? h('div', { className: 'se-toast' }, h(L.Toast, null, toast)) : null));
  }

  ReactDOM.createRoot(document.getElementById('root')).render(h(App));
})();
