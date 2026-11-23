#!/usr/bin/env python3
"""Portable entry point for the pinned physical 7E runner."""
import argparse
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys

RAILGUN = Path(__file__).resolve().parents[1]
LEGACY = RAILGUN / "scripts/poseidon_t3_7e_legacy.py"
FIXTURE = RAILGUN / "vectors/poseidon-t3-rounds.json"
LEGACY_SHA = "2e89eaf498f1a2516996a8c3a097684a86ea85469de520e0bf1312665d8d1c7b"
FIXTURE_SHA = "9055080ad906b5fe73c83aa21e01303cfcf6d1137d3ab2f435ead179283ab5fe"
CAP_SHA = "da9329e4682ffb132d092b128d283e3a50f0d461fd6a7bddda9cdaf564bfdfe6"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verified(path, expected):
    if not path.is_file() or digest(path) != expected:
        raise SystemExit("Artifact missing or SHA-256 mismatch")
    return path

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--hardware", action="store_true")
    parser.add_argument("--vector", choices=(
        "zero", "one-two", "three-five", "mixed", "boundary"
    ))
    parser.add_argument("--cap", type=Path)
    parser.add_argument(
        "--artifact", action="append", default=[],
        metavar="SHA256=PATH",
        help="Supply another pinned legacy dependency"
    )
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    verified(LEGACY, LEGACY_SHA)
    verified(FIXTURE, FIXTURE_SHA)

    if args.self_test:
        if args.vector or args.cap or args.artifact or args.save:
            parser.error("Hardware arguments require --hardware")
        raise SystemExit(subprocess.call([
            sys.executable, "-B", "-m", "unittest", "discover",
            "-s", str(RAILGUN / "tests"),
            "-p", "test_poseidon_t3_7e.py", "-v"
        ]))

    if not args.vector or not args.cap:
        parser.error("--hardware requires --vector and --cap")

    cap = verified(args.cap.expanduser(), CAP_SHA)

    spec = importlib.util.spec_from_file_location(
        "poseidon_7e_original", LEGACY
    )
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)

    overrides = {FIXTURE_SHA: FIXTURE, CAP_SHA: cap}

    for item in args.artifact:
        fingerprint, separator, filename = item.partition("=")
        if not separator or len(fingerprint) != 64:
            parser.error("Expected SHA256=PATH")
        overrides[fingerprint.lower()] = verified(
            Path(filename).expanduser(), fingerprint.lower()
        )

    original_hashes = set(module.PINS.values())
    if FIXTURE_SHA not in original_hashes or CAP_SHA not in original_hashes:
        raise SystemExit("Unexpected legacy dependency contract")

    pins = {}
    for old_path, fingerprint in module.PINS.items():
        path = overrides.get(fingerprint, old_path)
        if not Path(path).is_file():
            raise SystemExit(
                "Missing dependency with SHA256: " + fingerprint
            )
        verified(Path(path), fingerprint)
        pins[Path(path)] = fingerprint

    module.FIXTURE = FIXTURE
    module.PINS = pins

    # The historical runner's PC/SC execution remains unchanged.
    previous = sys.argv
    sys.argv = [str(LEGACY), "--vector", args.vector]
    if args.save:
        sys.argv.append("--save")
    try:
        module.main()
    finally:
        sys.argv = previous

if __name__ == "__main__":
    main()
