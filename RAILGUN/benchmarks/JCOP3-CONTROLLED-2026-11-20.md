# JCOP3 controlled native ECC and PACE-GM replay

Date: 2026-11-20

## Scope

Physical research-applet replay using public cryptographic
vectors on the designated experimental JCOP3 Keycard.

Both operations used the same HID OMNIKEY PC/SC reader.
The runner did not independently attest the chip generation.

## Hardware and methodology

- Reader: HID Global OMNIKEY 3x21 Smart Card Reader
- Card: operator-designated experimental JCOP3 Keycard
- Timing: one host-observed PC/SC `connection.transmit()` call
- SELECT and initialization-stage queries excluded
- No applet installation, deletion, or initialization
- No PIN, wallet signing, or private-key access
- Research-applet public scalar state may change
- Every measured operation verified against expected output

## Verified physical results

| Operation | Applet AID | Verified | Median latency |
| --- | --- | ---: | ---: |
| Native ECC `0x75` | F0424E3235343701 | 60/60 | 203.890 ms |
| PACE-GM `0x77` | F0424E3235343C01 | 10/10 | 221.596 ms |

These are distinct cryptographic operations. Their median
latencies must not be used to calculate an ECC-versus-PACE
hardware speedup.

## Native ECC details

- Algorithm: `ALG_EC_SVDP_DH_PLAIN`
- Six fixed public scalars
- Ten rounds per scalar
- Minimum: 196.948 ms
- Maximum: 215.201 ms
- Verified outputs: 60/60

| Scalar selector | Verified | Median transmit |
| --- | ---: | ---: |
| 0 | 10/10 | 203.662 ms |
| 1 | 10/10 | 203.784 ms |
| 2 | 10/10 | 205.220 ms |
| 3 | 10/10 | 203.887 ms |
| 4 | 10/10 | 206.299 ms |
| 5 | 10/10 | 203.720 ms |

The native ECC runner validates expected 32-byte
X-coordinates derived independently from the published
short-Weierstrass curve parameters.

## PACE-GM details

- Published PACE-GM research applet
- Ten public point-addition vectors
- Verified outputs: 10/10
- Median transmit: 221.596 ms
- Earlier JCOP3 transmit replay: 222.923 ms

The current PACE-GM median differs from that earlier
replay by 1.327 ms.

## Original evidence

The original machine-readable reports remain outside
the repository under the operator's local benchmark
directory.

- Native ECC report: `native-ecc-jcop3-10-rounds.json`
  - SHA-256: `31e3c6f0b5ea47d2344db435e4b4700a495be37dd146a10cb03489f7a08f762e`
  - Contains 60 individual timing samples
- PACE-GM report: `pace-gm-jcop3-controlled-replay.json`
  - SHA-256: `177d18d5ebb2be2cc212c4a9a7c0afdea8f120054bc8ec286961b2a6ca3496d3`
  - Contains ten verified vector results

These hashes identify the original local evidence files.
This document does not reconstruct missing samples.

## JCOP4 comparison boundary

Mikkoph independently reported approximately
85.6–85.9 ms native ECDH latency and 150.046 ms
PACE-GM latency on JCOP4.

The tested configurations differ in reader, host,
provider behavior, and potentially applet implementation.

An isolated chip-generation speedup has therefore
not been established.

Four independently supplied JCOP4 JSON reports have since been
[imported and SHA-256-pinned](jcop4-2026-11-19/README.md).
Our separately built JCOP4 `4E01` K=1 applet remains physically
unverified; Mikkoph's successful physical result used `4D01`.

See [JCOP3 vs. JCOP4](JCOP3-VS-JCOP4.md) and
[JCOP4 independent results](JCOP4-2026-11-19.md).

## Reproducibility

- [Native ECC runner](../scripts/physical_native_ecc.py)
- [Native ECC public vectors](../vectors/PUBLIC-NATIVE-ECC-VECTORS.json)
- [Physical PACE runner](../scripts/physical_pace.py)
- [Hardware safety](../HARDWARE-SAFETY.md)
