---
hide:
  - toc
---

# MSG Gripper Manual

![MSG gripper](assets/hero.png){ .hero }

<!-- doc-meta: msg -->

[Quick start](quick-start.md){ .md-button .md-button--primary } [About this manual](about.md){ .md-button }

Source Robotics d.o.o. publishes this document for the MSG compliant AI stepper gripper. It is revised as the
product and its firmware change; the document number, firmware version, revision and date above identify the
version you are reading, and the document history on the About page says what changed. The gripper runs the
STEPFOC driver's firmware: take care that the firmware version named under *Applies to* matches what the gripper
reports; the version selector in the header switches between firmware releases. The text and the images are
licensed CC BY-SA 4.0, the code examples MIT.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Quick start**

    ---

    [One page](quick-start.md) from the box to a gripper that opens and closes on command, through the gripper
    GUI or Python, with a link into the manual at every step.

-   :material-book-open-variant:{ .lg .middle } **The manual**

    ---

    [Safety](02-safety.md), [Technical data](03-technical-data/index.md), [Installation](04-installation/index.md),
    [First setup](05-setup/index.md), [Operation](06-operation/index.md), [Firmware](07-firmware.md),
    [Troubleshooting](08-troubleshooting.md).

-   :material-robot-industrial:{ .lg .middle } **On a robot**

    ---

    [PAROL6 and PAR6](06-operation/robots.md), [ROS 2](06-operation/ros2.md), [Python](06-operation/python.md):
    the gripper from the robot's own software, from a ROS 2 node, or from your program over CAN.

-   :material-code-braces:{ .lg .middle } **API reference**

    ---

    The gripper's [CAN messages](reference/can/index.md) and [UART commands](reference/uart/index.md), the
    [status bits](reference/errors.md) and the [Python library](reference/python.md), read from the firmware.

-   :material-hammer-wrench:{ .lg .middle } **Build your own**

    ---

    [The guide](guides/build.md): print the parts for your rail and stepper, source the rest from the BOM,
    assemble, configure the driver.

</div>
