# V3-R0 — Privacy Pools Credential and Recovery Contract

**Status:** Source-level requirements identified; recovery oracle pending.
**SDK:** @kohaku-eth/privacy-pools 0.1.0-alpha.36
**Implementation baseline:** kohaku-cli, tag kohaku-key-v2-sepolia-poc

## Objective

Determine whether existing Keycard hardware can provide
deterministic, recoverable credentials compatible with the
installed Privacy Pools V1 SDK.

## SDK integration contract

ISecretManager exposes:

- getDepositSecrets(params)
- getSecrets(params)
- deriveEphemeralSigner(params)
- deriveDelegatorSigner(params)

Secret contains:

- nullifier: bigint
- salt: bigint
- precommitment: bigint
- nullifierHash: bigint

Derivation inputs include chainId, entrypointAddress,
depositIndex and, for withdrawals, withdrawIndex.

## Existing signature-derived scheme

An EIP-712 PrivacyPoolNote envelope binds the chain,
entrypoint contract, depositIndex and secretIndex.

The SDK canonicalizes ECDSA r and low-s, then computes:

- nullifier = trunc31(keccak256("nullifier" || canonicalRS))
- salt = trunc31(keccak256("salt" || canonicalRS))
- ephemeral key = trunc31(keccak256("signer" || canonicalRS))
- precommitment = Poseidon(nullifier, salt)
- nullifierHash = Poseidon(nullifier)

The SDK checks signature determinism within a session.

The tested Keycard's randomized ECDSA cannot directly
satisfy this scheme's repeatability requirement.

## Existing legacy scheme

Legacy SecretManager derives material from BIP-32 paths
under m/28784'/1', then applies protocol-specific Poseidon
field derivation.

Legacy and signature-derived notes are separate schemes.
Their credentials are not interchangeable.

## Note discovery and recovery

1. Derive deposit secrets at successive deposit indexes.
2. Match each precommitment against observed deposits.
3. Stop discovery at the first unmatched deposit index.
4. Follow withdrawal history using nullifier hashes.
5. Derive subsequent secrets at successive withdrawal indexes.

Consequences:

- Stable derivation is mandatory across restarts.
- Consistent index assignment is mandatory.
- A missing or mismatched index can interrupt discovery.
- Recovery must be tested with partial withdrawals.

## Security boundaries

- Ethereum signing keys may remain inside Keycard.
- Nullifier and salt values enter host/prover memory.
- Ephemeral signer derivation exposes a private key to host code.
- Determinism alone does not establish credential secrecy.
- A device backup does not prove privacy-note recovery.
- On-chain public execution does not prove note-key isolation.

## Candidate hardware experiments

### Keycard applet 3.1: BIP-85

Determine actual API availability, output format,
domain separation, repeatability and backup recovery.

### Experimental applet 4.0: ECDH

Determine key selection, peer-key validation,
shared-secret exposure, repeatability and recovery.

Neither candidate is currently verified as compatible.

## R0 remaining acceptance work

- Implement an offline reference credential/recovery oracle.
- Establish fixed test inputs and expected commitments.
- Verify restart and partial-withdrawal derivation behavior.
- Document where private material enters host memory.
- Define a distinct identity for any new derivation scheme.

No deposits, broadcasts or hardware mutations are
required for this checkpoint.

## Offline reference oracle — verified

**Test:** `tests/v3-r0-privacy-pools.sh`
**SDK:** `@kohaku-eth/privacy-pools@0.1.0-alpha.36`
**Result:** 8 checks passed.

Verified with synthetic test signing keys:

- Reproducible deposit secrets across new manager instances.
- Independent canonical ECDSA `(r, low-s)` secret derivation.
- Matching deposit and initial withdrawal secrets.
- Reproducible partial-withdrawal derivation.
- Distinct deposit-index commitments.
- Chain-bound credential derivation.
- Reproducible ephemeral sender private keys.
- Rejection of inconsistent signatures from alternating keys.

The nondeterminism fixture alternates signing keys rather than
producing randomized signatures from one key.

**Not yet verified:** full blockchain-state note rediscovery,
physical hardware credentials, device-loss recovery, or
cross-device backup recovery.

This is an offline reference test, not a hardware-backed
Privacy Pools integration.
