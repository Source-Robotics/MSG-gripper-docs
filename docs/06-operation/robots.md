# On PAROL6 and PAR6

The gripper is made for the Source Robotics arms. Both drive it over their own CAN bus; their software calibrates
it, moves it and reads its state, so a program for the robot does not talk CAN itself. What any robot's software
needs to carry the gripper, the tool centre point, the mass, the centre of mass and the inertia, is on
[Data for robot integration](../03-technical-data/integration-data.md).

## PAROL6

### Mounting and connecting

1. Replace the gripper's `ring_cover` with `ring_cover-PAROL6` from the STEP files' `Common parts`
   ([Mounting on a robot](../04-installation/mounting.md)). It bolts to the robot's last joint, and the coupler
   plate's shaft coupler (8 mm bore, two M4 clamp screws) takes the joint 6 shaft.
2. Slide the gripper onto the shaft with the camera looking down between the jaws, and tighten the two clamp
   screws with blue threadlocker.
3. Connect the [PAROL6 gripper cable](https://source-robotics.com/products/gripper-cable) between the gripper and
   the M8 connector at the forearm. Only this cable: the PAR6 cable is wired differently and destroys the gripper
   ([The cable](../04-installation/cable.md)).
4. Route the camera's USB cable outside the arm, with slack for joints 4, 5 and 6, and fix it so that the arm
   cannot catch it.
5. Keep the gripper's node ID at 0 and set its termination switch ON; it is the last node on the robot's bus.

### The joint 5 homing offset

Joint 5 homes against the tool, and the control board firmware's default offset (8900) is for the pneumatic
gripper holder, not for the MSG's ring cover. After the first homing, check joint 5 with the pin through its
witness marks. If it is off, measure the offset and set `j5_homing_offset` in `main.cpp` of the control board
firmware, as the PAROL6 documentation's mastering page describes.

### Driving it

The gripper calibrates after every power-up and does not move before that. Clear the gripper's errors first, then
calibrate, then wait until the calibration is done, up to about ten seconds: a gripper move or a clear sent while
it runs ends the calibration.

=== "Commander software"
    The **Gripper** tab: after homing the robot, press **Clear gripper error**, then **Calibrate gripper**, and
    wait until the status says calibrated. Then set the position, speed and current with the sliders and press
    **Move GoTo**. In RBTscript: `Gripper_cal()`, `Delay(10)`, then `Gripper(position, speed, current)`, with the
    current in mA.

=== "Python API"
    ```python
    import time

    rbt.select_tool("MSG", variant_key="150mm")           # the parol6 package; 100mm, 150mm or 200mm: the rail
    rbt.tool.calibrate()                                   # with the robot at rest
    time.sleep(10)                                         # the calibration takes up to about ten seconds
    rbt.tool.set_position(0.8, speed=0.5, current=0.4)     # fractions; current 0.4 is 1180 mA
    print(rbt.tool.status())
    ```

    The API allows the calibration 2 s before it sends the next gripper action, which is too short for the MSG;
    the pause above waits for the calibration to finish.

The Python API's `current` is a fraction of the range 100 to 2800 mA: the gripper gets 100 + 2700 × `current` mA,
so 1.0 is 2800 mA, more than any of the steppers takes. Keep it within the stepper's maximum
([Force and speed](../03-technical-data/force-and-speed.md)):

| Stepper | Maximum current | Largest `current` |
|---|---|---|
| 21.5 mm | 1.5 A | 0.51 |
| 40 mm | 2.0 A | 0.70 |
| 60 mm | 2.1 A | 0.74 |

`position` and `speed` are fractions of the position and speed bytes: 0.8 is position 204, 0.5 is speed 128.

The [PAROL6 documentation](https://docs.source-robotics.com/PAROL-docs/) covers the robot's side: the gripper
port, the commander software, the API and the tool centre point.

## PAR6

The PAR6 arm's control box runs the gripper on its CAN bus as a tool, with the PAR6 gripper cable (different from
the PAROL6 one). The [PAR6 documentation](https://docs.source-robotics.com/par6/) covers the tool configuration,
the runtime's gripper commands and the firmware updates the box can do for the gripper.

## Another robot

Any controller with a CAN interface drives the gripper directly: [Over CAN](can.md) is the protocol,
[With Python](python.md) and [With ROS 2](ros2.md) are two ready implementations, and the
[CAN reference](../reference/can/index.md) has every byte.
