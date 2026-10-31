# CAN frame tool and downloads

Build or inspect a frame using the command definitions of this manual's firmware release. All calculations
run in your browser; the tool does not connect to an adapter or send commands to hardware.

## Downloads

[Command definitions (JSON)](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/can/protocol-V108.json) · [Gripper DBC](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/can/protocol-V108-gripper.dbc)

The JSON includes the firmware tag, source commit, message IDs, every documented layout and its bit order.
The DBC files cover **nodes 0 to 13**, with both the clean and fault-bit identifiers of driver replies.
Reserved commands are omitted. Values use the firmware's native units: ticks, ticks/s, mA and the units in
the [CAN reference](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/).

An RTR request uses the same identifier as its data reply. DBC describes the **data reply**; it does not
represent the request's RTR flag or the empty gripper status poll. Both are supported by the browser tool.

The gripper's two object-detection bits have an unusual order: bit 5 is the low bit, bit 4 the high bit.
The DBC signal `gripper_object_detection_raw` retains the wire value and supplies text labels (raw 2 =
object while closing, raw 1 = object while opening). The browser decoder converts that pair to the firmware's
numeric status (1 = closing, 2 = opening).

## Try a frame

The example `0x07A`, data `C8 1E 01 2C C0`, is a command to gripper node 0: position 200, speed 30,
current 300 mA, activate and action set, E-stop and release direction clear. These are an illustration of the
encoding; the device's current and motion limits still apply. Select another message above the fields to build
one of its documented forms. To inspect a reply, enter its identifier and data bytes below.

<div class="can-tool" data-schema="../../assets/can/protocol-V108.json" markdown="0">
  <p class="can-tool__status" role="status">Loading the firmware's command definitions…</p>
  <fieldset><legend>Build a frame</legend>
    <label for="ct-node">Node ID (0–13)</label><input id="ct-node" name="node" type="number" min="0" max="13" step="1" value="0">
    <label for="ct-command">Message and layout</label><select id="ct-command" name="command"></select>
    <label><input name="error" type="checkbox"> Driver reply has an active fault (error bit 1)</label>
    <div class="can-tool__fields"></div>
    <button type="button" name="build" class="md-button md-button--primary">Build frame</button>
    <pre class="can-tool__built" aria-live="polite"></pre>
    <button type="button" name="use" class="md-button">Use this frame in the decoder</button>
  </fieldset>
  <fieldset><legend>Decode a frame</legend>
    <label for="ct-id">CAN identifier (hex)</label><input id="ct-id" name="identifier" type="text" value="0x07A" spellcheck="false">
    <label for="ct-data">Data bytes (hex, up to eight)</label><input id="ct-data" name="data" type="text" value="C8 1E 01 2C C0" spellcheck="false">
    <label><input name="remote" type="checkbox"> Remote request (RTR; no payload)</label>
    <button type="button" name="decode" class="md-button md-button--primary">Decode frame</button>
    <div class="can-tool__decoded" aria-live="polite"></div>
  </fieldset>
  <noscript>Enable JavaScript for the frame tool, or use the reference tables and downloads above.</noscript>
</div>

**Check:** the example decodes to the values above. Change the identifier to `0x1FA` to see the same command
addressed to node 3. An invalid length or out-of-range field produces an explanation instead of a frame.

For wiring, termination, host timing and recovery, use [Over CAN](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/can/). To look up a
message's purpose and accepted lengths, use the [CAN reference](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/).
