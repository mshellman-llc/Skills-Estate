/* Roadmap Kit v2 live bindings. Load after rk.js. Optional: without it, or outside a claude.ai Artifact
   that declares the `mcp` capability, the plan renders from its snapshot data.
   Each entry in plan.live watches one read tool on the viewer's connector and maps its result into one block.
   Binding schema and connector recipes: references/connectors.md */
(function () {
  "use strict";
  var RKG = window.RoadmapKit = window.RoadmapKit || {};

  /* ---------- mapping (pure; also used by tests) ---------- */
  function get(obj, path) {
    if (path == null || path === "") return obj;
    var parts = String(path).replace(/\[(\d+)\]/g, ".$1").split(".");
    for (var i = 0; i < parts.length; i++) {
      if (obj == null) return undefined;
      if (Array.isArray(obj) && !/^\d+$/.test(parts[i])) {
        // path through an array: collect from every element (e.g. "labels.nodes.name")
        var rest = parts.slice(i).join(".");
        return obj.map(function (x) { return get(x, rest); }).filter(function (x) { return x != null; });
      }
      obj = obj[parts[i]];
    }
    return obj;
  }
  function toRecords(payload, b) {
    var arr = get(payload, b.items);
    if (typeof arr === "string") { try { arr = JSON.parse(arr); } catch (e) { arr = null; } }
    if (!Array.isArray(arr)) throw { code: "mapping", message: "No list found at items path \"" + (b.items || "") + "\"." };
    if (b.format === "rows") {
      var header = (arr[0] || []).map(function (h) { return String(h).trim(); });
      return arr.slice(1).filter(function (r) { return r && r.some(function (c) { return c !== "" && c != null; }); }).map(function (r) {
        var o = {};
        header.forEach(function (h, k) { o[h] = r[k] == null ? "" : r[k]; });
        return o;
      });
    }
    return arr;
  }
  function val(rec, spec) {
    if (spec == null) return undefined;
    if (typeof spec === "object" && "const" in spec) return spec["const"];
    return get(rec, spec);
  }
  function date(v) {
    if (!v) return null;
    var s = String(v).trim();
    if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10);
    var t = Date.parse(s);
    return isNaN(t) ? null : new Date(t).toISOString().slice(0, 10);
  }
  function list(v) {
    if (v == null || v === "") return [];
    if (Array.isArray(v)) return v.map(String);
    return String(v).split(/[,;]\s*/).filter(Boolean);
  }
  function lookup(table, v, fallback) {
    if (!table) return v == null ? fallback : v;
    var k = v == null ? "" : String(v);
    if (Object.prototype.hasOwnProperty.call(table, k)) return table[k];
    var lower = k.toLowerCase();
    for (var key in table) if (key.toLowerCase() === lower) return table[key];
    return Object.prototype.hasOwnProperty.call(table, "*") ? table["*"] : fallback;
  }

  /* Map records into a block patch. Returns {patch, used, skipped}. */
  function mapBinding(payload, b, block) {
    var recs = toRecords(payload, b), m = b.map || {}, vm = b.values || {}, skipped = 0, out = [];
    var limit = b.limit || 200;
    recs.forEach(function (r) {
      if (out.length >= limit) { skipped++; return; }
      var o = {
        id: val(r, m.id), title: val(r, m.title), body: val(r, m.body), owner: val(r, m.owner),
        group: lookup(vm.group, val(r, m.group), b.defaults && b.defaults.group),
        col: lookup(vm.col, val(r, m.col), b.defaults && b.defaults.col),
        row: lookup(vm.row, val(r, m.row), b.defaults && b.defaults.row),
        points: val(r, m.points), start: date(val(r, m.start)), end: date(val(r, m.end)),
        deps: list(val(r, m.deps)), url: val(r, m.url), kicker: val(r, m.kicker),
        lane: m.lane ? lookup(vm.lane, val(r, m.lane), "Other") : null
      };
      if (o.id == null || o.title == null || o.title === "") { skipped++; return; }
      o.id = String(o.id);
      if (m.fields) {
        o.fields = [];
        Object.keys(m.fields).forEach(function (label) { var v = val(r, m.fields[label]); if (v != null && v !== "") o.fields.push([label, String(v)]); });
      }
      if (m.tags) {
        o.tags = [];
        m.tags.forEach(function (t) {
          [].concat(val(r, t.path) || []).forEach(function (v) {
            if (v === "" || v == null) return;
            var tone = t.tones ? lookup(t.tones, v, t.tone) : t.tone;
            o.tags.push(tone ? { t: (t.prefix || "") + v, tone: tone } : (t.prefix || "") + v);
          });
        });
      }
      out.push(o);
    });

    if (block.type === "board" || block.type === "matrix") {
      var cols = (block.columns || []).map(function (c) { return c.id; });
      var rows = block.type === "matrix" ? (block.rows || []).map(function (x) { return x.id; }) : null;
      var cards = [];
      out.forEach(function (o) {
        if (cols.indexOf(o.col) < 0 || (rows && rows.indexOf(o.row) < 0)) { skipped++; return; }
        var c = { id: o.id, col: o.col, title: String(o.title) };
        if (rows) c.row = o.row;
        if (o.group != null) c.group = o.group;
        if (o.body) c.body = String(o.body);
        if (o.kicker) c.kicker = String(o.kicker);
        c.owner = o.owner ? String(o.owner) : "TBD";
        if (o.points != null && o.points !== "") { c.points = +o.points; if (!o.tags || !m.tags) c.tags = [c.points + (block.unit ? " " + block.unit : "")]; }
        if (o.fields && o.fields.length) c.fields = o.fields;
        if (o.tags && o.tags.length) c.tags = (c.tags || []).concat(o.tags);
        cards.push(c);
      });
      return { patch: { cards: cards }, used: cards.length, skipped: skipped };
    }
    if (block.type === "timeline") {
      var tl = [], min = null, max = null;
      out.forEach(function (o) {
        if (!o.start || !o.end) { skipped++; return; }
        if (o.end < o.start) { var t = o.start; o.start = o.end; o.end = t; }
        var row = { id: o.id, label: String(o.title), start: o.start, end: o.end };
        if (o.group != null) row.group = o.group;
        if (o.owner !== undefined) row.owner = o.owner ? String(o.owner) : "TBD";
        if (o.deps.length) row.deps = o.deps;
        if (o.lane != null) row.lane = String(o.lane);
        tl.push(row);
        if (!min || o.start < min) min = o.start;
        if (!max || o.end > max) max = o.end;
      });
      var ids = tl.map(function (x) { return x.id; });
      tl.forEach(function (x) { if (x.deps) { x.deps = x.deps.filter(function (d) { return ids.indexOf(d) > -1; }); if (!x.deps.length) delete x.deps; } });
      if (b.sort !== false) tl.sort(function (a, c) { return (a.lane || "").localeCompare(c.lane || "") || a.start.localeCompare(c.start); });
      var patch = { rows: tl };
      if (b.autoRange !== false && min) {
        patch.start = block.start && block.start < min ? block.start : min;
        patch.end = block.end && block.end > max ? block.end : max;
      } else {
        tl = tl.filter(function (x) { return x.start >= block.start && x.end <= block.end; });
        patch.rows = tl;
      }
      return { patch: patch, used: tl.length, skipped: skipped };
    }
    if (block.type === "table") {
      var cols2 = (block.columns || []).map(function (c) { return c.key; });
      var trs = recs.slice(0, limit).map(function (r) {
        var row = {};
        cols2.forEach(function (k) { if (m[k] != null) row[k] = val(r, m[k]); });
        return row;
      });
      return { patch: { rows: trs }, used: trs.length, skipped: Math.max(0, recs.length - limit) };
    }
    throw { code: "mapping", message: "Live data can fill board, matrix, timeline or table blocks, not " + block.type + "." };
  }

  RKG.mapBinding = mapBinding;

  /* ---------- connector wiring ---------- */
  function ago(ms) {
    var s = Math.round((Date.now() - ms) / 1000);
    if (s < 60) return "just now";
    if (s < 3600) return Math.round(s / 60) + " min ago";
    if (s < 86400) return Math.round(s / 3600) + " h ago";
    return new Date(ms).toISOString().slice(0, 10);
  }
  var FIX = {
    needs_reauth: function (sv) { return "Reconnect " + sv + " in claude.ai Settings \u2192 Connectors"; },
    server_not_connected: function (sv) { return "Add " + sv + " in claude.ai Settings \u2192 Connectors to see live data"; },
    selection_required: function (sv) { return "Choose which " + sv + " connector to use when claude.ai asks"; },
    server_not_found: function (sv) { return sv + " is no longer available"; },
    not_in_manifest: function (sv) { return sv + " is not allowed for this page"; },
    blocked_by_policy: function (sv) { return "Your organization blocks " + sv + " here"; }
  };
  var RETRACT = { needs_reauth: 1, server_not_connected: 1, selection_required: 1, server_not_found: 1, not_in_manifest: 1, blocked_by_policy: 1, approval_required: 1 };

  function attach(rk) {
    if (rk._liveAttached) return;
    rk._liveAttached = true;
    var plan = rk.data, bindings = plan.live || [];
    var snapLabel = plan.meta && plan.meta.updated ? "Snapshot " + plan.meta.updated : "Snapshot";
    bindings.forEach(function (b) { rk.live[b.block] = { text: snapLabel + " \u00b7 connecting to " + b.server, tone: "muted" }; });
    rk.render();
    if (!window.claude || typeof window.claude.use !== "function") {
      bindings.forEach(function (b) { rk.live[b.block] = { text: snapLabel + " from " + b.server, tone: "muted" }; });
      rk.render(); rk.applyFilter();
      return;
    }
    window.claude.use("mcp").then(function (mcp) {
      if (!mcp) {
        bindings.forEach(function (b) { rk.setLive(b.block, { text: snapLabel + " from " + b.server + " \u00b7 live data needs claude.ai", tone: "muted" }); });
        return;
      }
      bindings.forEach(function (b) { watch(rk, mcp, b, snapLabel); });
    });
  }

  function watch(rk, mcp, b, snapLabel) {
    var snapshot = JSON.parse(JSON.stringify(rk.src.blocks[b.block])), lastGood = null, retried = false;
    function apply(result) {
      var block = rk.src.blocks[b.block];
      try {
        var res = mapBinding(result.payload, b, block);
        rk.setBlock(b.block, res.patch);
        var when = result.cache && result.cache.storedAt ? result.cache.storedAt : Date.now();
        lastGood = when;
        rk.setLive(b.block, { text: "Live \u00b7 " + b.server + " \u00b7 " + ago(when) + (res.skipped ? " \u00b7 " + res.skipped + " not shown" : ""), tone: "good" });
      } catch (e) {
        rk.setLive(b.block, { text: (lastGood ? "Showing " + b.server + " data from " + ago(lastGood) : snapLabel) + " \u00b7 " + (e.message || "the data didn't match this roadmap"), tone: "warn" });
      }
    }
    function restoreSnapshot() {
      var patch = {};
      ["cards", "rows", "start", "end"].forEach(function (k) { if (snapshot[k] !== undefined) patch[k] = snapshot[k]; });
      rk.setBlock(b.block, patch);
      lastGood = null;
    }
    function onErr(err) {
      var code = err && err.code, sv = b.server;
      if (code === "not_granted" || code === "capability_disabled" || code === "capability_removed") {
        rk.setLive(b.block, { text: snapLabel + " from " + sv, tone: "muted" }); return;
      }
      if (code === "approval_required") {
        restoreSnapshot();
        rk.setLive(b.block, { text: snapLabel + " \u00b7 " + sv + " needs your approval", tone: "warn", action: { label: "Allow " + sv, run: function () {
          mcp.callTool(sv, b.tool, b.input == null ? null : b.input).then(apply, onErr);
        } } });
        return;
      }
      if (RETRACT[code]) { restoreSnapshot(); rk.setLive(b.block, { text: snapLabel + " \u00b7 " + FIX[code](sv), tone: "warn" }); return; }
      if (err && err.retryable && !retried) {
        retried = true;
        setTimeout(function () { mcp.callTool(sv, b.tool, b.input == null ? null : b.input).then(apply, onErr); }, (err.retryAfterMs || 1500) + Math.random() * 1000);
      }
      var msg = code === "tool_error" ? sv + " reported: " + (err.message || "an error") : "Couldn't refresh from " + sv;
      rk.setLive(b.block, { text: (lastGood ? "Showing data from " + ago(lastGood) : snapLabel) + " \u00b7 " + msg, tone: "warn" });
    }
    var unsub = mcp.watchTool(b.server, b.tool, b.input == null ? null : b.input, function (ev) {
      if (ev.type === "data") apply(ev.result); else onErr(ev.error);
    }, { refetchInterval: Math.max(b.refetch || 300000, 30000) });
    rk._unsubs = (rk._unsubs || []).concat(unsub);
  }

  RKG.attachLive = attach;
  // instances mounted before this file loaded
  if (RKG.instances) RKG.instances().forEach(function (rk) { if (rk.data.live && rk.data.live.length) attach(rk); });
})();
