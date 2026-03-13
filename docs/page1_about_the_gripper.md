# About the Gripper


<p align="left"><img src="../assets/MSG_banner.png" alt="MSG gripper banner image" width="5000" /><br /></p>

## 📖 Project overview
The **MSG compliant AI stepper gripper** is built around [StepFOC stepper drivers](https://source-robotics.com/products/stepfoc-stepper-controller), which enable precise FOC-based force control on standard stepper motors. This makes it well-suited for assembly tasks, human-robot collaboration, and AI data collection applications — including embodied AI, teleoperation, and VLA training — thanks to its camera-friendly design.

**The gripper is modular in two key ways:**

| Option | Variants | Notes |
|--------|----------|-------|
| Rail length | 100 mm, 150 mm, 200 mm | Determines maximum grip span |
| Stepper length | 21.5 mm, 40 mm, 60 mm | Determines maximum grip force output |

**All mechanical files, firmware, and software are open source, allowing you to attach a custom gripping tool and integrate the gripper with any robotic arm or platform.**



## ⚒️ How to build / where to buy

You can buy the MSG gripper on our website: https://source-robotics.com/products/msg-gripper

If you want to source all parts yourself and build your own gripper, follow these steps:

Print parts from the STEP files folder based on your chosen configuration:

| Rail Size | Folders to Print |
|-----------|------------------|
| 100 mm | [Common parts](STEP%20files/Common%20parts) + [Linear rail dependant parts/100mm rail](STEP%20files/Linear%20rail%20dependant%20parts/100mm%20rail) + [Stepper dependant parts/\<your stepper size\>](STEP%20files/Stepper%20dependant%20parts) |
| 150 mm | [Common parts](STEP%20files/Common%20parts) + [Linear rail dependant parts/150mm rail](STEP%20files/Linear%20rail%20dependant%20parts/150mm%20rail) + [Stepper dependant parts/\<your stepper size\>](STEP%20files/Stepper%20dependant%20parts) |
| 200 mm | [Common parts](STEP%20files/Common%20parts) + [Linear rail dependant parts/200mm rail](STEP%20files/Linear%20rail%20dependant%20parts/200mm%20rail) + [Stepper dependant parts/\<your stepper size\>](STEP%20files/Stepper%20dependant%20parts) |

- Source all parts from the [BOM](https://github.com/PCrnjak/MSG-compliant-AI-stepper-gripper/blob/main/BOM.md)
- Follow the [assembly video instructions](https://youtu.be/oAUhDKYgLso) to assemble your gripper
- Follow the [docs](https://source-robotics.github.io/MSG-gripper-docs/) to get your gripper up and running

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| [Official website](https://source-robotics.com) | Buy the MSG gripper or explore other Source Robotics products |
| [DOCS](https://source-robotics.github.io/MSG-gripper-docs/) | Getting started, wiring, configuration, and full API reference |
| [Python API](https://github.com/PCrnjak/Spectral-BLDC-Python/tree/main) | Control the gripper from Python over CAN bus |
| [BOM](https://github.com/PCrnjak/MSG-compliant-AI-stepper-gripper/blob/main/BOM.md) | Complete list of parts needed to build the gripper |
| [Building instructions](https://youtu.be/oAUhDKYgLso) | Mechanical assembly walkthrough |
| [URDF & MJCF files](/MSG_gripper_description/) | Ready-to-use robot description files for ROS2, Gazebo, and MuJoCo |
| [ROS2 package — MSG gripper](https://github.com/BiomechatronicsLab/source_robotics_msg_gripper_ros2) | ROS2 driver and example nodes for the MSG gripper |
| [ROS2 package — SSG48 gripper](https://github.com/Lass6230/ssg48_adaptive_electric_gripper_ros2) | ROS2 driver and example nodes for the SSG48 gripper (should also work with MSG) |


## 💻 Quick start code example

```python
import Spectral_BLDC as Spectral
import time

Communication1 = Spectral.CanCommunication(bustype='slcan', channel='COM20', bitrate=1000000)
Motor1 = Spectral.SpectralCAN(node_id=0, communication=Communication1)

Motor1.Send_Clear_Error()
Motor1.Send_gripper_calibrate()
time.sleep(4)

temp_var = 0
while True:
   if temp_var == 0:
      Motor1.Send_gripper_data_pack(50,100,700,1,1,0,0) 
      temp_var = 1
   elif temp_var == 1:
      Motor1.Send_gripper_data_pack(240,100,700,1,1,0,0) 
      temp_var = 0

   message, UnpackedMessageID = Communication1.receive_can_messages(timeout=0.2) 

   if message is not None:
      print(f"Message is: {message}")
      print(f"Node ID is : {UnpackedMessageID.node_id}")
      print(f"Message ID is: {UnpackedMessageID.command_id}")
      print(f"Error bit is: {UnpackedMessageID.error_bit}")
      print(f"Timestamp is: {message.timestamp}")

   time.sleep(3)
```


