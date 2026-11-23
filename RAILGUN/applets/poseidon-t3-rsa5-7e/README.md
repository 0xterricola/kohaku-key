# Poseidon T3 RSA-5 — 7E

Hardware-verified JavaCard Poseidon research baseline.

- Package AID: `F0424E3235347E00`
- Applet AID: `F0424E3235347E01`
- CAP SHA-256: `da9329e4682ffb132d092b128d283e3a50f0d461fd6a7bddda9cdaf564bfdfe6`
- Platform tested: experimental JCOP3, PC/SC
- Five canonical vectors, 325 round-state checks
- Reported physical execution: approximately 230.5 seconds/hash

## Offline regression

From the repository root:

```sh
python3 -B RAILGUN/scripts/poseidon_t3_7e.py --self-test
```

Requires Python 3 only. No smart card is accessed.

## Physical reproduction

Obtain the exact matching CAP from an authorized build or
research artifact, install it using an authorized management
workflow on an expendable compatible JavaCard, and verify the
installed applet AID before testing.

This repository does **not** automatically install applets.

```sh
python3 -B RAILGUN/scripts/poseidon_t3_7e.py \
  --hardware --cap /path/to/pinned-7e.cap --vector one-two
```

Repeat for `zero`, `three-five`, `mixed`, and `boundary`.
The original runner verifies round states and final results.
The hardware benchmark uses the original PC/SC implementation;
reader selection and platform compatibility must be verified
for each test environment.

Additional pinned dependencies may be supplied with
`--artifact SHA256=PATH` when required.

The exact historical CAP and reconstructed arithmetic source
are not redistributed in this checkpoint pending provenance
and licensing review. Consequently, a fresh clone can run
all offline tests, but cannot independently build or install
the original 7E applet from this repository alone.

## Benchmark evidence

[Physical baseline and original JSON results](../../benchmarks/poseidon-t3-rsa5-7e-2026-11-21/README.md)

Hardware performance is not equivalent to simulator performance.
This is a cryptographic research applet, not a production wallet.
