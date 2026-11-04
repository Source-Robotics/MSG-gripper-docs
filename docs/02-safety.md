# Safety

The MSG gripper is a force-controlled gripper for collaborative and research robots, not a certified safety
component. Whoever puts it on a machine is responsible for the risk assessment of the gripper, the robot and
everything around them. Read this chapter before you power the gripper; the rules here are the ones that injure a
hand or destroy the gripper when they are ignored.

## Mechanical

!!! danger "The jaws"
    The jaws are a pinch point. With the current limit at the stepper's rating they close with tens of newtons,
    enough to crush a finger, and at full speed they travel the whole stroke in well under a second. Never put a
    finger between the jaws of a powered gripper. Keep hands away during calibration, which moves the jaws over
    the whole stroke without any command from you.

!!! warning "Start low"
    Test every new setup with a low current and speed: current 300 to 500 mA, speed 30. Raise them step by step
    once the application behaves, and never above the stepper's rated current
    ([Force and speed](03-technical-data/force-and-speed.md)).

!!! warning "Objects"
    A gripped object that slips, or that the jaws crush, can fly or fall. The grip force is a current limit, not a
    measurement: a hard object takes the full force, a soft one deforms until the force is reached.

### Clothing, hair and eyes

The jaws, and the open rack and pinion behind them, catch more than fingers: long hair, loose sleeves, gloves,
lanyards, rings and bracelets. Tie back long hair and take those off before you work at a powered gripper, and
keep them out of the jaws' travel while it calibrates or moves. Wear safety glasses when a gripped part can break,
slip or be thrown.

### If a finger is caught

!!! danger "The E-stop does not open the jaws"
    The gripper's E-stop bit and Send_ESTOP stop the jaws where they are; they do not open them, and a powered
    gripper holds its grip. To free a finger, switch off the gripper's supply: without current the stepper holds
    nothing beyond its own friction, and the jaws can be pushed apart by hand. A gripper without an error opens
    with a move to position 0 as well (**Open** in Motor GUI). Keep the supply's switch within reach while you
    test.

## Electrical

!!! danger "The cable"
    The gripper's M8 connector carries 24 V next to the CAN bus. A cable with the wrong pinout, including the
    cable of the other Source Robotics robot, puts 24 V on the CAN pins and destroys the driver. Use the cable
    made for your robot or check every pin of your own; see [The cable](04-installation/cable.md).

!!! warning "Supply"
    24 V DC. The driver inside tolerates 12 to 29 V, but the gripper's force and speed figures assume 24 V.

!!! warning "Do not unplug a powered gripper"
    Connect and disconnect the cable with the supply off. Hot-plugging the connector can damage the driver.

## Temperature

A thermistor on the motor housing measures the motor's temperature. At 75 °C the driver raises a temperature error and the gripper goes
idle; it clears when the motor has cooled and the error is cleared. A gripper holding an object at a high current
for long heats up: for a long hold, use the lowest current that holds the object. A self-built gripper without the
thermistor on its motor has no protection and can burn out its motor; see [Driver configuration](build/first-run.md).

## Stopping the gripper

- The E-stop bit of the move command (`Send_gripper_data_pack`) stops the gripper and raises the gripper E-stop
  error. The error stays as long as the last command carries the bit: send a command with the bit at 0, then
  clear it ([Errors and recovery](06-operation/errors.md)).
- `Send_ESTOP` to the driver, or `#Idle` over UART, stops it as well.
- The CAN watchdog ([Send_Watchdog](reference/can/system.md)) stops the gripper by itself when the host stops
  talking, which is the right protection for a program that may crash mid-grip.
- Cutting the supply releases the grip: a stepper without current holds nothing beyond its own friction, so an
  object can drop.

None of these is a certified safety function. A machine that can hurt someone needs an emergency stop that cuts
the power, independent of the gripper and the robot software.

## Care

The gripper is not waterproof or dustproof: the rail and the racks are open to dust, chips and liquids. Keep it out
of wet or dusty places. What to check, and when to grease the mechanism, is in [Maintenance](07-maintenance.md).

## Liability

The MSG gripper is sold as a component for people who build their own machines, and its designs are published
for people who build the gripper itself. The hardware designs, the firmware and this documentation are under
development and may contain errors. Whoever builds or operates
a machine with the gripper is responsible for its safe design, assembly and operation. The
[full disclaimer](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/blob/main/SAFETY_WARNING_AND_DISCLAIMER.md)
is in the product repository.
