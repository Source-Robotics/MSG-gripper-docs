# Calibrate, activate, move

Every session with the gripper starts the same way: calibrate, activate, clear what errors there are. Then it
moves. This page does it once with the GUI, with Python and over UART; [How the gripper works](../06-operation/how-it-works.md)
explains what happens inside.

!!! danger
    The jaws move over the whole stroke during calibration, and close with the set force afterwards. Nothing in
    reach of them, fingers included.

## 1. Power up

At power-up the gripper reports *Not calibrated* and does not move. Its stepper must be calibrated too, which a
bought gripper is from the factory; a self-built gripper gets that in [Driver configuration](driver-configuration.md).

## 2. Calibrate

The gripper calibration finds the two end stops: the jaws open fully, pause, then close fully, at low force
(500 mA) and low speed. Each end is recognised when the jaws have stood still against it for half a second. It
takes about ten seconds; the result is not kept over a power cycle, so this runs at every power-up.

=== "Gripper GUI"
    **Calibrate**. When the jaws stop, section 3 shows *Calibrated*.

=== "Python"
    ```python
    gripper.Send_gripper_calibrate()
    time.sleep(10)
    ```

=== "UART"
    ```
    #Gripcal
    ```

If the jaws do not move at all, or move to one end and stop: the gripper is in an error state (clear it first, see
step 4), or the stepper is not calibrated. If the routine runs for 24 seconds and gives up, an end stop was not
found: something blocks the jaws short of the end, or the mechanism is too stiff for 500 mA.

## 3. Activate

A calibrated gripper carries out a move only while it is activated.

=== "Gripper GUI"
    **Activate**. Section 3 shows *Activated*.

=== "Python"
    The activate bit is part of every move command (the fourth argument below); send it as 1.

=== "UART"
    `#Grippos` activates by itself; `#Gripact 1` activates without moving.

## 4. Clear errors

The driver powers up in an error state until its motor is calibrated and it has run through its checks; an
E-stop, an over-temperature or a supply fault leave an error too. A gripper with an error does not move.

=== "Gripper GUI"
    **Clear**, when section 3 shows an error.

=== "Python"
    ```python
    gripper.Send_Clear_Error()
    ```

=== "UART"
    ```
    #Clear
    ```

An error whose cause is still present comes straight back; [Errors and recovery](../06-operation/errors.md) says
what each needs.

## 5. Move

A move is three numbers: the position (0 open, 255 closed), the speed (0 to 255) and the current limit in mA, which
is the grip force ([Force and speed](../03-technical-data/force-and-speed.md)). Start with speed 30 and 300 mA.

=== "Gripper GUI"
    Set *Speed* 30 and *Current* 300 with their **Set** buttons. Move the *Position* slider: the jaws follow, the
    plots show the position and the current, and *Object detection* says whether the jaws reached the position
    or stopped on something.

=== "Python"
    ```python
    gripper.Send_gripper_data_pack(200, 30, 300, 1, 1, 0, 0)   # position, speed, current, activate, action, E-stop, release direction
    time.sleep(2)
    gripper.Send_gripper_data_pack(20, 30, 300, 1, 1, 0, 0)
    ```

=== "UART"
    ```
    #Gripvel 30
    #Gripcur 300
    #Grippos 200
    #Grippos 20
    ```

Put an object between the jaws and close on it: the jaws stop on it and hold it with 300 mA, and the state reads
*object detected while closing*. Raise the current for a firmer grip, within the stepper's rating, and the speed
once the motion is what you want.

## What the gripper reports

Every move command is answered with the gripper's state, which the GUI shows in sections 3 and 4 and the
library puts into attributes: the position, the current, whether it is calibrated and activated, whether a move
is in progress, the object-detection result, and the three error bits. [How the gripper works](../06-operation/how-it-works.md)
goes through them.
