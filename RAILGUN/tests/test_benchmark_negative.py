"""Offline adversarial tests for the published RAILGUN verifier.

Only temporary copies of public fixtures are modified.
No smart-card operations or APDUs.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
REL_VECTOR = "RAILGUN/vectors/PUBLIC-PACE-VECTORS.json"


class BenchmarkNegativeTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix="railgun-m35-"
        )
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

        shutil.copytree(
            SOURCE / "RAILGUN",
            self.root / "RAILGUN"
        )

        self.script = (
            self.root / "RAILGUN/scripts/benchmark.py"
        )
        self.fixture = self.root / REL_VECTOR
        self.manifest = (
            self.root / "RAILGUN/SHA256SUMS"
        )

    def execute(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(self.script), *args],
            cwd=self.root,
            text=True,
            capture_output=True,
            timeout=30,
        )

    def expect_stop(self, expected):
        result = self.execute()
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("STOP:", output)
        self.assertIn(expected, output)

    def update_manifest(self):
        digest = hashlib.sha256(
            self.fixture.read_bytes()
        ).hexdigest()

        lines = self.manifest.read_text().splitlines()
        updated = []
        found = False

        for line in lines:
            parts = line.split(None, 1)

            if len(parts) == 2 and (
                parts[1].lstrip("*") == REL_VECTOR
            ):
                updated.append(
                    f"{digest}  {REL_VECTOR}"
                )
                found = True
            else:
                updated.append(line)

        self.assertTrue(found, "Fixture absent from manifest")
        self.manifest.write_text(
            "\n".join(updated) + "\n"
        )

    def mutate_vectors(self, callback):
        data = json.loads(self.fixture.read_text())
        callback(data)
        self.fixture.write_text(
            json.dumps(data, indent=2) + "\n"
        )
        self.update_manifest()

    def test_01_baseline_offline_pass(self):
        result = self.execute()
        self.assertEqual(
            result.returncode, 0,
            result.stdout + result.stderr
        )
        self.assertIn(
            "PASS Offline validation complete",
            result.stdout
        )
        self.assertIn(
            "Physical execution: NOT IMPLEMENTED",
            result.stdout
        )

    def test_02_corrupted_manifest_digest(self):
        content = self.manifest.read_text()
        self.manifest.write_text(
            "0" * 64 + content[64:]
        )
        self.expect_stop("Checksum mismatch")

    def test_03_missing_artifact(self):
        self.fixture.unlink()
        self.expect_stop("Missing artifact")

    def test_04_duplicate_vector_index(self):
        def change(data):
            data["vectors"][1]["index"] = (
                data["vectors"][0]["index"]
            )

        self.mutate_vectors(change)
        self.expect_stop("Duplicate index")

    def test_05_off_curve_point(self):
        def change(data):
            data["vectors"][0][
                "expected_edwards_x"
            ] = "00"
            data["vectors"][0][
                "expected_edwards_y"
            ] = "00"

        self.mutate_vectors(change)
        self.expect_stop("Off-curve")

    def test_06_invalid_h_multiplier(self):
        def change(data):
            data["vectors"][0][
                "h_multiplier"
            ] = "0"

        self.mutate_vectors(change)
        self.expect_stop("Invalid H multiplier")

    def test_07_group_law_mismatch(self):
        def change(data):
            data["vectors"][0][
                "scalar_s"
            ] = "0"

        self.mutate_vectors(change)
        self.expect_stop("PACE H + sB mismatch")

    def test_09_invalid_apdu_cla(self):
        def change(data):
            v = data["vectors"][0]
            v["apdu_hex"] = "00" + v["apdu_hex"][2:]
        self.mutate_vectors(change)
        self.expect_stop("Unexpected APDU header")

    def test_10_invalid_apdu_ins(self):
        def change(data):
            v = data["vectors"][0]
            v["apdu_hex"] = v["apdu_hex"][:2] + "78" + v["apdu_hex"][4:]
        self.mutate_vectors(change)
        self.expect_stop("Unexpected APDU header")

    def test_11_invalid_apdu_p1(self):
        def change(data):
            v = data["vectors"][0]
            v["apdu_hex"] = v["apdu_hex"][:4] + "01" + v["apdu_hex"][6:]
        self.mutate_vectors(change)
        self.expect_stop("Unexpected APDU header")

    def test_12_invalid_apdu_p2(self):
        def change(data):
            v = data["vectors"][0]
            v["apdu_hex"] = v["apdu_hex"][:6] + "01" + v["apdu_hex"][8:]
        self.mutate_vectors(change)
        self.expect_stop("Unexpected APDU header")

    def test_13_invalid_apdu_lc(self):
        def change(data):
            v = data["vectors"][0]
            v["apdu_hex"] = v["apdu_hex"][:8] + "40" + v["apdu_hex"][10:]
        self.mutate_vectors(change)
        self.expect_stop("Invalid APDU Lc")

    def test_14_truncated_apdu(self):
        def change(data):
            v = data["vectors"][0]
            v["apdu_hex"] = v["apdu_hex"][:-2]
        self.mutate_vectors(change)
        self.expect_stop("Invalid APDU length")

    def test_15_mismatched_apdu_input(self):
        def change(data):
            data["vectors"][0]["apdu_hex"] = (
                data["vectors"][1]["apdu_hex"]
            )
        self.mutate_vectors(change)
        self.expect_stop("APDU input mismatch")

    def test_16_invalid_point_prefix(self):
        def change(data):
            v = data["vectors"][0]
            v["input_hex"] = "02" + v["input_hex"][2:]
        self.mutate_vectors(change)
        self.expect_stop("Invalid input_hex point encoding")

    def test_17_truncated_expected_point(self):
        def change(data):
            v = data["vectors"][0]
            v["expected_hex"] = v["expected_hex"][:-2]
        self.mutate_vectors(change)
        self.expect_stop("Invalid expected_hex point encoding")

    def test_18_wrong_instruction_metadata(self):
        def change(data):
            data["instruction"] = "0x78"
        self.mutate_vectors(change)
        self.expect_stop("Unexpected PACE instruction")

    def test_08_no_physical_execution_claim(self):
        report = self.root / "report.json"

        result = self.execute(
            "--report", str(report)
        )

        self.assertEqual(
            result.returncode, 0,
            result.stdout + result.stderr
        )

        data = json.loads(report.read_text())
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["mode"], "offline")
        self.assertIs(
            data["physical_execution"], False
        )
        self.assertIs(
            data["pace_operation_recomputed"], True
        )


if __name__ == "__main__":
    unittest.main()
