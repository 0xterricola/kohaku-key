"""Mock-only native ECC physical runner regression tests.

No PC/SC import, card selection, or physical APDU execution.
"""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "RAILGUN/scripts/physical_native_ecc.py"

spec = importlib.util.spec_from_file_location(
    "physical_native_ecc_under_test", RUNNER
)
ecc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ecc)


class FakeConnection:
    def __init__(
        self, vectors, stage=11, bad_index=None,
        bad_sw=None, bad_select=False
    ):
        self.expected = {
            command: result
            for _, command, result in vectors
        }
        self.stage = stage
        self.bad_index = bad_index
        self.bad_sw = bad_sw
        self.bad_select = bad_select
        self.commands = []

    def transmit(self, command):
        command = bytes(command)
        self.commands.append(command)

        if command == ecc.SELECT:
            return ([], 0x6A, 0x82) if self.bad_select else (
                [], 0x90, 0x00
            )

        if command == ecc.STAGE:
            return [self.stage], 0x90, 0x00

        if command not in self.expected:
            raise AssertionError("Unexpected APDU sent to fake")

        index = command[2]

        if index == self.bad_sw:
            return [], 0x6F, 0x02

        result = self.expected[command]

        if index == self.bad_index:
            result = bytes([result[0] ^ 1]) + result[1:]

        return list(result), 0x90, 0x00


class NativeEccRunnerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.vectors = ecc.load_vectors()

    def test_01_fixture_has_six_fixed_public_commands(self):
        self.assertEqual(len(self.vectors), 6)
        self.assertEqual(
            [cmd.hex().upper() for _, cmd, _ in self.vectors],
            [f"8075{i:02X}0000" for i in range(6)]
        )

    def test_02_successful_two_round_replay(self):
        fake = FakeConnection(self.vectors)
        report = ecc.execute(fake, self.vectors, 2)
        self.assertEqual(report["verified"], 12)
        self.assertEqual(report["stage_verified"], 11)
        self.assertFalse(report["generation_attested"])
        self.assertEqual(len(report["samples"]), 12)
        self.assertEqual(len(fake.commands), 14)
        self.assertEqual(fake.commands[:2], [
            ecc.SELECT, ecc.STAGE
        ])
        self.assertEqual(
            [sample["index"] for sample in report["samples"]],
            list(range(6)) * 2
        )
        for item in report["per_vector"].values():
            self.assertEqual(item["count"], 2)
            self.assertGreaterEqual(item["median_ms"], 0)

    def test_03_reject_wrong_initialization_stage(self):
        fake = FakeConnection(self.vectors, stage=10)
        with self.assertRaisesRegex(
            ecc.BenchmarkError, "stage 11"
        ):
            ecc.execute(fake, self.vectors, 1)
        self.assertEqual(fake.commands, [
            ecc.SELECT, ecc.STAGE
        ])

    def test_04_reject_corrupt_cryptographic_output(self):
        fake = FakeConnection(self.vectors, bad_index=3)
        with self.assertRaisesRegex(
            ecc.BenchmarkError, "cryptographic response mismatch"
        ):
            ecc.execute(fake, self.vectors, 1)

    def test_05_reject_non_success_status(self):
        fake = FakeConnection(self.vectors, bad_sw=2)
        with self.assertRaisesRegex(
            ecc.BenchmarkError, "SW=6F02"
        ):
            ecc.execute(fake, self.vectors, 1)

    def test_06_reject_failed_applet_select(self):
        fake = FakeConnection(self.vectors, bad_select=True)
        with self.assertRaisesRegex(
            ecc.BenchmarkError, "SELECT failed: 6A82"
        ):
            ecc.execute(fake, self.vectors, 1)
        self.assertEqual(fake.commands, [ecc.SELECT])

    def test_07_block_install_and_initialize(self):
        fake = FakeConnection(self.vectors)
        allowed = ecc.allowed_commands(self.vectors)
        forbidden = [
            bytes.fromhex("80E4000000"),
            bytes.fromhex("8071010000"),
            bytes.fromhex("8076000000"),
            bytes.fromhex("8075060000"),
            bytes.fromhex("00A4040008FFFFFFFFFFFFFFFF"),
        ]
        for command in forbidden:
            with self.subTest(command=command.hex()):
                with self.assertRaisesRegex(
                    ecc.BenchmarkError, "Blocked APDU"
                ):
                    ecc.transmit(fake, command, allowed)
        self.assertEqual(fake.commands, [])

    def test_08_offline_cli_never_requests_pcsc(self):
        process = subprocess.run(
            [sys.executable, "-B", str(RUNNER)],
            capture_output=True, text=True, check=True
        )
        self.assertIn(
            "OFFLINE VALIDATION ONLY", process.stdout
        )
        self.assertIn("Six pinned", process.stdout)

    def test_09_refuse_execution_without_authorization(self):
        process = subprocess.run(
            [
                sys.executable, "-B", str(RUNNER),
                "--execute-public-vectors",
            ],
            capture_output=True, text=True
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn(
            "--confirm-test-card required", process.stderr
        )


if __name__ == "__main__":
    unittest.main()
