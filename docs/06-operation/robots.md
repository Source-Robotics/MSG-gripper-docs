# On PAROL6 and PAR6

The gripper is made for the Source Robotics arms. Both drive it over their own CAN bus; their software calibrates
it, moves it and reads its state, so a program for the robot does not talk CAN itself.

## PAROL6

1. Mount the gripper with the `ring_cover-PAROL6` part ([Mounting on a robot](../04-installation/mounting.md)).
2. Connect it with the [PAROL6 gripper cable](https://source-robotics.com/products/gripper-cable) to the
   robot's gripper port. Only this cable: the PAR6 cable is wired differently and destroys the gripper
   ([The cable](../04-installation/cable.md)).
3. Keep the gripper's node ID at 0 and set its termination switch ON; it is the last node on the robot's bus.

The PAROL6 commander software has the electric gripper's controls: calibrate, then a position, a speed and a
current for a move, and the gripper's status. The PAROL6 Python API drives it as a tool, from a program:

```python
rbt.select_tool("MSG", variant_key="150mm")           # the parol6 package; 100mm, 150mm or 200mm, the rail
rbt.tool.calibrate()                                   # queued with the motion; lasts a few seconds
rbt.tool.set_position(0.8, speed=0.5, current=0.4)     # fractions of the ranges
print(rbt.tool.status())
```

The [PAROL6 documentation](https://docs.source-robotics.com/PAROL-docs/) covers the robot's side: the gripper
port, the commander software and the API.

## PAR6

The PAR6 arm's control box runs the gripper on its CAN bus as a tool, with the PAR6 gripper cable (different from
the PAROL6 one). The [PAR6 documentation](https://docs.source-robotics.com/par6/) covers the tool configuration,
the runtime's gripper commands and the firmware updates the box can do for the gripper.

## Another robot

Any controller with a CAN interface drives the gripper directly: [Over CAN](can.md) is the protocol,
[With Python](python.md) and [With ROS 2](ros2.md) are two ready implementations, and the
[CAN reference](../reference/can/index.md) has every byte.
