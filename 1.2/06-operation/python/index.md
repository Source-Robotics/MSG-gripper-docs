# With Python

The `Spectral-BLDC` library wraps the driver's CAN protocol, gripper messages included: one method per message,
and the gripper's answers unpacked into attributes. The ROS 2 driver and the legacy gripper GUI are built on it.

## Installing

In a virtual environment, with Python 3.10 or newer:

=== "Windows"
    ```
    py -m venv .venv
    .venv\Scripts\activate
    pip install Spectral-BLDC
    ```
    The CANvas adapter's port is `COM` and a number: Device Manager lists it under **Ports (COM & LPT)**. Give it
    as `channel='COM20'`.

=== "Linux"
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install Spectral-BLDC
    sudo usermod -aG dialout $USER     # access to the adapter's port; log out and in again once
    ```
    The adapter's port is `/dev/ttyACM0` (`ls /dev/ttyACM*` lists it).

=== "macOS"
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install Spectral-BLDC
    ```
    The adapter's port is `/dev/tty.usbmodem` and a number (`ls /dev/tty.usbmodem*` lists it).

The library pulls `python-can` and `pyserial`. The source and the examples are in
[Spectral-BLDC-Python](https://github.com/Source-Robotics/Spectral-BLDC-Python).

## The first program

```python
import Spectral_BLDC as Spectral
import time

# the adapter: a CANvas on COM20 (Windows) or /dev/ttyACM0 (Linux), 1 Mbit/s
bus = Spectral.CanCommunication(bustype='slcan', channel='COM20', bitrate=1000000)
gripper = Spectral.SpectralCAN(node_id=0, communication=bus)

gripper.Send_Clear_Error()                      # clear first: with an error active, the calibration does not run
gripper.Send_gripper_calibrate()                # the jaws open fully, then close fully
for _ in range(120):                            # wait for the calibrated bit, up to 24 s
    time.sleep(0.2)
    gripper.Send_gripper_data_pack()            # only empty frames now: a move or a clear ends the calibration
    message, ids = bus.receive_can_messages(timeout=0.05)
    if message is not None:
        gripper.UnpackData(message, ids)
        if gripper.gripper_calibrated:
            break

for position in (200, 20, 200, 20):
    # position 0..255, speed 0..255, current mA, activate, action, E-stop, release direction
    gripper.Send_gripper_data_pack(position, 30, 300, 1, 1, 0, 0)
    bus.receive_can_messages(timeout=0.05)      # its answer still carries the state from before the move
    time.sleep(0.1)                             # give the move time to start
    for _ in range(40):                         # poll the state for up to 2 s
        gripper.Send_gripper_data_pack()        # an empty frame: status only
        message, ids = bus.receive_can_messages(timeout=0.05)
        if message is not None:
            gripper.UnpackData(message, ids)
            print(gripper.gripper_position, gripper.gripper_current, gripper.gripper_object_detection)
            if gripper.gripper_object_detection in (1, 2, 3):   # object found, or at the position
                break
```

The answer to a move command is sent before the gripper acts on it, so it still carries the state from before:
after a finished move, object detection 3. The example reads that answer and drops it. At the very start of a
move the jaws are still slow, and with the current near its limit the object detection can briefly read 1 or 2;
the pause of 0.1 s covers that. While the gripper calibration runs, send only empty frames: a full command or
Send_Clear_Error ends the calibration, and the gripper stays uncalibrated.

`Send_gripper_data_pack` with all seven arguments sends the move; without arguments it sends the empty status
poll. `receive_can_messages` returns the raw `python-can` message and the node ID, command ID and error bit from
the identifier; `UnpackData` fills the gripper attributes:

| Attribute | Meaning |
|---|---|
| `gripper_position` | 0 open to 255 closed |
| `gripper_current` | the motor current in mA |
| `gripper_activated`, `gripper_action_status` | the activate flag; the action bit of the last command, which stays 1 while the gripper holds |
| `gripper_object_detection` | 0 moving, 1 object found while closing, 2 object found while opening, 3 at the position |
| `gripper_temperature_error`, `gripper_timeout_error`, `gripper_estop_error` | the three error bits |
| `gripper_calibrated` | the gripper calibration is done |

!!! note "Object detection in library 1.20 and older"
    Library 1.20 and older assemble `gripper_object_detection` with its two bits swapped relative to the firmware:
    they report 1 where the gripper sends 2 (object found while opening) and 2 where it sends 1 (object found
    while closing); 0 and 3 are unaffected. 1.21 and newer read them right. The example tests for "1 or 2", which
    is right with every version.

## Stopping

```python
gripper.Send_gripper_data_pack(20, 30, 300, 1, 1, 1, 0)   # the E-stop bit: stops, raises the E-stop error
gripper.Send_gripper_data_pack(20, 30, 300, 1, 0, 0, 0)   # to recover: first the bit back at 0, action 0
gripper.Send_Clear_Error()                                 # then clear; while the bit is 1, the error comes back
gripper.Send_Watchdog(500)                                 # from now on the gripper stops 500 ms after the last frame
```

With the watchdog set, keep the status poll running at a steady rate; a program that crashes releases the grip
within the watchdog time.

## Several grippers

One `CanCommunication` per bus, one `SpectralCAN` per gripper with its node ID; every answer carries the node ID
in `ids.node_id`, so route it to the right object. The [teleoperation guide](https://docs.source-robotics.com/MSG-gripper-docs/1.2/guides/teleoperation/) couples
two grippers this way.

The complete map of calls to messages is in the [Python library](https://docs.source-robotics.com/MSG-gripper-docs/1.2/reference/python/) reference.
