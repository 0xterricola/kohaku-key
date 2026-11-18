# RAILGUN Hardware Research Roadmap

## Objective 1 — Physical BabyJubJub signing

Completed:
- Native JCOP3 scalar multiplication verification
- Native PACE addition verification
- Synthetic host-side EdDSA-Poseidon compatibility

Pending:
- Independent review of two-phase signing
- Synthetic-key physical signing
- Nonce lifecycle and reset testing
- Secure spending-key derivation and custody

## Objective 2 — Poseidon acceleration

Completed:
- Two full physical hashes with round-state verification
- RSA BN254 modular squaring experiments

Pending:
- Identify arithmetic bottlenecks
- Benchmark specialized RSA squaring
- Investigate Keycard native JCOP math library
- Compare JCOP3, JCOP4, and JCOP4.5
- Benchmark Shell STM32H573 PKA implementation
- Validate five-input RAILGUN signing challenges

## Objective 3 — Secure integration

Pending:
- COMMIT/RESPOND protocol security evaluation
- Host-challenge and ROS threat analysis
- Explicit Shell approval
- RAILGUN verifier compatibility
- End-to-end signing performance measurements

No complete physical RAILGUN signing implementation
is claimed by this document.
