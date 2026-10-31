/* Known wire vectors, boundary values and invalid input. No browser or hardware. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const codec = require("../docs/javascripts/can-tools.js");
const schema = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const get = (key, length, direction = "host") => schema.commands.find(c => c.key === key).forms.find(f => f.length === length && f.direction === direction);
const grip = get("IN_GRIPPER_DATA_PACK", 5);
assert.equal(codec.hexBytes(codec.encodeFields(grip, [200, 30, 300, 1, 1, 0, 0])), "C8 1E 01 2C C0");
let response = codec.decodeFrame(schema, 0x1F9, codec.parseBytes("64 FE D4 A1"), false);
assert.equal(response.node, 3);
assert.equal(response.error, 1);
assert.deepEqual(response.values, [100, -300, 1, 0, 1, 0, 0, 0, 1]); // bit 5 is detection bit 0
response = codec.decodeFrame(schema, 0x078, codec.parseBytes("64 FE D4 91"), false);
assert.equal(response.values[4], 2); // bit 4 is detection bit 1
assert.equal(codec.hexBytes(codec.encodeFields(response.form, response.values)), "64 FE D4 91");
assert.equal(codec.decodeFrame(schema, 0x07A, new Uint8Array(), false).form.title, "status poll");
assert.equal(codec.decodeFrame(schema, 0x030, new Uint8Array(), true).form.remote, true);
assert.throws(() => codec.decodeFrame(schema, 0x07A, new Uint8Array(4), false), /not supported/);
assert.throws(() => codec.decodeFrame(schema, 0x030, new Uint8Array(2), true), /no data payload/);
assert.throws(() => codec.encodeFields(grip, [256, 30, 300, 1, 1, 0, 0]), /0 to 255/);
assert.throws(() => codec.encodeFields(grip, ["", 30, 300, 1, 1, 0, 0]), /enter a value/);
assert.throws(() => codec.parseBytes("F 01"), /byte pairs/);
assert.throws(() => codec.parseBytes("00 01 02 03 04 05 06 07 08"), /eight/);
assert.throws(() => codec.parseIdentifier("0x800"), /0x7FF/);
assert.equal(codec.parseIdentifier("1fa"), 0x1FA);
if (schema.commands.some(c => c.key === "IN_DATA_PACK_1")) {
  const motion = get("IN_DATA_PACK_1", 8);
  assert.equal(codec.hexBytes(codec.encodeFields(motion, [-8388608, 8388607, -32768])), "80 00 00 7F FF FF 80 00");
  assert.deepEqual(codec.decodeFields(motion, codec.parseBytes("FF FF FF 00 00 01 FF FF")), [-1, 1, -1]);
  assert.equal(codec.decodeFrame(schema, 0x004, new Uint8Array(5), false).form.length, 5);
  assert.equal(codec.decodeFrame(schema, 0x004, new Uint8Array(2), false).form.length, 2);
  const gains = get("IN_KP_KD", 8);
  assert.equal(codec.hexBytes(codec.encodeFields(gains, [1.5, -2.25])), "3F C0 00 00 C0 10 00 00");
  assert.deepEqual(codec.decodeFields(gains, codec.parseBytes("3F C0 00 00 C0 10 00 00")), [1.5, -2.25]);
  assert.throws(() => codec.encodeFields(gains, [1e39, 0]), /32-bit float/);
}
console.log("CAN codec known vectors and validation passed");
