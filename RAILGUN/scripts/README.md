# Benchmark Scripts

The original physical benchmark evidence is preserved in the
local research validation workspace.

Portable JCOP3/JCOP4/JCOP4.5 benchmarking is the next
publication task. Any installer must be separate from the
benchmark runner, require explicit authorization, and verify
card compatibility before modifying installed applets.

No test script should provision or expose wallet keys.

## Hardware preflight

`hardware_preflight.py` enumerates PC/SC readers and optionally
selects an already-installed ECC or PACE research applet.

It does not install applets or run benchmark APDUs.
See [hardware developer setup](../experiments/physical-benchmark-runner/README.md).
