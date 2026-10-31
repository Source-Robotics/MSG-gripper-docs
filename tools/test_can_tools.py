"""Test generated layouts/DBC and the JS codec; optional cantools validates the DBC independently.

For independent DBC validation: pip install cantools==40.7.1
"""
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("can_tools_test", ROOT / "hooks/can_tools.py")
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)
SCHEMA = tools.protocol(ROOT / "docs", ROOT.name)
try:
    import cantools
except ImportError:
    cantools = None


class CanTools(unittest.TestCase):
    def test_versioned_facts_and_supported_commands(self):
        self.assertTrue(SCHEMA["firmware"].startswith(("V", "v")))
        self.assertRegex(SCHEMA["commit"], r"^[0-9a-f]{7,40}$")
        self.assertNotIn("IN_DATA_PACK_2", [c["key"] for c in SCHEMA["commands"]])
        grip = next(c for c in SCHEMA["commands"] if c["key"] == "IN_GRIPPER_DATA_PACK")
        self.assertEqual(grip["id"], 61)
        self.assertEqual({f["length"] for f in grip["forms"]}, {0, 5})

    def test_dbc_has_unique_standard_ids_and_fixed_motion_layouts(self):
        for length in (8, 5, 2):
            with self.subTest(length=length):
                text = tools.dbc(SCHEMA, length)
                frames = re.findall(r"^BO_ (\d+) (\w+): (\d+) (\w+)$", text, re.M)
                ids = [int(f[0]) for f in frames]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertTrue(all(0 <= n <= 0x7FF for n in ids))
                self.assertTrue(all(len(f[1]) <= 32 for f in frames))
                self.assertIn(0x078, ids)
                self.assertIn(0x079, ids)
                self.assertIn((13 << 7) | 0x079, ids)
                motion = [f for f in frames if int(f[0]) == 4]
                if motion:
                    self.assertEqual(int(motion[0][2]), length)

    @unittest.skipUnless(shutil.which("node"), "Node.js is needed for the offline JS codec tests")
    def test_browser_codec_against_known_wire_vectors(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "protocol.json"
            path.write_text(json.dumps(SCHEMA), encoding="utf-8")
            subprocess.run(["node", str(ROOT / "tools/test_can_codec.js"), str(path)], check=True)

    @unittest.skipUnless(cantools, "Install cantools for independent DBC parsing/decoding")
    def test_dbc_in_an_independent_decoder(self):
        for length in (8, 5, 2):
            database = cantools.database.load_string(tools.dbc(SCHEMA, length), "dbc", strict=True)
            command = database.get_message_by_frame_id(0x7A).decode(bytes.fromhex("C8 1E 01 2C C0"))
            self.assertEqual((command["Position"], command["Speed"], command["Current"]), (200, 30, 300))
            response = database.get_message_by_frame_id(0x79).decode(bytes.fromhex("64 FE D4 A1"))
            self.assertEqual(response["gripper_current"], -300)
            self.assertEqual(str(response["gripper_object_detection_raw"]), "object while closing")
            if any(c["key"] == "IN_DATA_PACK_1" for c in SCHEMA["commands"]):
                gains = database.get_message_by_frame_id(0x020).decode(bytes.fromhex("3F C0 00 00 C0 10 00 00"))
                self.assertEqual((gains["KP"], gains["KD"]), (1.5, -2.25))
                if length == 8:
                    motion = database.get_message_by_frame_id(0x004).decode(bytes.fromhex("80 00 00 7F FF FF 80 00"))
                    self.assertEqual(list(motion.values()), [-8388608, 8388607, -32768])


if __name__ == "__main__":
    unittest.main()
