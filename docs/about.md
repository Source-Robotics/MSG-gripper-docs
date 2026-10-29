# About this manual

The MSG Gripper Manual covers the MSG compliant AI stepper gripper from unpacking to a gripper that works on a robot: mounting and cabling, the
first setup with Motor GUI, control over CAN and UART, from Python, from ROS 2 and from the PAROL6 and PAR6
robots, and firmware updates. It is written for a maker, a student or an engineer who can plug in a cable and run
a Python script. Read [Safety](02-safety.md) before you power anything; [First setup](05-setup/index.md) is the
shortest path to a gripper that moves.

The gripper is a STEPFOC stepper driver in gripper mode. The driver itself, from its full command set to its calibration
and its bootloader, is documented on the [STEPFOC site](https://docs.source-robotics.com/STEPFOC-docs/); this manual links there instead of
repeating it.

## Finding your way

--8<-- "navigation.md"

## Warnings and notes

--8<-- "symbols.md"

## Related documents

<!-- documents-table -->

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
| 2026.A (draft) | — | First version in this form: the manual chapters, the generated CAN and UART reference; gripper release 1.1, firmware 108 |
