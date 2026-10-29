# With Python

The `Spectral-BLDC` library wraps the driver's CAN protocol, gripper messages included: one method per message,
and the gripper's answers unpacked into attributes. The ROS 2 driver and the legacy gripper GUI are built on it.

## Installing

```
pip install Spectral-BLDC
```

The source and the examples are in [Spectral-BLDC-Python](https://github.com/Source-Robotics/Spectral-BLDC-Python).

## The first program

```python
import Spectral_BLDC as Spectral
import time

# the adapter: a CANvas on COM20 (Windows) or /dev/ttyACM0 (Linux), 1 Mbit/s
bus = Spectral.CanCommunication(bustype='slcan', channel='COM20', bitrate=1000000)
gripper = Spectral.SpectralCAN(node_id=0, communication=bus)

gripper.Send_Clear_Error()
gripper.Send_gripper_calibrate()
time.sleep(10)                                  # the jaws open fully, then close fully

for position in (200, 20, 200, 20):
    # position 0..255, speed 0..255, current mA, activate, action, E-stop, release direction
    gripper.Send_gripper_data_pack(position, 30, 300, 1, 1, 0, 0)
    for _ in range(40):                         # poll the state for up to 2 s
        gripper.Send_gripper_data_pack()        # an empty frame: status only
        message, ids = bus.receive_can_messages(timeout=0.05)
        if message is not None:
            gripper.UnpackData(message, ids)
            print(gripper.gripper_position, gripper.gripper_current, gripper.gripper_object_detection)
            if gripper.gripper_object_detection in (1, 2, 3):   # object found, or at the position
                break
```

`Send_gripper_data_pack` with all seven arguments sends the move; without arguments it sends the empty status
poll. `receive_can_messages` returns the raw `python-can` message and the node ID, command ID and error bit from
the identifier; `UnpackData` fills the gripper attributes:

| Attribute | Meaning |
|---|---|
| `gripper_position` | 0 open to 255 closed |
| `gripper_current` | the motor current in mA |
| `gripper_activated`, `gripper_action_status` | the activate flag; 1 while a move is in progress |
| `gripper_object_detection` | 0 moving, 1 object found while closing, 2 object found while opening, 3 at the position |
| `gripper_temperature_error`, `gripper_timeout_error`, `gripper_estop_error` | the three error bits |
| `gripper_calibrated` | the gripper calibration is done |

!!! note "Object detection in library 1.20"
    Library version 1.20 assembles `gripper_object_detection` with its two bits swapped relative to the firmware:
    it reports 1 where the gripper sends 2 (object found while opening) and 2 where it sends 1 (object found
    while closing); 0 and 3 are unaffected. Until the library is fixed, swap the two values in your program, or
    test for "1 or 2" as this example does.

## Stopping

```python
gripper.Send_gripper_data_pack(20, 30, 300, 1, 1, 1, 0)   # the E-stop bit: stops, raises the E-stop error
gripper.Send_Clear_Error()                                 # clears it; the next command must have the bit at 0
gripper.Send_Watchdog(500)                                 # from now on the gripper stops 500 ms after the last frame
```

With the watchdog set, keep the status poll running at a steady rate; a program that crashes releases the grip
within the watchdog time.

## Several grippers

One `CanCommunication` per bus, one `SpectralCAN` per gripper with its node ID; every answer carries the node ID
in `ids.node_id`, so route it to the right object. The [teleoperation guide](../guides/teleoperation.md) couples
two grippers this way.

The complete map of calls to messages is in the [Python library](../reference/python.md) reference.
