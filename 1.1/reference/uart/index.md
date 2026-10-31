# UART commands

The commands a gripper needs over the driver's serial port, for the firmware release this site describes. The
kind, the argument type, the mode a command enters and what it prints are read from the firmware; the
descriptions are written by hand. [Over UART](https://docs.source-robotics.com/MSG-gripper-docs/1.1/06-operation/uart/) says where the port is and how it is
used.

## Syntax

```
#<Name> [number]
```

- A **Set/Get** command sets the value when a number follows and prints the current value either way.
- A **Get** command only prints.
- An **Action** command does something; a number after it is ignored.
- Names are case-sensitive, at most 19 characters; the number at most 19; the line ends with LF (CR before it is
  fine). 256000 baud, 8N1, 3.3 V.
- A name the parser does not know is answered `Unknown command`.

## The commands a gripper needs

| Command | Kind | Argument | Group |
|---|---|---|---|
| [`#Cal`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Action |  | Driver setup |
| [`#Calibrated`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Set/Get | int | Status and utility |
| [`#CANID`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | int | Driver setup |
| [`#Cbw`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | float | Driver setup |
| [`#Clear`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Action |  | Status and utility |
| [`#Default`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Action |  | Driver setup |
| [`#Error`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Get |  | Status and utility |
| [`#Gripact`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Set/Get | int | Gripper |
| [`#Gripcal`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Action |  | Gripper |
| [`#Gripcur`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Set/Get | int | Gripper |
| [`#Gripinfo`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Get |  | Gripper |
| [`#Gripper`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Set/Get | int | Gripper |
| [`#Grippos`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Set/Get | int | Gripper |
| [`#Gripstop`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Set/Get | int | Gripper |
| [`#Gripvel`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/) | Set/Get | int | Gripper |
| [`#Help`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Action |  | Status and utility |
| [`#Ilim`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | int | Driver setup |
| [`#Info`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Get |  | Status and utility |
| [`#Kiiq`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | float | Driver setup |
| [`#Kpiq`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | float | Driver setup |
| [`#Kt`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | float | Driver setup |
| [`#L`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | float | Driver setup |
| [`#LED`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Set/Get | int | Status and utility |
| [`#Magnet`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Get |  | Status and utility |
| [`#Mode`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Get |  | Status and utility |
| [`#PP`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | int | Driver setup |
| [`#R`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | float | Driver setup |
| [`#Reset`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Action |  | Status and utility |
| [`#Save`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Action |  | Driver setup |
| [`#Temp`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Get |  | Status and utility |
| [`#Term`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | int | Driver setup |
| [`#Tlim`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/) | Set/Get | int | Driver setup |
| [`#Vbus`](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/) | Get |  | Status and utility |

The driver's other commands (motion, gains, the calibration settings) are in the
[STEPFOC UART reference](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/uart/).

## By group

- [Gripper](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/gripper/): gripper mode, the gripper calibration, the setpoints, the state
- [Driver setup](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/setup/): the defaults, the motor parameters and calibration, the gains, the thermistor, the node ID, saving
- [Status and utility](https://docs.source-robotics.com/MSG-gripper-docs/1.1/reference/uart/utility/): identity, errors, temperature, help
