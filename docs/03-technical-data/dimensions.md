# Dimensions and CAD

The gripper's dimensions depend on the rail and the stepper: the rail length sets the width (100, 150 or 200 mm
plus the jaws at full opening), the stepper length what sticks out behind the body. The STEP files of every part
and of the whole gripper in each variant are in the product repository, and are the reference for anything that
has to fit:

- [STEP files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/STEP%20files):
  `Common parts` (the coupler plate, the ring covers, the camera mount, the jaw blocker, the stepper spacer),
  `Linear rail dependant parts` (the body and the jaw carriers per rail length), `Stepper dependant parts` (the
  covers and spacers per stepper length), `Gripper jaws attachment` (the jaw designs), `Tools` (the magnet tool).
- [Print files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/Print%20files):
  the same parts as 3MF, ready to slice.

<figure markdown="span">
  ![The STEP model](../assets/MSG_3D_model.png){ width="600" }
  <figcaption>Figure 8: The STEP model of the gripper, seen from the coupler plate.</figcaption>
</figure>

## For simulation

The [MSG_gripper_description](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/MSG_gripper_description)
folder has a URDF of the gripper for ROS 2 and Gazebo and an MJCF for MuJoCo 3.1.3 and newer, with a scene file.

[CAD and downloads](../cad-files.md) lists everything that can be downloaded.
