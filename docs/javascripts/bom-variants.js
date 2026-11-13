/* The version selector on the Bill of materials page (owner, 2026-11-13): pick the rail, the stepper and the
   camera, and the list keeps only the rows that version needs (one motor and its screws, the camera only with a
   camera), marks the rail length to buy, and says which 3MF files to print. The data is docs/includes/bom-variants.yml,
   which tools/sync_bom.py writes into the page's .bom-variants element. A choice clicked again is cleared; with
   nothing chosen the page is the whole BOM. ?rail=150&stepper=40&camera=without in the address chooses a version.
   The choice is remembered in this browser only. Without JavaScript, and in print, the page is the plain BOM. */
(function () {
  var KEY = "msg-bom-version";

  function remembered() { try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; } }
  function remember(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* private window */ } }
  function text(el) {
    var c = el.cloneNode(true);
    c.querySelectorAll(".headerlink, .bom-variants__pick").forEach(function (a) { a.remove(); });
    return c.textContent.replace(/\s+/g, " ").trim();
  }
  function el(tag, cls, words) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (words) e.textContent = words;
    return e;
  }
  function list(words) {
    return words.length < 2 ? words.join("") : words.slice(0, -1).join(", ") + " and " + words[words.length - 1];
  }

  function setup() {
    var box = document.querySelector(".bom-variants[data-variants]");
    if (!box || box.dataset.ready || box.closest("#print-site-page")) return;
    var data;
    try { data = JSON.parse(box.dataset.variants); } catch (e) { return; }
    box.dataset.ready = "1";
    var choices = data.choices, keys = Object.keys(choices);

    // every row of every table after the box, with its section
    var rows = [], section = "";
    for (var n = box.nextElementSibling; n; n = n.nextElementSibling) {
      if (n.tagName === "H2") { section = text(n); continue; }
      var table = n.tagName === "TABLE" ? n : n.querySelector("table");
      if (!table || !table.tBodies.length) continue;
      Array.prototype.forEach.call(table.tBodies[0].rows, function (tr) {
        rows.push({ tr: tr, section: section, first: text(tr.cells[0]),
                    all: Array.prototype.map.call(tr.cells, text).join(" | ") });
      });
    }
    // the rows each entry names (sync_bom.py has checked that each names exactly one)
    var named = [];
    (data.rows || []).forEach(function (e) {
      rows.forEach(function (r) {
        if (r.section === e.section && r.first === e.first && (!e.has || r.all.indexOf(e.has) >= 0)) named.push({ e: e, r: r });
      });
    });

    // the buttons: one group per choice, and a button for the whole list
    var state = {};
    var panel = el("div", "bom-variants__panel");
    panel.appendChild(el("p", "bom-variants__q", "Which version do you build?"));
    var buttons = [];
    keys.forEach(function (k) {
      var group = el("div", "bom-variants__group");
      group.setAttribute("role", "group");
      group.setAttribute("aria-label", choices[k].label);
      group.appendChild(el("span", "bom-variants__label", choices[k].label));
      // numbers in ascending order: a browser lists whole-number keys ("40") before the others ("21.5")
      var values = Object.keys(choices[k].options);
      if (values.every(function (v) { return !isNaN(parseFloat(v)); })) {
        values.sort(function (a, b) { return parseFloat(a) - parseFloat(b); });
      }
      values.forEach(function (v) {
        var o = choices[k].options[v];
        var b = el("button", "md-button", o.label);
        b.type = "button";
        b.dataset.choice = k;
        b.dataset.value = v;
        if (o.detail) b.title = o.detail;
        b.addEventListener("click", function () {
          state[k] = state[k] === v ? "" : v;
          remember(state);
          apply();
        });
        group.appendChild(b);
        buttons.push(b);
      });
      panel.appendChild(group);
    });
    var reset = el("button", "bom-variants__reset", "Show the whole list");
    reset.type = "button";
    reset.addEventListener("click", function () { state = {}; remember(state); apply(); });
    var summary = el("div", "bom-variants__summary");
    summary.hidden = true;
    box.appendChild(panel);
    box.appendChild(summary);

    function apply() {
      buttons.forEach(function (b) {
        var on = state[b.dataset.choice] === b.dataset.value;
        b.classList.toggle("md-button--primary", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      var hidden = 0;
      named.forEach(function (x) {
        var e = x.e, tr = x.r.tr, need = true;
        Object.keys(e.only || {}).forEach(function (k) {
          if (state[k] && e.only[k].indexOf(state[k]) < 0) need = false;
        });
        tr.classList.toggle("bom-variants__off", !need);
        if (!need) hidden += 1;
        tr.cells[0].querySelectorAll(".bom-variants__pick").forEach(function (s) { s.remove(); });
        Object.keys(e.note || {}).forEach(function (k) {
          var word = state[k] && e.note[k][state[k]];
          if (word) tr.cells[0].appendChild(el("span", "bom-variants__pick", word));
        });
      });

      var chosen = keys.filter(function (k) { return state[k]; });
      summary.hidden = !chosen.length;
      summary.innerHTML = "";
      if (!chosen.length) return;
      // "the 150 mm rail (105 mm stroke) and the 40 mm stepper (...), without a camera"
      var named_ = [], phrases = [];
      chosen.forEach(function (k) {
        var o = choices[k].options[state[k]];
        if (o.phrase) phrases.push(o.phrase);
        else named_.push("the " + o.label + " " + choices[k].label.toLowerCase() + (o.detail ? " (" + o.detail + ")" : ""));
      });
      var words = [list(named_)].concat(phrases).filter(Boolean).join(", ");
      var line = el("p", "", "");
      line.appendChild(el("strong", "", "Your version: "));
      line.appendChild(document.createTextNode(words + ". "));
      line.appendChild(document.createTextNode(hidden
        ? "The list below leaves out " + hidden + (hidden === 1 ? " row" : " rows") + " it does not need. "
        : "Every row below is needed. "));
      reset.remove();
      line.appendChild(reset);
      summary.appendChild(line);

      var p = data.print || {}, files = (p.common || []).slice();
      ["rail", "stepper"].forEach(function (k) { if (state[k] && p[k]) files = files.concat(p[k][state[k]] || []); });
      var print = el("p", "", "");
      print.appendChild(el("strong", "", "Print: "));
      print.appendChild(document.createTextNode(list(files.map(function (f) { return f + ".3mf"; }))));
      print.appendChild(document.createTextNode(", from "));
      var a = el("a", "", "Print files");
      a.href = p.url;
      print.appendChild(a);
      print.appendChild(document.createTextNode("."));
      var missing = ["rail", "stepper"].filter(function (k) { return !state[k]; });
      if (missing.length) print.appendChild(document.createTextNode(" Choose the " + list(missing) + " for the rest."));
      if (state.camera === "without" && p["without camera"]) {
        print.appendChild(document.createTextNode(" Without a camera: " + p["without camera"] + "."));
      }
      summary.appendChild(print);
    }

    // ?rail=150&stepper=40&camera=without in the address wins over the remembered choice
    var asked = {}, any = false;
    try {
      var q = new URLSearchParams(window.location.search);
      keys.forEach(function (k) { var v = q.get(k); if (v !== null && choices[k].options[v]) { asked[k] = v; any = true; } });
    } catch (e) { any = false; }
    state = any ? asked : remembered();
    keys.forEach(function (k) { if (state[k] && !choices[k].options[state[k]]) state[k] = ""; });
    if (any) remember(state);
    apply();
  }

  if (window.document$ && window.document$.subscribe) { window.document$.subscribe(setup); }
  else if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", setup); }
  else { setup(); }
})();
