# JCOP3 vs. JCOP4 — RAILGUN hardware research

## Scope

Comparison of experimentally observed JavaCard cryptographic
operations for the Kohaku Key and RAILGUN research effort.

This report distinguishes directly comparable measurements
from measurements that differ in operation or methodology.

## Hardware

| Attribute | JCOP3 | JCOP4 |
| --- | --- | --- |
| Platform | Experimental Keycard 4.x on JCOP3 | NXP JCOP4 research card |
| Reader | HID OMNIKEY PC/SC | ACS ACR39U |
| Applet | Published PACE-GM | Experimental K=1 PACE-GM |
| PACE-GM implementation | Published 3C01 | Mikkoph's 4D00 variant |
| Timing basis | PC/SC transmit | PC/SC transmit |

Different readers and host environments limit attribution
of the observed difference solely to the chip generation.

## Direct comparison: PACE-GM

| Metric | JCOP3 | JCOP4 |
| --- | ---: | ---: |
| Median latency | 222.923 ms | 150.046 ms |
| Verified published vectors | 10/10 | 50/50 |
| Measurement convention | PC/SC transmit | PC/SC transmit |

Calculated from the reported medians:

- Latency reduction: 32.69%
- Relative speedup: 1.486x
- Absolute median difference: 72.877 ms

The JCOP4 median is approximately 32.7% lower.

Both measurements use host-observed PC/SC transmit timing.
The result is a comparison of the tested configurations,
not a controlled isolation of silicon performance.

The JCOP4 experiment used `key.setK((short)1)`, required
by the tested provider's PACE-GM path. The underlying
curve's mathematical cofactor remains 8.

## Results that must not be compared directly

### JCOP3 warm-session PACE-GM

The historical JCOP3 warm-session median is 369.752 ms.

That measurement uses a different timing convention
than the 222.923 ms PC/SC transmit replay. It must
not be compared numerically with the JCOP4
150.046 ms median to claim a hardware speedup.

### Native ECDH on JCOP4

The reported JCOP4 native ECDH median remained
approximately 85.6 to 85.9 ms across fixed public
scalars from 2 to 251 bits.

This is a separate operation from PACE-GM.
There is no equivalent, verified same-methodology
JCOP3 result established in the compared reports.

Do not derive a JCOP3-to-JCOP4 ECDH speedup from
these data.

### RSA coprocessor measurements

JCOP4 RSA-1024 modular exponentiation:

- Exponent: 3
- Median PC/SC transmit: 241.751 ms
- Responses verified: 10/10

The JCOP3 BN254 RSA-squaring research benchmarks
use different exponentiation and reduction workloads.

These results are not an apples-to-apples RSA speed
comparison. No cross-generation RSA speedup is
calculated here.

## Correctness and capability

JCOP4 demonstrated:

- Native ECDH outputs matching host reference arithmetic
- Flat measured ECDH latency across tested scalar lengths
- PACE-GM agreement with 50/50 published vector executions
- RSA-1024 response verification, 10/10
- A provider-specific `K=1` initialization requirement

The published PACE-GM applet returned SW 6F02 on
the tested JCOP4 provider without the correction.

The independently verified JCOP4 implementation was
Mikkoph's separate 4D00 variant.

Our 4E00/4E01 variant passes offline CAP verification
and mock tests; its physical execution remains unverified.

## Measurement limitations

The PACE-GM medians use the same measurement convention,
but the benchmarks were not conducted on identical
readers, host environments, or applet configurations.

The reported numbers do not measure isolated
cryptographic engine execution time.

The original JCOP4 machine-readable JSON artifacts
are not yet imported into this repository.

No per-sample measurements have been reconstructed
or invented from the published aggregates.

The results establish research capability and
reproducibility, not side-channel security or a
complete hardware-isolated RAILGUN signing implementation.

## Sources

JCOP3 physical report:

- RESULTS.md — M3.6b verified physical replay
- BN254-RSA-PHYSICAL.md — separate RSA research

JCOP4 independent reproduction by Mikkoph,
dated 2026-11-19:

- JCOP4-2026-11-19.md
- https://gist.github.com/bitgamma/18bed236b7073b8b951f26ba68e76515

Original JCOP4 machine-readable result files:
pending import and independent verification.
