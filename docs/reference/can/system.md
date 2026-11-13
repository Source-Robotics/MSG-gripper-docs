# System

Node ID, stopping, saving, resetting, clearing errors, the watchdog and the heartbeat setup: the driver's system
messages a gripper host uses.

<!-- can-commands: system -->

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

The Python library 1.21 has no names for 90 to 93: use the numbers. `gripper.Send_Parameter(92, 1)` writes one;
`gripper.Send_Get_Parameter(93)` asks for one, and its answer, passed through `UnpackData`, lands in
`gripper.parameters[93]`.
