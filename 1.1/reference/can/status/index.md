# Status requests

Remote frames the host sends under a command ID, answered by the gripper with a data frame under the same ID,
and the heartbeat the gripper sends on its own when it is set up.

### Send_Respond_Ping

<div class="cmd-facts" markdown><span class="fact">ID 10</span><span class="fact">host → driver as a remote frame, driver → host as a data frame</span><span class="fact">remote frame, 0 bytes</span><span class="fact">Python: `Send_Respond_Ping()`</span></div>

Asks the driver to answer with an empty frame, to see that it is on the bus.

**The frame** (0 bytes)

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|

The driver answers with **Send_Respond_Ping**.

---

### Send_Respond_Temperature

<div class="cmd-facts" markdown><span class="fact">ID 23</span><span class="fact">host → driver as a remote frame, driver → host as a data frame</span><span class="fact">remote frame, 0 bytes</span><span class="fact">Python: `Send_Respond_Temperature()`</span></div>

Asks for the thermistor temperature. Meaningful only with the thermistor enabled (`#Term 1`).

**The frame** (2 bytes)

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0-1 |  | temperature | signed 16-bit | °C |

The driver answers with **Send_Respond_Temperature**.

---

### Send_Respond_Voltage

<div class="cmd-facts" markdown><span class="fact">ID 24</span><span class="fact">host → driver as a remote frame, driver → host as a data frame</span><span class="fact">remote frame, 0 bytes</span><span class="fact">Python: `Send_Respond_Voltage()`</span></div>

Asks for the supply voltage.

**The frame** (2 bytes)

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0-1 |  | voltage | unsigned 16-bit | mV |

The driver answers with **Send_Respond_Voltage**.

---

### Send_Respond_Device_Info

<div class="cmd-facts" markdown><span class="fact">ID 25</span><span class="fact">host → driver as a remote frame, driver → host as a data frame</span><span class="fact">remote frame, 0 bytes</span><span class="fact">Python: `Send_Respond_Device_Info()`</span></div>

Asks for the driver's identity: hardware version, batch date and serial number from the EEPROM, and the firmware release (from firmware 105 on this is the build's own version; before, a value from the EEPROM).

**The frame** (7 bytes)

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0 |  | HARDWARE_VERSION | unsigned 8-bit | PCB revision |
| 1 |  | BATCH_DATE | unsigned 8-bit | production batch |
| 2 |  | SOFTWARE_VERSION | unsigned 8-bit | firmware release, e.g. 108 |
| 3-6 |  | SERIAL_NUMBER | unsigned 32-bit | serial number |

The driver answers with **Send_Respond_Device_Info**.

---

### Send_Respond_State_of_Errors

<div class="cmd-facts" markdown><span class="fact">ID 26</span><span class="fact">host → driver as a remote frame, driver → host as a data frame</span><span class="fact">remote frame, 0 bytes</span><span class="fact">Python: `Send_Respond_State_of_Errors()`</span></div>

Asks for every error flag and the calibrated, activated and watchdog states.

**The frame** (2 bytes)

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0 | 7 | error | bit | any error is active |
| 0 | 6 | temperature_error | bit | motor over the temperature limit |
| 0 | 5 | encoder_error | bit | magnet not detected or misaligned |
| 0 | 4 | vbus_error | bit | supply voltage outside the limits |
| 0 | 3 | driver_error | bit | the MOSFET driver reports undervoltage, thermal shutdown or overcurrent |
| 0 | 2 | velocity_error | bit | speed over the limit |
| 0 | 1 | current_error | bit | reserved; never set by this firmware |
| 0 | 0 | estop_error | bit | Send_ESTOP was received |
| 1 | 7 | calibrated | bit | the motor is calibrated |
| 1 | 6 | activated | bit | the controller is activated |
| 1 | 5 | watchdog_error | bit | the watchdog ran out |

The driver answers with **Send_Respond_State_of_Errors**.

---

### Respond_Heartbeat

<div class="cmd-facts" markdown><span class="fact">ID 9</span><span class="fact">driver → host</span><span class="fact">0 bytes</span></div>

The frame the driver sends on its own at the heartbeat interval (Send_Heartbeat_Setup); empty. Off by default. Any other frame the driver sends resets the heartbeat timer, so a driver that answers motion commands at a high rate never sends a heartbeat.

**The frame** (0 bytes)

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|

---
