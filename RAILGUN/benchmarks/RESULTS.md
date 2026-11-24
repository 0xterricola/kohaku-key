# Physical JCOP3 Benchmark Summary

**Authoritative fastest-measured-by-operation index:** [Hardware leaderboard](HARDWARE-LEADERBOARD.md). This page also preserves historical measurements whose timing scopes differ. Four independently supplied JCOP4 JSON reports are archived [here](jcop4-2026-11-19/README.md).

Device: Experimental Keycard 4.x on JCOP3.

Reader: HID OMNIKEY 3x21 over PC/SC.

| Experiment | Verified | Result |
| --- | ---: | --- |
| Native ECC initial regression | 20/20 full-point results | PASS |
| PACE-GM public addition | 10/10 vectors | PASS |
| Warm interleaved ECC/PACE replay | 50/50 APDUs | PASS |
| Historical BN254 RSA square tests | 120/120 APDUs | PASS |
| Historical Poseidon T3 implementation | 2/2 hashes, 130/130 round states | PASS |
| **RSA-5 7E Poseidon T3** | **5/5 hashes, 325/325 round states** | **PASS** |
| Barrett 7F Poseidon T3 | 1/1 hash, 65/65 round states | PASS |

The two historical Poseidon hashes are **not** the 7E result. Current
fastest measured Poseidon T3 is 7E; the 7F result covers one vector.
The 7F host-elapsed timing boundary is not identical to the original
7E 65-round timing boundary.

## Warm-session medians

- 2B: 347.034 ms
- KB: 352.742 ms
- PACE: 369.752 ms
- No-op 0x37: 149.615 ms
- No-op 0x3C: 146.757 ms

All warm measurements include CLI startup, applet
selection, PC/SC, and smart-card execution.

## Reproducibility requirements

Cross-generation benchmarking must record the card model,
JavaCard platform, applet/CAP hashes, reader, transport,
test vectors, initialization state, and APDU timing method.

Do not compare simulator projections with physical card
measurements as if they were equivalent.

## M3.6b verified JCOP3 replay — 2026-11-18

- Hardware: experimental JCOP3 Keycard
- Transport: HID Global OMNIKEY 3x21, PC/SC
- Applet: PACE-GM research applet, stage 11
- Public vectors: 10/10 exact response matches
- Status words: 10/10 SW 9000
- Median PC/SC transmit latency: 222.923 ms
- SELECT latency: 48.946 ms
- Stage query latency: 5.875 ms
- Offline regression tests: 22/22 passed
- No wallet signing, installation or reprovisioning

Timing is host-observed PC/SC transmit latency,
not isolated secure-element computation time.

The physical runner and mock tests are published under
RAILGUN/scripts and RAILGUN/tests.

## Poseidon T3 RSA-5 — JCOP3 7E

Fastest measured JCOP3 on-card Poseidon T3: **7E RSA-5**. Five canonical vectors and 325 physical round checkpoints passed. Reported five-vector latency: **~230.520 seconds/hash**; two original per-run records are pinned (230.716374 s `one-two`, 230.569210 s `three-five`). See the [archived evidence](poseidon-t3-rsa5-7e-2026-11-21/README.md).

## Poseidon T3 — 7F Barrett

JCOP3 physical `one-two`: **65/65 rounds PASS**, **255.289453 s** host elapsed. The 7E baseline was **230.716374 s**. 7F was **10.65% slower** in this single-run comparison. See the [7F report](poseidon-t3-rsa5-7f-2026-11-23/README.md).
