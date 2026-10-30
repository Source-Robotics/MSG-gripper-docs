/* The force and speed calculator on the Force and speed page: the page's own formulas, with the reader's numbers.
   The constants come from the element's data attributes, so another gripper reuses the script with its own; an
   optional stepper select (value = newtons per ampere, data-max-ma = the slider's maximum) and rail select
   (value = the stroke in mm) switch them, as on the MSG gripper's page. */
(function () {
  function setup() {
    document.querySelectorAll(".gripper-calc").forEach(function (el) {
      if (el.dataset.ready) return;
      el.dataset.ready = "1";
      var kNA = parseFloat(el.dataset.newtonsPerAmp);
      var r = parseFloat(el.dataset.radiusMm) / 1000;
      var tMin = parseFloat(el.dataset.ticksMin), tMax = parseFloat(el.dataset.ticksMax);
      var tRev = parseFloat(el.dataset.ticksPerRev), stroke = parseFloat(el.dataset.strokeMm);
      var q = function (n) { return el.querySelector("[name=" + n + "]"); };
      var out = function (n, v) { var o = el.querySelector("[data-out=" + n + "]"); if (o) o.textContent = v; };
      var I = q("current"), mu = q("mu"), S = q("safety"), C = q("speed"), stepper = q("stepper"), rail = q("rail");
      function constants() {
        if (stepper) {
          var o = stepper.options[stepper.selectedIndex];
          kNA = parseFloat(o.value);
          if (o.dataset.maxMa) { I.max = o.dataset.maxMa; if (+I.value > +o.dataset.maxMa) I.value = o.dataset.maxMa; }
        }
        if (rail) stroke = parseFloat(rail.value);
      }
      function update() {
        constants();
        var amps = I.value / 1000, F = kNA * amps;
        var W = 2 * parseFloat(mu.value || 0) * F / parseFloat(S.value || 1);
        out("current", I.value + " mA");
        out("force", F.toFixed(F < 10 ? 1 : 0) + " N");
        out("payload", (W / 9.81).toFixed(2) + " kg");
        var ticks = tMin + (tMax - tMin) / 255 * C.value;
        var v = ticks / tRev * 2 * Math.PI * r * 1000;     /* mm/s per jaw */
        out("speedbyte", C.value);
        out("jaw", v.toFixed(v < 10 ? 1 : 0) + " mm/s");
        out("closing", (2 * v).toFixed(2 * v < 10 ? 1 : 0) + " mm/s");
        out("stroke", (stroke / (2 * v)).toFixed(2 * v > 50 ? 2 : 1) + " s");
      }
      [I, mu, S, C].forEach(function (x) { x.addEventListener("input", update); });
      [stepper, rail].forEach(function (x) { if (x) x.addEventListener("change", update); });
      update();
    });
  }
  if (window.document$ && window.document$.subscribe) { window.document$.subscribe(setup); }
  else if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", setup); }
  else { setup(); }
})();
