# CAN messages

CAN 2.0, 1 Mbit/s, 11-bit identifiers. The identifier carries the node ID (bits 10 to 7, 0 to 13), the command ID
(bits 6 to 1, 0 to 63) and, in frames from the gripper, the error bit (bit 0). [Over CAN](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/can/)
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

| ID | Message | Direction | Length | Group |
|---|---|---|---|---|
| 0 | [Send_ESTOP](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_estop) | host → driver | 0 | System |
| 1 | [Send_Clear_Error](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_clear_error) | host → driver | 0 | System |
| 9 | [Respond_Heartbeat](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#respond_heartbeat) | driver → host | 0 | Status requests |
| 10 | [Send_Respond_Ping](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_ping) | host → driver as a remote frame, driver → host as a data frame | 0 (remote) / 0 | Status requests |
| 11 | [Send_CAN_ID](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_can_id) | host → driver | 1 | System |
| 12 | [Send_Idle](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_idle) | host → driver | 0 | System |
| 13 | [Send_Save_config](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_save_config) | host → driver | 0 | System |
| 14 | [Send_Reset](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_reset) | host → driver | 0 | System |
| 15 | [Send_Watchdog](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_watchdog) | host → driver | 5 | System |
| 23 | [Send_Respond_Temperature](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_temperature) | host → driver as a remote frame, driver → host as a data frame | 0 (remote) / 2 | Status requests |
| 24 | [Send_Respond_Voltage](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_voltage) | host → driver as a remote frame, driver → host as a data frame | 0 (remote) / 2 | Status requests |
| 25 | [Send_Respond_Device_Info](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_device_info) | host → driver as a remote frame, driver → host as a data frame | 0 (remote) / 7 | Status requests |
| 26 | [Send_Respond_State_of_Errors](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_state_of_errors) | host → driver as a remote frame, driver → host as a data frame | 0 (remote) / 2 | Status requests |
| 30 | [Send_Heartbeat_Setup](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_heartbeat_setup) | host → driver | 4 | System |
| 60 | [Respond_Gripper_data_pack](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/gripper/#respond_gripper_data_pack) | driver → host | 4 | Gripper |
| 61 | [Send_gripper_data_pack](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/gripper/#send_gripper_data_pack) | host → driver | 0, 5 | Gripper |
| 62 | [Send_gripper_calibrate](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/gripper/#send_gripper_calibrate) | host → driver | 0 | Gripper |

The driver's other messages (the motion commands, the gains and limits, the encoder and current requests) are
not listed here; they are in the [STEPFOC CAN reference](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/can/).

## By group

- [Gripper](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/gripper/): the move command and its answer, the gripper calibration
- [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/): node ID, E-stop, idle, save, reset, clear, watchdog, heartbeat setup
- [Status requests](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/): temperature, voltage, identity, the driver's error flags, the heartbeat

## The Python library

Every message the host can send has a method of the same name in `Spectral_BLDC.SpectralCAN`, listed in
[Python library](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/python/).

## Tools and downloads

[Build or decode a CAN frame, and download this firmware's JSON and DBC definitions](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can-tools/).
