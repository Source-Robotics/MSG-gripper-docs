/* Offline CAN frame builder/decoder. Layouts are generated from this release's
   reference data. No ports, adapters, network control, or hardware access. */
(function (root, factory) {
  var codec = factory();
  if (typeof module === "object" && module.exports) module.exports = codec;
  if (typeof document === "undefined") return;

  function setup() {
    document.querySelectorAll(".can-tool").forEach(function (el) {
      if (el.dataset.ready) return;
      el.dataset.ready = "1";
      var status = el.querySelector(".can-tool__status");
      fetch(new URL(el.dataset.schema, document.baseURI)).then(function (response) {
        if (!response.ok) throw new Error("Command definitions could not be loaded (" + response.status + ")");
        return response.json();
      }).then(function (schema) { init(el, schema, status); }).catch(function (error) {
        status.textContent = error.message + ". Reload the page or use the reference tables.";
      });
    });
  }

  function init(el, schema, status) {
    var q = function (name) { return el.querySelector('[name="' + name + '"]'); };
    var options = [], command = q("command"), fields = el.querySelector(".can-tool__fields");
    var built = el.querySelector(".can-tool__built"), decoded = el.querySelector(".can-tool__decoded");
    var lastFrame = null;
    status.textContent = schema.product + " · firmware " + schema.firmware + " · 1 Mbit/s · big-endian. Works offline after loading.";
    schema.commands.slice().sort(function (a, b) { return a.id - b.id; }).forEach(function (c) {
      c.forms.forEach(function (form) {
        var option = document.createElement("option");
        option.value = options.length;
        option.textContent = c.name + " · " + form.title + " · " + (form.remote ? "RTR" : form.length + " bytes") + " · " + (form.direction === "host" ? "host → driver" : "driver → host");
        options.push({command: c, form: form});
        command.appendChild(option);
      });
    });
    var initial = options.findIndex(function (item) { return item.command.key === "IN_GRIPPER_DATA_PACK" && item.form.length === 5; });
    command.value = String(Math.max(0, initial));

    function selected() { return options[Number(command.value)]; }
    function renderFields() {
      fields.replaceChildren();
      var form = selected().form;
      q("error").disabled = form.direction !== "driver";
      if (q("error").disabled) q("error").checked = false;
      form.fields.forEach(function (f, i) {
        var label = document.createElement("label"), input = document.createElement("input"), hint = document.createElement("small");
        label.htmlFor = "ct-field-" + i;
        label.textContent = f.name;
        input.id = label.htmlFor;
        input.name = "field-" + i;
        input.type = "number";
        input.step = f.float ? "any" : "1";
        if (!f.float) {
          input.min = f.signed ? -Math.pow(2, f.width - 1) : 0;
          input.max = Math.pow(2, f.width - (f.signed ? 1 : 0)) - 1;
        }
        var defaults = {Position: 200, Speed: 30, Current: 300, Activate: 1, Action: 1};
        input.value = defaults[f.name] === undefined ? "0" : String(defaults[f.name]);
        hint.textContent = f.meaning;
        fields.append(label, input, hint);
      });
      build();
    }

    function build() {
      lastFrame = null;
      try {
        var nodeText = q("node").value, node = Number(nodeText), item = selected(), form = item.form;
        if (!nodeText.trim() || !Number.isInteger(node) || node < 0 || node > 13) throw new Error("Choose a node ID from 0 to 13; 14 and 15 are reserved for updates.");
        var values = form.fields.map(function (_, i) { return q("field-" + i).value; });
        var payload = codec.encodeFields(form, values);
        var id = (node << 7) | (item.command.id << 1) | (form.direction === "driver" && q("error").checked ? 1 : 0);
        lastFrame = {id: id, data: payload, remote: form.remote};
        built.textContent = "ID " + codec.hexId(id) + " · " + (form.remote ? "RTR" : "DLC " + payload.length) + "\n" + (payload.length ? codec.hexBytes(payload) : "(no data bytes)");
      } catch (error) { built.textContent = error.message; }
      q("use").disabled = !lastFrame;
    }

    function decode() {
      decoded.replaceChildren();
      try {
        var result = codec.decodeFrame(schema, codec.parseIdentifier(q("identifier").value), codec.parseBytes(q("data").value), q("remote").checked);
        var summary = document.createElement("p");
        summary.textContent = "Node " + result.node + " · command " + result.command.id + " (" + result.command.name + ") · " + result.form.title + " · error bit " + result.error;
        decoded.appendChild(summary);
        if (result.node > 13) {
          var warning = document.createElement("p");
          warning.textContent = "Node 14 or 15 is accepted by the firmware but reserved by the bootloader; use nodes 0–13 for devices that need CAN updates.";
          decoded.appendChild(warning);
        }
        if (result.form.direction === "host" && result.error) {
          var note = document.createElement("p");
          note.textContent = "The firmware ignores the error bit in a host command.";
          decoded.appendChild(note);
        }
        var table = document.createElement("table"), head = document.createElement("thead"), body = document.createElement("tbody"), row = document.createElement("tr");
        ["Field", "Value", "Meaning"].forEach(function (title) { var th = document.createElement("th"); th.textContent = title; row.appendChild(th); });
        head.appendChild(row);
        result.values.forEach(function (value, i) {
          var tr = document.createElement("tr");
          [result.form.fields[i].name, String(value), result.form.fields[i].meaning].forEach(function (text) { var td = document.createElement("td"); td.textContent = text; tr.appendChild(td); });
          body.appendChild(tr);
        });
        if (result.values.length) { table.append(head, body); decoded.appendChild(table); }
        else { var empty = document.createElement("p"); empty.textContent = "This frame carries no fields."; decoded.appendChild(empty); }
      } catch (error) { decoded.textContent = error.message; }
    }
    command.addEventListener("change", renderFields);
    q("node").addEventListener("input", build);
    q("error").addEventListener("change", build);
    fields.addEventListener("input", build);
    q("build").addEventListener("click", build);
    q("decode").addEventListener("click", decode);
    q("use").addEventListener("click", function () {
      if (!lastFrame) return;
      q("identifier").value = codec.hexId(lastFrame.id);
      q("data").value = codec.hexBytes(lastFrame.data);
      q("remote").checked = lastFrame.remote;
      decode();
    });
    renderFields();
    decode();
  }

  if (root.document$ && root.document$.subscribe) root.document$.subscribe(setup);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setup);
  else setup();
})(typeof window !== "undefined" ? window : this, function () {
  "use strict";
  function numeric(field, text) {
    if (typeof text === "string" && !text.trim()) throw new Error(field.name + ": enter a value.");
    var value = Number(text);
    if (!Number.isFinite(value)) throw new Error(field.name + ": enter a finite number.");
    if (!field.float) {
      var min = field.signed ? -Math.pow(2, field.width - 1) : 0;
      var max = Math.pow(2, field.width - (field.signed ? 1 : 0)) - 1;
      if (!Number.isInteger(value) || value < min || value > max) throw new Error(field.name + ": enter an integer from " + min + " to " + max + ".");
    }
    return value;
  }
  function encodeFields(form, values) {
    if (values.length !== form.fields.length) throw new Error("Every field needs a value.");
    var data = new Uint8Array(form.length), view = new DataView(data.buffer);
    form.fields.forEach(function (field, index) {
      var value = numeric(field, values[index]);
      if (field.bits) {
        field.bits.forEach(function (bit, i) {
          var shift = field.lsb_first ? i : field.width - 1 - i;
          data[field.byte] |= ((value >> shift) & 1) << bit;
        });
      } else if (field.float) {
        view.setFloat32(field.byte, value, false);
        if (!Number.isFinite(view.getFloat32(field.byte, false))) throw new Error(field.name + ": value is outside the 32-bit float range.");
      } else {
        if (value < 0) value += Math.pow(2, field.width);
        for (var b = field.size - 1; b >= 0; b--) { data[field.byte + b] = value % 256; value = Math.floor(value / 256); }
      }
    });
    return data;
  }
  function decodeFields(form, data) {
    if (data.length !== form.length) throw new Error("Expected " + form.length + " data bytes, received " + data.length + ".");
    var view = new DataView(data.buffer, data.byteOffset, data.byteLength);
    return form.fields.map(function (field) {
      var value = 0;
      if (field.bits) {
        field.bits.forEach(function (bit, i) {
          var shift = field.lsb_first ? i : field.width - 1 - i;
          value += ((data[field.byte] >> bit) & 1) * Math.pow(2, shift);
        });
      } else if (field.float) value = view.getFloat32(field.byte, false);
      else {
        for (var b = 0; b < field.size; b++) value = value * 256 + data[field.byte + b];
        if (field.signed && value >= Math.pow(2, field.width - 1)) value -= Math.pow(2, field.width);
      }
      return value;
    });
  }
  function parseIdentifier(text) {
    var value = text.trim();
    if (!/^(?:0x)?[0-9a-f]{1,3}$/i.test(value)) throw new Error("Enter an 11-bit hexadecimal identifier, for example 0x07A.");
    var id = parseInt(value.replace(/^0x/i, ""), 16);
    if (id > 0x7FF) throw new Error("Standard CAN identifiers range from 0x000 to 0x7FF.");
    return id;
  }
  function parseBytes(text) {
    var value = text.trim();
    if (!value) return new Uint8Array(0);
    if (!/^(?:[0-9a-f]{2})+$|^[0-9a-f]{2}(?:\s+[0-9a-f]{2})*$/i.test(value)) throw new Error("Enter complete hexadecimal byte pairs, for example C8 1E 01 2C C0.");
    var hex = value.replace(/\s/g, "");
    if (hex.length > 16) throw new Error("A classic CAN frame carries at most eight data bytes.");
    return new Uint8Array(hex.match(/../g).map(function (pair) { return parseInt(pair, 16); }));
  }
  function decodeFrame(schema, id, data, remote) {
    if (!Number.isInteger(id) || id < 0 || id > 0x7FF) throw new Error("Identifier must fit an 11-bit CAN frame.");
    var command = schema.commands.find(function (c) { return c.id === ((id >> 1) & 63); });
    if (!command) throw new Error("Command " + ((id >> 1) & 63) + " is reserved or is not in this firmware's reference.");
    if (remote && data.length) throw new Error("An RTR request has no data payload; clear the data bytes.");
    var form = command.forms.find(function (f) { return f.remote === Boolean(remote) && f.length === data.length; });
    if (!form) throw new Error(command.name + ": this frame type/length is not supported. Expected " + command.forms.map(function (f) { return f.remote ? "RTR" : f.length + " bytes"; }).join(" or ") + ".");
    return {node: id >> 7, error: id & 1, command: command, form: form, values: decodeFields(form, data)};
  }
  return {encodeFields: encodeFields, decodeFields: decodeFields, decodeFrame: decodeFrame,
    parseBytes: parseBytes, parseIdentifier: parseIdentifier,
    hexId: function (id) { return "0x" + id.toString(16).toUpperCase().padStart(3, "0"); },
    hexBytes: function (data) { return Array.from(data).map(function (b) { return b.toString(16).toUpperCase().padStart(2, "0"); }).join(" "); }};
});
