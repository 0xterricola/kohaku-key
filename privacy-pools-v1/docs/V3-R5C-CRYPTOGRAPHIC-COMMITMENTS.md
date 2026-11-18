# V3-R5-C1 — Cryptographic Commitment Recovery

Status: Offline integration checkpoint.

## Protocol scope

Privacy Pools v1, using the installed Kohaku SDK
@kohaku-eth/privacy-pools 0.1.0-alpha.36.

## Contract formulas

BN254 scalar field:
21888242871839275222246405745257275088548364400416034343698204186575808495617

Pool scope:
keccak256(abi.encodePacked(poolAddress, chainId, assetAddress))
modulo the scalar field.

Deposit label:
keccak256(abi.encodePacked(scope, incrementedPoolNonce))
modulo the scalar field.

Deposit commitment:
Poseidon(value, label, depositPrecommitment).

Precommitment:
Poseidon(nullifier, salt).

Spent nullifier hash:
Poseidon(nullifier).

Partial-withdrawal replacement commitment:
Poseidon(remainingValue, originalLabel, nextNotePrecommitment).

## Test

tests/v3-r5c-commitment-recovery.sh

Uses the real PrivacyPoolsV1Protocol synchronization and
note/history APIs.

It derives credentials from a fresh runtime-generated
synthetic root using the V3-R3 experimental adapter.

Expected balances:
- Deposit 0: 1000 -> 800 -> 500
- Deposit 1: 600
- Combined: 1100

The provider emits calculated commitments, pool labels,
matching entrypoint deposits and sequential withdrawal
nullifiers. No actual blockchain interaction occurs.

## Maintainer feedback

Keycard maintainer recommends BIP-85 for deterministic
privacy credentials and EIP-1581 for compatibility.

Future credential identifiers should map to versioned,
reproducible derivation locations.

The existing V3-R3 BIP-85 root path and HMAC derivation
contract remain unchanged. Any revised mapping requires
an explicit new version and migration design.

## Limitations

- No actual on-chain commitment comparison yet.
- No Groth16 proof generation or verification.
- No physical Keycard involved in this checkpoint.
- No real transactions or deployed-contract execution.
- No chain-root verification in the synthetic harness.
- No claim that derived secrets remain hardware-isolated.
- Synthetic roots and credentials are never persisted.

## Sources

https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/contracts/src/contracts/PrivacyPool.sol

https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/contracts/src/contracts/State.sol

https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/circuits/circuits/commitment.circom

https://github.com/0xbow-io/privacy-pools-core/blob/main/packages/circuits/circuits/withdraw.circom

## Next

R5-C2: independently validate calculated commitments
against contract/circuit test vectors and Merkle roots.

Then: read-only Sepolia event verification and
physical Keycard-to-SDK cold recovery.
