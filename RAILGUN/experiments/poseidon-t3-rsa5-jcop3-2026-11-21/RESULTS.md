# JCOP3 physical Poseidon RSA-5 benchmark results

- **Date:** 2026-11-21
- **Experiment milestones:** M3.42i.3a, M3.42i.4, M3.42i.7
- **Applet AID:** `F0424E3235347E01`
- **Package AID:** `F0424E3235347E00`

## Five canonical physical vectors

| Vector | Total (s) | Full median (ms) | Partial median (ms) | Historical baseline ratio | Final state |
|---|---:|---:|---:|---:|---|
| zero | 230.342 | 5749.785 | 3235.379 | 1.573× | PASS |
| one-two | 230.716 | 5763.380 | 3246.927 | 1.571× | PASS |
| three-five | 230.569 | 5689.713 | 3246.466 | 1.572× | PASS |
| mixed | 230.437 | 5723.312 | 3234.925 | 1.573× | PASS |
| boundary | 230.535 | 5707.474 | 3236.602 | 1.572× | PASS |

**All 325 physical rounds passed (SW `9000`). All five final 96-byte states match canonical fixtures.**

- **Mean execution time:** 230.520 seconds
- **Historical Poseidon T3 reference:** 362.363 seconds
- **Historical-to-current execution ratio:** 1.572×

These values include PC/SC round-trip overhead but exclude SELECT
and vector initialization. The comparison uses separately measured
historical and current applets, not a controlled interleaved hardware benchmark.

## Final-state fingerprints

SHA-256 identifies each full 96-byte final state.

| Vector | SHA-256 | Result |
|---|---|---|
| zero | `7d5dc71981bb3ca593c233b3aad1ef44e4c5b6961c70700b7a4535d808a1c12b` | PASS |
| one-two | `c5b5f2594cfc02fadfd69805667e461f14e26da62bae230d73383a6541d7edbf` | PASS |
| three-five | `021f99e20af0ce33f408a9c3eb165d8b13cb46336e5546475b0de005c96a06ed` | PASS |
| mixed | `ab4f182cd4611a056d1c1b335823fd166fcd2bf8c196330b5e07dbbc6502f698` | PASS |
| boundary | `f1fdd5d92257160f153780de5255bbe7903fdbe3377c1d5bfc6e73f3007cfc15` | PASS |

## RSA-5 and dictionary optimization

| Applet variant | CAP component bytes |
|---|---:|
| 7C two-square S-box | 17,116 |
| 7D RSA-5 S-box | 17,778 |
| 7E RSA-5 sparse dictionary | **16,409** |

The 7E dictionary saves 1,369 bytes relative to 7D.

jCardSim measured 1.220× for 7D versus 7C and 1.001× for
7E versus 7D. These simulator timings are distinct from the
physical hardware measurements above.

## Raw timing evidence

`round-times.csv` contains all **325** round measurements, with
vector indices, full/partial classification and status words.

The first 195 records originated from displayed physical-run logs.
The final 130 originated from the reusable native PC/SC runner.

### New machine-readable runs

| Vector | Evidence | SHA-256 |
|---|---|---|
| one-two | `runs/20261121T233700210857Z-one-two.json` | `84a37ed7bff0b1fdb834a82105fd6910fbda1b643b363df181ef3bc2256ab7bb` |
| one-two | `runs/20261121T233700210857Z-one-two.csv` | `382e785a0e99c30cceeef6ae84d4174ab613a0e8087e959fc851b7333c6ea13c` |
| three-five | `runs/20261121T234050909184Z-three-five.json` | `1ca1e0cefd7de2a1fdea059ebaf4181a3923f91266185c55d6525f01a1380864` |
| three-five | `runs/20261121T234050909184Z-three-five.csv` | `67a4c277d8e37a7d0a11a0a0445151713eb18c86b5c968889bad07319b3f64a7` |

Each execution ran one complete 65-round hash. One execution
per vector was recorded; there is no repeated-trial confidence
interval.

The installed research applet and initialized wallet remained unchanged
during these measurements. No PIN, private-key, installation or
deletion operations were performed.
