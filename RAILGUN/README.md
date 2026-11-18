# RAILGUN — Secure Element Research

Independent investigation of BabyJubJub, Poseidon,
BN254 arithmetic, and hardware-assisted EdDSA signing.

## Current physical accomplishments

### Native BabyJubJub scalar multiplication

Converted BabyJubJub to short-Weierstrass representation
and used JCOP3 native ECC KeyAgreement operations.

- 2B initial median: 209.317 ms
- Fixed 251-bit KB initial median: 207.989 ms
- Initial regression: 20/20 verified full-point results

The segmented software 2B baseline was 600.954497 seconds.
The initial host-observed execution paths differed by
approximately 2,871 times.

### PACE point addition

Native ALG_EC_PACE_GM point addition with public s=1:

- 10 distinct input points
- 10/10 verified full X/Y results
- Initial median: 358.967 ms

### Controlled warm-session benchmark

Ten interleaved rounds:

| Operation | Median |
| --- | ---: |
| Native 2B | 347.034 ms |
| Native KB | 352.742 ms |
| PACE addition | 369.752 ms |
| ECC no-op | 149.615 ms |
| PACE no-op | 146.757 ms |

All 50/50 APDUs passed.

These measurements include process startup, applet selection,
PC/SC transport, and card execution. They are not isolated
coprocessor latencies.

### Poseidon

Two complete physical two-input hashes passed, with
130/130 intermediate round states matching reference results.

- Hash [0,0]: 376.979 seconds
- Hash [1,2]: 375.644 seconds

The physical Poseidon implementation remains too slow for
practical on-card signing without substantial optimization.

### BN254 RSA modular squaring

Archived physical experiments document 120/120 successful
APDUs against independent reference arithmetic.

For dense operands, approximately 550 ms was observed for
single-RSA squaring versus 633 ms for the earlier three-RSA
implementation.

This does not demonstrate arbitrary field multiplication
at equivalent speed.

## Current objectives

1. Physical BabyJubJub EdDSA-Poseidon signing
2. Poseidon hardware acceleration on JCOP and Shell
3. Secure RAILGUN signing integration and key isolation

See [Research Roadmap](docs/ROADMAP.md) and
[Physical Benchmarks](benchmarks/RESULTS.md).

## Reproducibility

Compiled JavaCard CAPs and source are included when their
original physical-test fingerprints can be verified.

CAPs are experimental. Do not install them on a wallet
containing valuable credentials.

Simulator correctness and physical device results must remain
separately documented.
