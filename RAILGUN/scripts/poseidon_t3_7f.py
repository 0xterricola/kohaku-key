#!/usr/bin/env python3
"""JCOP Poseidon T3 RSA-5 Barrett (7F) benchmark."""

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
FIXTURE = BASE / "vectors/poseidon-t3-rounds.json"

FIXTURE_SHA = "9055080ad906b5fe73c83aa21e01303cfcf6d1137d3ab2f435ead179283ab5fe"
CAP_SHA = "be1c0cb797624ba50235e9b26086f8f2c18b6c1e0917a8d28335634182ac71f0"

AID = bytes.fromhex("F0424E3235347F01")
NAMES = ("zero", "one-two", "three-five", "mixed", "boundary")

def verify(path, expected):
    if (
        not path.is_file()
        or path.is_symlink()
        or hashlib.sha256(path.read_bytes()).hexdigest() != expected
    ):
        raise RuntimeError("Missing or mismatched pinned artifact")
    return path

def load_fixture():
    data = json.loads(verify(FIXTURE, FIXTURE_SHA).read_text())

    assert (
        data["width"],
        data["full_rounds"],
        data["partial_rounds"]
    ) == (3, 8, 57)

    assert tuple(x["name"] for x in data["vectors"]) == NAMES

    return data

def offline_test():
    data = load_fixture()

    p = int(data["field"])
    constants = list(map(int, data["round_constants"]))
    matrix = [[int(x) for x in row] for row in data["mds"]]

    assert len(constants) == 195
    assert len(matrix) == 3

    count = 0

    for vector in data["vectors"]:
        x, y = map(int, vector["inputs"])
        state = [0, x, y]

        assert len(vector["states"]) == 65

        for r in range(65):
            state = [
                (state[i] + constants[3*r+i]) % p
                for i in range(3)
            ]

            full = r < 4 or r >= 61

            state = [
                pow(value, 5, p) if full or i == 0 else value
                for i, value in enumerate(state)
            ]

            state = [
                sum(matrix[i][j] * state[j] for j in range(3)) % p
                for i in range(3)
            ]

            expected = list(map(int, vector["states"][r]))
            assert state == expected, (vector["name"], r)

            count += 1

        assert state[0] == int(vector["expected_hash"])

    assert count == 325
    return count

def physical(args):
    # Only the local CAP file is fingerprinted.
    # This does not attest the installed card binary.
    verify(args.cap.expanduser(), CAP_SHA)
    offline_test()

    from smartcard.System import readers

    matches = [r for r in readers() if str(r) == args.reader]

    if len(matches) != 1:
        raise RuntimeError("Exact PC/SC reader match required")

    fixture = load_fixture()
    index = NAMES.index(args.vector)
    vector = fixture["vectors"][index]

    connection = matches[0].createConnection()
    started = time.perf_counter()
    connected = False

    def transmit(apdu, label):
        began = time.perf_counter()
        data, sw1, sw2 = connection.transmit(list(apdu))
        elapsed = (time.perf_counter() - began) * 1000

        if (sw1, sw2) != (0x90, 0x00):
            raise RuntimeError(
                f"{label}: SW={sw1:02X}{sw2:02X}"
            )

        return bytes(data), elapsed

    try:
        connection.connect()
        connected = True

        _, select_ms = transmit(
            bytes.fromhex("00A4040008") + AID,
            "SELECT"
        )

        _, init_ms = transmit(
            bytes([0x80, 0x7D, index, 0x00, 0x01]),
            "INIT"
        )

        timings = []

        for i, expected_state in enumerate(vector["states"]):
            response, ms = transmit(
                bytes.fromhex("807E000060"),
                f"ROUND_{i}"
            )

            expected = b"".join(
                int(value).to_bytes(32, "big")
                for value in expected_state
            )

            if response != expected:
                raise RuntimeError(
                    f"ROUND_{i}: canonical state mismatch"
                )

            timings.append(round(ms, 3))

            if (i + 1) % 10 == 0 or i == 64:
                print(
                    f"PHYSICAL_ROUNDS: {i+1}/65 PASS",
                    flush=True
                )

    finally:
        if connected:
            connection.disconnect()

    host_ms = (time.perf_counter() - started) * 1000

    result = {
        "implementation": "7F Barrett",
        "platform": args.platform,
        "package_aid": "F0424E3235347F00",
        "applet_aid": AID.hex().upper(),
        "cap_sha256": CAP_SHA,
        "vector": args.vector,
        "verified_rounds": 65,
        "canonical_final": "PASS",
        "select_ms": round(select_ms, 3),
        "init_ms": round(init_ms, 3),
        "round_transmit_ms": timings,
        "median_round_ms": round(
            statistics.median(timings), 3
        ),
        "host_elapsed_ms": round(host_ms, 3),
        "timing_scope": (
            "PCSC connect, SELECT, INIT, "
            "65 round APDUs, disconnect"
        ),
        "on_card_cap_attestation": False,
        "wallet_operations": 0,
    }

    print("CANONICAL_FINAL: PASS")
    print("PHYSICAL_ROUNDS: 65/65 PASS")
    print(f"HOST_ELAPSED_MS: {host_ms:.3f}")

    if args.output:
        path = args.output.expanduser()

        if path.exists() or path.is_symlink():
            raise RuntimeError("Refusing report overwrite")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(result, indent=2) + "\n"
        )
        print("REPORT_SAVED: PASS")

def main():
    parser = argparse.ArgumentParser(description=__doc__)

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--hardware", action="store_true")

    parser.add_argument("--vector", choices=NAMES)
    parser.add_argument("--reader")
    parser.add_argument("--cap", type=Path)
    parser.add_argument("--platform", default="experimental JCOP3")
    parser.add_argument("--confirm-test-card", action="store_true")
    parser.add_argument("--output", type=Path)

    args = parser.parse_args()

    if args.self_test:
        print(f"OFFLINE_ROUNDS: {offline_test()}/325 PASS")
        print("OFFLINE_HASHES: 5/5 PASS")
        return

    if not (
        args.confirm_test_card
        and args.reader
        and args.vector
        and args.cap
    ):
        parser.error(
            "--hardware requires --confirm-test-card, "
            "--reader, --vector and --cap"
        )

    physical(args)

if __name__ == "__main__":
    main()
