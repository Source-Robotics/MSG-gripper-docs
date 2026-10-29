# Maintenance

The gripper needs little: every wearing part is printed, so a worn part is replaced by printing a new one, and
the mechanism is a rail, two racks and a pinion that want a little grease now and then. Power the gripper off
before any work on it.

## Before each session

- The jaws sit tight on their carriers, nothing is cracked, the pads or the sponge tape are whole.
- The cable's M8 nut is tight, the cable has slack for the wrist's full motion and runs clear of the jaws.
- Nothing lies in the jaws' travel, and the gripper calibration finds both end stops.

## When the motion gets rough, and every few months of regular use

- **Grease.** A little lithium grease on the rail and on the rack and pinion. Remove the four screws that hold
  the linear rail to reach the mechanism, wipe off the old grease and the dust, grease, refit, and move the jaws
  over the whole stroke by hand before you power up. A grinding noise, a stiff motion or a calibration that
  stops short of an end are the signs that it is due.
- **Clean** with a dry cloth. The gripper is not waterproof or dustproof: keep it out of wet and dusty places,
  and blow chips out of the rail rather than wash them out.
- **Screws**: the jaw screws, the rail screws and the clamp screws of the shaft coupler; threadlocker where the
  assembly instructions use it.
- **The camera lens**, with a lens cloth.

## Replacing worn parts

The jaws, the pads and every other printed part are in the product repository,
[Print files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/Print%20files); the
rail, the carriages, the pinion and the screws are in the
[BOM](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/blob/main/BOM.md). A replacement jaw
is the same part as a new one, and the gripper calibration at the next power-up takes care of the end stops.

A stepper or a driver is not serviced but replaced: the stepper by one of the three in the BOM, after which the
motor calibration of [Driver configuration](build/first-run.md) is run again; the driver by a new
[STEPFOC driver](https://source-robotics.com/products/stepfoc-stepper-controller), configured the same way.
