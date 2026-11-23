# JCOP3 Poseidon t3 — RSA-5 dictionary experiment

**Date:** 2026-11-21  
**Milestones:** M3.42g.3d, M3.42h.4, M3.42i.2, M3.42i.3a, M3.42i.4  
**Status:** Physical execution verified, 5/5 canonical final states PASS

## Objective

Accelerate BN254 Poseidon t3 on NXP JCOP3 by using the native RSA
engine for exponent-5 S-box computation and exponent-2 arithmetic
for matrix multiplication, while reducing applet installation size.

This experiment measures public-input Poseidon hashing. It does not
demonstrate hardware-isolated RAILGUN spending-key signing.

## Hardware and transport

- Card: Main JCOP3 experimental Keycard
- Reader: HID Global OMNIKEY 3x21 Smart Card Reader
- Protocol: PC/SC T=1
- Host: macOS, native PCSC.framework via Python ctypes
- Target applet AID: `F0424E3235347E01`
- Package AID: `F0424E3235347E00`
- CAP component bytes: **16,409**
- CAP SHA-256: `da9329e4682ffb132d092b128d283e3a50f0d461fd6a7bddda9cdaf564bfdfe6`

## Arithmetic design

The RSA-5 engine uses a 736-bit composite modulus:

`N = p * (2^482 + 1)`

where `p` is the BN254 scalar-field prime. Reduction of the RSA
result modulo `p` yields the required field exponentiation.

The S-box path uses RSA exponent 5; matrix multiplication continues
to use exponent 2. The simulator design reduced S-box RSA invocations
from 324 to 81 per full hash. Physical execution verified RSA
exponent switching and the custom modulus for the tested vectors.

Sparse coefficient arrays are deduplicated into dictionary values
and one-byte indices. The applet indexes the dictionary directly,
without materializing an expanded coefficient table in transient RAM.

## Applet progression

| Variant | Package / applet suffix | CAP component bytes | Evidence |
|---|---|---:|---|
| Two-square matrix | `7B00 / 7B01` | 17,331 | Simulator |
| Two-square S-box | `7C00 / 7C01` | 17,116 | Simulator |
| Single-key RSA-5 S-box | `7D00 / 7D01` | 17,778 | Simulator, 1.220x vs 7C |
| RSA-5 sparse dictionary | `7E00 / 7E01` | **16,409** | Simulator and physical JCOP3 |

7E saves 1,369 CAP component bytes relative to 7D. The interleaved
jCardSim comparison measured a 1.001x ratio between 7D and 7E.

## Installation history

M3.42i.2 deleted only obsolete research package
`F0424E3235347700` and its applet `F0424E3235347701`.

Then 7E was installed successfully. The final registry contained
31 entries. All 29 other registry entries, including the existing
t3 benchmark applet (`F0424E3235347801`), wallet applets and
security domain, were preserved.

No PIN operations, key exports or wallet modification occurred.

## Physical APDU protocol

- SELECT: `00A4040008F0424E3235347E01`
- Initialize vector: `80 7D <index> 00 01`
- Execute next round: `807E000060`
- 65 round commands per vector
- Round response: 96-byte state followed by SW `9000`
- Full rounds: 0–3, 61–64
- Partial rounds: 4–60

Indices tested: zero=0, one-two=1, three-five=2, mixed=3, boundary=4.

Round timings are host-side `perf_counter_ns()` elapsed times
around PC/SC transmissions, so they include communication overhead.

## Evidence files

- [RESULTS.md](RESULTS.md): correctness and performance summary
- [round-times.csv](round-times.csv): all 325 individual round timings
- [artifacts.json](artifacts.json): structured measurements, AIDs,
  SHA-256 fingerprints and provenance

The first 195 timing values were transcribed from the displayed terminal
results of M3.42i.3a and M3.42i.4, not recovered from raw PC/SC
traces. The runner was generated ephemerally during testing.

## Source provenance

- Candidate: `~/Developer/keycard-railgun-poseidon-fullhash/research-t3-rsa-square/deferred-rsa5-dictionary-source`
- Fixture: `~/Developer/keycard-railgun-poseidon-fullhash/fixtures/poseidon-t3-rounds.json`
- Source and CAP fingerprints: `artifacts.json`

## Limitations

Physical results cover five canonical public vectors with one complete
execution per vector. The historical t3 baseline was measured separately,
not in an interleaved controlled benchmark. This is not a private-key
signing benchmark, nor evidence of production-ready RAILGUN integration.


## Reproducing the physical benchmark

The native macOS PC/SC runner is
[`physical_poseidon_t3.py`](physical_poseidon_t3.py).

Offline verification (no card access):

`python3 physical_poseidon_t3.py --self-test`

Execute and archive one public hardware vector:

`python3 physical_poseidon_t3.py --vector one-two --save`

Supported vectors: `zero`, `one-two`, `three-five`, `mixed`,
and `boundary`.

Hardware execution occurs only with `--vector`. Successful
measurements can be saved under `runs/` as JSON and CSV.
Each invocation executes one 65-round hash and verifies
the full canonical final state.

The runner sends only research applet SELECT, public-vector
initialization and Poseidon round APDUs. It contains no
installation, deletion, wallet or PIN operations.


## Completed five-vector hardware validation — M3.42i.7

**All 5/5 canonical vectors and 325/325 physical rounds PASS.**

The previously archived zero, mixed and boundary vectors were
supplemented by one-two and three-five using the preserved
`physical_poseidon_t3.py` runner. All five final 96-byte states
matched the pinned canonical fixtures.

Mean physical execution time: **230.520 seconds**.
Historical-to-current ratio: **1.572×**.

The master [`round-times.csv`](round-times.csv) now contains
all 325 measurements. The two new executions also have
independent JSON and CSV records in [`runs/`](runs/).

See [`RESULTS.md`](RESULTS.md) for the complete hardware timing
table, hashes, and source provenance.
