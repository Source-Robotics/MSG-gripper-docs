# System

Node ID, stopping, saving, resetting, clearing errors, the watchdog and the heartbeat setup: the driver's system
messages a gripper host uses.

### Send_CAN_ID

<div class="cmd-facts" markdown><span class="fact">ID 11</span><span class="fact">host → driver</span><span class="fact">1 bytes</span><span class="fact">Python: `Send_CAN_ID()`</span></div>

Gives the driver a new node ID, 0 to 13 (the firmware accepts up to 15, but the bootloader reserves 14 and 15: a driver on one of those cannot be updated over CAN). Setting the ID also sets the bootloader's board ID. The driver answers to the new ID at once; the ID is kept over a power cycle only after Send_Save_config.

**1 bytes**

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0 |  | ID | unsigned 8-bit | 0 to 15 |

The driver does not answer this command.

---

### Send_ESTOP

<div class="cmd-facts" markdown><span class="fact">ID 0</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_ESTOP()`</span></div>

Stops the motor and raises the E-stop error, which stays until Send_Clear_Error.

The driver does not answer this command.

---

### Send_Idle

<div class="cmd-facts" markdown><span class="fact">ID 12</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Idle()`</span></div>

Puts the driver in idle mode (the motor coasts or brakes, see Send_Settings).

The driver does not answer this command.

---

### Send_Save_config

<div class="cmd-facts" markdown><span class="fact">ID 13</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Save_config()`</span></div>

Writes the current configuration (gains, limits, calibration, CAN ID, heartbeat, watchdog, gripper flag) to the EEPROM.

The driver does not answer this command.

---

### Send_Reset

<div class="cmd-facts" markdown><span class="fact">ID 14</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Reset()`</span></div>

Resets the driver. From firmware 105 the reset lands in the bootloader, which waits 2 s for a flashing host and then starts the firmware again; this is how a firmware update begins.

The driver does not answer this command.

---

### Send_Clear_Error

<div class="cmd-facts" markdown><span class="fact">ID 1</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_Clear_Error()`</span></div>

Clears the error flags and goes to idle. An error whose cause is still present comes straight back. A calibration error is cleared only by calibrating.

The driver does not answer this command.

---

### Send_Watchdog

<div class="cmd-facts" markdown><span class="fact">ID 15</span><span class="fact">host → driver</span><span class="fact">5 bytes</span><span class="fact">Python: `Send_Watchdog()`</span></div>

Sets the watchdog: every valid CAN frame the driver receives resets it; when the time runs out the driver reports a watchdog error and stops. 0 turns it off (the default). The action byte is stored but not acted on by this firmware: the driver always stops into its idle behaviour.

**5 bytes**

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0-3 |  | Time | unsigned 32-bit | ms; 0 = off |
| 4 |  | Action | unsigned 8-bit | 0 idle, 1 hold, 2 brake (stored only) |

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
