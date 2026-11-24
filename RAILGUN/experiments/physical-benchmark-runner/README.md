# Physical JavaCard benchmark runner

**Current status:** offline vector validation, SELECT-only hardware
preflight, and opt-in PACE-GM physical vector replay are implemented.
An opt-in native ECC physical runner also exists. Historical milestones
below describe the progression from preflight to physical testing.
See [developer setup](../../DEVELOPER-SETUP.md) and
[hardware safety](../../HARDWARE-SAFETY.md).

## Requirements

A dedicated test card with an already-installed compatible research
applet, a PC/SC reader, Python 3, and pyscard.

JCOP3 binaries are supplied for research comparison, but compatibility
with JCOP4 and JCOP4.5 has not been established.

## Setup

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install pyscard
python3 -B RAILGUN/scripts/benchmark.py
python3 -B RAILGUN/scripts/hardware_preflight.py --list-readers
```

To check an already-installed experimental applet:

```sh
python3 -B RAILGUN/scripts/hardware_preflight.py \
  --reader "EXACT PCSC READER NAME" \
  --applet pace-gm \
  --select-only --confirm-test-card
```

Choose `native-ec` to check the other experimental applet.

The command sends only an ISO 7816 SELECT-by-AID APDU.
It never installs or deletes an applet, authenticates a wallet,
requests a PIN, or executes cryptographic benchmark APDUs.

A missing applet may return `6A82`. SELECT success proves only
that the AID is selectable, not hardware/algorithm compatibility.

## Benchmark availability

The opt-in physical PACE-GM runner (`RAILGUN/scripts/physical_pace.py`)
and native ECC runner (`RAILGUN/scripts/physical_native_ecc.py`)
are implemented. The former was used for verified JCOP3 PACE-GM
replay; independently supplied JCOP4 results are archived in
[the JCOP4 evidence index](../../benchmarks/jcop4-2026-11-19/README.md).

The local `4E01` K=1 variant still lacks physical validation.
Keep installation instructions separate from benchmark execution.
Do not install experimental applets on cards holding valuable keys;
SELECT success alone is not proof of cryptographic compatibility.

## Published PACE-GM APDU contract

Experimental applet AID: `F0424E3235343C01`.

Instruction `0x77` requires initialization stage 11.

Command: `80 77 00 00 41` followed by a 65-byte
uncompressed ANSI X9.62 point.

The command is exactly 70 bytes:

- CLA: 80
- INS: 77
- P1/P2: 00/00
- Lc: 41 (65 bytes)
- Data: 04 || X (32 bytes) || Y (32 bytes)

The experimental applet computes H + sG using a fixed
public scalar s=1 and a host-supplied public point H.

X9.62 Weierstrass coordinates must not be confused with
the separate BabyJubJub Edwards coordinates in the fixture.

The published expected response is a 65-byte
uncompressed point.

## Offline adversarial verification

Run from the repository root:

    python3 -B RAILGUN/scripts/benchmark.py
    python3 -B -m unittest discover -s RAILGUN/tests -p 'test_*.py' -v

The tests cover artifact integrity, public curve points,
group-law equations, APDU header and length validation,
point encodings, duplicate indices, invalid multipliers,
and mismatched public payloads.

Negative tests mutate temporary copies of public artifacts.
They never transmit malformed APDUs to physical hardware.

The offline verifier does not perform physical cryptographic
execution. The separate hardware preflight tool supports only reader
discovery and explicitly authorized applet SELECT.

Physical APDU replay and response comparison were subsequently
implemented as described in the M3.6b section below. Independent
JCOP4 `4D01` results are archived; local `4E01` physical testing
remains pending.

No wallet keys, installation, or reprovisioning are required.

## M3.6b physical benchmark runner

An opt-in Python runner now replays all 10 published
PACE-GM vectors against an already-installed research
applet on a dedicated test card.

### Prerequisites

- Compatible experimental JCOP3 card
- Research applet AID F0424E3235343C01 installed
- Research initialization stage 11
- PC/SC reader and Python with pyscard
- Published artifact integrity checks passing

Use a Python environment with pyscard installed.

### Offline verification

    python3 -B RAILGUN/scripts/benchmark.py
    python3 -B -m unittest discover -s RAILGUN/tests -p 'test_*.py' -v

These checks require no connected smart card.

### Physical execution

From the repository root, on a dedicated test card:

```sh
python3 -B RAILGUN/scripts/physical_pace.py \
  --reader "EXACT PCSC READER NAME" \
  --confirm-test-card \
  --execute-public-vectors \
  --report pace-results.json
```

This command explicitly authorizes 10 public PACE APDUs.

The runner performs SELECT, verifies stage 11, then
transmits all 10 published vectors.

It requires SW 9000 and byte-for-byte matching responses.
Execution stops on the first mismatch.

The JSON report records individual PC/SC transmit latency,
SELECT latency, stage-query latency, and median latency.

Reports are not overwritten automatically.

The runner does not install applets, initialize the card,
provision credentials, or perform wallet signing.

### Security and measurement boundaries

The benchmark uses the research applet's fixed public
scalar s=1. It does not establish secret-scalar isolation
for RAILGUN signing.

Latency covers individual PC/SC transmit calls, excluding
SELECT, stage query, CLI startup and reader discovery.

Mock transport tests verify success, stage rejection,
incorrect response rejection, and non-success status
handling without a physical card.

The original published `3C01` applet's XY and PACE-GM paths failed
on Mikkoph's JCOP4 setup with `6F02`; his separate K=1 `4D01`
variant passed 50/50 PACE-GM samples. Our `4E01` remains untested
on JCOP4, and JCOP4.5 compatibility remains unverified.

## M3.7 offline trace reconciliation

The offline trace reconciler verifies previously recorded physical
PACE-GM APDUs against the published public vector fixture.

From the repository root:

    python3 -B RAILGUN/scripts/reconcile_trace.py --trace PATH_TO_APDU_JSONL

The input is a JSONL file or a directory containing `apdu.jsonl`.
Each public PACE record must have a label `pace-01` through
`pace-10`, plus `apdu_hex`, `response_hex`, `sw`, and `elapsed_ms`.

All ten commands must match the published APDUs exactly. Every
status word must equal `9000`, and every response must match
its expected 65-byte public point. Duplicate or missing PACE
records, malformed timings, and mismatches cause failure.

The tool does not access a smart card. It only validates
previously captured evidence. Recorded timing is not a fresh
hardware measurement.

Run regression tests with:

    python3 -B -m unittest discover -s RAILGUN/tests -p 'test_*.py' -v

The M3.6b physical runner remains the authoritative tool for
new PC/SC measurements. Its JSON summary is not the JSONL
trace format required by this reconciler.
