# With ROS 2

The [msg_gripper_ros2](https://github.com/Source-Robotics/source_robotics_msg_gripper_ros2) package is a ROS 2
Humble driver for the gripper, built on the Python library and a `python-can` adapter. It was developed by the
UCLA Biomechatronics Lab and Ben Forbes, and is MIT licensed.

## What it offers

| Direction | Topic or action | Type |
|---|---|---|
| Command | `/gripper/command_joint_states` | `sensor_msgs/JointState`, the position as the gripper's own units, 0 to 255 |
| Feedback | `/gripper/feedback_joint_states` | `sensor_msgs/JointState`, the position in the same units and the effort in mA |
| Action | `/gripper_command` | `control_msgs/GripperCommand` |

## Installing

Ubuntu 22.04 with ROS 2 Humble, Python 3.10 or newer, and a USB-to-CAN adapter that speaks slcan, such as the
CANvas:

```bash
pip install Spectral_BLDC python-can
cd ~/ros2_ws/src
git clone https://github.com/Source-Robotics/source_robotics_msg_gripper_ros2.git
cd ~/ros2_ws
colcon build --packages-select msg_gripper_ros2
source install/setup.bash
```

On Linux, add yourself to the `dialout` group to open the adapter's port without `sudo`, and log in again.

## Running

```bash
ros2 launch msg_gripper_ros2 msg_gripper_launch.py
```

The only setting that depends on your machine is the adapter's port, `channel` in `config/default.yaml`:
`/dev/ttyACM0` or `/dev/ttyUSB0` on Linux, `/dev/tty.usbmodem*` on macOS, `COM3` on Windows. Copy the file,
change it, and pass it at launch:

```bash
ros2 launch msg_gripper_ros2 msg_gripper_launch.py config_file:=~/my_gripper.yaml node_name:=my_gripper namespace:=robot
```

The package's README has the rest: the parameters, the node names, and the platforms it was tested on.

## The SSG-48 package

The [ssg48_adaptive_electric_gripper_ros2](https://github.com/Lass6230/ssg48_adaptive_electric_gripper_ros2)
package, written for the SSG-48 gripper, speaks the same protocol and should work with the MSG as well.

## The description files

The URDF and the MJCF of the gripper for ROS 2, Gazebo and MuJoCo are in the product repository's
[MSG_gripper_description](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/MSG_gripper_description).
