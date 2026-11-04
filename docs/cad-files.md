# CAD and downloads

Everything to download for the MSG gripper, at the versions these pages describe. The versions come from one
file, `versions.yml`, so this page changes with them; which versions work together is in
[Versions and compatibility](appendix/compatibility.md), and the faults known in each are on
[Known issues](09-troubleshooting/known-issues.md).

## Firmware and software

| What | Version | Download | How to install |
|---|---|---|---|
| The driver's firmware (STEPFOC), which is the gripper's firmware | <!-- version-link: firmware --> | the image `stepfoc-firmware-V<number>.bin` and its manifest in the [releases](https://github.com/Source-Robotics/STEPFOC-stepper-controller/releases); the source at the tag, [STEPFOC firmware](<!-- version-url: firmware -->/STEPFOC%20firmware) | [Firmware](08-firmware.md) |
| Bootloader and its host tool, `host_tools/bl_flash.py` | | [stm32f103c-bootloader](https://github.com/Source-Robotics/stm32f103c-bootloader) | [Firmware: updating](08-firmware.md#updating) |
| Motor GUI, the browser tool for the driver and the gripper | runs in the browser, always the latest | [motorgui.com](https://motorgui.com/) | [Motor GUI](05-setup/motor-gui.md) |
| Python library (`Spectral-BLDC`) | the one in [Versions and compatibility](appendix/compatibility.md) | [Spectral-BLDC-Python](https://github.com/Source-Robotics/Spectral-BLDC-Python), `pip install Spectral-BLDC` | [With Python](06-operation/python.md) |
| ROS 2 driver | main branch | [source_robotics_msg_gripper_ros2](https://github.com/Source-Robotics/source_robotics_msg_gripper_ros2) | [With ROS 2](06-operation/ros2.md) |
| CAN definitions (JSON, DBC) for this firmware release, and the frame tool | | [CAN frame tool and downloads](reference/can-tools.md) | |
| The legacy gripper GUI, a Python program | | [SSG-gripper-GUI](https://github.com/Source-Robotics/SSG-gripper-GUI) | |

The firmware's version link opens the source at exactly that release. Motor GUI and the ROS 2 driver have no
releases these pages are tied to: Motor GUI is served in its latest version, the ROS 2 driver from its main branch.

## CAD and build files

The latest files, on the main branch of the
[product repository](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper); the gripper release
these pages describe is <!-- version-link: product -->.

| What | Where |
|---|---|
| STEP files of every part, by rail length and stepper length | [STEP files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/STEP%20files) in the product repository |
| Print files (3MF) for the body, the covers and the jaws | [Print files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/Print%20files) |
| Jaw designs: solid, hollow, with a TPU pad | [Gripper jaws attachment](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/STEP%20files/Gripper%20jaws%20attachment) |
| Bill of materials | [BOM.md](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/blob/main/BOM.md), and on this site: [Bill of materials](build/bill-of-materials.md) |
| Assembly video | [YouTube](https://youtu.be/EosuDy-heqM) |
| Cable wiring diagrams | [Building_cables.md](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/blob/main/Assembly%20manual/Building_cables.md) |
| URDF and MJCF (MuJoCo) models, standalone and on PAROL6 and PAR6 | the [msg_description](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/msg_description) guide; the files are in [robot_descriptions](https://github.com/Source-Robotics/robot_descriptions) |

## More

| What | Where |
|---|---|
| The driver's documentation | [docs.source-robotics.com/STEPFOC-docs](https://docs.source-robotics.com/STEPFOC-docs/) |
| The driver's repository | [STEPFOC-stepper-controller](https://github.com/Source-Robotics/STEPFOC-stepper-controller) |
| CANvas USB-to-CAN adapter | [CANvas-adapter](https://github.com/Source-Robotics/CANvas-adapter) |
| Safety warning and disclaimer | [SAFETY_WARNING_AND_DISCLAIMER.md](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/blob/main/SAFETY_WARNING_AND_DISCLAIMER.md) |
| This documentation | [MSG-gripper-docs](https://github.com/Source-Robotics/MSG-gripper-docs) |
| Shop | [source-robotics.com](https://source-robotics.com/products/msg-gripper) |
