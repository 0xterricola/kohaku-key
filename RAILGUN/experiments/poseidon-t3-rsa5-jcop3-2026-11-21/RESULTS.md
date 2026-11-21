# JCOP3 physical Poseidon RSA-5 benchmark results

Date: 2026-11-21  
Applet: `F0424E3235347E01`  
CAP: `da9329e4682ffb132d092b128d283e3a50f0d461fd6a7bddda9cdaf564bfdfe6`

## Physical execution time

| Vector | Total (s) | Full median (ms) | Partial median (ms) | Historical baseline ratio | Canonical |
|---|---:|---:|---:|---:|---|
| zero | 230.342 | 5749.785 | 3235.379 | 1.573x | PASS |
| mixed | 230.437 | 5723.312 | 3234.925 | 1.573x | PASS |
| boundary | 230.535 | 5707.474 | 3236.602 | 1.572x | PASS |

Historical t3 reference: **362.363 seconds**.

Mean across the three observed RSA-5 executions:
**230.438 seconds**.

Historical-to-current mean ratio: **1.572x**.

This ratio compares different applet versions and separately measured
runs; it is not a controlled same-session comparative benchmark.

## Canonical final-state verification

The following SHA-256 fingerprints identify the complete 96-byte
final Poseidon state, not merely its first 32-byte hash word.

| Vector | Final-state SHA-256 | Result |
|---|---|---|
| zero | `7d5dc71981bb3ca593c233b3aad1ef44e4c5b6961c70700b7a4535d808a1c12b` | PASS |
| mixed | `ab4f182cd4611a056d1c1b335823fd166fcd2bf8c196330b5e07dbbc6502f698` | PASS |
| boundary | `f1fdd5d92257160f153780de5255bbe7903fdbe3377c1d5bfc6e73f3007cfc15` | PASS |

All 195 physical rounds returned SW `9000`; all three final states
matched the pinned canonical fixtures byte-for-byte as reported by
their respective runners.

## Storage and simulator benchmarks

| Variant | CAP components |
|---|---:|
| 7C two-square S-box | 17,116 bytes |
| 7D RSA-5 S-box | 17,778 bytes |
| 7E RSA-5 dictionary | **16,409 bytes** |

7D versus 7C simulator ratio: **1.220x**.  
7E versus 7D simulator ratio: **1.001x**.  
7E CAP reduction versus 7D: **1,369 bytes**.

Simulator and physical timings must not be directly equated.

## Timing methodology

Eight full rounds and 57 partial rounds per hash. Each measured round
includes the PC/SC APDU transmission latency. Totals exclude
initialization and SELECT. Values are one-run samples per vector,
not repeated-run medians.

## Data integrity

The individual timings, observed totals, observed medians, full-state
fingerprints and fixture hashes are recorded in `round-times.csv` and
`artifacts.json`.

No APDU payloads containing secrets were recorded. All test inputs
were public.
