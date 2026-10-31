# Errors and recovery

When the driver inside the gripper detects a fault it stops the motor, goes to idle and sets the error bit in
every CAN frame it sends. The grip is released: an idle stepper holds nothing beyond the mechanism's friction.

## Seeing the error

- **The error bit** of every answer's identifier: 1 while any error is active.
- **Respond_Gripper_data_pack** carries the three gripper error bits: temperature, timeout, E-stop.
- **Send_Respond_State_of_Errors** returns every flag of the driver, which is where the other causes show.
- Motor GUI shows the errors in its gripper panel; `#Error` over UART prints them.

## The errors

| Error | Reported in | Cause | What to do |
|---|---|---|---|
| Temperature | the gripper's temperature bit | the thermistor on the motor housing reads more than 75 °C (`#Tlim`) | let the motor cool; hold with less current |
| Timeout | the gripper's timeout bit | the driver's CAN watchdog ran out: no valid frame within the time set by Send_Watchdog | the host stopped sending; fix the host, then clear |
| E-stop | the gripper's E-stop bit | a move command with the E-stop bit set, or `#Gripstop 1` | clear, then send a command with the bit at 0: a command with the bit still set raises it again |
| Not calibrated (motor) | State_of_Errors, `#Error` | the driver's own motor calibration is missing: a self-built gripper before [Driver configuration](https://docs.source-robotics.com/MSG-gripper-docs/1.1/build/first-run/), or after `#Default` | calibrate the motor |
| Vbus | State_of_Errors | the supply is below 9 V or above 29.5 V | the supply, the cable |
| Encoder | State_of_Errors | the driver's encoder does not see its magnet | the magnet on the stepper shaft (a self-built gripper) |
| Driver | State_of_Errors | the driver stage's own protection tripped: overcurrent, overtemperature | lower the current; check the motor leads |
| Velocity | State_of_Errors | the motor exceeded the driver's speed limit | unlikely in a gripper; clear |
| Driver E-stop | State_of_Errors | Send_ESTOP was received | clear |

A gripper that is not **gripper-calibrated** is not in error: it just refuses moves until Send_gripper_calibrate
has found the end stops.

## Clearing

Send_Clear_Error, **Clear** in the GUI or `#Clear` clears every flag, the gripper's E-stop included, and goes to
idle. An error whose cause is still present comes straight back: a hot motor, a supply that is still low. After
an E-stop, the next move command must carry the E-stop bit at 0, or the error is raised again at once.

After clearing, the gripper is idle and still calibrated and activated; the next move command moves it.

## When the gripper does not answer

- No answer at all: the supply, the cable (and its pinout), the bus termination (about 60 Ω across CANH and CANL
  with everything unpowered), 1 Mbit/s on the adapter, the node ID.
- Answers but does not move: not calibrated, not activated, an error active, or the action bit at 0.
- Moves to one end during calibration and stops there: the other end stop is blocked, or the mechanism is too
  stiff for the calibration's 500 mA; after 24 seconds the routine gives up.

[Troubleshooting](https://docs.source-robotics.com/MSG-gripper-docs/1.1/09-troubleshooting/) goes through the symptoms one by one.
