# V3-R5-C2 — Independent Cryptographic Vectors

## Status

Offline cross-check checkpoint.

## Test

`tests/v3-r5c-independent-vectors.sh`

Verifies:
- Four independently published circomlib Poseidon vectors
- BN254 scalar-field arithmetic
- Solidity-packed scope encoding
- Solidity-packed deposit-label derivation
- Poseidon precommitment and nullifier derivation
- Commitment input ordering
- Successive partial-withdrawal replacement commitments
- Mutation and domain-separation negative controls

All test inputs are public synthetic fixtures.

## Protocol references

PrivacyPool.sol:
https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/contracts/src/contracts/PrivacyPool.sol

State.sol:
https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/contracts/src/contracts/State.sol

Commitment circuit:
https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/circuits/circuits/commitment.circom

Withdrawal circuit:
https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/circuits/circuits/withdraw.circom

Independent Poseidon reference:
https://github.com/Verified-zkEVM/clean/blob/main/Clean/Specs/Poseidon.lean

## Boundaries

The known vectors provide an independent check of the
installed MACI Poseidon implementation for those inputs.

The SDK recovery regression verifies the protocol-derived
synthetic event lifecycle.

This does not execute a Circom witness, Solidity contract,
Groth16 proof, or real chain synchronization.

No hardware-derived entropy, private keys, PINs, or
credential secrets are stored.

The frozen Kohaku CLI V2 remains unchanged.

## Next

R5-C3: Execute the actual commitment circuit witness
against the same public test fixtures, where suitable
compiled circuit artifacts are available.

Then proceed to read-only Sepolia verification and
physical Keycard-to-SDK cold recovery.
