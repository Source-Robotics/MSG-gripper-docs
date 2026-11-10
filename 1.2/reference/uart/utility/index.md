# Status and utility

| Command | Kind | Argument | What it does | Response |
|---|---|---|---|---|
| `#Magnet` | Get |  | Reads the encoder's magnet status. | `Magnet Good` or `Magnet Bad` |
| `#Reset` | Action |  | Resets the driver. From firmware 105 the reset lands in the bootloader, which waits 2 s for a flashing host and then starts the firmware again. | nothing |
| `#Temp` | Get |  | Prints the thermistor temperature. | °C, or `Temp Off` while the thermistor is disabled |
| `#Mode` | Get |  | Prints the control mode. In gripper mode (mode 11) it prints nothing; `#Gripinfo` shows the gripper's state. | `Idle mode`, `Position control`, `Speed control`, `Current control`, `PD control`, `Open loop`, `Gripper calib mode` during the gripper calibration; `Gripper mode` is what it prints for mode 6, voltage torque |
| `#Vbus` | Get |  | Prints the supply voltage. | mV |
| `#Error` | Get |  | Prints which errors are active. | `No errors!` or `In error state!` followed by one line per active error |
| `#Clear` | Action |  | Clears the errors and goes to idle, and ends a running gripper calibration. An error whose cause is still present comes straight back, the gripper's E-stop too while `#Gripstop` is 1; a calibration error is cleared only by calibrating (or `#Calibrated 1`). Enters **idle** mode. | `Clear errors` |
| `#Help` | Action |  | Prints a short command reference. Added in firmware 106. | the reference |
| `#Info` | Action |  | Prints the driver's identity and state: hardware version, batch date and firmware version, the ISR time, the CAN ID, the motor calibration, the thermistor and temperature, the supply voltage and the motor parameters (phase direction and order, pole pairs, R, L, Kt, KV). The serial number is printed by `#SERNUM`, the errors by `#Error`, gripper mode by `#Gripper`. | the report |
| `#Calibrated` | Set/Get | int: 0 or 1 | The calibrated flag. `#Calibrated 1` clears a calibration error without calibrating; the motor may still be uncalibrated. | the flag |
| `#LED` | Set/Get | int: 0 or 1 | Turns the status LED on or off. | the LED state |
