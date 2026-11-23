#!/usr/bin/env python3
"""JCOP3 Poseidon t3 RSA-5 physical benchmark.

--self-test        Verify pinned public fixtures; no card access
--vector NAME      Execute one canonical vector on physical JCOP3
--save             Save successful execution JSON/CSV under runs/
"""

import argparse
import csv
import ctypes as C
import hashlib
import json
import re
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "Developer/keycard-railgun-poseidon-fullhash"
BASE = ROOT / "research-t3-rsa-square/deferred-rsa5-dictionary-source"
FIXTURE = ROOT / "fixtures/poseidon-t3-rounds.json"

PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617
AID = bytes.fromhex("F0424E3235347E01")

NAMES = (
    "zero", "one-two", "three-five", "mixed", "boundary"
)

PINS = {
    FIXTURE:
        "9055080ad906b5fe73c83aa21e01303cfcf6d1137d3ab2f435ead179283ab5fe",
    BASE / "build/m342h4/poseidonoptrsa5dict.cap":
        "da9329e4682ffb132d092b128d283e3a50f0d461fd6a7bddda9cdaf564bfdfe6",
    BASE / (
        "src/main/java/im/status/keycard/railgun/"
        "poseidonoptrsa5dict/PoseidonT3Rsa5DictionaryApplet.java"
    ):
        "eee33a6a70ad08fce7b03f3544b1d4a2e6419d20ac57b13916d8ea7d30a3f611",
}

KNOWN_HASHES = {
    "zero":
        "7d5dc71981bb3ca593c233b3aad1ef44e4c5b6961c70700b7a4535d808a1c12b",
    "mixed":
        "ab4f182cd4611a056d1c1b335823fd166fcd2bf8c196330b5e07dbbc6502f698",
    "boundary":
        "f1fdd5d92257160f153780de5255bbe7903fdbe3377c1d5bfc6e73f3007cfc15",
}


def field_element(value):
    # Fixtures may encode canonical elements as decimal strings.
    # Reject booleans, hex, floats, negative and malformed strings.
    if type(value) is int:
        number = value
    elif isinstance(value, str) and re.fullmatch(r"[0-9]+", value):
        number = int(value, 10)
    else:
        raise ValueError(
            "Unsupported BN254 field element representation"
        )

    if not 0 <= number < PRIME:
        raise ValueError("Noncanonical BN254 field element")

    return number


def final_state(vector):
    return b"".join(
        field_element(value).to_bytes(32, "big")
        for value in vector["states"][-1]
    )


def load_vectors():
    for path, expected in PINS.items():
        if not path.is_file():
            raise RuntimeError("Missing pinned artifact: " + str(path))

        actual = hashlib.sha256(path.read_bytes()).hexdigest()

        if actual != expected:
            raise RuntimeError("Artifact SHA256 mismatch: " + str(path))

    data = json.loads(FIXTURE.read_text())

    if (
        data.get("width") != 3
        or data.get("full_rounds") != 8
        or data.get("partial_rounds") != 57
    ):
        raise RuntimeError("Unexpected Poseidon parameters")

    vectors = data["vectors"]

    if len(vectors) != 5 or tuple(
        item["name"] for item in vectors
    ) != NAMES:
        raise RuntimeError("Unexpected fixture names or order")

    string_elements = 0
    integer_elements = 0

    for vector in vectors:
        if len(vector["states"]) != 65:
            raise RuntimeError("Incorrect round-state count")

        for state in vector["states"]:
            if len(state) != 3:
                raise RuntimeError("Unexpected state width")

            for value in state:
                field_element(value)

                if isinstance(value, str):
                    string_elements += 1
                else:
                    integer_elements += 1

        if vector["name"] in KNOWN_HASHES:
            digest = hashlib.sha256(final_state(vector)).hexdigest()

            if digest != KNOWN_HASHES[vector["name"]]:
                raise RuntimeError(
                    "Known final-state mismatch: " + vector["name"]
                )

    print("PINNED_ARTIFACTS: 3/3 PASS")
    print("CANONICAL_VECTORS: 5/5 PASS")
    print("CANONICAL_STATES: 325/325 PASS")
    print("DECIMAL_STRING_ELEMENTS:", string_elements)
    print("INTEGER_ELEMENTS:", integer_elements)
    print("KNOWN_FINAL_STATE_HASHES: 3/3 PASS")

    return vectors


DWORD = C.c_uint32
HANDLE = C.c_int32
LONG = C.c_int32


class IORequest(C.Structure):
    _fields_ = [
        ("protocol", DWORD),
        ("length", DWORD),
    ]


def pcsc_check(result, operation):
    if result != 0:
        raise RuntimeError(
            "%s PCSC_ERROR=0x%08X" %
            (operation, result & 0xffffffff)
        )


def load_pcsc():
    lib = C.CDLL(
        "/System/Library/Frameworks/PCSC.framework/PCSC"
    )

    lib.SCardEstablishContext.argtypes = [
        DWORD, C.c_void_p, C.c_void_p, C.POINTER(HANDLE)
    ]
    lib.SCardEstablishContext.restype = LONG

    lib.SCardListReaders.argtypes = [
        HANDLE, C.c_char_p, C.c_void_p, C.POINTER(DWORD)
    ]
    lib.SCardListReaders.restype = LONG

    lib.SCardConnect.argtypes = [
        HANDLE, C.c_char_p, DWORD, DWORD,
        C.POINTER(HANDLE), C.POINTER(DWORD)
    ]
    lib.SCardConnect.restype = LONG

    lib.SCardTransmit.argtypes = [
        HANDLE, C.POINTER(IORequest),
        C.c_void_p, DWORD,
        C.c_void_p, C.c_void_p, C.POINTER(DWORD)
    ]
    lib.SCardTransmit.restype = LONG

    lib.SCardDisconnect.argtypes = [HANDLE, DWORD]
    lib.SCardDisconnect.restype = LONG

    lib.SCardReleaseContext.argtypes = [HANDLE]
    lib.SCardReleaseContext.restype = LONG

    return lib


def benchmark(vector, vector_index):
    lib = load_pcsc()
    context = HANDLE()
    card = HANDLE()

    context_open = False
    connected = False

    try:
        pcsc_check(
            lib.SCardEstablishContext(
                DWORD(2), None, None, C.byref(context)
            ),
            "EstablishContext"
        )
        context_open = True

        size = DWORD()

        pcsc_check(
            lib.SCardListReaders(
                context, None, None, C.byref(size)
            ),
            "ListReadersSize"
        )

        if not size.value:
            raise RuntimeError("No connected PC/SC readers")

        buffer = C.create_string_buffer(size.value)

        pcsc_check(
            lib.SCardListReaders(
                context, None, buffer, C.byref(size)
            ),
            "ListReaders"
        )

        readers = [
            item.decode("utf-8", errors="replace")
            for item in buffer.raw[:size.value].split(b"\x00")
            if item
        ]

        matches = [
            name for name in readers
            if "omnikey" in name.lower()
        ]

        if len(matches) != 1:
            raise RuntimeError(
                "Expected exactly one OMNIKEY reader"
            )

        protocol = DWORD()

        pcsc_check(
            lib.SCardConnect(
                context,
                matches[0].encode("utf-8"),
                DWORD(2),
                DWORD(3),
                C.byref(card),
                C.byref(protocol)
            ),
            "Connect"
        )
        connected = True

        if protocol.value not in (1, 2):
            raise RuntimeError("Unsupported PC/SC protocol")

        pci = IORequest(
            protocol.value, C.sizeof(IORequest)
        )

        print("READER:", matches[0], flush=True)
        print(
            "PROTOCOL:",
            "T=1" if protocol.value == 2 else "T=0",
            flush=True
        )

        def transmit(command, label):
            cmd = C.create_string_buffer(command, len(command))
            response = C.create_string_buffer(4096)
            size_out = DWORD(4096)

            started = time.perf_counter_ns()

            pcsc_check(
                lib.SCardTransmit(
                    card,
                    C.byref(pci),
                    C.cast(cmd, C.c_void_p),
                    DWORD(len(command)),
                    None,
                    C.cast(response, C.c_void_p),
                    C.byref(size_out)
                ),
                "Transmit " + label
            )

            ms = (time.perf_counter_ns() - started) / 1e6
            raw = response.raw[:size_out.value]

            if len(raw) < 2:
                raise RuntimeError(label + ": Truncated response")

            sw = int.from_bytes(raw[-2:], "big")

            if sw != 0x9000:
                raise RuntimeError(
                    "%s SW=%04X" % (label, sw)
                )

            return raw[:-2], ms

        _, select_ms = transmit(
            bytes.fromhex("00A4040008") + AID,
            "SELECT"
        )

        print("APPLET_SELECT: PASS")
        print("SELECT_MS: %.3f" % select_ms)

        _, init_ms = transmit(
            bytes([0x80, 0x7D, vector_index, 0, 1]),
            "INIT"
        )

        print("VECTOR:", vector["name"])
        print("INIT_MS: %.3f" % init_ms, flush=True)

        records = []
        last_state = None

        for i in range(65):
            state, elapsed = transmit(
                bytes.fromhex("807E000060"),
                "ROUND_%02d" % i
            )

            if len(state) != 96:
                raise RuntimeError(
                    "Unexpected response length at round %d" % i
                )

            kind = (
                "full" if i < 4 or i >= 61 else "partial"
            )

            records.append({
                "round": i,
                "round_type": kind,
                "elapsed_ms": round(elapsed, 3),
                "status_word": "9000"
            })

            last_state = state

            print(
                "ROUND=%02d TYPE=%s MS=%.3f SW=9000" %
                (i, kind.upper(), elapsed),
                flush=True
            )

        expected = final_state(vector)

        actual_sha = hashlib.sha256(last_state).hexdigest()
        expected_sha = hashlib.sha256(expected).hexdigest()

        print("ACTUAL_FINAL_SHA256:", actual_sha)
        print("EXPECTED_FINAL_SHA256:", expected_sha)

        if last_state != expected:
            raise RuntimeError(
                "Physical canonical final-state mismatch"
            )

        full = [
            r["elapsed_ms"] for r in records
            if r["round_type"] == "full"
        ]
        partial = [
            r["elapsed_ms"] for r in records
            if r["round_type"] == "partial"
        ]

        total = sum(r["elapsed_ms"] for r in records)

        print("CANONICAL_FINAL: PASS")
        print("PHYSICAL_ROUNDS: 65/65 PASS")
        print("TOTAL_ROUNDS_MS: %.3f" % total)
        print("FULL_MEDIAN_MS: %.3f" % statistics.median(full))
        print("PARTIAL_MEDIAN_MS: %.3f" % statistics.median(partial))
        print(
            "SPEEDUP_VS_HISTORICAL_T3: %.3fx" %
            (362363.0 / total)
        )

        return {
            "vector": vector["name"],
            "vector_index": vector_index,
            "applet_aid": AID.hex().upper(),
            "captured_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "final_state_sha256": actual_sha,
            "expected_state_sha256": expected_sha,
            "select_ms": round(select_ms, 3),
            "init_ms": round(init_ms, 3),
            "total_rounds_ms": round(total, 3),
            "full_median_ms": round(statistics.median(full), 3),
            "partial_median_ms": round(statistics.median(partial), 3),
            "rounds": records,
            "result": "PASS"
        }

    finally:
        if connected:
            rc = lib.SCardDisconnect(card, DWORD(0))
            print(
                "PCSC_DISCONNECT:",
                "PASS" if rc == 0 else "FAILED",
                flush=True
            )

        if context_open:
            lib.SCardReleaseContext(context)


def save_result(result):
    folder = Path(__file__).resolve().parent / "runs"
    folder.mkdir(parents=True, exist_ok=True)

    identifier = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%S%fZ"
    ) + "-" + result["vector"]

    json_path = folder / (identifier + ".json")
    csv_path = folder / (identifier + ".csv")

    with json_path.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    with csv_path.open("x", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "round", "round_type",
                "elapsed_ms", "status_word"
            ]
        )
        writer.writeheader()
        writer.writerows(result["rounds"])

    print("SAVED_JSON:", json_path)
    print("SAVED_CSV:", csv_path)


def main():
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--vector", choices=NAMES)

    parser.add_argument("--save", action="store_true")

    args = parser.parse_args()

    if args.save and not args.vector:
        parser.error("--save requires --vector")

    vectors = load_vectors()

    if args.self_test:
        print("CARD_APDUS: 0")
        print("SELF_TEST: PASS")
        return

    index = NAMES.index(args.vector)
    result = benchmark(vectors[index], index)

    if args.save:
        save_result(result)

    print("BENCHMARK: PASS")


if __name__ == "__main__":
    main()
