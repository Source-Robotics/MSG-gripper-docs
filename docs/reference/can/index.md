# CAN messages

CAN 2.0, 1 Mbit/s, 11-bit identifiers. The identifier carries the node ID (bits 10 to 7, 0 to 13), the command ID
(bits 6 to 1, 0 to 63) and, in frames from the gripper, the error bit (bit 0). [Over CAN](../../06-operation/can.md)
explains how the pieces are used; this page lists them.

Three kinds of message:

- **Send_…** — the host sends data to the gripper. The gripper command is answered with Respond_Gripper_data_pack;
  the others are not answered.
- **Send_Respond_…** — the host asks for data with a **remote frame** (RTR bit set, no data) under the command ID;
  the gripper answers with a data frame under the same command ID.
- **Respond_…** — frames only the gripper sends.

Multi-byte values are big-endian (data[0] first); bits inside a byte are numbered from the most significant bit
(bit 7 first).

## The messages a gripper needs

<!-- can-overview -->

The driver's other messages (the motion commands, the gains and limits, the encoder and current requests) are
not listed here; they are in the [STEPFOC CAN reference](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/can/).

## By group

- [Gripper](gripper.md): the move command and its answer, the gripper calibration
- [System](system.md): node ID, E-stop, idle, save, reset, clear, watchdog, heartbeat setup
- [Status requests](status.md): temperature, voltage, identity, the driver's error flags, the heartbeat

## The Python library

Every message the host can send has a method of the same name in `Spectral_BLDC.SpectralCAN`, listed in
[Python library](../python.md).

## Tools and downloads

[Build or decode a CAN frame, and download this firmware's JSON and DBC definitions](../can-tools.md).
