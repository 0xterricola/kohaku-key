# Physical JCOP3 RSA-accelerated BN254 squaring

## Research checkpoint

- Experiments: M2.22ba, M2.22bb, M2.22bc
- Hardware: physical experimental JCOP3 Keycard 4.x, OMNIKEY PC/SC
- Package AID: `F0424E3235341700`
- Applet AID: `F0424E3235341701`
- CAP SHA-256: `b1a4022d97b753d493fb395c35f65a1ed9537ec1562aab5d379b45dc385713f3`
- Input: public canonical BN254 field element
- Output: 32-byte big-endian square modulo the BN254 field prime

## Implementations

- `0x62`: one RSA exponent-2 operation followed by `modRed`
- `0x63`: existing three-RSA `modMul(a,a)` implementation
- Both use the existing `BigNumberMath.modRed` reduction algorithm.

## Correctness

- jCardSim: 74/74 public vectors, 148/148 arithmetic APDUs
- jCardSim: 3/3 reselection comparisons
- jCardSim: 6/6 malformed APDU rejection checks
- Physical M2.22ba: 8/8 APDUs
- Physical M2.22bb: 40/40 APDUs
- Physical M2.22bc: 72/72 APDUs
- Every physical result matched independent Python arithmetic.
- Existing wallet identity, initialization, master-key presence,
  and three PIN retries were preserved.

## Repeated benchmark: M2.22bb

Four measured pairs per operand, one warm-up pair, alternating
instruction order in a single CLI shell session.

| Operand | Single RSA | Three RSA | Savings |
|---|---:|---:|---:|
| Zero | 38 ms | 127 ms | 89.5 ms |
| One | 38 ms | 127 ms | 89.4 ms |
| Dense | 550 ms | 633 ms | 83.6 ms |
| Near modulus | 531 ms | 615 ms | 83.7 ms |

These are host-observed APDU latencies, not isolated JavaCard
instruction timings.

## Operand bit-length profile: M2.22bc

Each row reports the median of two measured APDUs per instruction,
following one warm-up pair.

| Input bits | Single RSA (ms) | Three RSA (ms) | Savings (ms) |
|---:|---:|---:|---:|
| 0 | 38 | 127 | 89.6 |
| 1 | 38 | 127 | 89.5 |
| 32 | 38 | 127 | 89.4 |
| 64 | 38 | 127 | 89.4 |
| 96 | 38 | 127 | 89.4 |
| 112 | 38 | 127 | 89.3 |
| 128 | 50 | 140 | 89.1 |
| 144 | 113 | 201 | 88.3 |
| 160 | 175 | 263 | 87.5 |
| 192 | 301 | 386 | 85.7 |
| 224 | 426 | 510 | 84.1 |
| 253 | 538 | 622 | 83.9 |

All 72/72 physical APDUs passed.

## Interpretation

The shared latency rises sharply once the square becomes large
enough to require substantial BN254 modular reduction. The
difference between implementations remains approximately
84–90 ms across the measured input lengths.

This is strong evidence that shared reduction work is the
principal performance bottleneck, but RSA execution and reduction
have not been independently timed.

Replacing four general modular squarings inside BabyJubjub
doubling may save approximately 0.33 seconds for comparable dense
operands. This is an extrapolation, not a measured doubling result.

## Limitations

- No private operands, keys, or signing operations were tested.
- Operand-dependent latency is observable.
- No constant-time or side-channel safety claims.
- No full RAILGUN scalar multiplication was benchmarked.
- No changes to the wallet or other installed research applets.
- Next candidate: independently validated BN254-specific modular
  reduction before physical performance comparison.
