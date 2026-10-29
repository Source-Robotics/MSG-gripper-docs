# API reference

The CAN messages and UART commands a gripper needs, the status and error bits, and the Python library's calls
that send them, for the firmware release this site describes.

The gripper is a STEPFOC driver in gripper mode and understands the driver's whole command set. This reference
lists the gripper messages, the system and status messages a gripper host uses, and the driver commands a
self-built gripper is configured with. Everything else, from the motion commands to the tuning gains, is in the
[STEPFOC reference](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/).

## Where the facts come from

The command IDs, the frame lengths the firmware accepts, the responses it sends, the list of UART commands with
their kind (Set/Get, Get or action), their argument type and what they print are read from the STEPFOC firmware's
source at its release tag by `tools/sync_firmware.py` in the documentation repository, and the pages are built
from that at every build. The descriptions, units and byte layouts are written by hand, and the build fails when
they name a command the firmware does not have, or when a byte layout does not fit the frame. The firmware
version is in the version box on the [landing page](../index.md).

## Conventions

- **Bytes** are numbered from 0, the first byte on the bus (`data[0]`). Multi-byte values are **big-endian**: the
  most significant byte first.
- **Bits** inside a byte are numbered from the most significant bit: bit 7 is the first flag the firmware packs
  into the byte, bit 0 the last.
- The gripper's **position** is 0 (open) to 255 (closed), its **speed** 0 to 255, its **current** in mA.
- UART command names are **case-sensitive** and spelled exactly as the firmware compares them.

## In the API reference

- [CAN messages](can/index.md): the identifier, and the gripper, system and status messages
- [UART commands](uart/index.md): the gripper commands, the driver setup commands, status and utility
- [Errors and status bits](errors.md)
- [Python library](python.md): library call → message
