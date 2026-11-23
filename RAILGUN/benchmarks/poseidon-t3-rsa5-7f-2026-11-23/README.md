# Physical JCOP3 Poseidon T3 — Barrett 7F

Date: 2026-11-23

## Artifact identity

- Package AID: `F0424E3235347F00`
- Applet AID: `F0424E3235347F01`
- CAP SHA-256: `be1c0cb797624ba50235e9b26086f8f2c18b6c1e0917a8d28335634182ac71f0`
- CAP archive size: 115244 bytes
- Platform: experimental JCOP3
- Reader: HID OMNIKEY 3x21 over PC/SC

## Verified physical result

Experiment: `M3.42j.24`

- Canonical vector: `one-two`
- Applet SELECT: PASS
- Intermediate rounds: **65/65 PASS**
- Canonical final hash: PASS
- Host elapsed time: **255.289453 seconds**
- Wallet operations: zero

The JSON report is reconstructed from the sanitized terminal
summary. It is not a raw timing trace.

## Comparison

| Implementation | Vector | Time |
| --- | --- | ---: |
| 7E RSA-5 | one-two | 230.716374 s |
| 7F Barrett | one-two | 255.289453 s |

7F took 24.573079 seconds longer, a 10.65% regression
relative to 7E in this single-run comparison.

The measurements were collected in separate physical runs.
They are not controlled, repeated-trial medians, and
the timing boundaries are not fully identical.

## Technical interpretation

Barrett reduction replaces division-based modular reduction
with reciprocal multiplication.

This implementation adds a 196-byte transient workspace,
byte-limb arithmetic, correction loops, and two Barrett
reduction stages for the 92-byte RSA result.

The physical result establishes correctness for one 7F
vector, but not a performance improvement over 7E.

The source of the slowdown has not been isolated.

## Installation findings

The pinned 7F package loaded successfully, but its first
applet installation returned SW 6985.

After removing the 7E applet and executable package,
the already-loaded 7F applet installed successfully.

The wallet remained accessible and its verified identity
was preserved.

This is consistent with a card-resource constraint, but
the specific resource exhaustion mechanism is unproven.

## Reproducibility

See the 7F applet README and Python runner.

Offline verification requires only Python 3.
Physical execution requires a compatible installed applet,
PC/SC reader, pyscard and the matching pinned CAP.

The CAP and reconstructed arithmetic source are not
redistributed pending provenance and licensing review.

This is public-input arithmetic research, not complete
hardware RAILGUN signing or side-channel validation.
