# Force and speed

A move command carries a current limit in mA and a speed from 0 to 255. This page says what they mean in
newtons and millimetres per second.

## Grip force

The driver limits the motor's current to the value you command, so the torque the motor produces is limited to
$T = K_t \, I_q$, with $K_t$ the motor's torque constant in Nm/A (`#Kt` prints what the driver uses) and $I_q$
the current limit in amperes (the command is in mA). The pinion turns the torque into the force the jaws press
with:

$$
F = \frac{K_t \, I_q}{r}, \qquad r = 8.3\ \text{mm}
$$

$r$ is the pitch radius of the pinion (32 DP, 21 teeth). The force is proportional to the current, with a slope
set by the stepper:

| Stepper | Motor | $K_t$ | Force per ampere | Maximum current | Grip force at the maximum current |
|---|---|---|---|---|---|
| 21.5 mm | 17HS08-1004S | 0.17 Nm/A | 20 N/A | 1.5 A | about 31 N |
| 40 mm | 17HS16-2004S1 | 0.21 Nm/A | 25 N/A | 2.0 A | about 50 N |
| 60 mm | 17HS24-2104S | 0.30 Nm/A | 36 N/A | 2.1 A | about 76 N |

<figure markdown="span">
  ![Grip force against the current limit, per stepper](../assets/grip_force_light.png#only-light){ width="820" }
  ![Grip force against the current limit, per stepper](../assets/grip_force_dark.png#only-dark){ width="820" }
  <figcaption>Figure 5: The grip force against the current limit for the three steppers, each up to its maximum current, from the formula above.</figcaption>
</figure>

The curves are computed from the torque constants, not measured with a force gauge: a measurement on your gripper
is the only exact calibration, and a self-built gripper with another stepper has another $K_t$. Below about
150 mA the motor does not move reliably, so the usable range starts at a few newtons. Motor GUI commands up to
1500 mA; the full force of the 40 mm and 60 mm steppers needs a command from Python or over CAN.

The force is a limit, not a controlled value: a hard object takes the full force the moment the jaws touch it; a
soft object is squeezed until the force is reached.

!!! danger "Stay within the stepper's maximum"
    The firmware does not clamp the gripper's current. A current above the stepper's maximum overheats the
    motor; the thermistor stops the gripper at 75 °C, but a motor driven far over its rating heats faster than
    the thermistor follows. The maximums are in the table above.

## Payload

The grip force is not the weight the gripper can lift. An object held by friction between the two jaws is held
by $2\,\mu F$, with $\mu$ the friction coefficient between the jaw faces and the object, and a safety factor $S$
covers what the robot adds:

$$
W = \frac{2\,\mu\,F}{S}
$$

With a conservative $\mu$ = 0.3 (a hard printed jaw on steel or smooth plastic; a TPU pad or sponge tape on a dry
object gives more) and $S$ = 2, the 60 mm stepper at 76 N holds about 23 N, 2.3 kg, and the 21.5 mm stepper at
31 N about 9 N, 0.9 kg. That is the weight held at rest: a robot accelerating at 1 g doubles the load, and an
emergency stop decelerates harder than any programmed move. The friction coefficient is the big unknown; measure
it with your jaws on your object, or close on the object's shape (a form-fit grip) and let friction be the
reserve.

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
