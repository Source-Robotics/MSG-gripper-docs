# System

Node ID, stopping, saving, resetting, clearing errors, the watchdog and the heartbeat setup: the driver's system
messages a gripper host uses.

### Send_CAN_ID

<div class="cmd-facts" markdown><span class="fact">ID 11</span><span class="fact">host → driver</span><span class="fact">1 bytes</span><span class="fact">Python: `Send_CAN_ID()`</span></div>

Gives the driver a new node ID, 0 to 13 (the firmware accepts up to 15, but the bootloader reserves 14 and 15: a driver on one of those cannot be updated over CAN). The driver answers to the new ID at once; Send_Save_config keeps it over a power cycle and also writes it into the bootloader's board ID.

**1 bytes**

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0 |  | ID | unsigned 8-bit | 0 to 15 |

The driver does not answer this command.

---

### Send_ESTOP

<div class="cmd-facts" markdown><span class="fact">ID 0</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_ESTOP()`</span></div>

Stops the motor and raises the E-stop error, which stays until Send_Clear_Error. A running calibration ends. From firmware 110 `#Estop` does the same over UART.

The driver does not answer this command.

---

### Send_Idle

<div class="cmd-facts" markdown><span class="fact">ID 12</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Idle()`</span></div>

Puts the driver in idle mode (the motor coasts or brakes, see Send_Settings).

The driver does not answer this command.

---

### Send_Save_config

<div class="cmd-facts" markdown><span class="fact">ID 13</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Save_config()`</span></div>

Writes the current configuration (gains, limits, the motor calibration, CAN ID, heartbeat, watchdog, gripper flag, and from firmware 110 brake or coast) to the EEPROM. The gripper calibration is not saved: it runs after every power-up.

The driver does not answer this command.

---

### Send_Reset

<div class="cmd-facts" markdown><span class="fact">ID 14</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Reset()`</span></div>

Resets the driver. From firmware 105 the reset lands in the bootloader, which waits 2 s for a flashing host and then starts the firmware again; this is how a firmware update begins.

The driver does not answer this command.

---

### Send_Clear_Error

<div class="cmd-facts" markdown><span class="fact">ID 1</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Clear_Error()`</span></div>

Clears the error flags and goes to idle. An error whose cause is still present comes straight back; the gripper's E-stop error comes back while the last gripper command's E-stop bit is 1, so send a command with the bit at 0 first. A clear also ends a running gripper calibration. A calibration error is cleared only by calibrating.

The driver does not answer this command.

---

### Send_Watchdog

<div class="cmd-facts" markdown><span class="fact">ID 15</span><span class="fact">host → driver</span><span class="fact">5 bytes</span><span class="fact">Python: `Send_Watchdog()`</span></div>

Sets the watchdog: the gripper command (full or empty) and the status requests reset it, Send_Clear_Error, Send_gripper_calibrate and the setup messages do not; when the time runs out the driver reports a watchdog error and does what the action byte says. 0 turns it off (the default). Hold and descend run for the fallback time, then the after-action (parameters 2 and 5), and only when the watchdog runs out while the driver is in gripper mode. From firmware 110 a watchdog that runs out while the driver is idle starts neither, also not when the next gripper command arrives. The STEPFOC site explains each action, [The watchdog](https://docs.source-robotics.com/STEPFOC-docs/latest/06-operation/watchdog/).

**5 bytes**

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0-3 |  | Time | unsigned 32-bit | ms; 0 = off |
| 4 |  | Action | unsigned 8-bit | 0 legacy (brake or coast as idle does), 1 hold the position, 2 brake, 3 coast, 4 descend at the fallback current and speed; other values act as 0 |

The driver does not answer this command.

---

### Send_Heartbeat_Setup

<div class="cmd-facts" markdown><span class="fact">ID 30</span><span class="fact">host → driver</span><span class="fact">4 bytes</span><span class="fact">Python: `Send_Heartbeat_Setup()`</span></div>

Sets the heartbeat interval in ms; 0 turns the heartbeat off (the default). Kept by Send_Save_config.

**4 bytes**

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0-3 |  | Interval | unsigned 32-bit | ms; 0 = off |

---

## Parameters a gripper uses

Settings without a message of their own are numbered parameters. Send_Parameter (ID 36) writes one,
Send_Get_Parameter (ID 37) asks for one, and the driver answers with Respond_Parameter (ID 38). The frames and the
whole list are on the STEPFOC site,
[Parameters](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/can/parameters/). These concern a
gripper:

| Parameter | What it is | Values |
|---|---|---|
| 16 | the driver's current limit in mA, for the motor modes; gripper moves and the gripper calibration leave it as it is | a float |
| 18 | brake or coast when idle; kept by Send_Save_config | 1 brake, 0 coast; a driver that never saved it brakes |
| 90 | `#Rstint`: zero the velocity and current integrators on every setpoint command | 0 or 1; 0 on a gripper |
| 91 | `#Term`: the thermistor measurement | 0 or 1; 1 on a gripper |
| 92 | `#Gripper`: gripper mode, in force at once; written only while the driver is idle | 0 or 1; 1 on a gripper |
| 93 | read only: the gripper's stroke between positions 0 and 255, in encoder ticks | 0 until the gripper is calibrated |

Parameters 90 to 93 are new in firmware 110, and from 110 Send_Save_config keeps 18 too; it keeps 90 to 92 like
the other settings. A value outside the range is refused, and the value in force stays.

The Python library names them from 1.22 (`PARAM_RSTINT`, `PARAM_THERMISTOR`, `PARAM_GRIPPER_MODE`,
`PARAM_GRIPPER_STROKE`); 1.21 takes the numbers. `gripper.Send_Parameter(92, 1)` writes one;
`gripper.Send_Get_Parameter(93)` asks for one, and its answer, passed through `UnpackData`, lands in
`gripper.parameters[93]`.
