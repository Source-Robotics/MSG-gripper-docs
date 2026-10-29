# Copilot instructions

This repository is the documentation of the MSG gripper, built with MkDocs Material in the same form as the other
Source Robotics documentation (STEPFOC-docs, Spectral-BLDC-docs, par6). README.md says how it is built, versioned
and published; the Contributing page on the site has the house rules.

- The manual chapters are the numbered folders under `docs/`; the API reference under `docs/reference/` is
  generated at build time from `docs/includes/generated/firmware_facts.json` (never edit) and the descriptions in
  `docs/includes/can_commands.yml` and `uart_commands.yml`.
- Facts come from the firmware (the STEPFOC release named in `versions.yml`) and the product repository. When a
  page and the firmware disagree, the firmware is right.
- Spell commands exactly as the firmware does. Write short sentences, in the second person, without filler.
- Every push runs `python tools/test_tools.py` and `mkdocs build --strict`; a broken link fails the build.
