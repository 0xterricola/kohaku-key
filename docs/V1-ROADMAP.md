# V1 Roadmap

## Iteration 0 — Feasibility
Test canonical EIP-712 signature determinism on actual Keycard
hardware. Compare r and normalized low-s across repeated signing
sessions. Test Keycard Shell independently.

## PR 1 — Software Signer Refactor
Replace raw private-key parameters in public Ethereum transaction
paths with viem LocalAccount. Preserve existing behavior and tests.
Do not change the privacy plugin Keystore.deriveAt contract.

## PR 2 — Keycard Signer
Implement a viem-compatible account backed by Keycard.
Validate Ethereum transactions, EIP-712, and EIP-7702.
Demonstrate a signed Sepolia transaction.

## PR 3 — Privacy Pools
Implement the existing EnvelopeSigner interface if deterministic
signature recovery and protocol compatibility are demonstrated.

## Acceptance
Each PR is independently reviewable, tested, and documented.
No production funds during research.
