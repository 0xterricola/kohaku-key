#!/usr/bin/env python3
"""JCOP3 native ECC public-vector benchmark.

Only the published research applet and six fixed public
vectors are permitted. No initialization or installation.
"""
import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAILGUN = ROOT / "RAILGUN"
FIXTURE = RAILGUN / "vectors/PUBLIC-NATIVE-ECC-VECTORS.json"
SOURCE = RAILGUN / (
    "applets/native-ec/src/main/java/"
    "im/status/keycard/railgun/nativeecprobe/"
    "NativeEcProbeApplet.java"
)
CAP = RAILGUN / "applets/native-ec/nativeecprobe.cap"

FIXTURE_SHA = (
    "220459665ccc10dce832ca36163f2e084470276e0dd3146248acf23a34c4eb4a"
)
SOURCE_SHA = (
    "c51d825963ed44e5076383c5b0e598c08a31b6df1b5ac25fd03e57ca28ce8df5"
)
CAP_SHA = (
    "a1b6dd093c4fefa9642b6ad614f9613d0052dfe200276d90303d6f69b7f14763"
)
AID = bytes.fromhex("F0424E3235343701")
SELECT = bytes.fromhex("00A4040008") + AID
STAGE = bytes.fromhex("80710000")


class BenchmarkError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise BenchmarkError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_vectors():
    require(sha256(FIXTURE) == FIXTURE_SHA,
            "Published vector fixture fingerprint mismatch")
    require(sha256(SOURCE) == SOURCE_SHA,
            "Native ECC source fingerprint mismatch")
    require(sha256(CAP) == CAP_SHA,
            "Native ECC CAP fingerprint mismatch")

    data = json.loads(FIXTURE.read_text())
    require(
        data.get("schema") ==
        "kohaku-key.native-ecc.public-vectors.v1",
        "Unexpected fixture schema"
    )
    require(data.get("applet_aid") == AID.hex().upper(),
            "Applet AID mismatch")
    require(data.get("required_stage") == 11,
            "Stage requirement mismatch")
    require(data.get("instruction") == "0x75",
            "Instruction mismatch")
    require(data.get("algorithm") == "ALG_EC_SVDP_DH_PLAIN",
            "Algorithm mismatch")
    require(data.get("source_sha256") == SOURCE_SHA,
            "Fixture source hash mismatch")
    require(data.get("cap_sha256") == CAP_SHA,
            "Fixture CAP hash mismatch")

    vectors = data["vectors"]
    require(len(vectors) == 6, "Exactly six vectors required")

    commands = []
    for index, vector in enumerate(vectors):
        command = bytes.fromhex(vector["command_hex"])
        expected_command = bytes.fromhex(
            f"8075{index:02X}0000"
        )
        expected_x = bytes.fromhex(vector["expected_x_hex"])

        require(vector["index"] == index,
                "Incorrect vector ordering")
        require(command == expected_command,
                "Unexpected public APDU")
        require(len(expected_x) == 32,
                "Expected result must be 32 bytes")
        require(vector["expected_length_bytes"] == 32,
                "Output length contract mismatch")
        require(len(bytes.fromhex(vector["scalar_hex"])) == 32,
                "Public scalar length mismatch")
        require(
            int(vector["scalar_hex"], 16).bit_length()
            == vector["scalar_bits"],
            "Public scalar bit length mismatch"
        )
        commands.append((index, command, expected_x))

    return commands


def allowed_commands(vectors):
    return frozenset(
        (SELECT, STAGE, *(command for _, command, _ in vectors))
    )


def transmit(connection, command, allowed):
    require(command in allowed,
            "Blocked APDU outside public allowlist")

    start = time.perf_counter_ns()
    response, sw1, sw2 = connection.transmit(list(command))
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000

    sw = f"{sw1:02X}{sw2:02X}"
    return bytes(response), sw, elapsed_ms


def execute(connection, vectors, rounds):
    allowed = allowed_commands(vectors)

    selected, sw, select_ms = transmit(
        connection, SELECT, allowed
    )
    require(sw == "9000", f"Applet SELECT failed: {sw}")

    stage, sw, stage_ms = transmit(
        connection, STAGE, allowed
    )
    require(sw == "9000", f"Stage query failed: {sw}")
    require(stage == b"\x0b",
            f"Applet must already be at stage 11; got {stage.hex()}")

    samples = []
    for round_index in range(rounds):
        for index, command, expected in vectors:
            actual, sw, elapsed_ms = transmit(
                connection, command, allowed
            )
            require(
                sw == "9000",
                f"Round {round_index}, vector {index}: SW={sw}"
            )
            require(
                actual == expected,
                f"Round {round_index}, vector {index}: "
                "cryptographic response mismatch"
            )
            samples.append({
                "round": round_index,
                "index": index,
                "scalar_bits": int.from_bytes(
                    bytes.fromhex(
                        json.loads(FIXTURE.read_text())
                        ["vectors"][index]["scalar_hex"]
                    ), "big"
                ).bit_length(),
                "transmit_ms": round(elapsed_ms, 6),
            })

    timings = [item["transmit_ms"] for item in samples]
    per_vector = {}

    for index, _, _ in vectors:
        values = [
            item["transmit_ms"] for item in samples
            if item["index"] == index
        ]
        per_vector[str(index)] = {
            "count": len(values),
            "median_ms": statistics.median(values),
            "minimum_ms": min(values),
            "maximum_ms": max(values),
        }

    return {
        "operation": "ALG_EC_SVDP_DH_PLAIN",
        "instruction": "0x75",
        "applet_aid": AID.hex().upper(),
        "fixture_sha256": FIXTURE_SHA,
        "source_sha256": SOURCE_SHA,
        "cap_sha256": CAP_SHA,
        "timing_scope": "single host PC/SC transmit call",
        "select_ms": select_ms,
        "stage_query_ms": stage_ms,
        "stage_verified": 11,
        "generation_attested": False,
        "rounds": rounds,
        "verified": len(samples),
        "median_ms": statistics.median(timings),
        "minimum_ms": min(timings),
        "maximum_ms": max(timings),
        "per_vector": per_vector,
        "samples": samples,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reader")
    parser.add_argument("--rounds", type=int, default=10)
    parser.add_argument("--confirm-test-card", action="store_true")
    parser.add_argument("--execute-public-vectors",
                        action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    require(1 <= args.rounds <= 30,
            "Rounds must be between 1 and 30")

    vectors = load_vectors()
    print("PASS: Six pinned native ECC public vectors")
    print("PASS: Original source and CAP fingerprints")
    print("PASS: Explicit SELECT/stage/vector allowlist")
    print("Applet:", AID.hex().upper())

    if not args.execute_public_vectors:
        require(not args.report,
                "--report requires physical execution")
        print("OFFLINE VALIDATION ONLY — no PC/SC access")
        return

    require(args.confirm_test_card,
            "Explicit --confirm-test-card required")
    require(bool(args.reader),
            "Explicit --reader required")

    if args.report:
        require(not args.report.exists(),
                "Refusing to overwrite existing report")

    from smartcard.System import readers

    available = list(readers())
    matches = [r for r in available if str(r) == args.reader]
    require(len(matches) == 1,
            "Reader must match exactly one attached reader")

    connection = matches[0].createConnection()
    connection.connect()

    try:
        result = execute(connection, vectors, args.rounds)
    finally:
        connection.disconnect()

    result["reader"] = args.reader
    print("PASS:", result["verified"], "verified physical APDUs")
    print("Median PC/SC transmit:", result["median_ms"], "ms")
    print("Minimum:", result["minimum_ms"], "ms")
    print("Maximum:", result["maximum_ms"], "ms")

    for index, values in result["per_vector"].items():
        print(
            f"Vector {index}: median "
            f"{values['median_ms']:.3f} ms"
        )

    if args.report:
        args.report.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8"
        )
        print("Report:", args.report)


if __name__ == "__main__":
    try:
        main()
    except (BenchmarkError, OSError, ValueError,
            ImportError, KeyError) as exc:
        print("STOP:", exc, file=sys.stderr)
        sys.exit(1)
