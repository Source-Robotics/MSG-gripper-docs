# Gripper

| Command | Kind | Argument | What it does | Response |
|---|---|---|---|---|
| `#Gripper` | Set/Get | int: 0 or 1 | Whether this driver is a gripper. A gripper has it set and saved; `#Default` clears it, so set it again after restoring the defaults. | the flag |
| `#Gripcal` | Action |  | Starts the gripper calibration (the jaws find their end stops). Enters **gripper calibration** mode. | `Gripper calibration!` |
| `#Gripinfo` | Get |  | Prints the gripper state: calibrated, activated, end stops, position, current. | the report |
| `#Gripstop` | Set/Get | int: 0 or 1 | The gripper E-stop bit. | the bit |
| `#Gripact` | Set/Get | int: 0 or 1 | The activate bit. | the bit |
| `#Gripcur` | Set/Get | int: current in mA | The current limit of gripper moves, the grip force. The firmware does not clamp it; keep it at or below the stepper's rated current (see Force and speed). | the setpoint |
| `#Gripvel` | Set/Get | int: 0 to 255 | The speed setpoint of gripper moves. | the setpoint |
| `#Grippos` | Set/Get | int: 0 (open) to 255 (closed) | The position setpoint; also activates the gripper, sets the action bit and goes to gripper mode. Enters **gripper** mode. | the current position |
