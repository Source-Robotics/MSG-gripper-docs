# Quick start

From an assembled MSG gripper to its first gentle open and close, using Motor GUI on a PC.
For a gripper already connected to a robot, use [On PAROL6 and PAR6](06-operation/robots.md).

!!! danger "Before connecting power"
    Keep fingers and loose objects out of the stroke. Calibration opens and closes the jaws fully. A wrong
    cable can put 24 V on the CAN pins and destroy the driver: check the [numbered pinout](03-technical-data/connector.md#pin-numbers).

## 1. Choose your starting point

| Your gripper | Start here |
|---|---|
| Bought assembled | Its stepper is already calibrated and the driver configured. Continue below; the jaws still need calibration after each power-up. |
| Self-built, or a replacement driver or stepper | Finish [Driver setup and first run](build/first-run.md) first, then return here. Do not apply a factory preset to a bought gripper just to try this page. |
| No hardware yet | Open [Motor GUI](https://motorgui.com/), choose **Mock CAN (demo)** and **Connect**, then switch to **Gripper**. The demo is an SSG-48; the control panel is shared with MSG. |

## 2. Gather and mount

You need a mounted gripper with jaws/fingers fitted, a **24 V supply**, a correctly wired **M8 cable**, a
**CANvas USB-to-CAN adapter**, and Chrome or Edge. The [What you need](01-overview/what-you-need.md) page lists
the parts; [Mounting](04-installation/mounting.md) and [Jaws](04-installation/jaws.md) cover the mechanics.

**Check:** the body cannot shift, the jaws travel freely, and the cable cannot enter their path.

## 3. Wire with power off

1. Check the cable against [Connector and pinout](03-technical-data/connector.md): gripper pin 3 is +24 V,
   pin 4 GND, pin 2 CANH, pin 1 CANL. Check continuity before the first power-up.
2. Connect the supply and the CANvas adapter as shown below.
3. Set the gripper's CAN termination ON for this two-node bench bus; the CANvas adapter provides the other end.
   Leave the gripper at its shipped node ID, **0**, unless you already assigned another.

```mermaid
flowchart LR
    PC[PC USB] --> A[CANvas adapter]
    A -- CANH --> P2[Gripper pin 2: CANH]
    A -- CANL --> P1[Gripper pin 1: CANL]
    S[24 V supply] -- positive --> P3[Gripper pin 3: +24 V]
    S -- return --> P4[Gripper pin 4: GND]
```

**Check, unpowered:** the supply polarity and cable pinout match, and CANH-to-CANL measures about **60 Ω**
with the bus connected. Otherwise check [The cable](04-installation/cable.md) and
[CAN termination](04-installation/can-termination.md) before powering it.

## 4. Connect Motor GUI

Power the gripper, plug the CANvas adapter into USB, and open [motorgui.com](https://motorgui.com/).
Choose **CAN (slcan)** at **1 Mbit/s**, press **Connect**, and choose the adapter's serial port.
Select node **0** (or your assigned ID) and switch from **Motor** to **Gripper**.

**Check:** position and current feedback arrive. *Not calibrated* after power-up is normal. If feedback is
missing, check the power, port, node ID and termination: [Troubleshooting](09-troubleshooting.md).
If a fault disables the controls, resolve it using [Errors and recovery](06-operation/errors.md).
The [illustrated Motor GUI guide](05-setup/motor-gui.md) shows the panel.

## 5. Calibrate and activate

With the stroke empty and the gripper deactivated, press **Calibrate**, read the prompt, and press
**Start calibration**. Let the jaws find both end stops. Follow [Calibrate, activate, move](05-setup/first-moves.md)
for the full procedure, then **Activate** and check for faults.

**Check:** the panel says **Calibrated**, **Activated**, and **No errors** before you command a move.
A calibration that times out after 24 seconds has not found its end stops; do not continue as if it passed.
Use [Calibration troubleshooting](09-troubleshooting.md#calibration).

## 6. Make the first move

Set **Speed 30** and **Current 300 mA**, applying each with its **Set** button. Press **Open**, then **Close**.
After that works, put a light test object between the jaws and repeat, keeping fingers clear.

**Check:** the position follows the command; on an object the jaws stop before fully closed and the panel reports
an object. If it does not move, slips or reports an error, use [Troubleshooting](09-troubleshooting.md).
The current limit sets an approximate force limit; [Force and speed](03-technical-data/force-and-speed.md)
explains the relationship and the motor's limits.

## 7. Finish and continue

Remove the test object before deactivating or switching off: the grip may release. Disconnect Motor GUI and
switch off the supply before changing cables.

| Next task | Guide |
|---|---|
| Control it from a program | [With Python](06-operation/python.md), [With ROS 2](06-operation/ros2.md) |
| Put it on a robot | [On PAROL6 and PAR6](06-operation/robots.md) |
| Inspect a CAN frame or download DBC definitions | [CAN frame tool and downloads](reference/can-tools.md) |
| Diagnose a problem | [Troubleshooting](09-troubleshooting.md), [Errors and recovery](06-operation/errors.md) |
