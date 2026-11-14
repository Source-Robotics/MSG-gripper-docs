# About this manual

The MSG Gripper Manual covers the MSG compliant AI stepper gripper from unpacking to a gripper that works on a robot: mounting and cabling, the
first setup with Motor GUI, control over CAN and UART, from Python, from ROS 2 and from the PAROL6 and PAR6
robots, and firmware updates. It is written for a maker, a student or an engineer who can plug in a cable and run
a Python script. Read [Safety](https://docs.source-robotics.com/MSG-gripper-docs/1.2/02-safety/) before you power anything; [First setup](https://docs.source-robotics.com/MSG-gripper-docs/1.2/05-setup/) is the
shortest path to a gripper that moves.

The gripper is a STEPFOC stepper driver in gripper mode. The driver itself, from its full command set to its calibration
and its bootloader, is documented on the [STEPFOC site](https://docs.source-robotics.com/STEPFOC-docs/); this manual links there instead of
repeating it.

## Finding your way

Four tabs: **MSG Gripper Manual**, the numbered chapters, read from the start; **API reference**, the gripper's CAN
messages, UART commands, status bits and Python calls, for looking things up (the driver's complete reference is on
the STEPFOC site); **Guides**, worked examples; **Support**, help and problem reports.

The dropdown next to the site name switches between gripper releases, and a page of an older release says so in a
bar at the top. The repository card in the header opens the product repository; every page ends with a link to
edit it and one to report a problem with it.
## Warnings and notes

!!! note "Note"
    Points out something that is easy to miss or that changes what follows: a default, a limit, a side effect.

!!! warning "Notice"
    The robot, the tool, or data on the control box can be damaged or lost if this is ignored. Nobody is at risk.

!!! danger "Danger"
    Someone can be injured if this is ignored. Stop and read the whole box before acting on the step it belongs to.
## Related documents

| Document | Number | Covers |
|---|---|---|
| MSG Gripper Manual | SR-5003 | the MSG compliant AI stepper gripper: safety, technical data, installation, setup, operation over CAN, UART, Python and ROS 2, firmware, the build guide; the gripper's API reference; guides |

A document marked with a firmware release describes MSG gripper release 1.2 running STEPFOC firmware 110. The version selector in the header switches between gripper releases; a new firmware release for the same gripper updates the pages in place. The compatibility table says which firmware, Python library and hardware revisions work together.

The driver inside the gripper is documented at [https://docs.source-robotics.com/STEPFOC-docs/](https://docs.source-robotics.com/STEPFOC-docs/). The SSG-48 gripper, the MSG's predecessor on the Spectral Micro driver, is at [docs.source-robotics.com/SSG48-gripper-docs](https://docs.source-robotics.com/SSG48-gripper-docs/). The robots the gripper is
made for: [docs.source-robotics.com/PAROL-docs](https://docs.source-robotics.com/PAROL-docs/) and
[docs.source-robotics.com/par6](https://docs.source-robotics.com/par6/).

## Document history

The manual is versioned by gripper release, the version the product repository tags (the selector in the header);
within a release it follows the STEPFOC firmware the gripper runs, with a new revision letter per update. The
text and the images are licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), the code
examples [MIT](https://github.com/Source-Robotics/MSG-gripper-docs/blob/main/LICENSE-CODE); the hardware design is published under the CERN Open Hardware Licence v2, strongly reciprocal in the
[product repository](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper). The Source Robotics name, the product names and the logos are not covered
by any of these.

| Revision | Date | Changes |
|---|---|---|
| 2026.E | 2026-11-13 | STEPFOC firmware 110: a move ends cleanly, with a few mA left (KI-11); a soft start; 0 and 255 reached without pressing on the stops, each end read under a light push (KI-12); an object reported after 50 ms of standstill; the gripper pushes with its own current and leaves the driver's limit alone (KI-13); the calibration restarts from the beginning and needs 1000 ticks of stroke (KI-3); brake or coast saved (KI-14); a watchdog that runs out while idle starts no hold (KI-15); parameters 90 to 93; `#Estop` over UART. The MSG 21.5 mm preset's values tuned on firmware 110 (Motor GUI 0.7.0) |
| 2026.D | 2026-11-10 | STEPFOC firmware 109: the generated CAN and UART reference; the encoder table and the anti-cogging that follow `#Cal` in the first run, and the presets' gains on 109; a poll right after a move no longer cancels it (KI-10); calibration puts the current limit back (KI-5); the gripper's current clamped at 2800 mA. Python library 1.21, which reads the object detection right (KI-6) |
| 2026.C | 2026-11-05 | The M8 pinout corrected to the one the gripper is built with (1 +24 V, 2 CANL, 3 GND, 4 CANH; page 17 of the SSG-48 assembly manual): the pin table, its drawing and the quick start of 2026.B had all four pins wrong; the bootloader comes with STEPFOC release 105, not 104; the camera works with any webcam software; the cable warnings: the other robot's cable reverses the supply, it does not put 24 V on the CAN pins; the PAROL6 cable's pin pairs |
| 2026.B | 2026-11-04 | Gripper release 1.2, with the files as downloads on the release; dimension drawings and what changes per variant; data for robot integration (frame, mass, inertia, TCP); known issues; the downloads with their versions; safety for clothing, hair and eyes, a caught finger, static and cleaning; check boxes after each step and Windows, Linux and macOS tabs; numbered figure captions; the 380 g variant |
| 2026.A | 2026-11-03 | First version in this form: the manual chapters, the generated CAN and UART reference; gripper release 1.1, firmware 108 |
