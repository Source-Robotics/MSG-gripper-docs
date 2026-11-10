# Gripper

| Command | Kind | Argument | What it does | Response |
|---|---|---|---|---|
| `#Gripper` | Set/Get | int: 0 or 1 | Whether this driver is a gripper. A gripper has it set and saved; `#Default` clears it, so set it again after restoring the defaults. | the flag |
| `#Gripcal` | Action |  | Starts the gripper calibration (the jaws find their end stops). Clear any error first; until `#Gripinfo` reports it calibrated, send no `#Grippos` or `#Clear`, which end it. Enters **gripper calibration** mode. | `Gripper calibration!` |
| `#Gripinfo` | Get |  | Prints the gripper state: gripper mode, calibrated, activated, the position, speed and current setpoints, the E-stop and action bits, the object detection, and the end stops in encoder ticks. | the report |
| `#Gripstop` | Set/Get | int: 0 or 1 | The gripper E-stop bit. While it is 1, the E-stop error is raised again at every cycle: set it to 0 before `#Clear`. | the bit |
| `#Gripact` | Set/Get | int: 0 or 1 | The activate bit. | the bit |
| `#Gripcur` | Set/Get | int: current in mA | The current limit of gripper moves, the grip force. The firmware clamps it only at 2800 mA; keep it at or below the stepper's rated current (see Force and speed). | the setpoint |
| `#Gripvel` | Set/Get | int: 0 to 255 | The speed setpoint of gripper moves. | the setpoint |
| `#Grippos` | Set/Get | int: 0 (open) to 255 (closed) | The position setpoint; also activates the gripper, sets the action bit and goes to gripper mode. Enters **gripper** mode. | the current position |
