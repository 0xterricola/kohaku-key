#!/usr/bin/env python3
"""Offline developer preflight. No smart-card access."""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAILGUN = ROOT / "RAILGUN"

VARIANT = (
    RAILGUN
    / "experiments/physical-benchmark-runner"
    / "applets/pace-gm-k1"
)

REQUIRED = (
    RAILGUN / "vectors/PUBLIC-PACE-VECTORS.json",
    RAILGUN / "scripts/benchmark.py",
    RAILGUN / "scripts/physical_pace.py",
    RAILGUN / "tests/test_physical_pace.py",
    VARIANT / "build.xml",
    VARIANT / "build-offline.sh",
    VARIANT / "pace-gm-k1.cap",
)

def main():
    print("RAILGUN developer preflight")
    print("OFFLINE | NO PC/SC | NO APDUs")

    failures = []

    print()
    print("Required research files")

    for path in REQUIRED:
        present = path.is_file()
        print(
            "PASS" if present else "FAIL",
            path.relative_to(ROOT)
        )
        if not present:
            failures.append(str(path))

    print()
    print("Host tools")

    for name in ("python3", "java", "javac", "ant"):
        found = shutil.which(name)
        print("PASS" if found else "MISSING", name)
        if name == "python3" and not found:
            failures.append(name)

    print()
    print("Optional build dependencies")

    for name, kind in (
        ("ANT_JAVACARD_JAR", "file"),
        ("KEYCARD_JC_SDK", "directory"),
        ("KEYCARD_MATH_HOME", "math"),
    ):
        value = os.environ.get(name)

        if not value:
            print("UNSET", name)
            continue

        path = Path(value).expanduser()

        if kind == "file":
            valid = path.is_file()
        elif kind == "math":
            valid = (path / "keycard-math.jar").is_file()
        else:
            valid = path.is_dir()

        print("PASS" if valid else "INVALID", name)

    print()
    print("Physical card access: DISABLED")

    if failures:
        raise SystemExit("STOP: Offline preflight failed")

    print("PASS: Offline developer preflight")

if __name__ == "__main__":
    main()
