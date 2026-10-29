# Basic control in Python

The shortest program that drives the gripper: it connects through the CANvas adapter, clears the errors,
calibrates, then closes and opens every three seconds and prints what the gripper answers. It is the example from
the product repository's README; `pip install Spectral-BLDC` is the only requirement. Change `COM20` to your
adapter's port (`/dev/ttyACM0` on Linux) and `node_id` to the gripper's CAN ID if you changed it from 0.

!!! danger
    700 mA closes the jaws with real force, about 14 N with the 21.5 mm stepper and 25 N with the 60 mm. Keep fingers out of the jaws, and start with a lower current
    if the gripper is new to you.

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

The arguments of `Send_gripper_data_pack`, in order: the position (0 open, 255 closed), the speed (0 to 255), the
current limit in mA (the force), then the activate bit, the action bit, the E-stop bit and the release direction.
[With Python](../06-operation/python.md) explains the library's calls, [How the gripper works](../06-operation/how-it-works.md)
the state the gripper answers with, and [Force and speed](../03-technical-data/force-and-speed.md) what the
current means in newtons.
