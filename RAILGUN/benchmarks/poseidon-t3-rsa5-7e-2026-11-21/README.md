# JCOP3 Poseidon T3 RSA-5 — 7E Physical Baseline

**Status:** Physically verified research baseline  
**Device:** Experimental JCOP3 Keycard  
**Reader:** HID OMNIKEY 3x21, PC/SC  
**Package AID:** `F0424E3235347E00`  
**Applet AID:** `F0424E3235347E01`  
**CAP SHA-256:** `da9329e4682ffb132d092b128d283e3a50f0d461fd6a7bddda9cdaf564bfdfe6`  
**Physical runner SHA-256:** `2e89eaf498f1a2516996a8c3a097684a86ea85469de520e0bf1312665d8d1c7b`

## Results

| Measurement | Result |
| --- | ---: |
| Poseidon width | 3 field elements |
| Full / partial rounds | 8 / 57 |
| Total rounds per hash | 65 |
| Canonical vectors verified | 5/5 |
| Physical round checkpoints verified | 325/325 |
| Reported five-vector latency | ~230.520 seconds/hash |
| Previous physical baseline | ~362.363 seconds/hash |
| Relative speedup | ~1.572x |

The five canonical vectors were `zero`, `one-two`, `three-five`,
`mixed`, and `boundary`. Their physical round-state outputs were
checked against the independent reference.

## Pinned individual physical records

| Vector | 65-round execution time |
| --- | ---: |
| `one-two` | 230.716374 seconds |
| `three-five` | 230.569210 seconds |

These are the two original physical execution records preserved in
this directory. Their original SHA-256 digests are recorded in
`SHA256SUMS`. The two-record mean is 230.642792 seconds.

The broader 325-round result is a separate reported physical
benchmark result. Do not infer that all five original JSON records
are included here.

## Methodology

The JCOP3 applet performs Poseidon T3 computation using the
experimental RSA-5 BN254 arithmetic implementation. The physical
runner submits public canonical field elements and checks the
computed round states and final result against reference fixtures.

Reported timings reflect physical execution through PC/SC and
include benchmark transport/dispatch overhead. They are not
isolated RSA coprocessor timings.

## Reproduction and limitations

The original runner remains at
`RAILGUN/experiments/poseidon-t3-rsa5-jcop3-2026-11-21/physical_poseidon_t3.py`.

The CAP's original SHA-256 is recorded above. The original compiled
CAP and separate JavaCard source repository are not copied into
this evidence snapshot.

This baseline demonstrates physical Poseidon correctness, not
complete RAILGUN signing, private-scalar isolation, side-channel
resistance, or practical transaction-signing latency.

## Subsequent implementation: 7F Barrett — physically measured

The first 7F installation attempt returned `6985` after successful package load. After targeted retirement of 7E's applet and package, the already-loaded 7F installed and selected successfully on November 23; wallet identity checks passed. The failure's exact resource cause remains unproven.

7F physically verified the canonical `one-two` vector, all **65/65 intermediate rounds**, and final output at **255.289453 seconds** host elapsed. The original pinned 7E `one-two` run was **230.716374 seconds**: 7F was **10.65% slower** in this non-identical-timing-boundary, single-run comparison. See [7F benchmark](../poseidon-t3-rsa5-7f-2026-11-23/README.md). The 7E physical applet is retired from the card; its pinned CAP hash, runner, vectors, and original measurements remain archived.
