# Specifications

## Electrical

| | Value |
|---|---|
| Supply voltage | 24 V DC; the driver tolerates 12 to 29 V, the force and speed figures assume 24 V |
| Idle power | 0.5 W |
| Motor current | up to 1.5 A (21.5 mm stepper), 2.0 A (40 mm), 2.1 A (60 mm); set per move as the grip force |
| Interface | CAN 2.0, 1 Mbit/s, 11-bit identifiers; node ID 0 as shipped |
| Connector | M8, 4 pins: 24 V, GND, CANH, CANL |
| CAN termination | 120 Ω, switchable, reachable through the stepper cover |
| Service port | the driver's UART, 3.3 V, 256000 baud, inside the housing |
| Driver | STEPFOC stepper controller, field-oriented control, 14-bit encoder on the motor shaft |
| Temperature protection | thermistor on the motor housing, 75 °C limit (changeable with `#Tlim`) |

## Mechanical

| | Value |
|---|---|
| Stroke | 55 mm (100 mm rail), 105 mm (150 mm rail), 155 mm (200 mm rail) |
| Mass | about 320 g; a longer rail or stepper adds to it |
| Position resolution | 1/255 of the stroke: 0.2 to 0.6 mm per step of the position byte |
| Drive | NEMA 17 stepper, pinion (32 DP, 21 teeth, 8.3 mm pitch radius) on two racks, MGN7 linear rail |
| Grip force | ideal combined force up to about 31 N (21.5 mm stepper), 50 N (40 mm) or 76 N (60 mm) at the stepper's maximum current; see the model assumptions in [Force and speed](force-and-speed.md) |
| Jaw speed | up to about 190 mm/s per jaw at speed 255; see [Force and speed](force-and-speed.md) |
| Grasps | external (closing on the object) and internal (opening inside a hollow object) |
| Mounting | coupler plate for an 8 mm shaft (shaft coupler with M4 clamp screws); a ring cover for the PAROL6 wrist |
| Body material | PETG, printed with 25 % infill |
| Jaws | printed: solid, hollow, or a PETG body with a TPU pad; sponge tape on the faces |
| Camera | mount for an OV9732 USB camera module (100°), looking between the jaws |

## Environmental

| | Value |
|---|---|
| Operating temperature | −5 to 65 °C |
| Protection | none: not waterproof or dustproof |

## Variants

| Rail | Stroke | | Stepper | Motor | Maximum current | Assumed torque constant | Ideal combined force at the maximum current |
|---|---|---|---|---|---|---|---|
| 100 mm | 55 mm | | 21.5 mm | 17HS08-1004S | 1.5 A | 0.17 Nm/A | about 31 N |
| 150 mm | 105 mm | | 40 mm | 17HS16-2004S1 | 2.0 A | 0.21 Nm/A | about 50 N |
| 200 mm | 155 mm | | 60 mm | 17HS24-2104S | 2.1 A | 0.30 Nm/A | about 76 N |

Any rail goes with any stepper, and the body comes in black or grey; see [Variants](../01-overview/variants.md).
