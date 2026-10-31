# The gripper at a glance

The MSG is a two-jaw parallel gripper driven by a NEMA 17 stepper under field-oriented control. The
[STEPFOC driver](https://docs.source-robotics.com/STEPFOC-docs/) on the back of the stepper regulates the motor's
current, so a move sets not only where the jaws go and how fast, but how hard they press: the current limit is the
grip force. The jaws stop on an object, hold it with that force, and the driver reports that an object was found.
We designed the MSG specifically for teleoperation, VLA (vision-language-action) training and physical
intelligence. A camera on top of the body looks down between the jaws, from a place chosen for a clear view of
both jaws and the object between them.

<figure markdown="span">
  ![The MSG gripper](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/MSG_banner.webp){ width="900" }
  <figcaption>Figure 1: The MSG gripper with the 150 mm rail and the camera mount.</figcaption>
</figure>

## The parts

| Part | What it does |
|---|---|
| NEMA 17 stepper motor, 21.5, 40 or 60 mm long | the actuator; its length sets the grip force: about 31, 50 or 76 N at its maximum current |
| STEPFOC driver on the back of the stepper | field-oriented control of the stepper, the gripper state machine, the CAN and UART interfaces |
| Pinion on the motor shaft, two racks on a linear rail | the pinion turns, the two racks move in opposite directions: the jaws open and close symmetrically |
| MGN7 linear rail, 100, 150 or 200 mm | carries the jaws; its length sets the stroke |
| Jaws | printed, in several shapes, with a soft TPU pad or solid; yours to adapt |
| Thermistor on the motor housing | temperature protection: the gripper stops at 75 °C |
| M8 4-pin connector | 24 V and the CAN bus, one cable to the robot |
| Camera mount | an OV9732 USB camera module looking between the jaws |
| Coupler plate | mounts the gripper on an 8 mm shaft, or on the PAROL6 wrist with its own cover |

The driver's status LED and its UART port are inside the housing; the CAN termination switch is reachable
through the stepper cover ([CAN termination](https://docs.source-robotics.com/MSG-gripper-docs/1.1/04-installation/can-termination/)).

## What the firmware does

After power-up the gripper calibrates by finding both end stops. Then it takes move commands: a position from 0
(open) to 255 (closed), a speed from 0 to 255 and a current limit in mA. When the jaws stop short of the target
with the current at its limit, an object is in the way and is held; when they reach the target, the position is
held. Every answer carries the state: moving, object found while closing or opening, or at the position. The
gripper stops itself on an over-temperature, an E-stop bit from the host, a CAN watchdog that runs out, and every
fault the driver detects. [How the gripper works](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/how-it-works/) and
[Errors and recovery](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/errors/) have the details.

## How it is controlled

- **CAN**, 1 Mbit/s, on the same cable as the power: one message moves the gripper and is answered with its
  state. From a PC with the CANvas adapter, from a ROS 2 node, from PAROL6 or PAR6, or from your own controller.
  See [Over CAN](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/can/).
- **Python**, the `Spectral-BLDC` library on top of CAN. See [With Python](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/python/).
- **Motor GUI** in the browser: connect, calibrate, open and close, watch the plots. See [Motor GUI](https://docs.source-robotics.com/MSG-gripper-docs/1.1/05-setup/motor-gui/).
- **UART**, the driver's serial port inside the housing: for configuration, and for a self-built gripper. See
  [Over UART](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/uart/).
