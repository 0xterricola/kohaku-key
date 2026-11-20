# JCOP4 PACE-GM compatibility experiment

This variant preserves the original PACE-GM research applet
and adds `key.setK((short)1)` at initialization step 7.

## Evidence

Mikkoph's JCOP4 physical reproduction (2026-11-19):

- Published PACE-GM implementation: SW `6F02`
- Corrected K=1 implementation: 50/50 vectors matched
- JCOP4 median PACE-GM: 150.046 ms
- Published JCOP3 median: 222.923 ms
- Measurements use per-APDU transmit latency

## Important distinction

The underlying curve's mathematical cofactor is 8.
Setting K=1 is an experimentally observed compatibility
requirement for this JCOP4 provider and these public vectors.

This does not establish subgroup safety for arbitrary
points or production RAILGUN signing compatibility.

## Safety

Research-only applet. Do not install onto an initialized
wallet without explicit hardware and lifecycle review.
No private scalars or wallet credentials are used by
the published benchmark vectors.

## Local build and validation — 2026-11-20

The experimental source adds `key.setK((short)1)` at
initialization step 7. Original published source and CAP remain
unchanged.

- Package AID: `F0424E3235344E00`
- Applet AID: `F0424E3235344E01`
- Experimental CAP: `pace-gm-k1.cap`
- Initial build ZIP SHA-256 (historical): `2e8575b79125f6771f120054f8f86dfcb68c9ca0db0c28fce1f3437e58db177e`
- Published CAP SHA-256: `12083cee1614ad080a24c5af7c3e9b1cdf1aeaedfb67a5fcff22cf97fb4353d8`
- Compiler: JavaCard SDK 3.0.4, JDK 11, ant-javacard 26.05.15
- JavaCard converter verification: PASS
- `test_physical_pace.py`: 4/4 mock tests PASS
- `scripts/benchmark.py`: offline artifact/vector checks PASS

### Evidence boundaries

Local mock tests do not execute this CAP or prove JCOP4
compatibility. The offline benchmark validates reference fixtures,
not the modified applet's runtime behavior.

Mikkoph independently reported 50/50 physical PACE-GM vector
matches on JCOP4 using his separately built K=1 variant
(package `F0424E3235344D00`), with 150.046 ms median
per-APDU transmit latency. His result does not constitute a
physical test of this `4E00` CAP.

`K=1` is a provider-specific research compatibility setting,
not the actual curve cofactor (8). Arbitrary-point and subgroup
safety remain unverified.

### Rebuild requirements

The Gradle configuration references the JavaCard SDK and
keycard-math dependency through `KEYCARD_JC_SDK` and
`KEYCARD_MATH_HOME` environment variables.

The local Ant build was derived from an experimental toolchain.
Audit machine-specific paths before treating it as a portable
developer build. Do not deploy to an initialized wallet as
part of an automated test.

## Reproducibility and CAP packaging

The JavaCard converter produced identical payloads for all
10 CAP components in two consecutive builds on 2026-11-20.

The enclosing CAP ZIP SHA-256 changed between builds because
the archive representation was not byte-for-byte identical.
The build should therefore not require a fixed ZIP hash.

Current local CAP ZIP SHA-256: `54d3fca1e99e47ecf2c3be2127e678f9fcdf3dac8b83de7bd70c35a4360cb38c`

Canonical component digest: `a5dfbcd5b875c1a8d539ac480fea98017808d4c2b34f94b13c043d7dbbaa1e96`

Canonical digest method: SHA-256 over the lexicographically
sorted `.cap` ZIP entries, concatenating for each entry its
UTF-8 filename prefixed by a 4-byte big-endian length and its
uncompressed contents prefixed by an 8-byte big-endian length.

This digest identifies the tested component payloads, but
does not establish reproducibility across other SDK/compiler
versions or prove physical JCOP4 execution.

The original published CAP is unchanged.
