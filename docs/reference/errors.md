# Errors and status bits

## The gripper's state byte

Byte 3 of Respond_Gripper_data_pack, the answer to every gripper command, bits numbered from the most significant:

| Bit | Flag | Meaning |
|---|---|---|
| 7 | `activated` | the activate flag is set |
| 6 | `action_status` | 1 while a move is in progress; 0 when idle, holding, auto-releasing or calibrating |
| 5, 4 | `object_detection` | bit 5 is the low bit, bit 4 the high bit: 0 moving, 1 object found while closing, 2 object found while opening, 3 at the position |
| 3 | `temperature_error` | the thermistor in the windings is above the limit |
| 2 | `timeout_error` | the driver's CAN watchdog ran out |
| 1 | `estop_error` | the E-stop bit of a command was received |
| 0 | `calibrated` | the gripper calibration is done |

The Python library's attributes are `gripper_activated`, `gripper_action_status`, `gripper_object_detection`,
`gripper_temperature_error`, `gripper_timeout_error`, `gripper_estop_error` and `gripper_calibrated`; library
version 1.20 assembles `gripper_object_detection` with its two bits swapped (1 and 2 exchanged).

## The driver's error flags

The flags as the firmware keeps them, the line `#Error` prints for each, and where each sits in the two bytes of
Send_Respond_State_of_Errors (bits numbered from the most significant).

| Flag | `#Error` prints | Byte, bit | Raised when |
|---|---|---|---|
| `Error` | `In error state!` | 0, 7 | any of the flags below is set (also the error bit of every CAN identifier) |
| `temperature_error` | `Temp error` | 0, 6 | the thermistor reads above `#Tlim` (75 °C) |
| `encoder_error` | `Encoder error` | 0, 5 | the driver's encoder does not see its magnet |
| `Vbus_error` | `Vbus error` | 0, 4 | the supply is below 9 V or above 29.5 V |
| `Driver_error` | `Driver error (undervoltage, thermal shutdown, or overcurrent)` | 0, 3 | the driver stage's fault output is active |
| `Velocity_error` | `Velocity error` | 0, 2 | the motor speed exceeds the driver's limit |
| `Current_error` | `Current error` | 0, 1 | never in this firmware; reserved |
| `ESTOP_error` | `Received ESTOP command` | 0, 0 | Send_ESTOP was received |
| `Calibrated` (0) | `Not calibrated` | 1, 7 (1 = calibrated) | the driver's motor calibration is missing |
| `Activated` | — | 1, 6 | the activated flag, not an error |
| `Watchdog_error` | `Watchdog error` | 1, 5 | the watchdog time passed without a valid CAN frame |

The gripper's `timeout_error` is the driver's `Watchdog_error`; the gripper's `temperature_error` is the driver's.
The gripper's `estop_error` is its own, raised by the E-stop bit of the gripper command, and is distinct from the
driver's `ESTOP_error` raised by Send_ESTOP.

## Clearing

Send_Clear_Error and `#Clear` clear every flag, the gripper's E-stop included, and go to idle; a flag whose cause
persists is set again at once. After an E-stop, the next gripper command must carry the E-stop bit at 0. The
driver's `Calibrated` flag is set only by the motor calibration (`#Cal`).

## The LED

The driver's status LED is inside the housing: three short flashes and a pause in normal operation, flashing
every 0.5 s during the motor calibration, on steadily in error mode or while the motor is not calibrated.
