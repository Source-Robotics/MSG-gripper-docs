# Driver setup and first run

A gripper from the shop arrives with its driver configured: the stepper calibrated, gripper mode on, the
thermistor on, the gains set, everything saved.

A gripper you build has a bare STEPFOC driver that must be
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

Static electricity damages the driver: touch earthed metal before you handle it, hold it by its edges, and
connect and disconnect its cables with the supply off.

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
the STEPFOC site. `#Default` also resets the serial number the driver reports; note what `#SERNUM` prints before
you start if you need it.

!!! note "STEPFOC firmware 109 and newer"
    From STEPFOC firmware 109 a successful `#Cal` is followed by two runs of its own, the encoder table and the
    anti-cogging: the motor turns slowly for about another minute, and the driver saves everything when they
    finish. Keep the pinion off until then, and start step 2 when `#Info` no longer shows `running:` under
    `In force:`. The encoder-table run holds 80 % of the current limit in the coils for some 20 s; after
    `#Default` the limit is 1700 mA, so set `#Ilim` for the stepper (its maximum in
    [Force and speed](../03-technical-data/force-and-speed.md)) before `#Cal`. See
    [Calibration](https://docs.source-robotics.com/STEPFOC-docs/latest/05-setup/calibration/) on the STEPFOC
    site.

!!! success "Check"
    The terminal ends with `Calibration success!`, and `#Info` prints `Calibrated`, `Number of pole pairs: 50` and
    the resistance and inductance you entered. If it ends with `Calibration failed!`, the STEPFOC page
    [Calibration](https://docs.source-robotics.com/STEPFOC-docs/latest/05-setup/calibration/) explains each message.

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
| `#Kpiq 1.4047`, `#Kiiq 0.1149` | the current loop gains of Motor GUI's gripper presets on firmware 108 and older, the same for the three steppers. From 109 the presets send `#Cbw 160` and each stepper's own gains (21.5 mm 4.828 / 0.5951, 40 mm 2.7033 / 0.1769, 60 mm 3.1464 / 0.2574), `#Kpv 0.014` / `#Kiv 0.00014` for the 21.5 mm and 0.02 / 0.001 for the others, and the tool id, `#Tool` 11 to 33 (tens: the rail, 1 = 100, 2 = 150, 3 = 200 mm; units: the stepper, 1 = 21.5, 2 = 40, 3 = 60 mm). On 108 the gains the calibration computes for the stepper are sharper than a gripper needs |
| `#CANID 0` | the node ID on the robot's bus; 0 to 13, see [Over CAN](../06-operation/can.md) |
| `#Save` | nothing above survives a power cycle until it is saved |

!!! success "Check"
    After a power cycle, `#Info` prints `CAN ID is: 0` and `Gripper: 1`, and `#Gripinfo` prints `I am a gripper`.
    If not, the settings were not saved: enter them again and end with `#Save`.

## 3. Assemble and calibrate the gripper

Fit the pinion and assemble the gripper, power it up, and run the gripper calibration (`#Gripcal`, or Motor GUI's
**Calibrate**): the jaws open fully and close fully. Then a first move at a low current, as in
[Calibrate, activate, move](../05-setup/first-moves.md). `#Gripinfo` prints the gripper's state, including the end stops the
calibration found.

!!! success "Check"
    The jaws opened fully and closed fully, `#Gripinfo` prints `Gripper calibrated is: 1`, and a move at a low
    current goes to its position. If the calibration gives up after 24 s:
    [Calibration](../09-troubleshooting/index.md#calibration).

## Current limit

The gripper's moves use the current limit of each command, not the driver's `#Ilim`. Keep the commanded current
at or below the stepper's maximum current ([Force and speed](../03-technical-data/force-and-speed.md)); the
firmware clamps it only at 2800 mA.
