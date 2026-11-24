# Benchmark Scripts

Validated JCOP3 physical evidence and independently supplied JCOP4
results are indexed in the [hardware leaderboard](../benchmarks/HARDWARE-LEADERBOARD.md).
The [experiment archive](../experiments/README.md) distinguishes
historical captures from portable reproduction tools.

No benchmark runner should provision or expose wallet keys.
Applet installation and lifecycle management are separate, explicitly
authorized operations; benchmark scripts must not perform them.

## Hardware preflight

`hardware_preflight.py` enumerates PC/SC readers and optionally
selects an already-installed ECC or PACE research applet.

It does not install applets or run benchmark APDUs.
The opt-in `physical_native_ecc.py` and `physical_pace.py` runners
can transmit public test APDUs to separately verified research cards.
See [hardware developer setup](../DEVELOPER-SETUP.md) and
[hardware safety](../HARDWARE-SAFETY.md).

## Offline validation

```sh
python3 -B RAILGUN/scripts/check_developer_setup.py
python3 -B RAILGUN/scripts/benchmark.py
python3 -B -m unittest discover -s RAILGUN/tests -p 'test_*.py' -v
```

These commands do not access a card.

## Poseidon T3 RSA-5 regression

Run `python3 -B RAILGUN/scripts/poseidon_t3_7e.py --self-test` from the repository root. See [7E hardware reproduction](../applets/poseidon-t3-rsa5-7e/README.md).

## Poseidon T3 — 7F Barrett

Run `python3 -B RAILGUN/scripts/poseidon_t3_7f.py --self-test` to verify all five canonical vectors.
