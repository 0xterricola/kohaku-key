#!/usr/bin/env python3
"""Explicitly authorized public PACE-GM replay; no installation or wallet access."""

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "RAILGUN/vectors/PUBLIC-PACE-VECTORS.json"
AID = "F0424E3235343C01"


class BenchmarkError(Exception):
    pass


def require(ok, message):
    if not ok:
        raise BenchmarkError(message)


def published_vectors():
    # Verify authentic, unmodified public research artifacts first.
    check = subprocess.run(
        [sys.executable, "-B",
         str(ROOT / "RAILGUN/scripts/benchmark.py")],
        cwd=ROOT, capture_output=True, text=True,
        timeout=30
    )
    require(check.returncode == 0,
            "Offline artifact verification failed")

    data = json.loads(FIXTURE.read_text())
    require(data["applet_aid"].upper() == AID,
            "Unexpected applet AID")
    require(data["instruction"].lower() == "0x77",
            "Unexpected PACE instruction")
    require(len(data["vectors"]) == 10,
            "Expected exactly 10 public vectors")

    vectors = []
    for v in data["vectors"]:
        require(int(v["scalar_s"]) == 1,
                "Only public scalar s=1 is authorized")
        command = bytes.fromhex(v["apdu_hex"])
        expected = bytes.fromhex(v["expected_hex"])
        require(len(command) == 70 and
                command[:5] == bytes.fromhex("8077000041"),
                "Unexpected APDU encoding")
        require(command[5:] == bytes.fromhex(v["input_hex"]),
                "APDU/input mismatch")
        require(len(expected) == 65 and expected[0] == 4,
                "Unexpected response encoding")
        vectors.append((v["index"], command, expected))
    return vectors


def transmit(connection, command):
    start = time.perf_counter_ns()
    response, sw1, sw2 = connection.transmit(list(command))
    duration = (time.perf_counter_ns() - start) / 1_000_000
    return bytes(response), f"{sw1:02X}{sw2:02X}", duration


def replay(connection, vectors):
    aid = bytes.fromhex(AID)
    select = bytes([0, 0xA4, 4, 0, len(aid)]) + aid

    response, sw, select_ms = transmit(connection, select)
    require(sw == "9000", f"SELECT failed: {sw}")

    stage_response, sw, stage_ms = transmit(
        connection, bytes.fromhex("80710000")
    )
    require(sw == "9000", f"Stage query failed: {sw}")
    require(stage_response == b"\x0b",
            "Research applet is not at stage 11")

    results = []
    for index, command, expected in vectors:
        actual, sw, elapsed = transmit(connection, command)
        require(sw == "9000",
                f"Vector {index} status: {sw}")
        require(actual == expected,
                f"Vector {index} response mismatch; "
                f"expected_sha256={hashlib.sha256(expected).hexdigest()} "
                f"actual_sha256={hashlib.sha256(actual).hexdigest()}")
        print(f"PASS vector {index}: {elapsed:.3f} ms", flush=True)
        results.append({
            "index": index,
            "status_word": sw,
            "response_match": True,
            "response_bytes": len(actual),
            "transmit_ms": round(elapsed, 3)
        })

    times = [r["transmit_ms"] for r in results]
    return {
        "status": "PASS",
        "mode": "physical-public-vectors",
        "applet_aid": AID,
        "vectors_verified": len(results),
        "select_ms": round(select_ms, 3),
        "stage_query_ms": round(stage_ms, 3),
        "median_transmit_ms": round(statistics.median(times), 3),
        "timing_scope": "PC/SC transmit only; excludes SELECT and stage query",
        "wallet_signing": False,
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reader", required=True,
                        help="Exact PC/SC reader name")
    parser.add_argument("--confirm-test-card", action="store_true")
    parser.add_argument("--execute-public-vectors", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if not (args.confirm_test_card and args.execute_public_vectors):
        parser.error("Explicit --confirm-test-card and "
                     "--execute-public-vectors required")

    vectors = published_vectors()

    # Deliberately lazy: offline tests do not require pyscard.
    from smartcard.System import readers
    matches = [r for r in readers() if str(r) == args.reader]
    require(len(matches) == 1,
            "Reader must match exactly one connected device")

    connection = matches[0].createConnection()
    connection.connect()
    try:
        report = replay(connection, vectors)
    finally:
        connection.disconnect()

    report["reader"] = args.reader
    print(f"PASS {report['vectors_verified']}/10 physical PACE vectors")
    print(f"Median PC/SC transmit: {report['median_transmit_ms']} ms")

    if args.report:
        require(not args.report.is_symlink(),
                "Report path must not be a symbolic link")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        require(not args.report.exists(),
                "Report already exists; refusing overwrite")
        args.report.write_text(json.dumps(report, indent=2) + "\n")
        print("Report:", args.report)


if __name__ == "__main__":
    try:
        main()
    except (BenchmarkError, OSError, ValueError, ImportError) as exc:
        sys.exit("STOP: " + str(exc))
