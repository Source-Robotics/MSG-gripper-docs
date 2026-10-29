# Quick start

From the box to a gripper that opens and closes on command, on one page. The quickest way through is the
[gripper GUI](05-setup/gripper-gui.md) on a PC with the CANvas adapter; every step also shows the Python call,
and ends with a link to the chapter that explains it. Follow the link when a step is not clear or something fails.

!!! danger "Read first"
    The jaws close with enough force to injure a finger, and the gripper moves by itself during calibration. Keep
    hands out of the jaws, start with a low current and speed, and read the [Safety](02-safety.md) chapter: it is
    two minutes long.

## 1. What you need

| | Where to get it |
|---|---|
| **MSG gripper**, assembled | [the shop](https://source-robotics.com/products/msg-gripper); or [build your own](guides/build.md) |
| **A gripper cable**: M8 4-pin to the robot or to your own wiring | [PAROL6 gripper cable](https://source-robotics.com/products/gripper-cable); for a bench setup, [a cable you make](04-installation/cable.md) |
| **A 24 V supply**, on the robot or on the bench | a bench supply with a current limit of 2 A is the safest start |
| **CANvas USB-to-CAN adapter** for a PC, or a robot with its own CAN bus | [CAN adapter](https://source-robotics.com/products/canvas-usb-to-can-adapter) |
| **Software**: the gripper GUI, or Python with the `Spectral-BLDC` library | [SSG-gripper-GUI](https://github.com/Source-Robotics/SSG-gripper-GUI) (Windows build in its releases), `pip install Spectral-BLDC` |

Read in more detail: [What you need](01-overview/what-you-need.md).

## 2. Mount it, or clamp it

On a robot: the coupler plate fits an 8 mm shaft; PAROL6 takes its own ring cover. On the bench: clamp the body
so that the jaws can move freely over their whole stroke, with nothing in reach of them.

Read in more detail: [Mounting on a robot](04-installation/mounting.md).

## 3. Connect

1. The cable to the M8 connector on the gripper: it carries **24 V, GND, CANH and CANL**, nothing else.
2. The other end to the robot's gripper port, or on the bench to the supply and to the CANvas adapter's CAN
   terminals. The gripper has its own termination switch; on a short bench bus turn it **ON**.
3. Power on.

!!! danger "Cables"
    PAROL6 and PAR6 use different gripper cables, and a cable with the wrong pinout destroys the gripper's
    driver. Use the cable made for your robot, or check every pin of your own against the pinout.

Read in more detail: [The cable](04-installation/cable.md) · [Connector and pinout](03-technical-data/connector.md) ·
[CAN termination](04-installation/can-termination.md).

## 4. Calibrate

After every power-up the gripper has to find its end stops: it opens fully, then closes fully, at low force, in
about ten seconds.

=== "Gripper GUI"
    Enter the CANvas adapter's COM port and the gripper's CAN ID (0 unless you changed it), **Connect**, then
    **Calibrate**. The jaws move; when they stop, the status shows *Calibrated*.

=== "Python"
    ```python
    import Spectral_BLDC as Spectral, time
    bus = Spectral.CanCommunication(bustype='slcan', channel='COM20', bitrate=1000000)
    gripper = Spectral.SpectralCAN(node_id=0, communication=bus)
    gripper.Send_Clear_Error()
    gripper.Send_gripper_calibrate()
    time.sleep(10)
    ```

Read in more detail: [Calibrate, activate, move](05-setup/first-moves.md).

## 5. Activate and clear errors

A calibrated gripper still does nothing until it is activated. If the status shows an error (the driver reports
*Not calibrated* as an error until the stepper itself is calibrated, which a bought gripper already is), clear it.

=== "Gripper GUI"
    **Activate**, and **Clear** if an error is shown.

=== "Python"
    The activate bit travels with every move command, see the next step; `gripper.Send_Clear_Error()` clears.

## 6. Move it

A move is a position (0 open, 255 closed), a speed (0 to 255) and a current limit in mA, which is the force. Start
low: speed 30, current 300.

=== "Gripper GUI"
    Set *Speed* to 30 and *Current* to 300 with their **Set** buttons, then move the *Position* slider. The jaws
    follow; the plots show position and current.

=== "Python"
    ```python
    gripper.Send_gripper_data_pack(200, 30, 300, 1, 1, 0, 0)   # position, speed, current, activate, action, E-stop, release direction
    time.sleep(2)
    gripper.Send_gripper_data_pack(20, 30, 300, 1, 1, 0, 0)
    ```

Put something between the jaws and close on it: the gripper stops on the object, holds it with the set current,
and reports *object detected*. Raise the current for a firmer grip, within the stepper's rating.

Read in more detail: [How the gripper works](06-operation/how-it-works.md) · [Force and speed](03-technical-data/force-and-speed.md).

## 7. Where to go next

| You want to | Read |
|---|---|
| use the gripper on PAROL6 or PAR6 | [On PAROL6 and PAR6](06-operation/robots.md) |
| drive it from ROS 2 | [With ROS 2](06-operation/ros2.md) |
| write your own control program | [With Python](06-operation/python.md), [Over CAN](06-operation/can.md) |
| understand the status and the errors it reports | [Errors and recovery](06-operation/errors.md) |
| change the jaws | [Jaws](04-installation/jaws.md) |
| build a gripper yourself | [Build your own](guides/build.md) |
| update the firmware | [Firmware](07-firmware.md) |
| look up a message or a command | [API reference](reference/index.md) |
