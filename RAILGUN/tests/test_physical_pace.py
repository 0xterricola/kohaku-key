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
    def __init__(self, stage=11, bad_index=None, bad_sw=None,
                 bad_status=(0x6A, 0x80)):
        self.stage = stage
        self.bad_index = bad_index
        self.bad_sw = bad_sw
        self.bad_status = bad_status
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
            return list(response), *self.bad_status

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


    def test_05_jcop4_k1_select_and_vectors(self):
        fake = FakeConnection()
        result = pace.replay(fake, VECTORS, applet="jcop4-k1")
        self.assertEqual(result["vectors_verified"], 10)
        self.assertEqual(
            result["applet_aid"], "F0424E3235344E01"
        )
        self.assertEqual(
            result["applet_configuration"], "jcop4-k1"
        )
        self.assertEqual(
            fake.commands[0],
            bytes.fromhex("00A4040008F0424E3235344E01")
        )

    def test_06_default_published_select(self):
        fake = FakeConnection()
        result = pace.replay(fake, VECTORS)
        self.assertEqual(
            result["applet_aid"], "F0424E3235343C01"
        )
        self.assertEqual(
            fake.commands[0],
            bytes.fromhex("00A4040008F0424E3235343C01")
        )

    def test_07_reject_unknown_applet_before_apdu(self):
        fake = FakeConnection()
        with self.assertRaisesRegex(
            pace.BenchmarkError, "Unknown applet"
        ):
            pace.replay(fake, VECTORS, applet="unknown")
        self.assertEqual(fake.commands, [])

    def test_08_explain_jcop4_uninitialized_key(self):
        fake = FakeConnection(
            bad_sw=0, bad_status=(0x6F, 0x02)
        )
        with self.assertRaisesRegex(
            pace.BenchmarkError, "UNINITIALIZED_KEY"
        ):
            pace.replay(fake, VECTORS, applet="jcop4-k1")
        self.assertEqual(len(fake.commands), 3)

    def test_09_jcop4_reject_uninitialized_stage(self):
        fake = FakeConnection(stage=0)
        with self.assertRaisesRegex(
            pace.BenchmarkError, "stage 11"
        ):
            pace.replay(fake, VECTORS, applet="jcop4-k1")
        self.assertEqual(len(fake.commands), 2)



    def test_10_block_unknown_apdu_before_transmission(self):
        fake = FakeConnection()
        allowed = pace.public_allowlist(
            VECTORS, pace.APPLET_CONFIGS["published"]
        )
        with self.assertRaisesRegex(
            pace.BenchmarkError, "Blocked APDU"
        ):
            pace.transmit(fake, bytes.fromhex("80E4000000"), allowed)
        self.assertEqual(fake.commands, [])

    def test_11_reject_modified_vector_before_select(self):
        fake = FakeConnection()
        mutated = list(VECTORS)
        index, command, expected = mutated[0]
        mutated[0] = (
            index, command[:-1] + bytes([command[-1] ^ 1]),
            expected
        )
        with self.assertRaisesRegex(
            pace.BenchmarkError, "differs from published fixture"
        ):
            pace.replay(fake, mutated)
        self.assertEqual(fake.commands, [])

    def test_12_reject_truncated_vector_set(self):
        fake = FakeConnection()
        with self.assertRaisesRegex(
            pace.BenchmarkError, "differs from published fixture"
        ):
            pace.replay(fake, VECTORS[:-1])
        self.assertEqual(fake.commands, [])



    def test_13_block_install_apdu(self):
        fake = FakeConnection()
        allowed = pace.public_allowlist(
            VECTORS, pace.APPLET_CONFIGS["published"]
        )
        with self.assertRaisesRegex(
            pace.BenchmarkError, "Blocked APDU"
        ):
            pace.transmit(
                fake, bytes.fromhex("80E6020000"), allowed
            )
        self.assertEqual(fake.commands, [])

    def test_14_block_wrong_applet_select(self):
        fake = FakeConnection()
        allowed = pace.public_allowlist(
            VECTORS, pace.APPLET_CONFIGS["published"]
        )
        with self.assertRaisesRegex(
            pace.BenchmarkError, "Blocked APDU"
        ):
            pace.transmit(
                fake,
                bytes.fromhex("00A4040008F0424E3235344E01"),
                allowed
            )
        self.assertEqual(fake.commands, [])


if __name__ == "__main__":
    unittest.main()
