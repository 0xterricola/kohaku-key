# Experimental JavaCard applets

Research applets for evaluating BabyJubJub elliptic-curve operations, BN254 field arithmetic, and Poseidon hashing on JCOP smart cards.

These implementations are experimental and are not production-ready hardware signers.

## Applet overview

| Applet | Purpose | Validation |
| --- | --- | --- |
| Native ECC | BabyJubJub-compatible scalar multiplication through Weierstrass conversion | Physical JCOP3 |
| PACE-GM | Native elliptic-curve point addition | Physical JCOP3 and JCOP4 variants |
| Poseidon T3 RSA-5 (7E) | RSA-assisted BN254 arithmetic and Poseidon hashing | 325/325 physical rounds on JCOP3 |
| Poseidon T3 Barrett (7F) | Alternative modular reduction implementation | 65/65 physical rounds on JCOP3 |

## Poseidon implementations

### RSA-5 sparse dictionary (7E)

Fastest measured JCOP3 Poseidon T3 implementation: approximately **230.5 seconds per hash**.

[Implementation and reproduction notes](poseidon-t3-rsa5-7e/README.md)

### RSA-5 Barrett (7F)

Validated alternative reduction implementation. Approximately **255.3 seconds per hash** on the compared physical vector, 10.7% slower than 7E.

[Implementation and reproduction notes](poseidon-t3-rsa5-7f/README.md)

## Compatibility and reproducibility

Physical validation is specific to the tested applet, card generation, and execution environment. JCOP3 results do not automatically establish JCOP4 or JCOP4.5 compatibility.

Some imported sources require separate JavaCard SDKs or build-time dependencies. CAP availability and SHA-256 verification requirements are documented per experiment; not every experimental CAP is distributed in this repository.

Installing or removing applets modifies card state and requires explicit authorization.

## Related documentation

- [Hardware benchmarks](../benchmarks/RESULTS.md)
- [Benchmark scripts](../scripts/README.md)
- [Research experiments](../experiments/README.md)
- [Documentation conventions](../docs/DOCUMENTATION-STYLE.md)
