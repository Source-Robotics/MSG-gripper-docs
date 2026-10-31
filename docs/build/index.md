# Build guide

**The MSG is open source, and that is important to us.** Everything the gripper is made of is published in the
[product repository](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper) under the CERN Open
Hardware Licence: the STEP and print files of every part, the bill of materials with a link for every item, the
assembly video, and the URDF and MJCF models. The driver's firmware and the software that drives the gripper are
open source too. A gripper you build is the same gripper as the one from the shop, and this manual applies to
it; change the jaws, the camera mount or the body for your application, or fit the gripper to a robot it was not
designed for. This guide is the order to do it in.

!!! warning
    A self-built gripper is yours to make safe: the thermistor on the motor, the current within the stepper's
    maximum, and the [Safety](../02-safety.md) chapter apply to it as to a bought one. The gripper is in beta:
    expect rough edges in the hardware and the software.

## The steps

1. Choose a rail length for the stroke and a stepper length for the force: [Variants](../01-overview/variants.md).
2. [Bill of materials](bill-of-materials.md): the repository's BOM, with the reference images.
3. [Printing the parts](printing.md): PETG at 25 % infill, the folders for your rail and stepper, the jaws.
4. [Mechanical assembly](mechanical-assembly.md): the video, the order, the cable.
5. [Driver setup and first run](first-run.md): the motor calibration before the pinion goes in, gripper mode,
   the thermistor, the first moves.

## Kits and the shop

You do not have to source everything yourself:

| | What is in it | You add |
|---|---|---|
| [STEPFOC starter kit](https://source-robotics.com/products/stepfoc-starter-kit) | the STEPFOC driver, the CANvas USB-to-CAN adapter, the USB-to-serial adapter, an ST-Link with the programming adapter, the UART, power and CAN cables, the 6 × 2.5 mm encoder magnet, the 100K thermistor | the stepper, the rail and its carriages, the pinion, the shaft coupler, the M8 connector, the screws and inserts, the camera, the printed parts |
| [STEPFOC driver](https://source-robotics.com/products/stepfoc-stepper-controller) alone | the driver | the rest, and the adapters its setup needs |
| [Assembled MSG gripper](https://source-robotics.com/products/msg-gripper) | the gripper, built, calibrated and configured, in the rail, stepper and colour you choose | the [cable](https://source-robotics.com/products/gripper-cable) |

The starter kit is the good-value start for a build: it has the driver and everything the driver's setup needs,
the CAN adapter for Motor GUI, the serial adapter for the UART, the magnet, the thermistor and the two internal
cables, for little more than the driver alone. The [PAROL6 gripper cable](https://source-robotics.com/products/gripper-cable)
is in the shop too.
