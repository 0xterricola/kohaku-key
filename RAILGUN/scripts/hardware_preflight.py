#!/usr/bin/env python3
"""PC/SC research applet discovery. No installation or benchmark APDUs."""

import argparse
import json
import sys
import time
from pathlib import Path

AIDS = {
    "native-ec": "F0424E3235343701",
    "pace-gm": "F0424E3235343C01",
}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list-readers", action="store_true")
    p.add_argument("--reader", help="Exact PC/SC reader name")
    p.add_argument("--applet", choices=sorted(AIDS))
    p.add_argument("--select-only", action="store_true")
    p.add_argument("--confirm-test-card", action="store_true")
    p.add_argument("--report", type=Path)
    args = p.parse_args()

    if args.select_only and not (
        args.reader and args.applet and args.confirm_test_card
    ):
        p.error("SELECT requires --reader, --applet and --confirm-test-card")

    try:
        from smartcard.System import readers
    except ImportError:
        sys.exit("Install pyscard in a virtual environment first.")

    found = list(readers())

    if not args.select_only:
        print("PC/SC readers:")
        for r in found:
            print(" ", str(r))
        if not found:
            print("  None detected")
        return

    matching = [r for r in found if str(r) == args.reader]
    if len(matching) != 1:
        sys.exit("STOP: Reader must match exactly one connected device.")

    aid = bytes.fromhex(AIDS[args.applet])
    command = bytes([0x00, 0xA4, 0x04, 0x00, len(aid)]) + aid

    print("Mode: SELECT only; no installation or signing")
    print("Applet:", args.applet)
    print("Reader:", args.reader)

    connection = matching[0].createConnection()
    connection.connect()
    try:
        start = time.perf_counter()
        response, sw1, sw2 = connection.transmit(list(command))
        elapsed = (time.perf_counter() - start) * 1000
    finally:
        connection.disconnect()

    sw = f"{sw1:02X}{sw2:02X}"
    result = {
        "mode": "select-only",
        "applet": args.applet,
        "reader": args.reader,
        "status_word": sw,
        "response_length": len(response),
        "select_elapsed_ms": round(elapsed, 3),
        "benchmark_executed": False,
    }

    print(json.dumps(result, indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")

    if sw != "9000":
        sys.exit("STOP: Applet SELECT did not succeed.")

if __name__ == "__main__":
    main()
