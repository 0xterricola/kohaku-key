# V3-R5-E — Deterministic Credential Identifiers

Status: R5-E3 hardware-assisted research PoC validated; production integration pending.

## Decision

A reproducible credential identifier maps to an
unambiguous location in the existing deterministic
Privacy Pools credential derivation hierarchy.

Preserve the proven V3-R3 BIP-85 root and HMAC
adapter. Do not silently change derivation paths.

## Identifier v1

Canonical representation:

kkid:v1:privacy-pools-v1:eip155:<chainId>:<entrypoint>:<accountIndex>:<depositIndex>:<role>:<secretIndex>

Roles:
- deposit: secretIndex = 0
- withdraw: secretIndex >= 1

The identifier describes the location of a credential.
It is not itself a secret or cryptographic commitment.

All integers use unpadded decimal representation.
Entrypoint addresses use lowercase 20-byte hex.

## SDK compatibility

Map the identifier to existing SDK coordinates:

- chainId
- entrypointAddress
- accountIndex
- depositIndex
- deposit secret / withdrawal secret index

The existing SDK ppPath implementation defines the
actual hardened path values. Do not invent or modify
its secret-type encoding.

The BIP-85 root extraction and HMAC derivation domain
remain unchanged in V3.

A different derivation algorithm or hierarchy requires
a new explicit derivation-contract version.

## Security

- Never derive credential IDs from secret material.
- Never use a commitment as its own derivation ID.
- Do not publish persistent account identifiers by default.
- Separate networks, protocols and contract contexts.
- Never persist derived credential secrets.
- Public IDs do not guarantee transaction unlinkability.
- Host-memory exposure remains an experimental limitation.

## Recovery

A complete recovery must establish:

1. Same physical card and derivation contract
2. Same identifier and network/Entrypoint context
3. Identical derived credential material
4. Matching Privacy Pools SDK note discovery
5. Correct recovered withdrawal history and balance
6. No credential-secret backup required

Identifier discovery is separate from derivation.
The SDK's sequential-index discovery limitation
must be handled explicitly.

## Scope

V3:
- Privacy Pools identifier contract
- Deterministic mapping regression tests
- Physical Keycard cold-recovery PoC
- Public blockchain history integration

V4 research:
- RAILGUN integration
- Additional protocol-specific namespaces
- General-purpose credential framework

## Sequence

R5-D historical scanning remains independent verification.
R5-E uses Kohaku's bundled Sepolia state and SDK discovery.

This document records the architectural decision.
R5-E3 validates identifier-to-SDK mapping in a physical Keycard research harness; production integration remains pending.

## Validated checkpoints

- R5-E1B: synthetic credentials recover an owned note from
  the real SDK with an in-memory augmented Sepolia snapshot.
- R5-E2: two authenticated Keycard 4.0 sessions reproduce
  the same BIP-85 root and recover the same synthetic note.
- R5-E3: canonical IDs select the existing SDK derivation
  coordinates; deposit index 17 and withdrawal index 1
  reproduce across independent physical-card sessions.
- Negative tests: incorrect root, invalid identifiers,
  and network/Entrypoint mismatches are rejected.

## Remaining boundaries

- Synthetic deposits have no actual on-chain inclusion.
- Offline on-chain root verification is intentionally refused.
- Sparse deposit-index discovery remains unresolved.
- Identified withdrawal derivation is tested, not spending.
- BIP-85 entropy enters host memory; it is not confined
  to the secure element after export.
- Live recovery and production integration remain pending.
