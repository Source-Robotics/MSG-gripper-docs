# Over CAN

CAN is the gripper's interface: the one cable carries it next to the power, and a robot's control board, a PC with
the CANvas adapter or any microcontroller with a CAN transceiver drives the gripper with it. The gripper is a
STEPFOC driver on the bus, so the frames are the driver's; this page is the part a gripper needs.

## The frame

CAN 2.0 data frames with 11-bit identifiers at 1 Mbit/s. The identifier carries the node, the command and the
error state:

![Bits 10 to 7 of the identifier are the node ID, bits 6 to 1 the command ID, bit 0 the error bit](../assets/can-id.svg#only-light){ width="600" }
![Bits 10 to 7 of the identifier are the node ID, bits 6 to 1 the command ID, bit 0 the error bit](../assets/can-id_dark.svg#only-dark){ width="600" }

- **Node ID**, bits 10 to 7: which device. Every gripper ships as node 0; set another with Send_CAN_ID or `#CANID`
  and save it. Use 0 to 13: the driver's bootloader reserves 14 and 15, and a device on one of those cannot be
  updated over CAN.
- **Command ID**, bits 6 to 1: which message. The gripper command is 61, its answer 60, the calibration 62.
- **Error bit**, bit 0: in a frame from the gripper, 1 while any error is active. In a frame from the host it is
  ignored.

So the gripper command to node 0 travels on identifier `(0 << 7) | (61 << 1)` = 0x7A, and the answer comes back on
`(60 << 1) | error` = 0x78 or 0x79; to node 3 the command is 0x1FA and the answer 0x1F8. Multi-byte values are
big-endian; flags inside a byte are numbered from the most significant bit.

## The messages a gripper needs

| Message | ID | What for |
|---|---|---|
| [Send_gripper_data_pack](../reference/can/gripper.md#send_gripper_data_pack) | 61 | the move command: position, speed, current, the activate, action and E-stop bits; 0 bytes to poll |
| [Respond_Gripper_data_pack](../reference/can/gripper.md#respond_gripper_data_pack) | 60 | the answer: position, current, the state and error bits |
| [Send_gripper_calibrate](../reference/can/gripper.md#send_gripper_calibrate) | 62 | the gripper calibration, after every power-up |
| [Send_Clear_Error](../reference/can/system.md#send_clear_error) | 1 | clears the errors |
| [Send_ESTOP](../reference/can/system.md#send_estop), [Send_Idle](../reference/can/system.md#send_idle) | 0, 12 | stop |
| [Send_Watchdog](../reference/can/system.md#send_watchdog) | 15 | the gripper stops when the host stops talking |
| [Send_CAN_ID](../reference/can/system.md#send_can_id), [Send_Save_config](../reference/can/system.md#send_save_config) | 11, 13 | another node ID, saved |
| [Send_Respond_State_of_Errors](../reference/can/status.md#send_respond_state_of_errors), [Send_Respond_Temperature](../reference/can/status.md#send_respond_temperature) | 26, 23 | the driver's error flags, the motor temperature |

The [CAN reference](../reference/can/index.md) has the bytes of each; the driver's other messages, which a
gripper does not need, are on the [STEPFOC site](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/can/).

## A control loop

1. At power-up: Send_Clear_Error, then Send_gripper_calibrate; poll with empty Send_gripper_data_pack frames
   until the calibrated bit is 1 (up to about ten seconds; the routine gives up after 24 s). Send nothing else
   meanwhile.
2. For each grip: one Send_gripper_data_pack with the position, speed and current and the activate and action
   bits set. Its answer still carries the state from before it; ignore it. Then poll with empty frames until
   the object-detection field reads 1, 2 or 3, or your own timeout passes.
3. Keep polling at a steady rate (50 Hz is plenty) if you set the watchdog: every frame resets it, and the gripper
   stops by itself when your program stops.

The answer to every frame tells the whole state, so a host never has to ask twice.

## Host checklist

- **Clear, then calibrate.** With an error active, the driver drops the calibration request; a clear sent during
  the calibration ends it.
- **During the calibration, only empty frames.** A full Send_gripper_data_pack ends the calibration as well, and
  the gripper keeps the calibration it had before (none after a power-up). Wait for the calibrated bit; the
  routine gives up after 24 s. A new Send_gripper_calibrate starts it from the beginning.
- **The first answer is old.** The answer to a full command is sent before the gripper acts on it. Ignore it.
  The polls after it can be trusted at once: an object is reported only after the jaws have stood still against
  it for 50 ms, so the slow start of a move does not read as one.
- **The action status repeats your bit.** It is the action bit you last sent and stays 1 while the gripper
  holds. Follow a move by its object detection.
- **An identical command does nothing.** To repeat a move to the position the gripper holds, change the speed
  or the current by one.
- **E-stop recovery:** first a command with the E-stop bit at 0 (and the action bit at 0), then
  Send_Clear_Error. While the last command carries the E-stop bit, a clear does not hold.
- **Watchdog:** with Send_Watchdog set, keep the polls coming. The gripper commands and the status requests
  reset it; Send_Clear_Error and Send_gripper_calibrate do not. After a timeout, fix the host, clear, and
  resume.
- **Current:** keep the commanded current within the stepper's maximum, 1.5, 2.0 or 2.1 A; the firmware clamps
  it only at 2800 mA ([Force and speed](../03-technical-data/force-and-speed.md)). The commanded current is the
  gripper's own limit; the driver's current limit (parameter 16) stays as you set it.
- **Settings by number:** gripper mode, the thermistor and the gripper's measured stroke are parameters 92, 91
  and 93, read and written with Send_Get_Parameter and Send_Parameter
  ([Parameters a gripper uses](../reference/can/system.md#parameters-a-gripper-uses)).

## From a PC

The [CANvas adapter](https://source-robotics.com/products/canvas-usb-to-can-adapter) shows up as a serial port and
speaks slcan; `python-can` opens it with `bustype='slcan'`, and the [Python library](python.md) wraps the messages.
Any CAN adapter that `python-can` supports works the same way.

## On a bus with other devices

A gripper on a robot shares the bus with the robot's joints or other grippers. Give each device its own node ID
(connect one at a time, Send_CAN_ID, Send_Save_config), terminate both ends of the bus
([CAN termination](../04-installation/can-termination.md)), and keep in mind that a lower node ID wins the bus
arbitration.
