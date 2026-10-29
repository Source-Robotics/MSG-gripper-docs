# UART commands

The commands a gripper needs over the driver's serial port, for the firmware release this site describes. The
kind, the argument type, the mode a command enters and what it prints are read from the firmware; the
descriptions are written by hand. [Over UART](../../06-operation/uart.md) says where the port is and how it is
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

<!-- uart-overview -->

The driver's other commands (motion, gains, the calibration settings) are in the
[STEPFOC UART reference](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/uart/).

## By group

- [Gripper](gripper.md): gripper mode, the gripper calibration, the setpoints, the state
- [Driver setup](setup.md): the defaults, the motor parameters and calibration, the gains, the thermistor, the node ID, saving
- [Status and utility](utility.md): identity, errors, temperature, help
