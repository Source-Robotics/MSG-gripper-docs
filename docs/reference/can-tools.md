# CAN frame tool and downloads

Build or inspect a frame using the command definitions of this manual's firmware release. All calculations
run in your browser; the tool does not connect to an adapter or send commands to hardware.

## Downloads

<!-- can-downloads -->

The JSON includes the firmware tag, source commit, message IDs, every documented layout and its bit order.
The DBC files cover **nodes 0 to 13**, with both the clean and fault-bit identifiers of driver replies.
Reserved commands are omitted. Values use the firmware's native units: ticks, ticks/s, mA and the units in
the [CAN reference](can/index.md).

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

<!-- can-tool -->

**Check:** the example decodes to the values above. Change the identifier to `0x1FA` to see the same command
addressed to node 3. An invalid length or out-of-range field produces an explanation instead of a frame.

For wiring, termination, host timing and recovery, use [Over CAN](../06-operation/can.md). To look up a
message's purpose and accepted lengths, use the [CAN reference](can/index.md).
