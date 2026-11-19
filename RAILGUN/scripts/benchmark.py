#!/usr/bin/env python3
"""Offline integrity and BabyJubJub fixture validation. No card I/O."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
RAILGUN = ROOT / "RAILGUN"
P = 21888242871839275222246405745257275088548364400416034343698204186575808495617
A, D = 168700, 168696

CAPS = {
    "applets/native-ec/nativeecprobe.cap":
        "a1b6dd093c4fefa9642b6ad614f9613d0052dfe200276d90303d6f69b7f14763",
    "applets/pace-gm/pace-gm.cap":
        "12083cee1614ad080a24c5af7c3e9b1cdf1aeaedfb67a5fcff22cf97fb4353d8",
}

def require(condition, message):
    if not condition:
        raise SystemExit("STOP: " + message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def integer(value):
    if isinstance(value, int):
        return value
    s = str(value).strip()
    return int(s, 16 if s.lower().startswith("0x") or
               any(c in "abcdefABCDEF" for c in s) else 10)

def hex_bytes(value):
    s = str(value).removeprefix("0x").removeprefix("0X")
    return bytes.fromhex(s)

def on_curve(x, y):
    if not (0 <= x < P and 0 <= y < P):
        return False
    xx, yy = x*x % P, y*y % P
    return (A*xx + yy - 1 - D*xx*yy) % P == 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    print("◆ RAILGUN — OFFLINE BENCHMARK VALIDATION")
    print("No card access | No APDUs | No installation")

    manifest = RAILGUN / "SHA256SUMS"
    entries = manifest.read_text().splitlines()
    require(len(entries) >= 5, "Incomplete checksum manifest")

    for entry in entries:
        parts = entry.split(None, 1)
        require(len(parts) == 2, "Malformed SHA256SUMS entry")
        expected, name = parts
        target = ROOT / name.removeprefix("*")
        require(target.is_file(), f"Missing artifact: {name}")
        require(digest(target) == expected,
                f"Checksum mismatch: {name}")

    print(f"PASS {len(entries)} artifact checksums")

    for name, expected in CAPS.items():
        cap = RAILGUN / name
        require(digest(cap) == expected, f"Original CAP changed: {name}")
        with ZipFile(cap) as archive:
            components = [
                n for n in archive.namelist()
                if n.endswith(".cap")
            ]
        require(len(components) == 11,
                f"Unexpected CAP components: {name}")
        print(f"PASS {name}: 11 CAP components")

    fixture = json.loads(
        (RAILGUN / "vectors/PUBLIC-PACE-VECTORS.json").read_text()
    )
    require(integer(fixture["field_modulus"]) == P,
            "Unexpected BabyJubJub field modulus")

    require(fixture["applet_aid"].upper() ==
            "F0424E3235343C01",
            "Unexpected PACE applet AID")
    require(str(fixture["instruction"]).lower() == "0x77",
            "Unexpected PACE instruction")
    require(fixture["expected_encoding"] ==
            "uncompressed ANSI X9.62",
            "Unexpected point encoding metadata")

    vectors = fixture["vectors"]
    require(len(vectors) == 10, "Expected 10 PACE vectors")

    seen = set()
    for v in vectors:
        index = v["index"]
        require(index not in seen, f"Duplicate index: {index}")
        seen.add(index)

        for key in ("input_hex", "expected_hex", "apdu_hex"):
            raw = hex_bytes(v[key])
            require(bool(raw), f"Empty {key}: {index}")

        # Published PACE-GM command:
        # 80 77 00 00 41 || 65-byte X9.62 input point.
        # The X9.62 coordinates are Weierstrass coordinates,
        # not the Edwards coordinates recorded separately.
        for key in ("input_hex", "expected_hex"):
            encoded = hex_bytes(v[key])
            require(len(encoded) == 65 and encoded[0] == 4,
                    f"Invalid {key} point encoding: {index}")

        command = hex_bytes(v["apdu_hex"])
        require(len(command) == 70,
                f"Invalid APDU length: {index}")
        require(command[:4] == bytes.fromhex("80770000"),
                f"Unexpected APDU header: {index}")
        require(command[4] == 65,
                f"Invalid APDU Lc: {index}")
        require(command[5:] == hex_bytes(v["input_hex"]),
                f"APDU input mismatch: {index}")

        for prefix in ("input_edwards", "expected_edwards"):
            x = int(str(v[prefix + "_x"]), 16)
            y = int(str(v[prefix + "_y"]), 16)
            require(on_curve(x, y),
                    f"Off-curve {prefix} point: {index}")

    print("PASS 10/10 public PACE vectors structurally valid")
    print("PASS 20/20 Edwards points on BabyJubJub curve")

    def point(v, prefix):
        return tuple(
            int(str(v[f"{prefix}_{axis}"]), 16)
            for axis in ("x", "y")
        )

    def add(u, v):
        x1, y1 = u
        x2, y2 = v
        t = x1 * x2 * y1 * y2 % P
        x = (x1*y2 + y1*x2) * pow((1+D*t) % P, -1, P) % P
        y = (y1*y2 - A*x1*x2) * pow((1-D*t) % P, -1, P) % P
        return x, y

    def multiply(q, n):
        require(n >= 0, "Negative scalar")
        result = (0, 1)
        while n:
            if n & 1:
                result = add(result, q)
            q = add(q, q)
            n >>= 1
        return result

    # Validate scalar metadata before locating the base point.
    # Otherwise an invalid multiplier can be misreported as a
    # missing base-point vector.
    for v in vectors:
        require(integer(v["h_multiplier"]) > 0,
                "Invalid H multiplier")

    base = next(
        (point(v, "input_edwards") for v in vectors
         if integer(v["h_multiplier"]) == 1),
        None,
    )
    require(base is not None, "Missing base-point vector")

    for v in vectors:
        j = integer(v["h_multiplier"])
        s = integer(v["scalar_s"])
        require(j > 0, "Invalid H multiplier")
        h = point(v, "input_edwards")
        expected = point(v, "expected_edwards")
        require(multiply(base, j) == h, f"Invalid H = {j}B")
        require(add(h, multiply(base, s)) == expected,
                f"PACE H + sB mismatch: j={j}, s={s}")

    print(f"PASS {len(vectors)}/10 PACE group-law equations")

    report = {
        "status": "PASS",
        "mode": "offline",
        "artifact_checksums_verified": len(entries),
        "verified_caps": len(CAPS),
        "pace_vectors": len(vectors),
        "edwards_points_checked": len(vectors) * 2,
        "physical_execution": False,
        "pace_operation_recomputed": True,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")

    print("PASS Offline validation complete")
    print("Physical execution: NOT IMPLEMENTED")

if __name__ == "__main__":
    main()
