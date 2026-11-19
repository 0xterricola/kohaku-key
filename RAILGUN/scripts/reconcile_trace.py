#!/usr/bin/env python3
"""Offline verification of recorded public PACE-GM APDUs."""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from physical_pace import BenchmarkError, published_vectors, require


def decode(value):
    require(isinstance(value, str), "Expected hex string")
    return bytes.fromhex(
        value.strip().replace(" ", "").replace(":", "")
        .removeprefix("0x").removeprefix("0X")
    )


def reconcile(records, vectors):
    require(isinstance(records, list), "Invalid trace records")
    require(len(vectors) == 10, "Expected 10 public vectors")

    indexed = {}
    for record in records:
        require(isinstance(record, dict), "Malformed trace record")
        label = record.get("label", "")
        if not isinstance(label, str) or not label.startswith("pace-"):
            continue
        require(label not in indexed, "Duplicate PACE record")
        indexed[label] = record

    require(len(indexed) == 10, "Expected 10 PACE records")
    results = []

    for position, (index, command, expected) in enumerate(vectors, 1):
        label = f"pace-{position:02d}"
        require(label in indexed, f"Missing {label}")
        record = indexed[label]

        require(decode(record["apdu_hex"]) == command,
                f"{label}: APDU mismatch")
        require(str(record["sw"]).upper() == "9000",
                f"{label}: unsuccessful status")
        require(decode(record["response_hex"]) == expected,
                f"{label}: response mismatch")

        elapsed = float(record["elapsed_ms"])
        require(math.isfinite(elapsed) and 0 <= elapsed < 1000000,
                f"{label}: invalid timing")

        results.append({
            "index": index,
            "label": label,
            "status_word": "9000",
            "response_match": True,
            "apdu_match": True,
            "elapsed_ms": elapsed,
        })

    median = statistics.median(r["elapsed_ms"] for r in results)
    return {
        "status": "PASS",
        "mode": "offline-trace-reconciliation",
        "card_access": False,
        "verified_vectors": 10,
        "median_recorded_ms": round(median, 3),
        "timing_scope": "recorded external trace; not newly measured",
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True,
                        help="JSONL file or directory containing apdu.jsonl")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    path = args.trace
    if path.is_dir():
        path = path / "apdu.jsonl"

    require(path.is_file(), "Trace file missing")
    require(path.stat().st_size <= 2_000_000,
            "Trace exceeds maximum size")

    records = [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]

    result = reconcile(records, published_vectors())

    print("PASS 10/10 recorded PACE APDUs")
    print("PASS 10/10 status words")
    print("PASS 10/10 exact responses")
    print("Recorded median:", result["median_recorded_ms"], "ms")
    print("Hardware accessed: NO")

    if args.report:
        require(not args.report.is_symlink(),
                "Report must not be a symlink")
        require(not args.report.exists(),
                "Report already exists")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (BenchmarkError, OSError, ValueError, KeyError,
            TypeError, json.JSONDecodeError) as exc:
        sys.exit("STOP: " + str(exc))
