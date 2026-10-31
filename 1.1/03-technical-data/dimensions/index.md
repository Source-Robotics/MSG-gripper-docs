# Dimensions and CAD

<div class="gripper-viewer" data-base="../../assets/models/msg/" markdown="0">
  <canvas class="gripper-viewer__canvas" aria-label="The MSG gripper in 3D: drag to turn, scroll to zoom"></canvas>
  <div class="gripper-viewer__controls">
    <label class="gripper-viewer__field">Opening <input type="range" name="opening" min="0" max="100" value="50"></label>
    <label class="gripper-viewer__field">Body <span class="gripper-viewer__swatches" data-target="body"></span><input type="color" name="body" value="#d2d2cf" title="Any colour"></label>
    <label class="gripper-viewer__field">Jaws <span class="gripper-viewer__swatches" data-target="jaws"></span><input type="color" name="jaws_color" value="#1a1a1a" title="Any colour"></label>
    <button type="button" name="reset" class="md-button">Reset view</button>
  </div>
  <p class="gripper-viewer__hint">Drag to turn the gripper, scroll to zoom, open and close the jaws, try the colours. The model is the
repository's <a href="https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/MSG_gripper_description">URDF</a> of the 150 mm rail variant; the shop sells the body in black and grey.</p>
</div>

The gripper's dimensions depend on the rail and the stepper: the rail length sets the width (100, 150 or 200 mm
plus the jaws at full opening), the stepper length what sticks out behind the body. The STEP files of every part
and of the whole gripper in each variant are in the product repository, and are the reference for anything that
has to fit:

- [STEP files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/STEP%20files):
  `Common parts` (the coupler plate, the ring covers, the camera mount, the jaw blocker, the stepper spacer),
  `Linear rail dependant parts` (the body and the jaw carriers per rail length), `Stepper dependant parts` (the
  covers and spacers per stepper length), `Gripper jaws attachment` (the jaw designs), `Tools` (the magnet tool).
- [Print files](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/Print%20files):
  the same parts as 3MF, ready to slice.

<figure markdown="span">
  ![The STEP model](https://docs.source-robotics.com/MSG-gripper-docs/1.1/assets/MSG_3D_model.webp){ width="600" }
  <figcaption>Figure 7: The STEP model of the gripper, seen from the coupler plate.</figcaption>
</figure>

## For simulation

The [MSG_gripper_description](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/tree/main/MSG_gripper_description)
folder has a URDF of the gripper for ROS 2 and Gazebo and an MJCF for MuJoCo 3.1.3 and newer, with a scene file.

[CAD and downloads](https://docs.source-robotics.com/MSG-gripper-docs/1.1/cad-files/) lists everything that can be downloaded.
