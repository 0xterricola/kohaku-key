"""Mock PC/SC regression tests. No physical card communication."""
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "RAILGUN/scripts/physical_pace.py"

spec = importlib.util.spec_from_file_location("physical_pace", SCRIPT)
pace = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pace)

fixture = json.loads(
    (ROOT / "RAILGUN/vectors/PUBLIC-PACE-VECTORS.json").read_text()
)
VECTORS = [
    (v["index"], bytes.fromhex(v["apdu_hex"]),
     bytes.fromhex(v["expected_hex"]))
    for v in fixture["vectors"]
]


class FakeConnection:
    def __init__(self, stage=11, bad_index=None, bad_sw=None):
        self.stage = stage
        self.bad_index = bad_index
        self.bad_sw = bad_sw
        self.commands = []

    def transmit(self, command):
        command = bytes(command)
        self.commands.append(command)

        if command.startswith(bytes.fromhex("00A40400")):
            return [], 0x90, 0x00

        if command == bytes.fromhex("80710000"):
            return [self.stage], 0x90, 0x00

        position = len(self.commands) - 3
        if position < 0 or position >= len(VECTORS):
            raise AssertionError("Unexpected APDU")

        _, expected_command, response = VECTORS[position]
        assert command == expected_command, "Unexpected public vector"

        if position == self.bad_index:
            response = bytes([response[0] ^ 1]) + response[1:]

        if position == self.bad_sw:
            return list(response), 0x6A, 0x80

        return list(response), 0x90, 0x00


class PhysicalPaceMockTests(unittest.TestCase):
    def test_01_ten_public_vectors(self):
        fake = FakeConnection()
        result = pace.replay(fake, VECTORS)
        self.assertEqual(result["vectors_verified"], 10)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(fake.commands), 12)
        self.assertTrue(all(
            item["response_match"] for item in result["results"]
        ))

    def test_02_reject_uninitialized_card(self):
        fake = FakeConnection(stage=0)
        with self.assertRaisesRegex(
            pace.BenchmarkError, "stage 11"
        ):
            pace.replay(fake, VECTORS)
        self.assertEqual(len(fake.commands), 2)

    def test_03_reject_corrupt_response(self):
        fake = FakeConnection(bad_index=0)
        with self.assertRaisesRegex(
            pace.BenchmarkError, "response mismatch"
        ):
            pace.replay(fake, VECTORS)
        self.assertEqual(len(fake.commands), 3)

    def test_04_reject_non_success_status(self):
        fake = FakeConnection(bad_sw=0)
        with self.assertRaisesRegex(
            pace.BenchmarkError, "status: 6A80"
        ):
            pace.replay(fake, VECTORS)
        self.assertEqual(len(fake.commands), 3)


if __name__ == "__main__":
    unittest.main()
