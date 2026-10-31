---
hide:
  - toc
comments: false
---

# MSG Gripper Manual

![MSG gripper](assets/hero.webp){ .hero }

<!-- doc-meta: msg -->

[Quick start](quick-start.md){ .md-button .md-button--primary } [About this manual](about.md){ .md-button }

Source Robotics d.o.o. publishes this document for the MSG compliant AI stepper gripper. It is revised as the gripper and its
firmware change; the document number, the gripper release, the firmware, the revision and the date above identify
the version you are reading, and the document history on the About page says what changed. The version selector
in the header switches between gripper releases. The gripper runs the STEPFOC driver's firmware: take care that
the firmware named under *Applies to* matches what the gripper reports. The text and the images are licensed
CC BY-SA 4.0, the code examples MIT.

**The MSG is open source, and that is important to us.** Everything the gripper is made of is published: the
CAD and print files, the bill of materials, the assembly instructions, the driver's firmware and the software that
drives it. Buy the gripper assembled, or build one yourself; change the jaws or the body for your application and
fit it to any robot. The [build guide](build/index.md) is the order to do it in.

**Made for teleoperation and robot learning.** We designed the MSG specifically for teleoperation, VLA
(vision-language-action) training and physical intelligence. The camera on top of the body is placed with care:
it looks down between the jaws at an angle that keeps both jaws, and the object between them, in view, the
picture a teleoperator and a learning model need.

<div class="gripper-viewer" data-base="assets/models/msg/" markdown="0">
  <canvas class="gripper-viewer__canvas" aria-label="The MSG gripper in 3D: drag to turn, scroll to zoom"></canvas>
  <div class="gripper-viewer__controls">
    <label class="gripper-viewer__field">Opening <input type="range" name="opening" min="0" max="100" value="50"></label>
    <label class="gripper-viewer__field">Body <span class="gripper-viewer__swatches" data-target="body"></span><input type="color" name="body" value="#d2d2cf" title="Any colour"></label>
    <label class="gripper-viewer__field">Jaws <span class="gripper-viewer__swatches" data-target="jaws"></span><input type="color" name="jaws_color" value="#1a1a1a" title="Any colour"></label>
    <button type="button" name="reset" class="md-button">Reset view</button>
  </div>
  <p class="gripper-viewer__hint">Drag to turn the gripper, scroll to zoom, open and close the jaws, try the colours. The model is the
repository's <a href="https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/MSG_gripper_description">URDF</a> of the 150 mm rail variant; the shop sells the body in black and grey.</p>
</div>

<div class="grid cards" markdown>

-   :material-play-circle:{ .lg .middle } **Quick start**

    ---

    [One-page quick start](quick-start.md): choose the cable, check the bus, connect Motor GUI, calibrate,
    and make the first gentle open and close. Each step says what to check before continuing.

-   :material-book-open-variant:{ .lg .middle } **The manual**

    ---

    [Safety](02-safety.md), [Technical data](03-technical-data/index.md), [Installation](04-installation/index.md),
    [First setup](05-setup/index.md), [Operation](06-operation/index.md), [Maintenance](07-maintenance.md), [Firmware](08-firmware.md),
    [Troubleshooting](09-troubleshooting.md).

-   :material-robot-industrial:{ .lg .middle } **On a robot**

    ---

    [PAROL6 and PAR6](06-operation/robots.md), [ROS 2](06-operation/ros2.md), [Python](06-operation/python.md):
    the gripper from the robot's own software, from a ROS 2 node, or from your program over CAN.

-   :material-code-braces:{ .lg .middle } **API reference**

    ---

    The gripper's [CAN messages](reference/can/index.md) and [UART commands](reference/uart/index.md), the
    [status bits](reference/errors.md) and the [Python library](reference/python.md), read from the firmware.

-   :material-hammer-wrench:{ .lg .middle } **Open source: build your own**

    ---

    [The build guide](build/index.md): the repository's bill of materials, printing, the assembly, the driver's
    setup and the first run. The same manual applies.

</div>
