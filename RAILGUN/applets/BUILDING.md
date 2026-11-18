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

Run Gradle from each applet directory.

The verified CAP files in this repository are
physical JCOP3 research artifacts.

Rebuilding may produce different CAP hashes.
Do not replace the verified artifacts without
independent correctness and compatibility testing.

Do not commit proprietary NXP SDK files.

No applet installation is required to build.
