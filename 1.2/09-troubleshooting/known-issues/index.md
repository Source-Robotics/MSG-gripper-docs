# Known issues

The faults in the gripper's firmware and in the software that drives it that are known and not yet fixed, and
what to do until they are. The pages that describe each part say the same where it matters; this page collects
them in one place. Which versions work together is in [Versions and compatibility](https://docs.source-robotics.com/MSG-gripper-docs/1.2/appendix/compatibility/).

### STEPFOC firmware

Seen in: 108 (the driver's firmware, gripper mode).

| | What happens | What to do | More |
|---|---|---|---|
| KI-1 | After a gripper command with the E-stop bit set, the E-stop error comes back at every control cycle for as long as the last gripper command carries the bit, so a clear seems to do nothing. | First send a gripper command with the E-stop bit at 0 and the action bit at 0 (`#Gripstop 0` over UART), then clear. | [Errors and recovery, clearing](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/errors/#clearing) |
| KI-2 | The answer to a full gripper command is sent before the gripper acts on it, so it carries the state from before the command, for example object detection 3 of the move before. | Ignore that answer. Poll with empty Send_gripper_data_pack frames, and give a move about 100 ms before you trust its object detection. | [How the gripper works, the answer](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/how-it-works/#the-answer) |
| KI-3 | A full gripper command or a clear sent while the gripper calibration runs ends it, and the gripper stays uncalibrated. The routine's progress and its 24 s timer are not reset, so the next calibration can start part way through or give up early. | Clear first, then calibrate, and send only empty status polls until the calibrated bit is 1. After an interrupted calibration, switch the gripper off and on before you calibrate again. | [How the gripper works, the states](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/how-it-works/#the-states) |
| KI-4 | The action status in the gripper's answer is the action bit of the last command as it was received; the gripper never clears it, so it stays 1 after a move has finished and while the gripper holds. | Follow a move by its object detection (0 moving, 1 or 2 object found, 3 at the position), not by the action status. | [How the gripper works, the answer](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/how-it-works/#the-answer) |
| KI-5 | The motor calibration (`#Cal`) leaves the driver's current limit at 1600 mA, whatever it was before, which is more than the 21.5 mm stepper's 1.5 A. Gripper moves use the current of each command; the limit applies when the driver runs as a motor (Motor GUI's Motor side, the UART motor modes). | After `#Cal`, set `#Ilim` to the stepper's maximum current (1500, 2000 or 2100) before `#Save`, or apply Motor GUI's MSG preset, which sets the current limit. | [Driver setup, current limit](https://docs.source-robotics.com/MSG-gripper-docs/1.2/build/first-run/#current-limit) |

### Python library (Spectral-BLDC)

Seen in: 1.20.

| | What happens | What to do | More |
|---|---|---|---|
| KI-6 | `UnpackData` assembles `gripper_object_detection` with its two bits swapped: it reports 1 where the gripper sends 2 (object found while opening) and 2 where it sends 1 (object found while closing); 0 and 3 are right. | Swap 1 and 2 in your program, or test for "1 or 2" when any object will do. | [With Python](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/python/#the-first-program) |

### PAROL6 Python API (parol6)

Seen in: 0.9.1.

| | What happens | What to do | More |
|---|---|---|---|
| KI-7 | `tool.status()` does not follow the gripper's status byte: `engaged` reads true at all times, and `part_detected` comes from bits 3 and 2 of the byte, which hold the temperature and timeout errors, not the object detection. The calibrated and error bits are not in it. | Use the jaw position (`positions`) and the current (`channels`), and check where the jaws stopped to know that a part is held. | [On PAROL6 and PAR6, driving it](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/robots/#driving-it) |
| KI-8 | `calibrate()` counts the calibration done after a fixed 2 s without reading the calibrated bit; the next gripper action then ends a calibration that is still running, and the MSG's takes up to about ten seconds. The API has no action that clears the gripper's errors. | Wait about 10 s after `calibrate()` before the next gripper action. Clear a gripper error with the commander's **Clear gripper error** or with Motor GUI, then calibrate. | [On PAROL6 and PAR6, driving it](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/robots/#driving-it) |
| KI-9 | The MSG's `current` is a fraction of 100 to 2800 mA, so `current=1.0` commands 2800 mA, more than any of the three steppers takes, and the firmware does not clamp it. | Keep `current` at or below 0.51 (21.5 mm stepper), 0.70 (40 mm) or 0.74 (60 mm). | [On PAROL6 and PAR6, driving it](https://docs.source-robotics.com/MSG-gripper-docs/1.2/06-operation/robots/#driving-it) |

## Something that is not here

Check [Troubleshooting](https://docs.source-robotics.com/MSG-gripper-docs/1.2/09-troubleshooting/) first. If it is still not explained,
[Report a problem](https://docs.source-robotics.com/MSG-gripper-docs/1.2/support/report-a-problem/) says what to include so it can be reproduced. A fixed issue
stays on this page, under "Fixed", with the version that fixes it.
