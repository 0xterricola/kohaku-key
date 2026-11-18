# Physical JCOP3 Benchmark Summary

Device: Experimental Keycard 4.x on JCOP3.

Reader: HID OMNIKEY 3x21 over PC/SC.

| Experiment | Verified | Result |
| --- | ---: | --- |
| Native ECC regression | 20/20 | PASS |
| PACE addition | 10/10 | PASS |
| Warm interleaved APDUs | 50/50 | PASS |
| Historic BN254 RSA square APDUs | 120/120 | PASS |
| Full two-input Poseidon hashes | 2/2 | PASS |
| Poseidon intermediate round states | 130/130 | PASS |

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
