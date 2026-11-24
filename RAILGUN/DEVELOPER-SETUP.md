# RAILGUN Developer Setup

Reproduce the Kohaku Key PACE-GM research without accessing
or modifying a physical smart card.

## Requirements

Offline validation requires Python 3.

Building the JCOP4 compatibility applet requires:

- JDK 11
- Apache Ant
- ant-javacard 26.05.15 (tested)
- JavaCard SDK 3.0.4 (tested)
- Compatible keycard-math JAR and export files

Physical execution additionally requires pyscard and a
dedicated research smart card.

Do not distribute GlobalPlatform credentials, wallet secrets,
or proprietary SDK components through this repository.

## Clone and validate offline

    git clone https://github.com/0xterricola/kohaku-key.git
    cd kohaku-key

```sh
python3 -B RAILGUN/scripts/check_developer_setup.py
python3 -B -m unittest discover -s RAILGUN/tests -p 'test_physical_pace.py' -v
python3 -B RAILGUN/scripts/benchmark.py
```

All three commands are offline.

## Build the JCOP4 compatibility CAP

Set your local dependency paths:

```sh
export JAVA_HOME=/path/to/jdk-11
export PATH="$JAVA_HOME/bin:$PATH"
export ANT_JAVACARD_JAR=/path/to/ant-javacard.jar
export KEYCARD_JC_SDK=/path/to/jc304_kit
export KEYCARD_MATH_HOME=/path/to/keycard-math
```

Then run:

```sh
RAILGUN/experiments/physical-benchmark-runner/applets/pace-gm-k1/build-offline.sh
```

The experimental applet uses:

- Package AID: F0424E3235344E00
- Applet AID: F0424E3235344E01

The published original uses:

- Package AID: F0424E3235343C00
- Applet AID: F0424E3235343C01

The original applet and CAP remain unchanged.

## Physical benchmark

The existing physical runner supports two applet configurations:

- published: F0424E3235343C01
- jcop4-k1: F0424E3235344E01

These are applet configurations, not automatic JCOP
hardware-generation detection.

The runner requires an already-installed applet at stage 11.
It does not install or initialize applets.

View available options:

```sh
python3 -B RAILGUN/scripts/physical_pace.py --help
```

On a separately prepared dedicated research card only:

```sh
python3 -B RAILGUN/scripts/physical_pace.py \
  --reader "READER_NAME" \
  --applet jcop4-k1 \
  --confirm-test-card \
  --execute-public-vectors \
  --report RAILGUN/benchmarks/local-pace-run.json
```

This final command TRANSMITS APDUs. Do not run it during
offline setup or on an unverified wallet card.

## Research evidence

Mikkoph independently reported 50/50 matching PACE-GM
vectors on JCOP4 using a separate K=1 applet variant.

Published median PC/SC transmit measurements:

- JCOP3: 222.923 ms
- JCOP4 with K=1: 150.046 ms

Our 4E00 variant compiles and passes offline validation.
Physical execution of this exact CAP remains unverified.

K=1 is an experimentally observed JCOP4 provider setting,
not the underlying curve's mathematical cofactor (8).

Consult the JCOP4-COMPATIBILITY.md document in the
pace-gm-k1 applet directory for detailed evidence and
CAP reproducibility information.
