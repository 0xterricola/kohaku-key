"""Offline trace reconciliation regression tests."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "RAILGUN/scripts"
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location(
    "reconcile_trace", SCRIPTS / "reconcile_trace.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

from physical_pace import BenchmarkError

fixture = json.loads(
    (ROOT / "RAILGUN/vectors/PUBLIC-PACE-VECTORS.json").read_text()
)
vectors = [
    (v["index"], bytes.fromhex(v["apdu_hex"]),
     bytes.fromhex(v["expected_hex"]))
    for v in fixture["vectors"]
]


def make_records():
    return [
        {
            "label": f"pace-{i:02d}",
            "apdu_hex": command.hex(),
            "response_hex": expected.hex(),
            "sw": "9000",
            "elapsed_ms": 225.0,
        }
        for i, (_, command, expected) in enumerate(vectors, 1)
    ]


class TraceTests(unittest.TestCase):
    def test_01_valid_trace(self):
        result = module.reconcile(make_records(), vectors)
        self.assertEqual(result["verified_vectors"], 10)
        self.assertFalse(result["card_access"])

    def test_02_duplicate_record(self):
        records = make_records()
        records.append(records[0].copy())
        with self.assertRaisesRegex(BenchmarkError, "Duplicate"):
            module.reconcile(records, vectors)

    def test_03_wrong_apdu(self):
        records = make_records()
        records[0]["apdu_hex"] = "80780000"
        with self.assertRaisesRegex(BenchmarkError, "APDU mismatch"):
            module.reconcile(records, vectors)

    def test_04_bad_status(self):
        records = make_records()
        records[0]["sw"] = "6A80"
        with self.assertRaisesRegex(BenchmarkError, "status"):
            module.reconcile(records, vectors)

    def test_05_bad_response(self):
        records = make_records()
        records[0]["response_hex"] = "04"
        with self.assertRaisesRegex(BenchmarkError, "response mismatch"):
            module.reconcile(records, vectors)


if __name__ == "__main__":
    unittest.main()
