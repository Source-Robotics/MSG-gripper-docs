# Firmware release notes

What changed in each release of the STEPFOC firmware the gripper runs, from the release notes in the driver's
repository, up to the release this site describes. Entries about the driver's motion modes do not concern a
gripper; the gripper mode, the CAN protocol and the bootloader do.

## V110 (2026-11-13)

STEPFOC firmware **V110** — application image for flashing via the Spectral bootloader. Mostly gripper work: an MSG gripper (a STEPFOC in gripper mode) now ends its moves cleanly and reaches positions 0 and 255 without pressing on its stops. Everything below is described in the manual: [STEPFOC docs](https://docs.source-robotics.com/STEPFOC-docs/); what a driver keeps and what to run after the update: [Upgrading from older firmware](https://docs.source-robotics.com/STEPFOC-docs/latest/07-firmware/upgrading/).

#### Grippers
- **A move ends cleanly.** On 109 the current took over a second to settle after every move: the speed loop's integral was carried into the hold and unwound slowly through friction. Now the integral is dropped on arrival, the last stretch of a move slows down, and the hold has a small dead zone (a quarter of a position count). A few mA are left after a move.
- **A soft start.** A move picks up speed over 0.1 s instead of starting at full speed. On an MSG at full speed the start current fell from 600 mA to about 210 mA, and the speed ripple from 35 % to 2 %.
- **Positions 0 and 255 clear the stops.** On 109 the calibration read the ends while pushing at 500 mA, so 0 and 255 lay inside the stops: a full open or close pressed on the stop, drew the grip current for good and often reported an object. Each end is now read under a light 100 mA push; 0 sits 32 ticks inside the open stop and 255 16 ticks from the closed one.
- **Object detection** reports an object after the jaws have stood still against it for 50 ms.
- **The gripper pushes with its own current limit.** On 109 every gripper command overwrote the driver's current limit (parameter 16) with its grip current, and a Save config then stored it.
- The gripper calibration can be started again while it runs, ends on a timeout or a stroke under 1000 ticks, and puts the current limit back. The position is rounded to the nearest count (it was cut off).

#### CAN bus
- **Parameters 90-93:** 90 `#Rstint`, 91 the thermistor (`#Term`), 92 gripper mode (`#Gripper`, written only while idle), each 0 or 1 and saved by Save config, so a preset over CAN can set everything (issue #7); 93, read only, the gripper's stroke between positions 0 and 255 in ticks (0 until calibrated).

#### UART
- **`#Estop`:** the E-stop, as CAN has it. The motor is released, a running calibration ends, and the E-stop latches until `#Clear`.
- **`#Close` during a motor calibration** stops the calibration (`Close: the calibration is stopped`). On 109 it switched the mode under the running calibration.

#### Settings and safety
- **Brake or coast when idle (parameter 18) is saved** by Save config. On 109 it was back to its default at every power-up. A driver that never saved it brakes, as before.
- **Watchdog:** a trip while the driver is idle no longer starts the hold or the descend (on 109 it did, for the whole fallback time). A trip while a loop is closed holds as before.

#### Compatibility
- The settings and the motor calibration of 109 are kept. The gripper calibration is kept in RAM, as always: calibrate the gripper after the update.
- Python library **1.22** (`pip install --upgrade Spectral-BLDC`) names parameters 90-93; 1.21 reads them by number. Motor GUI **0.7.0** uses what 110 adds: STOP over UART sends `#Estop`, brake or coast counts as saved, a preset over CAN writes 90-92.
- Bench-tested for this release on an MSG gripper (21.5 mm motor, 150 mm rail): the moves and the hold, the ends, the soft start, gripping objects, parameters 90-93, brake or coast over a save and a restart, the driver's current limit through gripper moves, the watchdog while idle and in a closed loop, an aborted gripper calibration; `#Estop` and `#Close` over UART. Not tested on the bench: an upgrade from V103 with the ST-Link, and a downgrade.

#### Assets
- `stepfoc-firmware-V110.bin` — application firmware image (flash at `0x08003000`, target STM32F103CB).
- `firmware.json` — manifest with version, size, and SHA-256 for download verification by the web flasher.

#### Integrity
- SHA-256: `5109a3b3819091ce45726ae422a9f953ea609142d48eb24ff096e5c938a798b8`
- Size: 112768 bytes

Built from commit 9c9165c on `bootloader-version` (`#Info` shows it as `Build: 9C9165C`). Includes bootloader entry support (CAN/UART reset-into-bootloader).

## V109 (2026-11-10)

STEPFOC firmware **V109** — application image for flashing via the Spectral bootloader. From 109 the STEPFOC and the Spectral Micro share their version numbers. Everything below is described in the manual: [STEPFOC docs](https://docs.source-robotics.com/STEPFOC-docs/); what a driver keeps and what to run after the update: [Upgrading from older firmware](https://docs.source-robotics.com/STEPFOC-docs/latest/07-firmware/upgrading/).

#### New features
- **Parameters:** any setting or read-out by number over CAN (commands 36-38) or `#Par`: the gains and limits, the watchdog, the current loop, the speed estimate, the tool id and more (parameters 1-87). Identity (39) and telemetry (40) frames.
- **Capture, histogram and buffers** (41-43): record three signals from the control loop, read the encoder and anti-cogging tables.
- **Watchdog actions:** on a lost host the driver can idle, brake, coast, hold the position, or descend at a capped speed, with a fallback time.
- **Current loop from R, L and one bandwidth** (parameter 49, default 160 Hz); the direct PLL speed estimate at 60 Hz by default; commutation delay compensation, 166 µs by default; a position input filter and a velocity-integral deadband.
- **Encoder table and anti-cogging measured on the driver:** `#Cal` runs the calibration, then the encoder table and the anti-cogging identification, and saves; `#Calonly` is the calibration alone.
- **Sound through the motor:** tones, a queue of notes and samples (CAN 44 and 45, `#Tone`).
- **Identification:** `#Info` and parameters 84-87 report the build (git commit), the board ID and a calibration ID.
- **Settings in blocks with their own checksums;** a reset keeps the CAN ID; a product lock refuses a Spectral image on a STEPFOC board.

#### Calibration
- The angle alignment locks the rotor with the calibration current through the coil's resistance (it used a fixed 0.5 V, too weak for small motors with a high coil resistance). On a 20 mm stepper the alignment offset now comes out 6× steadier from run to run; 25 of 25 calibrations passed.
- Kt and KV are measured in four spins alternating direction at a forced 6 V; a warning only when two same-direction spins differ by more than 5 %.
- `#Cal` from a moving motor switches the bridge off first; a failed calibration switches it off at once; an E-stop ends a calibration, and `#Cal` is refused while one is latched (`Cal: not started, the E-stop is latched (#Clear first)`); the alignment starts from its first stage after a calibration that was ended from outside. `#Calangle` is refused while the driver is in error.
- The current limit is put back when a calibration ends.

#### Safety
- Limits: a negative or not-a-number value is ignored by the legacy CAN frames (limits, gains, Kt, voltage limit 0-60000 mV); `#Ilim` and `#Vlimit` take the magnitude; the current of a gripper move stays within 0-2800 mA; `#PP` takes 1-200 pole pairs, only while idle. PWM duties stay between 0 and 100 %.
- The current-sense zero waits for the motor supply: started on USB before the supply, the driver used a zero about 100 mA off. It now says so in `#Info` and measures the zero by itself once the supply is there.
- No undervoltage error while the supply ramps up at power-up.

#### CAN bus
- A gripper poll right after a new move command no longer cancels it as new: object detection reports contact again (it read "at position" while pressing on an object). The same in every release before 109.
- The current and PD frames set their setpoint and mode together. Length codes above 8 are read as 8; extended (29-bit) frames are ignored.
- Watchdog: setting its time or a save starts a fresh window; a negative time means off; hold and descend no longer use the last moving loop's delay compensation.

#### Bug fixes
- After `#Cal`, a host that takes the driver within 3 s drops the encoder-table and anti-cogging runs (they used to start by themselves at the next idle). `#Encal` and `#Cogcal` start only on their own words. While such a run turns the motor, a capture is not armed and the histogram is not changed.
- A storage block whose check fails is read up to three times before its defaults are used. `#Info` says the anti-cogging is saved only while what is in RAM equals what is stored.
- The current-loop integrals are cleared whenever the bridge brakes or coasts. The sound queue and sample buffer no longer replay old content after a stop; a pitch the driver cannot play answers `Tone: not played`.

#### Compatibility
- Python library **1.21 or newer** (`pip install --upgrade Spectral-BLDC`), Motor GUI **0.5.0**.
- The calibration and the settings of 108 are kept. Not tested on the bench for this release: an upgrade from V103 with the ST-Link, and a downgrade.

#### Assets
- `stepfoc-firmware-V109.bin` — application firmware image (flash at `0x08003000`, target STM32F103CB).
- `firmware.json` — manifest with version, size, and SHA-256 for download verification by the web flasher.

#### Integrity
- SHA-256: `94bc56430195b323f48dd47237be99700623ec8d0ae391f974a809e3eae123cc`
- Size: 112088 bytes

Built from commit 118fe17 on `bootloader-version` (`#Info` shows it as `Build: 118FE17`). Includes bootloader entry support (CAN/UART reset-into-bootloader).

## V108 (2026-08-26)

STEPFOC firmware **V108** — application image for flashing via the Spectral bootloader.

#### Bug fixes
- Fixed calibration (`#Cal`) spuriously failing with `Phase order is wrong!` on otherwise-healthy motors. The "confirm commutation" pre-check (before the real angle-offset search) commands a pure torque-axis voltage using the not-yet-calibrated encoder angle — depending on a given unit's actual rotor-to-encoder mounting angle, that command could land almost entirely on the wrong axis and produce ~zero torque, failing the check even though nothing was actually broken. Bench-confirmed on a real unit.
- Fix: retry the pre-check once at a 90° angle bias before declaring failure — guaranteed to land within 45° of the true torque axis on at least one of the two tries. The downstream angle-offset search is unaffected and already independent of this pre-check.
- Added `Spin-confirm delta` / `Vbus` diagnostics to `#Cal`'s failure report, for the rare case both tries still fail.

#### Assets
- `stepfoc-firmware-V108.bin` — application firmware image (flash at `0x08003000`, target STM32F103CB).
- `firmware.json` — manifest with version, size, and SHA-256 for download verification by the web flasher.

#### Integrity
- SHA-256: `25cbc4887ca2c192eba6e708930eb6b6c677fd1e76299313c3b3ce3459e0e8a1`
- Size: 99188 bytes

Built from commit 46b4911 on `bootloader-version`. Includes bootloader entry support (CAN/UART reset-into-bootloader).

## V107 (2026-08-24)

STEPFOC firmware **V107** — application image for flashing via the Spectral bootloader.

#### Bug fixes
- Fixed PD mode (`IN_DATA_PACK_PD` over CAN): the commanded speed was written into `Feedforward_speed`, but `PD_mode()` reads `Velocity_setpoint` for its KD term — so the KD (velocity-damping) term of the impedance controller was always evaluated against a stale/zero setpoint and had no effect. The CAN handler now writes the field the control law actually reads. `IN_DATA_PACK_1` / position mode is unaffected — `Feedforward_speed` there is correct and continues to feed the position cascade.

#### CAN bus
- Added a generic settings command (`IN_SETTINGS`) so future boolean settings don't each need their own command ID. Payload is `mask` + `value` (one byte each), one bit per setting — only bits set in the mask are applied, so a sender only needs to know about the bits it cares about.
- First setting on this command: brake vs. coast (bit 0), previously only selectable over UART (`Brake` / `Coast`), now selectable over CAN as well.

#### Assets
- `stepfoc-firmware-V107.bin` — application firmware image (flash at `0x08003000`, target STM32F103CB).
- `firmware.json` — manifest with version, size, and SHA-256 for download verification by the web flasher.

#### Integrity
- SHA-256: `63699037c79318e1d78738edcb13e9f9bc00a3393dc5803f920b244a60622ae2`
- Size: 98972 bytes

Built from commit 04ec180 on `bootloader-version`. Includes bootloader entry support (CAN/UART reset-into-bootloader).

## V106 (2026-07-05)

STEPFOC firmware **V106** — application image for flashing via the Spectral bootloader.

#### CAN bus
- The controller now drains up to 8 CAN messages per pass instead of just 1, so short bursts (multiple commands sent back-to-back, or a busy multi-node bus) no longer silently drop messages once the 3-deep hardware FIFO fills.
- A CAN peripheral that fails to initialize no longer bricks the board — UART stays fully usable, only the CAN bus is skipped.

#### Safety
- Added a hardware watchdog (100ms). If the control loop ever stops running, the board resets instead of leaving the motor driven at a stale duty cycle.
- Fixed a bug where `Torque_mode` could silently overwrite your commanded Iq setpoint when clamping to the current limit — reading it back after clamping now shows what you actually asked for, and raising the current limit afterward immediately restores the original commanded torque instead of requiring the command to be resent.
- Fixed undefined behavior in a serial-protocol integer conversion (`fourBytesToInt`).
- Synced default configuration values that had drifted between two locations in the code, so a fresh `#Default` and a freshly-flashed board's built-in defaults now agree.

#### EEPROM / configuration integrity
- Added CRC validation over the saved configuration, split into two independent halves: **calibration data** (resistance, inductance, Kt/KV, angle offset, current-loop gains, etc.) and **settings** (PID tuning, limits, watchdog config, CAN ID, etc.).
- This means a corrupted save (e.g. from a power loss mid-write) is detected and safely defaulted instead of silently running with garbage values — and critically, a *future* firmware update that only adds a new setting can no longer wipe your calibration, since the two are validated independently.
- Boards upgrading from older, pre-CRC firmware keep their existing calibration automatically — no need to recalibrate after this update.
- A few unused slots were reserved in the calibration block for upcoming features (e.g. magnet alignment), so those can be added later without another migration.

#### Performance
- PWM output no longer re-resolves which timer/channel it's writing to on every single call (it was doing this 4x per control tick) — resolved once and cached, freeing up ISR headroom.
- Velocity calculation switched from a floating-point divide to an integer multiply.

#### Usability
- New `#Help` command — prints a summary of the available commands.
- Serial now responds with "Unknown command" for unrecognized input instead of silently ignoring it.
- Calibration now prints progress during the angle-offset search (previously up to ~40 seconds of silence that could look like the board had hung).
- `#Error` now also reports driver faults (undervoltage/thermal/overcurrent), not just the other error types.
- `#Info` now always reports live ISR execution time, useful for checking control-loop headroom on the bench.

#### Assets
- `stepfoc-firmware-V106.bin` — application firmware image (flash at `0x08003000`, target STM32F103CB).
- `firmware.json` — manifest with version, size, and SHA-256 for download verification by the web flasher.

#### Integrity
- SHA-256: `bc061fb273e7c836e3180fa597ecd373e7e357b0eab9130b63a7fd19b70a6073`
- Size: 98940 bytes

Built from commit 661e7d3 on `bootloader-version`. Includes bootloader entry support (CAN/UART reset-into-bootloader).

## V105 (2026-07-04)

STEPFOC firmware **V105** — application image for flashing via the Spectral bootloader.

#### What's new
- Reversed stepper phase wiring now calibrates automatically — no more "switch phases and try again." The firmware detects the wiring and compensates it in software, so **all 8 phase-wiring permutations calibrate identically and symmetrically**.
- `#Info` now reports the firmware's own build version, so the version is correct immediately after flashing (no `#Default` needed).

#### Assets
- `stepfoc-firmware-V105.bin` — application firmware image (flash at `0x08003000`, target STM32F103CB).
- `firmware.json` — manifest with version, size, and SHA-256 for download verification by the web flasher.

#### Integrity
- SHA-256: `0d80ce3cf78109f6ff54697425ed475ffca4e97e220d72fe0823ce1bd60a4908`
- Size: 95924 bytes

Built from commit bda57d6 on `bootloader-version`. Includes bootloader entry support (CAN/UART reset-into-bootloader).

## V103 (2025-12-28)

First stable release for public

## V102 (2025-12-28)

First official release for the public

## V101 (2025-09-29)

Initial fully functional release based on spectral micro firmware.
