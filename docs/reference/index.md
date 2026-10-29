# API reference

The gripper's CAN messages and UART commands, its status and error bits, and the Python library calls that send
them, for the firmware named on the landing page. The gripper is a STEPFOC stepper driver in gripper mode and accepts the
driver's whole command set; only what a gripper host or a self-built gripper needs is here, the rest is in the
[STEPFOC reference](https://docs.source-robotics.com/STEPFOC-docs/latest/reference/).

- [CAN messages](can/index.md): the identifier, and the gripper, system and status messages
- [UART commands](uart/index.md): the gripper commands, the driver setup commands, status and utility
- [Errors and status bits](errors.md)
- [Python library](python.md): which library call sends which message

**Conventions.** Bytes are numbered from 0 and multi-byte values are big-endian. Bits are numbered from the most
significant: bit 7 is the first flag in a byte. The position is 0 (open) to 255 (closed), the speed 0 to 255, the
current in mA. UART command names are case-sensitive.

The command IDs, frame lengths and responses are read from the firmware's source at its release tag when the site
is built, so they cannot drift from the firmware; the descriptions and byte layouts are written by hand.
