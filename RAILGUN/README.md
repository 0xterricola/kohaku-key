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

### Poseidon — fastest JCOP3 physical implementation

The **7E RSA-5 sparse-dictionary** implementation is the fastest measured on-card Poseidon T3 implementation in this research: **~230.520 seconds/hash** reported over five canonical vectors, with **325/325 physical round states** verified. Two pinned original run records include `one-two` **230.716374 s** and `three-five` **230.569210 s**.

The older implementation measured **376.979 s** for `[0,0]` and **375.644 s** for `[1,2]`; those remain historical baselines, not current records. The later **7F Barrett** variant passed 65/65 rounds on `one-two` but took **255.289453 s**, 10.65% longer than 7E in the reported single-run comparison. Benchmark timing boundaries are not fully identical. Neither T3 result establishes a viable on-card RAILGUN T6 challenge.

See the [hardware leaderboard](benchmarks/HARDWARE-LEADERBOARD.md) and [7E/7F physical evidence](benchmarks/RESULTS.md).

### BN254 RSA modular squaring

Archived physical experiments document 120/120 successful
APDUs against independent reference arithmetic.

For dense operands, approximately 550 ms was observed for
single-RSA squaring versus 633 ms for the earlier three-RSA
implementation.

This does not demonstrate arbitrary field multiplication
at equivalent speed.

## JCOP3 and JCOP4 compatibility

The JCOP3 physical experiments establish native ECC, PACE-GM,
BN254 arithmetic, and Poseidon research capabilities. The
measurements are not evidence of complete hardware-isolated
RAILGUN EdDSA-Poseidon signing.

Mikkoph independently reproduced the PACE-GM operation on JCOP4.
The tested JCOP4 provider required `key.setK((short)1)` at
initialization step 7. This is a provider compatibility setting,
not the BabyJubJub curve's mathematical cofactor (8).

| Research result | JCOP3 | JCOP4 |
| --- | --- | --- |
| PACE-GM public vectors | 10/10 physical PASS | 50/50 physical PASS, independently reported |
| PACE-GM median PC/SC transmit | 222.923 ms | 150.046 ms |
| Native ECDH | Physically demonstrated | Independently demonstrated |
| Local K=1 `4E00/4E01` CAP | Not physically tested | Offline verified; physical test pending |
| Complete RAILGUN hardware signing | Not demonstrated | Not demonstrated |

The reported JCOP4 PACE-GM median is 32.69% lower than the
JCOP3 replay median. Different readers, hosts, and applet
configurations prevent attributing this difference solely to
JCOP4 silicon. CLI-inclusive and PC/SC transmit measurements
must not be mixed.

JCOP4.5 performance and compatibility remain unverified.

### Reproduction and evidence

- [JCOP3 physical replay](benchmarks/RESULTS.md)
- [JCOP4 independent reproduction](benchmarks/JCOP4-2026-11-19.md)
- [Cross-generation comparison](benchmarks/JCOP3-VS-JCOP4.md)
- [K=1 applet compatibility experiment](experiments/physical-benchmark-runner/applets/pace-gm-k1/JCOP4-COMPATIBILITY.md)
- [Developer setup](DEVELOPER-SETUP.md)
- [Hardware safety](HARDWARE-SAFETY.md)
- [JavaCard error diagnostics](JAVACARD-ERRORS.md)

Four original machine-readable JCOP4 benchmark files supplied by Mikkoph are now archived, SHA-256-pinned and checked for internal consistency, without synthesizing samples. See [source and raw results](benchmarks/jcop4-2026-11-19/README.md). Physical re-execution of our separate `4E01` variant remains pending.

## Current objectives

1. Verify JCOP4 compatibility (Mikkoph's `4D01` result is complete; our `4E01` is pending)
2. Validate two-phase synthetic-key BabyJubJub EdDSA-Poseidon signing on JCOP3, then JCOP4
3. Evaluate Shell approval, host challenge binding, and progressive hardening with Keycard/Railgun developers
4. Keep on-card Poseidon RSA-5 as a documented, paused performance track

See [Research Roadmap](docs/ROADMAP.md) and
[Physical Benchmarks](benchmarks/RESULTS.md).

## Reproducibility

Compiled JavaCard CAPs and source are included when their
original physical-test fingerprints can be verified.

CAPs are experimental. Do not install them on a wallet
containing valuable credentials.

Simulator correctness and physical device results must remain
separately documented.
