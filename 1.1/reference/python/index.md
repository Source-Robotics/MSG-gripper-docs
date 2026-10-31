# Python library

The `Spectral-BLDC` package ([Spectral-BLDC-Python](https://github.com/Source-Robotics/Spectral-BLDC-Python),
`pip install Spectral-BLDC`) has one method per CAN message in `Spectral_BLDC.SpectralCAN`, and
`Spectral_BLDC.CanCommunication` for the bus. [With Python](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/python/) shows how they are used
with the gripper.

## Calls and messages

The calls for the messages this reference describes; the library has one for every message of the driver.

| Library call | Sends | Answered with | Reference |
|---|---|---|---|
| `Send_gripper_data_pack()` | Send_gripper_data_pack (ID 61) | Respond_Gripper_data_pack | [Gripper](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/gripper/#send_gripper_data_pack) |
| `Send_gripper_calibrate()` | Send_gripper_calibrate (ID 62) | — | [Gripper](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/gripper/#send_gripper_calibrate) |
| `Send_CAN_ID()` | Send_CAN_ID (ID 11) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_can_id) |
| `Send_ESTOP()` | Send_ESTOP (ID 0) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_estop) |
| `Send_Idle()` | Send_Idle (ID 12) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_idle) |
| `Send_Save_config()` | Send_Save_config (ID 13) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_save_config) |
| `Send_Reset()` | Send_Reset (ID 14) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_reset) |
| `Send_Clear_Error()` | Send_Clear_Error (ID 1) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_clear_error) |
| `Send_Watchdog()` | Send_Watchdog (ID 15) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_watchdog) |
| `Send_Heartbeat_Setup()` | Send_Heartbeat_Setup (ID 30) | — | [System](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/system/#send_heartbeat_setup) |
| `Send_Respond_Ping()` | Send_Respond_Ping (ID 10) | Send_Respond_Ping (data frame) | [Status requests](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_ping) |
| `Send_Respond_Temperature()` | Send_Respond_Temperature (ID 23) | Send_Respond_Temperature (data frame) | [Status requests](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_temperature) |
| `Send_Respond_Voltage()` | Send_Respond_Voltage (ID 24) | Send_Respond_Voltage (data frame) | [Status requests](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_voltage) |
| `Send_Respond_Device_Info()` | Send_Respond_Device_Info (ID 25) | Send_Respond_Device_Info (data frame) | [Status requests](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_device_info) |
| `Send_Respond_State_of_Errors()` | Send_Respond_State_of_Errors (ID 26) | Send_Respond_State_of_Errors (data frame) | [Status requests](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/can/status/#send_respond_state_of_errors) |

`Send_gripper_data_pack(position, speed, current, activate, action, estop, release_direction)` sends the 5-byte
move; called without arguments it sends the empty frame that only asks for the state.

## Receiving

`CanCommunication.receive_can_messages(timeout)` returns `(message, ids)`: the raw `python-can` message and a tuple
`ids` with `node_id`, `command_id` and `error_bit` from the identifier, or `(None, None)` after the timeout.
`SpectralCAN.UnpackData(message, ids)` decodes the message into the object's attributes:

| Message | Attributes |
|---|---|
| Respond_Gripper_data_pack | `gripper_position`, `gripper_current`, `gripper_activated`, `gripper_action_status`, `gripper_object_detection`, `gripper_temperature_error`, `gripper_timeout_error`, `gripper_estop_error`, `gripper_calibrated` |
| Send_Respond_State_of_Errors | `error`, `temperature_error`, `encoder_error`, `vbus_error`, `driver_error`, `velocity_error`, `current_error`, `estop_error`, `calibrated`, `activated`, `watchdog_error` |
| Send_Respond_Temperature | `temperature` |
| Send_Respond_Voltage | `voltage` |
| Send_Respond_Device_Info | `HARDWARE_VERSION`, `BATCH_DATE`, `SOFTWARE_VERSION`, `SERIAL_NUMBER` |

!!! note "Object detection in the library"
    Library version 1.20 assembles `gripper_object_detection` with the two bits swapped relative to the firmware,
    so it reports 1 where the gripper sends 2 (object detected while opening) and 2 where it sends 1 (object
    detected while closing); 0 and 3 are unaffected. Until the library is fixed, swap the two values in your
    program, or read the bits yourself from the frame.
