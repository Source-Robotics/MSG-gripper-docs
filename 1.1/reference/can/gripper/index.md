# Gripper

The move command, its answer, and the gripper calibration. [How the gripper works](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/how-it-works/)
explains what the gripper does with them.

### Send_gripper_data_pack

<div class="cmd-facts" markdown><span class="fact">ID 61</span><span class="fact">host → driver</span><span class="fact">0 or 5 bytes</span><span class="fact">Python: `Send_gripper_data_pack()`</span></div>

The gripper command, for a driver set up as a gripper (`#Gripper 1`, saved). Position, speed and the current limit of the move, plus the activate, action and E-stop bits. A move is carried out only while the gripper is calibrated, activated and the action bit is 1. An empty frame (0 bytes) only asks for the state.

**5 bytes**

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0 |  | Position | unsigned 8-bit | 0 fully open, 255 fully closed |
| 1 |  | Speed | unsigned 8-bit | 0 slowest, 255 fastest |
| 2-3 |  | Current | signed 16-bit | current limit of the move in mA, the grip force; not clamped by the firmware, keep it at or below the stepper's rated current (Force and speed) |
| 4 | 7 | Activate | bit | 1 activate the gripper, 0 deactivate |
| 4 | 6 | Action | bit | 1 go to the position, 0 idle |
| 4 | 5 | E-stop | bit | 1 raises the gripper E-stop error |
| 4 | 4 | Release direction | bit | read by the firmware but not used |

The driver answers with **Respond_Gripper_data_pack**.

---

### Respond_Gripper_data_pack

<div class="cmd-facts" markdown><span class="fact">ID 60</span><span class="fact">driver → host</span><span class="fact">4 bytes</span></div>

The driver's answer to Send_gripper_data_pack: position, measured current, and the state bits. Python attributes `gripper_position`, `gripper_current`, `gripper_activated`, `gripper_action_status`, `gripper_object_detection`, `gripper_temperature_error`, `gripper_timeout_error`, `gripper_estop_error`, `gripper_calibrated`.

**The frame** (4 bytes)

| Byte | Bit | Field | Type | Meaning |
|---|---|---|---|---|
| 0 |  | gripper_position | unsigned 8-bit | 0 fully open, 255 fully closed |
| 1-2 |  | gripper_current | signed 16-bit | measured current in mA |
| 3 | 7 | gripper_activated | bit | 1 activated |
| 3 | 6 | gripper_action_status | bit | 1 going to the position, 0 idle, auto-release or calibrating |
| 3 | 5-4 | gripper_object_detection | 2 bits | bit 5 is the low bit, bit 4 the high bit: 0 moving, 1 object detected while closing, 2 object detected while opening, 3 at the position |
| 3 | 3 | gripper_temperature_error | bit |  |
| 3 | 2 | gripper_timeout_error | bit |  |
| 3 | 1 | gripper_estop_error | bit |  |
| 3 | 0 | gripper_calibrated | bit | 1 calibrated |

---

### Send_gripper_calibrate

<div class="cmd-facts" markdown><span class="fact">ID 62</span><span class="fact">host → driver</span><span class="fact">0 bytes</span><span class="fact">Python: `Send_gripper_calibrate()`</span></div>

Starts the gripper calibration (the jaws find their end stops). Needed after every power-up.

The driver does not answer this command.

---
