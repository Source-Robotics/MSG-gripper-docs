# Over UART

The driver inside the gripper has a serial port. It is not the gripper's everyday interface, which is CAN, but it
is the way to configure the driver of a self-built gripper and the quickest way to look at what the driver
reports when something is wrong.

## Reaching the port

The UART connector of the driver (JST SH, 4 pins, 3.3 V) is inside the housing, under the coupler plate. Unscrew
the plate, plug in the [USB-to-serial adapter](https://source-robotics.com/products/usb-to-serial-adapter) with
the UART cable, and open a terminal at 256000 baud with CR+LF line endings; the gripper's 24 V must be on for
anything but reading settings. [The serial terminal](https://docs.source-robotics.com/STEPFOC-docs/latest/05-setup/terminal/)
on the STEPFOC site walks through the terminal setup.

!!! danger
    The port is 3.3 V. A 5 V adapter destroys the driver.

## The gripper commands

| Command | What it does |
|---|---|
| `#Gripper 1` | gripper mode on (set and saved on every gripper); `#Gripper` prints it |
| `#Gripcal` | the gripper calibration |
| `#Gripvel 30` | the speed of the next moves, 0 to 255 |
| `#Gripcur 300` | the current limit of the next moves, mA |
| `#Grippos 200` | move to the position, 0 open to 255 closed; activates the gripper and starts the move |
| `#Gripact 1` | the activate flag without moving |
| `#Gripstop 1` | the E-stop bit |
| `#Gripinfo` | the gripper's state: calibrated, activated, the setpoints, the object detection, the end stops |

Only `#Grippos` starts a move. A session:

```
#Clear
#Gripcal
#Gripinfo
#Gripvel 30
#Gripcur 300
#Grippos 200
#Grippos 20
```

The [UART reference](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/) has these and the driver commands a gripper needs; the driver's
whole command set is on the [STEPFOC site](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/uart/).
