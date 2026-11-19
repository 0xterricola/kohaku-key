#!/usr/bin/env python3
"""Compare public PACE vectors with recorded physical APDUs. Offline only."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def hexb(value):
    s = re.sub(r"[\s:]", "", str(value))
    if s.lower().startswith("0x"):
        s = s[2:]
    return bytes.fromhex(s)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    fixture = ROOT / "vectors/PUBLIC-PACE-VECTORS.json"
    data = json.loads(fixture.read_text())
    vectors = data["vectors"]

    records = [
        json.loads(line)
        for line in (args.trace / "apdu.jsonl").read_text().splitlines()
        if line.strip()
    ]

    pace = {}
    for record in records:
        match = re.fullmatch(
            r"pace-(\d+)", str(record.get("label", ""))
        )
        if match:
            index = int(match.group(1))
            if index in pace:
                raise SystemExit("STOP: Duplicate PACE record")
            pace[index] = record

    if len(vectors) != 10 or set(pace) != set(range(1, 11)):
        raise SystemExit("STOP: Unexpected PACE vector or trace count")

    print("◆ PHYSICAL TRACE ↔ PUBLIC VECTOR COMPARISON")
    print("Offline only | No APDUs transmitted")
    print()

    results = []

    for i, vector in enumerate(vectors, 1):
        record = pace[i]

        apdu = hexb(record["apdu_hex"])
        response = hexb(record["response_hex"])
        public_apdu = hexb(vector["apdu_hex"])
        point = hexb(vector["input_hex"])
        expected = hexb(vector["expected_hex"])

        result = {
            "test": i,
            "h_multiplier": str(vector["h_multiplier"]),
            "apdu_bytes": len(apdu),
            "header": apdu[:5].hex().upper(),
            "public_apdu_exact": apdu == public_apdu,
            "input_contained": point in apdu,
            "response_exact": response == expected,
            "status_word": str(record.get("sw")),
            "response_bytes": len(response),
        }
        results.append(result)

        print(
            f"{i:02d} j={result['h_multiplier']:>2} "
            f"APDU={len(apdu)}B "
            f"header={result['header']} "
            f"input={result['input_contained']} "
            f"output={result['response_exact']} "
            f"SW={result['status_word']}"
        )

    inputs = sum(r["input_contained"] for r in results)
    outputs = sum(r["response_exact"] for r in results)
    exact = sum(r["public_apdu_exact"] for r in results)

    report = {
        "mode": "offline",
        "tests": 10,
        "public_apdu_matches": exact,
        "input_point_matches": inputs,
        "expected_response_matches": outputs,
        "results": results,
        "card_access": False,
    }

    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n")

    print("\n◆ RESULTS")
    print(f"Exact public APDU matches: {exact}/10")
    print(f"Public input point matches: {inputs}/10")
    print(f"Expected output matches: {outputs}/10")
    print("Hardware access: NONE")

    if outputs == 10 and inputs == 10:
        print("PASS: Physical trace reconciled with public vectors")
    else:
        print("REVIEW: Physical protocol requires further mapping")

if __name__ == "__main__":
    main()
