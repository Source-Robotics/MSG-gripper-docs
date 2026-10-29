# The gripper GUI

The [SSG-gripper-GUI](https://github.com/Source-Robotics/SSG-gripper-GUI) is a small program for a PC that
connects to one gripper over the CANvas adapter: it calibrates and activates the gripper, moves it with three
sliders, shows its status and plots its position and current. It was written for the SSG-48 and works unchanged
with the MSG, which speaks the same protocol. Everything it does is one CAN message, so what you learn here
carries over to [Python](../06-operation/python.md) and the other interfaces.

## Installing

- **Windows**: the built program is in the repository's [releases](https://github.com/Source-Robotics/SSG-gripper-GUI/releases).
- **Any platform**: clone the repository and run it with Python 3.10 after `pip install -r requirements.txt`.

Motor GUI, the driver's tool in the browser ([motorgui.com](https://motorgui.com/)), also has a gripper panel
with the same controls, and it reaches the gripper over CAN as well; use whichever you prefer.

## Connecting

1. Plug the [CANvas adapter](https://source-robotics.com/products/canvas-usb-to-can-adapter) into the PC and
   into the gripper's CAN bus; power the gripper.
2. Enter the adapter's port in *COM port* (`COMx` on Windows, `/dev/ttyACMx` on Linux) and the gripper's CAN ID
   (0 unless you changed it), then **Connect**.
3. The status (section 3) fills in: *Not calibrated*, *Not activated*, and the active errors.

Only one gripper can be connected at a time; to work with another, change the CAN ID and connect again.

## What is on the screen

<figure markdown="span">
  ![The gripper GUI](../assets/GUI2.png){ width="900" }
  <figcaption>Figure 14: The gripper GUI.</figcaption>
</figure>

| Section | What it is |
|---|---|
| 1 | **Calibrate**, **Activate**, **Estop**, **Clear** (errors); the CAN ID and the port; **Connect**; the object-detection state |
| 2 | the move: *Position* (0 open, 255 closed), *Speed* (0 to 255) and *Current* (mA, the force), each with a **Set** button |
| 3 | the gripper's status: calibrated, activated, the errors |
| 4 | the feedback: the position and the current the gripper reports |
| 5 | live plots of position and current |
| 6 | the GUI's frame rate, and light or dark mode |

Setting *Speed* or *Current* only stores the value; a change of *Position* starts a move with the stored speed and
current. **Estop** sends the move command with the E-stop bit set: the gripper stops and shows the E-stop error
until **Clear**.

## What next

[Calibrate, activate, move](first-moves.md) is the first session with a connected gripper.
