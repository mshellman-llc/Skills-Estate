/* Roadmap Kit v2 renderer. No dependencies. Schema: references/schema.md
   Three ways in: <rk-roadmap src="plan.json"> (or with an inline <script type="application/json"> child),
   RoadmapKit.mount(plan, element), or a page with <main id="rk-root"> and <script id="rk-data">.
   Live connector data is added by rk-live.js through RoadmapKit.setBlock / setLive. */
(function () {
  "use strict";
  var DAY = 86400000;
  var UNIT_W = { day: 32, week: 68, month: 120, quarter: 210 };
  var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function d(s) { var p = String(s).split("-"); return Date.UTC(+p[0], +p[1] - 1, +(p[2] || 1)); }
  function fmt(t) { var x = new Date(t); return MONTHS[x.getUTCMonth()] + " " + x.getUTCDate(); }
  function attr(name, v) { return v == null || v === "" ? "" : " " + name + '="' + esc(v) + '"'; }
  function store(key, val) {
    try { if (val === undefined) return JSON.parse(localStorage.getItem(key)); localStorage.setItem(key, JSON.stringify(val)); }
    catch (e) { return null; }
  }

  // Formats. Earlier names still work: work = compact, pastel = relaxed, present = editorial.
  var MODES = { relaxed: "relaxed", compact: "compact", editorial: "editorial", pastel: "relaxed", work: "compact", present: "editorial" };

  function RK(data, root) {
    this.src = JSON.parse(JSON.stringify(data));
    this.data = data;
    this.root = root;
    this.groups = {};
    var self = this;
    ((data.legend && data.legend.items) || []).forEach(function (g) { self.groups[g.key] = g; });
    this.active = null;
    this.live = {};
    // The mode is chosen when the roadmap is built (meta.mode). The viewer switch exists only for
    // design review pages that turn it on with mount(..., {modeSwitch: true}).
    this.modeSwitch = false;
    this.mode = MODES[(data.meta && data.meta.mode) || "relaxed"] || "relaxed";
    this.corners = (data.meta && data.meta.corners) || "rounded";
    this.parts = { header: true, toolbar: true, blocks: true, footer: true };
    var saved = data.id && data.persist !== false ? store("rk:" + data.id) : null;
    if (saved && saved.cards) this.applyPositions(saved.cards);
  }

  RK.prototype.cat = function (key) { var g = this.groups[key]; return g ? g.c : null; };

  RK.prototype.applyPositions = function (pos) {
    (this.data.blocks || []).forEach(function (b) {
      if (b.type !== "board") return;
      b.cards.forEach(function (c) { if (c.id && pos[c.id]) c.col = pos[c.id]; });
    });
  };

  RK.prototype.render = function () {
    var D = this.data, h = [], P = this.parts;
    this.root.setAttribute("data-rk-mode", this.mode);
    this.root.setAttribute("data-rk-corners", this.corners);
    if (P.header) h.push(this.header(D.meta || {}));
    if (P.toolbar) h.push(this.toolbar(D));
    var self = this;
    (D.blocks || []).forEach(function (b, i) { if (P.blocks) h.push(self.block(b, i)); });
    var M = D.meta || {}, srcs = (M.sources || []).map(function (x) {
      return "<span>" + esc(x.name) + (x.detail ? " \u00b7 " + esc(x.detail) : "") + (x.retrieved ? " \u00b7 " + esc(x.retrieved) : "") + "</span>";
    }).join("");
    if (P.footer) h.push('<footer class="rk-foot"><span class="rk-sources">' + (M.source ? "<span>" + esc(M.source) + "</span>" : "") + srcs + "</span><span class=\"rk-mono\">" +
      esc(M.updated ? "Updated " + M.updated : "") + "</span></footer>");
    this.root.innerHTML = h.join("");
    this.bind();
    this.drawDeps();
  };

  RK.prototype.header = function (m) {
    var h = '<header class="rk-head">';
    var eb = m.eyebrow ? '<div class="rk-eyebrow">' + [].concat(m.eyebrow).map(function (e) { return "<span>" + esc(e) + "</span>"; }).join("") + "</div>" : "<div></div>";
    if (m.logo && m.logo.src) h += '<div class="rk-brandrow">' + eb + '<img class="rk-logo" src="' + esc(m.logo.src) + '" alt="' + esc(m.logo.alt || "") + '"></div>';
    else if (m.eyebrow) h += eb;
    h += '<h1 class="rk-title">' + esc(m.title || "Roadmap") + "</h1>";
    if (m.subtitle) h += '<p class="rk-sub">' + esc(m.subtitle) + "</p>";
    if (m.northStar) h += '<div class="rk-northstar"><b>' + esc(m.northStar.label || "North star") + "</b><span>" + esc(m.northStar.value) + "</span></div>";
    if (m.stats && m.stats.length) {
      h += '<dl class="rk-stats">' + m.stats.map(function (s) {
        var v = esc(s.value);
        if (s.target != null) v += '<span class="rk-arrow">\u2192</span><span class="rk-target">' + esc(s.target) + "</span>";
        return '<div class="rk-stat"' + attr("data-tone", s.tone) + "><dt>" + esc(s.label) + "</dt><dd>" + v + "</dd></div>";
      }).join("") + "</dl>";
    }
    return h + "</header>";
  };

  RK.prototype.toolbar = function (D) {
    var L = D.legend || {}, h = '<div class="rk-bar"><ul class="rk-legend" aria-label="Legend">';
    if (L.items && L.items.length) {
      h += '<li class="rk-legend-title">' + esc(L.title || "Key") + "</li>";
      h += L.items.map(function (g) {
        return '<li><button type="button" class="rk-key" aria-pressed="true" data-key="' + esc(g.key) + '"' + attr("data-c", g.c) +
          '><span class="rk-sw"></span>' + esc(g.label) + "</button></li>";
      }).join("");
    }
    (L.symbols || []).forEach(function (s) {
      h += '<li><span class="rk-key" style="cursor:default"><span class="rk-sw ' + (s.shape ? "is-" + esc(s.shape) : "") + '"' +
        attr("data-c", s.c) + "></span>" + esc(s.label) + "</span></li>";
    });
    h += "</ul>";
    var hasBoard = (D.blocks || []).some(function (b) { return b.type === "board" && b.movable !== false; });
    h += '<div class="rk-actions"><span class="rk-toast" role="status" aria-live="polite"></span>';
    if (this.modeSwitch) h += '<span class="rk-mode" role="group" aria-label="View mode"><button type="button" data-mode="relaxed" aria-pressed="' + (this.mode === "relaxed") + '">Relaxed</button><button type="button" data-mode="compact" aria-pressed="' + (this.mode === "compact") + '">Compact</button><button type="button" data-mode="editorial" aria-pressed="' + (this.mode === "editorial") + '">Editorial</button></span>';
    if (hasBoard) h += '<button type="button" class="rk-btn" data-act="reset">Reset moves</button>';
    h += '<button type="button" class="rk-btn" data-act="copy">Copy plan JSON</button></div></div>';
    return h;
  };

  RK.prototype.section = function (b, i, inner) {
    var lv = this.live[i], pill = "";
    if (lv) pill = ' <span class="rk-live"' + attr("data-tone", lv.tone) + ' role="status">' + esc(lv.text) + (lv.action ? ' <button type="button" data-live-act="' + i + '">' + esc(lv.action.label) + "</button>" : "") + "</span>";
    var t = (b.title || lv) ? '<h2 class="rk-h2">' + esc(b.title || "") + (b.kicker ? " <small>" + esc(b.kicker) + "</small>" : "") + pill + "</h2>" : "";
    var n = b.note ? '<p class="rk-note">' + esc(b.note) + "</p>" : "";
    return '<section class="rk-section" data-block="' + i + '" data-type="' + esc(b.type) + '">' + t + n + inner + "</section>";
  };

  RK.prototype.block = function (b, i) {
    var fn = this["b_" + b.type];
    return fn ? this.section(b, i, fn.call(this, b, i)) : "";
  };

  /* ---------- shared pieces ---------- */
  RK.prototype.tags = function (tags) {
    if (!tags || !tags.length) return "";
    return '<div class="rk-tags">' + tags.map(function (t) {
      if (typeof t === "string") return '<span class="rk-tag">' + esc(t) + "</span>";
      return '<span class="rk-tag"' + attr("data-tone", t.tone) + attr("title", t.title) + ">" + esc(t.t) + "</span>";
    }).join("") + "</div>";
  };
  RK.prototype.owner = function (o) {
    var set = o && !/^(tbd|owner|\?|)$/i.test(String(o).trim());
    return '<span class="rk-owner' + (set ? " is-set" : "") + '">' + esc(set ? o : "Owner: TBD") + "</span>";
  };
  RK.prototype.fields = function (f) {
    if (!f) return "";
    var rows = Array.isArray(f) ? f : Object.keys(f).map(function (k) { return [k, f[k]]; });
    if (!rows.length) return "";
    return '<dl class="rk-fields">' + rows.map(function (r) { return "<dt>" + esc(r[0]) + "</dt><dd>" + esc(r[1]) + "</dd>"; }).join("") + "</dl>";
  };
  // Evidence references: cite is a list of numbers in the host page's evidence list. Each renders as a
  // small superscript link to meta.citeHref + n (default "#ev-n"), so evidence stays in one list.
  RK.prototype.cites = function (list) {
    if (list == null || list === "") return "";
    var pre = (this.data.meta && this.data.meta.citeHref) || "#ev-";
    return '<sup class="rk-cites">' + [].concat(list).map(function (n) {
      return '<a class="rk-ref" href="' + esc(pre + n) + '" aria-label="Evidence ' + esc(n) + '">' + esc(n) + "</a>";
    }).join("") + "</sup>";
  };
  RK.prototype.card = function (c, opts) {
    opts = opts || {};
    var g = this.groups[c.group], h = "";
    h += '<article class="rk-card" tabindex="0"' + attr("data-id", c.id) + attr("data-ref", c.ref) + attr("data-g", c.group) +
      attr("data-c", g && g.c) + (opts.drag ? ' draggable="true"' : "") + ">";
    this._n = (this._n || 0) + 1;
    h += '<span class="rk-num" aria-hidden="true">' + this._n + "</span>";
    var top = "";
    if (g && !opts.noGroup) top += '<span class="rk-chip"><span class="rk-sw"></span>' + esc(g.label) + "</span>";
    if (c.kicker) top += '<span class="rk-chip is-plain">' + esc(c.kicker) + "</span>";
    top += this.tags(c.tags).replace(/^<div class="rk-tags">|<\/div>$/g, "");
    if (top) h += '<div class="rk-card-top">' + top + "</div>";
    h += '<h3 class="rk-card-title">' + esc(c.title) + this.cites(c.cite) + "</h3>";
    if (c.body) h += '<p class="rk-card-body">' + esc(c.body) + "</p>";
    h += this.fields(c.fields);
    var foot = (c.owner !== false ? this.owner(c.owner) : "") + (opts.drag ? '<span class="rk-move"><button type="button" data-mv="-1" aria-label="Move left">\u25c0</button><button type="button" data-mv="1" aria-label="Move right">\u25b6</button></span>' : "");
    if (foot) h += '<div class="rk-card-foot">' + foot + "</div>";
    return h + "</article>";
  };
  RK.prototype.meter = function (label, value, max, opts) {
    opts = opts || {};
    var pct = max ? Math.min(100, (value / max) * 100) : 0, over = opts.flag !== false && max && value > max;
    return '<div class="rk-meter' + (over ? " is-over" : "") + '"' + attr("data-tone", opts.tone) + attr("data-c", opts.c) +
      '><div class="rk-meter-label"><span>' + esc(label) + "</span><b>" + esc(value) + (max ? " / " + esc(max) : "") + esc(opts.unit || "") +
      (over ? " over" : "") + '</b></div><div class="rk-meter-track" role="img" aria-label="' + esc(label + ": " + value + (max ? " of " + max : "")) +
      '"><div class="rk-meter-fill" style="width:' + pct.toFixed(1) + '%"></div></div></div>';
  };

  /* ---------- board: columns of cards, movable ---------- */
  RK.prototype.b_board = function (b, i) {
    var self = this, drag = b.movable !== false;
    this._n = 0;
    var h = '<div class="rk-board' + (b.stack !== false ? " is-stack" : "") + '" data-board="' + i + '">';
    b.columns.forEach(function (col, ci) {
      var cards = b.cards.filter(function (c) { return c.col === col.id; });
      var used = cards.reduce(function (a, c) { return a + (+c.points || 0); }, 0);
      var over = col.capacity != null && used > col.capacity;
      h += '<div class="rk-col' + (over ? " is-flag" : "") + '" data-col="' + esc(col.id) + '" data-ci="' + ci + '"' + attr("data-tone", col.tone) + '><div class="rk-col-head">' +
        '<div class="rk-col-title"><h3>' + esc(col.title) + "</h3><span><b>" + cards.length + "</b><i>" + (cards.length === 1 ? " item" : " items") + "</i></span></div>";
      if (col.subtitle) h += '<p class="rk-col-sub">' + esc(col.subtitle) + "</p>";
      if (col.capacity != null) h += self.meter(b.capacityLabel || "Planned / capacity", used, col.capacity, { unit: b.unit ? " " + b.unit : "" });
      if (col.tags) h += self.tags(col.tags);
      h += '</div><div class="rk-col-list">' + cards.map(function (c) { return self.card(c, { drag: drag }); }).join("") + "</div></div>";
    });
    return h + "</div>";
  };

  /* ---------- timeline: gantt, swimlanes, countdown ---------- */
  RK.prototype.b_timeline = function (b) {
    var self = this, scale = b.scale || "month";
    var S = d(b.start), E = d(b.end) + DAY, span = E - S;
    function x(t) { return ((t - S) / span) * 100; }
    var ticks = [], t;
    // relative: "week" or "day" labels the axis 1, 2, 3 ... from start, for plans that have durations
    // but no calendar dates. Bar dates are then placeholders counted from start.
    var rel = b.relative === "week" || b.relative === "day" ? b.relative : null, relStep = (rel === "day" ? 1 : 7) * DAY;
    var when = rel ? function (t) { return (rel === "day" ? "day " : "week ") + (Math.floor((t - S) / relStep) + 1); } : fmt;
    if (rel) {
      for (t = S; t < E; t += relStep) ticks.push({ t: t, label: String(Math.round((t - S) / relStep) + 1), major: false });
      if (ticks.length) ticks[0].sub = rel === "day" ? "Day" : "Week";
      scale = rel;
    } else if (b.countdown) {
      var ev = d(b.countdown.date), step = (b.countdown.unit === "day" ? 1 : 7) * DAY;
      for (t = ev; t >= S; t -= step) ticks.unshift({ t: t, label: "T-" + Math.round((ev - t) / step), sub: fmt(t), major: t === ev });
      ticks[ticks.length - 1].label = "T-0";
      scale = b.countdown.unit === "day" ? "day" : "week";
    } else if (scale === "week") {
      var s0 = new Date(S), dow = (s0.getUTCDay() + 6) % 7;
      for (t = S - dow * DAY; t < E; t += 7 * DAY) if (t >= S) ticks.push({ t: t, label: fmt(t), major: new Date(t).getUTCDate() <= 7 });
    } else if (scale === "day") {
      for (t = S; t < E; t += DAY) ticks.push({ t: t, label: String(new Date(t).getUTCDate()), major: new Date(t).getUTCDay() === 1 });
    } else {
      var dt = new Date(S), y = dt.getUTCFullYear(), mo = dt.getUTCMonth();
      var inc = scale === "quarter" ? 3 : 1;
      if (scale === "quarter") mo = mo - (mo % 3);
      for (t = Date.UTC(y, mo, 1); t < E; mo += inc, t = Date.UTC(y, mo, 1)) {
        var m = new Date(t).getUTCMonth(), yy = new Date(t).getUTCFullYear();
        ticks.push({ t: Math.max(t, S), label: scale === "quarter" ? "Q" + (m / 3 + 1) : MONTHS[m], sub: (m === 0 || !ticks.length) ? String(yy) : (scale === "month" && m % 3 === 0 ? "Q" + (m / 3 + 1) : ""), major: m % 3 === 0 });
      }
    }
    var units = Math.max(ticks.length, 1);
    var unitW = b.unitWidth || UNIT_W[scale] || 64;
    var markers = (b.markers || []).slice();
    if (b.today) markers.push({ date: b.today, label: "Today", tone: "muted", dashed: true });
    var h = '<div class="rk-tl-wrap"><div class="rk-tl' + (markers.length ? " has-markers" : "") + '" style="--rk-units:' + units + ";--rk-unit-w:" + unitW + "px" + (b.labelWidth ? ";--rk-label-w:" + b.labelWidth + "px" : "") + '">';
    h += '<div class="rk-tl-corner">' + esc(b.labelHeader || "Workstream") + '</div><div class="rk-tl-axis">';
    ticks.forEach(function (k) {
      h += '<div class="rk-tl-tick' + (k.major ? " is-major" : "") + '" style="left:' + x(k.t).toFixed(3) + '%">' + esc(k.label) + (k.sub ? "<small>" + esc(k.sub) + "</small>" : "") + "</div>";
    });
    h += "</div>";
    var grid = ticks.map(function (k) { return '<div class="rk-tl-grid" style="left:' + x(k.t).toFixed(3) + '%"></div>'; }).join("");
    var lane = null, rowH = 40;
    (b.rows || []).forEach(function (r) {
      if (r.lane && r.lane !== lane) {
        lane = r.lane;
        var lg = self.groups[r.laneGroup || r.group];
        h += '<div class="rk-tl-lane"' + attr("data-g", r.laneGroup) + '><div' + attr("data-c", lg && lg.c) + ">" + (lg ? '<span class="rk-sw"></span>' : "") + esc(lane) + "</div><div></div></div>";
      }
      var bars = (r.bars || (r.start ? [{ id: r.id, start: r.start, end: r.end, label: r.barLabel || r.label, group: r.group, kind: r.kind, deps: r.deps }] : [])).slice();
      bars.sort(function (a, c) { return d(a.start) - d(c.start); });
      var tracks = [];
      bars.forEach(function (br) {
        var s = d(br.start), e = d(br.end) + DAY, k = 0;
        while (tracks[k] != null && tracks[k] > s) k++;
        tracks[k] = e; br._k = k;
      });
      var n = Math.max(tracks.length, 1), height = n * rowH + (r.milestones && r.milestones.length && bars.length ? 18 : 0);
      var g = self.groups[r.group];
      var heat = "";
      if (r.heat) {
        for (var q = 1; q <= 3; q++) heat += '<i class="' + (q <= r.heat.n ? "on" : "") + '"></i>';
        heat = '<span class="rk-heat"' + attr("data-tone", r.heat.tone || (r.heat.n >= 3 ? "crit" : r.heat.n === 2 ? "warn" : "good")) + ' title="' + esc(r.heat.title || "Risk heat " + r.heat.n + " of 3") + '" aria-label="' + esc(r.heat.title || "Risk heat " + r.heat.n + " of 3") + '">' + heat + "</span>";
      }
      var meta = heat + (r.owner !== undefined ? self.owner(r.owner) : "");
      h += '<div class="rk-tl-label" style="height:' + height + 'px"' + attr("data-g", r.group) + attr("data-id", r.id && !r.start ? r.id : null) + ">" +
        '<span class="rk-tl-line">' + (g ? '<span class="rk-sw"' + attr("data-c", g.c) + "></span>" : "") + '<span class="rk-tl-name" title="' + esc(r.label) + '">' + esc(r.label) + "</span>" + self.cites(r.cite) + "</span>" +
        (meta ? '<span class="rk-tl-meta">' + meta + "</span>" : "") + "</div>";
      h += '<div class="rk-tl-track" style="height:' + height + 'px">' + grid;
      bars.forEach(function (br) {
        var s = d(br.start), e = d(br.end) + DAY, bg = self.groups[br.group || r.group];
        var lab = br.label || r.label;
        var aria = lab + ", " + when(s) + (when(s) === when(e - DAY) ? "" : " to " + when(e - DAY)) + (bg ? ", " + bg.label : "") + (br.deps && br.deps.length ? ", after " + br.deps.join(", ") : "");
        h += '<div class="rk-tl-bar' + (br.kind ? " is-" + esc(br.kind) : "") + '" tabindex="0" role="img"' + attr("data-id", br.id) + attr("data-g", br.group || r.group) +
          attr("data-c", bg && bg.c) + attr("data-deps", (br.deps || []).join(" ")) + ' aria-label="' + esc(aria) + '" title="' + esc(aria) + '" style="left:' + x(s).toFixed(3) + "%;width:calc(" + (x(e) - x(s)).toFixed(3) + "% - 2px);top:" + (br._k * rowH + 6) + 'px">' + esc(lab) + "</div>";
      });
      (r.milestones || []).forEach(function (ms) {
        var mt = d(ms.date), top = bars.length ? n * rowH + 9 : rowH / 2;
        h += '<div class="rk-tl-ms' + (x(mt) > 72 ? " is-end" : "") + '" role="img" tabindex="0"' + attr("data-id", ms.id) + ' aria-label="' + esc("Milestone: " + ms.label + ", " + when(mt)) + '" style="left:' + x(mt).toFixed(3) + "%;top:" + top + 'px"><span>' + esc(ms.label) + " \u00b7 " + when(mt) + "</span></div>";
      });
      h += "</div>";
    });
    // vertical markers span the whole chart below the axis
    markers.forEach(function (mk) {
      h += '<div class="rk-tl-marker' + (mk.dashed ? " is-dashed" : "") + (x(d(mk.date)) > 85 ? " is-end" : "") + '"' + attr("data-tone", mk.tone || "crit") + ' style="left:calc(var(--rk-label-w, 240px) + (100% - var(--rk-label-w, 240px)) * ' + (x(d(mk.date)) / 100).toFixed(5) + ')"><span>' + esc(mk.label) + "</span></div>";
    });
    h += '<svg class="rk-tl-deps" aria-hidden="true" data-crit="' + esc((b.critical || []).join(" ")) + '"></svg>';
    return h + "</div></div>";
  };

  RK.prototype.drawDeps = function () {
    this.root.querySelectorAll(".rk-tl").forEach(function (tl) {
      var svg = tl.querySelector(".rk-tl-deps");
      if (!svg) return;
      var crit = (svg.getAttribute("data-crit") || "").split(" ").filter(Boolean);
      var box = tl.getBoundingClientRect();
      svg.setAttribute("width", tl.scrollWidth); svg.setAttribute("height", tl.scrollHeight);
      var out = '<defs><marker id="rk-ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z"/></marker>' +
        '<marker id="rk-ah-crit" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z"/></marker></defs>';
      tl.querySelectorAll(".rk-tl-bar[data-deps]").forEach(function (to) {
        to.getAttribute("data-deps").split(" ").filter(Boolean).forEach(function (fid) {
          var from = tl.querySelector('.rk-tl-bar[data-id="' + fid + '"]');
          if (!from) return;
          var a = from.getBoundingClientRect(), c = to.getBoundingClientRect();
          var x1 = a.right - box.left, y1 = a.top + a.height / 2 - box.top, x2 = c.left - box.left, y2 = c.top + c.height / 2 - box.top;
          var bend = Math.max(14, Math.min(40, Math.abs(x2 - x1) / 2));
          var isCrit = crit.indexOf(fid) > -1 && crit.indexOf(to.getAttribute("data-id")) > -1;
          var path = x2 >= x1 + 8
            ? "M" + x1 + "," + y1 + " C" + (x1 + bend) + "," + y1 + " " + (x2 - bend) + "," + y2 + " " + (x2 - 1) + "," + y2
            : "M" + x1 + "," + y1 + " h8 V" + ((y1 + y2) / 2) + " H" + (x2 - 10) + " V" + y2 + " H" + (x2 - 1);
          out += '<path class="' + (isCrit ? "is-crit" : "") + '" d="' + path + '" marker-end="url(#' + (isCrit ? "rk-ah-crit" : "rk-ah") + ')" data-from="' + esc(fid) + '"></path>';
        });
      });
      svg.innerHTML = out;
    });
  };

  /* ---------- matrix: phases (columns) x lanes (rows) ---------- */
  RK.prototype.b_matrix = function (b) {
    var self = this;
    this._n = 0;
    var h = '<div class="rk-matrix-wrap"><div class="rk-matrix" style="--rk-cols:' + b.columns.length + (b.labelWidth ? ";--rk-label-w:" + b.labelWidth + "px" : "") + '"><div class="rk-mx-corner"></div>';
    var heads = b.columns.map(function (c, ci) {
      var inner = "<h3>" + esc(c.title) + "</h3>" + (c.subtitle ? "<p>" + esc(c.subtitle) + "</p>" : "");
      if (c.meter) inner += self.meter(c.meter.label, c.meter.value, c.meter.max, c.meter);
      if (c.split) inner += self.splitBar(c.split);
      if (c.tags) inner += self.tags(c.tags);
      return '<div class="rk-mx-head"' + attr("data-tone", c.tone) + ' style="--o:' + ci * 1000 + '">' + inner + "</div>";
    });
    // desktop: header row then one row per lane. On mobile, CSS order (--o) regroups cells under their column head.
    h += heads.join("");
    b.rows.forEach(function (r, ri) {
      var g = self.groups[r.group];
      h += '<div class="rk-mx-row"' + attr("data-g", r.group) + attr("data-c", g && g.c) + ">" + (g ? '<span class="rk-sw" style="margin-top:4px"></span>' : "") + esc(r.label) + "</div>";
      b.columns.forEach(function (c, ci) {
        var cards = b.cards.filter(function (k) { return k.col === c.id && k.row === r.id; });
        h += '<div class="rk-mx-cell" data-row="' + esc(r.label) + '" style="--o:' + (ci * 1000 + ri + 1) + '">' + cards.map(function (k) { return self.card(k, { noGroup: k.group === r.group }); }).join("") + "</div>";
      });
    });
    return h + "</div></div>";
  };

  RK.prototype.splitBar = function (s) {
    var self = this, total = s.parts.reduce(function (a, p) { return a + p.value; }, 0) || 1;
    var bar = s.parts.map(function (p) {
      var g = self.groups[p.group];
      return '<div class="rk-meter-fill"' + attr("data-c", g && g.c) + attr("data-tone", p.tone) + ' style="width:' + ((p.value / total) * 100).toFixed(1) + '%"></div>';
    }).join("");
    var keys = s.parts.map(function (p) {
      var g = self.groups[p.group];
      return "<span" + attr("data-c", g && g.c) + attr("data-tone", p.tone) + '><span class="rk-sw" style="background:' + (g ? "var(--c)" : "var(--t)") + '"></span>' + esc(p.label || (g && g.label)) + ' <b class="rk-mono">' + esc(p.value) + (s.unit || "") + "</b></span>";
    }).join("");
    return '<div class="rk-meter">' + (s.label ? '<div class="rk-meter-label"><span>' + esc(s.label) + "</span></div>" : "") +
      '<div class="rk-meter-track" role="img" aria-label="' + esc((s.label || "Split") + ": " + s.parts.map(function (p) { return (p.label || p.group) + " " + p.value + (s.unit || ""); }).join(", ")) + '">' + bar + '</div><div class="rk-split-keys">' + keys + "</div></div>";
  };

  /* ---------- panels ---------- */
  RK.prototype.b_callouts = function (b) {
    var self = this;
    return '<div class="rk-callouts">' + b.items.map(function (it, k) {
      return '<div class="rk-callout"' + attr("data-tone", it.tone || "crit") + attr("data-ref", it.ref) + ' tabindex="0"><h4>' + (b.numbered !== false ? '<span class="rk-rank">' + (k + 1) + "</span>" : "") + esc(it.title) + self.cites(it.cite) + "</h4>" +
        (it.body ? "<p>" + esc(it.body) + "</p>" : "") + (it.meta ? '<p class="rk-mono" style="font-size:12px">' + esc(it.meta) + "</p>" : "") + "</div>";
    }).join("") + "</div>";
  };
  RK.prototype.b_meters = function (b) {
    var self = this;
    return '<div class="rk-splits">' + b.items.map(function (it) {
      var g = self.groups[it.group];
      var inner = it.parts ? self.splitBar(it) : self.meter(it.label, it.value, it.max, { unit: it.unit, tone: it.tone, c: g && g.c, flag: it.flag });
      return '<div class="rk-split"' + attr("data-g", it.group) + ">" + (it.parts && it.title ? '<b style="font-size:13px">' + esc(it.title) + "</b>" : "") + inner + (it.note ? '<p class="rk-note">' + esc(it.note) + "</p>" : "") + "</div>";
    }).join("") + "</div>";
  };
  RK.prototype.b_table = function (b) {
    var self = this;
    var h = '<div class="rk-table-wrap"><table class="rk-table"><thead><tr>' + b.columns.map(function (c) { return '<th scope="col">' + esc(c.label) + "</th>"; }).join("") + "</tr></thead><tbody>";
    b.rows.forEach(function (r) {
      var g = self.groups[r.group];
      h += "<tr" + attr("data-ref", r.ref) + attr("data-g", r.group) + attr("data-c", g && g.c) + ' tabindex="0">' + b.columns.map(function (c, ci) {
        var v = r[c.key], cite = ci === 0 ? self.cites(r.cite) : "";
        if (c.key === "owner") return "<td>" + self.owner(v) + "</td>";
        if (v && typeof v === "object") return '<td><span class="rk-tag"' + attr("data-tone", v.tone) + ">" + esc(v.t) + "</span>" + cite + "</td>";
        if (c.swatch && g) return '<td><span style="display:inline-flex;gap:6px;align-items:center"><span class="rk-sw"></span>' + esc(v) + cite + "</span></td>";
        return "<td>" + esc(v) + cite + "</td>";
      }).join("") + "</tr>";
    });
    return h + "</tbody></table></div>";
  };
  RK.prototype.b_checklist = function (b, i) {
    return '<ul class="rk-check">' + b.items.map(function (it, k) {
      var id = "rk-ck-" + i + "-" + k;
      return '<li><label for="' + id + '"><input type="checkbox" id="' + id + '"' + (it.done ? " checked" : "") + "><span>" + esc(it.t || it) + (it.owner ? ' <span class="rk-owner is-set">' + esc(it.owner) + "</span>" : "") + "</span></label></li>";
    }).join("") + "</ul>";
  };
  // One numbered evidence list that cite numbers link to. Item n gets the id citeHref + n without the "#".
  RK.prototype.b_evidence = function (b) {
    var pre = ((this.data.meta && this.data.meta.citeHref) || "#ev-").replace(/^#/, "");
    return (b.intro ? '<p class="rk-note">' + esc(b.intro) + "</p>" : "") + '<ol class="rk-evidence">' + b.items.map(function (it, k) {
      return '<li id="' + esc(pre + (k + 1)) + '">' + esc(typeof it === "string" ? it : it.t) + "</li>";
    }).join("") + "</ol>";
  };
  RK.prototype.b_text = function (b) {
    return [].concat(b.body).map(function (p) { return '<p class="rk-sub">' + esc(p) + "</p>"; }).join("");
  };

  /* ---------- behaviour ---------- */
  RK.prototype.toast = function (msg) {
    var t = this.root.querySelector(".rk-toast");
    if (t) { t.textContent = msg; clearTimeout(this._tt); this._tt = setTimeout(function () { t.textContent = ""; }, 2600); }
  };
  RK.prototype.positions = function () {
    var pos = {};
    (this.data.blocks || []).forEach(function (b) { if (b.type === "board") b.cards.forEach(function (c) { if (c.id) pos[c.id] = c.col; }); });
    return pos;
  };
  /* Replace parts of a block (used by rk-live.js). The patch becomes the new baseline for "Reset moves". */
  RK.prototype.setBlock = function (i, patch) {
    [this.data, this.src].forEach(function (D) { Object.keys(patch).forEach(function (k) { D.blocks[i][k] = JSON.parse(JSON.stringify(patch[k])); }); });
    var saved = this.data.id && this.data.persist !== false ? store("rk:" + this.data.id) : null;
    if (saved && saved.cards) this.applyPositions(saved.cards);
    this.render(); this.applyFilter();
  };
  /* Status pill for a block: {text, tone, action: {label, run}} or null. */
  RK.prototype.setLive = function (i, state) {
    if (state) this.live[i] = state; else delete this.live[i];
    var sec = this.root.querySelector('.rk-section[data-block="' + i + '"]');
    if (!sec) return;
    this.render(); this.applyFilter();
  };
  RK.prototype.setMeta = function (patch) {
    var D = this.data;
    D.meta = D.meta || {};
    Object.keys(patch).forEach(function (k) { D.meta[k] = patch[k]; });
    this.render(); this.applyFilter();
  };

  RK.prototype.move = function (bi, id, colId) {
    var b = this.data.blocks[bi], card = b.cards.filter(function (c) { return c.id === id; })[0];
    if (!card || card.col === colId) return;
    card.col = colId;
    if (this.data.id && this.data.persist !== false) store("rk:" + this.data.id, { cards: this.positions() });
    var col = b.columns.filter(function (c) { return c.id === colId; })[0];
    this.render();
    this.applyFilter();
    var el = this.root.querySelector('.rk-card[data-id="' + CSS.escape(id) + '"]');
    if (el) el.focus();
    this.toast("Moved \u201c" + card.title + "\u201d to " + (col ? col.title : colId));
  };
  RK.prototype.applyFilter = function () {
    var act = this.active;
    this.root.querySelectorAll("[data-g]").forEach(function (el) {
      if (el.classList.contains("rk-key")) return;
      el.classList.toggle("rk-dim", !!act && !act[el.getAttribute("data-g")]);
    });
    this.root.querySelectorAll(".rk-key[data-key]").forEach(function (k) { k.setAttribute("aria-pressed", !act || act[k.getAttribute("data-key")] ? "true" : "false"); });
  };
  RK.prototype.bind = function () {
    var self = this, R = this.root;
    R.querySelectorAll(".rk-key[data-key]").forEach(function (k) {
      k.addEventListener("click", function () {
        var key = k.getAttribute("data-key"), all = Object.keys(self.groups);
        if (!self.active) { self.active = {}; self.active[key] = true; }
        else if (self.active[key]) { delete self.active[key]; if (!Object.keys(self.active).length) self.active = null; }
        else { self.active[key] = true; if (Object.keys(self.active).length === all.length) self.active = null; }
        self.applyFilter();
      });
    });
    R.querySelectorAll("[data-live-act]").forEach(function (btn) {
      btn.addEventListener("click", function () { var lv = self.live[+btn.getAttribute("data-live-act")]; if (lv && lv.action) lv.action.run(); });
    });
    R.querySelectorAll("[data-mode]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        self.mode = MODES[btn.getAttribute("data-mode")] || "relaxed";
        if (self.data.id) store("rk-mode:" + self.data.id, self.mode);
        self.render(); self.applyFilter();
        var b2 = R.querySelector('[data-mode="' + self.mode + '"]'); if (b2) b2.focus();
      });
    });
    var copy = R.querySelector('[data-act="copy"]');
    if (copy) copy.addEventListener("click", function () {
      var txt = JSON.stringify(self.data, null, 2);
      var done = function () { self.toast("Plan JSON copied. Paste it back to the AI to update the plan."); };
      var fallback = function () {
        var ta = document.createElement("textarea"); ta.value = txt; ta.setAttribute("aria-label", "Plan JSON"); ta.style.cssText = "width:100%;height:200px;font:12px var(--rk-font-mono)";
        R.appendChild(ta); ta.focus(); ta.select(); self.toast("Copy blocked here. The JSON is selected at the bottom of the page.");
      };
      try { navigator.clipboard.writeText(txt).then(done, fallback); } catch (e) { fallback(); }
    });
    var reset = R.querySelector('[data-act="reset"]');
    if (reset) reset.addEventListener("click", function () {
      store("rk:" + self.data.id, { cards: {} });
      self.data = JSON.parse(JSON.stringify(self.src));
      self.render(); self.applyFilter(); self.toast("Board reset to the original plan.");
    });
    // board drag and move buttons
    R.querySelectorAll(".rk-board").forEach(function (board) {
      var bi = +board.getAttribute("data-board"), cols = board.querySelectorAll(".rk-col"), dragId = null;
      board.querySelectorAll(".rk-card").forEach(function (card) {
        var ci = +card.closest(".rk-col").getAttribute("data-ci");
        card.querySelectorAll("[data-mv]").forEach(function (btn) {
          var to = ci + +btn.getAttribute("data-mv");
          if (to < 0 || to >= cols.length) btn.disabled = true;
          btn.addEventListener("click", function (e) { e.stopPropagation(); self.move(bi, card.getAttribute("data-id"), cols[to].getAttribute("data-col")); });
        });
        card.addEventListener("dragstart", function (e) { dragId = card.getAttribute("data-id"); card.classList.add("is-dragging"); try { e.dataTransfer.setData("text/plain", dragId); } catch (x) {} });
        card.addEventListener("dragend", function () { card.classList.remove("is-dragging"); });
      });
      cols.forEach(function (col) {
        col.addEventListener("dragover", function (e) { e.preventDefault(); col.classList.add("is-over"); });
        col.addEventListener("dragleave", function () { col.classList.remove("is-over"); });
        col.addEventListener("drop", function (e) { e.preventDefault(); col.classList.remove("is-over"); if (dragId) self.move(bi, dragId, col.getAttribute("data-col")); });
      });
    });
    // linked highlight: data-ref <-> data-id, and dependency chains on bars
    function hot(el, on) {
      var ids = [];
      if (el.getAttribute("data-ref")) ids = el.getAttribute("data-ref").split(" ");
      if (el.getAttribute("data-id")) ids.push(el.getAttribute("data-id"));
      if (el.getAttribute("data-deps")) ids = ids.concat(el.getAttribute("data-deps").split(" "));
      ids.filter(Boolean).forEach(function (id) {
        R.querySelectorAll('[data-id="' + CSS.escape(id) + '"]').forEach(function (t) { if (t !== el) t.classList.toggle("rk-hot", on); });
        R.querySelectorAll("[data-ref]").forEach(function (t) { if (t !== el && t.getAttribute("data-ref").split(" ").indexOf(id) > -1) t.classList.toggle("rk-hot", on); });
      });
    }
    R.querySelectorAll("[data-ref], .rk-tl-bar[data-id], .rk-card[data-id]").forEach(function (el) {
      ["mouseenter", "focus"].forEach(function (ev) { el.addEventListener(ev, function () { hot(el, true); }); });
      ["mouseleave", "blur"].forEach(function (ev) { el.addEventListener(ev, function () { hot(el, false); }); });
    });
  };

  var instances = [], rt;
  function mount(data, root, opts) {
    opts = opts || {};
    if (!root.classList.contains("rk")) root.classList.add("rk");
    if (opts.theme && opts.theme !== "auto") root.setAttribute("data-rk-theme", opts.theme);
    if (opts.embed) root.classList.add("rk-embed");
    var rk = new RK(data, root);
    if (opts.mode && MODES[opts.mode]) rk.mode = MODES[opts.mode];
    if (opts.corners) rk.corners = opts.corners;
    if (opts.modeSwitch) {
      rk.modeSwitch = true;
      var saved = data.id ? store("rk-mode:" + data.id) : null;
      if (saved && MODES[saved]) rk.mode = MODES[saved];
    }
    if (opts.parts) Object.keys(rk.parts).forEach(function (k) { rk.parts[k] = opts.parts.indexOf(k) > -1; });
    instances = instances.filter(function (x) { return x.root !== root && document.contains(x.root); });
    instances.push(rk);
    rk.render();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { rk.drawDeps(); });
    if (opts.live !== false && data.live && data.live.length && window.RoadmapKit.attachLive) window.RoadmapKit.attachLive(rk);
    return rk;
  }
  window.addEventListener("resize", function () {
    clearTimeout(rt);
    rt = setTimeout(function () { instances.forEach(function (x) { x.drawDeps(); }); }, 120);
  });
  window.RoadmapKit = window.RoadmapKit || {};
  window.RoadmapKit.version = 3;
  window.RoadmapKit.mount = mount;
  window.RoadmapKit.instances = function () { return instances.slice(); };
  window.RoadmapKit.escape = esc;
  /* Building blocks as HTML strings, for pages that place single elements (a tag, a meter, a card) themselves. */
  window.RoadmapKit.html = function (legend) {
    var rk = new RK({ legend: legend || { items: [] }, blocks: [], persist: false }, document.createElement("div"));
    return {
      tags: function (t) { return rk.tags(t); },
      owner: function (o) { return rk.owner(o); },
      fields: function (f) { return rk.fields(f); },
      meter: function (label, value, max, o) { return rk.meter(label, value, max, o); },
      split: function (s) { return rk.splitBar(s); },
      card: function (c, o) { return rk.card(c, o); }
    };
  };

  function fail(root, msg) { root.innerHTML = '<p class="rk-error" role="alert">' + esc(msg) + "</p>"; }

  /* <rk-roadmap src="plan.json" theme="auto|light|dark" live="off"> */
  if (window.customElements && !customElements.get("rk-roadmap")) {
    customElements.define("rk-roadmap", class extends HTMLElement {
      connectedCallback() {
        if (this._mounted) return;
        this._mounted = true;
        var el = this, inline = this.querySelector('script[type="application/json"]');
        var root = document.createElement("main");
        root.className = "rk";
        root.setAttribute("aria-label", this.getAttribute("label") || "Roadmap");
        var go = function (data) {
          el.appendChild(root);
          mount(data, root, { theme: el.getAttribute("theme"), mode: el.getAttribute("mode"), corners: el.getAttribute("corners"), live: el.getAttribute("live") !== "off" });
          if (data.meta && data.meta.title && !el.getAttribute("label")) root.setAttribute("aria-label", data.meta.title);
        };
        if (inline) {
          try { go(JSON.parse(inline.textContent)); } catch (e) { el.appendChild(root); fail(root, "The roadmap data is not valid JSON: " + e.message); }
          return;
        }
        var src = this.getAttribute("src");
        if (!src) { el.appendChild(root); fail(root, "This roadmap has no data: add a src attribute or an inline JSON script."); return; }
        fetch(src).then(function (r) { if (!r.ok) throw new Error(r.status + " " + r.statusText); return r.json(); })
          .then(go)
          .catch(function (e) { el.appendChild(root); fail(root, "Could not load " + src + ": " + e.message); });
      }
    });
  }

  function boot() {
    var src = document.getElementById("rk-data"), root = document.getElementById("rk-root");
    if (!src || !root) return;
    var data;
    try { data = JSON.parse(src.textContent); }
    catch (e) { fail(root, "The plan data is not valid JSON: " + e.message); return; }
    mount(data, root);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
