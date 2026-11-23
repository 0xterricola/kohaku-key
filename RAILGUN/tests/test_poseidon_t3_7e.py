"""Offline regression tests for the verified 7E baseline."""
from pathlib import Path
import hashlib
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "vectors/poseidon-t3-rounds.json"
RUNNER = ROOT / "scripts/poseidon_t3_7e_legacy.py"
ARCHIVE = ROOT / "benchmarks/poseidon-t3-rsa5-7e-2026-11-21"

PINS = {
    FIXTURE: "9055080ad906b5fe73c83aa21e01303cfcf6d1137d3ab2f435ead179283ab5fe",
    RUNNER: "2e89eaf498f1a2516996a8c3a097684a86ea85469de520e0bf1312665d8d1c7b",
    ARCHIVE / "one-two.json": "84a37ed7bff0b1fdb834a82105fd6910fbda1b643b363df181ef3bc2256ab7bb",
    ARCHIVE / "three-five.json": "1ca1e0cefd7de2a1fdea059ebaf4181a3923f91266185c55d6525f01a1380864",
}

class Poseidon7ETests(unittest.TestCase):
    def test_artifact_integrity(self):
        for path, expected in PINS.items():
            with self.subTest(path=path.name):
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    expected
                )

    def test_all_reference_rounds(self):
        data = json.loads(FIXTURE.read_text())
        self.assertEqual(
            (data["width"], data["full_rounds"],
             data["partial_rounds"]), (3, 8, 57)
        )
        p = int(data["field"])
        constants = [int(x) for x in data["round_constants"]]
        matrix = [[int(x) for x in row] for row in data["mds"]]

        self.assertEqual(len(constants), 195)
        self.assertEqual(len(data["vectors"]), 5)
        self.assertEqual(
            [v["name"] for v in data["vectors"]],
            ["zero", "one-two", "three-five", "mixed", "boundary"]
        )

        total = 0
        for vector in data["vectors"]:
            x, y = map(int, vector["inputs"])
            state = [0, x, y]
            self.assertEqual(len(vector["states"]), 65)

            for r in range(65):
                state = [
                    (state[i] + constants[r*3+i]) % p
                    for i in range(3)
                ]
                full = r < 4 or r >= 61
                state = [
                    pow(v, 5, p) if full or i == 0 else v
                    for i, v in enumerate(state)
                ]
                state = [
                    sum(matrix[i][j] * state[j]
                        for j in range(3)) % p
                    for i in range(3)
                ]
                self.assertEqual(
                    state,
                    list(map(int, vector["states"][r])),
                    (vector["name"], r)
                )
                total += 1

            self.assertEqual(state[0], int(vector["expected_hash"]))

        self.assertEqual(total, 325)

if __name__ == "__main__":
    unittest.main()
