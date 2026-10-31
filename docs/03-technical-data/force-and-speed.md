# Force and speed

A move command carries a current limit in mA and a speed from 0 to 255. This page estimates the resulting
force and speed. Force and payload values are ideal model estimates, not measured ratings.

## Grip force

The driver limits the motor's current to the value you command, so the torque the motor produces is limited to
$T = K_t \, I_q$, with $K_t$ the motor's torque constant in Nm/A (`#Kt` prints what the driver uses) and $I_q$
the current limit in amperes (the command is in mA). The pinion shares that torque between two racks.
Here $F$ is the **combined normal force of both jaws**,
not the force at one jaw:

$$
F = \frac{K_t \, I_q}{r}, \qquad r = 8.3\ \text{mm}
$$

$r$ is the pitch radius of the pinion (32 DP, 21 teeth). The force is proportional to the current, with a slope
set by the stepper:

| Stepper | Motor | Assumed $K_t$ | Ideal combined force per ampere | Maximum current | Ideal combined force at the maximum current |
|---|---|---|---|---|---|
| 21.5 mm | 17HS08-1004S | 0.17 Nm/A | 20 N/A | 1.5 A | about 31 N |
| 40 mm | 17HS16-2004S1 | 0.21 Nm/A | 25 N/A | 2.0 A | about 50 N |
| 60 mm | 17HS24-2104S | 0.30 Nm/A | 36 N/A | 2.1 A | about 76 N |

<figure markdown="span">
  ![Grip force against the current limit, per stepper](../assets/grip_force_light.webp#only-light){ width="820" }
  ![Grip force against the current limit, per stepper](../assets/grip_force_dark.webp#only-dark){ width="820" }
  <figcaption>Figure 5: The grip force against the current limit for the three steppers, each up to its maximum current, from the formula above.</figcaption>
</figure>

The curves use the listed torque constants; they are not force-gauge measurements. STEPFOC estimates `#Kt`
from a no-load speed/voltage test, rather than measuring shaft torque. The constant must match the driver's
$q$-axis current convention; a motor datasheet's current rating or supply current cannot be substituted directly.
A self-built gripper with another stepper needs its own force calibration. Below about
150 mA the motor does not move reliably, so the usable range starts at a few newtons. Motor GUI commands up to
1500 mA; the full force of the 40 mm and 60 mm steppers needs a command from Python or over CAN.

The current limit caps motor torque; it does not guarantee that the commanded current or the estimated
contact force is reached. Mechanism friction, finger flex and the contact position affect the actual force.

!!! danger "Stay within the stepper's maximum"
    The firmware does not clamp the gripper's current. A current above the stepper's maximum overheats the
    motor; the thermistor stops the gripper at 75 °C, but a motor driven far over its rating heats faster than
    the thermistor follows. The maximums are in the table above.

For a symmetric grip, each jaw applies $F/2$. The torque balance is
$T = F_\mathrm{left} r + F_\mathrm{right} r = F r$; counting $F$ once for each jaw would count the motor's torque twice.
These are theoretical forces before losses in the mechanism. A compression gauge between the jaws reads the
force at **one contact**; double that reading before comparing it with the combined force here. Record the
current, fingers and contact position when measuring; the same setup is needed for a useful comparison.

## Try it

<div class="gripper-calc" data-newtons-per-amp="25.3" data-radius-mm="8.3" data-ticks-min="500" data-ticks-max="60000" data-ticks-per-rev="16384" data-stroke-mm="105" markdown="0">
  <div class="gripper-calc__row gripper-calc__row--inline">
    <label for="gc-stepper">Stepper</label>
    <select id="gc-stepper" name="stepper">
      <option value="20.5" data-max-ma="1500">21.5 mm, 17HS08-1004S</option>
      <option value="25.3" data-max-ma="2000" selected>40 mm, 17HS16-2004S1</option>
      <option value="36.1" data-max-ma="2100">60 mm, 17HS24-2104S</option>
    </select>
    <label for="gc-rail">Rail</label>
    <select id="gc-rail" name="rail">
      <option value="55">100 mm, 55 mm stroke</option>
      <option value="105" selected>150 mm, 105 mm stroke</option>
      <option value="155">200 mm, 155 mm stroke</option>
    </select>
  </div>
  <div class="gripper-calc__row">
    <label for="gc-current">Current limit of the move: <output data-out="current">400 mA</output></label>
    <input id="gc-current" type="range" name="current" min="150" max="2000" step="10" value="400">
  </div>
  <div class="gripper-calc__row gripper-calc__row--inline">
    <label for="gc-mu">Friction coefficient µ</label>
    <input id="gc-mu" type="number" name="mu" min="0.1" max="1.5" step="0.05" value="0.3">
    <label for="gc-safety">Safety factor</label>
    <input id="gc-safety" type="number" name="safety" min="1" max="5" step="0.5" value="2">
  </div>
  <p class="gripper-calc__result">Ideal combined grip force <strong data-out="force">10 N</strong> · estimated static payload <strong data-out="payload">0.15 kg</strong> with the chosen friction and safety factor</p>
  <div class="gripper-calc__row">
    <label for="gc-speed">Speed byte: <output data-out="speedbyte">30</output></label>
    <input id="gc-speed" type="range" name="speed" min="0" max="255" step="1" value="30">
  </div>
  <p class="gripper-calc__result">Each jaw <strong data-out="jaw">24 mm/s</strong> · the jaws close at <strong data-out="closing">48 mm/s</strong> · the full stroke takes <strong data-out="stroke">2.2 s</strong></p>
</div>

The formulas of this page, with your numbers: the force from the current and the stepper's torque constant, the
weight held by friction with the safety factor of the next section, and the speed from the speed byte over the
rail's stroke.

## Payload

The grip force is not the weight the gripper can lift. An object held by friction between the two jaws is held
by $\mu(F_\mathrm{left} + F_\mathrm{right}) = \mu F$, with $\mu$ the friction coefficient between the jaw faces
and the object. Dividing the available friction force by a chosen safety factor $S$ gives the static estimate:

$$
W = \frac{\mu\,F}{S}, \qquad m = \frac{W}{g}
$$

Using an assumed $\mu$ = 0.3 and $S$ = 2, the model gives about 11 N of supported weight (1.2 kg) at 76 N
of combined grip force, or 4.7 N (0.47 kg) at 31 N. These are static estimates. Upward acceleration of 1 g
doubles the load; acceleration and emergency-stop loads need a separate check. Friction can be lower than
0.3, so measure it with your jaws on your object. A form-fit grip needs its own load assessment.

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
