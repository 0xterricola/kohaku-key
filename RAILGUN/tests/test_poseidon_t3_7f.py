"""Offline regression for Poseidon T3 Barrett 7F."""

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RUNNER = ROOT / "scripts/poseidon_t3_7f.py"
REPORT = (
    ROOT / "benchmarks/poseidon-t3-rsa5-7f-2026-11-23"
    / "M3.42j.24-reported.json"
)

spec = importlib.util.spec_from_file_location("poseidon7f", RUNNER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestPoseidon7F(unittest.TestCase):
    def test_canonical_vectors(self):
        self.assertEqual(module.offline_test(), 325)

    def test_report(self):
        data = json.loads(REPORT.read_text())

        self.assertEqual(data["physical_rounds_verified"], 65)
        self.assertEqual(data["canonical_final"], "PASS")
        self.assertFalse(data["raw_timing_trace_available"])

        self.assertGreater(
            data["host_elapsed_ms"],
            data["7e_reference_ms"]
        )

if __name__ == "__main__":
    unittest.main()
