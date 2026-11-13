# Data for robot integration

What a robot's software needs to carry the gripper: the frame the numbers are given in, the mass, the centre of
mass and the inertia, and the tool centre point (TCP).

The numbers are taken from the gripper's robot model in
[robot_descriptions](https://github.com/Source-Robotics/robot_descriptions) (version 2.18.1, `msg_description`
in URDF and `msg` in MJCF) and moved into the frame below. The model is the 150 mm rail with the 21.5 mm stepper,
the variant of the [drawings](https://docs.source-robotics.com/MSG-gripper-docs/1.2/03-technical-data/dimensions/).

## The frame

The origin is on the coupler axis, at the centre of the coupler's back face: the face that rests against the
robot.

- **Z** runs along the coupler axis, from the robot toward the jaw tips: the approach direction.
- **Y** runs along the jaw travel, parallel to the rail, positive toward the side of the M8 connector.
- **X** completes the frame: from the rail and the jaws toward the stepper and the camera. The jaws' centre line
  is at X = −28.35 mm, the top of the camera mount at X = +78.97 mm.

The axes are those of the model's `flange` frame. That frame's origin lies 15.50 mm further along Z, inside the
body behind the coupler ring: subtract 15.50 mm from a Z below to have it in the model's `flange` frame.

## Mass and inertia

| Model, jaws | Mass measured | Mass in the model | Centre of mass x, y, z (mm) | Ixx, Iyy, Izz (10⁻⁶ kg·m²) | Ixy, Ixz, Iyz (10⁻⁶ kg·m²) |
|---|---|---|---|---|---|
| URDF, jaws open | about 380 g | 380.0 g | −0.70, 0.22, 32.34 | 508.5, 147.6, 525.5 | 0.4, 42.0, −1.9 |
| URDF, jaws closed | about 380 g | 380.0 g | −0.70, 0.22, 32.34 | 200.2, 147.6, 217.2 | 0.4, 42.0, 0.2 |
| MJCF, jaws open | about 380 g | 380.0 g | −0.42, 0.24, 31.89 | 471.7, 137.5, 488.0 | 0.6, 35.7, −5.7 |
| MJCF, jaws closed | about 380 g | 380.0 g | −0.42, 0.24, 31.89 | 199.6, 137.5, 215.9 | 0.5, 35.7, 1.6 |

The model's mass is the body, 301.4 g, and two moving assemblies of 39.3 g each (the rail carriage, the jaw
carrier and the jaw). The inertia is about the centre of mass, with the axes of the frame above, as the elements of
the inertia tensor that a URDF's `<inertia>` takes.

The solid and the soft TPU jaws have the same mass data in the
model, so one row serves both. Closed is the model's closed end of the travel.

Opening and closing move the two
jaws along Y by the same amount in opposite directions: the centre of mass stays where it is, Ixx and Izz change.
The URDF and the MJCF model give the jaws different centres of mass and inertias, hence the two pairs of rows.

## Tool centre point

| Jaws | The point | x (mm) | y (mm) | z (mm) | Orientation | Opening |
|---|---|---|---|---|---|---|
| Solid | the middle between the jaw tips | −28.35 | 0 | 110.30 | the frame's axes | any |
| Solid | the middle between the gripping faces | −28.43 | 0 | 79.65 | the frame's axes | any |
| Soft TPU | the middle between the jaw tips | −28.35 | 0 | 110.30 | the frame's axes | any |
| Soft TPU | the middle between the TPU pads | −28.43 | 0 | 80.15 | the frame's axes | any |
| Both | the model's `tcp` frame | −28.35 | 0 | 99.30 | the frame's axes | any |

The two jaws move by the same amount in opposite directions, so each point stays on the gripper's centre plane
(y = 0) at every opening.

A gripping face is the centre of its area: the solid jaw's face is 18.00 mm wide along X
and runs from z = 51.30 to 110.30 mm, the TPU pad from z = 52.30 to 110.30 mm.

Fully open, the solid jaws' faces
are 106.20 mm apart, the TPU pads 104.20 mm. The model's `tcp` is its control point on the jaws' centre line,
11.00 mm short of the tips, the same for both jaws; robot_descriptions says it is not a measured grasp centre.

## How accurate this is

The masses are measured: about 380 g for the whole gripper with the 150 mm rail and the 21.5 mm stepper (the
variant the model shows), 39.3 g for each moving assembly (an approximate
figure).

The centres of mass and the inertias are not: robot_descriptions 2.18.1 calls them existing, unverified
estimates, not scaled to the measured masses or checked against the CAD's mass distribution. Use them for
simulation and for a first payload setting, not as a measurement.

The model has one variant; a longer rail or
stepper is heavier and moves the centre of mass toward the extra part, and the model does not say by how much.

## Where the numbers go

In the PAROL6 Python API the MSG is a built-in tool, `rbt.select_tool("MSG", variant_key="150mm")`, with its TCP at
(−29, 0, −109.5) mm in the API's flange frame, whose Z points back into the wrist
([Tools and the TCP](https://docs.source-robotics.com/PAROL-docs/latest/programming/02-python-api/tools-and-tcp/)).

In a URDF, the mass, the centre of mass and the inertia go into the gripper link's `<inertial>` and the TCP into a
fixed joint from the mounting frame.
