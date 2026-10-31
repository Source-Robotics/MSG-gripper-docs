# Mechanical assembly

The assembly is shown in the repository's video; a PDF manual is in preparation. Watch the video once before you
start, with the parts in front of you.

<iframe width="100%" height="460" src="https://www.youtube-nocookie.com/embed/oAUhDKYgLso" title="MSG gripper assembly" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

[Open the video on YouTube](https://youtu.be/oAUhDKYgLso)

## The order

1. The driver first: calibrated, in gripper mode, with the thermistor, as [Driver setup and first run](https://docs.source-robotics.com/MSG-gripper-docs/1.1/build/first-run/)
   describes. The motor calibration turns the stepper several revolutions, which the racks cannot follow, so it
   happens before the pinion meshes.
2. The brass inserts into the printed parts with a soldering iron.
3. The rail with its two carriages into the body, the racks onto the carriers.
4. The stepper, with the pinion on its shaft and the driver on its back, into the body so that the pinion meshes
   with both racks; the thermistor's leads to the driver.
5. The driver's power and CAN cables to the M8 connector in its lid; the lid onto the body.
6. The stepper cover over the driver, with the termination switch reachable through its opening.
7. The coupler plate with the shaft coupler on the back, or `ring_cover-PAROL6` for the PAROL6 wrist.
8. The jaws onto the carriers, the camera into its mount.

## The cable

The gripper's cable is not in the box. [The cable](https://docs.source-robotics.com/MSG-gripper-docs/1.1/04-installation/cable/) has the parts, the wiring
diagrams for PAROL6 and PAR6, and the warning that the two are not interchangeable; the repository's
[cable guide](https://github.com/Source-Robotics/MSG-compliant-AI-stepper-gripper/blob/main/Assembly%20manual/Building_cables.md)
is the original.

## The jaws

Printing, gluing and padding the jaws: [Printing the parts](https://docs.source-robotics.com/MSG-gripper-docs/1.1/build/printing/) and [Jaws](https://docs.source-robotics.com/MSG-gripper-docs/1.1/04-installation/jaws/).
