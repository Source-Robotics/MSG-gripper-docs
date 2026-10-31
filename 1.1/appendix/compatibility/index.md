# Versions and compatibility

Which STEPFOC firmware release works with which bootloader, gripper hardware, Python library and ROS 2 driver.
One row per firmware release, newest first; the last column names the version of this site, a gripper release, that
describes it.

| Firmware (STEPFOC) | Released | Bootloader | MSG gripper | Python library (Spectral-BLDC) | ROS 2 driver | Docs (gripper release) |
|---|---|---|---|---|---|---|
| 108 | 2026-08-26 | required (installed on grippers shipped with 104 or newer) | V1.1 | 1.20 or newer | msg_gripper_ros2 (ROS 2 Humble) | 1.1 |
| 107 | 2026-08-24 | required | V1.1 | 1.20 or newer | msg_gripper_ros2 | not published |
| 106 | 2026-07-05 | required | V1.1 | 1.19 or newer | msg_gripper_ros2 | not published |
| 105 | 2026-07-04 | required (the first release that needs it) | V1.1 | 1.19 or newer | msg_gripper_ros2 | not published |
| 103 | 2025-12-28 | none (flashed with a programming adapter) | V1.1 | 1.17 or newer | msg_gripper_ros2 | the STEPFOC site, version 103 |

Send_Respond_Device_Info returns the firmware release a gripper runs; `#Info` prints it over UART.
