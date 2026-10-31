# Variants

The gripper is modular in two ways: the length of the linear rail sets the stroke, the length of the stepper sets
the force. Any rail goes with any stepper, and the body comes in black or grey; the body, the jaw carriers and the
stepper cover are printed for the chosen combination.

<figure markdown="span">
  ![The three rail lengths](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/Gripper_strokes.webp){ width="900" }
  <figcaption>Figure 2: The three rail lengths and the stroke each gives.</figcaption>
</figure>

=== "Black"
    <figure markdown="span">
      ![The nine variants, black body](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/MSG_variants_black.webp){ width="900" }
      <figcaption>Figure 3: The nine combinations of rail and stepper, black body: 55, 105 and 155 mm of stroke across, the 21.5, 40 and 60 mm steppers down.</figcaption>
    </figure>

=== "Grey"
    <figure markdown="span">
      ![The nine variants, grey body](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/MSG_variants_grey.webp){ width="900" }
      <figcaption>The same nine combinations, grey body.</figcaption>
    </figure>

## Rail length and stroke

| Rail | Stroke | Printed parts |
|---|---|---|
| 100 mm | 55 mm | `MSG_Gripper_body_100mm`, `gripper_jaw_100mm_L/R` |
| 150 mm | 105 mm | `MSG_Gripper_body_150mm`, `gripper_jaw_150mm_L/R` |
| 200 mm | 155 mm | `MSG_Gripper_body_200mm`, `gripper_jaw_200mm_L/R` |

The stroke is the distance between the jaw carriers from fully open to fully closed; the opening between the
jaw faces depends on the jaws you fit ([Jaws](https://docs.source-robotics.com/MSG-gripper-docs/1.1/04-installation/jaws/)). A longer rail makes the gripper wider
and a little heavier and does not change the force.

## Stepper length and force

| Stepper | Motor | Maximum current | Assumed torque constant | Ideal combined force at the maximum current | Printed parts |
|---|---|---|---|---|---|
| 21.5 mm | 17HS08-1004S | 1.5 A | 0.17 Nm/A | about 31 N | `Stepper_cover_21_5mm`, `Stepper_spacer_21_5` |
| 40 mm | 17HS16-2004S1 | 2.0 A | 0.21 Nm/A | about 50 N | `Stepper_cover_40mm` |
| 60 mm | 17HS24-2104S | 2.1 A | 0.30 Nm/A | about 76 N | `Stepper_cover_60mm` |

A longer stepper gives more torque and so more grip force, at the price of weight and length behind the
gripper. The force is proportional to the current limit you command, with the slope of the stepper's torque
constant; the curves and the formula are in [Force and speed](https://docs.source-robotics.com/MSG-gripper-docs/1.1/03-technical-data/force-and-speed/). The
current limit must stay within the stepper's maximum.

## Grasps

The gripper grips from the outside (the jaws close on the object) and from the inside (the jaws open inside a
hollow object). Both are the same move command with a different target; object detection reports *while closing*
for the first and *while opening* for the second.

## The camera

The camera mount on top of the body carries an OV9732 USB camera module (100° version in the BOM), looking down
between the jaws. Its place and angle were chosen with care: the camera sees both jaws and the object between
them, the view that teleoperation and VLA training need. It is a plain USB camera with its own cable,
independent of the gripper's electronics; the mount
and its lid are printed parts (`camera extension`, `camera_lid`), and a gripper without a camera simply leaves
them off.

<figure markdown="span">
  ![The camera's view](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/MSG_and_camera.webp){ width="700" }
  <figcaption>Figure 4: The gripper on a PAROL6 and what its camera sees.</figcaption>
</figure>
