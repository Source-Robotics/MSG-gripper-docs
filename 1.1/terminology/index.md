# Glossary

**Action bit**
:   A bit of the move command: 1 carries out the move, 0 leaves the gripper idle with the command stored.

**Activated**
:   A flag the gripper keeps, set by the activate bit of the move command or by `#Gripact`. A move is carried out
    only while the gripper is activated and calibrated.

**CAN ID** (node ID)
:   The address of the gripper on the CAN bus, 0 to 13; every gripper ships as 0. It occupies bits 10 to 7 of the
    11-bit CAN frame identifier; the command ID occupies bits 6 to 1 and the error bit is bit 0.

**CANvas**
:   Source Robotics' USB-to-CAN adapter. It appears as a serial port and speaks slcan, which `python-can`, Motor
    GUI and the ROS 2 driver use.

**Current limit** (grip force)
:   The current, in mA, the driver may put into the motor during a move. Torque is current times the motor's
    torque constant, so the current limit sets the force with which the jaws press on an object.

**Driver**
:   The STEPFOC board on the back of the gripper's stepper: field-oriented control of the motor, the gripper state
    machine and the CAN and UART interfaces. The gripper's firmware is the driver's firmware.

**E-stop bit**
:   A bit of the move command. 1 stops the gripper and raises the gripper E-stop error, which stays until it is
    cleared and a command with the bit at 0 arrives.

**Error bit**
:   Bit 0 of every CAN frame identifier the driver sends: 1 while any error is active.

**Field-oriented control** (FOC)
:   Controlling the stepper's current as a vector relative to the rotor, from the driver's encoder. It turns the
    stepper into a motor whose torque is known and limited, which is what makes a force-controlled gripper out
    of it.

**Firmware release**
:   One build of the STEPFOC firmware, numbered 103, 104, 105, … and tagged `V103`, `V104`, … in the driver's
    repository. `#Info` prints the release a gripper runs. This documentation describes one release; the version
    selector switches between them.

**Gripper calibration**
:   The routine (`Send_gripper_calibrate`, `#Gripcal`) that opens the jaws fully, then closes them fully, at low
    force, and records both end stops as positions 0 and 255. Needed after every power-up.

**Gripper mode**
:   The driver's mode in which it runs a gripper (`#Gripper 1`, saved): move commands with a jaw position, a speed
    and a current limit, and object detection.

**Motor calibration**
:   The driver's own calibration of the stepper (`#Cal`): the pole pairs, resistance and inductance entered, the
    encoder aligned, the motor constants measured. Done once, at the factory or when you build the gripper; not
    to be confused with the gripper calibration.

**Object detection**
:   The gripper's report of why the jaws stopped: 0 still moving, 1 an object stopped them while closing, 2 an
    object stopped them while opening, 3 they reached the commanded position.

**Position**
:   The jaw position as the gripper commands and reports it: 0 fully open, 255 fully closed, linear in between.

**Rack and pinion**
:   The gripper's mechanism: a pinion on the motor shaft meshes with two racks that run on the linear rail in
    opposite directions, so one motor moves both jaws symmetrically.

**Speed**
:   The speed of a move, 0 to 255, mapped by the firmware to 500 to 60000 encoder ticks per second of the motor.

**Stroke**
:   How far each jaw carrier travels from fully open to fully closed: 55, 105 or 155 mm, set by the rail length.

**Timeout error** (watchdog)
:   The driver's CAN watchdog, as the gripper reports it: when the watchdog is set (`Send_Watchdog`) and no valid
    frame arrives in time, the gripper stops and raises it.

**Watchdog**
:   A timer the driver resets with every valid CAN frame it receives. When it is set and runs out, the gripper
    reports a timeout error and stops.
