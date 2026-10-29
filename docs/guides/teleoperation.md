# Teleoperation with two grippers

Two grippers on one CAN bus, coupled so that each follows the other: squeeze one by hand and the other closes;
when the other meets an object, the one in your hand pushes back with the force it feels. A hundred lines of
Python, and the basis of a teleoperation setup with force feedback.

This guide does not use the gripper mode. Both drivers run in **current (torque) mode**, the driver's own motion
command, and the PC closes a position loop between them at a fixed rate. The gripper mode's position, speed and
object detection are not involved; the drivers are plain torque sources here.

## What you need

- Two grippers, calibrated as motors (a bought gripper is), with different node IDs: 0 and 1 (`#CANID 1`,
  `#Save` on one of them over UART).
- Both on one bus with the CANvas adapter, 24 V on both, termination at the two ends.
- `pip install Spectral-BLDC SourceRoboticsToolbox`.

!!! warning
    In current mode the gripper has no end-stop knowledge and no object detection: it pushes with whatever current
    the loop commands. Set the driver's current limit to the stepper's rating (`#Ilim`) on both grippers, start
    with low gains, and keep fingers out of the jaws.

## The idea

Each driver is commanded a current proportional to the difference between the two positions, plus a damping
term on the speed difference and a little damping of its own motion:

$$
I_0 = K_p\,(p_1 - p_0) + K_d\,(v_1 - v_0) - K_k\, v_0, \qquad
I_1 = K_p\,(p_0 - p_1) + K_d\,(v_0 - v_1) - K_k\, v_1
$$

$p$ is the jaw position of each gripper in the same units, $v$ its speed. When the two positions agree, both
currents are zero and the grippers rest. Move one by hand and the difference drives the other after it; block
the other, and the difference drives the one in your hand back with the same current, which is the force you
feel. $K_p$ is the stiffness of the virtual spring between them, $K_d$ its damping.

The two drivers' encoders do not read the same number at the same jaw position, so each position is referred to
a reference reading taken once with both grippers in the same position; the Source Robotics Toolbox's `Joint`
does that bookkeeping and unwraps the encoder over its 16384-tick turns.

## The code

```python
import time
import numpy as np
import Spectral_BLDC as Spectral
import SourceRoboticsToolbox as Toolbox

INTERVAL_S = 0.002                 # the loop rate: 500 Hz
REFERENCE = [10440, 13555]         # each gripper's raw encoder reading with both jaws in the same position

Kp, Kd, Kk = 650, 0.0055, 0.0003   # stiffness, damping between the two, damping of each

bus = Spectral.CanCommunication(bustype='slcan', channel='COM123', bitrate=1000000)
motors = [Spectral.SpectralCAN(node_id=i, communication=bus) for i in (0, 1)]
joints = [Toolbox.Joint(encoder_resolution=14, master_position=REFERENCE[i], gear_ratio=1, offset=0, dir=0)
          for i in (0, 1)]

position = np.zeros(2)             # each gripper's position, referred to its reference
sector_known = [False, False]
current = [0, 0]

while True:
    t0 = time.perf_counter()
    for i in (0, 1):               # command the currents; each answer carries position and speed
        motors[i].Send_data_pack_1(Position=None, Speed=None, Current=int(current[i]))
    for _ in (0, 1):
        message, ids = bus.receive_can_messages(timeout=0.001)
        if ids is None:
            continue
        i = ids[0]
        motors[i].UnpackData(message, ids)
        if not sector_known[i]:
            joints[i].determine_sector(motors[i].position)
            sector_known[i] = True
        position[i] = joints[i].get_joint_position(motors[i].position)

    current[0] = Kp * (position[1] - position[0]) + Kd * (motors[1].speed - motors[0].speed) - Kk * motors[0].speed
    current[1] = Kp * (position[0] - position[1]) + Kd * (motors[0].speed - motors[1].speed) - Kk * motors[1].speed

    time.sleep(max(0.0, INTERVAL_S - (time.perf_counter() - t0)))
```

The reference readings: with both grippers powered and their jaws set by hand to the same opening, read each
driver's position (`#Info` over UART, or `Send_Respond_Encoder_data` from Python) and put the two numbers in
`REFERENCE`.

## Tuning

Start with `Kp` at a tenth of the value above and raise it until the follower tracks the leader without lagging;
raise `Kd` if the pair oscillates. The current the formula produces is in mA and is clamped by each driver's
`#Ilim`, so the stepper's rating is the ceiling of the force feedback. A fixed loop rate matters: a loop that
runs at an uneven rate makes the damping terms noisy.

The full example, with a timer for a precise loop rate, is
[gripper_teleop_PC_calc.py](https://github.com/Source-Robotics/Spectral-BLDC-Python/tree/main/examples/Advanced/SSG48%20gripper%20bilateral%20teleop)
in the Python library's examples, and the [bilateral teleoperation guide](https://docs.source-robotics.com/STEPFOC-docs/latest/guides/bilateral-teleoperation/)
on the STEPFOC site explains the control law with a joint instead of a gripper.
