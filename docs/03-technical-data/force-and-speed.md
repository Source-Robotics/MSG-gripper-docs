# Force and speed

A move command carries a current limit in mA and a speed from 0 to 255. This page says what they mean in
newtons and millimetres per second.

## Grip force

The driver limits the motor's current to the value you command, so the torque the motor can produce is limited
to

$$
T = K_t \, I_q
$$

with $K_t$ the motor's torque constant in Nm/A, which the driver measures when the stepper is calibrated (`#Kt`
prints it), and $I_q$ the current limit in amperes (the command is in mA). The pinion turns that torque into a
force on the two racks. With an object between the jaws both racks are loaded, so the torque is shared between
them and each jaw presses with

$$
F = \frac{T}{2\,r}, \qquad r = 8.3\ \text{mm}
$$

$r$ is the pitch radius of the pinion (32 DP, 21 teeth). A current of 1 A on a motor with $K_t$ = 0.16 Nm/A gives
0.16 Nm and about 10 N of grip force.

!!! note "Estimates per stepper"
    The torque constant of a stepper under field-oriented control is in the order of its holding torque divided
    by its rated current, times about 0.7 (the holding torque is rated with both phases driven). With that, the
    grip force at the rated current comes to roughly:

    | Stepper | Rated current | Holding torque | Grip force at the rated current, about |
    |---|---|---|---|
    | 21.5 mm, 17HS08-1004S | 1.0 A | 16 Ncm | 7 N |
    | 40 mm, 17HS16-2004S1 | 2.0 A | 45 Ncm | 19 N |
    | 60 mm, 17HS24-2104S | 2.1 A | 65 Ncm | 27 N |

    These are estimates from the motors' datasheets, not measurements. Measured force-against-current curves for
    the three steppers will follow; until then, use the `#Kt` your driver reports and the formula above.

The force is a limit, not a controlled value: a hard object takes the full force the moment the jaws touch it; a
soft object is squeezed until the force is reached. Below about 150 mA the motor does not move reliably.

!!! danger "Stay within the stepper's rating"
    The firmware does not clamp the gripper's current. A current above the stepper's rated current overheats the
    motor; the thermistor stops the gripper at 75 °C, but a motor driven far over its rating heats faster than
    the thermistor follows. The ratings are in the table above.

## Speed

The speed byte of a move is mapped by the firmware to the motor's speed in encoder ticks per second, linearly
from 500 at speed 0 to 60000 at speed 255:

$$
\text{ticks/s} = 500 + \frac{60000 - 500}{255}\, C
$$

The motor's encoder has 16384 ticks per revolution, so the angular speed is $\omega = \text{ticks/s} / 16384 \times 2\pi$
and each jaw moves at

$$
v = \omega \, r
$$

| Speed byte | Motor speed | Each jaw moves at | The jaws close at |
|---|---|---|---|
| 0 | 500 ticks/s, 0.03 rev/s | 1.6 mm/s | 3 mm/s |
| 30 | 7500 ticks/s, 0.46 rev/s | 24 mm/s | 48 mm/s |
| 128 | 30400 ticks/s, 1.9 rev/s | 97 mm/s | 190 mm/s |
| 255 | 60000 ticks/s, 3.7 rev/s | 190 mm/s | 380 mm/s |

Both jaws move, so the gap closes at twice the speed of one jaw. At speed 255 a 105 mm stroke takes about half a
second. The gripper calibration runs at speed 40 and 500 mA.

## Position

The position byte is linear over the stroke: 0 is the fully open end stop found by the gripper calibration, 255
the fully closed one. One step of the byte is the stroke divided by 255: 0.22 mm on the 100 mm rail, 0.41 mm on
the 150 mm rail, 0.61 mm on the 200 mm rail. The driver considers the position reached within 5 encoder ticks,
about 0.03 mm.
