# Report a problem

Open an issue in the [product repository](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/issues)
for the gripper and its files, in the [driver's repository](https://github.com/Source-Robotics/STEPFOC-stepper-controller/issues)
for the firmware, or in [Spectral-BLDC-Python](https://github.com/Source-Robotics/Spectral-BLDC-Python/issues)
for the Python library. Include:

1. **The gripper**: bought or self-built, the rail and the stepper, the jaws.
2. **The firmware release** the gripper runs: Send_Respond_Device_Info, or `#Info` over UART, which also carries
   the driver's configuration and errors.
3. **The gripper's status** when the problem happens: the state and error bits of Respond_Gripper_data_pack, or
   `#Gripinfo`.
4. **What you did and what happened**: the commands, in order, with their position, speed and current, and the
   answers.
5. **How it is connected**: the robot or the adapter, the cable, the termination; a photo helps more than a
   description.

For a problem with this documentation, the *Report it* link at the end of the page opens an issue in the
documentation repository with the page already named.
