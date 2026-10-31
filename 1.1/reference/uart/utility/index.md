# Status and utility

| Command | Kind | Argument | What it does | Response |
|---|---|---|---|---|
| `#Magnet` | Get |  | Reads the encoder's magnet status. | `Magnet Good` or `Magnet Bad` |
| `#Reset` | Action |  | Resets the driver. From firmware 105 the reset lands in the bootloader, which waits 2 s for a flashing host and then starts the firmware again. | nothing |
| `#Temp` | Get |  | Prints the thermistor temperature. | °C, or `Temp Off` while the thermistor is disabled |
| `#Mode` | Get |  | Prints the control mode. | `Idle mode`, `Position control`, `Speed control`, `Current control`, `PD control`, `Open loop`, `Gripper mode` |
| `#Vbus` | Get |  | Prints the supply voltage. | mV |
| `#Error` | Get |  | Prints which errors are active. | `No errors!` or `In error state!` followed by one line per active error |
| `#Clear` | Action |  | Clears the errors and goes to idle. An error whose cause is still present comes straight back; a calibration error is cleared only by calibrating (or `#Calibrated 1`). Enters **idle** mode. | `Clear errors` |
| `#Help` | Action |  | Prints a short command reference. Added in firmware 108. | the reference |
| `#Info` | Get |  | Prints the driver's identity and state: hardware and firmware version, serial number, motor parameters, calibration, errors. | the report |
| `#Calibrated` | Set/Get | int: 0 or 1 | The calibrated flag. `#Calibrated 1` clears a calibration error without calibrating; the motor may still be uncalibrated. | the flag |
| `#LED` | Set/Get | int: 0 or 1 | Turns the status LED on or off. | the LED state |
