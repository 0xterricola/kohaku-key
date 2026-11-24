# JavaCard Research Applet Builds

The ECC and PACE applets use JavaCard 3.0.4 and
the Keycard math library.

Set these environment variables before building:

```sh
export KEYCARD_JC_SDK=/path/to/jc304_kit
export KEYCARD_MATH_HOME=/path/to/keycard-math
```

KEYCARD_MATH_HOME must contain keycard-math.jar
and its JavaCard export files.

The `native-ec` and `pace-gm` applet directories use Gradle.
The separate `4E01` compatibility applet documents an Ant-based
`build-offline.sh` workflow under
[`experiments/physical-benchmark-runner/applets/pace-gm-k1/`](../experiments/physical-benchmark-runner/applets/pace-gm-k1/JCOP4-COMPATIBILITY.md).

Some compiled native ECC and PACE research CAPs are included as
fingerprint-verified JCOP3 artifacts. The original Poseidon 7E/7F
CAPs are **not** redistributed; offline arithmetic fixtures and
physical measurement evidence are documented separately.

Rebuilding may produce different CAP hashes.
Do not replace the verified artifacts without
independent correctness and compatibility testing.

Do not commit proprietary NXP SDK files.

No applet installation is required to build.
