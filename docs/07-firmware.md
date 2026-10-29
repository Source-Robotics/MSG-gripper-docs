# Firmware

The gripper has no firmware of its own: it runs the STEPFOC driver's firmware with gripper mode turned on, and a
gripper release is a STEPFOC release. This site describes the release named in the version box on the landing
page; the version selector in the header switches between releases.

## Which release does my gripper run?

Over CAN, Send_Respond_Device_Info returns the firmware version as its third byte; over UART, `#Info` prints
`Software version: <number>`. The [compatibility table](appendix/compatibility.md) says which releases go with
which Python library and bootloader.

## Updating

A gripper shipped with firmware 104 or newer carries the driver's bootloader and updates over its CAN cable: the
host tells the driver to reset, the bootloader waits two seconds for a host, and the host streams the new image
into it. Nothing is opened. The image is `stepfoc-firmware-V<number>.bin` from the driver's
[GitHub releases](https://github.com/Source-Robotics/STEPFOC-stepper-controller/releases), with a manifest
`firmware.json` and the release notes.

| From | How |
|---|---|
| a PC with the CANvas adapter | [Motor GUI](https://motorgui.com/) over CAN: choose the release, the GUI fetches the image and flashes it |
| a PC, scripted | `host_tools/bl_flash.py` from the [bootloader repository](https://github.com/Source-Robotics/stm32f103c-bootloader), over CAN (slcan or gs_usb adapters) or over the driver's UART port |
| a PAR6 control box | the box updates every device on its bus, the gripper included, from its dashboard or `tools/flash_motor_firmware.py` |

The procedure, the bootloader's protocol and what to do when a flash is interrupted are in the STEPFOC
documentation: [Updating through the bootloader](https://docs.source-robotics.com/STEPFOC-docs/latest/07-firmware/update/)
and [The bootloader](https://docs.source-robotics.com/STEPFOC-docs/latest/07-firmware/the-bootloader/).

!!! warning "Before you update"
    - Open the gripper or take the object out: it loses its grip during the update and until it is calibrated
      and commanded again.
    - An update may clear the driver's configuration (the release notes say so when it does). A bought gripper's
      configuration is in [Driver configuration](05-setup/driver-configuration.md), so it can be restored; note
      what `#Info` prints before you start.
    - Give the gripper a node ID from 0 to 13: the bootloader cannot address 14 or 15.

A gripper whose driver runs firmware 103 or older has no bootloader; it is updated once with a programming
adapter on the driver's JTAG pads, inside the housing, as described in
[Installing the bootloader on an older board](https://docs.source-robotics.com/STEPFOC-docs/latest/07-firmware/bootloader/).
From then on it updates over CAN like any other.

## Release notes

The release notes of every STEPFOC release up to the one this site describes are in the appendix,
[Firmware release notes](appendix/firmware-release-notes.md).
