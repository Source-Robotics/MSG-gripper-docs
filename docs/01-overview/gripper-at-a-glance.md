# The gripper at a glance

The MSG is a two-jaw parallel gripper driven by a stepper motor under field-oriented control. The
[STEPFOC driver](https://docs.source-robotics.com/STEPFOC-docs/) on the back of the stepper regulates the motor's
current, so the gripper controls not only where its jaws are and how fast they move but how hard they press: the
current limit of a move is the grip force. The jaws stop on an object and hold it with that force, and the driver
reports that an object was found. That makes the gripper safe to use around people, gentle enough for soft
objects, and informative enough for data collection and learning: it is built with a camera mount that looks
between the jaws, for teleoperation and for training vision-language-action models.

<figure markdown="span">
  ![The MSG gripper](../assets/MSG_banner.png){ width="900" }
  <figcaption>Figure 1: The MSG gripper with the 150 mm rail and the camera mount.</figcaption>
</figure>

## How it works

| Part | What it does |
|---|---|
| NEMA 17 stepper motor, 21.5, 40 or 60 mm long | the actuator; its length sets the grip force: about 20, 50 or 76 N at the rated current |
| STEPFOC driver on the back of the stepper | field-oriented control of the stepper, the gripper state machine, the CAN and UART interfaces |
| Pinion on the motor shaft, two racks on a linear rail | the pinion turns, the two racks move in opposite directions: the jaws open and close symmetrically |
| MGN7 linear rail, 100, 150 or 200 mm | carries the jaws; its length sets the stroke |
| Jaws | printed, in several shapes, with a soft TPU pad or solid; yours to adapt |
| Thermistor in the motor windings | temperature protection: the gripper stops at 75 °C |
| M8 4-pin connector | 24 V and the CAN bus, one cable to the robot |
| Camera mount | an OV9732 USB camera module looking between the jaws |
| Coupler plate | mounts the gripper on an 8 mm shaft, or on the PAROL6 wrist with its own cover |

The driver's status LED and its UART port are inside the housing; the CAN termination switch is reachable
through the stepper cover ([CAN termination](../04-installation/can-termination.md)).

## What the firmware does

The gripper runs the STEPFOC firmware with its gripper mode turned on. After power-up it calibrates by finding
both end stops, then it accepts move commands: a jaw position from 0 (open) to 255 (closed), a speed from 0 to
255 and a current limit in mA. During a move the driver watches speed and current: when the jaws stop before the
target with the current at its limit, an object is in the way and the gripper holds it; when they reach the
target, it holds the position. The state the gripper reports with every answer says which: moving, object found
while closing, object found while opening, or at the position. [How the gripper works](../06-operation/how-it-works.md)
has the details.

The gripper protects itself: it stops on an over-temperature of the motor, on an E-stop bit from the host, on a
CAN watchdog that runs out, and on every fault the driver itself detects (supply voltage, encoder, driver stage).
[Errors and recovery](../06-operation/errors.md) says what each means.

## How it is controlled

- **CAN**, 1 Mbit/s, on the same cable as the power: one message moves the gripper and is answered with its
  state. From a PC with the CANvas adapter, from a ROS 2 node, from PAROL6 or PAR6, or from your own controller.
  See [Over CAN](../06-operation/can.md).
- **Python**, the `Spectral-BLDC` library on top of CAN. See [With Python](../06-operation/python.md).
- **Motor GUI** in the browser: connect, calibrate, open and close, watch the plots. See [Motor GUI](../05-setup/motor-gui.md).
- **UART**, the driver's serial port inside the housing: for configuration, and for a self-built gripper. See
  [Over UART](../06-operation/uart.md).
