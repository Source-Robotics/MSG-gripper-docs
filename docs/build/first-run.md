# Driver setup and first run

A gripper from the shop arrives with its driver configured: the stepper calibrated, gripper mode on, the
thermistor on, the gains set, everything saved. A gripper you build has a bare STEPFOC driver that must be
brought to the same state once, over its UART port. This page is that procedure; the commands are the driver's,
and the [STEPFOC documentation](https://docs.source-robotics.com/STEPFOC-docs/) explains each in depth.

## What you need

- The driver mounted on the stepper with its encoder magnet, before the pinion is engaged in the racks: the
  motor calibration turns the motor several revolutions in both directions, which the racks cannot follow. Do
  this step with the stepper out of the gripper or with the pinion not yet fitted.
- A 3.3 V [USB-to-serial adapter](https://source-robotics.com/products/usb-to-serial-adapter) on the driver's
  UART connector, a terminal at 256000 baud with CR+LF line endings, and 24 V on the driver's power connector.
  [The serial terminal](https://docs.source-robotics.com/STEPFOC-docs/latest/05-setup/terminal/) on the STEPFOC
  site shows the terminal setup.
- The thermistor from the BOM, soldered to the driver's thermistor connector and fixed to the motor housing
  with thermal cement.

## With Motor GUI

[Motor GUI](../05-setup/motor-gui.md), connected over **UART** through the serial adapter, has a preset per stepper on its
setup page: *MSG 21.5 mm motor*, *MSG 40 mm motor* and *MSG 60 mm motor*. A preset writes the stepper's
resistance, inductance and 50 pole pairs, the current limit, the loop gains, gripper mode, the thermistor and
the CAN ID, then saves; its CAN ID is 6, the PAR6 gripper's, so change it before applying for another robot.
Apply it after the motor calibration of step 1: it does step 2 for you.

## 1. The motor calibration

Restore the defaults first, so that nothing from another motor or junk in the EEPROM goes into the calibration,
then enter the stepper's parameters and calibrate:

| Stepper | `#PP` | `#R` | `#L` |
|---|---|---|---|
| 21.5 mm, 17HS08-1004S | 50 | 3.7 | 0.0045 |
| 40 mm, 17HS16-2004S1 | 50 | 1.1 | 0.0026 |
| 60 mm, 17HS24-2104S | 50 | 1.6 | 0.0030 |

```
#Default
#PP 50
#R 1.1
#L 0.0026
#Cal
```

The motor turns, the driver prints each step and ends with `Calibration success!`. The whole routine and its
messages are in [Calibration](https://docs.source-robotics.com/STEPFOC-docs/latest/05-setup/calibration/) on
the STEPFOC site. `#Default` also resets the serial number the driver reports; note what `#Info` printed if you
need it.

## 2. The gripper settings

```
#Gripper 1
#Term 1
#Tlim 75
#Kpiq 1.4047
#Kiiq 0.1149
#CANID 0
#Save
```

| Command | What it does |
|---|---|
| `#Gripper 1` | gripper mode: the driver runs the gripper state machine and answers the gripper messages |
| `#Term 1`, `#Tlim 75` | the thermistor on, the temperature limit at 75 °C. Without it the motor can burn out under a long grip |
| `#Kpiq 1.4047`, `#Kiiq 0.1149` | the current loop gains of Motor GUI's gripper presets, the same for the three steppers; the gains the calibration computes for the stepper are sharper than a gripper needs |
| `#CANID 0` | the node ID on the robot's bus; 0 to 13, see [Over CAN](../06-operation/can.md) |
| `#Save` | nothing above survives a power cycle until it is saved |

## 3. Assemble and calibrate the gripper

Fit the pinion and assemble the gripper, power it up, and run the gripper calibration (`#Gripcal`, or Motor GUI's
**Calibrate**): the jaws open fully and close fully. Then a first move at a low current, as in
[Calibrate, activate, move](../05-setup/first-moves.md). `#Gripinfo` prints the gripper's state, including the end stops the
calibration found.

## Current limit

The gripper's moves use the current limit of each command, not the driver's `#Ilim`. Keep the commanded current
at or below the stepper's maximum current ([Force and speed](../03-technical-data/force-and-speed.md)); the
firmware does not clamp it.
