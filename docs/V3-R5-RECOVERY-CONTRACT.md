# V3-R5 — Recovery Metadata and Card-Loss Contract

Status: R5-A research specification.

## Objective

Preserve the exact hardware-assisted Privacy Pools
derivation configuration without persisting secrets.

The recovery manifest is configuration, not a backup
of the cryptographic root.

## Versioned derivation contract

Format: kohaku-key/v3-recovery/1
Method: keycard4-bip85-hmac-sha256/1

Hardware:
- Keycard applet 4.0
- BIP-85 path: m/83696968'/128169'/32'/0'
- BIP-85 output: 32 bytes

Adapter:
- HMAC-SHA256
- Key: runtime-only BIP-85 output
- Input: UTF-8 domain || 0x00 || UTF-8 SDK path
- Domain: kohaku-key/v3-r3/privacy-pools-v1/deriveAt
- SDK derivation prefix: m/28784'/1'
- SDK account index: 0

Any incompatible derivation change requires a new
version, explicit migration strategy, and recovery tests.

## Allowed recovery metadata

- Format and derivation contract identifiers
- Public derivation configuration
- Chain ID
- Privacy Pools SDK entrypoint address
- Blockchain scan starting block

The scan starting block must not omit any relevant
contract activity. Blockchain discovery remains untested.

## Prohibited persisted data

- Master seed or mnemonic
- Private keys
- BIP-85 output
- ECDH shared secrets
- PIN or PUK
- Nullifier or salt secrets
- Ephemeral signer secrets
- Derived credential material
- Card identity or fingerprint

The validator rejects additional fields.

Even permitted public metadata can reveal usage patterns
when combined with other records. Do not automatically
publish user-specific manifests.

## Recovery scenarios

### Application restart with the same Keycard

Verified in R4.

The device reconstructs the BIP-85 root, and the
adapter reproduces the same SDK credential derivations.

### Lost card with an independently backed-up seed

Potential recovery path, not yet validated.

A replacement device would need to reproduce the
same seed, supported BIP-85 semantics, derivation
path, and adapter contract.

Never use a production backup for experimentation.

### Lost card without a recoverable seed

Metadata alone cannot reconstruct the credentials.

Recovery must not be represented as possible without
a separate verified recovery mechanism.

### Compromised host

Derived material enters host memory.

The card provides authentication and deterministic
derivation, but does not prevent a compromised host
from obtaining material returned by BIP-85.

## Outstanding tests

1. Validate public recovery metadata against the schema.
2. Test actual blockchain note rediscovery.
3. Test recovery with a separately provisioned test card.
4. Verify SDK-version compatibility.
5. Evaluate host memory exposure and backup threats.
6. Test withdrawal-chain reconstruction and scan gaps.

No actual deposits, withdrawals, or production recovery
are authorized by this research checkpoint.
