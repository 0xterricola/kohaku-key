# V3-R5-C3 — Commitment Circuit Verification

## Status

Actual commitment circuit verification completed offline.

## Implementation

Test: `tests/v3-r5c-circuit-witness.sh`

Artifacts:
- @fatsolutions/privacy-pools-core-circuits/commitment.wasm
- @fatsolutions/privacy-pools-core-circuits/commitment.zkey

## Verified

Three synthetic fixtures:
1. Original deposit, value 1000
2. First replacement, remaining value 800
3. Second replacement, remaining value 500

Checks:
- Compiled Circom witness generation
- Poseidon commitment equality
- Poseidon nullifier-hash equality
- Distinct replacement commitments
- Four Groth16 public signals
- Groth16 proof generation
- Groth16 proof verification
- Tampered commitment rejection

## Tooling

Node.js 23 with installed snarkjs.

Witness/proof generation and verification-key export
run in separate Node.js processes to avoid the observed
resource-lifecycle stall.

No intermediate witness or proof files are created.
Proof and public signals are passed between processes
in memory through a shell variable and child environment.

All fixtures use publicly known synthetic values.

## Security boundaries

- No physical Keycard credentials involved.
- No real private keys, PINs, or BIP-85 entropy.
- No transaction signing or broadcasting.
- No real blockchain interaction.
- No full withdrawal-circuit verification.
- No deployed Solidity-verifier execution.
- Installed proving artifacts are not independently audited.

## Conclusion

The installed commitment circuit agrees with the
Poseidon calculations used by the V3-R5-C1 SDK
recovery test for the checked synthetic fixtures.

A generated Groth16 proof verifies against the
installed verification key.

This establishes an offline circuit-level research
checkpoint, not production readiness.

## Next

R5-D: Read-only Sepolia contract and event validation.

Then physical Keycard 4.0 to Privacy Pools SDK
cold-recovery integration.
