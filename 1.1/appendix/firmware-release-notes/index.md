# Firmware release notes

What changed in each release of the STEPFOC firmware the gripper runs, from the release notes in the driver's
repository, up to the release this site describes. Entries about the driver's motion modes do not concern a
gripper; the gripper mode, the CAN protocol and the bootloader do.

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
