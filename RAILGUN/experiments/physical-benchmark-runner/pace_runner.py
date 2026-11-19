#!/usr/bin/env python3
"""Replay or explicitly benchmark the research PACE-GM applet."""
import argparse
import json
import statistics
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
VECTOR_FILE = BASE / "vectors/PUBLIC-PACE-VECTORS.json"
AID = bytes.fromhex("F0424E3235343C01")

def decode(text):
    value = str(text).strip().replace(" ", "").replace(":", "")
    if value.lower().startswith("0x"):
        value = value[2:]
    return bytes.fromhex(value)

def demand(ok, why):
    if not ok:
        raise RuntimeError(why)

def fixtures():
    doc = json.loads(VECTOR_FILE.read_text())
    demand(decode(doc["applet_aid"]) == AID, "Unexpected applet AID")
    vectors = doc["vectors"]
    demand(len(vectors) == 10, "Expected 10 public vectors")
    out = []
    for v in vectors:
        a = decode(v["apdu_hex"])
        x = decode(v["expected_hex"])
        demand(
            len(a) == 70 and a[:5] == bytes.fromhex("8077000041"),
            "Invalid fixture APDU"
        )
        demand(len(x) == 65 and x[0] == 4, "Invalid expected point")
        out.append((v, a + b"\x41", x))
    return out

def check_result(label, reply, sw, expected):
    demand(sw == "9000", f"{label}: unexpected SW={sw}")
    demand(reply == expected, f"{label}: output mismatch")

def replay(path, items):
    records = [
        json.loads(x) for x in path.read_text().splitlines()
        if x.strip()
    ]
    matches = {
        r["label"]: r for r in records
        if str(r.get("label", "")).startswith("pace-")
    }
    demand(len(matches) == 10, "Expected 10 PACE trace records")
    results = []

    for i, (v, command, expected) in enumerate(items, 1):
        label = f"pace-{i:02d}"
        demand(label in matches, f"Missing {label}")
        r = matches[label]
        demand(decode(r["apdu_hex"]) == command, f"{label}: APDU mismatch")
        sw = str(r["sw"]).upper()
        check_result(label, decode(r["response_hex"]), sw, expected)
        ms = float(r["elapsed_ms"])
        demand(0 <= ms < 1000000, "Invalid elapsed time")
        print(f"PASS {label}: j={v['h_multiplier']} {ms:.3f} ms")
        results.append({
            "vector": i, "h_multiplier": v["h_multiplier"],
            "elapsed_ms": ms, "verified": True
        })
    return results

def live(reader_name, items):
    try:
        from smartcard.System import readers
    except ImportError as exc:
        raise RuntimeError("Install pyscard before live testing") from exc

    selected = [r for r in readers() if str(r) == reader_name]
    demand(len(selected) == 1, "Reader must match exactly one device")

    connection = selected[0].createConnection()
    connection.connect()

    def send(command):
        start = time.perf_counter_ns()
        response, sw1, sw2 = connection.transmit(list(command))
        ms = (time.perf_counter_ns() - start) / 1000000
        return bytes(response), f"{sw1:02X}{sw2:02X}", ms

    try:
        select = bytes([0, 0xA4, 4, 0, len(AID)]) + AID
        _, sw, _ = send(select)
        demand(sw == "9000", f"Research applet SELECT failed: {sw}")

        stage, sw, _ = send(bytes.fromhex("8071000001"))
        demand(
            sw == "9000" and stage == b"\x0b",
            f"Applet must already be at stage 11; "
            f"got {stage.hex()}, SW={sw}. No initialization attempted."
        )
        print("PASS Research applet selected; stage 11 verified")

        results = []
        for i, (v, command, expected) in enumerate(items, 1):
            label = f"pace-{i:02d}"
            response, sw, ms = send(command)
            check_result(label, response, sw, expected)
            print(f"PASS {label}: j={v['h_multiplier']} {ms:.3f} ms")
            results.append({
                "vector": i, "h_multiplier": v["h_multiplier"],
                "elapsed_ms": round(ms, 3), "verified": True
            })
        return results
    finally:
        connection.disconnect()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--replay", type=Path, metavar="TRACE_JSONL")
    mode.add_argument("--live", action="store_true")
    parser.add_argument("--reader")
    parser.add_argument(
        "--generation", choices=["JCOP3", "JCOP4", "JCOP4.5"]
    )
    parser.add_argument("--confirm-dedicated-test-card", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if args.live and not (
        args.reader and args.generation and args.confirm_dedicated_test_card
    ):
        parser.error(
            "--live requires --reader, --generation, "
            "and --confirm-dedicated-test-card"
        )

    print("◆ M3.4 — PACE BENCHMARK")
    print("Mode:", "LIVE" if args.live else "OFFLINE REPLAY")

    items = fixtures()
    results = (
        live(args.reader, items)
        if args.live else replay(args.replay, items)
    )

    times = [r["elapsed_ms"] for r in results]
    report = {
        "status": "PASS",
        "mode": "live" if args.live else "replay",
        "card_generation_label": (
            args.generation if args.live else "JCOP3 (recorded)"
        ),
        "generation_attested": False,
        "samples": len(results),
        "timing_scope": (
            "host PC/SC transmit" if args.live
            else "historical GP CLI trace"
        ),
        "median_ms": round(statistics.median(times), 3),
        "min_ms": round(min(times), 3),
        "max_ms": round(max(times), 3),
        "vectors": results,
        "no_applet_installation": True,
        "no_applet_initialization": True
    }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n")

    print(f"PASS {len(results)}/10 outputs verified")
    print(f"Median: {report['median_ms']:.3f} ms")
    print("Hardware accessed:", "YES" if args.live else "NO")
    if args.report:
        print("Evidence:", args.report)

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, KeyError) as exc:
        raise SystemExit("STOP: " + str(exc)) from None
