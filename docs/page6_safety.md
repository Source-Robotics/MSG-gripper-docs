# Safety and Maintenance

The MSG gripper is not meant for use with industrial robots. You must evaluate the gripper, robot, and surrounding equipment with a risk assessment, and this is the responsibility of the system integrator.

!!! warning "Warning"
    The operator must read and understand all of the instructions noted in this manual before using and handling the gripper.

## Warning
!!! danger "Danger"
    The gripper should not be used in disregard of these safety tips and warnings, as it may lead to injury or damage.

## Temperature warning

The gripper has a built-in thermistor on the motor surface to prevent excessive temperature rise. The default limit is 75°C. When this limit is reached, a temperature error is triggered and the gripper goes to idle mode. You can change this limit through UART commands.

## Gripper force

This gripper can exert large force and also reach high speeds.
These two factors can be dangerous for people and nearby objects. It is recommended to keep current and speed at low values during testing, for example:

* Current: 500
* Speed: 30

After you confirm your application works safely, increase values gradually.

!!! danger "Danger"
    **NEVER PLACE YOUR FINGER INSIDE THE GRIPPER.**

## Pinching points

!!! danger "Pinching points"
    The gripper jaws act as a pinching point. If the current limit is set high, they can injure you or others.

## Estop

The gripper goes to idle mode if it receives `estop_status = 1` from `Send_gripper_data_pack`.

## Maintenance

The gripper is not waterproof or dustproof. The jaws area has large gaps that allow dust, water, and particles to enter. Never use the gripper in dusty or moist environments.

## Gear lubrication

You can apply lithium grease to lubricate the gripper gears. Remove the 4 screws that hold the jaw linear track, then apply grease to the jaw mechanism.

## Errors

The gripper returns 4 error-related bits in **Respond_Gripper_data_pack**:

* **General error bit** - This bit will be 1 if any other error is active
* **Temperature error bit** - If temperature of motor coils goes above some value this will go to 1
* **Timeout error bit** - Not implemented
* **Estop error bit** - Will go to 1 if we receive Estop status 1 from Send_gripper_data_pack

!!! note "Errors"
    Errors remain active until you call `Send_Clear_Error`.
