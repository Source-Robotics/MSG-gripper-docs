# What you need

## The gripper: buy it, or build it

The MSG gripper is sold assembled, calibrated and configured in the [Source Robotics shop](https://source-robotics.com/products/msg-gripper),
in the rail and stepper combination you choose, in black or grey. A bought gripper ships with the current STEPFOC
firmware release and the bootloader installed, its driver configured for gripper mode and its stepper calibrated.
It works out of the box; the gripper calibration (finding the end stops) runs after every power-up and is part of
normal use.

### Build your own { #build-your-own }

**The MSG is open source, and that is important to us.** Everything the gripper is made of is published in the
[product repository](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper) under the CERN Open
Hardware Licence: the STEP files of every part, the print files, the bill of materials with a link for every item,
the assembly video, and the URDF and MJCF models. The driver's firmware and the software that drives the gripper
are open source too. A gripper you build is the same gripper as the one from the shop, and this manual applies
to it; and you can change the jaws, the camera mount or the body for your application, or fit the gripper to a
robot it was not designed for.

| Step | Where |
|---|---|
| 1. Choose a rail length for the stroke and a stepper length for the force | [Variants](variants.md) |
| 2. Print the parts: `Common parts`, the body and the jaw carriers of your rail (`Linear rail dependant parts`), the cover of your stepper (`Stepper dependant parts`), and the jaws | [STEP files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/STEP%20files), [Print files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/Print%20files) (3MF, ready to slice). PETG, 25 % infill; TPU for the jaw pads |
| 3. Source the rest: the stepper, the STEPFOC driver, the encoder magnet, the thermistor, the MGN7 rail and carriages, the pinion, the shaft coupler, the M8 connector and the internal cables, inserts and screws, the camera | [BOM](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/blob/main/BOM.md) |
| 4. Configure the driver before the pinion goes in: the motor calibration, gripper mode, the thermistor | [Driver configuration](../05-setup/driver-configuration.md) |
| 5. Assemble | [Assembly video](https://youtu.be/oAUhDKYgLso) |
| 6. Cable it, calibrate, make the first moves | [The cable](../04-installation/cable.md), [Calibrate, activate, move](../05-setup/first-moves.md) |

!!! warning
    A self-built gripper is yours to make safe: the thermistor in the windings, the current within the stepper's
    rating, and the [Safety](../02-safety.md) chapter apply to it as to a bought one. The gripper is in beta: expect
    rough edges in the hardware and the software.

If the calibration of a self-built gripper does not find both end stops, the mechanism is too stiff: loosen the
rail, check the pinion's depth in the racks, grease.

## A cable and a 24 V supply

The gripper is powered and controlled through one M8 4-pin cable: 24 V, GND, CANH, CANL.

| Where the gripper goes | Cable |
|---|---|
| PAROL6 | the [PAROL6 gripper cable](https://source-robotics.com/products/gripper-cable) from the shop |
| PAR6 | the PAR6 gripper cable (the shop; coming soon), wired differently from the PAROL6 one |
| a bench, or your own robot | a cable you make from an M8 4-pin connector and four wires, see [The cable](../04-installation/cable.md) |

!!! danger "The two robot cables differ"
    PAROL6 and PAR6 put the four signals on different pins. A cable for the wrong robot, or a self-made cable with
    a wrong pin, puts 24 V where the CAN bus belongs and destroys the gripper's driver. Check the pinout before
    you plug in a cable for the first time.

On the bench, a 24 V supply with a current limit (2 A is plenty for one gripper) is the safest source.

## A CAN interface

The gripper talks CAN. On a robot, the robot's control board provides the bus. On a PC, the
[CANvas USB-to-CAN adapter](https://source-robotics.com/products/canvas-usb-to-can-adapter) does; it shows up as a
serial port and works with Motor GUI, the Python library and the ROS 2 driver. Any adapter that `python-can` supports works
with the library.

## Software

- **Motor GUI**, [motorgui.com](https://motorgui.com/), in the browser over the CANvas adapter: the recommended
  tool to test and set up a gripper, with a gripper panel for the MSG and the SSG-48; see
  [Motor GUI](../05-setup/motor-gui.md). The earlier [SSG-gripper-GUI](https://github.com/Source-Robotics/SSG-gripper-GUI),
  a Python program, is legacy.
- **Python**: `pip install Spectral-BLDC`, the library the ROS 2 driver is built on; see
  [With Python](../06-operation/python.md).
- **ROS 2**: the [msg_gripper_ros2](https://github.com/Source-Robotics/source_robotics_msg_gripper_ros2) package;
  see [With ROS 2](../06-operation/ros2.md).
- **PAROL6 and PAR6**: the robots' own software drives the gripper; see [On PAROL6 and PAR6](../06-operation/robots.md).
- **For a self-built gripper**: a 3.3 V USB-to-serial adapter ([serial adapter](https://source-robotics.com/products/usb-to-serial-adapter))
  for the driver's UART port, to configure the driver with Motor GUI or a terminal; see
  [Driver configuration](../05-setup/driver-configuration.md).

## Optional

- **Jaws** for your objects: the printed jaws in the repository (solid, hollow, or with a TPU pad), sponge tape
  for the gripping faces, or your own design; see [Jaws](../04-installation/jaws.md).
- **A camera**: an OV9732 USB module for the camera mount; see [Variants](variants.md).
